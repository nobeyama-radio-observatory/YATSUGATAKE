# study-rfsoc からの移植計画（2G-4）

- 状態: **M1 済み**（2026-10-28。表の行き先に置き、パスだけを直した。下の「M1 の結果」）。Makefile から試行の目標を外した（ブランチ `2g-4/makefile-trim`）。次は M2
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
- **動かして確かめたこと**（作業用の PC。Vivado は使っていない）: `make model-g24`・`model`・`model-cu` が全部通過、**COEF_CRC 0x891BE197**。`make gen`・`tools/gen_crc32.py` の出力が `src/g24/` の hex 4 個・`crc32_d32.vh` とバイト単位で同じ。`make sim-all`（g24c・g24t・g24p・g24ch）と `sim-recfr`（写しの `rec_fr.v`）が「全部通過」、陽性対照 8 本は落ちた（≒ 3 分）。Tcl 5 個が `info complete` で完結、`sw/pynq-2g/` の .py 46 個が `py_compile` を通る
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
| M2 | sim を全部回す: model-g24・model・model-cu、sim-g24c・g24t・g24p・g24ch・lane・g24a・g24s・recfr・g24core・g24s45・g24x4（cuclr・cuclrno を含む）・**g24ds**・sep・all2・cu | proj031-m0 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ |
| M3 | ビルド（`-1`、**既定の戦略**） | **FDRI が移植元と同じ**（`f05e1f62…3b1c`）。WNS / WHS が移植元と小数 6 桁まで同じ |
| M4 | 実機の短い回帰（ボードの新しいディレクトリ、study-rfsoc の道具のディレクトリと混ぜない） | ID・係数 URAM の VERIFY（CRC 0x891be197・0.7 s 台）・4 窓 × 200 の照合と `g24cw`・4 コアの bit 単位の同等（50 / 50 組 × 3）・tint 20.48 ms で 300 s 取りこぼし 0 が proj031 / proj036 と同じ値 |
| M5 | Fine の M5a・M5b を 2G-4 に当て、`sw/pynq-2g/` を `sw/pynq/` に一本化 | 下の「M5」 |
| M6 | 2G-4 の判定（`test/acceptance/2g-4/`）を全部通し、性能評価を書く | `docs/performance/2g-4/<版>.md` |
| M7 | spec・design・user の 2G-4 の分を書き、リリース | `release.md`。ボードの準備（AXI_MAX_PIPELINE 0x0102・s45fast.c のビルド）を手順に入れる |

### M3 の心配（M3 の前に書いた）

移植元の WHS は **+0.000 ns** で、WNS +0.047 ns も薄い（proj031 の結論）。Fine・Wide の M3 は「ディレクトリだけ違う」作り直しで構成データまで同じになったので、2G-4 も同じになる見込みが高い。
**負に落ちたら RTL も制約も直さずに止め、どうするかを決め直す**（直すと移植ではなくなる）。PE（WNS +0.007・WHS +0.010）に替えるのも M3 の中では行わない（比べの相手が変わる）。
`make build` は bit に焼く COEF_CRC を `make model-cu` の出力から読む（numpy の版で浮動小数の丸めが変わると CRC が変わりうる）。M3 の前に `runs/model_cu.txt` の COEF_CRC が 0x891BE197 であることを確かめる

### M5（Wide の M5 と違うところ）

- **PS の一本化を 2G の 3 本ぶん一度に**: 2G の PS は proj023 の頃に枝分かれした系統（G21・G22・G24 の Backend と s45fast.c）。`sw/pynq/` は Wide の M5 の版（M5a の CAL の鍵・M5b の USR_ACCESS・shm の取り残しの直し・LMX の PWR 3 など）。2G-1-Fast・2G-2 の移植を待たずに、G21・G22 の Backend も入れる（後で 2 回マージし直さないため）。2G-1・2G-2 の判定はそれぞれの移植で
- **LMX の出力の強さ**: proj036 の specd の既定は PWR 31（R-4 の ID で `lmx_pwr=31`）。`sw/pynq/` の既定 PWR 3 に合わせ、2G-4 の F-2 と TP の線形性を PWR 3 で測り直す（Wide の「M5 の後」と同じ）
- **予算を越える tint を SET で断る照合を specd に入れる**（interface 4.5 の約束。今の specd には無い）: 2G-4 は 20.48 ms 未満を断る。陽性対照: `SET tint=0.01024` が ERR
- **リング 64 MiB**（interface 4.1・8. の 11）: 2G の bit の既定を `--ring-mib 64` にする（今は起動の引数）
- **s45fast.c**: ボードで `build_fast.sh` で libs45fast.so を作る。CRC が「命令」で作られたことを起動の記録に残す。リリースの組（`tools/release_files.py`）と user の手順に入れる
- 較正の鍵を (BIT_KIND, BIT_REV) = (3, 1) に。timebase の CAL に proj031 R-5 の値（上の表）。BIT_REV は 1 のまま
- Makefile・build.tcl に Fine の M5b のフック（USR_ACCESS を焼く・`bitinfo.py` で読み返す）。FDRI は M3 と同じになるはず

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
