# 2G-4

4 ADC × 4 コア。PFB（係数は 4 コアで共有の URAM `g24_cu`、PS が AXI4-Lite で書いて CRC で VERIFY）＋ 16 レーンのレーン FFT（4096 点、2-for-1 で IP 8 個 / コア）で全帯域 2048 MHz を 32768 ch（62.5 kHz）・10.24 ms。BIT_KIND 3。

**状態:** 移植中（M4 まで済み: sim の出力・ビルドの FDRI・実機の短い回帰が移植元と同じ）。study-rfsoc の proj031 rev 2（`proj031-m0`、PROJ 0x0031_0200）から置いた。`Makefile`・`build.tcl`・`build_post.tcl`・`sim/`（2G-4 の試験台と照合・FFT IP の模型）・`tools/`（係数とひねり係数・CRC の式の生成、OOC の道具）・`src/`（2G-4 の部品 `g24/`・2-for-1 の部品 `s2_*.v`・共有のファイルの写し）。計画は [`docs/migration-2g-4.md`](../../../docs/migration-2g-4.md)。

- `core_cmn.v`・`rec_fr.v`・`tp_core.v` は `hw/common/` の版を読む（2026-10-29 に一本化。proj024 で足した口 `F0_EXT`・`NCH` は既定では Fine・Wide と同じ式）。一本化で rec_fr の `np − 1` を `np − 1'b1` にしたので、**合成が移植元（proj031）と変わり、bit の FDRI は移植元と別物**（下）
- Makefile の目標: ビルド（`make build IMPL=Performance_ExtraTimingOpt` → `build-PETO/`）・`post`・sim（`make sim-all` = 模型 3 本 ＋ sim 15 本、`build-sim-logs/` の 18 個で判定。`SIM_J` で並べる数）・表の作り直し（`gen`・`gen-crc`）・部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`・`ooc-cu`）。proj031 までの試行の目標（`coef-ooc`・`wide-hier`・`ooc-ref`）は外した（2g-4/makefile-trim）
- `make build` は先に `make model-cu` を回し、`runs/model_cu.txt` の COEF_CRC（期待 0x891BE197）を bit に焼く。`runs/` は git に入れない
- 実装の戦略は **`IMPL=Performance_ExtraTimingOpt`**（2026-10-29 から。一本化の後、既定の戦略では WNS −0.352 ns で閉じない。PETO で WNS +0.046737・WHS +0.009404 ns、FDRI `a9a01b81…5488`）。移植元と M3〜M5 の bit は既定の戦略（WNS +0.047 ns・FDRI `f05e1f62…3b1c`）
- 親の Vivado が `impl_1` の後（設計を開き直す所）で落ちたら `make post IMPL=Performance_ExtraTimingOpt`（合成・実装をやり直さずに照合・報告・`build-PETO/` への写し）。2026-10-29 の PETO はこれで仕上げた

系譜: proj027（2G-4 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj031（係数の共有 URAM）。PS は proj036（束ねの取得の C）。
