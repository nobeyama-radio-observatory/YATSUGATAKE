# SAM45-Fine

4 ADC × 2 窓（256〜8 MHz）・4096 点・40.96 ms ＋ ADC ごとの total power 1.024 ms。窓の分光に PFB（T = 4）。

**状態:** 移植中（M1）。study-rfsoc の proj021（`proj021-m0`）から置いた。`Makefile`・`build.tcl`・`program.tcl`・`sim/`・`tools/`・`src/`（FFT IP の設定・PFB の係数の ROM）。

系譜: proj017（1 本目）→ proj020（PFB T = 4）→ proj021（インターフェース v2）。

## 版と BIT_REV

規則は [`../../../docs/release.md`](../../../docs/release.md) の「BIT_REV と版」。リリースごとに 1 行足す。

| 版 | BIT_REV | USR_ACCESS（タグの commit） | FDRI の sha256 | 性能評価 |
|---|---|---|---|---|
| v1.0.0 | 3 | `79528880` = commit 7952888 | `e095fa977cf9ebaa6f980a7a0f5f8bc0212ae6bed469ecdb047b6e18dfbc29f9` | [v1.0.0](../../../docs/performance/sam45-fine/v1.0.0.md) |
