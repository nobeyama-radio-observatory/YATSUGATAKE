# 2G-4 の判定（受け入れ試験）

2G-4 の bit（BIT_KIND 3・BIT_REV 1・PROJ 0x0031_0200、study-rfsoc の proj031 rev 2 と FDRI が同じ）と、それに載せる PS（M1〜M4 は `sw/pynq-2g/`、M5 の後は `sw/pynq/`）を、リリースの前に実機で通す判定。
1 判定 1 ファイル。書き方は 6 項目（ID・前提・手順・合格・陽性対照・記録）。**合格は測る前に書く**。

proj027・030・031・036 の判定は README の中にだけあった（4a・4b・R-1〜R-6・P-1・R-1〜R-4 など）。Wide はこれを M6 の前に書き起こしたが、2G-4 は**移植の M0 で書き起こした**（2026-10-28）。
ID は Wide の判定と同じ意味のものは同じ ID（ID-1・H-0・H-2・F-2・V2-b）にし、2G-4 で新しいものに ID を付けた（CU・EQ-4・V2-L・RING・BUND・NET）。

## 共通の前提

- **bit**: 2G-4（`proj031.bit`）。specd の ID で adc_id 0x0203_0101・time_id 0x0203_0102・proj 0x0031_0200・kind g24。bit の隣に係数の hex（`g24_coef_lo.hex`・`g24_coef_hi.hex`、PS が係数 URAM に書く元）
- **ボードの準備**: GEM1 の AXI_MAX_PIPELINE が **0x0102**（起動時の systemd のユニット。study-rfsoc proj035、runbook の 09）。判定の前と後に読み返して記録に残す。**4 本以上（0x0104〜）にしない**（CPU の DDR の読みが遅れ、取得が追いつかない）。libs45fast.so をボードで `build_fast.sh` で作り、最後の行が「CRC: 命令」
- **ファン**: proj027 4f の配置のまま（2G-4 は VCCINT ≒ 31 A で目安 38 A を下回るが、配置は変えない）
- **クロック**: 外部 10 MHz と 1PPS（入口に LPF を常設）。`--clkin 0 --ref 10`
- **specd**: `sudo -E $(which python3) specd.py --g24 --bitfile proj031.bit --clkin 0 --ref 10 --ring-mib 64 --prefault --fast --fast-ring`（M5 の後は bits.json の `kind` と既定で同じになる）。止めるときは `SHUTDOWN confirm=1` か pid のファイルで（`pkill -f specd.py` は ssh のコマンド行にも当たる）
- **送り出し**: specd を起こした後、受けを取る前に一度 **`SEND ON`** を打つ（打たないと記録が specd の溜まりに残り、受けのファイルが空になる。照合は「通過」のまま spec 0 で出るので気づきにくい。proj031 R-1a と 2G-4 の M4 で踏んだ）。溜まりに残った分は `CLEAR` で捨ててから取り直す
- **宛先**: 環境変数 `B`（ボード）・`SG`・`PM`・`ATT`。宛先はファイルに書かない
- **2 つの動かし方**: 「specd」（制御 PC から specctl・specrecv）と「ボード直」（specd を止め、root で道具が Overlay を載せる。F-2 だけ）
- **SET の既定**: `A0.src=A B0.src=B C0.src=C D0.src=D shift=7 fmt=f32`。窓 A0〜D0 = コア 0〜3
- **ネットワークの tint**: 2G-4 の最小は **20.48 ms**（interface 4.5、予算 1 ボード 30 MB/s）。それより短い tint（10.24 ms）は PL の確かめ（H-0・EQ-4・H-2・CU）で受けをボードの上に置くか、短い N で使う
- **レベルを tint や設定をまたいで比べるときは、1 回の Overlay の読み込みの中で切り替える**（載せ直すと 1 % 級の段が出る。proj036 R-2）
- **配線**（Wide の判定の README と同じ名前）: N（ノイズ ON）・N/S（ノイズ OFF・SG の CW）・P（1PPS を ADC にも分配）

## 一覧

| ID | 何を確かめるか | 動かし方 | 配線 | study-rfsoc で |
|---|---|---|---|---|
| [ID-1](ID-1.md) | 自己記述・係数 URAM の書きと VERIFY・起動の見張り | specd | どれでも | 通過（proj031 rev 2） |
| [CU](CU.md) | 係数 URAM の見張り（OK が落ちる・START を断る・CRC の 1 bit・書き直しで消える） | specd ＋ cuctl | どれでも | 通過（proj031 R-2 rev 2） |
| [H-0](H-0.md) | 4 窓の立ち上げ（頭の欄・照合・床） | specd | N か N/S | 通過（proj031 R-1a） |
| [EQ-4](EQ-4.md) | 4 コアに同じ ADC で bit 単位で同じ | specd | どれでも | 通過（proj031 R-1b） |
| [H-2](H-2.md) | ch → IF（直接の側と 2-for-1 の共役の側、4 点 × 4 窓） | specd | N/S ＋ SG | 通過（proj030 R-6） |
| [F-2](F-2.md) | ADC → コアの遅れ（timebase.CAL[0x0031_0200]） | ボード直 | P | 通過（proj031 R-5） |
| [BUND](BUND.md) | 束ね（C の道）のレベルが tint をまたいで同じ | specd | N | 通過（proj036 R-2） |
| [V2-b](V2-b.md) | tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | specd | N | 通過（proj036 R-3） |
| [V2-L](V2-L.md) | tint 20.48 ms で 2 時間（電流・温度・落ちない） | specd | N | proj036 R-4 |
| [RING](RING.md) | リング 64 MiB が PS の 0.3 s の止まりを吸う | specd | N | なし（新しく。interface 8. の 11） |
| [NET](NET.md) | 予算を越える tint を SET で断る | specd | どれでも | なし（M5 で入れる。interface 4.5） |

**2G-4 では回さない判定**: Wide の H-1（束ねた ch の応答）・H-4（モードの切り替え）・V2-d（LOAD の往復は 2G の PS を `sw/pynq/` に一本化した M5 の後に、Wide・Fine と組で V2-d を広げる）・P-8・PS-3（TP の線形性・跳ねの見張りは TP の作りが Wide と同じ。M6 で回すかを決める）。
sim の判定（D_S・D_eff は sim-g24ds、係数 URAM は sim-cu・sim-g24x4 の cudrop・cuclr）は `hw/bits/2g-4` の sim（M2 で移植元と同じ出力）。
