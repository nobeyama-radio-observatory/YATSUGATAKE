# 2G-1-Fast の設計

1 ADC × 1 コア。全帯域（2048 MHz）を PFB（T = 4、係数は ROM）＋ 16 レーンのレーン FFT（16384 点、2-for-1）で分け、131072 ch（15.625 kHz）・10.24 ms ＋ TP 1.024 ms。コアの入力の ADC（SRC）は 4 本から選ぶ。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)、FULL の約束は [`../../spec/interface.md`](../../spec/interface.md) の 2.1・2.4・4.5・6.。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 11・BIT_REV 1・PROJ 0x0033_0100。IF_ID 0x020B_0101（コア）・0x020B_0102（time_core）。PS は PROJ を照らさない（移植の M5 の決めること 4、案 A） |
| コア | `s45_core_0` の 1 個（module reference の `g21_s45_core` = core_cmn ＋ g21_core（FULL、s 0）＋ raw_core（RAW、s 1））。FULL・RAW の入力はそれぞれの `axis_sel4`（full_sel・raw_sel）で ADC A〜D から選ぶ |
| 分光 | PFB T = 4 → 16 レーンのレーン FFT 16384 点（実のレーン 2 本を複素の IP 1 個に = 2-for-1、IP 8 個。FFT 262144 点、FRAME_BEATS 16384 = 64 µs）→ 電力 → 積分。131072 ch、第 2 ナイキスト（ch c の IF = 4096 − c·df MHz） |
| 2-for-1 | `s2_sep`（IP 8 個の出口を実のレーン 16 本に分ける。加減算だけ）→ `s2_chain`（丸め・ひねり係数・16 点 DFT の鎖）→ `s2_q`（均しの待ち行列。1 拍に 1 行ずつ電力にして積分器 `g21_acc` へ）。2G-4 の同じ名前のファイルと中身が違う（寸法の既定と、`s2_chain` は丸めの式）ので `hw/bits/2g-1-fast/src/` に置く。一本化は 2G-2 の移植の後 |
| 係数 | PFB の係数は `g21_coef`（前半・後半の表 `g21_coef_lo.hex`・`g21_coef_hi.hex` を 2 ポートの ROM にし、線形補間で作る）、ひねり係数は `g21_tw`（`g21_tw_a.hex`・`g21_tw_b.hex`）。**どちらも bit に焼く**（2G-4 の係数 URAM と違い、PS は書かない） |
| SHIFT・SRC | コアに 1 つ。SHIFT は RUN で、SRC は次の WRST で取り込む |
| 起動 | 束ねの見張り r = 2·G = 1,048,576（窓 A0。M4〜M6 の STATUS の `bund_r`） |
| ダンプ | BASE 10.24 ms（PL、nacc 160 × 16384 ビート）、tint は specd が C の道（`--fast-ring`）で束ねる（既定 40.96 ms、ネットワークの最小 20.48 ms） |
| データの道 | レコード（1 MiB × 1 / 10.24 ms = 102.4 MB/s）→ `s45_ring_0`（入口 1 本）→ DDR（リング 64 MiB）。PS はリングの上のレコードを C（`libs45fast.so`）で照らし・束ね・逆順・float32・CRC |
| TP | 2 本（FULL の TP = SRC の ADC、コアの TP = ADC_A）。PS が ADC ごとの欄に振る（SRC が A なら 1 本） |
| クロック | RFDC 341.33 MHz × 12 サンプル → DSP 256 MHz × 16 サンプル（SAM45-Wide と同じギアボックス。ADC → コアの道は共通の道 1） |
| 時刻 | FULL（PFB 入り）の D_eff = D_S ＋ 1.5·L = 1 ＋ 24576 ビート = 24577 ビート ≒ 96.0 µs（sim-g21ds）。`CAL` に行は無い（[`../../spec/timing.md`](../../spec/timing.md)） |
| ビルド | `hw/bits/2g-1-fast/`（**`make build IMPL=Performance_Explore`** → `build-PE/`。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、Performance_Explore）

| | 値 |
|---|---|
| WNS / WHS | +0.025345 ns / +0.009647 ns |
| LUT / FF | 70,248（16.52 %）/ 123,411（14.51 %） |
| DSP / BRAM タイル / URAM | 628（PFB 144・IP 264・ひねり係数 60・s2_chain 96・s2_q 16・TP 48）/ 586.5 / 48 |
| `report_cdc` | CDC-3 Info 60・CDC-6 Warning 2・CDC-15 Warning 3,137 |

移植元（study-rfsoc proj033-m0 の `build-PE/`）と FDRI が同じ（[`../../migration-2g-1-fast.md`](../../migration-2g-1-fast.md) の M3・M5）。**WNS +0.025 ns で薄い**。既定の戦略では閉じない（WNS −0.242 ns）。RTL・置き場所を変えたら `-1` で閉じることを必ず確かめる（閉じなくなったら proj033 の B-2: 記憶のカスケードに段を足す）。rec_fr は `src/rec_fr.v`（移植元の版。2G-4 の写しと同じ中身）を読む。

## 経緯と詳しい説明

系譜は proj024（2G-1-Fast の RTL）→ proj030（レーン FFT の 2-for-1）→ proj033（2G-1-Fast に 2-for-1。DSP 924 → 628・VCCINT 16.8 → 13.3 A、精度と機能は同じ）。PS は 2G-4 の M5 で一本化した `sw/pynq/` の G21Backend。設計の決めと sim の照合は study-rfsoc の各 proj の README、模型は `model/g2_model.py`・`g21_fixed.py`・`s2_model_g21.py`（sim の照合が読む）。

## 性能

実機で測った値は [`../../performance/2g-1-fast/`](../../performance/2g-1-fast/)、判定は [`../../../test/acceptance/2g-1-fast/`](../../../test/acceptance/2g-1-fast/)。
