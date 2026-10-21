# sw/pynq-wide — SAM45-Wide の PS 側（移植中）

**状態: 移植中（M1）。** study-rfsoc の proj023（`proj023-m0`）の `pynq/` を**バイト単位でそのまま**置いた（ボードで使う道具 `h2peek.py`・`sgstat.py` は proj023 の `tools/` から）。
`sw/pynq/`（SAM45-Fine）とは別に置いているのは、M1〜M4 の回帰を移植元と同じ PS で行うため（[`docs/migration-sam45-wide.md`](../../docs/migration-sam45-wide.md) の原則 4）。

- `s45core.py` などの既定は **SAM45-Wide**（BIT_KIND 1）。Fine の bit には `sw/pynq/` を使う
- `sw/pynq/` との違い: proj023 が変えたもの（s45core・s45acq・specd・timebase・plring・s45client・sg・specrecv・spectrometer・test_fake.sh・gbboot）と Wide の道具（wide.py・wide_v2.py・widef2.py・wideresp.py）。`sw/pynq/` の M1 の後の変更（M5a の較正の鍵・M5b の USR_ACCESS・pps の符号の直し・(2, 3) の TP の較正）はここには無い。pps の符号の直しは proj023 にも入っている（test_cal_b.py）
- `sw/pynq/` への一本化は Wide の M5
