# study-rfsoc からの移植計画（2G-2）

- 状態: **M0 済み**（2026-10-31、ブランチ `2g-2/m0-map`）。置き場所の表・`hw/common/` との違い・移植元の bit を数え、判定を `test/acceptance/2g-2/` に書き起こした。決めること 1〜4 は開発者が案どおりに決めた（2026-10-31、PR #88）。**M1 済み**（2026-10-31、ブランチ `2g-2/m1-place`。表の行き先に置き、パスと模型の名前だけを直した。下の「M1 の結果」）。Makefile から試行の目標を外した（ブランチ `2g-2/makefile-trim`）。**M2 済み**（2026-10-31、同じブランチ。sim の出力が移植元とバイト単位で同じ。下の「M2 の結果」）。**M3 済み**（2026-10-31、ブランチ `2g-2/m3-build`。既定の戦略の作り直しで FDRI・WNS / WHS まで移植元と同じ。下の「M3 の結果」）。**M4 済み**（2026-10-31、ブランチ `2g-2/m4`。ID・H-0・EQ-2・tint 40.96 ms で 300 s が proj034 R-1・R-1c・R-3 と同じ。specd は `--prefault --fast --fast-ring` で回すことにした。下の「M4 の結果」）。**M5 済み**（2026-11-01、ブランチ `2g-2/m5`。PROJ を照らさない（案 A）、ADC の道は共通、USR_ACCESS を焼いた bit で M2〜M4 の回し直しが予言どおり。下の「M5 の結果」）
- 移植元: **`study-rfsoc@proj034-m0`**（注釈つきタグ、commit c8b90cb、2026-10-30）。RTL・ビルド・sim・模型・PS が 1 つの proj にある（2G-1-Fast と同じ形）
  - proj034 は proj025-m0（2G-2 の最初の形）に proj030 の 2-for-1 を入れたもの。精度・機能は proj025 と同じで、DSP 1,848 → 1,256・LUT 37.1 → 26.9 %・BRAM 759.5 → 635.5・VCCINT（実測）25.1 → 18.8 A
  - 移植元を proj025-m0 から proj034-m0 に替えた（2026-10-30、開発者。proj034 README の「結論・次にやること」）。2G-1-Fast を proj033-m0 に替えたのと同じ
  - **既定の戦略で閉じた bit を引き継ぐ**（proj034 B-1: 既定 WNS +0.074 ns・PE +0.032 ns。2G-1-Fast は既定で閉じず PE だった）
- 土台にする決め方: 2G-1-Fast の [`migration-2g-1-fast.md`](migration-2g-1-fast.md)（= 2G-4 の [`migration-2g-4.md`](migration-2g-4.md) = SAM45-Fine の [`migration.md`](migration.md) の M0〜M7）と同じ段取り。違うところだけをここに書く
- 2G の移植の順（2026-10-28 に決めた）: 2G-4（v1.2.0）→ 2G-1-Fast（v1.3.0）→ **2G-2** → 2G-1-Fine。仕様は [ADR 0022](decisions/0022-2g-1-fast-and-fine.md)・[`spec/bits.md`](spec/bits.md)・[`spec/interface.md`](spec/interface.md) 2.4

## 原則（2G-1-Fast と違うところ）

1. 2G-4 の原則 1〜3 はそのまま（変更は一度に一つ・数えて確かめる・**study-rfsoc の proj034 は書き換えない**）
2. **M1〜M4 は SAM45-Fine・SAM45-Wide・2G-4・2G-1-Fast のファイルに触らない。** 同じ名前で中身が違うもの（`s2_*`・`tb_s2_*`・`check_s2.py`・`model/s2_model.py`）は 2G-2 の側に置く。`s2_sep`・`s2_q` の一本化は 2G-2 の M3 の後の別の PR（2G-1-Fast の決めること 1）
3. **PS は `sw/pynq/` のまま使う**（2G-1-Fast と同じ）。G22 の Backend（`--g22`、proj025 の版）は `sw/pynq/` に入っている。移植元の PS と違うのは 3 か所だけ（下の「PS」）で、M5 で入れる

## 始める条件

- [x] proj034 の判定（M-1・M-2・P-1〜P-4・S・E-1・B-1・R-1〜R-3・R-6）が通り、README に結論が書かれている（2026-10-30）。外れは S の s2_q の FF（少ない側）・R-1 の loop_max（proj025 も同じ、PS の側）・R-2c の絶対の電流（予言の下の端を 0.2〜0.9 A 割った。差は予言の内）。F-2（R-5）は ADR 0023 で回さず
- [x] 2G-2 の運用に使う bit を決めた → **proj034 の build/（既定の戦略）**（下の「移植元の bit」。B-1 で「両方閉じたら WNS の大きい方」と測る前に決めてあった）
- [x] **タグ** `proj034-m0`（c8b90cb）を push した（2026-10-30）
- [x] ボードの準備（AXI_MAX_PIPELINE 0x0102）は 2G-4 と同じボードに入っている（2G-4 の始める条件）
- [x] **判定を `test/acceptance/2g-2/` の書き方で書き起こした**（2026-10-31、M0 で）: 8 判定（ID-1・H-0・EQ-2・H-2・V2-b・V2-L・RING・NET）。EQ-2 は 2G-4 の EQ-4 の 2 コア版。V2-b の 20.48 ms・V2-L・RING・NET は study-rfsoc で回していない（M6 で初めて）
- [x] **2 時間の連続運転**・**tint 20.48 ms での 30 分** → **M6 の V2-L・V2-b で初めて回す**（決めること 2）。proj034 R-3・proj025 4c とも tint 40.96 ms・30 分まで

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj034 README「B-1」の**既定の戦略**のビルド（`build/`、2026-10-30 01:36）。sha256・FDRI は手元の `proj034/build/` で数えた（2026-10-31）。

| 項目 | 値 |
|---|---|
| bit の sha256 | `5cb996c5619bbe64f5bcd71f0436f5125fad3d5d1167a44fe4929259d07060c5`（34,437,476 B） |
| hwh の sha256 | `ea3f400f4c6c7bfea5a10c3f0925ff9408003a164806c91163b504f6a9542e9b` |
| FDRI（`sw/pynq/bitinfo.py`） | 8,608,824 語・sha256 `b9dec08c865b43de56a95efe74131e3c40c417061671a3f35447ed02ea2c313f` |
| 構成の流れ（欄 e）の sha256 | `4f011d9c1fed6f17b97b4402175502edf0b07b3cc586d8ca5adfb5cf989fd9df` |
| ID | BIT_KIND 10・BIT_REV 1・**PROJ 0x0034_0100**。IF_ID 0x020A_0101（コア 2 個）・0x020A_0102（time_core）。USR_ACCESS なし |
| 実装の戦略 | **既定**（`make build`、出力は `build/`）。同じ RTL の Performance_Explore（`build-PE/`、WNS +0.032296）は使わない |
| `-1` の WNS / WHS | **+0.074 ns / +0.010 ns**（README は +0.073585・+0.009528） |
| LUT / FF | 114,545（26.93 %）/ 199,476（23.45 %） |
| DSP / BRAM タイル / URAM | 1,256（29.40 %）/ 635.5 / 48 |
| `report_cdc` | CDC-3 Info 75・CDC-6 Warning 3・CDC-15 Warning 3,137 |
| Vivado | 2024.1 |
| F-2 | 回していない（ADR 0023）。proj034 は CAL[0x0034_0100] に proj025 4d の値を写した。YATSUGATAKE では CAL に入れない（下の「PS」） |

- ビルドは 18b4569（B-1 の予言）の後に始めた。その後タグまでの commit（f7b2034・c8b90cb など）が変えたのは README・`pynq/timebase.py`・`tools/amslog.py`・`tools/shapecmp22.py` だけで、RTL・`build.tcl`・`build_post.tcl`・`Makefile` は変わっていない（`git diff 18b4569 proj034-m0`）。FDRI が同じになるかは M3 で確かめる
- bit そのものは git に入れない（ADR 0018）

## 置き場所の対応（M0、2026-10-31）

ファイル 1 つずつの行き先は付録 [`migration-2g-2-files.md`](migration-2g-2-files.md)（148 個: 置く 45・2G-2 の側に写し 1・既にある 81・移さない 21）。

| study-rfsoc（proj034-m0） | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| `src/g22/`（13 個）・`src/s2_*.v`（3 個） | `hw/bits/2g-2/src/` | 2G-2 の部品・係数とひねり係数の hex。`s2_*` は 2G-4・2G-1-Fast の同名と違う版（下） |
| `src/common/rec_fr.v` | `hw/bits/2g-2/src/` に**写し** | `hw/bits/2g-1-fast/src/rec_fr.v`・`hw/bits/2g-4/src/rec_fr.v` と同じ中身（下の「`hw/common/` との違い」） |
| `src/common/` の残り 34 個・`src/board/` 3 個 | **既にある** `hw/common/`・`hw/board/` | バイト単位で同じ |
| `Makefile`・`build.tcl`・`build_post.tcl` | `hw/bits/2g-2/` | パスだけを直す（下の「M1 で直すパス」）。`build_post.tcl` は 2G-4 にはあり、2G-1-Fast には無い |
| `sim/`（18 個） | `hw/bits/2g-2/sim/` | 試験台・照合・IP の模型（lane_fft_g22_model）。`rec_fr_ref.v`・`tb_recfr_eq.v` は 2G-4・2G-1-Fast の同名と同じ中身、`tb_s2_*`・`check_s2.py` は違う版 |
| `model/g22_fixed.py`・`model/g22_model.py` | `model/` | 名前は今の `model/` と重ならない |
| `model/s2_model.py` | **`model/s2_model_g22.py`**（名前を替える） | 2G-4 の `model/s2_model.py`・2G-1-Fast の `model/s2_model_g21.py` と中身が違う（下の「模型の名前」） |
| `model/g2_model.py` | **既にある** `model/g2_model.py` | バイト単位で同じ |
| `tools/` のうちビルド・sim が使う 4 個 | `hw/bits/2g-2/tools/` | gen_g22_tables・ip_impl・ip_survey・ooc_rtl（後の 3 個は 2G-1-Fast と同じ中身） |
| `pynq/g22cw.py` | `sw/pynq/` | 2G-2 の判定の道具（2G-4 の移植で「2G-2 の道具はそれぞれの移植で」とした） |
| `pynq/` の残り 42 個・`tools/amslog.py` | **既にある** `sw/pynq/` | 同じ 21・違う 21（2G-4 の M5 で一本化した版を使う） |
| `pynq/` の 18 個・`tools/` の 2 個・README | 移さない | Fine・窓・試行の道具、bench_g21、`tp_cal.json`（ボードに置く、ADR 0025）、power_rpt・shapecmp22 |

### `hw/common/` との違い（2026-10-31）

proj034 の `src/common/` 35 個と `src/board/` 3 個を、YATSUGATAKE の main（73a6740、2G-1-Fast の M7 の後）の `hw/common/`・`hw/board/` と比べた: **37 個がバイト単位で同じ、違うのは `rec_fr.v` の 1 個**（2G-1-Fast と同じ）。

| ファイル | 違い | 2G-2 の使い方 |
|---|---|---|
| `rec_fr.v` | `hw/common/` の版は、2G-4 の一本化のときに `n_cap == np - 1` の 2 か所を `np - 1'b1` に直した（PR #74）。proj034 の版は直す前のもので、**`hw/bits/2g-1-fast/src/rec_fr.v`・`hw/bits/2g-4/src/rec_fr.v` とバイト単位で同じ** | `NCH(65536)`（g22_core）。**proj034 の版の写しを `hw/bits/2g-2/src/` に置く**（2G-1-Fast と同じ扱い。`hw/common/` の版で作ると FDRI が移植元と変わるおそれがあり、M3 の比べができない） |

- 2G-2 の build.tcl が `src/common/` から読むのは 13 個（core_cmn・raw_core・cmul・dft16f・tp_core・rec_fr・rec_arb・adc_ev・time_core・s45_ring・gb_adc・gb_gate・axis_sel4。2G-1-Fast と同じ組）。sim は ほかに `dft16.v`（sim-g22ch・ooc-ref の proj025 の鎖）を読む
- `rec_fr.v` の写し 3 個（2G-4・2G-1-Fast・2G-2）を `hw/common/` の版に寄せるのは、別の PR で（3 本とも FDRI が変わるかを作り直して数える）

### s2_* の扱い（2G-1-Fast の決めること 1 のとおり）

2G-1-Fast の M0 で 3 本の版を比べ、「M1 では bit ごとに置き、**2G-2 の移植（M3 まで）の後に `s2_sep`・`s2_q` を 1 本にして `hw/common/` に上げる**。`s2_chain` は bit ごとに置いたまま」と決めてある。2G-2 は M1 で 3 個とも `hw/bits/2g-2/src/` に移植元のまま置く。

- 今の main で数え直した違い（diff の行）: `s2_sep.v` は 2G-1-Fast と 14・2G-4 と 26、`s2_q.v` は 15・35、`s2_chain.v` は 52・64。2G-1-Fast との数は 2G-1-Fast の M0 の表（「2G-1-Fast と 2G-2 の違い」）と同じ
- proj034 の `s2_q` は行の幅を parameter `KB` に出した形（proj033 と同じ）。1 本にするときはこの形を `hw/common/` の版にし、2G-4 は AB 9・KB 12 を渡す（2G-1-Fast の M0 の表）

### 模型の名前（決めること 1、2026-10-31 に案どおり決めた）

proj034 の `model/s2_model.py` は 2G-2 の寸法（ADC 1 本あたり N 131072・M 8192）の版で、2G-4 の `model/s2_model.py`（312 行違う）とも、2G-1-Fast の `model/s2_model_g21.py`（51 行違う）とも中身が違う。

**決め**: 2G-1-Fast の決めること 2 と同じく、**`model/s2_model_g22.py`** に置き、読む側の `import s2_model` を `import s2_model_g22` に直す（`sim/check_s2.py`・`sim/check_g22.py` の 2 行と、Makefile の `model` の 1 行。docstring の名前は M1 で数える）。M1 の照合ではこれを「名前の直し」として別に数える

### M1 で直すパス（予定）

2G-1-Fast の M1 と同じ型。中身は変えない:
- `Makefile`・`build.tcl`・`build_post.tcl`: `src/common/` → `../../common/`（**写しの `rec_fr.v` は `src/`**）、`src/board/` → `../../board/`、`model/` → `../../../model/`（`s2_model.py` は `s2_model_g22.py`）。`src/g22/`・`src/s2_*.v` は `hw/bits/2g-2/src/` の下に同じ形で置くので直さない
- `sim/check_s2.py`・`sim/check_g22.py`・`tools/gen_g22_tables.py` の模型の道（`"..", "model"` → `"..", "..", "..", "..", "model"` などの形）と、上の import の 2 行
- `model/s2_model_g22.py`・`model/g22_fixed.py`・`model/g22_model.py` は直さない（同じディレクトリの `g2_model`・`g22_fixed` を読む）
- `runs/` は git に入れない（`.gitignore` に `/hw/bits/2g-2/runs/`）
- **在ってはいけない側の照合**: 2G-2 の Makefile・build.tcl・sim・tools が `hw/common/rec_fr.v` と、`hw/bits/2g-4/`・`hw/bits/2g-1-fast/` の下のファイルを指していないこと（指していると、別の寸法の `s2_*` か 1'b1 の版の rec_fr で作られる）。`import s2_model as`（2G-4 の版）・`s2_model_g21` を読む行が無いこと

### M1 の結果（2026-10-31、ブランチ `2g-2/m1-place`）

- **置く**（fc39902）: 付録の 46 個（置く 45・写し 1）を `git show study-rfsoc@proj034-m0:…` から取り出して置いた。46 個とも移植元と blob が同じ（`model/s2_model.py` は `model/s2_model_g22.py` に、`src/common/rec_fr.v` は `src/rec_fr.v` に）
- **パスの直し**: 6 個・43 行（Makefile 13・build.tcl 20・build_post.tcl 4・Python 6）。**違う行はすべてパスの行か模型の名前の行**: 新しい行のパスと名前を元に戻すと 43 行とも古い行と一致（機械で照合。陽性対照: 行に 1 字足すと不一致になる）。名前の行は 4 行（`import s2_model_g22` 2・`check_s2.py` の docstring 1・Makefile の `model` 1）。`src/g22/`・`src/s2_*.v` は直していない。`model/` の 3 個と `sw/pynq/g22cw.py` は移植元のまま
- **在ってはいけない側**: 2G-2 の Makefile・build.tcl・build_post.tcl・sim・tools が `hw/common/rec_fr.v`（`src/common/rec_fr`）・`hw/bits/2g-4/`・`hw/bits/2g-1-fast/`・`import s2_model as`・`s2_model_g21` を指す行は 0（直す前の版 fc39902 に当てると Makefile 2・check_s2.py 1 行を拾う = 照合が働いている）。build.tcl は `include` を使う RTL を読まない（include_dirs は要らない）
- **動かして確かめたこと**（この PC、Vivado は使っていない）: `make model-g22`（M-a〜M-d）・`model`（M-1a〜M-2b、鎖の入口 (i)）が全部通過。`make gen` の出力が `src/g22/` の hex 4 個とバイト単位で同じ（係数 524,288 タップ・ひねり係数 16 × 8192 の読み返しも一致）。`sim-recfr`（写しの `rec_fr.v`）・`sim-sep` が「全部通過」、陽性対照 4 本（recfr_posctl・sep_addr・sep_swap・sep_pos）は落ちた。Tcl 5 個が `info complete` で完結、Python 7 個（`sw/pynq/g22cw.py`・`model/` の 3 個・sim と tools の 3 個）が `py_compile` を通る
- **`runs/` は git に入れない**（`.gitignore` に `/hw/bits/2g-2/runs/`）。`hw/bits/2g-2/README.md` を足し、`hw/bits/README.md` の行を直した
- **動かないままにしたもの**: Makefile の `s2`・`survey`・`ooc-*` は Vivado で動くはずだが回していない。`sim-all` は 1a〜1d の 4 つだけ。直すのは下の 1

### M1 の後にすること（それぞれ別の PR）

1. **Makefile から試行の目標を外す**（2G-4・2G-1-Fast の makefile-trim と同じ型）: `s2`・`survey`・`ooc-ref`・`ooc-all` と、それだけが使う `JOBS`（proj034 の Makefile は `PYTHON`・`IVERILOG`・`VVP`・`JOBS` を 2 回定義している。重なりを外すのも中身を変えない直しとして数える）。部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`）は 2G-4・2G-1-Fast と同じく残す。
   `sim-all` は今は 1a〜1d の 4 つだけを回すので、2G-2 の sim の全部（下の M2 の表、模型 2 本と sim 14 本）に替える。`sim-g22s` は `x.hex` が在れば作り直さないようにする（2G-1-Fast と同じ 1 行。並べた `g22core`・`g22s45`・`g22x2` が書きかけの `x.hex` を読まないように）。外した後に M2
   - **済み（2026-10-31、ブランチ `2g-2/makefile-trim`、b9dc2d8）**: `s2`・`survey`・`ooc-ref`・`ooc-all` と、二重に定義していた `PYTHON`・`IVERILOG`・`VVP`・`JOBS`（`JOBS` はそれだけが使う）を外した。部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`）と `post` は残した。`tools/ip_impl.tcl`・`ip_survey.tcl` は 2G-4・2G-1-Fast と同じく置いたまま
   - `sim-all` は模型 2 本（`model-g22`・`model`、「まとめ」の行に「不合格」が無いこと）と sim 14 本（M2 の表の全部、最後の行「sim-…: 全部通過」）を回し、`build-sim-logs/` の 16 個で判定する。共有の入力 `g22s_in/x.hex` を先に作ってから、目標を `SIM_J`（既定 4）本ずつ並べる（2G-1-Fast の `sim-all` と同じ形）
   - **`sim-g22s` は `x.hex` が在れば作り直さないようにした**（1 行）。中身は同じ乱数の種で作るので出力は変わらない（下の M2 で確かめた）
   - `g22_chain.v`・`sim-g22ch` は残す（2G-4・2G-1-Fast と同じ。`g22_tw` と `dft16.v` の回帰を兼ねる）
2. `s2_sep`・`s2_q` の一本化 → **2G-2 の M3 の後**（上）。3 本の bit を作り直して FDRI がそれぞれのリリース（2G-2 は M3）と同じことを合格にする
3. `rec_fr.v` の写し 3 個を `hw/common/` に寄せる（上。2 と一緒でもよい）

### M2 の結果（2026-10-31、ブランチ `2g-2/makefile-trim`）

この PC（Icarus Verilog 11.0・Python 3.10.12・numpy 1.21.5）で、移植先（`hw/bits/2g-2/`、b9dc2d8）の `make sim-all` と、**タグ `proj034-m0` の proj034 を `git archive` で取り出して同じ 16 個を回したもの**を比べた（同じ PC・同じ版の道具で、同じ時間に並べて回した。移植先 26 分・移植元 38 分。別の作業の Vivado のビルドと重なった）:

- **16 個とも「全部通過」**（模型 2 本は「まとめ」の行が全部通過、sim 14 本は最後の行が全部通過）。陽性対照は 20 本がすべて落ちるべきところで落ちた（g22ds・g22x2 の陽性対照は判定の文のとおりのところだけで落ちる）。両側で同じ
- 移植元の `sim-g22s` は `x.hex` を毎回作り直すので、移植元の側だけ `sim-g22s` を先に 1 本で回し、残りの 13 本を 4 本ずつ並べた（Makefile には触っていない）
- **`build-sim/` の出力 237 個のうち 198 個がバイト単位で同じ**（各変種の `tb.log`・`check.log`・入力の hex を含む）。違う 39 個は iverilog のコンパイル物 `tb` だけで、**パス（`src/common/` ↔ `../../common/`・写しの `rec_fr.v` は `src/`）と、コンパイルごとに変わる番地（`0x…`）を読み替えると 39 個とも同じ**（陽性対照: 1 字足すと不一致になる）
- **`build-sim-logs/` の 16 個のうち 14 個がバイト単位で同じ**。違う 2 個は模型のログで、違うのは make が出すコマンドの行（`model/` ↔ `../../../model/`、`s2_model.py` ↔ `s2_model_g22.py`）と経過秒だけ

## 手順

| 手順 | 2G-2 ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録）・始める条件・`hw/common/` との違いの数え・判定の書き起こし | 全ファイルに行き先がある・始める条件が全部 [x] |
| M1 | 表の行き先に置き、パスと模型の名前だけを直す | `git diff --stat` で中身の変更がパスの行と名前の行だけ。在ってはいけない側の照合（上）（**2026-10-31**: 上の「M1 の結果」） |
| M2 | sim を全部回す: model-g22・model、sim-g22c・g22t・g22p・g22ch・lane・g22a・g22s・recfr・g22core・g22s45・g22x2・g22ds・sep・all2 | proj034-m0 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**2026-10-31**: 下の「M2 の結果」） |
| M3 | ビルド（`-1`、**既定の戦略**） | **FDRI が移植元と同じ**（`b9dec08c…313f`）。WNS / WHS が移植元と小数 6 桁まで同じ（+0.073585 / +0.009528）（**2026-10-31**: 下の「M3 の結果」） |
| M4 | 実機の短い回帰（ボードの新しいディレクトリ、`sw/pynq/` で `specd --g22`） | ID・H-0・EQ-2・tint 40.96 ms で 300 s 取りこぼし 0 が proj034 R-1・R-1c・R-3 と同じ値。`--fast` の有無を両方回して決める（下の「M4 の予定」）（**2026-10-31**: 下の「M4 の結果」） |
| M5 | 下の「PS」の 3 つと、Fine の M5b（USR_ACCESS）を 2G-2 に当てる | M2〜M4 の回し直しが予言どおり（USR_ACCESS は FDRI の外なので FDRI は変わらず、構成の流れが変わる）（**2026-11-01**: 下の「M5 の結果」） |
| M6 | 2G-2 の判定（`test/acceptance/2g-2/`）を全部通し、性能評価を書く | `docs/performance/2g-2/<版>.md` |
| M7 | spec・design・user の 2G-2 の分を書き、リリース | `release.md` |

### M3 の心配（M3 の前に書く）

- 2G-4 の M3（既定）・2G-1-Fast の M3（PE）とも、ディレクトリだけ違う作り直しで構成データまで同じだった。2G-2 も同じになる見込みが高い
- WNS +0.074 ns は 2G-4（+0.047）・2G-1-Fast（+0.025）より余裕があるが、配置の揺れの幅（±0.1 ns 級、proj034 E-0）の中。**負に落ちたら RTL も制約も直さずに止め、決め直す**。PE（+0.032）に替えるのも M3 の中では行わない（比べの相手が変わる）
- proj034 の B-1 では PE のビルドで Vivado が OOC の合成で 4 回落ちた（回し直しで完走）。既定のビルドでは落ちていない。落ちたら build.tcl の回し直しに任せ、記録する
- `.hwh` は係数とひねり係数の hex の絶対パスと TIMESTAMP が違うはず（2G-1-Fast の M3 と同じ）

### M3 の結果（2026-10-31）

この PC で、移植先（`hw/bits/2g-2/`、main df5b78a の木 = M2 と同じ RTL・build.tcl）の `make build BUILD_JOBS=4`（`-1`・既定の戦略）を回した（67 分。別の作業の Vivado のビルドと重ねた。開発者の指示で BUILD_JOBS 4）。予言（上の「M3 の心配」）どおり、**ディレクトリだけ違う作り直しで構成データまで同じ**:

| | 移植元（proj034-m0 の `build/`） | 移植先（`build/`） |
|---|---|---|
| FDRI | 8,608,824 語 / `b9dec08c865b43de56a95efe74131e3c40c417061671a3f35447ed02ea2c313f` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `4f011d9c1fed6f17b97b4402175502edf0b07b3cc586d8ca5adfb5cf989fd9df` | **同じ**（.bit のファイルはヘッダの日付だけ違う） |
| TIMING（確定） | WNS 0.073585 ns / WHS 0.009528 ns | **同じ** |
| 資源・CDC | LUT 114,545・FF 199,476・DSP 1,256・BRAM 635.5・URAM 48、CDC-3 75・CDC-6 3・CDC-15 3,137 | 報告 16 個のうち 15 個が見出しの行（日付など）を除いて同じ |
| ERROR・CRITICAL WARNING | ERROR 2 行（`lane_fft_g22` の `output_width` を読む既知の 2 行、ビルドは続く）・CRITICAL WARNING 1 行（見張りの陽性対照の目印） | 同じ |

- **`.hwh`** は sha256 が違う（`dc023c9e…6ef8`）。違うのは TIMESTAMP と、係数とひねり係数の hex の絶対パス（`…/rfsoc/proj034/src/g22/` ↔ `…/YATSUGATAKE/hw/bits/2g-2/src/g22/`）だけ（2G-1-Fast の M3 と同じ）
- **`drc.rpt`** は、RTSTAT-10（ロードの無いネット 40 本）の網の一覧の並びが 4 本入れ替わっただけ。本数と残りの行は同じ。並びはツールの出し方で、構成データには効かない（FDRI が同じ。2G-1-Fast の M3 と同じ型）
- Vivado は落ちなかった（重ねたビルドでも OOC の合成の回し直しは無し）
- `bitinfo.py`（`sw/pynq/`）で読んだ。USR_ACCESS は焼いていない（M5 で入れる）。.bit は git に入れない（ADR 0018）

### M4 の予定

- 起こし方: `specd.py --g22 --bitfile proj034.bit --clkin 0 --ref 10`（root の ssh なら `/etc/profile.d/` を読んでから。2G-1-Fast の M4 で `KeyError: 'BOARD'` を踏んだ）。配線は N（ノイズ ON・ATT 13 dB）。**載せる前に `ATT?` を読み、別の作業の specd が動いていないかを見る**（ボードと器を分け合っている）
- 1 回の Overlay の中で ID-1 → H-0（`A0.src=A B0.src=B`）→ EQ-2（C・C fmt=both × 50）→ tint 40.96 ms で 300 s → tint 20.48 ms で 300 s。specd を `--fast` なし（移植元の R と同じ形）と `--prefault --fast --fast-ring`（2G-4・2G-1-Fast の形）の 2 回起こす
- **`--fast` が要る見込み**: proj034 R-3（tint 40.96 ms・src C・D・TP 4 本）は loop_max 29.7 ms・p99 28.7 ms（1 周で 2 ダンプを抱える形）で、20.48 ms では `--fast` なしは間に合わないおそれがある。2G-4（流れ 4 本）・2G-1-Fast（1 本）は `--fast` ありで 1 周の最長 7 ms 以下だった
- 比べる値: proj034 R-1・R-2'（床の中央値 A0 3,196〜3,220・B0 3,175〜3,194 @ TP A −31.39〜−31.42・B −31.34〜−31.37 dBFS）、R-1c（50 / 50 組）、R-3（取りこぼし 0・pl_peak 4.6 MB）

### M4 の結果（2026-10-31）

M3 で作った bit（FDRI `b9dec08c…313f`、`.bit` sha256 `34f48b30…20e8a`）と `sw/pynq/`（ボードの写しが手元と sha256 で全部同じ）を、ボードの新しいディレクトリ（`~/2g-2-m4`）に置いた。`build_fast.sh` は「CRC: 命令」。
載せる前に、別の作業の specd が動いていないこと（/dev/shm 0 %）と機器を読んだ: ATT 13 dB・ノイズソース ON（15.00 V・512 mA）・SG 出力 OFF（配線 N）。機器には触っていない。
specd を root の ssh で `--g22 --bitfile proj034.bit --clkin 0 --ref 10` で起こし（`/etc/profile.d/` を読んでから）、受けは制御 PC。**specd を 2 回起こし**、1 回目は `--fast` なし（移植元の R と同じ形）、2 回目は `--prefault --fast --fast-ring --loop-log-ms 0.1`（2G-4・2G-1-Fast の形）。それぞれの 1 回の Overlay の中で ID-1 → H-0 → EQ-2 → tint 40.96 ms で 300 s → tint 20.48 ms で 300 s の順に回した（300 s は proj034 R-3 と同じ重い形: src C・D・TP 4 本）:

| | 移植先（M4、`--fast` なし） | 移植先（M4、`--fast` あり） | 移植元の記録（proj034、`--fast` なし） |
|---|---|---|---|
| ID-1 | adc 020a0101・time 020a0102・proj 00340100・kind g22・usr none・lmx_pwr 3・**tcal board**、IDLE・time_ok 1・health 0・flags 0 | 同じ | R-1: 同じ ID（tcal は「未較正」） |
| H-0（A0 A・B0 B × 200） | SPEC 400・CRC 0・説明のない欠け 0・照合 通過・`g22cw` 全部通過（nch 65536・nacc 1280・DUMP_T の進み 10,485,760・2 窓の DUMP_T が揃う）・flags 0・sat 0、陽性対照（`--src CD`）で NG。TP A −31.47・B −31.44 dBFS、床 A0 3.18e3・B0 3.15e3、loop_max 21.0 ms | 同じ（TP −31.49・−31.48、床 3.16e3・3.12e3）、loop_max 12.3 ms・p99 7.6 ms | R-1・R-2': 同じ。TP A −31.39〜−31.42・B −31.34〜−31.37、床 A0 3,196〜3,220・B0 3,175〜3,194、loop_max 20.8〜22.3 ms |
| EQ-2（C・C fmt=both × 50） | **50 / 50 組**・照合 通過、陽性対照 0 / 49 組（違う ch 65,528〜65,536）。miss・drop 0、**loop_max 106.4 ms・loop_slow 26** | 50 / 50 組、陽性対照 0 / 49 組。**loop_max 16.7 ms・loop_slow 0** | R-1c: 50 / 50 組・陽性対照 0 / 49 組。fmt both の loop_max 72.4 ms・loop_slow 28 |
| tint 40.96 ms で 300 s | SPEC 14,625・3.69 GB・CRC・欠け・kgap・tdev 0・照合 通過、miss・drop・pl_drop・pl_crc・pl_err・loop_slow・tp_rec_lost 0、**loop_max 30.0 ms**・p99 26.1 ms・pl_peak 13.6 MB | SPEC 14,626・同じ取りこぼし 0、**loop_max 22.2 ms・p99 7.5 ms**・pl_peak 3.2 MB | R-3（30 分）: 取りこぼし 0・loop_max 29.7 ms・p99 28.7 → 22.0 ms・pl_peak 4.6 MB |
| tint 20.48 ms で 300 s | SPEC 29,255・7.35 GB・取りこぼし 0・照合 通過、**loop_max 68.7 ms・p99 57.4 ms・loop_slow 5,453**・pl_peak 13.6 MB | SPEC 29,261・7.36 GB・取りこぼし 0・照合 通過、**loop_max 22.1 ms・p99 7.5 ms・loop_slow 1**・pl_peak 3.2 MB。**1 周の計 11.71 ms**（`loopsum.py --nwin 2`、1 BASE あたり。周のログの上限 300 周の分） | 回していない |

- AXI_MAX_PIPELINE は起こす前（2 回とも）と後で 0x0102。終わりの機器は前と同じ（ATT 13 dB を読み返した）
- 床は R-2' より −0.1〜−0.2 dB、TP は −0.05〜−0.1 dB（H-0 の線: TP が ±0.5 dB の内なので床は ±0.7 dB の内で合格）
- **`--fast` を使うと決めた**（判定の README の持ち越し）: 20.48 ms で `--fast` なしは 1 周の p99 が 57.4 ms（20.48 ms の 2.8 倍）・loop_slow 5,453 で、V2-b の線（1 周の計 ≦ 16 ms・loop_slow ≦ 5）に入らない（リングが吸って取りこぼしは 0）。`--fast` ありは 1 周の計 11.71 ms・p99 7.5 ms。2G-4・2G-1-Fast と同じ形（`--prefault --fast --fast-ring`）で M5 以降と判定を回す
- **fmt both の重さ（proj034 からの持ち越し）は `--fast` で消えた**（loop_max 106 → 16.7 ms・loop_slow 26 → 0）。`--fast` なしの 106 ms は proj034 の 72〜76 ms より重いが、運転は `--fast` ありなので追わない
- `--fast` なしの pl_peak 13.6 MB は R-3 の 4.6 MB より大きい（同じ形の 40.96 ms で）。1 周が遅い間にリングに溜まった分で、64 MiB に対して余裕がある。`--fast` ありは 3.2 MB
- 記録: 制御 PC の作業用のディレクトリ（`id1a/b.txt`・`h0a/b*`・`eq2a/b*`・`l40a/b*`・`l20a/b*` の .json・.status.txt）、ボードの `~/2g-2-m4/runs/`（specd のログ 2 本・`axi_*.txt`）。`.s45` は照合が済んだ 300 s の分を消した

### PS（M5、2G-1-Fast の M5 と違うところ）

`sw/pynq/` には 2G-4 の M5 で G22 の Backend（`--g22`、proj025 の版）が入っている。proj034 の PS は proj025 の PS から 3 か所だけ変えたもの（`git diff proj025-m0:proj025/pynq proj034-m0:proj034/pynq`、3 ファイル 9 行）。2G-1-Fast の 3 か所と同じ形:

1. **`s45core.PROJ_G22`** を 0x0025_0100 → 0x0034_0100。G22Backend は `discover(bit_kind=10, ncore=2)` で開くので、proj025 の bit（同じ (10, 1)）も通る。PROJ は照らさない（決めること 3、案 A）。M5 で `PROJ_G22` を直し、「追跡のため。照合には使わない」と注釈する
2. **timebase**: proj034 は `CAL[0x0034_0100]` に proj025 4d の値を写した。YATSUGATAKE は ADR 0023 でボードの較正ファイルを使うので、**CAL には足さない**。ADC → コアの道は共通の道と見込む: 道の RTL（gb_adc・gb_gate・raw_core・adc_ev・time_core・axis_sel4）は `hw/common/` の同じファイル、**proj034 の build/ の `rfdc_params.rpt` が SAM45-Fine・SAM45-Wide・2G-4・2G-1-Fast のビルドの同じ報告と 1 行も違わない**（2026-10-31 に数えた）。M5 で `ADC_PATH` の注釈に足す
3. widef2 の `--bitfile` の既定（proj025.bit → proj034.bit）。`sw/pynq/` では bits.json の項目（`"kind": "g22"`）で指すので、既定は直さない

ほかに 2G-4 の M5 で入れたもの（予算の照合 `check_net`・リング 64 MiB・LMX の PWR 3・ボードの印・2G の pump の止まりの仕掛け）は G22 にも効いている。2G-2 で確かめるのは M4〜M6 の回帰で。`bits.example.json` に `"2g-2"`（`"kind": "g22"`）を足す

### M5 でしたこと（2026-10-31、ブランチ `2g-2/m5`）

- **決めること 3（案 A）のとおり PROJ は照合しない**。`s45core.PROJ_G22` を 0x0034_0100 に直し、「追跡のため。照合には使わない」と注釈した。G22Backend は今までどおり (BIT_KIND 10, BIT_REV 1) で開く
- **ADC → コアの道は共通の道**（`timebase.ADC_PATH` に (10, 1) を足さない。注釈だけ足した）: 道の RTL は `hw/common/` の同じファイル、RFDC のセルの組み立てと fs・spw_adc 12 → spw 16 が Wide と同じ、ビルドの `rfdc_params.rpt` がほかの 4 本のビルドと 1 行も違わない（M0 で数えた。M3 の作り直しでも同じ）。M4 の `tcal=board` はこれで正しい
- **USR_ACCESS のフック**（M5b、Fine・Wide・2G-4・2G-1-Fast と同じ）: Makefile に 12 行・build.tcl に 22 行（2G-1-Fast の行をそのまま）。RTL・制約は変えない
- `bits.example.json` に `"2g-2"`（`"kind": "g22"`）。PC で `test_fake.sh all`・`test_timecal`・`test_tpcal`・`test_nch` が全部通過

### M5 の予言（作り直しと回し直しの前に書いた、2026-10-31）

1. **M2 の回し直し**: `make sim-all` が 16 個とも通過。`build-sim/` は M2 の出力と、iverilog の `tb` の番地（`0x…`）を除いてバイト単位で同じ（RTL も sim も変えていない）
2. **M3 の焼き直し**（`make build BUILD_JOBS=4`、この commit の木）: USR_ACCESS が commit（汚れ 0）。**FDRI は M3 と同じ**（`b9dec08c…313f`。USR_ACCESS は FDRI の外）、構成の流れの sha256 は変わる。WNS / WHS は M3 と小数 6 桁まで同じ（0.073585 / 0.009528）。報告は drc.rpt の並びの入れ替わりのほかは同じ。外れて WNS が負になったら、作り直しはやめて決め直す（「M3 の心配」）
3. **M4 の回し直し**（ボードの新しいディレクトリ `~/2g-2-m5`、specd は `--bits bits.json --clkin 0 --ref 10 --prefault --fast --fast-ring --loop-log-ms 0.1`、`--g22` なし）: ID の `usr` が commit・`tcal=board`、H-0 通過（床は M4 と ±0.1 dB）、EQ-2 50 / 50 組、NET（10.24 ms は ERR・20.48 ms は OK、陽性対照 `--net-budget-mbs 0` で 10.24 ms が OK）、tint 20.48 ms で 300 s 取りこぼし 0・1 周の計 ≦ 16 ms（`loopsum.py`）。ID-1 の陽性対照: ボードの proj025 の bit で起こすと ID の proj が 00250100（案 A なので START は通る）

### M5 の結果（2026-11-01）: 予言 1〜3 とも当たり

**予言 1（M2 の回し直し、b0dc6ea の木）: 当たり**。`make sim-all` が 16 個とも「全部通過」（26 分、ビルドと並べて回した）。`build-sim/` の 237 個のうち 198 個が M2 の出力とバイト単位で同じ、違う 39 個は iverilog の `tb` だけで、番地（`0x…`）を読み替えると 39 個とも同じ

**予言 2（M3 の焼き直し、b0dc6ea、`make build BUILD_JOBS=4`、`-1`・既定、66 分）: 当たり**

| | M3（移植元と同じ） | M5b |
|---|---|---|
| USR_ACCESS（bitinfo） | なし | **b0dc6ea0 = commit b0dc6ea（汚れなし）**（書き込み 1 回）。make の読み返しの照合 通過、vivado.log にも `USR_ACCESS: 0xb0dc6ea0` |
| **FDRI** | 8,608,824 語 / `b9dec08c865b43de56a95efe74131e3c40c417061671a3f35447ed02ea2c313f` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `4f011d9c…d9df` | `9e7ee7be08555d1f5ec1dd5506ffac8d1531d3a74369a50390397100d7ad7790`（USR_ACCESS の書き込みの分） |
| TIMING（確定） | WNS 0.073585 / WHS 0.009528 ns | **同じ（小数 6 桁まで）** |
| 報告 16 個（見出しの行を除く） | | 15 個が同じ。drc.rpt は RTSTAT-10 の網の一覧の並びの入れ替わりだけ（M3 と同じ型、40 本は同じ） |
| ERROR・CRITICAL WARNING | ERROR 2 行（`output_width`）・CW 1 行（見張りの陽性対照の目印） | 同じ |
| `.bit` / `.hwh` の sha256 | `34f48b30…20e8a` / `dc023c9e…6ef8` | `eb2314022658f92c22d4ad264206394d497da5bebe9044c3e51b82627c90b7bb` / `9e105352cc860daab575bad234a176e9176630dda423ca3dc89ced5845673894` |

**予言 3（M4 の回し直し）: 当たり**。ボードの `~/2g-2-m5`（今回の bit・hwh、`sw/pynq/` の 64 個、bits.json は `"2g-2"` の 1 項目・`"kind": "g22"`・sha256 付き。手元と sha256 で全部同じ、`build_fast.sh` で「CRC: 命令」）。載せる前に別の作業の specd が無いことと機器（ATT 13 dB・ノイズ ON・SG OFF、配線 N）を読んだ。specd は **`--bits bits.json --clkin 0 --ref 10 --prefault --fast --fast-ring --loop-log-ms 0.1`**（`--g22` なし）。1 回の Overlay の中で ID-1 → H-0 → EQ-2 → NET → tint 20.48 ms で 300 s、そのあと陽性対照 2 つを起こし直して回した:

| | M5（今回） | M4（`--fast` あり） |
|---|---|---|
| 起動のログ | LMX の出力の強さ OUTA 31 → 3・OUTB 31 → 3、リング SIZE 67108864（64 MiB）、「SPEC の記録（FULL）は C（s45fast、CRC 命令）」、bit `2g-2` | 同じ（bit は default） |
| ID-1 | adc 020a0101・time 020a0102・proj 00340100・kind g22・**usr b0dc6ea0**・lmx_pwr 3・tcal board、IDLE・time_ok 1・health 0・flags 0 | 同じ（usr none） |
| ID-1 の陽性対照 | ボードの `~/proj025/proj025.bit`（`de3ee453…`）で起こすと ID の **proj 00250100**・usr none。案 A なので START は通り、20 本の取得も照合 通過 | — |
| H-0（A0 A・B0 B × 200） | 照合 通過・`g22cw` 全部通過・flags 0・sat 0、陽性対照（`--src CD`）で NG。床 A0 3.15e3・B0 3.14e3（M4 と −0.01〜+0.03 dB）・TP −31.51・−31.45 dBFS | 床 3.16e3・3.12e3・TP −31.49・−31.48 |
| EQ-2 | 50 / 50 組・照合 通過、陽性対照 0 / 49 組（違う ch 65,525〜65,535） | 同じ |
| NET | `SET tint=0.01024` → `ERR ARG … 51.2 MB/s（予算 30 MB/s を越える。INTERFACE 4.5）。この構成の tint の最小は 0.02048 s`、直後の GET は 0.04096 のまま、`SET tint=0.02048` は OK。**陽性対照**（`--net-budget-mbs 0` で起こし直す）: `SET tint=0.01024` が OK・GET 0.01024 | （回していない） |
| tint 20.48 ms で 300 s（src C・D） | SPEC 29,254・7.35 GB・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。STATUS: miss・drop・pl_drop・pl_crc・pl_err・tp_rec_lost 0・time_ok 1・forced 0・loop_slow 1・**最長 21.5 ms・p99 7.5 ms**・pl_peak 3.2 MB。**1 周の計 11.77 ms**（`loopsum.py --nwin 2`、周のログの上限 300 周の分） | 取りこぼし 0・最長 22.1 ms・p99 7.5 ms・pl_peak 3.2 MB・1 周の計 11.71 ms |

- AXI_MAX_PIPELINE は起こす前（3 回とも）と後で 0x0102。終わりに specd を止めた。**PL には陽性対照の proj025 の bit が載ったまま**（次に載せる人は bit を指定して起こすので影響はない）
- 記録: 制御 PC の作業用のディレクトリ（`id1.txt`・`h0*`・`eq2*`・`net.txt`・`netp.txt`・`v2b*`・`p025*`）、ボードの `~/2g-2-m5/runs/`（specd のログ 3 本・`axi_*.txt`）。300 s の `.s45` は照合が済んだので消した

### 持ち越し（proj034 から）

- **fmt both の運転の loop_max 72〜76 ms・loop_slow 26〜28**（tint 40.96 ms、proj025 も同じ。miss・drop 0）。PS の側の話。→ **M4 で `--fast` ありなら loop_max 16.7 ms・loop_slow 0 と分かったので閉じる**（上の「M4 の結果」）
- R-1 の loop_max（20.8〜22.3 ms）が proj025 4b（13.4 ms）より重い理由（PS の側。proj025 も同じ）

## 判定（`test/acceptance/2g-2/`、2026-10-31 に書き起こした）

2G-4・2G-1-Fast の判定から 2G-2 に当たるものを選んだ。ID は同じ意味のものは同じ ID にする。

| ID | 何を確かめるか | study-rfsoc で |
|---|---|---|
| ID-1 | 自己記述（adc 0x020A_0101・time 0x020A_0102・proj 0x0034_0100・kind g22）・起動の見張り | 通過（proj034 R-1） |
| H-0 | 立ち上げ（2 窓の頭の欄・照合・床、kind 1・nch 65536・flags 0（待ち行列のあふれ・pos_mis・2Y の飽和を含む）） | 通過（proj034 R-1・R-2'） |
| EQ-2 | 2 コアに同じ ADC で bit 単位で同じ | 通過（proj034 R-1c） |
| H-2 | ch → IF（直接の側 2 点と共役の側 2 点、2 窓とも。3000.25・2500.5・3396.5・2597.25 MHz） | 通過（proj034 R-6） |
| V2-b | tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | tint 40.96 ms でだけ通過（proj034 R-3） |
| V2-L | tint 20.48 ms で 2 時間（電流・温度・落ちない） | なし |
| RING | リング 64 MiB が PS の 0.3 s の止まりを吸う | なし（2G-4 で入れた判定） |
| NET | 予算を越える tint（10.24 ms）を SET で断る | なし（2G-4 の M5 で入れた照合） |

- 回さないもの: F-2（ADR 0023）・CU・BUND（2G-4 だけの機能）。proj034 R-2 の proj025 との床・ch の並びの比べ（移植では比べる相手が無い）
- ノイズ OFF の要る H-2 は `instr.py ns off`／`on` で（ADR 0024）

## 決めること

1. **proj034 の `model/s2_model.py` の置き場所** → **決め**（2026-10-31）: `model/s2_model_g22.py` に名前を替える（上の「模型の名前」。2G-1-Fast の決めること 2 と同じ）
2. **2 時間と tint 20.48 ms の 30 分を、始める条件にするか M6 で回すか** → **決め**（2026-10-31）: M6（V2-L・V2-b）。2G-2 の電流（19.1 A）は 2G-4（32.6 A）より低く、取得の量は 2G-4・2G-1-Fast と同じ 25.6 MB/s（2 × 65,536 ch × 4 B / 20.48 ms）で、両方とも 30 分・2 時間が通っている（2G-1-Fast の決めること 3 と同じ）
3. **G22Backend で PROJ を照らすか**（上の「PS」の 1）→ **決め**（2026-10-31、案 A）: 照らさない（2G-1-Fast の決めること 4 と同じ。bit の約束は (BIT_KIND, BIT_REV) で、proj025 と proj034 はレジスタの並び・頭の欄・ch の並び・精度が同じ。取り違えは bits.json と記録の `ids.proj`・`usr` で分かる）
4. **実装の戦略** → **決め**（2026-10-31）: 既定（proj034 B-1 の決め。WNS +0.074 は PE の +0.032 より大きい）
