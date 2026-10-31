# 2G-1-Fast

1 ADC × 1 コア。PFB（係数 ROM）＋ 16 レーンのレーン FFT（16384 点、2-for-1 で IP 8 個）で帯域 2048 MHz を 131072 ch（15.625 kHz）・10.24 ms。BIT_KIND 11。

**状態:** 移植中（M5 まで済み: sim の出力・ビルドの FDRI・実機の短い回帰が移植元と同じ。USR_ACCESS に commit を焼く）。study-rfsoc の proj033（`proj033-m0`、PROJ 0x0033_0100）から置いた。`Makefile`・`build.tcl`・`sim/`（2G-1-Fast の試験台と照合・FFT IP の模型）・`tools/`（係数とひねり係数の生成、OOC の道具）・`src/`（2G-1-Fast の部品 `g21/`・2-for-1 の部品 `s2_*.v`・`rec_fr.v` の写し）。計画は [`docs/migration-2g-1-fast.md`](../../../docs/migration-2g-1-fast.md)。

- **`rec_fr.v` は `src/rec_fr.v`（proj033 の版）を読む**。`hw/bits/2g-4/src/rec_fr.v` と同じ中身。`hw/common/rec_fr.v`（`np − 1'b1` で引く形）で作ると FDRI が移植元と変わるおそれがある
- **`s2_sep.v`・`s2_q.v`・`s2_chain.v` は 2G-4 の同じ名前のファイルと中身が違う**（寸法の既定と、`s2_chain` は丸めの式）。一本化は 2G-2 の移植の後
- 模型は `model/g2_model.py`（`make model-g21`）と **`model/s2_model_g21.py`**（`make model`）。2G-4 の `model/s2_model.py` とは別のもの
- Makefile の目標: ビルド（`make build IMPL=Performance_Explore`）・sim（`make sim-all` = 模型 2 本 ＋ sim 13 本、`build-sim-logs/` の 15 個で判定。`SIM_J` で並べる数。この PC で 1 時間前後）・表の作り直し（`gen`）・部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`）。proj033 までの試行の目標（`estimate`・`s2`・`survey`・`ooc-ref`）は外した（2g-1-fast/makefile-trim）
- 実装の戦略は **Performance_Explore**（`make build IMPL=Performance_Explore` → `build-PE/`）。移植元の bit はこれで作った（WNS +0.025 ns）。既定の戦略では閉じない（WNS −0.242 ns）
- `runs/` は git に入れない

系譜: proj024（2G-1-Fast の RTL）→ proj030（レーン FFT の 2-for-1）→ proj033（2G-1-Fast に 2-for-1）。PS は `sw/pynq/` の G21 の Backend（2G-4 の M5 で一本化）と `sw/pynq/g21cw.py`。
