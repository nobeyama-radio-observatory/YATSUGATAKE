# 2G-2 の判定（受け入れ試験）

2G-2 の bit（BIT_KIND 10・BIT_REV 1・PROJ 0x0034_0100、study-rfsoc の proj034 の build/（既定の戦略）と FDRI が同じ）と、それに載せる PS（`sw/pynq/`。2G-4 の M5 で G22 の Backend を一本化してある）を、リリースの前に実機で通す判定。
1 判定 1 ファイル。書き方は 6 項目（ID・前提・手順・合格・陽性対照・記録）。**合格は測る前に書く**。

proj025・proj034 の判定は README の中にだけあった（4a〜4d・R-1〜R-6）。2G-4・2G-1-Fast と同じく**移植の M0 で書き起こした**（2026-10-31）。
ID は 2G-4・2G-1-Fast の判定と同じ意味のものは同じ ID にした（ID-1・H-0・H-2・V2-b・V2-L・RING・NET）。**EQ-2** は 2G-4 の EQ-4 の 2 コア版（proj034 R-1c・proj025 4a-3 の E-4）。

## 共通の前提

- **bit**: 2G-2（`proj034.bit`）。specd の ID で adc_id 0x020A_0101・time_id 0x020A_0102・proj 0x0034_0100・kind g22。コア 2 個（コア 0 は RAW を持ち NSTREAM 2、コア 1 は NSTREAM 1）。係数は ROM で、コアごとに 1 組
- **ボードの準備**: 2G-4 と同じ（GEM1 の AXI_MAX_PIPELINE が **0x0102**。判定の前と後に読み返して記録に残す。**4 本以上にしない**）。`--fast` を使うなら libs45fast.so をボードで `build_fast.sh` で作り、最後の行が「CRC: 命令」
- **ファン**: proj027 4f の配置のまま（2G-2 は VCCINT ≒ 19 A）
- **クロック**: 外部 10 MHz と 1PPS（入口に LPF を常設）。`--clkin 0 --ref 10`
- **specd**: `sudo -E $(which python3) specd.py --g22 --bitfile proj034.bit --clkin 0 --ref 10`（bits.json の項目なら `"kind": "g22"`）。リング 64 MiB・LMX の PWR 3・予算 30 MB/s の照合は既定。
  proj034 の R は `--fast` を付けずに回した。**M4 で両方回し、`--prefault --fast --fast-ring`（2G-4・2G-1-Fast の形）を付けると決めた**（2026-10-31。tint 20.48 ms で 1 周の p99 が `--fast` なし 57.4 ms・loop_slow 5,453、あり 7.5 ms・1 周の計 11.71 ms。migration の「M4 の結果」）。判定は `sudo -E $(which python3) specd.py --g22 --bitfile proj034.bit --clkin 0 --ref 10 --prefault --fast --fast-ring` で起こす。記録には付けたかどうかを書く。止めるときは `SHUTDOWN confirm=1` か pid のファイルで
- **ボードと器は別の作業と分け合っている**: specd を起こす前に、別の作業の specd が動いていないか（`pgrep -af "[s]pecd"`）と `ATT?` を読む。ATT が 13 dB でなければ、戻す前に開発者に聞く（100 dB のままだと入力が来ず、TP は ADC の床 −60 dBFS 前後になる。proj034 R-1 で踏んだ）
- **送り出し**: specd を起こした後、受けを取る前に一度 **`SEND ON`** を打つ。溜まりに残った分は `CLEAR` で捨ててから取り直す。specrecv は同じファイルに足して書くので、取り直すときはファイルを消してから
- **宛先**: 環境変数 `B`（ボード）・`SG`・`PM`・`ATT`・`RFSOC_NS`。宛先はファイルに書かない。STATUS の `data_client`・`data_drop` には受け手の IP が出るので、記録に残すときは伏せる
- **ノイズソースはいつも ON**（[ADR 0024](../../../docs/decisions/0024-noise-source-always-on-remote-off.md)）。OFF の要る判定（H-2）は、測る前に `python3 instr.py ns off`、測り終えたら `python3 instr.py ns on`。手で ON / OFF しない
- **時刻の較正**（[ADR 0023](../../../docs/decisions/0023-time-calibration-per-board.md)）: ボードの `/etc/yatsugatake/time_cal.json` が当たり、specd の `ID` が `tcal=board` になる見込み（`timebase.ADC_PATH` に (10, 1) が無いので共通の道とみなされる。道が共通かは M0 で `rfdc_params.rpt` を数え、M5 で注釈に書く）。記録には `tcal` を書く。TP の dBm もボードの `tp_cal.json`（ADR 0025）
- **SET の既定**: `A0.src=A B0.src=B shift=7 fmt=f32`。流れは FULL の 2 本（鍵 A0 = コア 0・B0 = コア 1）。`src` はコアごと（2 コアに同じ ADC も可）
- **ネットワークの tint**: 2G-2 の最小は **20.48 ms**（2 × 65,536 ch × 4 B で 25.6 MB/s、interface 4.5、予算 1 ボード 30 MB/s。2G-4・2G-1-Fast と同じ量）。10.24 ms は SET で断られる（NET）
- **レベルを tint や設定をまたいで比べるときは、1 回の Overlay の読み込みの中で切り替える**（載せ直すと 1 % 級の段が出る。proj036 R-2）
- **配線**（2G-4 の判定の README と同じ名前）: N（ノイズ ON）・N/S（SG の CW を足す。ノイズ ON が既定、OFF は道具が作る）。P は使わない（F-2 を回さない）

## 一覧

| ID | 何を確かめるか | 動かし方 | 配線 | study-rfsoc で |
|---|---|---|---|---|
| [ID-1](ID-1.md) | 自己記述・起動の見張り | specd | どれでも | 通過（proj034 R-1） |
| [H-0](H-0.md) | 立ち上げ（2 窓の頭の欄・照合・床・2-for-1 の見張り） | specd | N か N/S | 通過（proj034 R-1・R-2'） |
| [EQ-2](EQ-2.md) | 2 コアに同じ ADC で bit 単位で同じ | specd | N か N/S | 通過（proj034 R-1c） |
| [H-2](H-2.md) | ch → IF（直接の側と 2-for-1 の共役の側、4 点 × 2 窓） | specd | N/S ＋ SG | 通過（proj034 R-6） |
| [V2-b](V2-b.md) | tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | specd | N | tint 40.96 ms でだけ通過（proj034 R-3） |
| [V2-L](V2-L.md) | tint 20.48 ms で 2 時間（電流・温度・落ちない） | specd | N | なし |
| [RING](RING.md) | リング 64 MiB が PS の 0.3 s の止まりを吸う | specd | N | なし（2G-4 の判定） |
| [NET](NET.md) | 予算を越える tint を SET で断る | specd | どれでも | なし（2G-4 の M5 で入れた照合） |

**回さない判定**: F-2（ADR 0023）・CU・BUND（2G-4 だけの機能）。
proj034 R-2 の proj025 との床・ch の並びの比べは、移植では比べる相手が無いので回さない（bit 単位の確かめは sim の P-2・P-3・P-4a、M2 で移植元と同じ出力）。
sim の判定（D_eff は sim-g22ds、2 コアの同等は sim-g22x2、2-for-1 の部品は sim-sep・sim-all2）は `hw/bits/2g-2` の sim。
