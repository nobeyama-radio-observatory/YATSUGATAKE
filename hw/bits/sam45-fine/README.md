# SAM45-Fine

4 ADC × 2 窓（256〜8 MHz）・4096 点・40.96 ms ＋ ADC ごとの total power 1.024 ms。窓の分光に PFB（T = 4）。

**状態:** 移植中（M1）。study-rfsoc の proj021（`proj021-m0`）から置いた。`Makefile`・`build.tcl`・`program.tcl`・`sim/`・`tools/`・`src/`（FFT IP の設定・PFB の係数の ROM）。

系譜: proj017（1 本目）→ proj020（PFB T = 4）→ proj021（インターフェース v2）。
