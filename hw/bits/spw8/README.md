# SpW8

4 ADC × 窓 8 本。コアごとに粗い PFB（64 MHz 間隔、全速 16 標本 / クロック）→ 窓の頭（NCO ＋ 半帯域 1 段目、8 本）→ 全窓で共有の後段（ddcb）→ 時分割の機関 3 本（PFB T 4 ＋ 4096 点 FFT ＋ 電力 ＋ 積分）。幅 128・64・32・16・8 MHz、4096 ch、10.24 ms。BIT_KIND 7。

**状態:** 移植中（M7 のリリースの準備、2026-11-05。判定 11 が通過、性能評価は [`docs/performance/spw8/v1.0.0.md`](../../../docs/performance/spw8/v1.0.0.md)、設計は [`docs/design/spw8/`](../../../docs/design/spw8/)）。study-rfsoc の proj032 の b5 rev 10（`proj032-m0`、PROJ 0x0032_0300・BIT_REV 10）から置いた。計画は [`docs/migration-spw8.md`](../../../docs/migration-spw8.md)。

- `Makefile`・`build.tcl`・`build_post.tcl`: proj032 の `b5/` の 3 個。**実装の戦略は Performance_ExplorePostRoutePhysOpt**（`make IMPL=Performance_ExplorePostRoutePhysOpt` → `build-PEPRPO/`）。移植元の bit はこれで作った（WNS +0.016 ns）。M5c から `make build` は USR_ACCESS に commit（[31:4]）と汚れ（[0]）を焼き、書き出した .bit を `sw/pynq/bitinfo.py --expect` で読み返す（`USR_ACCESS=none` で焼かない）。`OUTDIR=…` で出力先を分けられる
- `src/spw/`: SpW の部品（.v 20 個）と係数の `.vh` 2 個。共通の部品は `../../common/`（`hw/common/`）を読む。窓は全部チップ内の履歴の枠（S 8）で、PL の DDR は使わない（`ddrr.v`・`ddrw.v` は機関の道の部品として入るが、b5 では DDR の窓を作らない）
- `sim/`: 試験台 12・照合 8・FFT IP の模型・PS の DDR の模型。**`make sim-all`**（模型 3 ＋ sim 11、`SIM_J` 本ずつ並べる。重いのは sim-core・sim-front で 1 時間半ほど）。成否は make の終了状態でなく、`build-sim-logs/` の各ログの最後の行「sim-…: 全部通過」で読む。`make sim-rdmux`（b3 rev 6 の読み手のまとめ、b5 には入っていない）は sim-core の後に回し、「記録どおり」の不合格を照らす。出力は `build-sim/<変種>/`
- 模型は `model/win64_model.py`（仕様の模型）・`model/win64_fixed.py`（窓の頭と後段の整数の模型）・`model/pfb64_fixed.py`（粗い PFB の整数の模型）。係数の設計は **`model/spw8_coef.json`**（proj032 の `runs/m0_coef.json`）
- `tools/`: `test_spwplan.py`（窓の計画の机の上の試験）・`crc128_masks.py`（リングの CRC の係数を作る）・`spw_recv_check.py`（specd から受けた記録を論理の窓で照らす: CW の ch・双子・記録の頭。M5b）
- `pynq/`: **移植元の試行の道具**（`spw_b5.py`・`spwfast.c`）。M4 の実機の回帰で使う。読む `spwplan.py`・`plring.py`・`s45core.py`・`extref.py` は M5b から `sw/pynq/` の版（ボードでは同じ場所に写す）。specd の SpW の Backend は `sw/pynq/`（`specd.py --spw`）
- `runs/` は git に入れない

系譜: proj032 の b1（1 ADC・窓 6 本）→ b2（PL の DDR の窓）→ b4 rev 8（4 ADC・窓 6 本）→ **b5 rev 10（4 ADC・窓 8 本）**。
