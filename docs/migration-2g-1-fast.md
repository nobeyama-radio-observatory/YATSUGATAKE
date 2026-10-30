# study-rfsoc からの移植計画（2G-1-Fast）

- 状態: **M0 済み**（2026-10-30、ブランチ `2g-1-fast/m0-map`。PR #78）。置き場所の表・`hw/common/` との違い・移植元の bit を数え、判定を `test/acceptance/2g-1-fast/` に書き起こした。決めること 1〜3 は開発者が案どおりに決めた（2026-10-30）。**M1 済み**（2026-10-31、ブランチ `2g-1-fast/m1-place`。表の行き先に置き、パスと模型の名前だけを直した。下の「M1 の結果」）。Makefile から試行の目標を外した（ブランチ `2g-1-fast/makefile-trim`）。**M2 済み**（2026-10-31、同じブランチ。sim の出力が移植元とバイト単位で同じ。下の「M2 の結果」）。次は M3（ビルド）
- 移植元: **`study-rfsoc@proj033-m0`**（注釈つきタグ、commit a12715d、2026-10-29）。RTL・ビルド・sim・模型・PS が 1 つの proj にある（2G-4 は RTL が proj031、PS が proj036 だった）
  - proj033 は proj024-m0（2G-1-Fast の最初の形）に proj030 の 2-for-1 を入れたもの。精度・機能は proj024 と同じで、DSP 924 → 628・LUT 22.2 → 16.5 %・BRAM 673 → 586.5・VCCINT 16.8 → 13.3 A
  - 移植元を proj024 から proj033 に替えた（proj033 README の「次にやること」2、7eab913）。proj033 の B-2（記憶のカスケードに段を足し、既定の戦略で閉じる形にする）はやらず、**Performance_Explore で閉じた bit を引き継ぐ**
- 土台にする決め方: 2G-4 の [`migration-2g-4.md`](migration-2g-4.md)（= SAM45-Fine の [`migration.md`](migration.md) の M0〜M7）と同じ段取り。違うところだけをここに書く
- 2G の移植の順（2026-10-28 に決めた）: 2G-4（v1.2.0）→ **2G-1-Fast** → 2G-2（proj034-m0）→ 2G-1-Fine。仕様は [ADR 0022](decisions/0022-2g-1-fast-and-fine.md)・[`spec/bits.md`](spec/bits.md)・[`spec/interface.md`](spec/interface.md) 2.4

## 原則（2G-4 と違うところ）

1. 2G-4 の原則 1〜3 はそのまま（変更は一度に一つ・数えて確かめる・**study-rfsoc の proj033 は書き換えない**）
2. **M1〜M4 は SAM45-Fine・SAM45-Wide・2G-4 のファイルに触らない。** 2G-4 の `hw/bits/2g-4/` と同じ名前で中身が違うもの（`s2_*`・`tb_s2_*`・`check_s2.py`・`model/s2_model.py`）は、2G-1-Fast の側に置く。一本化は 2G-2 の移植の後の別の PR（下の「s2_* の扱い」）
3. **PS は `sw/pynq/` のまま使う。** 2G-4 の M5 で G21 の Backend（proj024 の版）を `sw/pynq/` に入れてある。2G-4 のように `sw/pynq-2g/` の段を置かない。移植元の PS と違うのは 3 か所だけ（下の「PS」）で、M5 で入れる

## 始める条件

- [x] proj033 の判定（M・P・S・E の sim と模型・B-1・R-1〜R-6）が通り、README に結論が書かれている（2026-10-29）。外れは B-1 の既定の戦略の WNS（−0.242 ns）・R-2c の VCCINT（13.3 A、予言 10〜13 A）・R-6 の絶対のレベル（入口の違い。2-for-1 の判定には効かない）
- [x] 2G-1-Fast の運用に使う bit を決めた → **proj033 の build-PE**（下の「移植元の bit」）。B-2 はやらない（7eab913）
- [x] **タグ** `proj033-m0`（a12715d）を push した（2026-10-29）
- [x] ボードの準備（AXI_MAX_PIPELINE 0x0102）は 2G-4 と同じボードに入っている（2G-4 の始める条件）
- [x] **判定を `test/acceptance/2g-1-fast/` の書き方で書き起こした**（2026-10-30、2G-4 と同じく M0 で）: 7 判定（ID-1・H-0・H-2・V2-b・V2-L・RING・NET）。V2-b の 20.48 ms・V2-L・RING・NET は study-rfsoc で回していない（M6 で初めて）
- [x] **2 時間の連続運転** → **M6 の V2-L で初めて回す**（決めること 3、2026-10-30）。proj033・proj024 とも 30 分（R-3・4c）までで、2 時間は回していない（2G-4 は始める条件にした、proj036 R-4）
- [x] **tint 20.48 ms（運用の最小）での 30 分** → **M6 の V2-b で初めて回す**（決めること 3、2026-10-30）。proj033 R-3 は tint 40.96 ms。2G-1-Fast は 1 ダンプ 131,072 ch × 4 B で 20.48 ms のとき 25.6 MB/s（2G-4 と同じ量、interface 4.5）

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj033 README「B-1」の **Performance_Explore** のビルド（`build-PE/`、2026-10-29 00:12）。sha256・FDRI は手元の `proj033/build-PE/` で数えた（2026-10-30）。

| 項目 | 値 |
|---|---|
| bit の sha256 | `204a61da9185564e0b1da5f4fabc5df9e43e2556361221ec83423509e69caf90`（34,437,476 B） |
| hwh の sha256 | `384747b8229e1c2fac1bd2cd5801b71870b1928b9ddc3f1af62d5eefdcc61500` |
| FDRI（`sw/pynq/bitinfo.py`） | 8,608,824 語・sha256 `6bdecddf9a5b0aa2e886ee4944d66f5042324b489fa441eb866c320d1759d8e4` |
| 構成の流れ（欄 e）の sha256 | `642bb6cbc7c610e391a2ebdd739f49fc3fc22e8c27feca54e21bda7c00c8ef99` |
| ID | BIT_KIND 11・BIT_REV 1・**PROJ 0x0033_0100**。IF_ID 0x020B_0101（コア）・0x020B_0102（time_core）。USR_ACCESS なし |
| 実装の戦略 | **Performance_Explore**（`make build IMPL=Performance_Explore`、出力は `build-PE/`）。既定の戦略は WNS −0.242 ns で閉じない |
| `-1` の WNS / WHS | **+0.025 ns / +0.010 ns**（README は +0.025345・+0.009647） |
| LUT / FF | 70,248（16.52 %）/ 123,411（14.51 %） |
| DSP / BRAM タイル / URAM | 628（14.70 %）/ 586.5 / 48 |
| `report_cdc` | CDC-3 Info 60・CDC-6 Warning 2・CDC-15 Warning 3,137 |
| Vivado | 2024.1 |
| F-2 | M = A 70.2・B 70.1・C 68.6・D 68.5 ns（proj033 R-5）。ADR 0023 の後は CAL に入れない（下の「PS」） |

- ビルドの後の commit a12715d は `g21_s45_core.v` の注釈 1 行（個人名を「開発者」に）だけを変えた。注釈なので FDRI は変わらない見込み（M3 で確かめる）
- bit そのものは git に入れない（ADR 0018）

## 置き場所の対応（M0、2026-10-30）

ファイル 1 つずつの行き先は付録 [`migration-2g-1-fast-files.md`](migration-2g-1-fast-files.md)（146 個: 置く 42・2G-1-Fast の側に写し 1・既にある 80・移さない 23）。

| study-rfsoc（proj033-m0） | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| `src/g21/`（13 個）・`src/s2_*.v`（3 個） | `hw/bits/2g-1-fast/src/` | 2G-1-Fast の部品・係数とひねり係数の hex。`s2_*` は 2G-4 の同名と違う版（下） |
| `src/common/rec_fr.v` | `hw/bits/2g-1-fast/src/` に**写し** | `hw/bits/2g-4/src/rec_fr.v` と同じ中身（下の「`hw/common/` との違い」） |
| `src/common/` の残り 34 個・`src/board/` 3 個 | **既にある** `hw/common/`・`hw/board/` | バイト単位で同じ |
| `Makefile`・`build.tcl` | `hw/bits/2g-1-fast/` | パスだけを直す（下の「M1 で直すパス」）。proj033 には `build_post.tcl` が無い |
| `sim/`（17 個） | `hw/bits/2g-1-fast/sim/` | 試験台・照合・IP の模型（lane_fft_g21_model）。`rec_fr_ref.v`・`tb_recfr_eq.v` は 2G-4 の同名と同じ中身、`tb_s2_*`・`check_s2.py` は違う版 |
| `model/g21_fixed.py` | `model/` | 名前は今の `model/` と重ならない |
| `model/s2_model.py` | **`model/s2_model_g21.py`**（名前を替える） | 2G-4 の `model/s2_model.py` と中身が違う（下の「模型の名前」） |
| `model/g2_model.py` | **既にある** `model/g2_model.py` | バイト単位で同じ |
| `tools/` のうちビルド・sim が使う 4 個 | `hw/bits/2g-1-fast/tools/` | gen_g21_tables・ip_impl・ip_survey・ooc_rtl |
| `pynq/g21cw.py` | `sw/pynq/` | 2G-1-Fast の CW の判定の道具（2G-4 の移植で「2G-1 の道具はそれぞれの移植で」とした） |
| `pynq/` の残り 41 個・`tools/amslog.py` | **既にある** `sw/pynq/` | 同じ 20・違う 21（2G-4 の M5 で一本化した版を使う） |
| `pynq/` の 18 個・`tools/` の 3 個・README・`runs/` | 移さない | Fine・窓・試行の道具、bench_g21、`tp_cal.json`（ボードに置く、ADR 0025）、estimate・power_rpt・shapecmp21 |

### `hw/common/` との違い（2026-10-30）

proj033 の `src/common/` 35 個と `src/board/` 3 個を、YATSUGATAKE の main（f2c22aa）の `hw/common/`・`hw/board/` と比べた: **37 個がバイト単位で同じ、違うのは `rec_fr.v` の 1 個**。
`core_cmn.v`・`tp_core.v` は 2G-4 の一本化（PR #74）で proj031 の版に替えたので、今は同じ。

| ファイル | 違い | 2G-1-Fast の使い方 |
|---|---|---|
| `rec_fr.v` | `hw/common/` の版は、一本化のときに `n_cap == np - 1` の 2 か所を `np - 1'b1` に直した（幅の無い 1 では合成が別の回路を作り、Fine の FDRI が v1.0.0 から変わった。PR #74） | `NCH(131072)`（g21_core）。**proj033 の版の写しを `hw/bits/2g-1-fast/src/` に置く**（2G-4 と同じ扱い。`hw/common/` の版で作ると FDRI が移植元と変わるおそれがあり、M3 の比べができない） |

- 2G-1-Fast の build.tcl が `src/common/` から読むのは 13 個（core_cmn・raw_core・cmul・dft16f・tp_core・rec_fr・rec_arb・adc_ev・time_core・s45_ring・gb_adc・gb_gate・axis_sel4）。sim は ほかに `dft16.v`（sim-g21ch・ooc-ref の proj024 の鎖）を読む
- `rec_fr.v` の写しを `hw/common/` の版に寄せるのは、2G-4 の写しと一緒に、別の PR で（どちらも FDRI が変わるかを作り直して数える）

### s2_* の扱い（決めること 1、2026-10-30 に案どおり決めた）

2G-4 の移植の M0 で「2-for-1 の部品 `s2_*` は 2G-1-Fast・2G-2 も使う見込み。そのときに `hw/common/` へ上げるかを決める」とした。3 本の版（proj031 = 2G-4・proj033 = 2G-1-Fast・proj034 = 2G-2）を比べた:

| 部品 | 2G-4 と 2G-1-Fast の違い | 2G-1-Fast と 2G-2 の違い | 1 本にできるか |
|---|---|---|---|
| `s2_sep.v` | パラメータの既定（ZW 28 → 30・KB 12 → 14）と注釈だけ（26 行） | 既定と注釈（14 行） | できる（式は M に依らない。既定を外して各 bit が渡す） |
| `s2_q.v` | proj033 で行の幅を KB のパラメータにした（34 行）。2G-4 の版は 12 bit の決め打ち | 既定（AB 11 → 10・KB 14 → 13）と注釈（15 行） | できる（proj033・034 の形で、2G-4 は AB 9・KB 12 を渡す） |
| `s2_chain.v` | **式が違う**: 2G-4 は 2Y を 27 bit に飽和して cmul SH 19、2G-1-Fast は 2Y を 3 bit 丸めて SH 18（proj033 M-1b の (i)） | 52 行 | 今の形ではできない（丸めの段をパラメータにすれば、できるかもしれない） |

**決め**: M1 では 3 個とも `hw/bits/2g-1-fast/src/` に移植元のまま置く（原則 1。2G-4 の木に触らない）。
2G-2 の移植（M3 まで）の後に、`s2_sep`・`s2_q` を 1 本にして `hw/common/` に上げる PR を別に作る。合格は 3 本の bit を作り直して FDRI がそれぞれのリリースと同じこと（2G-4 の一本化と同じ型）。`s2_chain` は bit ごとに置いたままにする。
3 本がそろってから一度に寄せるので、2G-4・2G-1-Fast の FDRI の確かめは 1 回で済む

### 模型の名前（決めること 2、2026-10-30 に案どおり決めた）

2G-4 の移植で、proj031 の `model/s2_model.py`（2G-4 の寸法: N 131072・M 4096）を `model/s2_model.py` に置いた。proj033 の `model/s2_model.py` は同じ名前で 2G-1-Fast の寸法（N 262144・M 16384）と鎖の入口 (i) の版（305 行違う）。

**決め**: proj033 の版を **`model/s2_model_g21.py`** に置き、読む側の `import s2_model` を `import s2_model_g21` に直す（`sim/check_s2.py`・`sim/check_g21.py` の 2 行と、Makefile の `model` の 1 行）。
- `model/` に模型を集める今の形（2G-4 の `g24_fixed.py`・`g24_model.py`）を崩さない
- 2G-4 の `model/s2_model.py` は名前を替えない（リリースした木に触らない）
- ほかの案: 2G-1-Fast の模型を `hw/bits/2g-1-fast/model/` に置く（import の行は直さなくて済むが、`model/` に集める形から外れ、`g2_model.py` を 2 か所に置くか道を足すことになる）
- M1 の「違う行はパスの行だけ」の照合では、この 3 行を「名前の直し」として別に数える

### M1 で直すパス（予定）

2G-4 の M1 と同じ型。中身は変えない:
- `Makefile`・`build.tcl`: `src/common/` → `../../common/`（**写しの `rec_fr.v` は `src/`**）、`src/board/` → `../../board/`、`model/` → `../../../model/`（`s2_model.py` は `s2_model_g21.py`）。`src/g21/`・`src/s2_*.v` は `hw/bits/2g-1-fast/src/` の下に同じ形で置くので直さない
- `sim/check_s2.py`・`sim/check_g21.py`・`tools/gen_g21_tables.py` の模型の道（`../model` → `../../../../model`）と、上の import の 2 行
- `model/s2_model_g21.py`・`model/g21_fixed.py` は直さない（同じディレクトリの `g2_model` を読む）
- `runs/` は git に入れない（`.gitignore` に `/hw/bits/2g-1-fast/runs/`）
- **在ってはいけない側の照合**: 2G-1-Fast の Makefile・build.tcl が `hw/common/rec_fr.v` と、`hw/bits/2g-4/` の下のファイルを指していないこと（指していると、2G-4 の寸法の `s2_*` か 1'b1 の版の rec_fr で作られる）。`model/s2_model.py`（2G-4 の版）を読む行が無いこと

### M1 の結果（2026-10-31、ブランチ `2g-1-fast/m1-place`）

- **置く**（c9051ec）: 付録の 43 個（置く 42・写し 1）を `git show study-rfsoc@proj033-m0:…` から取り出して置いた。43 個とも移植元と blob が同じ（`model/s2_model.py` は `model/s2_model_g21.py` に、`src/common/rec_fr.v` は `src/rec_fr.v` に）。既にある 80 個のうち M0 で「同じ」だった 62 個は、今の main（f2c22aa）でも同じ（M0 の比べの後に変わっていない）
- **パスの直し**（6d58805）: 5 個・43 行（Makefile 13・build.tcl 24・Python 6）。**違う行はすべてパスの行か模型の名前の行**: 新しい行のパスと名前を元に戻すと 43 行とも古い行と一致（機械で照合）。名前の行は 4 行（`import s2_model_g21` 2・docstring 1・Makefile の `model` 1）で、M0 で数えた 3 行に `check_s2.py` の docstring の 1 行が加わった。`src/g21/`・`src/s2_*.v` は直していない。`model/` の 2 個と `sw/pynq/g21cw.py` は移植元のまま
- **在ってはいけない側**: 2G-1-Fast の Makefile・build.tcl・sim・tools が `hw/common/rec_fr.v`（`src/common/rec_fr`）・`hw/bits/2g-4/`・`model/s2_model.py`（`import s2_model as`）を指す行は 0（直す前の版 c9051ec に当てると Makefile 2・build.tcl 1・check_s2.py 1・check_g21.py 1 行を拾う = 照合が働いている）。build.tcl と Makefile が読むファイル（コメントの行を除く）はすべて在る
- **動かして確かめたこと**（Vivado は使っていない）: `make model-g21`（M1〜M8）・`model`（M-1a〜M-2b、鎖の入口 (i)）が全部通過。`make gen` の出力が `src/g21/` の hex 4 個とバイト単位で同じ。`sim-recfr`（写しの `rec_fr.v`）・`sim-sep` が「全部通過」、陽性対照 4 本は落ちた。Tcl 4 個が `info complete` で完結、Python 6 個（`sw/pynq/g21cw.py`・`model/` の 2 個・sim と tools の 3 個）が `py_compile` を通る
- **`runs/` は git に入れない**（`.gitignore` に `/hw/bits/2g-1-fast/runs/`）
- **動かないままにしたもの**: Makefile の `estimate`（`tools/estimate.py` を移していない）。`s2`・`survey`・`ooc-*` は Vivado で動くはずだが回していない。外すのは下の 1
- `hw/bits/2g-1-fast/README.md` を足し、`hw/bits/README.md` の行を分けた

### M1 の後にすること（それぞれ別の PR）

1. **Makefile から試行の目標を外す**（2G-4 の `2g-4/makefile-trim` と同じ型）: `estimate`（`tools/estimate.py` を移さない）・`s2`・`survey`・`ooc-*`（とくに `ooc-ref` は proj024 の鎖 `g21_chain.v` を合成する比べの相手）。`sim-all` が無いので、2G-1-Fast の sim の全部（下の M2 の表）を回す目標を足す。外した後に M2
   - `src/g21/g21_chain.v`・`sim/tb_g21_chain.v`（`sim-g21ch`）は proj024 の鎖で、今の bit は使わない（`s2_chain` に替わった）。M1 では移植元のまま置き、ここで外すかを決める
   - **済み（2026-10-31、ブランチ `2g-1-fast/makefile-trim`、3b19edb）**: `estimate`・`s2`・`survey`・`ooc-ref`・`ooc-all` と、それだけが使う `JOBS` を外した。部品の OOC（`ooc-sep`・`ooc-chain`・`ooc-q`）は 2G-4 と同じく残した（M0 の案の「`ooc-*`」より狭くした）。`tools/ip_impl.tcl`・`ip_survey.tcl` は 2G-4 と同じく置いたまま
   - `sim-all` は模型 2 本（`model-g21`・`model`、「まとめ」の行に「不合格」が無いこと）と sim 13 本（M2 の表の全部、最後の行「sim-…: 全部通過」）を回し、`build-sim-logs/` の 15 個で判定する。共有の入力 `g21s_in/x.hex` を先に作ってから、目標を `SIM_J`（既定 4）本ずつ並べる。判定の陽性対照: ログの写しに「不合格」・NG・ログの欠けを入れると 3 つとも拾う
   - **`sim-g21s` は `x.hex` が在れば作り直さないようにした**（2G-4 の `sim-g24s` と同じ形、1 行）。移植元は毎回作り直すので、並べた `g21core`・`g21s45` が書きかけの `x.hex` を読むおそれがある（proj027 で踏んだ穴）。中身は同じ乱数の種で作るので出力は変わらない（下の M2 で確かめた）
   - **`g21_chain.v`・`sim-g21ch` は残す**: 2G-4 も `g24_chain`・`sim-g24ch` を残した。`g21_tw` と `dft16.v` の回帰を兼ね、軽い（M2 の表にも入れてある）
2. `s2_sep`・`s2_q` の一本化 → 2G-2 の移植の後（上）

### M2 の結果（2026-10-31、ブランチ `2g-1-fast/makefile-trim`）

この PC（Icarus Verilog 11.0・Python 3.10.12・numpy 1.21.5）で、移植先（`hw/bits/2g-1-fast/`、3b19edb）の `make sim-all` と、**タグ `proj033-m0` の proj033 を `git archive` で取り出して同じ 15 個を回したもの**を比べた（同じ PC・同じ版の道具で、同じ時間に並べて回した。移植先 53 分・移植元 77 分）:

- **15 個とも「全部通過」**（模型 2 本は「まとめ」の行が全部通過、sim 13 本は最後の行が全部通過）。陽性対照は 19 本がすべて落ちるべきところで落ちた（g21ds の陽性対照は D_S +0 のところだけで落ちる）。両側で同じ
- 移植元の `sim-g21s` は `x.hex` を毎回作り直すので、移植元の側だけ `sim-g21s` を先に 1 本で回し、残りの 12 本を 4 本ずつ並べた（Makefile には触っていない）
- **`build-sim/` の出力 224 個のうち 187 個がバイト単位で同じ**（各変種の `tb.log`・`check.log`・入力の hex を含む）。違う 37 個は iverilog のコンパイル物 `tb` だけで、**パス（`src/common/` ↔ `../../common/`・写しの `rec_fr.v` は `src/`）と、コンパイルごとに変わる番地（`0x…`）を読み替えると 37 個とも同じ**（陽性対照: 1 行に字を足すと不一致になる）
- **`build-sim-logs/` の 15 個のうち 13 個がバイト単位で同じ**。違う 2 個は模型のログで、違うのは make が出すコマンドの行（`model/` ↔ `../../../model/`、`s2_model.py` ↔ `s2_model_g21.py`）と経過秒（`[m2: 7.2 s]` ↔ `[m2: 7.1 s]` など）だけ。`runs/model.txt`・`runs/model-g21.log` も経過秒だけが違う

## 手順

| 手順 | 2G-1-Fast ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録）・始める条件・`hw/common/` との違いの数え・判定の書き起こし | 全ファイルに行き先がある・始める条件が全部 [x]（**2026-10-30**） |
| M1 | 表の行き先に置き、パスと模型の名前だけを直す | `git diff --stat` で中身の変更がパスの行と名前の行だけ。在ってはいけない側の照合（上）（**2026-10-31**: 上の「M1 の結果」） |
| M2 | sim を全部回す: model-g21・model、sim-g21c・g21t・g21p・g21ch・lane・g21a・g21s・recfr・g21core・g21s45・g21ds・sep・all2 | proj033-m0 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**2026-10-31**: 上の「M2 の結果」） |
| M3 | ビルド（`-1`、**`IMPL=Performance_Explore`**） | **FDRI が移植元と同じ**（`6bdecddf…d8e4`）。WNS / WHS が移植元と小数 6 桁まで同じ（+0.025345 / +0.009647） |
| M4 | 実機の短い回帰（ボードの新しいディレクトリ、`sw/pynq/` で `specd --g21`） | ID・照合・g21cw・tint 40.96 ms で 300 s 取りこぼし 0 が proj033 R-1・R-3 と同じ値 |
| M5 | 下の「PS」の 3 つと、Fine の M5b（USR_ACCESS）を 2G-1-Fast に当てる | M2〜M4 の回し直しが予言どおり（USR_ACCESS で FDRI は変わる。2G-4 の M5 と同じ） |
| M6 | 2G-1-Fast の判定（`test/acceptance/2g-1-fast/`）を全部通し、性能評価を書く | `docs/performance/2g-1-fast/<版>.md` |
| M7 | spec・design・user の 2G-1-Fast の分を書き、リリース | `release.md` |

### M3 の心配（M3 の前に書く）

- 2G-4 の M3 は既定の戦略で「ディレクトリだけ違う作り直しで構成データまで同じ」だった。Performance_Explore でも、同じ Vivado・同じ入力なら同じ結果が出る見込み（Wide は PE で v1.0.0 と FDRI が同じに作り直せている、PR #74 の 5）
- **WNS +0.025 ns は余裕が薄い**（proj033 B-1 の注: RTL を少し変えると負に戻る前提で扱う）。M1 は RTL を変えないので M3 は同じ値のはず。M5 の USR_ACCESS・後の一本化で配置が動くと負になりうる。そのときは B-2（記憶のカスケードに段）を study-rfsoc でやり直す（proj033 は書き換えない。新しい proj で）

### PS（M5、2G-4 の M5 と違うところ）

`sw/pynq/` には 2G-4 の M5 で G21 の Backend（`--g21`、proj024 の版）が入っている。proj033 の PS は proj024 の PS から 3 か所だけ変えたもの（`git diff proj024-m0:proj024/pynq proj033-m0:proj033/pynq`、5 ファイル 12 行）:

1. **`s45core.PROJ_G21`** を 0x0024_0100 → 0x0033_0100。今の `sw/pynq/` ではログ（widef2）に出るだけで、照合には使っていない。G21Backend は `discover(bit_kind=11, ncore=1, bit_rev_min=1)` で開くので、**proj024 の bit（PROJ 0x0024_0100、同じ (11, 1)）も通ってしまう**。M5 で PROJ を照らす（2G-4 の cuctl と同じく PROJ を見る）かを決める
2. **timebase**: proj033 は `CAL[0x0033_0100]`（F-2 の値）を足した。YATSUGATAKE は ADR 0023 でボードの較正ファイル（`/etc/yatsugatake/time_cal.json`）を使うので、**CAL には足さない**。M5 で 2G-1-Fast の ADC → コアの道が共通の道か（ギアボックス・time_core・RAW・axis_sel4 が `hw/common/` の同じファイル、RFDC の組み立てが同じ）を確かめ、`ADC_PATH` に書く（2G-4 と同じ。proj033 の M = 68.5〜70.2 ns は Wide の M と ±1.4 ns）
3. widef2・specd などの `--bitfile` の既定（proj024.bit → proj033.bit）。`sw/pynq/` では bits.json の項目（`"kind": "g21"`）で指すので、既定は直さない

ほかに 2G-4 の M5 で入れたもの（予算の照合 `check_net`・リング 64 MiB・LMX の PWR 3・ボードの印）は G21 にも効いている。2G-1-Fast で確かめるのは M4〜M6 の回帰で

## 判定（`test/acceptance/2g-1-fast/`、2026-10-30 に書き起こした）

2G-4 の判定から 2G-1-Fast に当たるものを選んだ。ID は 2G-4 と同じ意味のものは同じ ID にする。

| ID | 何を確かめるか | study-rfsoc で |
|---|---|---|
| ID-1 | 自己記述（adc 0x020B_0101・time 0x020B_0102・proj 0x0033_0100・kind g21）・起動の見張り | 通過（proj033 R-1） |
| H-0 | 立ち上げ（頭の欄・照合・床、kind 1・nch 131072・flags 0（待ち行列のあふれ・pos_mis・2Y の飽和を含む）） | 通過（proj033 R-1） |
| H-2 | ch → IF（直接の側 2 点と共役の側 2 点。3000.25・2500.5・3396.5・2597.25 MHz） | 通過（proj033 R-6） |
| V2-b | tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | tint 40.96 ms でだけ通過（proj033 R-3） |
| V2-L | tint 20.48 ms で 2 時間（電流・温度・落ちない） | なし |
| RING | リング 64 MiB が PS の 0.3 s の止まりを吸う | なし（2G-4 で入れた判定） |
| NET | 予算を越える tint（10.24 ms）を SET で断る | なし（2G-4 の M5 で入れた照合） |

- 回さないもの: F-2（ADR 0023）・CU・EQ-4・BUND（2G-4 だけの機能）。proj033 R-2 の proj024 との床の比べ（移植では比べる相手が無い）
- ノイズ OFF の要る H-2 は `instr.py ns off`／`on` で（ADR 0024）。`g21cw.py` に `--ns-off` は無い

## 決めること

1. **`s2_*` を `hw/common/` に上げるか** → **決め**（2026-10-30）: M1 では bit ごとに置き、2G-2 の移植の後に `s2_sep`・`s2_q` だけを 1 本にする（上の「s2_* の扱い」）
2. **proj033 の `model/s2_model.py` の置き場所** → **決め**（2026-10-30）: `model/s2_model_g21.py` に名前を替える（上の「模型の名前」）
3. **2 時間と tint 20.48 ms の 30 分を、始める条件にするか M6 で回すか** → **決め**（2026-10-30）: M6（V2-L・V2-b）。2G-4 は study-rfsoc で先に回したが、2G-1-Fast は電流が 2G-4 の半分以下で、取得の量は 2G-4 と同じ 25.6 MB/s（2G-4 で 30 分・2 時間とも通っている）。study-rfsoc で先に回すなら、proj033 は書き換えないので新しい proj の R にする
4. **G21Backend で PROJ を照らすか**（上の「PS」の 1）→ M5 で
