# 2G-2 の設計

2 ADC × 2 コア。コアごとに全帯域（2048 MHz）を PFB（T = 4、係数は ROM）＋ 16 レーンのレーン FFT（8192 点、2-for-1）で分け、65536 ch（31.25 kHz）・10.24 ms ＋ TP 1.024 ms。コアの入力の ADC（SRC）はコアごとに 4 本から選ぶ（2 コアに同じ ADC も可）。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)、FULL の約束は [`../../spec/interface.md`](../../spec/interface.md) の 2.1・2.4・4.5・6.。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 10・BIT_REV 1・PROJ 0x0034_0100。IF_ID 0x020A_0101（コア）・0x020A_0102（time_core）。PS は PROJ を照らさない（移植の M0 の決めること 3、案 A） |
| コア | `s45_core_0`・`s45_core_1`（module reference の `g22_s45_core` = core_cmn ＋ g22_core（FULL、s 0）。コア 0 だけ raw_core（RAW、s 1）を持つ = NSTREAM 2、コア 1 は NSTREAM 1）。FULL・RAW の入力はそれぞれの `axis_sel4` で ADC A〜D から選ぶ |
| 分光 | PFB T = 4 → 16 レーンのレーン FFT 8192 点（実のレーン 2 本を複素の IP 1 個に = 2-for-1、IP 8 個 / コア。FFT 131072 点、FRAME_BEATS 8192 = 32 µs）→ 電力 → 積分。65536 ch、第 2 ナイキスト（ch c の IF = 4096 − c·df MHz） |
| 2-for-1 | `s2_sep`（IP 8 個の出口を実のレーン 16 本に分ける）→ `s2_chain`（2Y の丸め・ひねり係数・16 点 DFT の鎖、そろった行だけ）→ `s2_q`（均しの待ち行列。1 拍に 1 行ずつ電力にして）→ 積分器 `g22_acc`（全 ch、URAM）。組み立ては `g22_spec.v`（2-for-1 の前の鎖 `g22_chain.v` は sim-g22ch が読むだけで、bit には入らない）。`s2_sep.v`・`s2_q.v`・`s2_chain.v` は 2G-4・2G-1-Fast の同じ名前のファイルと中身が違うので `hw/bits/2g-2/src/` に置く。`s2_sep`・`s2_q` の一本化は 2G-2 の移植の後（別の PR） |
| 係数 | PFB の係数は `g22_coef`（`g22_coef_lo.hex`・`g22_coef_hi.hex` の ROM）、ひねり係数は `g22_tw`（`g22_tw_a.hex`・`g22_tw_b.hex`）。コアごとに 1 組で、**どちらも bit に焼く**（2G-4 の係数 URAM と違い、PS は書かない） |
| SHIFT・SRC | コアに 1 つ。SHIFT は RUN で、SRC は次の WRST で取り込む |
| 起動 | 束ねの見張り r = 2·G = 1,048,576（窓 A0・B0。M6 の STATUS の `bund_r`）。2 窓の DUMP_T は同じ RUN_F0 から揃う |
| ダンプ | BASE 10.24 ms（PL、nacc 320 × 8192 ビート）、tint は specd が C の道（`--fast-ring`）で束ねる（既定 40.96 ms、ネットワークの最小 20.48 ms） |
| データの道 | レコード（512 KiB × 2 / 10.24 ms = 102.4 MB/s）→ `s45_ring_0`（入口 2 本）→ DDR（リング 64 MiB）。PS はリングの上のレコードを C（`libs45fast.so`）で照らし・束ね・逆順・float32・CRC。rec_fr は `src/rec_fr.v`（移植元の版。2G-1-Fast・2G-4 の写しと同じ中身） |
| TP | コアに 2 つ（FULL の TP = SRC の ADC、コアの TP = コアの ADC）。PS が ADC ごとの欄に振る（`s45acq.g22_tp_slots`、同じ ADC の 2 本は 1 つの欄に混ぜない） |
| クロック | RFDC 341.33 MHz × 12 サンプル → DSP 256 MHz × 16 サンプル（SAM45-Wide と同じギアボックス。ADC → コアの道は共通の道 1） |
| 時刻 | FULL（PFB 入り）の D_eff = D_S ＋ 1.5·L = 1 ＋ 12288 ビート = 12289 ビート ≒ 48.0 µs（sim-g22ds）。`CAL` に行は無い（[`../../spec/timing.md`](../../spec/timing.md)） |
| ビルド | `hw/bits/2g-2/`（`make build`、**既定の戦略** → `build/`。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、既定の戦略）

| | 値 |
|---|---|
| WNS / WHS | +0.073585 ns / +0.009528 ns |
| LUT / FF | 114,545（26.93 %）/ 199,476（23.45 %） |
| DSP / BRAM タイル / URAM | 1,256 / 635.5 / 48 |
| `report_cdc` | CDC-3 Info 75・CDC-6 Warning 3・CDC-15 Warning 3,137 |

移植元（study-rfsoc proj034-m0 の `build/`）と FDRI が同じ（[`../../migration-2g-2.md`](../../migration-2g-2.md) の M3・M5）。Performance_Explore（WNS +0.032 ns）より既定の戦略のほうが余裕があるので既定で作る。RTL・置き場所を変えたら `-1` で閉じることを必ず確かめる。

## 経緯と詳しい説明

系譜は proj025（2G-2 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj034（2G-2 に 2-for-1。DSP 1,848 → 1,256・LUT 37.1 → 26.9 %・BRAM 759.5 → 635.5・VCCINT 25.1 → 18.8 A、精度と機能は同じ）。PS は 2G-4 の M5 で一本化した `sw/pynq/` の G22Backend と `g22cw.py`。設計の決めと sim の照合は study-rfsoc の各 proj の README、模型は `model/g22_model.py`・`g22_fixed.py`・`s2_model_g22.py`（sim の照合が読む）。

## 性能

実機で測った値は [`../../performance/2g-2/`](../../performance/2g-2/)、判定は [`../../../test/acceptance/2g-2/`](../../../test/acceptance/2g-2/)。
