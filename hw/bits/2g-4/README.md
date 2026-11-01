# 2G-4

4 ADC × 4 コア。PFB（係数は 4 コアで共有の URAM `g24_cu`、PS が AXI4-Lite で書いて CRC で VERIFY）＋ 16 レーンのレーン FFT（4096 点、2-for-1 で IP 8 個 / コア）で全帯域 2048 MHz を 32768 ch（62.5 kHz）・10.24 ms。BIT_KIND 3。

**状態:** v1.0.0 を出した（2026-10-31、タグ `2g-4/v1.0.0`・リポジトリ全体 `v1.2.0`）。study-rfsoc の proj031 rev 2（`proj031-m0`、PROJ 0x0031_0200）から置いた。`Makefile`・`build.tcl`・`build_post.tcl`・`sim/`（2G-4 の試験台と照合・FFT IP の模型）・`tools/`（係数とひねり係数・CRC の式の生成、OOC の道具）・`src/`（2G-4 の部品 `g24/`・2-for-1 の鎖 `s2_chain.v`（`s2_sep`・`s2_q` は `hw/common/` の共通の部品で、寸法 ZW 28・KB 12・AB 9 は `g24_spec.v` が渡す）・共有のファイルの写し）。計画は [`docs/migration-2g-4.md`](../../../docs/migration-2g-4.md)。

- `core_cmn.v`・`tp_core.v` は `hw/common/` の版を読む（2026-10-29 に一本化。中身は proj031 の版と同じ）。**`rec_fr.v` だけは `src/rec_fr.v`（proj031 の版）を読む**: `hw/common/rec_fr.v` は Fine・Wide を v1.0.0 と同じにするため `np − 1'b1` で引く形にしたが、2G-4（NCH 32768）で使うと合成が変わり、既定・PETO・PE のどの戦略でも一続きの作り直しで閉じなかった（WNS −0.23〜−0.35 ns。migration）
- Makefile の目標: ビルド（`make build`、既定の戦略）・`post`・sim（`make sim-all` = 模型 3 本 ＋ sim 15 本、`build-sim-logs/` の 18 個で判定。`SIM_J` で並べる数）・表の作り直し（`gen`・`gen-crc`）・部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`・`ooc-cu`）。proj031 までの試行の目標（`coef-ooc`・`wide-hier`・`ooc-ref`）は外した（2g-4/makefile-trim）
- `make build` は先に `make model-cu` を回し、`runs/model_cu.txt` の COEF_CRC（期待 0x891BE197）を bit に焼く。`runs/` は git に入れない
- 実装の戦略は**既定**（移植元と M3〜M5 の bit はこれで作った。WNS +0.047 ns・FDRI `f05e1f62…3b1c`。2026-10-30 の一本化の後の作り直し 64dbf45、2026-11-01 の `s2_sep`・`s2_q` の一本化の後の作り直し dc82198 も同じ FDRI）
- 親の Vivado が `impl_1` の後（設計を開き直す所）で落ちたら `make post`（合成・実装をやり直さずに照合・報告・`build/` への写し）。`impl_1` の中で落ちて dcp から回し直した回は配置が一続きの回と別物になり、作り直せない（2026-10-30 の PETO）

## 版と BIT_REV

規則は [`../../../docs/release.md`](../../../docs/release.md) の「BIT_REV と版」。リリースごとに 1 行足す。

| 版 | BIT_REV | USR_ACCESS（タグの commit） | FDRI の sha256 | 性能評価 |
|---|---|---|---|---|
| v1.0.0 | 1 | `f2c22aa0` | `f05e1f62e5e374ced85e2fa99d95a9364a6b72749b6a14169f7161042e3a3b1c`（判定した .bit・移植元と同じ） | [v1.0.0](../../../docs/performance/2g-4/v1.0.0.md) |

系譜: proj027（2G-4 の RTL）→ proj030（レーン FFT の 2-for-1）→ proj031（係数の共有 URAM）。PS は proj036（束ねの取得の C）。
