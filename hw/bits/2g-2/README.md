# 2G-2

2 ADC × 2 コア。コアごとに PFB（係数 ROM）＋ 16 レーンのレーン FFT（8192 点、2-for-1 で IP 8 個）で帯域 2048 MHz を 65536 ch（31.25 kHz）・10.24 ms。BIT_KIND 10。

**状態:** v1.0.0 を出した（2026-11-01、タグ `2g-2/v1.0.0`・リポジトリ全体 `v1.4.0`。性能評価は [`docs/performance/2g-2/v1.0.0.md`](../../../docs/performance/2g-2/v1.0.0.md)、設計は [`docs/design/2g-2/`](../../../docs/design/2g-2/)）。study-rfsoc の proj034（`proj034-m0`、PROJ 0x0034_0100）から置いた。`Makefile`・`build.tcl`・`build_post.tcl`・`sim/`（2G-2 の試験台と照合・FFT IP の模型）・`tools/`（係数とひねり係数の生成、OOC の道具）・`src/`（2G-2 の部品 `g22/`・2-for-1 の鎖 `s2_chain.v`・`rec_fr.v` の写し）。計画は [`docs/migration-2g-2.md`](../../../docs/migration-2g-2.md)。

- **`rec_fr.v` は `src/rec_fr.v`（proj034 の版）を読む**。`hw/bits/2g-1-fast/src/rec_fr.v`・`hw/bits/2g-4/src/rec_fr.v` と同じ中身。`hw/common/rec_fr.v`（`np − 1'b1` で引く形）で作ると FDRI が移植元と変わるおそれがある
- **`s2_sep`・`s2_q` は `hw/common/` の共通の部品**（2G-4・2G-1-Fast と同じファイル。寸法 ZW 29・KB 13・AB 10 は `g22_spec.v` が渡す）。**`s2_chain.v` は `src/` の bit ごとの版**（2G-4・2G-1-Fast の同じ名前のファイルと丸めの式が違う）
- 模型は `model/g22_model.py`（`make model-g22`）と **`model/s2_model_g22.py`**（`make model`）。2G-4 の `model/s2_model.py`・2G-1-Fast の `model/s2_model_g21.py` とは別のもの
- 実装の戦略は **既定**（`make build` → `build/`）。移植元の bit はこれで作った（WNS +0.074 ns）。2026-11-01 の `s2_sep`・`s2_q` の一本化の後の作り直し dc82198 も v1.0.0 と同じ FDRI・WNS
- Makefile の目標: ビルド（`make build`・後段の再開 `make post`）・sim（`make sim-all` = 模型 2 本 ＋ sim 14 本、`build-sim-logs/` の 16 個で判定。`SIM_J` で並べる数）・表の作り直し（`gen`）・部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`）。proj034 までの試行の目標（`s2`・`survey`・`ooc-ref`・`ooc-all`）は外した（2g-2/makefile-trim）
- `runs/` は git に入れない

## 版と BIT_REV

規則は [`../../../docs/release.md`](../../../docs/release.md) の「BIT_REV と版」。リリースごとに 1 行足す。

| 版 | BIT_REV | USR_ACCESS（タグの commit） | FDRI の sha256 | 性能評価 |
|---|---|---|---|---|
| v1.0.0 | 1 | `4273ecb0` | `b9dec08c865b43de56a95efe74131e3c40c417061671a3f35447ed02ea2c313f`（判定した .bit・移植元と同じ） | [v1.0.0](../../../docs/performance/2g-2/v1.0.0.md) |

系譜: proj025（2G-2 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj034（2G-2 に 2-for-1）。PS は `sw/pynq/` の G22 の Backend（2G-4 の M5 で一本化）と `sw/pynq/g22cw.py`。
