# SpW8

4 ADC × 窓 8 本。コアごとに粗い PFB（64 MHz 間隔、全速 16 標本 / クロック）→ 窓の頭（NCO ＋ 半帯域 1 段目、8 本）→ 全窓で共有の後段（ddcb）→ 時分割の機関 3 本（PFB T 4 ＋ 4096 点 FFT ＋ 電力 ＋ 積分）。幅 128・64・32・16・8 MHz、4096 ch、10.24 ms。BIT_KIND 7。

**状態:** 移植中（M1、2026-11-03）。study-rfsoc の proj032 の b5 rev 10（`proj032-m0`、PROJ 0x0032_0300・BIT_REV 10）から置いた。計画は [`docs/migration-spw8.md`](../../../docs/migration-spw8.md)。

- `Makefile`・`build.tcl`・`build_post.tcl`: proj032 の `b5/` の 3 個。**実装の戦略は Performance_ExplorePostRoutePhysOpt**（`make IMPL=Performance_ExplorePostRoutePhysOpt` → `build-PEPRPO/`）。移植元の bit はこれで作った（WNS +0.016 ns）
- `src/spw/`: SpW の部品（.v 20 個）と係数の `.vh` 2 個。共通の部品は `../../common/`（`hw/common/`）を読む。窓は全部チップ内の履歴の枠（S 8）で、PL の DDR は使わない（`ddrr.v`・`ddrw.v` は機関の道の部品として入るが、b5 では DDR の窓を作らない）
- `sim/`: 試験台 12・照合 8・FFT IP の模型・PS の DDR の模型。**Makefile に sim の目標はまだ無い**（M2 の前に `spw8/sim-targets` で書き起こす）。今の回し方は `iverilog -g2012 -o tb -I src/spw -I ../../common -y src/spw -y ../../common sim/tb_<名前>.v && vvp -n tb`
- 模型は `model/win64_model.py`（仕様の模型）・`model/win64_fixed.py`（窓の頭と後段の整数の模型）・`model/pfb64_fixed.py`（粗い PFB の整数の模型）。係数の設計は **`model/spw8_coef.json`**（proj032 の `runs/m0_coef.json`）
- `tools/`: `test_spwplan.py`（窓の計画の机の上の試験）・`crc128_masks.py`（リングの CRC の係数を作る）
- `pynq/`: **移植元の試行の道具**（`spw_b5.py`・`spwfast.c`・`spwplan.py` と、それが読む `plring.py`・`s45core.py`・`extref.py`）。M4 の実機の回帰で使う。specd の SpW の Backend は M5b で `sw/pynq/` に入れる
- `runs/` は git に入れない

系譜: proj032 の b1（1 ADC・窓 6 本）→ b2（PL の DDR の窓）→ b4 rev 8（4 ADC・窓 6 本）→ **b5 rev 10（4 ADC・窓 8 本）**。
