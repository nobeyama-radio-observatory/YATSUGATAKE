# specd — 起動と命令

specd はボードの上で動く分光計のサーバー。制御の口（TCP 51000、1 行 1 命令）で命令を受け、データの口（TCP 51001）で s45proto v2 の記録を送る。命令と応答の約束の正典は [`../spec/interface.md`](../spec/interface.md) の 5.・6.。ここは使い方。

## 起こす

```bash
ssh xilinx@<board>
cd ~/sam45-fine-<版>                # bit の版ごとのディレクトリ（install.md）
ls /dev/shm                       # 前の specd の残り（psm_*）があれば消す: sudo rm /dev/shm/psm_*（kill -9 で落としたときなど）
sudo -E $(which python3) specd.py --clkin 0 --ref 10 --bits bits.json
```

- `sudo -E $(which python3)`: pynq の venv の python3 を root で動かす。`sudo python3` だとシステムの python3 になり、`ModuleNotFoundError: No module named 'pynq'` で止まる
- `--clkin 0 --ref 10`: CLK_IN の 10 MHz を基準にする（既定の `stock` はボードの水晶）。45m と試験台はこれ
- `--bits bits.json`: LOAD で許す bit の一覧（[`install.md`](install.md)）。起こすときの bit は `--bit <名前>`（既定は bits.json の `default`）
- 起きるまで数十秒（bit を載せ、RFDC と LMK/LMX を立て、1PPS を待つ）。ログに制御の口とデータの口を開いた行が出たら使える
- TP の較正ファイル（既定 `/etc/yatsugatake/tp_cal.json`、環境変数 `YATSUGATAKE_TP_CAL` か `--tp-cal`）が無い・別のボードのものなら、TP の dBm は出ない（dBFS は出る）。[`calibration.md`](calibration.md)
- 時刻の較正ファイル（既定 `/etc/yatsugatake/time_cal.json`、環境変数 `YATSUGATAKE_TIME_CAL`）が無い・別のボードのものなら、時刻は開発の値（暫定）で動く。`ID` の `tcal` が `board` / `provisional`（[`calibration.md`](calibration.md)）

その他の引数は `python3 specd.py -h`。`--buf-mb`（既定 256 MiB ≒ 38 秒ぶんの溜まり）・`--cpu`・`--rt` は試験で決めた値のまま使う。

## 命令

制御の口は**同時に 1 接続**。応答は `OK key=val …` か `ERR <理由>`。打ち方は [`client.md`](client.md)（specctl・s45client）。

| 命令 | 何をするか |
|---|---|
| `ID` | 自己記述（bit の種類と版、ADC・窓の数、記録の版、時刻の較正の印 `tcal`、ボードの印 `board`）。置いた bit が思ったものかをまず見る |
| `STATUS` | 今の状態（下の表） |
| `GET` / `GET CAL` | 今の設定 / 今の bit に当てている較正（時刻・TP） |
| `SET key=val …` | 設定。`tint`・`cfg`・窓ごとの `A0.if` `A0.ns` `A0.bw` `A0.shift` `A0.bundle`・全部の `all.shift` など（SAM45-Fine）。SAM45-Wide のキーは下。**specd を起こし直すまで残る** |
| `ANCHOR` | 時刻の錨を取り直す（1PPS とビートの対応） |
| `START [at=<UTC>] [n=<ダンプ数>] [force=1]` | 取得を始める。`at` は ISO 8601 か unix 秒、`n` を省くと STOP まで。時刻を答えられないときは断る（`force=1` で時刻なしで取る） |
| `STOP` | 取得を止める |
| `SEND ON [from=oldest\|now]` / `SEND OFF` | データの口へ送る / 送らない |
| `CLEAR` | 溜まりを空にする |
| `SNAP adc=A [n=1] [every=20]` | ADC の生の波形を取る |
| `BITS` / `LOAD bit=<名前>` | 載せられる bit の一覧 / bit を載せ替える（bits.json にあるものだけ） |
| `BYE` | 接続を閉じる |
| `SHUTDOWN confirm=1` | specd を止める |

### SAM45-Wide の SET

SAM45-Wide は全帯域の FFT（32768 点）の ch を ADC ごとに B 個ずつ束ね、4096 ch の流れにする（[`../spec/interface.md`](../spec/interface.md) の 2.1・5.）。**キーは bit で違うので、`LOAD` の後は `ID` で bit を確かめてから SET する。**

| キー | 意味 |
|---|---|
| `A.b`（`all.b`） | 束ね B = 4（全帯域 2048 MHz・500 kHz、流れ 1 本）・2（1 GHz × 2・250 kHz）・1（512 MHz × 2・125 kHz）。ADC ごとに 1 つ（`A0.b` もコアに効く） |
| `A.shift`（`all.shift`） | SHIFT。ADC ごとに 1 つ |
| `A0.s0`・`A1.s0`（別名 `ch0`） | 流れの最初の ch（束ねた ch の番号）。ch → IF は (S0 + i + (B − 1)/(2B))·fs / N |
| `tint`・`fmt`・`cfg` | Fine と同じ |

例（M6 の判定の設定）: `SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7`。B 4 の ADC の流れ 1 は空（STATUS の `bund_r` で「-」）。

## STATUS の見方

| 鍵 | 意味 | 見るところ |
|---|---|---|
| `state` | IDLE・ARMED（at を待っている）・RUN・ERROR | |
| `time_ok` | 時刻を答えられるか（1PPS が来ていて錨がある） | **0 なら START は断られる**（下） |
| `dumps`・`miss`・`kgap` | 出したダンプの数・取り損ね・番号の飛び | `miss`・`kgap` は 0 |
| `tp_dbfs`・`tp_dbm` | ADC ごとの TP | 入力レベル（[`wiring.md`](wiring.md)）。配線を変えたらまずここ |
| `tp_lost`・`tp_bad`・`tp_ovr`・`tp_jump`・`sat` | TP の欠け・異常・振り切れ・跳ね・飽和 | 0 が普通 |
| `loop_max_ms`・`loop_p99_ms` | 読み出しの 1 周の長さ | 読み出しの余裕 |
| `seq`・`drop`・`sent` | 記録の番号・捨てた数・送った数 | `drop` は 0 |
| `buf_used_mb` / `buf_cap_mb` | 溜まり | 受け側が止まると増える。満ちると捨てる（DROP） |
| `health`・`flags` | 健全性のビット | ビットの意味は [`../spec/interface.md`](../spec/interface.md) |
| `bund_r`（SAM45-Wide） | 流れごとの束ねの見張り r | 1,048,576（2·G）。違えば束ねの区切りがずれている |
| `send`・`data_client` | 送っているか・データの口の相手 | |

## 止める

```bash
python3 specctl.py --host <board> "SHUTDOWN confirm=1"    # 制御 PC から
```

ボードの上で Ctrl-C・`kill <PID>` でもよく、ssh が切れたときも specd は片付けてから止まる。`kill -9` で落としたときだけ `/dev/shm` に `psm_*` が残るので消す（次に起こすときに邪魔をする）。v1.0.0 の specd は普通に止めても残ることがある（既知の制限 3）

## 困ったとき

| 症状 | 見ること・すること |
|---|---|
| `START` が時刻で断られる（`time_ok=0`） | 1PPS が PPS Clk に来ているか（LPF を含めて）。来ていれば `ANCHOR`。時刻なしでよい試験なら `force=1`（記録の utc_ns は 0、健全性に印） |
| 起こした直後の最初の START がおかしい | specd を起こし直す（起こした直後の 1PPS の取り込みの異常が残っている。調べている途中） |
| `tp_dbfs` が思った値と違う | 配線とレベル（[`wiring.md`](wiring.md)）。分配器・ATT を替えていないか |
| `ERR BUSY` | 制御の口は 1 接続だけ。s45client を開いていないか。specctl に複数の命令をまとめて貼らず、1 行ずつ前が終わってから |
| 受け側を閉じた後の次の記録の頭に、前の RUN のダンプが入る | 受け側を閉じる前に `STOP` する（溜まりに残った分を specd が次の受け側に送る） |
| `buf_used_mb` が増え続ける | 受け側（specrecv）が止まっている・ACK が返っていない |
| 起こせない・`/dev/shm` が満ちる | 前の specd の残り `psm_*` を消す |
