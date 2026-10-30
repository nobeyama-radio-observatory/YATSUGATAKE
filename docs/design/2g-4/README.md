# 2G-4 の設計

4 ADC × 4 コア。コアごとに全帯域（2048 MHz）を PFB（T = 4）＋ 16 レーンのレーン FFT（4096 点、2-for-1）で分け、32768 ch（62.5 kHz）・10.24 ms ＋ ADC ごとの TP 1.024 ms。PFB の係数は 4 コアで共有の URAM に置き、PS が起動のときに書く。コアの入力の ADC（SRC）はコアごとに選ぶ。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)、FULL の約束は [`../../spec/interface.md`](../../spec/interface.md) の 2.1・2.4・4.5・6.。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 3・BIT_REV 1・PROJ 0x0031_0200。IF_ID 0x0203_0101（コア）・0x0203_0102（time_core） |
| コア | `s45_core_0..3`（module reference の `g24_s45_core` = core_cmn ＋ g24_core（FULL、s 0）＋ raw_core（RAW、s 1））。4 コアとも RAW の流れを持つ。FULL・RAW の入力はコアごとの `axis_sel4` で ADC A〜D から選ぶ（4 コアに同じ ADC も可） |
| 分光 | PFB T = 4 → 16 レーンのレーン FFT 4096 点（実のレーン 2 本を複素の IP 1 個に = 2-for-1、IP 8 個 / コア。FFT 65536 点、FRAME_BEATS 4096 = 16 µs）→ 電力 → 積分。32768 ch、第 2 ナイキスト（ch c の IF = 4096 − c·df MHz） |
| 係数 | 共有の URAM `g24_cu_0`（URAM 8、4096 行 × 576 bit。ポート B が係数の対称の半分を読む）。**URAM は初期値を持てない**ので、Overlay の後に PS が `g24_coef_lo.hex`・`g24_coef_hi.hex`（bit の隣）を AXI4-Lite で書き、PL が読み直した CRC が焼き込みの COEF_CRC（0x891BE197、`make model-cu`）と合えば OK を立てる（VERIFY、≒ 0.73 s）。書き・VERIFY で OK が落ちる。走っている間に落ちるとコアの flags bit 0、PS は START の前に OK を読み直して断る（判定 CU、道具 `cuctl.py`） |
| SHIFT・SRC | コアに 1 つ。SHIFT は RUN で、SRC は次の WRST で取り込む |
| 起動 | フレームの頭を T の格子に置く（T ≡ K_F mod 4096、F0 の格子は 128 フレーム = 2.048 ms）。束ねの見張り r = 2·G = 1,048,576（4 窓とも。M5・M6 の STATUS の `bund_r`） |
| ダンプ | BASE 10.24 ms（PL、nacc 640 × 4096 ビート）、tint は specd が C の道（`--fast-ring`）で束ねる（既定 40.96 ms、ネットワークの最小 20.48 ms） |
| データの道 | レコード（256 KiB × 4 / 10.24 ms = 102.4 MB/s）→ `s45_ring_0`（入口 4 本）→ S_AXI_HP0_FPD → DDR（リング 64 MiB）。PS はリングの上のレコードを C（`libs45fast.so`）で照らし・束ね・逆順・float32・CRC |
| TP | コアに 2 つ（FULL の TP = SRC の ADC、コアの TP = コアの ADC）。PS が ADC ごとの欄に振る（同じ ADC の 2 本は 1 欄） |
| クロック | RFDC 341.33 MHz × 12 サンプル → DSP 256 MHz × 16 サンプル（SAM45-Wide と同じギアボックス。ADC → コアの道は共通の道 1） |
| 時刻 | FULL（PFB 入り）の D_eff = D_S ＋ 1.5·L = 1 ＋ 6144 ビート = 6145 ビート ≒ 24.0 µs（sim-g24ds）。CAL は (3, 1)（[`../../spec/timing.md`](../../spec/timing.md)） |
| ビルド | `hw/bits/2g-4/`（`make build`、**既定の戦略**。先に `make model-cu` で COEF_CRC を作る。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、既定の戦略）

| | 値 |
|---|---|
| WNS / WHS | +0.047165 ns / +0.000000 ns |
| LUT / FF | 201,656（47.42 %）/ 345,687（40.64 %） |
| DSP / BRAM タイル / URAM | 2,064 / 692 / 56（g24_cu_0 に 8） |
| `report_cdc` | CDC-3 Info 119・CDC-6 Warning 5・CDC-15 Warning 3,137 |

移植元（study-rfsoc proj031 rev 2 の `build/`）と FDRI が同じ（[`../../migration-2g-4.md`](../../migration-2g-4.md) の M3・M5、`hw/common/` の一本化の後の作り直しも）。**WHS が 0.000 ns で薄い**。`hw/common/rec_fr.v` の版（`np − 1'b1`）では、どの戦略でも作り直しで閉じなかった（WNS −0.23〜−0.35 ns）ので、2G-4 は rec_fr だけ `src/` の写し（移植元の版）を読む。RTL・置き場所を変えたら `-1` で閉じることを必ず確かめる。

## 経緯と詳しい説明

系譜は proj027（2G-4 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj031（係数の共有 URAM）。PS は proj036（束ねの取得の C）。設計の決めと sim の照合は study-rfsoc の各 proj の README、模型は `model/g24_model.py`・`g24_fixed.py`・`s2_model.py`・`cu_model.py`（sim の照合が読む）。

## 性能

実機で測った値は [`../../performance/2g-4/`](../../performance/2g-4/)、判定は [`../../../test/acceptance/2g-4/`](../../../test/acceptance/2g-4/)。
