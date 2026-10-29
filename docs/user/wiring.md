# 結線と入力レベル

## つなぐもの

| 入力 | ボードの口 | 中身 | 注意 |
|---|---|---|---|
| IF × 4 | SMA の ADC_A〜D | 2048〜4096 MHz（第 2 ナイキスト、fs 4096 MSPS） | **SMA のラベルとタイルの対応は逆**（ADC_A = Tile 226 / slice 2）。[`../knowledge/hardware.md`](../knowledge/hardware.md) |
| 10 MHz | CLK_IN の SMA（LMK04828 の CLKin0） | 観測所の 10 MHz 基準（正弦波でよい） | **LPF を入れる**（下）。効いているかは状態レジスタでは分からない。1PPS の間隔（F-0）で ppm を見る |
| 1PPS | PPS Clk | 45m の +2.5 V / 100 µs をそのまま | **LPF を入れる**（下）。レベル変換・PULLUP は要らない |

**1PPS を ADC に常時入れない。** 1PPS を ADC に入れるのは、時刻の較正を測るとき（[`calibration.md`](calibration.md) の配線 P）だけ。

## 1PPS と 10 MHz の入口の LPF（常設）

- **Mini-Circuits BLP-10.7+（DC〜11 MHz）を、1PPS と 10 MHz の入力のコネクタの直前に 1 本ずつ**（直付け）。800 MHz 帯の携帯電話の上りの混信は 1PPS・10 MHz のケーブルから入る（[`../knowledge/pitfalls.md`](../knowledge/pitfalls.md)）
- 時刻の較正はこの LPF を含む（LPF の遅れ ≒ 71.6 ns）。**LPF を外す・替えたら、ボードの時刻の較正を測り直す**（[`calibration.md`](calibration.md)）
- LPF の後でも 10 MHz はロックする（10 MHz で挿入損失 0.65 dB）。1PPS の取り込み（F-0）も ±1 ビート
- LPF の混信への効きは、まだ測り終えていない（study-rfsoc proj026。電話では強さが揃わず、SG で測り直す）

## 入力レベル

| | 値 |
|---|---|
| フルスケール | 0 dBFS ≒ +5.8 dBm（ADC の口） |
| 振り切れの手前 | HOT で −10 dBFS 以下 |
| 運転 | HOT ≒ −16 dBFS・SKY ≒ −21 dBFS（HOT −10 dBm ≒ −16 dBFS） |

- **配線を変えたら、まず specd の STATUS の `tp_dbfs` でレベルを測る。** 分配器を替えただけで 18 dB 変わった実績がある（2026-10-21）
- ADC の前に 2〜4 GHz の BPF を入れる。下端は急峻に（2.0〜2.05 GHz が 2.05〜2.10 GHz に折り返す）
- 使わない分配器の口は 50 Ω で終端する。終端していない分配器は混信の入口になる

## 試験台の配線

判定（`test/acceptance/sam45-fine/`）で使う配線 N・N/S・P と、その日のレベルは [`../../test/acceptance/sam45-fine/README.md`](../../test/acceptance/sam45-fine/README.md) と性能評価の「測定系」（[`../performance/sam45-fine/`](../performance/sam45-fine/)）にある。
