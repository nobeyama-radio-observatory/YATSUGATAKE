# ハードウェアと版

> **仕様の正典**（[ADR 0021](../decisions/0021-spec-canonical-in-yatsugatake.md)）。bit と specd が前提にするボード・版・入力の口・クロックの構成はここが正。
> 実測の経緯と根拠は [`../knowledge/hardware.md`](../knowledge/hardware.md)・[`../knowledge/environment.md`](../knowledge/environment.md)（study-rfsoc の `VERSIONS.md` から）。

## 版

| | 値 | 根拠 |
|---|---|---|
| ボード | RealDigital RFSoC 4x2（XCZU48DR、FFVG1517） | [ADR 0003](../decisions/0003-platform-rfsoc4x2-pynq.md) |
| Part（ビルド） | `xczu48dr-ffvg1517-1-e`（遅いほうで閉じる。board file の宣言は `-2`） | [ADR 0004](../decisions/0004-build-with-speed-grade-1.md) |
| Vivado | 2024.1（ML Enterprise） | |
| PYNQ | RFSoC-PYNQ v3.1.1 | |
| Board files | RealDigitalOrg/RFSoC4x2-BSP `board_files/rfsoc4x2/1.0`、commit `40e6814a3b62eead76e41a29fdabc43030f89b6c` | |

## 入力の口

| SMA | RF-ADC | PYNQ | 流れの ADC の番号 |
|---|---|---|---|
| ADC_A | Tile 226 / slice 2 | `adc_tiles[2].blocks[1]` | 0 |
| ADC_B | Tile 226 / slice 0 | `adc_tiles[2].blocks[0]` | 1 |
| ADC_C | Tile 224 / slice 2 | `adc_tiles[0].blocks[1]` | 2 |
| ADC_D | Tile 224 / slice 0 | `adc_tiles[0].blocks[0]` | 3 |

- **ラベルとタイル・スライスは逆の順**。設計をラベルから書かない
- Tile 224 と 226 は入力の極性が反転（180°）。相互相関・位相を使う処理では符号を揃える
- 入力のバラン MABA-011118（10 MHz〜10 GHz、DC 結合ではない）

| 入力 | 値 |
|---|---|
| IF | 2048〜4096 MHz（第 2 ナイキスト）。ch は IF の昇順で送る |
| フルスケール | 0 dBFS ≒ +5.8 dBm（ADC の口） |
| 運転のレベル | HOT ≦ −10 dBFS（振り切れ）。HOT ≒ −16 dBFS・SKY ≒ −21 dBFS |

## クロックと 1PPS

| | 値 |
|---|---|
| 外部基準 | 10 MHz を **CLK_IN（SMA）→ LMK04828 の CLKin0**（specd `--clkin 0 --ref 10`）。出荷時の基準は CLKin1（基板の Si5395） |
| RFDC の基準 | LMX2594 の 491.52 MHz、出力の強さ **PWR 3**（specd `--lmx-pwr` の既定。31 だと n × 163.84 MHz の櫛が立つ） |
| fs | 4096.0 MSPS（タイル PLL R 1 / N 25 / M 3） |
| DSP のクロック | 256 MHz = 1 ビート（[`timing.md`](timing.md)） |
| 1PPS | PPS Clk に 45m の +2.5 V / 100 µs をそのまま（レベル変換・PULLUP なし） |
| 入口の LPF | **1PPS と 10 MHz の入力の直前に Mini-Circuits BLP-10.7+ を常設**（800 MHz 帯の混信の対策、2026-10-21）。遅れは `timebase.CAL` の `pps_det_ns`（[`timing.md`](timing.md)） |

## 固定のスプリアス

k·fs/8（IF 2560・3072・3584 MHz）と n × 163.84 MHz。運転のレベルでは揺れず、チョッパーホイールの Ta* では消える（proj019）。
