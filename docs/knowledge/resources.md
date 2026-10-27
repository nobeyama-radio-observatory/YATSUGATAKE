# 資源の内訳 — 構成要素ごとの BRAM・URAM・DSP

5 本の bit（SAM45-Fine・SAM45-Wide・2G-1・2G-2・2G-4）で、BRAM・URAM・DSP を**どの構成要素が使っているか**を並べた（2026-10-27）。
点数や窓の数を増やす案を比べるとき、何が壁になるかを見るためのもの。bit ごとの合計の資源は各 bit の `performance/` が正で、ここはその内訳。

- 数は**全コアの合計**。BRAM は RAMB36 に換算（RAMB18 は 0.5）。チップは XCZU48DR（BRAM 1,080・URAM 80・DSP 4,272）
- 配置配線の後のチェックポイントを開き、`report_utilization -hierarchical -hierarchical_depth 9` を読んで分けた（下の「出し方」）
- 合計は 5 本とも各 bit の記録（`performance/`・study-rfsoc の `INDEX.md`）と一致した

## 対象

| bit | 置き場所 | ビルド | `.bit` の sha256 |
|---|---|---|---|
| SAM45-Fine | YATSUGATAKE `hw/bits/sam45-fine/` | `build/`（既定の戦略） | `e12789bbc23dd6744b25af73eb46ac24df15ffc370977979c6287d7925c1891d`（v1.0.0 の配る .bit） |
| SAM45-Wide | YATSUGATAKE `hw/bits/sam45-wide/` | `build-PE/`（Performance_Explore） | `a31fccde6a0e93624047fcc0dde39e955845844cb71a0a6a11ecc9a8c4017069`（v1.0.0 の配る .bit） |
| 2G-1 | study-rfsoc proj024（タグ proj024-m0） | `build-PE/` | `fdb04d804fb50b30afd66f1ba56a45b3bf1929e5d2d4a7cc3a2016faba714dd8` |
| 2G-2 | study-rfsoc proj025（タグ proj025-m0） | `build/`（既定の戦略） | `de3ee45395a393c91c4cbacf0e21a9e1e5cc0f25ff4a00bf76bacb3a9cf30bf9` |
| 2G-4 | study-rfsoc proj027（進行中） | `build-PE/`（2f ビルド 1） | `8b35ecd411fb100bf3190169cbc46bcfb6ff22ae788aa6ddfa26b4fdf3eed511` |

2G の 3 本はまだ YATSUGATAKE に移していない。ビルドは実機に載せたもの。

## DSP

| 構成要素 | Fine | Wide | 2G-1 | 2G-2 | 2G-4 |
|---|---|---|---|---|---|
| 前段の PFB（Fine は 128 MHz の粗い PFB `pfb_core`、ほかは全帯域の T = 4） | **1,088** | 320 | 144 | 288 | 576 |
| DDC（`ddc_core`、窓ごと 72） | 576 | – | – | – | – |
| FFT の IP | 240（4096 点 × 8 窓） | **1,728**（レーン × 64） | **528**（× 16） | **1,056**（× 32） | **1,728**（× 64） |
| 鎖（dft16 ＋ cmul）＋ ひねり係数 | – | 576 | 204 | 408 | 816 |
| 窓の PFB T = 4 ほか（`wspec_core` の FFT の外） | 96 | – | – | – | – |
| TP | 96 | 96 | 48 | 96 | 192 |
| **計** | 2,096（49.1 %） | 2,720（63.7 %） | 924（21.6 %） | 1,848（43.3 %） | 3,312（77.5 %） |

- Fine の粗い PFB は 1 ADC で 272（分岐の和 192 ＋ dft16f 2 × 32 ＋ 窓ごとの実数化 4 × 2）
- 2G の前段 PFB はコアごとに係数の補間 64 ＋ 分岐の和 80。鎖はコアごとに 144 ＋ ひねり係数の積（hi × lo）60
- 2G の TP はコアに 2 つ（`u_cmn` の中と `u_full` の中、各 24）

## BRAM

| 構成要素 | Fine | Wide | 2G-1 | 2G-2 | 2G-4 |
|---|---|---|---|---|---|
| 前段の PFB（係数 ＋ 履歴） | 0 | 44（係数 ROM、4 コアで共有） | **306.5** | **307** | **308** |
| DDC（NCO の ROM） | 32 | – | – | – | – |
| FFT の IP | **120**（15 / 個） | **512**（8 / 個） | **344**（21.5 / 個） | **416**（13 / 個） | **448**（7 / 個） |
| ひねり係数の ROM | – | 116 | 11 | 23 | 46 |
| 窓の PFB の係数 ROM | 32 | – | – | – | – |
| 積分器 | （URAM） | 128 | （URAM） | （URAM） | （URAM） |
| TP | 8 | 8 | 2 | 4 | 8 |
| スナップショット（`win_core` の `snap_mem`） | 32 | – | – | – | – |
| RAW ＋ リング | 9.5 | 9.5 | 9.5 | 9.5 | 32（RAW がコアごと） |
| **計** | 233.5（21.6 %） | 817.5（75.7 %） | 673（62.3 %） | 759.5（70.3 %） | 842（78.0 %） |

## URAM

| | Fine | Wide | 2G-1 | 2G-2 | 2G-4 |
|---|---|---|---|---|---|
| 使い道 | 窓の溜め（5 面）＋ 積分器（7 / 窓 × 8） | 前段 PFB の履歴（10 / コア） | 積分器 | 積分器 | 積分器 |
| **計** | **56（70 %）** | 40（50 %） | 48（60 %） | 48（60 %） | 48（60 %） |

## 読めること

- **Wide と 2G-4 の DSP の最大はレーン FFT の IP**（1,728、チップの 40 %）。study-rfsoc proj030（実のレーン 2 本を複素の IP 1 個に）が減らすのはここ
- **Fine の DSP の半分は粗い PFB**（1,088）。窓を 1 つ足すと DSP ≒ 118（DDC 72 ＋ 窓の分光 42 ＋ 実数化 4）・BRAM 23・URAM 7 が増える。**窓の数の壁は URAM**（7 / 窓で 80 なら 11 窓ほど）
- **2G の前段 PFB の履歴（BRAM ≒ 300）と積分器（URAM 48）は、コアの数によらず一定**（全帯域と総 ch 数で決まる）。コアの数で増えるのは FFT の IP・鎖・TP
- **2G-1 は DSP 22 % で、壁は BRAM（62 %）と URAM（60 %）**。点数を増やす壁はチップ内の記憶（study-rfsoc proj028 の動機）
- FFT の IP 1 個の BRAM は点数に比例しない（16384 点 21.5・8192 点 13・4096 点 7〜8）
- 確かめていないこと: 2G の TP がコアに 2 つあるのが意図どおりか（2G-4 で DSP 96）。2G-4 だけ RAW がコアごとにある理由

## 出し方

チェックポイントを開いて報告を出すだけで、ビルドの成果物は変えない。5 本を並べて回して 1 本 3〜5 分（メモリは 1 本 6〜12 GB）。

```tcl
# rep.tcl — vivado -mode batch -nojournal -nolog -source rep.tcl -tclargs <routed.dcp> <out.rpt>
set dcp [lindex $argv 0]; set out [lindex $argv 1]
open_checkpoint $dcp
report_utilization -hierarchical -hierarchical_depth 9 -file $out
```

チェックポイントは `<build>/vivado/<proj>.runs/impl_1/system_wrapper_routed.dcp`。ビルドが書く `utilization_hier.rpt` は depth 4 で、コアの中の部品まで届かない。
