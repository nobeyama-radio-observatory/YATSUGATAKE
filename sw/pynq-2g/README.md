# sw/pynq-2g — 2G-4 の PS 側（移植中）

**状態: 移植中（M1）。** study-rfsoc の proj036（`proj036-m0`）の `pynq/` のうち 2G-4 が使う 47 個と `tools/` の `amslog.py`・`level.py`・`loopsum.py`、proj031 の `tools/cuctl.py` を**バイト単位でそのまま**置いた。
`sw/pynq/`（SAM45-Fine・SAM45-Wide）とは別に置いているのは、M1〜M4 の回帰を移植元と同じ PS で行うため（[`docs/migration-2g-4.md`](../../docs/migration-2g-4.md) の原則 5）。

- 起動: `specd.py --g24 --bitfile <2G-4 の .bit> --clkin 0 --ref 10 --ring-mib 64 --prefault --fast --fast-ring`。束ねの C は `build_fast.sh` でボードの上で `libs45fast.so` を作る
- 係数 URAM の中身は `g24cu.py`（`make build`・sim の CU_WORDS もこれを読む）
- `sw/pynq/` との違い（同じ 20・違う 18・無い 13）: proj031・proj036 が変えたもの（specd・s45acq・s45core・s45fast・timebase・plring など）と 2G-4 の道具。`sw/pynq/` の M1 の後の変更（較正の鍵・USR_ACCESS など）はここには無い。specd の `--lmx-pwr` は proj036 のまま
- `sw/pynq/` への一本化は M5（2G の 3 本の Backend を一度に）
