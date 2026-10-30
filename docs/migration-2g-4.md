# study-rfsoc からの移植計画（2G-4）

- 状態: **M1 済み**（2026-10-28。表の行き先に置き、パスだけを直した。下の「M1 の結果」）。Makefile から試行の目標を外した（ブランチ `2g-4/makefile-trim`）。**M2・M3・M4 済み**（下の「M2 の結果」「M3 の結果」「M4 の結果」）。**M5 済み**（2026-10-28〜29、ブランチ `2g-4/m5-ps`: PS を `sw/pynq/` に一本化・M5a の鍵 (3, 1)・M5b の USR_ACCESS・予算の照合・M2〜M4 の回し直しが予言どおり。下の「M5 の結果」）。LMX の PWR 3 での F-2 は 1 回の値を最多の山で読んで通過・CAL 据え置き、TP の線形性は通過、CU も通過。**`hw/common/` の一本化済み**（2026-10-29〜30、ブランチ `2g-4/common-unify`: Fine・Wide は v1.0.0 と FDRI まで同じ、2G-4 は rec_fr だけ M5 の写しを読み、既定の戦略で M5 と FDRI まで同じ bit。下の「`hw/common/` の一本化」の 3 節）。**M6 の判定は全部通過**（2026-10-30、ブランチ `2g-4/m6`。V2-b の陽性対照は 2G の取得の直しの後。下の「M6 の結果」）。性能評価は `docs/performance/2g-4/v1.0.0.md`（下書き）。残りは M7（リリース）。**M7**（2026-10-30〜31、ブランチ `2g-4/m7-docs`）: 仕様・設計・使い方の 2G-4 の分、CHANGELOG の v1.2.0、性能評価を確定。リリース `2g-4/v1.0.0`・`v1.2.0` を出した（下の「M7 の結果」）
- 移植元: **`study-rfsoc@proj031-m0`**（RTL・ビルド・sim・模型。proj031 rev 2）と **`study-rfsoc@proj036-m0`**（PS。proj031 の PS に束ねの取得の C を足したもの）。どちらも注釈つきタグで、同じ commit f97b060（2026-10-28 に push）
- 土台にする決め方: SAM45-Wide の [`migration-sam45-wide.md`](migration-sam45-wide.md)（= SAM45-Fine の [`migration.md`](migration.md) の M0〜M7）と同じ段取り。違うところだけをここに書く
- 2G の 4 本の移植の順（2026-10-28 に決めた）: **2G-4** → 2G-1-Fast（study-rfsoc proj033 の後）→ 2G-2（proj034 の後）→ 2G-1-Fine（製品の形にする study の proj を先に）。仕様は [ADR 0022](decisions/0022-2g-1-fast-and-fine.md)・[`spec/bits.md`](spec/bits.md)・[`spec/interface.md`](spec/interface.md) 2.4

## 原則

1. **変更は一度に一つ。** 移植の PR は「ファイルを置き直す」だけにする（Fine・Wide の原則 1 と同じ）
2. **同じものができたことを、数えて確かめる。** M3 は移植元の bit との FDRI の一致、M4 は移植元と同じ値
3. **study-rfsoc の proj031・proj036 は書き換えない**（タグの後）。移植の後に見つかった問題は、YATSUGATAKE で issue にする
4. **M1〜M4 は SAM45-Fine・SAM45-Wide のファイルに触らない。** `hw/common/` と中身の違う共有の部品（3 個、下の「`hw/common/` との違い」）は 2G-4 の側に写しを置き、一本化は M1 の後の別の PR にする
5. **PS は M1〜M4 では `sw/pynq-2g/` に proj036 のまま置く。** `sw/pynq/`（Wide の M5 で一本化した版）への一本化は M5 で、2G の 3 本（G21・G22・G24）の Backend を一度に入れる（下の「M5」）

## 始める条件

- [x] proj031 の判定（P-2 の sim・B・R・R-5 F-2）が通り、README に結論が書かれている（2026-10-28。rev 2 = PROJ 0x0031_0200 が最終）
- [x] proj036 の判定（P-1・R-1〜R-3）が通っている（2026-10-28。tint 20.48 ms で 1 周 13.4 ms（65 %）、30 分 24.8 MB/s で取りこぼし 0）
- [x] 2G-4 の運用に使う bit を決めた → **proj031 rev 2**（proj030 との比べは proj031 README の「決めること」。DSP が 256 少ない。電流は proj030 が 0.5 A 少ないが、どちらも 32 A 前後で連続運転の目安 38 A を下回る）
- [x] **proj031 の持ち越しを閉じる**
  - [x] `check_g24.py ds` を 2-for-1 の IP の出口（z_q = y_q + j·y_(q+8)）に合わせた（2026-10-28、study-rfsoc 575ae63）。sim-g24ds は normal 通過・陽性対照（D_S 0）は落ちた（下の「持ち越しを閉じた記録」）
  - [x] **2 時間以上の連続運転**（tint 20.48 ms・運用の形）→ proj036 R-4 で通過（2026-10-28、下の「持ち越しを閉じた記録」）
- [x] **判定が `test/acceptance/2g-4/` の書き方で書かれている**（Wide はこれが無いまま始めて M6 の前に書き起こした。2G-4 は M0 で書き起こした、2026-10-28）: 11 判定（ID-1・CU・H-0・EQ-4・H-2・F-2・BUND・V2-b・V2-L・RING・NET）。RING は 2026-10-28 に interface 8. の 11 で入れた新しい判定で study-rfsoc では回していない、NET は M5 で specd に照合を入れてから。M1〜M4 の回帰は判定の「記録」の値と比べる
- [x] **タグ** `proj031-m0`・`proj036-m0`（f97b060）を付け、study-rfsoc の公開前スキャンの後に push した（2026-10-28）。スキャンのヒットは、今回の 3 つの commit とその中のファイルには 0。ほかのヒット（1,600 件ほど）は追跡していない `runs/` など（受け手の IP・ホームパスはどれも追跡していないファイル）と、追跡しているファイルのボードの既定の利用者のホーム（実験の台本の `cd` 先）・`<作者>` の置き場の字・数値の偽陽性
- [x] **ボードの準備**（proj035）: GEM1 の AXI_MAX_PIPELINE（0xFF0C0054）を **0x0102** にする systemd のユニット（study-rfsoc `proj035/board/`、手順は `proj001/docs/runbook.md` の 09）をボードに入れ、有効にした。送り出し 194 → 348 Mbit/s。**読みの要求を 4 本以上にしない**（CPU の DDR の読みが遅れ、2G の取得が追いつかない）。判定の前提とリリースのボードの準備の手順にも入れる（M7）

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj031 README「B-2 rev 2」の既定の戦略のビルド（`build/`）。

| 項目 | 値 |
|---|---|
| bit の sha256 | `2a8565c7c76c00c8259e8fffb4ff9edfc637bd400c7ea98fdae5b5a0198b06d4`（34,437,476 B） |
| hwh の sha256 | `2c2b348ce1942d04d24e51284445c6b146c0f8fed5ed3c11716f8ad7ef16fb20` |
| FDRI（`sw/pynq/bitinfo.py`） | 8,608,824 語・sha256 `f05e1f62e5e374ced85e2fa99d95a9364a6b72749b6a14169f7161042e3a3b1c` |
| 構成の流れ（欄 e）の sha256 | `66dad151e1503c3897da2fdb5451bfa507d08d1d646e1063490fe3b80376bef6` |
| ID | BIT_KIND 3・BIT_REV 1・**PROJ 0x0031_0200**。IF_ID 0x0203_0101（コア 4）・0x0203_0102（time_core）。USR_ACCESS なし |
| 実装の戦略 | **既定**（`make build`、study-rfsoc の `build/`）。同じ RTL の Performance_Explore（`build-PE/`、WNS +0.007）は使わない |
| `-1` の WNS / WHS | **+0.047 ns / +0.000 ns**（失敗した端点 0） |
| LUT / FF | 201,656（47.42 %）/ 345,687（40.64 %） |
| DSP / BRAM タイル / URAM | 2,064（48.31 %）/ 692 / 56（g24_cu_0 に 8） |
| `report_cdc` | CDC-3 Info 119・CDC-6 Warning 5・CDC-15 Warning 3,137 |
| 係数 URAM の期待の CRC | 0x891BE197（`make model-cu` の `runs/model_cu.txt` の COEF_CRC。`make build` が bit に焼く） |
| F-2 | M = A 69.4・B 69.6・C 70.1・D 70.4 ns → timebase.CAL[0x0031_0200] = pps_det_ns 71.5・adc_to_core_ns {A 140.9・B 141.1・C 141.6・D 141.9}（proj031 R-5） |

bit そのものは git に入れない（ADR 0018）。

## 置き場所の対応（M0、2026-10-28）

ファイル 1 つずつの行き先は付録 [`migration-2g-4-files.md`](migration-2g-4-files.md)（proj031 の 172 個と proj036 の 75 個、計 247 個: 置く 103・2G-4 の側に写し 3・既にある 35・移さない 106）。

| study-rfsoc | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| proj031 `src/g24/`（15 個）・`src/s2_*.v`（3 個） | `hw/bits/2g-4/src/` | 2G-4 の部品・係数とひねり係数の hex・CRC の式。2-for-1 の部品 s2_* は 2G-1-Fast・2G-2 も使う見込み（そのときに `hw/common/` へ上げるかを決める） |
| proj031 `src/common/` の `core_cmn.v`・`rec_fr.v`・`tp_core.v` | `hw/bits/2g-4/src/` に**写し** | proj024 で口を足した版（下の「`hw/common/` との違い」）。Fine・Wide は `hw/common/` の版のまま。一本化は M1 の後 |
| proj031 `src/common/` の残り 32 個・`src/board/` 3 個 | **既にある** `hw/common/`・`hw/board/` | バイト単位で同じ |
| proj031 `Makefile`・`build.tcl`・`build_post.tcl` | `hw/bits/2g-4/` | パスだけを直す（下の「M1 で直すパス」） |
| proj031 `sim/`（21 個） | `hw/bits/2g-4/sim/` | 試験台・照合・IP の模型（lane_fft_g24_model）・cu_src |
| proj031 `model/`（5 個） | `model/` | g2_model・g24_fixed・g24_model・s2_model・cu_model。名前は `model/` の今のものと重ならない |
| proj031 `tools/` のうちビルド・sim が使う 5 個 | `hw/bits/2g-4/tools/` | gen_g24_tables・gen_crc32・ooc_rtl・ip_impl・ip_survey |
| proj036 `pynq/` のうち 2G-4 が使う 47 個と `tools/` 3 個、proj031 `tools/cuctl.py` | **`sw/pynq-2g/`**（51 個） | M1〜M4 は proj036-m0 の PS とバイト単位で同じにする。import は 51 個の中で閉じる。`sw/pynq/` への一本化は M5 |
| proj031 `pynq/`（69 個） | 移さない | proj036 の `pynq/` に同じものか新しい版がある（違うのは specd・s45acq・s45fast.c・s45fast.py の 4 個で、proj036 が束ねの C を足した版） |
| proj036 `pynq/` の Fine・Wide・窓の道具、2G-1・2G-2 の道具（g21cw・g22cw・bench_g21）、試行の道具 | 移さない | 2G-1・2G-2 の道具はそれぞれの移植で |
| README・`runs/`・`ref/`・試行の目標の道具（coef_ooc・wide_hier・run4c30b・shapecmp） | 移さない | |

`sw/pynq-2g/` の 51 個のうち、`sw/pynq/` と同じ 20・違う 18・`sw/pynq/` に無い 13（M5 の一本化の量の見当）。

### `hw/common/` との違い（M0 の 3.、2026-10-28）

proj031 の `src/common/` 35 個と `src/board/` 3 個を、YATSUGATAKE の main（c83cc0a）の `hw/common/`・`hw/board/` と比べた: **35 個がバイト単位で同じ、違うのは 3 個**。3 個とも proj024（2G-1）の手順 2d で口を足したもので、既定のパラメータでは今の式と同じ:

| ファイル | 違い（diff の行） | 中身 | 2G-4 の使い方 |
|---|---|---|---|
| `core_cmn.v` | 2 | tp_core の `f0_ext` の口を 0 で繋いだ（Synth 8-3848 の見張りのため） | そのまま |
| `tp_core.v` | 19 | パラメータ `F0_EXT`（既定 0）と入力 `f0_ext`。1 なら RUN の F0 を外から受け、TP の区切りを FULL のダンプと同じ T に並べる。宣言の位置の入れ替え（Icarus 14） | `F0_EXT(1)`（g24_core） |
| `rec_fr.v` | 52 | パラメータ `NCH`（既定 4096）・`CHW`。数えと `rd_ch` の幅と語 7 のバイト数を NCH から作る。NCH 4096 では 567fda2 と同じ幅・同じ値（proj024 の sim-recfr で旧版と全部の出口をクロックごとに比べた） | `NCH(32768)`（g24_core） |

2G-4 の build.tcl が `src/common/` から読むのは 13 個（adc_ev・axis_sel4・cmul・dft16f・raw_core・rec_arb・time_core・s45_ring・gb_adc・gb_gate と上の 3 個）。残りの 22 個（wide_*・win_*・spec_core など）は proj031 の木にあるだけで 2G-4 は使わない（「既にある」に数えた）。
**一本化**（3 個を proj031 の版で `hw/common/` を替え、2G-4 の写しを消す）は M1 の後の別の PR にする。合格は Wide の一本化（cmul・rec_fr、2026-10-23）と同じ型: Fine・Wide の sim の回帰と、**Fine と Wide を作り直して FDRI が今のリリースと同じ**こと（既定では同じ式なので同じはず。違えば一本化しない）。
`tp_core` に繋がない入力 `f0_ext` が増えるので、Wide の一本化の予言と同じく「式は同じでも配置のタイブレークが動く」おそれがある（そのときは sim は通り、FDRI だけが外れる）

### M1 で直すパス（予定）

Fine の M1・Wide の M1 と同じ型。中身は変えない:
- `Makefile`・`build.tcl`・`build_post.tcl`: `src/common/` → `../../common/`（**写しの 3 個は `src/`**）、`src/board/` → `../../board/`、`src/g24/`・`src/s2_*.v` → `src/`、`model/` → `../../../model/`、`pynq/g24cu.py` → `../../../sw/pynq-2g/g24cu.py`（`CU_WORDS` の依存。`make build` は `make model-cu` を先に回して COEF_CRC を読む）
- `model/cu_model.py` の `pynq`・`tools` の道（`../../sw/pynq-2g`・`../hw/bits/2g-4/tools`）、`sim/check_*.py`・`tools/gen_g24_tables.py` の模型の道（`../model` → `../../../../model`・`../../../model`）、`sim/check_cu.py` の `pynq` の道
- `runs/model_cu.txt` の置き場所: `make model-cu`・`make build` は bit のディレクトリの `runs/` に書く（git には入れない。`.gitignore` に足すかを M1 で決める）
- **在ってはいけない側の照合を M1 に付ける**: 2G-4 の Makefile・build.tcl が `hw/common/core_cmn.v`・`rec_fr.v`・`tp_core.v` を指していないこと（指していると、口の無い版で作られて合成で止まるか、NCH 4096 の幅で作られる）

### M1 の結果（2026-10-28、ブランチ `2g-4/m1-place`）

- **置く**（ec699fc）: 付録の 106 個（置く 103・写し 3）を `git show study-rfsoc@proj031-m0 / proj036-m0:…` から取り出して置いた。106 個とも移植元と blob が同じ。既にある 35 個も今の main（6fcabe1）の `hw/common/`・`hw/board/` とバイト単位で同じ（M0 の比べの後に変わっていない）
- **パスの直し**: 8 個・45 行（Makefile 15・build.tcl 20・build_post.tcl 4・Python 6）。**違う行はすべてパスの行**: 古い行と新しい行からパスの部分を消して比べ、45 行とも一致（陽性対照: パス以外を 1 文字・空白 1 つ変えた行はどちらも不一致になる）。`src/g24/`・`src/s2_*.v` は `hw/bits/2g-4/src/` の下に同じ形で置いたので直していない。`sw/pynq-2g/` と `model/` の 4 個は移植元のまま（`model/cu_model.py` だけ pynq・src の道を 2 行直した）
- **在ってはいけない側**: 2G-4 の Makefile・build.tcl が `hw/common/` の `core_cmn.v`・`rec_fr.v`・`tp_core.v` を指す行は 0（直す前の版に当てると 3・2 行を拾う = 照合が働いている）。build.tcl が読むファイル（コメントの行を除く）はすべて在る
- **動かして確かめたこと**（Vivado サーバ。Vivado は使っていない）: `make model-g24`・`model`・`model-cu` が全部通過、**COEF_CRC 0x891BE197**。`make gen`・`tools/gen_crc32.py` の出力が `src/g24/` の hex 4 個・`crc32_d32.vh` とバイト単位で同じ。`make sim-all`（g24c・g24t・g24p・g24ch）と `sim-recfr`（写しの `rec_fr.v`）が「全部通過」、陽性対照 8 本は落ちた（≒ 3 分）。Tcl 5 個が `info complete` で完結、`sw/pynq-2g/` の .py 46 個が `py_compile` を通る
- **`runs/` は git に入れない**（`.gitignore` に `/hw/bits/2g-4/runs/`）。`make build` がその場で `make model-cu` を回して作る
- **動かないままにしたもの**: Makefile の `coef-ooc`（`tools/coef_ooc.tcl`・study-rfsoc の git）・`wide-hier`（`tools/wide_hier.tcl`）・`ooc-ref`（`ref/`）。外すのは下の 1

### M1 の後にすること（それぞれ別の PR）

1. **Makefile から試行の目標を外す**: `coef-ooc`（study-rfsoc の git から proj025 の g22_coef を読む）・`wide-hier`（proj023 のチェックポイントを読む）・`ooc-ref`（`ref/` を移さない）。`sim-all` は今は 1a〜1d の 4 つだけを回すので、2G-4 の sim の全部（下の M2 の表）に替える。外した後に M2 をもう一度
   - **済み（2026-10-28、ブランチ `2g-4/makefile-trim`）**: 3 つの目標と、それだけが使う `JOBS`・`RULER_REV` を外した。`sim-all` は模型 3 本（`model-g24`・`model`・`model-cu`、「まとめ」の行に「不合格」が無いこと）と sim 15 本（M2 の表の全部、最後の行「sim-…: 全部通過」）を回し、`build-sim-logs/` の 18 個で判定する。共有の入力（CU_WORDS・`g24s_in/x.hex`）を先に作ってから、目標を `SIM_J`（既定 4）本ずつ並べる。この PC で 18 個とも通過（989 s）。判定の陽性対照: ログの写しに「不合格」・NG・ログの欠けを入れると 3 つとも拾う。Wide と違い M2 の前に外したので、M2 は 1 回で済む
2. **`core_cmn.v`・`rec_fr.v`・`tp_core.v` を `hw/common/` に一本化**（上）
3. **`sw/pynq-2g/` を `sw/pynq/` に一本化** → M5

## 手順

| 手順 | 2G-4 ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録）・始める条件・`hw/common/` との違いの数え | 全ファイルに行き先がある・始める条件が全部 [x] |
| M1 | 表の行き先に置き、パスだけを直す | `git diff --stat` で中身の変更がパスの行だけ。在ってはいけない側の照合（上）（**2026-10-28**: 上の「M1 の結果」） |
| M2 | sim を全部回す: model-g24・model・model-cu、sim-g24c・g24t・g24p・g24ch・lane・g24a・g24s・recfr・g24core・g24s45・g24x4（cuclr・cuclrno を含む）・**g24ds**・sep・all2・cu | proj031-m0 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**2026-10-28**: 下の「M2 の結果」） |
| M3 | ビルド（`-1`、**既定の戦略**） | **FDRI が移植元と同じ**（`f05e1f62…3b1c`）。WNS / WHS が移植元と小数 6 桁まで同じ（**2026-10-28**: 下の「M3 の結果」） |
| M4 | 実機の短い回帰（ボードの新しいディレクトリ、study-rfsoc の道具のディレクトリと混ぜない） | ID・係数 URAM の VERIFY（CRC 0x891be197・0.7 s 台）・4 窓 × 200 の照合と `g24cw`・4 コアの bit 単位の同等（50 / 50 組 × 3）・tint 20.48 ms で 300 s 取りこぼし 0 が proj031 / proj036 と同じ値（**2026-10-28**: 下の「M4 の結果」） |
| M5 | Fine の M5a・M5b を 2G-4 に当て、`sw/pynq-2g/` を `sw/pynq/` に一本化 | 下の「M5」 |
| M6 | 2G-4 の判定（`test/acceptance/2g-4/`）を全部通し、性能評価を書く | `docs/performance/2g-4/<版>.md` |
| M7 | spec・design・user の 2G-4 の分を書き、リリース | `release.md`。ボードの準備（AXI_MAX_PIPELINE 0x0102・s45fast.c のビルド）を手順に入れる |

### M2 の結果（2026-10-28）

Vivado サーバ（Icarus Verilog 11.0・Python 3.10.12・numpy 1.21.5）で、移植先（`hw/bits/2g-4/`、2g-4/makefile-trim の 1 つ目の commit）の `make sim-all` と、**タグ `proj031-m0` の proj031 を `git archive` で取り出して同じ 18 個を回したもの**を比べた（同じ PC・同じ版の道具で、同じ時間に並べて回した。移植先 989 s・移植元 1,018 s）:

- **18 個とも「全部通過」**（模型 3 本は「まとめ」の行が全部通過、sim 15 本は最後の行が全部通過）。陽性対照は 27 本がすべて落ちるべきところで落ちた（g24ds の陽性対照は D_S +0 のところだけで落ちる）。両側で同じ
- **`build-sim/` の出力 265 個のうち 217 個がバイト単位で同じ**（各変種の `tb.log`・`check.log`・入力の hex・CU_WORDS を含む）。違う 48 個は iverilog のコンパイル物 `tb` だけで、**パス（`src/common/` ↔ `../../common/`・写しの 3 個は `src/`）と、コンパイルごとに変わる番地（`0x…`）を読み替えると 48 個とも同じ**（陽性対照: 1 行に字を足すと不一致になる）
- **`build-sim-logs/` の 18 個のうち 15 個がバイト単位で同じ**。違う 3 個は模型のログで、違うのは make が出すコマンドの行（`model/` ↔ `../../../model/`）と経過秒（`[2.1 s]` ↔ `[2.0 s]` など）だけ。`runs/model_cu.txt` の COEF_CRC は両側とも **0x891BE197**
- 比べの相手について: Fine・Wide の M2 は移植元の作業ツリーに残っていた最後の実行と比べたが、2G-4 は移植元をタグから回し直した（proj031 の作業ツリーの出力は rev 2 の sim と ds の直しの後の g24ds で日付がまちまちのため）。回したのは M3 でビルドする Vivado サーバ

### M3 の心配（M3 の前に書いた）

移植元の WHS は **+0.000 ns** で、WNS +0.047 ns も薄い（proj031 の結論）。Fine・Wide の M3 は「ディレクトリだけ違う」作り直しで構成データまで同じになったので、2G-4 も同じになる見込みが高い。
**負に落ちたら RTL も制約も直さずに止め、どうするかを決め直す**（直すと移植ではなくなる）。PE（WNS +0.007・WHS +0.010）に替えるのも M3 の中では行わない（比べの相手が変わる）。
`make build` は bit に焼く COEF_CRC を `make model-cu` の出力から読む（numpy の版で浮動小数の丸めが変わると CRC が変わりうる）。M3 の前に `runs/model_cu.txt` の COEF_CRC が 0x891BE197 であることを確かめる

### M3 の結果（2026-10-28）

Vivado サーバで、移植先（`hw/bits/2g-4/`、commit 699c511 の木 = M2 と同じ RTL・build.tcl）の `make build`（`-1`・既定の戦略・BUILD_JOBS 8）を回した（6,429 s）。予言（上の「M3 の心配」）どおり、**ディレクトリだけ違う作り直しで構成データまで同じ**:

| | 移植元（proj031 rev 2 の `build/`） | 移植先 |
|---|---|---|
| FDRI | 8,608,824 語 / `f05e1f62e5e374ced85e2fa99d95a9364a6b72749b6a14169f7161042e3a3b1c` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `66dad151e1503c3897da2fdb5451bfa507d08d1d646e1063490fe3b80376bef6` | **同じ**（.bit のファイルはヘッダの日付だけ違う） |
| TIMING（確定） | WNS 0.047165 ns / WHS 0.000000 ns | **同じ** |
| 資源・CDC | LUT・FF・DSP・BRAM・URAM の表、CDC-3 119・CDC-6 5・CDC-15 3,137 | ログから取り出した行がすべて同じ |
| COEF_CRC（g24_cu_0） | 0x891BE197・PROJ 0x00310200 | 同じ |
| ERROR・CRITICAL WARNING | ERROR 2 行（`lane_fft_g24` の `output_width` を読む既知の 2 行、ビルドは続く）・runme の CRITICAL WARNING 0 | 同じ |

`bitinfo.py`（`sw/pynq/`）で読んだ。USR_ACCESS は焼いていない（M5 で Fine の M5b のフックを入れる）。.bit は git に入れない（ADR 0018）

### M4 の結果（2026-10-28）

M3 で作った bit（FDRI `f05e1f62…3b1c`）と `sw/pynq-2g/`（PS 52 個、ボードの写しが手元と sha256 で同じ）を、ボードの新しいディレクトリ（`2g-4-m4`、study-rfsoc の道具のディレクトリと混ぜない）に置き、`build_fast.sh`（「CRC: 命令」）の後に specd を `--g24 … --fast --fast-ring --loop-log-ms 0.1` で起こした。**1 回の Overlay の読み込みの中で**、ID-1 → H-0 → EQ-4 → tint 20.48 ms で 300 s の順に回した。配線 N/S・ノイズ ON（2026-10-29 に訂正。前は「配線 N」と書いていた）。配線 N を前提にする判定（V2-b）は前提から外れて回した:

| | 移植先（M4） | 移植元の記録 |
|---|---|---|
| ID-1 | 係数 URAM 4096 行を **0.73 s**・VERIFY 通過（CRC 0x891be197・STAT 0x15）、ID proj 00310200・kind g24、IDLE・time_ok 1・health 0・flags 0 | proj031 rev 2: 0.73 s・同じ CRC・STAT |
| H-0（4 窓 × 200） | 800 本・CRC 0・説明のない欠け 0・照合 通過・`g24cw` 全部通過、陽性対照（`--src DCBA`）で 4 窓とも NG | proj031 R-1a: 同じ（床は proj031 が N/S・ノイズ OFF の値なので比べない） |
| EQ-4 | **50 / 50 組 × 3**、陽性対照 0 / 49 組 × 3 | proj031 R-1b: 50 / 50 組 × 3、0 / 49 組 × 3 |
| tint 20.48 ms で 300 s | SPEC 58,505・7.36 GB（24.5 MB/s）・CRC・欠け・kgap・tdev 0・照合 通過、miss・pl_drop・pl_crc・pl_err 0・loop_slow 1・1 周の最長 22.74 ms・p99 11.2 ms・リングの山 3.2 MB・1 周の計 13.10 ms、AXI_MAX_PIPELINE 前後 0x102 | proj036 R-3・R-4: 取りこぼし 0・最長 23.2 / 23.09 ms・p99 11.2 ms・山 4.2 / 3.3 MB、R-1 の 1 周の計 13.4 ms |

**判定の書き方の誤りを 2 つ見つけて直した**（`test/acceptance/2g-4/`）:
- **H-0・EQ-4・H-2 の手順に `SEND ON` が無かった**。最初の H-0 は記録が specd の溜まり（101 MB）に残り、受けが spec 0 のまま「照合: 通過」になった（proj031 R-1a と同じ踏み方）。`CLEAR` して取り直した。共通の前提に「受けを取る前に `SEND ON`」を書き、3 つの手順に入れた
- **H-0 の陽性対照 `g24cw.py --posctl` は効かない**（`--posctl` は CW の判定 `--sg-mhz` にしか効かず、「全部通過」になった）。M0 で書き誤った。src の入れ替え（`--src DCBA`）に替えた

### M5（Wide の M5 と違うところ）

- **PS の一本化を 2G の 3 本ぶん一度に**: 2G の PS は proj023 の頃に枝分かれした系統（G21・G22・G24 の Backend と s45fast.c）。`sw/pynq/` は Wide の M5 の版（M5a の CAL の鍵・M5b の USR_ACCESS・shm の取り残しの直し・LMX の PWR 3 など）。2G-1-Fast・2G-2 の移植を待たずに、G21・G22 の Backend も入れる（後で 2 回マージし直さないため）。2G-1・2G-2 の判定はそれぞれの移植で
- **LMX の出力の強さ**: proj036 の specd の既定は PWR 31（R-4 の ID で `lmx_pwr=31`）。`sw/pynq/` の既定 PWR 3 に合わせ、2G-4 の F-2 と TP の線形性を PWR 3 で測り直す（Wide の「M5 の後」と同じ）
- **予算を越える tint を SET で断る照合を specd に入れる**（interface 4.5 の約束。今の specd には無い）: 2G-4 は 20.48 ms 未満を断る。陽性対照: `SET tint=0.01024` が ERR
- **リング 64 MiB**（interface 4.1・8. の 11）: 2G の bit の既定を `--ring-mib 64` にする（今は起動の引数）
- **s45fast.c**: ボードで `build_fast.sh` で libs45fast.so を作る。CRC が「命令」で作られたことを起動の記録に残す。リリースの組（`tools/release_files.py`）と user の手順に入れる
- 較正の鍵を (BIT_KIND, BIT_REV) = (3, 1) に。timebase の CAL に proj031 R-5 の値（上の表）。BIT_REV は 1 のまま
- Makefile・build.tcl に Fine の M5b のフック（USR_ACCESS を焼く・`bitinfo.py` で読み返す）。FDRI は M3 と同じになるはず

### `hw/common/` の一本化（core_cmn・rec_fr・tp_core）の手順と予言（2026-10-29、ブランチ `2g-4/common-unify`、回す前）

**変えたもの**: `hw/common/` の `core_cmn.v`・`rec_fr.v`・`tp_core.v` を 2G-4 の写し（= proj031 の版、上の「`hw/common/` との違い」）に替え、写しを消し、2G-4 の Makefile（3 行）・build.tcl（2 行）を `../../common/` に向けた。違いは口を足しただけで、既定のパラメータでは今の式と同じ:
- `tp_core.v`: パラメータ `F0_EXT`（既定 0）と入力 `f0_ext`。Fine の `win_core` と Wide の `core_cmn` は `f0_ext` を繋がない（Fine）か 0 で繋ぐ（core_cmn の 1 行）
- `rec_fr.v`: パラメータ `NCH`（既定 4096）・`CHW`。NCH 4096 では今と同じ幅・同じ値
- `core_cmn.v`: tp_core の `f0_ext` を 0 で繋いだ 1 行（Wide も使う）

**合格**（Wide の一本化と同じ型。1 つでも外れたら一本化しない）:
1. **Fine の sim**: `hw/bits/sam45-fine` で `make sim-all sim-ring` を、一本化の前（main 6ee64b1 の worktree）と後の 2 つの木で回し、sim の出力（ダンプ・照合のログ・結果の行）がバイト単位で同じ。陽性対照は前と同じ件数で落ちる。コンパイル物（`tb*`）は `tp_core`・`rec_fr` を含むものだけが読み替えても違ってよい
2. **Wide の sim**: `make sim-all` が 28 個とも通過し、sim のログが一本化の前の木と同じ
3. **2G-4 の sim**: `make sim-all` が 18 個とも通過し、出力が M5 の回し直しと同じ（`tb` の番地・模型のログの秒を除く）
4. **Fine のビルド**（既定の戦略・`JOBS=8`）: **FDRI が v1.0.0 と同じ**（`e095fa97…29f9`）
5. **Wide のビルド**（`IMPL=Performance_Explore JOBS=8`）: **FDRI が v1.0.0 と同じ**（`abc66e72…4d4736`）。Wide の一本化と同じく、配線の後の `open_run` で Vivado が落ちても bit が出ていれば FDRI で判定する
6. **2G-4 のビルド**（既定の戦略・BUILD_JOBS 8）: **FDRI が M3・M5 と同じ**（`f05e1f62…3b1c`）。2G-4 は読むファイルの中身が同じ（置き場所だけ違う）

**予言**: 6 つとも同じ。既定のパラメータでは式が同じなので、合成は同じネットリストを作る。外れるとしたら、Fine の `tp_core` に繋がない入力 `f0_ext`・Wide と Fine の `rec_fr` の幅をパラメータから作る書き方で、合成が名前・順番の違う部品を作り、配置のタイブレークが動くこと（そのときは 1〜3 は通り、4・5 だけが外れる）。2G-4 は M3 で「ディレクトリだけ違う作り直しで構成データまで同じ」だったので 6 は当たる見込みが高い

### `hw/common/` の一本化の 1 回目の結果と、直して回し直す予言（2026-10-29）

**1 回目（8f9916e）: 4 が外れた → このままでは一本化しない**。
1. Fine の sim: 通過。出力 399 個のうち 347 個がバイト単位で同じ、違う 52 個は全部 `tb*`（34 個は番地とパスの読み替えで同じ、18 個は 3 個のどれかを含む）。9 個とも「全部通過」、sim-ring「総合: 通過」（Wide の一本化のときの Fine と同じ形）
2. Wide の sim: 通過。28 個とも通過、`tb` 以外の 152 個が前の木とバイト単位で同じ（`tb` 27 個のうち 18 個は読み替えで同じ、9 個は 3 個を含む）
3. 2G-4 の sim: 通過。18 個とも通過、252 個のうち 204 個が M5 と同じ、違う 48 個の `tb` は番地とパスの読み替えで全部同じ、模型のログ 3 個は秒だけ
4. **Fine のビルド: 外れ**。FDRI `02b7e732…523c`（v1.0.0 は `e095fa97…29f9`）。**対照**: 同じ日・同じ条件で一本化の前の木（main 6ee64b1）を作り直すと `e095fa97…29f9`（v1.0.0 と同じ）→ 一本化が原因。OOC の `s45_core` の合成の時点で LUT +13〜+32・CARRY8 +1 違う（配置のタイブレークではなく合成が別の回路を作る）。1 個ずつ OOC で合成すると **rec_fr が LUT 594 → 599**、tp_core は同じ（LUT 807・FF 971）。原因は rec_fr の `n_cap == np - 1`（2 か所）: 旧版は `np - 13'd1`（13 bit で引く）、新版は幅の無い 1 で 32 bit に広げて引くので np = 0（起きない）の答えが違う。`np - 1'b1` に直すと OOC の LUT が 594 に戻る
5. Wide のビルド: `impl_1` の頭（dcp の読み込み）と OOC の合成で Vivado が 3 回 segfault（空きメモリ 80 GB 以上。前からの型）。直す前の rec_fr なので 4 の後で止めた
6. 2G-4 のビルド: メモリ（3 本同時で空き 2 GB）のため止め、回していない

**直したもの**: `hw/common/rec_fr.v` の `np - 1` → `np - 1'b1`（2 か所）。**予言（回し直す前）**: Fine・Wide は NCH 4096 で旧版と同じ式なので、1・2 は前と同じ出力、**4・5 の FDRI が v1.0.0 と同じ**。2G-4（NCH 32768）は np = 0 の式が M5（proj031）と変わるので、**6 の FDRI は M5 と違う見込み**（sim の 3 は同じ出力。sim-recfr は旧版と NCH 4096 で比べるので通る）。2G-4 は M6 の判定をこの bit で回す

### `hw/common/` の一本化の 2 回目の結果（eedc3dc、2026-10-29）と、2G-4 のタイミングを詰める予言

1. Fine の sim: 通過（1 回目と同じ形: 399 個のうち 347 個が同じ、`tb` の 34 個は読み替えで同じ、18 個は 3 個を含む。9 個とも「全部通過」、sim-ring「総合: 通過」）
2. Wide の sim: 通過（28 個、`tb` 以外の 152 個が前の木と同じ）
3. 2G-4 の sim: 通過（18 個。252 個のうち 204 個が M5 と同じ、34 個は読み替えで同じ、14 個は rec_fr を含む `tb`。sim の出力は全部 M5 と同じ）
4. **Fine のビルド: 合格**。FDRI `e095fa97…29f9`（v1.0.0 と同じ）・WNS / WHS +0.044057 / +0.009766 ns（v1.0.0 と同じ）・utilization_hier・cdc・net_check が v1.0.0 の build と同じ。1 回目の作り直しは `impl_1` の頭で Vivado が segfault（回し直しの仕組みの外）したので最初から作り直した
5. **Wide のビルド: 合格**。FDRI `abc66e72…4d4736`（v1.0.0 と同じ）・WNS / WHS +0.000716 / +0.009500 ns。この回の中で Vivado が 5 回 segfault し、`build.tcl` の回し直しで完走
6. **2G-4 のビルド（既定の戦略）: タイミングが閉じない**。WNS −0.351610 ns・WHS +0.009507 ns（M5 は +0.047 ns）。負けの経路は rec_fr ではなく全体に散る（PFB の sat_cnt −0.352、ひねり係数の掛け算 −0.188、FFT −0.146、u_cmn → gb_gate −0.076 など）。rec_fr の合成が変わって配置が組み替わり、もともとぎりぎり（+0.047）だった 2G-4 が負けた側に出た（予言は「FDRI が M5 と違う」までで、タイミングは読めていなかった）

**扱い（2026-10-29、実験者の判断）**: `hw/common/` は今の形（Fine・Wide は v1.0.0 と同じ）のまま、2G-4 は新しい形で実装の戦略を替えてタイミングを詰める。M3 の「移植元と FDRI が同じ」はこの bit では成り立たなくなり、M6 はこの bit で回す。
**予言（回す前）**: `IMPL=Performance_Explore` と `IMPL=Performance_ExtraTimingOpt` を並べて回す（BUILD_JOBS 8）。負けの量（−0.35 ns）は配置の運で出る幅（proj023 の Wide は既定で負け、PE で +0.0007）に入るので、どちらか 1 本は閉じる見込み（WNS ≧ 0・WHS ≧ 0・build.tcl の照合が全部通る）。閉じた方を 2G-4 の bit にし、FDRI・USR_ACCESS・WNS をここと 2G-4 の README に書く。2 本とも閉じなければ、負けの経路（PFB の sat_cnt）を見て RTL か制約で手を打つかを相談する

### 2G-4 のタイミングを詰めた結果（2026-10-29〜30）: 予言どおり 1 本が閉じた

- `IMPL=Performance_Explore`: 合成の段で Vivado が 4 回 segfault し、`raw_sel_1` の OOC が回し直しても通らず止まった（設計ではなく Vivado の不安定。下）
- **`IMPL=Performance_ExtraTimingOpt`: 閉じた**。配線の後 WNS +0.047・WHS +0.009 ns（負けの端点 0）。`impl_1` は `write_bitstream` まで完走したが、親の Vivado が設計を開き直す所で segfault（Wide の一本化のときと同じ型）→ `make post IMPL=Performance_ExtraTimingOpt` で後段を仕上げた: **TIMING（確定）WNS +0.046737 / WHS +0.009404 ns・FDRI `a9a01b81dd8c1f0942b7d82c1bd37c211e301d7a39b4ac1620704ae7c0f55488`・USR_ACCESS 52d27230（汚れなし）**。M5 の bit と比べて、address_map・cdc（分類別の件数）・clocks・net_check・rfdc_params・xfft_params が同じ、BRAM 692・URAM 56・DSP 2,064 が同じ、LUT −9・FF +117（配置の後の複製）、DRC は同じ規則で DPOP-3 が 63 → 64 だけ
- **Vivado の不安定（2026-10-29）**: 合わせて 15 回を越える segfault（合成・`impl_1` の頭・配置・設計を開き直す所と場所が散る）。いつもは数日に 1 回、多かったのはビルドを並べた 10-23 の 5 回。並べると落ちやすい見当だが、1 本だけでも落ちた。カーネルのログに MCE・EDAC の誤りは無い（EDAC はメモリコントローラの driver が当たっていないので、訂正の誤りが出ない形かもしれない）。Fine・Wide は v1.0.0 とビットまで同じ構成データを出したので、黙って壊れた結果ではない。2G-4 の PETO の bit は比べる相手が無いので、**同じ戦略でもう 1 回作り直し、FDRI がそろうかを確かめてから M6 に使う**

### 2G-4 の PETO の確かめの作り直し（2026-10-30）: FDRI がそろわず、一続きの回は閉じない

同じ戦略（`IMPL=Performance_ExtraTimingOpt`、BUILD_JOBS 8、8c0d68b）で 1 本だけ作り直した。**FDRI `4851ae4d…ffd9`（1 回目 `a9a01b81…5488` と違う）・WNS −0.351120 ns（334 端点）・WHS +0.009507 ns → 閉じない**（既定の戦略の −0.352 とほぼ同じ）。
- 合成の 39 個は資源の数が 1 回目と同じ。`impl_1` のチェックサムは配置の Phase 2.4.1 まで 1 回目と全部同じ
- **分かれた所**: 1 回目は Phase 2.4.2（Physical Synthesis In Placer）で Vivado が segfault し、回し直しが `system_wrapper_opt.dcp` を開くところから始まった（「ShapeDB restore issue … ShapeDB will be regenerated」）。そこから先の配置が別物になり、偶然 WNS +0.047 に着いた。2 回目は落ちずに一続きで走った
- **したがって 1 回目の bit `a9a01b81…` は作り直せない**（同じ所で落ちたときだけ出る）。マシンの不具合でデータが化けた形ではない（分かれた所が手順の違いで説明できる）
- 今の rec_fr の 2G-4 は、既定・PETO の一続きの回で閉じない。PE は合成の段の segfault で回っていない

**次の手（2026-10-30、実験者の判断）: `IMPL=Performance_Explore` を 1 本だけ**。予言: 閉じるかは五分五分（Wide を閉じた戦略だが、2G-4 は既定と PETO の一続きの回が同じ −0.35 ns に落ちた）。`impl_1` の中で Vivado が落ちて dcp から回し直したら、その回は作り直せない道筋なので閉じても保留にする。閉じたら同じ戦略でもう 1 回作り直し、FDRI がそろうことを確かめてから 2G-4 の bit にする

**Performance_Explore の結果（2026-10-30）: 閉じない**。WNS −0.230648 ns（118 端点）・WHS +0.001482 ns。合成の段で 2 回 segfault（回し直しで続いた）、`impl_1` の中では落ちていない（一続きの回）。今の rec_fr の 2G-4 は、既定（−0.352）・PETO の一続き（−0.351）・PE（−0.231）のどれでも閉じない

**扱い（2026-10-30、実験者の判断）: rec_fr だけ 2G-4 に写しを戻す**。`hw/bits/2g-4/src/rec_fr.v` を main 6ee64b1 の版（= proj031・M5）に戻し、2G-4 の Makefile（2 行）・build.tcl（1 行）の rec_fr をそちらへ。core_cmn・tp_core は `hw/common/` のまま（中身が M5 の写しとバイト単位で同じ）。`hw/common/` は変えない（Fine・Wide は v1.0.0 と FDRI まで同じことを確かめ済み）。rec_fr は 2 版が残る（`hw/common/` = NCH を引数・`np − 1'b1`、2G-4 = NCH を引数・`np − 1`）。
**予言**: 2G-4 が読む中身が全部 M5 と同じなので、既定の戦略 1 本で **FDRI `f05e1f62…3b1c`・WNS +0.047165 ns・WHS 0.000000 ns（M3・M5 と同じ）**、`make sim-all` の出力も M5 と同じ（`tb` は core_cmn・tp_core のパスだけ違う）

**rec_fr だけ写しを戻した結果（2026-10-30、64dbf45）: 予言どおり**。2G-4 の `make sim-all` が 18 個とも通過し、252 個のうち 204 個が M5 とバイト単位で同じ、48 個の `tb` は番地とパスの読み替えで全部同じ、ログ 18 個のうち 3 個は経過秒だけ。既定の戦略の作り直し（`impl_1` の中では落ちていない一続きの回）で **FDRI `f05e1f62…3b1c`・WNS / WHS +0.047165 / 0.000000 ns（M3・M5 と同じ）**、USR_ACCESS 64dbf450（汚れなし）。**一本化の結論**: `hw/common/` の core_cmn・tp_core は Fine・Wide・2G-4 で共有、rec_fr は `hw/common/`（Fine・Wide）と `hw/bits/2g-4/src/`（2G-4）の 2 版。2G-4 の bit は M5 のまま（M6 は M5 の bit で回せる）

### M5 の手順と予言（2026-10-28、ブランチ `2g-4/m5-ps`、測る前）

**M5b のフック**（7befb74）: Wide の Makefile・build.tcl の USR_ACCESS の部分（Makefile 12 行・build.tcl 22 行）をそのまま 2G-4 に写した。RTL・制約・配置には触れない。`make -n build` で USR_ACCESS が git から作られ、Vivado の後に `sw/pynq/bitinfo.py` の読み返しが走る。

**PS の一本化**（f8ee13d、`sw/pynq-2g/` を消した）。土台を study-rfsoc の **`proj023-m0` の `pynq/`** にした 3 方向のマージ（`sw/pynq/` は proj021-m0 ＋ proj023-m0 ＋ Fine・Wide の M5 の後の変更、`sw/pynq-2g/` は proj023-m0 から proj024〜036 で枝分かれした系統）:

| 分け | ファイル | 扱い |
|---|---|---|
| 同じ（20） | acqboot・extref・instr・rectap・s45pn・s45proto・s45resp・s45snap・s45snapplot・s45spur・s45tastar・s45v2a・s45v2c・s45v2f・sg・specctl・test_cal_b・test_tpjump・tpjump・window | そのまま |
| `sw/pynq/` の側だけ変えた（8） | bits.example.json・s45allan・s45cal・s45lin・spectrometer・test_regmap・timetest・tp_cal.json | `sw/pynq/` のまま |
| 2G の側だけ変えた（3） | s45client（`if_axis`・ch 数で溜めを割る）・specrecv（FULL のフレーム nch / 8）・**widef2** | s45client・specrecv は 2G の版。**widef2 は 2G の側が Wide の F-2 を 2G-4 専用に書き換えていた**（自動のマージでは 2G の版が勝ち、Wide の F-2 が壊れる）ので、Wide の版を残し、2G の版を **`g24f2.py`** として足した |
| 両方変えた・衝突なし（3） | s45acq（2G の 3 本の裏・Bundler の C の道・malloc_tune など、2G の変更はほぼ足すだけ）・specd・s45ring | 自動のマージ |
| 両方変えた・衝突あり（4、7 か所） | plring（`--bitfile` の既定）・s45core（定数 1・`--bitfile` 1）・test_fake.sh（使い方の注 1・試験の一覧 1）・timebase（CAL の表 1・time_core の ID の一覧 1） | `sw/pynq/` の形に 2G の分を足した（既定の bit は Fine の proj021 のまま。`BIT_REV_MIN_BY_KIND` に 2G の 3・10・11、CAL は (BIT_KIND, BIT_REV) の鍵のまま） |
| 2G だけ（13） | amslog・build_fast.sh・cuctl・g24cu・g24cw・level・loopsum・s45fast.c・s45fast.py・test_bund_fast・test_nch・test_ring_fast・test_s45fast | 足した（README は消した） |
| `sw/pynq/` だけ（7） | bitinfo・h2peek・sgstat・wide・wide_v2・widecomb・wideresp | そのまま |

足した直し:
- **timebase**: CAL に **(3, 1)**: pps_det_ns 71.5・adc_to_core_ns A 140.9・B 141.1・C 141.6・D 141.9・**bound_ns 50**（proj031 rev 2 の R-5 の F-2。bound は移植元の 50 のまま。Fine・Wide の 5 にそろえるかは F-2 を PWR 3 で測り直してから）。time_core の ID の一覧に 2G の 3 本（0x020B_0102・0x020A_0102・0x0203_0102）。**2G-1・2G-2 の CAL（11, 1）・(10, 1) は入れない**（proj024・025 の値は、移植で作り直す bit とは別の配置。入れないと、その bit では錨の前に「較正定数を持っていない」で止まる = 黙って違う値を使わない）
- **s45acq**: G21・G22（G24 はその子）の裏も `_setup_lmx()`・`_lmx_ids()` を通す（Wide の M5 の後の直しと同じ。proj024〜036 は LMX を書かず出荷時の 31 のままだった）。ID に `usr`（USR_ACCESS）
- **予算を越える tint を SET で断る**（`s45acq.check_net`、interface 4.5）: float32 の SPEC の中身の量（1 ダンプで送る ch の合計 × 4 B / tint、頭と TP は数えない）が **30 MB/s** を越えたら ERR。理由に量と、その構成の tint の最小を出す。2G-4・2G-2 は 10.24 ms（51.2 MB/s）を断り 20.48 ms（25.6）は通す、2G-1 も同じ。Fine・Wide は 10.24 ms で 12.8 MB/s（断らない）。**specd の `--net-budget-mbs 0` で外す**（陽性対照・BUND の 10.24 ms の試験の形）。fmt u64・both は試験の形なので float32 の量で照らす
- **リング 64 MiB**: コードは proj024 から 2G の裏の既定が `G_RING_MIB` 64（`--ring-mib` を渡さなければ 64）。specd の help が「既定 32、2G-1 は 64」と古いままだったので直した。判定の共通の前提から `--ring-mib 64` を外した
- `hw/bits/2g-4`（Makefile の CU_WORDS の依存・`sim/check_cu.py`・build.tcl の注）と `model/cu_model.py` の `sw/pynq-2g` の道を `sw/pynq` に。`libs45fast.so` を .gitignore に
- 判定（`test/acceptance/2g-4/`）: 共通の前提の specd の起こし方、F-2 を `g24f2.py`・鍵 (3, 1) に、BUND の前提に `--net-budget-mbs 0`、NET の手順・合格・陽性対照を確定

**PC で通したもの**（Vivado サーバ、作業用の写しで）: `test_fake.sh all` **31 試験とも通過**（Fine 13・shm・Wide 4・2G 11・net・netp）。**陽性対照の陽性対照**: 照合の定数を 0 にした s45acq では `net` が NG（2G-4 の 10.24 ms が OK になる）。`FAST=--fast`（C の道、x86 なので「CRC: 表」）の `test_fake.sh all` も回す（下の結果）。`test_cal_b`・`test_tpjump`・`wide.py` / `wide_v2.py` / `widecomb.py --selftest`・`test_nch`・`test_s45fast`・`test_ring_fast`・`test_bund_fast` が全部通過、.py 全部が `py_compile` を通る

**予言**:
1. **M2 の回し直し**（`make sim-all`、`sw/pynq/g24cu.py` の道で）: 18 個とも「全部通過」、`build-sim/` の出力は M2 と同じ（RTL も CU_WORDS の元も同じ。違うのは iverilog の `tb` の番地だけ）。COEF_CRC 0x891BE197
2. **M3 の焼き直し**（7befb74、`make build`、`-1`・既定の戦略）: USR_ACCESS `0x7befb740`（commit 7befb74・汚れなし）が焼け、make の読み返しが通る。**FDRI は M3 と同じ**（`f05e1f62…3b1c`）、WNS / WHS は 0.047165 / 0.000000 で小数 6 桁まで同じ。構成の流れ（欄 e）の sha256 は USR_ACCESS の分だけ M3 と違う
3. **M4 の回し直し**（ボードの新しいディレクトリ `2g-4-m5`、今回の bit と一本化した `sw/pynq/`、specd は `--g24` なしで bits.json の `"kind": "g24"`・`--ring-mib` なし・`--lmx-pwr` なし、配線 N/S・ノイズ ON（2026-10-29 に訂正。前は「配線 N」と書いていた））: 1 回の Overlay の読み込みの中で ID-1 → H-0 → EQ-4 → NET → tint 20.48 ms で 300 s。
   - ID-1: M4 と同じ（係数 URAM 0.7 s 台・CRC 0x891be197・STAT 0x15、ID proj 00310200・kind g24）に加えて、ID の **`usr=7befb740`・`lmx_pwr=3`**、ログに「リング 64 MiB」、錨が (3, 1) の CAL で「未較正」でない、「CRC: 命令」
   - H-0（4 窓 × 200、照合 通過・`g24cw` 全部通過、陽性対照 `--src DCBA` で 4 窓とも NG）・EQ-4（50 / 50 組 × 3、陽性対照 0 / 49 × 3）: M4 と同じ
   - NET: `SET tint=0.01024` が ERR で GET は変わらない、`SET tint=0.02048` が OK。陽性対照（`--net-budget-mbs 0` で起こし直す）は OK
   - tint 20.48 ms で 300 s: 取りこぼし 0（miss・pl_drop・pl_crc・pl_err 0、受けの CRC・欠け・kgap・tdev 0、照合 通過）、1 周の計 ≒ 13 ms（M4 の 13.10 ms ± 1 ms）。LMX の PWR が 31 → 3 に変わるので、櫛の線の強さと床の形は M4 と違ってよい（判定の外。tp_dbfs は ±0.1 dB で同じはず: 入力の電力は PWR で変わらない、Wide の M5 の後の 1）
4. **LMX の PWR 3 での測り直し**（Wide の「M5 の後」と同じ型）: F-2（配線 P、ケーブルの入れ替えあり 2 回）で M が CAL の (3, 1)（PWR 31 で測った値）と **4 ADC とも 1 ビート（3.9 ns）以内**（Wide は 31 → 3 で −0.03〜−0.62 ビート）。外れたら (3, 1) を PWR 3 の値で入れ直す。TP の線形性（配線 N ＋ PM・ATT、Wide の P-8 の L-1・L-2 の線）は PWR に依らず通る

### M5 の結果（2026-10-28〜29）: 予言 1〜3 当たり。4 は F-2（最多の山で読み直して通過・CAL 据え置き）・TP の線形性とも当たり

**予言 1（M2 の回し直し、f8ee13d の木、`sw/pynq/g24cu.py` の道）: 当たり**。`make sim-all` が 18 個とも「全部通過」（16 分）。`build-sim/` の 252 個のうち 204 個が M2 の出力とバイト単位で同じ、違う 48 個は iverilog の `tb` だけで、番地（`0x…`）を読み替えると 48 個とも同じ。`build-sim-logs/` の 18 個のうち 15 個が同じ、違う 3 個は模型のログの経過秒だけ（今回はコマンドの行も同じ）。COEF_CRC 0x891BE197

**予言 2（M3 の焼き直し、7befb74、`make build`、`-1`・既定の戦略、6,958 s）: 当たり**

| | M3（移植元と同じ） | M5b |
|---|---|---|
| USR_ACCESS（bitinfo） | なし | **7befb740 = commit 7befb74（汚れなし）**（書き込み 1 回）。make の読み返しの照合 通過、vivado.log と impl_1 の runme.log にも `USR_ACCESS: 0x7befb740` |
| **FDRI** | 8,608,824 語 / `f05e1f62e5e374ced85e2fa99d95a9364a6b72749b6a14169f7161042e3a3b1c` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `66dad151…bef6` | `94a107f13422df82b4876189c556f9c38cb0165c6998245844aa84d096d8b8d3`（USR_ACCESS の書き込みの分） |
| TIMING（確定） | WNS 0.047165 / WHS 0.000000 ns | **同じ（小数 6 桁まで）** |
| 報告 24 個（日付などの行を除く） | | 23 個が同じ。drc.rpt は RTSTAT-10 の網の一覧の最後の 2 行の並びの入れ替わりだけ（Fine の M5b・Wide の M5 と同じ型） |
| runme の CRITICAL WARNING | 0 | 0 |
| `.bit` / `.hwh` の sha256 | `79bb955a…` / `50b40685…` | `e3521f51650daa278a1d4b5ffb318c55dcb821f9c8e6f5030ee54f4300d4330d` / `36e3b23abb863de2e6526d096b49ad95a5cbf65ea4c18bfd7042ba1d5b752239` |

**予言 3（M4 の回し直し）: 当たり**。ボードの `2g-4-m5`（今回の bit・hwh・係数の hex、一本化した `sw/pynq/` の 59 個は手元と sha256 で全部同じ、`build_fast.sh` で「CRC: 命令」）、配線 N/S・ノイズ ON（2026-10-29 に訂正。前は「配線 N」と書いていた）。specd は **`--bits bits.json --clkin 0 --ref 10 --prefault --fast --fast-ring --loop-log-ms 0.1`**（`--g24`・`--ring-mib`・`--lmx-pwr` なし。bits.json の項目は `"kind": "g24"`）。1 回の Overlay の読み込みの中で ID-1 → H-0 → EQ-4 → NET → tint 20.48 ms で 300 s、最後に NET の陽性対照だけ起こし直した:

| | M5（今回） | M4 |
|---|---|---|
| 起動のログ | LMX の出力の強さ **OUTA 31 → 3・OUTB 31 → 3**、係数 URAM 4096 行を **0.73 s**・VERIFY 通過（CRC 0x891be197・STAT 0x15）、**リング SIZE 67108864（64 MiB）**、錨 `EPOCH 1`（(3, 1) の CAL で通った）、「SPEC の記録（FULL）は C（s45fast、CRC 命令）」 | 同じ（LMX は書かず 31、リングは `--ring-mib 64` で） |
| ID-1 | adc_id 02030101・time_id 02030102・**usr 7befb740・lmx_pwr 3**、STATUS IDLE・time_ok 1・health 0・flags 0。START の EVENT の ids に proj 00310200・kind g24。`GET CAL`（TP の dBm）は「bit が違う（較正 [(2, 3), (1, 1)]・載っている (3, 1)）」で使わない（2G-4 の tp_cal は M6） | 同じ（usr なし・lmx_pwr 31） |
| H-0（4 窓 × 200） | 800 本・CRC 0・説明のない欠け 0・照合 通過・`g24cw` 全部通過・miss・health・flags 0。床の中央値 A0 6.48e3・B0 6.41e3・C0 6.33e3・D0 6.45e3。陽性対照 `--src DCBA` で 4 窓とも NG | 床 6.47e3・6.43e3・6.32e3・6.44e3、ほか同じ |
| EQ-4 | **50 / 50 組 × 3**・照合 通過（f32 の組 200・不一致 0）、陽性対照 0 / 49 組 × 3（違う ch 32,765〜32,768） | 同じ |
| NET | `SET tint=0.01024` → `ERR ARG … 51.2 MB/s（予算 30 MB/s を越える。INTERFACE 4.5）。この構成の tint の最小は 0.02048 s`、直後の GET は 0.04096 のまま、`SET tint=0.02048` は OK。**陽性対照**（`--net-budget-mbs 0` で起こし直す）: `SET tint=0.01024` が OK・GET 0.01024 | （照合なし） |
| tint 20.48 ms で 300 s | SPEC **58,505**・7.36 GB・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。STATUS: miss・pl_drop・pl_crc・pl_err 0・time_ok 1・forced 0・loop_slow 1・最長 21.82 ms・p99 11.1 ms・pl_peak 3.2 MB・bund_r 4 窓とも 1,048,576。**1 周の計 13.03 ms**（`loopsum.py --nwin 4`）。tp_dbfs −31.35・−31.33・−31.31・−31.20。AXI_MAX_PIPELINE 前後 0x0102 | SPEC 58,505・最長 22.74 ms・p99 11.2 ms・山 3.2 MB・1 周の計 13.10 ms |

- 判定の外: specd を止めるとログに `KeyError: '/psm_…'`（multiprocessing の resource_tracker）が出る。Wide の M6 の specd のログ 4 本にも同じ行があり、`sw/pynq/` の溜まりの片付けの直し（既知の制限 3）からの振る舞い。`/dev/shm` は毎回空（一本化で増えたものではない）
- **STATUS の `data_drop` にも受け手の IP とポートが出る**（`data_client` と同じ）。記録に残すときは両方を伏せる
- 起こし方の注: 非ログインの ssh から specd を起こすと XRT の環境が無く `Overlay()` が「No Devices Found」で止まる（`boardname.sh` だけでは足りない）。`bash -lc` で起こした。判定の文書の specd の起こし方は root のログインシェルの前提のまま
- 先に M3 の bit（USR_ACCESS なし）で同じ PS の起動・ID・NET・20.48 ms で 30 s を通した（ボードの `2g-4-m5pre`、`usr=none`）。本番は上の `2g-4-m5`
- 記録: 制御 PC の `~/m2/2g4m5/`（`id1.txt`・`h0*`・`eq4*`・`net.txt`・`netp.txt`・`v2b_*`・`axi_*.txt`・`specd_m5.log`。`.s45` は照合が済んだので消してよい）、ボードの `2g-4-m5/runs/`

**予言 4 の F-2（2026-10-29、配線 P、bit `e3521f51…`・PWR 3、ボード直 `g24f2.py`、ボードの `2g-4-m5`）: M は当たり、判定は σ で失敗**。組は `f2_a2`（まっすぐ）と `f2_b`（A↔D・B↔C）: M = A 69.8・B 69.9・C 70.4・D 70.3 ns、CAL (3, 1) の M（69.4・69.6・70.1・70.4）から +0.4・+0.3・+0.3・−0.1 ns（1 ビートの 1 割）、2 回の差 0.05〜0.19 ビート → **CAL は据え置き**（予言 4 の線）。失敗は 1 回の中の σ: `f2_b` の A が 0.44（線 0.4。B・C・D は 0.34〜0.37）。最初の `f2_a`（まっすぐ）は A 0.41・B 0.40・C 0.42 で NG（D 0.34）。どちらも縁のサンプルは 5 試行で ±0.2 ビートに止まり、T − スタンプが 5 試行のうち 1〜2 回 ≒ 0.9 ビート低い（スタンプが +1 ビート）。`f2_b` では縁のサンプルが遅い試行（402.25）でスタンプが +1 → **1PPS のスタンプがビートの境目に乗っている**（Wide の M6 の F-2 の A の 1 試行と同じ形）。ケーブルを替えずに Overlay を載せ直した `f2_a2` は縁のビートが 348.7 → 130.0 に移り、σ 0.08〜0.13 で通過（予言どおり、境目の乗り方は Overlay の読み込みごとに変わる）。(p) は 3 回 × 4 ADC × 5 試行とも見えない（最大 / σ 3.0〜4.9）。σ の線（平均と σ で読む）を境目に乗った回でどう扱うかは保留（実験者の判断）。記録は制御 PC の `~/m2/2g4m5/f2/`

**F-2 の読み直し（2026-10-29、実験者の判断で案 1: 1 回の値を最多の山で読む。合格の線は b2ddc12 で先に書き換えた）の予言**: 組（`f2_a2`・`f2_b`）の M ≒ A 70.4・B 70.3・C 70.7・D 70.7 ns（CAL から +1.0・+0.7・+0.6・+0.3 ns、±1 ビートの内で通過）。境目に乗った試行（最多の山の外）は `f2_a2` が 4 ADC とも 0、`f2_b` が A 2・B 1・C 1・D 1。`g24f2.py --selftest` の陽性対照 3 つ（山が過半に届かない・山の間 2 ビート・山の中が広い）はどれも NG

**読み直しの結果: 当たり（組は通過）**。`g24f2.py --selftest` 全部通過（陽性対照 3 つとも NG）。npz の meta から戻した試行ごとの値の平均は 3 回 × 4 ADC とも json の平均と一致。組（`f2_a2`・`f2_b`）: M = A 70.5・B 70.3・C 70.7・D 70.7 ns（CAL から +1.1・+0.7・+0.6・+0.3 ns）・2 回の差 0.22〜0.37 ビート・山の中の σ ≦ 0.13・境目 `f2_a2` 0・`f2_b` A 2・B 1・C 1・D 1 → **F-2 通過、CAL は据え置き**。**見つけたこと**: 組にしなかった `f2_a` も最多の山で読むと 4 ADC とも山の線は通る（境目 A 2・B 2・C 2・D 1）が、C の 3 対 2 は低い側の山（+17.12）が勝ち、`f2_a` と `f2_b` の組では C の 2 回の差が 1.17 ビートで NG（M は 69.2・69.7・69.2・70.8 ns、CAL から ±1 ns の内）。境目に乗った回は、どちらの山が勝つかで 1 回の値に 1 ビートの曖昧さが残る（真の遅れは 2 つの山の間で、スタンプが 1 ビートに丸める）。CAL の決め（±1 ビート）はどちらの組でも変わらないが、2 回の差 ≦ 1 ビートの線はこの曖昧さに当たりうる。記録は `~/m2/2g4m5/f2/combine_peaks*.txt`

**main の取り込み（2026-10-29、PR #64〜#71。ADR 0023〜0026）**: 時刻の較正はボードごとのファイル（ADR 0023）・TP の dBm の較正もボードごと（0025）になっていた。ADR 0023 の「2G の PS は一本化のときにこの形に合わせる」に従い、G21・G22（G24 は G22 を継ぐ）の Backend の Timebase に `log` を渡し、ID に `tcal`・`board` を出す（Wide と同じ）。`bits.example.json` の 2g-4 から `tp_cal` を外した（ボードの `/etc/yatsugatake/tp_cal.json`）。**2G-4 の ADC → コアの道は共通コアと同じ**（ADC_PATH に番号を足さない）: ギアボックス・RAW・スタンプの RTL（gb_adc・gb_gate・raw_core・dstamp・adc_ev・time_core・axis_sel4）は `hw/common` の同じファイル、RFDC のセルの組み立て・fs 4.096 GSPS・spw_adc 12 → spw 16 が Wide の build.tcl と同じ、`src/core_cmn.v` と `hw/common/core_cmn.v` の差は TP の繋がない入口の 1 行。今日の F-2 の M（70.3〜70.7 ns）は Wide M6 の M（69.7〜70.1 ns）と ≦ 1.0 ns。ADR 0023 で F-2 は道を変えた bit だけになったので、上の F-2 の測りと最多の山の読みは、本番の較正（`timecal.py`、Wide の bit で Overlay 5 回）には効かない。ただし `timecal.py` の 1 回の線も σ ≦ 0.4 で、スタンプが境目に乗った回は同じ形で落ちうる

**CU（2026-10-29、配線 P のまま、ケーブルは A↔D・B↔C）: 通過**。M5 の bit・一本化した `sw/pynq/`、specd は bits.json の kind だけで起こした。(i)〜(iv) とも CU.md の合格どおり。(iv) の最初の取得は (i) の受けの後に溜まりに残った 222 個が混ざって g24cw が落ちた（D0 の DUMP_T・flags 0x1）。`CLEAR` してから取り直して通過（specd は起こし直さず）。記録は `~/m2/2g4m5/cu/`

**予言 4 の TP の線形性（2026-10-29 に測る前に書いた）**: 配線 N（ノイズ ON）＋ PM・ATT、specd は M5 の bit・bits.json の kind で、`SET tint=0.04096 fmt=f32 shift=7`（src は既定の ABCD）・`s45lin --lo 0 --hi 40 --step 2`。Wide の P-8 の線: L-1 は TP が −18〜−28 dBFS の段で 4 本とも残差の最大 ≦ 0.05 dB、L-2 は流れ / TP（A0〜D0、流れの中央 90 %）がレベルによらず ±0.02 dB。飽和・振り切れ 0 の段だけ。流れの絶対値は Fine の尺度なので記録だけ（Wide と同じ）。dBFS − PM は記録だけ（Wide M6 の −0.73〜−0.95 dB と同じ程度の見当。tp_cal の (3, 1) を足すかは M6 で決める）。PC の `specd --fake --g24` で `s45lin` が 4 窓と TP 4 本を読むことを確かめた（空の窓 A1〜D1 は飛ばす）

**結果（2026-10-29、`~/m2/2g4m5/lin/lin_g24`）: L-1・L-2 とも当たり**。49 段（ATT 0〜40 dB を 2 往復・床 7 段）、飽和・振り切れ・health 0。L-1（TP −18〜−28 dBFS = ATT 0〜8 の 10 段、`analyze(pm_min=-26.5)`）: TP A・B・C・D の残差の最大 0.013・0.011・0.009・0.009 dB、流れ A0〜D0 も 0.009〜0.013 dB（Wide M6 の 0.010〜0.014 と同じ程度）。L-2（流れ / TP）: ずれの最大 A0 0.0006・B0 0.0010・C0 0.0008・D0 0.0088 dB（±0.02 の内）。dBFS − PM（記録だけ）: A −0.91・B −0.90・C −0.90・D −0.80 dB（Wide M6 の −0.85・−0.95・−0.82・−0.73 と 0.1 dB 以内）。`s45lin` 自身の OK/NG は −45 dBm までの全段で見るので範囲が違う（流れ A0・B0・C0 が NG、記録だけ。Wide と同じ扱い）。STATUS miss・pl_drop 0・time_ok 1、AXI_MAX_PIPELINE 前後 0x0102。制御 PC に matplotlib が無く図は描けなかった（数値の記録 `.lin.json` は出た）

### M5 の後: 測り方の方針の変更への切り替え（ADR 0023〜0026、2026-10-29）

評価の配線の替え（F-2 の配線 P・ノイズソースの手での ON / OFF）で作業が止まるのを減らすため、2026-10-29 に方針を変えた（PR #64〜#71）。
M5 の main の取り込み（上）で、PS は ADR 0023・0025 の形にもう合わせてある。残りは測り方と判定の手順。

**進行中の測定は、今の手順のまま終える。** 判定の区切り（1 つの判定が終わったとき、または次の M の頭）から、下の形に切り替える。
途中で切り替えると、同じ判定の中で前提が混ざる。切り替えた日と、最初に新しい形で回した判定を、この節に書き足す。

1. **F-2（配線 P）は 2G-4 では回さない**（ADR 0023）
   - 2G-4 の ADC → コアの道は共通コアと同じ。M5 で確かめ、`ADC_PATH` に番号を足していない
   - 時刻は開発のボードの `/etc/yatsugatake/time_cal.json` が当たる（2026-10-29 に Wide の bit で `timecal.py`。M = A 69.6・B 71.2・C 69.7・D 69.7 ns、bound_ns 5）。specd の `ID` は `tcal=board` になる
   - それより前の 2G-4 の記録は `tcal=provisional`（`CAL[(3, 1)]`、bound_ns 50）。記録を比べるときは、どちらの較正で取ったかを書く
   - ギアボックス・RFDC の設定・RAW・スタンプの RTL を変えた版を作ったら、`ADC_PATH` に新しい番号を足し、その bit で `timecal.py` を回す（F-2 はそのときだけ）
2. **ノイズソースは常時 ON。手で切らない**（ADR 0024。電源 KIKUSUI PMX18-2A、宛先は環境変数 `RFSOC_NS`）
   - ノイズ OFF の要る判定は、道具で切って測り、測り終えたら戻す
     - ボードか制御 PC で `python3 instr.py ns off` → 測る → `python3 instr.py ns on`
     - Python の中なら `with instr.noise_off():`
   - `on()`・`off()` は電源の出力が落ち着くまで（≒ 1 s）待ってから戻る（PR #71）。戻った直後から測ってよい
   - 2G の道具（`g24cw.py` など）には `--ns-off` が無い。足すなら Wide の `wideresp.py` と同じ形で、別の PR にする
   - 切り替えのときに直す判定:
     - **H-2**（前提が「配線 N/S・ノイズソース OFF」）の手順に、上の OFF と ON を書く
     - README の配線の欄の「N/S ＋ ノイズ ON」の注を、「N/S はノイズ ON が既定、OFF は道具が作る」に書き換える
3. **TP の dBm は、ボードの `/etc/yatsugatake/tp_cal.json` が 2G-4 にも当たる**（ADR 0025。ADC の道 1 で引くので、(3, 1) に別に足す作業は無い）
   - 開発のボードには 2026-10-29 に、前の tp_cal.json（Fine・Wide で測った K）を `s45cal.py adopt` で置いた
   - **M6 で確かめること**: Wide の bit と同じ日・同じ配線で dBFS − PM を並べ、差が 4 本とも ≦ 0.07 dB か（Wide の (1, 1) を足したときと同じ線）
     - M5 の値は A −0.91・B −0.90・C −0.90・D −0.80 dB。Wide M6 との差は 0.05〜0.08 dB だが、別の日の比べ
     - 外れたら、TP の道を時刻の道（`ADC_PATH`）と分ける必要がある。今は 1 つの表なので、ADR を足してから直す
4. **一本化した `sw/pynq/` でそのまま効くもの**（2G の側の作業は無い）:
   - ボードの印が eth0 の MAC になる（ADR 0026）
   - `GET CAL` に `board`・`adc_path` が出る（PR #70）
   - ノイズソースの待ち（PR #71）
   - ただし、ボードの `2g-4-m5/` にある `sw/pynq/` の写しは PR #70・#71 より前のもの（`instr.py`・`timebase.py`・`specd.py` の sha256 が手元と違う）。切り替えのときに送り直す

**切り替えた日**: 2026-10-30。最初に新しい形で回した判定は M6 の ID-1（ボードの `time_cal.json`・`tp_cal.json`、ノイズは常時 ON で H-2 だけ道具で切る）

### M6 の手順と予言（2026-10-30、ブランチ `2g-4/m6`、測る前）

**bit と PS**: main 64dbf45 の作り直し（`hw/bits/2g-4/build/`、FDRI `f05e1f62…3b1c` = M3・M5 と同じ、USR_ACCESS 64dbf450）と、main be0370e の `sw/pynq/`（PR #70・#71 の後）。ボードの新しいディレクトリ `2g-4-m6` に置き、`build_fast.sh`（「CRC: 命令」）。specd は `--bits bits.json --clkin 0 --ref 10 --prefault --fast --fast-ring --loop-log-ms 0.1`（bits.json の kind g24、`tp_cal` は書かない = ボードの `/etc/yatsugatake/tp_cal.json`）。

**配線 N/S（ノイズ ON が既定・SG の口）で、1 回の Overlay の読み込みの中で** ID-1 → H-0 → EQ-4 → H-2 → CU → NET、最後に NET の陽性対照だけ specd を `--net-budget-mbs 0` で起こし直す。H-2 は `instr.py ns off` → 4 点 → `ns on`。

**予言**:
1. ID-1: adc 02030101・time 02030102・proj 00310200・kind g24・**usr 64dbf450**・lmx_pwr 3・**tcal board**（ボードの time_cal.json、ADR 0023 の後の初めての 2G-4）。係数 URAM 0.6〜1.0 s・CRC 0x891be197・STAT 0x15。STATUS IDLE・time_ok 1・health 0・flags 0。AXI_MAX_PIPELINE 0x0102。`GET CAL` は time の a2c_ns が A 69.6・B 71.2・C 69.7・D 69.7（ボードの M）、TP は道 1 の K でボードの tp_cal.json が当たる（M5 までは「bit が違う」で使わなかった）
2. H-0: 4 窓 × 200・CRC 0・説明のない欠け 0・`g24cw` 全部通過・flags・health・miss 0。床は M4・M5（同じ N/S・ノイズ ON）の 6.33e3〜6.48e3 と ±0.7 dB。陽性対照 `--src DCBA` で 4 窓とも NG
3. EQ-4: 50 / 50 組 × 3、陽性対照 0 / 49 組 × 3（M4・M5 と同じ）
4. H-2: 4 点（3000.25・2500.5・3396.5・2597.25 MHz）× 4 窓とも CW が見え、ピークの送る番号 i が期待と一致・軸と SG の差 ≦ df / 2（proj030 R-6 は 0 Hz）・sat 0。陽性対照 `--posctl` で 4 点とも落ちる。ノイズは `ns off` の後に `ns state` で OFF、終わりに ON に戻る
5. CU: M5 と同じ（(i) STAT 0x15 → 0x14・4 窓とも同じダンプから flags bit 0、(ii)(iii) START を断る・CRC 0x8d342791、(iv) `CLEAR` の後 4 窓 × 50・`g24cw` 通過・flags 0）
6. NET: 10.24 ms は ERR で GET は変わらず、20.48 ms は OK。陽性対照（`--net-budget-mbs 0`）で 10.24 ms が OK

配線 N に替えてから: BUND・V2-b（30 分）・V2-L（2 時間）・RING、TP の dBm の Wide との比べ（上の 3.）

### M6 の結果（配線 N/S の分、2026-10-30）: 予言 1〜6 とも当たり

ボードの `2g-4-m6`（bit `2ef9394c…`・FDRI `f05e1f62…3b1c`、`sw/pynq/` の 62 個は手元と sha256 で全部同じ、「CRC: 命令」）。前に study-rfsoc proj034 の amslog が動いていたので、実験者の了解で止めた。AXI_MAX_PIPELINE 前後 0x0102。

| 判定 | 結果 |
|---|---|
| ID-1 | usr 64dbf450・lmx_pwr 3・**tcal board**（a2c_ns A 69.6・B 71.2・C 69.7・D 69.7、bound 5）・TP は adc_path 1 の K が当たる（prov 0）。係数 URAM 0.73 s・CRC 0x891be197。STATUS IDLE・time_ok 1・health 0・flags 0 |
| H-0 | 4 窓 × 200・CRC・欠け 0・`g24cw` 全部通過。床 6.41e3・6.34e3・6.33e3・6.45e3（M5 と ±0.1 dB）。陽性対照 4 窓とも NG |
| EQ-4 | 50 / 50 組 × 3、陽性対照 0 / 49 組 × 3 |
| H-2 | 4 点 × 4 窓とも通過（軸と SG の差 0.0 Hz、ピーク / 中央値 64.6〜69.0 dB）。陽性対照 4 点とも落ちた。ノイズは道具で OFF → ON に戻った（ADR 0024 の形で初めて） |
| CU | (i)〜(iv) とも M5 と同じ |
| NET | 10.24 ms は ERR・GET は変わらず、20.48 ms は OK、陽性対照で 10.24 ms が OK |

記録は制御 PC の `~/m2/2g4m6/`。残り（配線 N）: BUND・V2-b・V2-L・RING、TP の dBm の Wide との比べ

### M6 の手順と予言（配線 N の分、2026-10-30、測る前）

**配線**: N/S の SG の出力を切った形（= 配線 N。N/S は N に SG の口を足しただけで、ノイズは常時 ON、PM の口も同じ）。bit・PS は N/S の分と同じ `2g-4-m6`。
**順**: ① specd を `--net-budget-mbs 0 --loop-log-ms 0.1` で起こし、2 分空回し → BUND（10.24 → 30.72 → 20.48 → 10.24 → 30.72 → 20.48 ms、各 20 s）→ RING（tint 20.48 ms で 2 分走らせ、取得の子のプロセス（s45acq、specd の子。`ps` で確かめる）を 0.3 s 止める → 1 分 → 0.8 s 止める（陽性対照））。② BUND の陽性対照（`--posctl-noacc`）。③ V2-b の陽性対照（`--posctl-ring-stall 8`、40 s）。④ V2-b（既定の引数、30 分、受けは制御 PC に書く）。⑤ V2-L（既定、2 時間、`--out` なし、ボードで amslog 10 s・STATUS と AXI を 1 分ごと）。⑥ TP の dBm: 同じ配線で 2G-4 と Wide（main の `hw/bits/sam45-wide/build-PE/proj023.bit`、FDRI は v1.0.0 と同じ）を `s45lin --lo 0 --hi 40 --step 2` で続けて測り、`analyze(pm_min=-26.5)` の dBFS − PM を並べる。

**予言**:
1. BUND: 4 窓とも 0.999〜1.001（proj036 R-2 は 0.9995〜1.0004）。陽性対照で 30.72 ms が 0.333 ± 0.01 倍
2. RING: 0.3 s で pl_drop 0・kgap 0・pl_peak ≒ 31 MB（< 64 MiB）。0.8 s で pl_drop > 0、受けの kgap は DROP の EVENT で説明される（説明のない欠け 0）
3. V2-b: SPEC ≒ 351,560（4 × 87,890）・24〜26 MB/s・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0、STATUS の miss・pl_drop・pl_crc・pl_err 0・time_ok 1・loop_slow ≦ 5、1 周の計 ≦ 16 ms（M4・M5 の 300 s は 13.0〜13.1 ms）。陽性対照で kgap 4・tdev 0・pl_drop > 0
4. V2-L: 7,200 s で受けの CRC・欠け・説明のない欠け・kgap・tdev 0、STATUS の miss・pl_drop 0 が毎分、AXI 毎分 0x0102、VCCINT ≦ 34 A で平ら（proj027 4f の 2G-4 は ≒ 31 A）、PL の温度が平ら、ボードが落ちない
5. TP の dBm: 2G-4 と Wide の dBFS − PM の差が 4 本とも ≦ 0.07 dB（TP の作りが同じで、同じ日・同じ配線。M5 の 2G-4 は A −0.91・B −0.90・C −0.90・D −0.80）。2G-4 の TP の L-1・L-2 も M5 と同じく通る

### M6 の結果（配線 N の分、2026-10-30）: 予言 1〜5 のうち 4 つ当たり、V2-b の陽性対照でボードが固まった

| 判定 | 結果 |
|---|---|
| BUND | 0.99991〜1.00068（4 窓とも線の内）。陽性対照 0.3330〜0.3332 倍 |
| RING | 0.3 s で pl_drop 0・kgap 0、pl_peak 48.3 MB（予言の 31 MB より多いが 64 MiB の内、ゆとり 28 %）。0.8 s で pl_drop 385・kgap 4 は `BDROP` で説明・説明のない欠け 0 |
| V2-b | 30 分で SPEC 351,479・24.6 MB/s・欠け 0・loop_slow 1・1 周の計 13.26 ms・AXI 前後 0x0102。**陽性対照（`--posctl-ring-stall 8`）でボードが固まった**（下） |
| V2-L | 2 時間で欠け 0・毎分の STATUS と AXI に異常なし・VCCINT 32.3〜33.0 A で平ら・PL の温度 55〜59 ℃ で平ら |
| TP の dBm | 同じ日・同じ配線で 2G-4 と Wide（eedc3dc の作り直し、FDRI は v1.0.0 と同じ、`LOAD` で切り替え）の dBFS − PM: 2G-4 A −0.82・B −0.79・C −0.78・D −0.67、Wide −0.85・−0.82・−0.79・−0.69、**差 +0.01〜+0.03 dB（≦ 0.07）** → ボードの tp_cal.json（道 1）が 2G-4 にそのまま当たる。TP の道を分ける ADR は要らない。2G-4 の L-1 0.010〜0.013 dB・L-2 ≦ 0.0093 dB、Wide の L-1 0.013〜0.014 dB・L-2 ≦ 0.0084 dB |

**V2-b の陽性対照でボードが固まった件（未解決）**: specd を `--posctl-ring-stall 8`（RUN の 100 周目に 8 秒リングを読まない）で起こして START すると、受けに ≒ 18 s 分（SPEC 3,564）届いたところで流れが止まり、制御の口も ssh も ping も応えなくなった。電源の入れ直しで戻った。前の起動の journal は 03:37:19 で途切れ、カーネルの異常の記録は無い（書き残す前に固まった）。RING の 0.8 s（64 MiB を溢れさせた）は正しく落ちを数えて捨てたので、違いは溢れ続けた長さ（8 s ≒ 820 MB 分）。見当: リングの書き手（s45_ring）が長く溢れ続けると番地を取り違えてリングの外の DDR を書く、または偶然。Wide では同じ陽性対照が通っている（2G-4 は 102.4 MB/s で速い）。**再現と止まりの長さ（2・4・8 s）による切り分けを、実験者がボードのそばにいるときに回す**

**V2-b の陽性対照の再現（2026-10-30、実験者がボードのそば、測る前）**: 同じ `--posctl-ring-stall 8` でもう 1 回。固まれば再現する不具合 → 入れ直しの後 2・4 s で切り分け。固まらず予言どおり（kgap 4・tdev 0・pl_drop > 0）なら前回は偶然と読み、もう 1 回回す

**V2-b の陽性対照の再現の結果（2026-10-30）**: 2 回目（同じ引数）は固まらず、止まりの効き目も無かった（pl_drop 0・kgap 0・SPEC 7,723 が欠けなく届く）。`s45acq.py` を読むと、止まりの仕掛け（RUN の 100 周目に `stall_at` 秒眠る）は `HwBackend.pump` の中だけにあり、**G21・G22（G24 は G22 を継ぐ）の `pump()` は自前で上書きしていて持っていなかった** → 2G-4 では陽性対照が黙って空振りしていた（M5 の一本化で 2G の `pump` を持ち込んだときの取りこぼし）。`HwBackend._posctl_stall()` にまとめて 3 つの `pump()` から呼ぶよう直し（`test_fake.sh all` 通過）、ボードで 3 回目: 「リングを 8.0 秒読まない」・1 周の最長 8,343 ms・pl_drop 6,009・miss 3,005・pl_peak 64 MiB・受けの kgap 4・tdev 0・説明のない欠け 0 → **予言どおり、V2-b の陽性対照は通過**、ボードは固まらない。**1 回目にボードが固まったのはリングの溢れではない**（止まりは起きていなかった）。原因は分からず、V2-b（30 分）・V2-L（2 時間）・ほかの判定では起きていない。性能評価の既知の制限に「1 回、原因の分からない固まり」として残す

### M7 の結果（2026-10-30〜31）: リリースした

- 文書（PR #77）: 仕様・設計（`docs/design/2g-4/`）・使い方（ボードの準備を install.md に）・CHANGELOG v1.2.0・性能評価を確定
- リリースのビルド（main f2c22aa、既定の戦略、ほかのビルドと重ねず）: **FDRI `f05e1f62…3b1c`・WNS / WHS +0.047165 / 0.000000 ns（判定した .bit と同じ）**、USR_ACCESS f2c22aa0（汚れなし）。合成で 1 回 segfault（回し直しで完走）、`impl_1` の中では落ちていない
- `tools/release_files.py`（`--bitfile proj031`）で組を作り、照合 通過。`.bit` sha256 `9820e959…0fff`
- 実機（配る .bit・.hwh と f2c22aa の `sw/pynq/`、ボードの `2g-4-v1.0.0`）: 係数 URAM 0.71 s で VERIFY、ID usr f2c22aa0・tcal board・lmx_pwr 3、STATUS time_ok 1・health 0・flags 0、4 窓 × 200 の短い取得で欠け 0・`g24cw` 全部通過。前に動いていた proj034 の amslog は実験者の了解で止めた
- タグ `2g-4/v1.0.0`・`v1.2.0`（注釈付き、f2c22aa）、GitHub Release「2G-4 v1.0.0」に 7 個と SHA256SUMS
- 気づいたこと: 手元の gh（2.4.0）は `gh release create --verify-tag` を持たない

## 持ち越しを閉じた記録（M0、2026-10-28）

### `check_g24.py ds`（proj030 からの持ち越し）

- 直し: IP の出口を「実のレーン 16 本」として読んでいたのを、「IP 8 個（z_q = y_q + j·y_(q+8)）。出口 Z を逆 FFT した z の実部がレーン q、虚部がレーン q＋8」に替えた（study-rfsoc の proj031 `sim/check_g24.py`）。0 でない出口の IP の番号が 8 未満であることも見る
- 直す前の sim の出力（proj031 rev 2 の 2026-10-27 22:16 の `build-sim/g24ds_*`）に当てた結果: **normal は全部通過**（インパルス 8 個とも 4 タップが模型と一致・境目 m 4095・0 を通った・D_S +1・D_eff 6,145 ビート。直す前は NG 3 件）、**陽性対照 posctl は D_S +0 で落ちるべきところだけ落ちた**
- 照合の直しそのものの陽性対照: 実部と虚部のレーンを入れ替えて読むと、8 個とも 4 タップが合わず落ちる（NG 5 件）
- **`make sim-g24ds` の回し直し（2026-10-28、study-rfsoc 575ae63 の木）: 「sim-g24ds: 全部通過（陽性対照は落ちた）」**。normal D_eff 6,145 ビート、posctl は D_S +0 だけで落ちた

### 2 時間の連続運転

study-rfsoc の proj036 R-4（2026-10-28 06:15〜08:15 UTC、予言は proj036 README）: **通過**
- 受け（7,200 s、制御 PC、`--out` なし）: 176.8 GB（24.6 MB/s）・SPEC 1,406,164・**CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過**
- STATUS（毎分 119 回）: miss・kgap・pl_drop・pl_crc・pl_err はどれも 0、AXI_MAX_PIPELINE は毎回 0x0102、loop_slow 1・1 周の最長 23.1 ms・loop_p99 11.2 ms・リングの山 3.3 MB
- VCCINT 32.6 A（32.3〜33.0）で平ら・PL 53.6〜60.0 ℃ で平ら・ボードは落ちなかった。**電流は予言（31.3 ± 0.5 A）の上に外れた**（取得 200 ダンプで測った proj031 R の値に、2 時間の送り出しの分が乗った見込み。確かめていない）。V2-L の合格（≦ 34 A）には入る
- STOP の前の STATUS の drop 903 は、受けが先に切れた後に specd の溜まりが満ちた分（台本の順）。受けが ACK した最後の seq までは全部届いた。V2-L の手順は「STOP を受けの終わりの前に打つ」か、drop を受けの終わりの前の STATUS で読む
