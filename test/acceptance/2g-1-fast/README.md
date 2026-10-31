# 2G-1-Fast の判定（受け入れ試験）

2G-1-Fast の bit（BIT_KIND 11・BIT_REV 1・PROJ 0x0033_0100、study-rfsoc の proj033 の build-PE と FDRI が同じ）と、それに載せる PS（`sw/pynq/`。2G-4 の M5 で G21 の Backend を一本化してある）を、リリースの前に実機で通す判定。
1 判定 1 ファイル。書き方は 6 項目（ID・前提・手順・合格・陽性対照・記録）。**合格は測る前に書く**。

proj024・proj033 の判定は README の中にだけあった（4a〜4d・R-1〜R-6）。2G-4 と同じく**移植の M0 で書き起こした**（2026-10-30）。
ID は 2G-4 の判定と同じ意味のものは同じ ID にした（ID-1・H-0・H-2・V2-b・V2-L・RING・NET）。2G-1-Fast で新しい判定は無い。

## 共通の前提

- **bit**: 2G-1-Fast（`proj033.bit`）。specd の ID で adc_id 0x020B_0101・time_id 0x020B_0102・proj 0x0033_0100・kind g21。係数 URAM は無い（係数は ROM で bit に入っている）
- **ボードの準備**: 2G-4 と同じ（GEM1 の AXI_MAX_PIPELINE が **0x0102**。判定の前と後に読み返して記録に残す。**4 本以上にしない**）。`--fast` を使うなら libs45fast.so をボードで `build_fast.sh` で作り、最後の行が「CRC: 命令」
- **ファン**: proj027 4f の配置のまま（2G-1-Fast は VCCINT ≒ 13.5 A）
- **クロック**: 外部 10 MHz と 1PPS（入口に LPF を常設）。`--clkin 0 --ref 10`
- **specd**: `sudo -E $(which python3) specd.py --g21 --bitfile proj033.bit --clkin 0 --ref 10`（bits.json の項目なら `"kind": "g21"`）。リング 64 MiB・LMX の PWR 3・予算 30 MB/s の照合は既定。
  proj033 の R は `--fast` を付けずに回した。**M4 で両方回し、`--prefault --fast --fast-ring`（2G-4 の形）を付けると決めた**（2026-10-31。tint 20.48 ms で 1 周の p99 が `--fast` なし 16.4 ms・あり 5.4 ms。migration の「M4 の結果」）。判定は `sudo -E $(which python3) specd.py --g21 --bitfile proj033.bit --clkin 0 --ref 10 --prefault --fast --fast-ring` で起こす。記録には付けたかどうかを書く。止めるときは `SHUTDOWN confirm=1` か pid のファイルで
- **送り出し**: specd を起こした後、受けを取る前に一度 **`SEND ON`** を打つ（proj033 R-1 でも付け忘れて受けが 0 個になった）。溜まりに残った分は `CLEAR` で捨ててから取り直す。specrecv は同じファイルに足して書くので、取り直すときはファイルを消してから
- **宛先**: 環境変数 `B`（ボード）・`SG`・`PM`・`ATT`・`RFSOC_NS`。宛先はファイルに書かない。STATUS の `data_client`・`data_drop` には受け手の IP が出るので、記録に残すときは伏せる
- **ノイズソースはいつも ON**（[ADR 0024](../../../docs/decisions/0024-noise-source-always-on-remote-off.md)）。OFF の要る判定（H-2）は、測る前に `python3 instr.py ns off`、測り終えたら `python3 instr.py ns on`。手で ON / OFF しない
- **時刻の較正**（[ADR 0023](../../../docs/decisions/0023-time-calibration-per-board.md)）: ボードの `/etc/yatsugatake/time_cal.json` が当たり、specd の `ID` が `tcal=board` になる（M5 で `ADC_PATH` を確かめた後）。記録には `tcal` を書く。`timebase.ADC_PATH` に (11, 1) が無いと共通の道とみなされ、M4 の時点でも `tcal=board` になった（M5 で道を確かめるまでは時刻の確かさの証拠にしない）。TP の dBm もボードの `tp_cal.json`（ADR 0025）
- **SET の既定**: `src=A shift=7 fmt=f32`。流れは FULL の 1 本（鍵 A0）。`src` は FULL と RAW の入力の ADC（次の WRST で効く）
- **ネットワークの tint**: 2G-1-Fast の最小は **20.48 ms**（131,072 ch × 4 B で 25.6 MB/s、interface 4.5、予算 1 ボード 30 MB/s）。10.24 ms は SET で断られる（NET）
- **レベルを tint や設定をまたいで比べるときは、1 回の Overlay の読み込みの中で切り替える**（載せ直すと 1 % 級の段が出る。proj036 R-2）
- **配線**（2G-4 の判定の README と同じ名前）: N（ノイズ ON）・N/S（SG の CW を足す。ノイズ ON が既定、OFF は道具が作る）。P は使わない（F-2 を回さない）

## 一覧

| ID | 何を確かめるか | 動かし方 | 配線 | study-rfsoc で |
|---|---|---|---|---|
| [ID-1](ID-1.md) | 自己記述・起動の見張り | specd | どれでも | 通過（proj033 R-1） |
| [H-0](H-0.md) | 立ち上げ（頭の欄・照合・床・2-for-1 の見張り） | specd | N か N/S | 通過（proj033 R-1） |
| [H-2](H-2.md) | ch → IF（直接の側と 2-for-1 の共役の側、4 点） | specd | N/S ＋ SG | 通過（proj033 R-6） |
| [V2-b](V2-b.md) | tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | specd | N | tint 40.96 ms でだけ通過（proj033 R-3） |
| [V2-L](V2-L.md) | tint 20.48 ms で 2 時間（電流・温度・落ちない） | specd | N | なし |
| [RING](RING.md) | リング 64 MiB が PS の 0.3 s の止まりを吸う | specd | N | なし（2G-4 の判定） |
| [NET](NET.md) | 予算を越える tint を SET で断る | specd | どれでも | なし（2G-4 の M5 で入れた照合） |

**回さない判定**: F-2（ADR 0023。2G-1-Fast の ADC → コアの道が共通コアと同じかは M5 で確かめて `timebase.ADC_PATH` に書く）・CU・EQ-4・BUND（2G-4 だけの機能）。
proj033 R-2 の proj024 との床・ch の並びの比べは、移植では比べる相手が無いので回さない（bit 単位の確かめは sim の P-2・P-3・P-4a、M2 で移植元と同じ出力）。
sim の判定（D_eff は sim-g21ds、2-for-1 の部品は sim-sep・sim-all2）は `hw/bits/2g-1-fast` の sim。
