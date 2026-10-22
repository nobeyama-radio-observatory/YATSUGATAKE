# SAM45-Wide

4 ADC × 1 コア。PFB（T = 4）＋ 16 レーンの全帯域 FFT 32768 点（固定長）、電力の後の ch の束ね B = 4 / 2 / 1 で全帯域 2048 MHz（500 kHz）/ 1 GHz × 2（250 kHz）/ 512 MHz × 2（125 kHz）を SLICE の流れに。4096 ch・40.96 ms。モードは ADC ごとに独立。

**状態:** 移植中（M1）。study-rfsoc の proj023（`proj023-m0`）から置いた。`Makefile`・`build.tcl`・`program.tcl`・`sim/`（Wide の試験台と照合）・`tools/`・`src/`（FFT IP の設定・係数とひねり係数の ROM の中身・Fine と共有のファイルの写し `cmul.v`・`rec_fr.v`）。計画は [`docs/migration-sam45-wide.md`](../../../docs/migration-sam45-wide.md)。

- **`src/cmul.v`・`src/rec_fr.v` は `hw/common/` の同じ名前のファイルの proj023 の版**（口 SH・W7HI を足した。既定では今までと同じ式）。この bit は必ずこちらを使う。`hw/common/` への一本化は M1 の後の別の PR
- **Makefile には proj021 から引き継いだ SAM45-Fine の目標（sim-win・sim-ddc・sim-spec-all・sim-ring など、`sim-all` も）が残っていて、M1 では動かない**（そのファイルを移していない）。Wide の sim は `make model-wide sim-wpfb sim-wch sim-wsp sim-wco sim-ws45 sim-wds`。Fine の目標を外すのは M1 の後の別の PR
- 実装の戦略は **`IMPL=Performance_Explore`**（移植元の bit はこれで作った。WNS +0.0007 ns）

系譜: proj014（レーン FFT）→ proj022（模型と見積もり）→ proj023（RTL、インターフェース v2 の上で）。
