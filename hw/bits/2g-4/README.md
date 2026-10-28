# 2G-4

4 ADC × 4 コア。PFB（係数は 4 コアで共有の URAM `g24_cu`、PS が AXI4-Lite で書いて CRC で VERIFY）＋ 16 レーンのレーン FFT（4096 点、2-for-1 で IP 8 個 / コア）で全帯域 2048 MHz を 32768 ch（62.5 kHz）・10.24 ms。BIT_KIND 3。

**状態:** 移植中（M1）。study-rfsoc の proj031 rev 2（`proj031-m0`、PROJ 0x0031_0200）から置いた。`Makefile`・`build.tcl`・`build_post.tcl`・`sim/`（2G-4 の試験台と照合・FFT IP の模型）・`tools/`（係数とひねり係数・CRC の式の生成、OOC の道具）・`src/`（2G-4 の部品 `g24/`・2-for-1 の部品 `s2_*.v`・共有のファイルの写し）。計画は [`docs/migration-2g-4.md`](../../../docs/migration-2g-4.md)。

- **`src/core_cmn.v`・`src/rec_fr.v`・`src/tp_core.v` は `hw/common/` の同じ名前のファイルの proj031 の版**（proj024 で口 `F0_EXT`・`NCH` を足した。既定では今までと同じ式）。この bit は必ずこちらを使う。`hw/common/` への一本化は M1 の後の別の PR
- **Makefile には試行の目標（`coef-ooc`・`wide-hier`・`ooc-ref`）が残っていて、M1 では動かない**（study-rfsoc の git・proj023 のチェックポイント・移していない `ref/` を読む）。`sim-all` は 1a〜1d の 4 つだけ。外すのは M1 の後の別の PR
- `make build` は先に `make model-cu` を回し、`runs/model_cu.txt` の COEF_CRC（期待 0x891BE197）を bit に焼く。`runs/` は git に入れない
- 実装の戦略は**既定**（移植元の bit はこれで作った。WNS +0.047 ns・WHS +0.000 ns）

系譜: proj027（2G-4 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj031（係数の共有 URAM）。PS は proj036（束ねの取得の C）。
