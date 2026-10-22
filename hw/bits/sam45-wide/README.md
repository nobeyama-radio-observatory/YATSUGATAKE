# SAM45-Wide

4 ADC × 1 コア。PFB（T = 4）＋ 16 レーンの全帯域 FFT 32768 点（固定長）、電力の後の ch の束ね B = 4 / 2 / 1 で全帯域 2048 MHz（500 kHz）/ 1 GHz × 2（250 kHz）/ 512 MHz × 2（125 kHz）を SLICE の流れに。4096 ch・40.96 ms。モードは ADC ごとに独立。

**状態:** 移植中（M1）。study-rfsoc の proj023（`proj023-m0`）から置いた。`Makefile`・`build.tcl`・`program.tcl`・`sim/`（Wide の試験台と照合）・`tools/`・`src/`（FFT IP の設定・係数とひねり係数の ROM の中身）。計画は [`docs/migration-sam45-wide.md`](../../../docs/migration-sam45-wide.md)。

- `cmul.v`・`rec_fr.v` は `hw/common/` の版を使う（proj023 で足した口 SH・W7HI は既定では今までと同じ式。M1〜M4 の間は Wide の側に写しを置いていた。sam45-wide/common-unify で一本化）
- Makefile の目標: ビルド（`make IMPL=Performance_Explore`）・`prog`・`id`・`ps-preset`・`survey`・dcp の道具（`worst-paths`・`physopt`・`floorplan`・`gb-cdc`）・sim（`make sim-all` = `model-wide` ＋ `sim-wpfb`・`sim-wch`・`sim-wsp`・`sim-wco`・`sim-ws45`・`sim-wds`、28 個のログが「結果: 全部通過」）・係数とひねり係数の ROM の作り直し（`wide-coef`・`wide-tw`）。proj021 から引き継いでいた SAM45-Fine の目標は外した（sam45-wide/makefile-trim）
- 実装の戦略は **`IMPL=Performance_Explore`**（移植元の bit はこれで作った。WNS +0.0007 ns）

系譜: proj014（レーン FFT）→ proj022（模型と見積もり）→ proj023（RTL、インターフェース v2 の上で）。
