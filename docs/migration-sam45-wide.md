# study-rfsoc からの移植計画（SAM45-Wide）

- 状態: **M4 済み**（2026-10-22、ブランチ `sam45-wide/m1-place`）。次は M5（Fine の M5a・M5b を当て、PS を一本化する。Fine の v1.0.0 の後）
- 移植元: **`study-rfsoc@proj023-m0`**（注釈つきタグ、commit 3a2ce56）
- 土台にする決め方: SAM45-Fine の [`migration.md`](migration.md) と同じ段取り（M0〜M7）。違うところだけをここに書く

## 原則

1. **変更は一度に一つ。** 移植の PR は「ファイルを置き直す」だけにする（Fine の原則 1 と同じ）
2. **同じものができたことを、数えて確かめる。** M3 は移植元の bit との FDRI の一致、M4 は移植元と同じ値
3. **study-rfsoc の proj023 は書き換えない。** 移植の後に見つかった問題は、YATSUGATAKE で issue にする
4. **M1〜M4 は SAM45-Fine のファイルに触らない。** Fine と共有で proj023 が変えたファイルは Wide の側に写しを置き、一本化は M1 の後の別の PR にする（下の「M1 の後に一本化するもの」）。Fine の最初のリリース（M7）と並行で進めるため

## 始める条件

- [x] proj023 の判定（B-1・H-1〜H-4・SNAP・D_S・F-2）が通り、README に結論が書かれている（2026-10-21。RTL はビルド 11、567fda2 で凍結）
- [x] 移植元の commit を 1 つに決めた → `study-rfsoc@proj023-m0`
- [ ] **proj023-m0 が push 済み**（study-rfsoc の公開前スキャンの後に push する。M1 の PR を出す前に要る）
- [ ] **判定が `test/acceptance/` の書き方で書かれている**: 満たしていない。proj023 の判定は README の中にだけある（proj023 の `test/acceptance/` は proj021 の Fine の写しのまま）。Fine は移植の前に 21 判定を書いていた。**M6 の前に `test/acceptance/sam45-wide/` に書く**（M1〜M4 の回帰は README の判定の値と比べる）

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj023 README「移植元と閉じたときの値」の写し。

| 項目 | 値 |
|---|---|
| bit の sha256 | `473911e59baa87fc8bff43d15e4791bd90d9cfd0cf2d4900898bd0218a3c5178`（34,437,476 B） |
| hwh の sha256 | `32759af1f59ff04fc6041977442a2029abc6c056b6aaa67ebf48b6c5a7bf769a` |
| ID | BIT_KIND 1・BIT_REV 1・PROJ 0x0023_0100。IF_ID 0x0201_0101（コア 4）・0x0201_0102（time_core） |
| 実装の戦略 | **Performance_Explore**（`IMPL=Performance_Explore`、study-rfsoc の `build-PE/`）。凍結した RTL（ビルド 11）は既定の戦略では作っていない（その前のビルド 8 は既定で WNS −0.008 ns、同じ RTL の PE で閉じた） |
| `-1` の WNS / WHS | **+0.000716 ns** / +0.009500 ns |
| LUT / FF | 255,211（60.01 %）/ 492,722（57.93 %） |
| DSP / BRAM タイル / URAM | 2,720 / 817.5 / 40 |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137（proj021-m0 と同じ件数） |

bit そのものは git に入れない（ADR 0018）。

## 置き場所の対応（M0、2026-10-21）

ファイル 1 つずつの行き先は付録 [`migration-sam45-wide-files.md`](migration-sam45-wide-files.md)（proj023 の 208 個: 置く 83・既にある 16・移さない 109）。

| study-rfsoc（proj023） | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| `src/common/` の新しいもの（`wide_*.v` 8 個・`core_cmn.v`） | `hw/common/` | 新しいファイルを足すだけ（Fine のファイルは変えない）。2G も同じ部品を使う |
| `src/common/` の `cmul.v`・`rec_fr.v`（proj023 で口を足した） | `hw/bits/sam45-wide/src/` に**写し** | 既定では今までと同じ式。Fine は `hw/common/` の版のまま。一本化は M1 の後 |
| `src/common/` の残り（Wide が使う 10 個） | **既にある** `hw/common/` | バイト単位で同じ。Wide が使わない Fine の部品（窓・DDC・spec_core など）は移さない |
| `src/board/`・`clocks/` | **既にある** `hw/board/` | バイト単位で同じ |
| `src/sam45wide/`（係数とひねり係数の hex）・`src/sam45fine/fft_cfg.tcl` | `hw/bits/sam45-wide/src/` | fft_cfg.tcl は Fine と同じ中身の写し（bit のディレクトリを自分で閉じるため） |
| `build.tcl`・`Makefile`・`program.tcl` | `hw/bits/sam45-wide/` | パスだけを直す（下の「M1 で直すパス」） |
| `sim/` の Wide の試験台と照合（9 個） | `hw/bits/sam45-wide/sim/` | sim-wpfb・wch・wsp・wco・ws45・wds と model-wide に要るものだけ。Fine の試験台は移さない |
| `tools/`（Wide の目標が使う 11 個） | `hw/bits/sam45-wide/tools/` | 係数・ひねり係数の生成、配線後の phys_opt、最悪の経路、フロアマップ、CDC、survey、PS のプリセット、資源の見積もり |
| `model/wide_model.py`・`bin_resp.py` | `model/` | 係数の原型の唯一の正（sim の check_wide.py が読む） |
| `pynq/`（specd・取得・受け側・制御・Wide の道具 wide*.py・`tp_cal.json`・`bits.example.json`）と `tools/` の `h2peek.py`・`sgstat.py` | **`sw/pynq-wide/`**（44 個） | M1〜M4 は proj023-m0 の PS とバイト単位で同じにする。`sw/pynq/` への一本化は Wide の M5 |
| `README.md` | 移さない | Wide の性能評価（M6）の材料として指す |
| `test/acceptance/` | 移さない | 中身は Fine の判定の写し。Wide の判定は M6 の前に書く |
| `runs/`・`pynq/` の測定の記録・Fine の試行の道具 | 移さない | |

### M1 で直すパス（予定）

Fine の M1（10ecff8）と同じ型。中身は変えない:
- `Makefile`・`build.tcl`: `src/common/` → `../../common/`、`src/board/` → `../../board/`、`src/sam45wide/` と `src/sam45fine/fft_cfg.tcl` → `src/`、**`src/common/cmul.v`・`rec_fr.v` → `src/`**、`model/` → `../../../model/`、`pynq/` → `../../../sw/pynq-wide/`
- `sim/check_wide.py` の模型のパス（`../model` → `../../../../model`）、`tools/gen_wide_coef.py`・`gen_wide_tw.py` の書き出し先
- **在ってはいけない側の照合を M1 に付ける**: Wide の Makefile・build.tcl が `hw/common/cmul.v`・`hw/common/rec_fr.v` を指していないこと（指していると、口の無い Fine の版で作られるおそれがある）

### M1 の後にすること（それぞれ別の PR）

1. **Makefile から Fine の目標を外す**（ブランチ `sam45-wide/makefile-trim`、2026-10-22）: proj023 の Makefile には proj021 から引き継いだ Fine の目標（sim-win・sim-ddc・sim-spec-all・sim-ring など、`sim-all` も Fine の 3 つを回す）が残っている。M1 では移さないファイルを指して動かないので、外して `sim-all` を Wide の sim に替える。外した後に M2 をもう一度
2. **`cmul.v`・`rec_fr.v` を `hw/common/` に一本化**（Fine の v1.0.0 のタグの後。ブランチ `sam45-wide/common-unify`、2026-10-22。下の「一本化の手順と予言」）: proj023 の版で `hw/common/` を替え、Wide の写しを消す。合格は、Fine の sim（sim-ring・sim-raw を含む）の回帰と、**Fine を作り直して FDRI が M5b の bit と同じ**こと（既定では同じ式なので同じはず。違えば一本化しない）
3. **`sw/pynq-wide/` を `sw/pynq/` に一本化** → Wide の M5 で行う（下）

## 手順

| 手順 | Wide ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録） | 全ファイルに行き先がある（**済み 2026-10-21**） |
| M1 | 表の行き先に置き、パスだけを直す | `git diff --stat` で中身の変更がパスの行だけ。在ってはいけない側の照合（上）（**2026-10-21**: 下の「M1 の結果」） |
| M2 | sim を全部回す（sim-wpfb 3・wch 6・wsp 9・wco 4・ws45 3・wds 2、model-wide） | proj023 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**済み 2026-10-21**: 下の「M2 の結果」） |
| M3 | ビルド（`-1`、**Performance_Explore**） | **FDRI が移植元と同じ**（Fine の M3 は構成データまで同じだった）。WNS は移植元と小数 6 桁まで同じ（**済み 2026-10-22**: 下の「M3 の結果」） |
| M4 | 実機の短い回帰 | ID（`wide.py --list`）・起動の見張り（FLAGS 0・IP の位相）・雑音の 7 本・V2-b（5 分）が proj023 と同じ値（**済み 2026-10-22**: 下の「M4 の結果」） |
| M5 | Fine の M5a・M5b を Wide に当て、`sw/pynq-wide/` を `sw/pynq/` に一本化 | 下の「M5」 |
| M6 | Wide の判定を `test/acceptance/sam45-wide/` に書き、全部通し、性能評価を書く | `docs/performance/sam45-wide/<版>.md` |
| M7 | spec・design・user の Wide の分を書き、リリース | `release.md` |

### M1 の結果（2026-10-21、ea3409c・7b3512c）

- **置く**（ea3409c）: 付録の 83 個を `git show study-rfsoc@proj023-m0:proj023/…` から取り出して置いた。置いた 83 個と既にある 16 個は、移植元と**バイト単位で同じ**（全部を照合）
- **パスの直し**（7b3512c）: 6 個・106 行（Makefile 63・build.tcl 35・ほか 8）。**違う行はすべてパスの行**: 古い行と新しい行からパスの部分を消して比べ、106 行とも一致（陽性対照: パス以外を 1 文字変えた行は不一致になる）。`sw/pynq-wide/`・`model/` は直していない（移植元のまま）
- **在ってはいけない側**: Wide の Makefile・build.tcl が `hw/common/cmul.v`・`rec_fr.v` を指す行は 0（直す前の版に当てると 2・22 行を拾う = 照合が働いている）。build.tcl が読むファイル（コメントの行を除く）はすべて在る。Wide の sim の目標（WPFB・WCH・WSP・WCO・WDS・WS45）の RTL もすべて在る
- **動かして確かめたこと**（作業用の環境。iverilog と Vivado は使っていない）: `make model-wide`（check_wide.py の自己検査、模型を `../../../model/` から読む）が全部通過。`tools/gen_wide_coef.py`・`gen_wide_tw.py` の出力が `src/wide_coef.hex`・`wide_tw.hex` とバイト単位で同じ。Tcl 10 個が `info complete` で完結、`sw/pynq-wide/` の 44 個が `py_compile` を通る
- **動かないままにしたもの**: Makefile の Fine の目標（sim-win・sim-ddc・sim-spec-all・sim-ring など、`sim-all` も）は、移していないファイル（Fine の試験台・`src/sam45fine/pfb4_rom.v` など）を指すので動かない。外すのは M1 の後の別の PR（「M1 の後にすること」の 1）

### M2 の結果（2026-10-21）

Vivado サーバで、移植先（`hw/bits/sam45-wide/`、66523e8）の `make sim-wpfb sim-wch sim-wsp sim-wco sim-ws45 sim-wds` を回し（27 本、≒ 20 分）、study-rfsoc の proj023 の作業ツリーに残っている同じ変種の出力と比べた:

- **27 本とも「結果: 全部通過」**。陽性対照 10 本（wpfb-p・wpfb-nm・wch-p・wch-skew・wsp-pa・wsp-pg・wsp-stlp・wco-p・ws45-p・wds-p）は落ちるべきところで落ちた（wds-p は D_S +1）
- **`build-sim-logs/*.log` の 27 個がバイト単位で同じ**（ログにパスが入らない書き方なので、Fine の M2 と違って読み替えも要らない）
- **`build-sim-w*/` の出力 151 個のうち 124 個がバイト単位で同じ**。違う 27 個は iverilog のコンパイル物 `tb` だけで、**パス（`src/common/` ↔ `../../common/`・`src/` の写しと hex）と、コンパイルごとに変わる番地（`0x…` のポインタ）を読み替えると 27 個とも同じ**（中の設計は同じ）
- 比べの相手について: 移植元の出力は proj023-m0 を回し直したものではなく、proj023 の作業ツリーに残っていた最後の実行（sim-wpfb 10-14・wch 10-15・wsp・wco・ws45 10-16・wds 10-17）。その後に変わったのは照合の道具 `check_wide.py`（wpfb・wch の後）と Makefile（ほかの目標）だけで、RTL と試験台は変わっていない（git の履歴で確かめた）。移植先は proj023-m0 の照合の道具で回して同じ出力なので、比べは成り立つ

### M3 の結果（2026-10-22）

Vivado サーバで、移植先（b87dab3）を `make IMPL=Performance_Explore`（`build-PE/`、OOC から書き出しまで ≒ 2 時間）で作り、study-rfsoc の proj023 の `build-PE/`（移植元の bit）と比べた。**予言どおり、構成データまで移植元と同じ**:

| 項目 | 移植先 | 移植元 |
|---|---|---|
| FDRI（`sw/pynq/bitinfo.py`） | 8,608,824 語・sha256 `abc66e72…4d4736` | **同じ** |
| 構成の流れ全体（欄 e）の sha256 | `f5cd867f…4dbffb` | **同じ** |
| `.bit` のファイルの sha256 | `216b36ed…a43a4f` | `473911e5…3c5178`。違うのはヘッダの日付と時刻の 7 バイトだけ |
| `.hwh` | `b9b98a47…ff245f` | `32759af1…bf769a`。違う 6 行は作った時刻 1 行と、ROM の中身の絶対パス（COEF_FILE 1・TW_FILE 4）だけ |
| `-1` の WNS / WHS | **+0.000716 ns / +0.009500 ns** | 同じ（小数 6 桁まで） |
| USR_ACCESS | なし（焼いていない。M5 で） | なし |

- **報告 15 個が、日付などの行を除いて同じ**: utilization（全体・階層）・cdc・net_check（結線の照合）・ROM 2 種・lane_fft・raw_core・timing・clock_interaction・address_map・xfft_params・rfdc_params・clocks。違ったのは drc.rpt の 2 行だけで、RTSTAT-10（ロードの無いネット 46 本、件数は同じ）が「最初の 15 本」を挙げるときの並びが 1 本入れ替わったもの
- build.tcl の照合: ROM の中身（OOC の run 5 個で $readmemh の失敗 0）・ドライバの無いネット（自作のセル 20 個で Synth 8-3848 0）・coef_q 1,185 / 1,152 / 1,152 / 1,152・tw_q 576 × 4・CRITICAL WARNING 5 件（移植元も 5 件）
- 移植元の作業ツリーも同じサーバの上にあるので、比べは同じ Vivado・同じボードのファイルで行った

### M4 の手順と予言（2026-10-22、実機の前）

**載せるもの**（ボードの新しいディレクトリ `~/sam45-wide-m4/`。study-rfsoc の proj023 の道具のディレクトリとは混ぜない）:
- 移植先の `hw/bits/sam45-wide/build-PE/` の `proj023.bit`・`proj023.hwh`（M3 で構成データが移植元と同じ。ID は変えていないので名前も proj023 のまま）
- `sw/pynq-wide/` の `*.py`・`*.json`・`*.sh`（移植元の proj023 の `pynq/` とバイト単位で同じ）
- `bits.json`: proj023 の 1 件だけ（`"kind": "wide"`）、`sha256` に移植先の bit の値（`216b36ed0273f70c9628f218e791d93828f290c3a0656d952ff3afd847a43a4f`）

| 判定 | 道具 | 合格 |
|---|---|---|
| ID・自己記述 | `wide.py --list` | IF_ID 0x02010101・PROJ 0x00230100・time_core 0x02010102・NSTREAM 3/2/2/2・CAPS 3・NCH 4096・FRAME_BEATS 2048・FFT_N 15 |
| 起動の見張り | `wide.py --list` の表の後 | 4 コアとも FLAGS 0x00 → 0x00、待たされた 1・待ち行列 2 語、IP の位相 入口 8・出口 155 |
| 雑音の 7 本 | `wide.py --mode A=1,B=2,C=4,D=1 --s0 A0=0,A1=12288,B0=0,B1=4096,D1=6000 --nacc 1250 --ndump 3` | 結果: 全部通過、FLAGS 0 |
| V2-b の短縮 | specd `--wide`（proj023 4d と同じ設定: A B 1・B B 2・C B 4・D B 1・SHIFT 7・tint 40.96 ms・float32） | **300 s**。CRC・欠け・kgap・tdev 0、STATUS の miss・bdrop・pl_drop 0、bund_r は 7 本とも 1,048,576（2·G） |

**予言**: 構成データも PS も移植元とバイト単位で同じなので、4 つとも proj023 の 10-17 の値（上の「合格」の欄）と同じになる。外れるとしたら置き場所（ボードのディレクトリ・bits.json・hwh の名前の組）か、その日の配線・クロック。外れたら同じ日に移植元の proj023 のディレクトリでも同じ判定を回し、どちらに付いた外れかを分ける

### M4 の結果（2026-10-22）: 合格

ボードの `~/sam45-wide-m4/`（M3 の bit `216b36ed…`、`sw/pynq-wide/`）で回した。

**配線**: 始めは P（1PPS を ADC にも分配、F-2 の配線）のまま回し、雑音の 7 本の最大の ch が帯域の端（IF 4096.0・3072.0 MHz）に出たので、N に戻して回し直した（ノイズソース → BPF → 分配器 → ADC、SG は出力 OFF、1PPS・10 MHz は PPS・CLK の入口へ LPF あり）。下の値は N のもの。ID と起動の見張りは P と N で同じだった

| 判定 | 結果 | 10-17 の proj023 |
|---|---|---|
| ID・自己記述 | IF_ID・PROJ・time_core・NSTREAM 3/2/2/2・CAPS 3・BASE_BEATS・BUILD・SID・NCH・FRAME_BEATS・PARAM・NFFT_MIN_MAX・S0_CUR・FFT_N 15 | **同じ** |
| 起動の見張り | 4 コアとも 0x00 → 0x00・待たされた 1・待ち行列 2・IP の位相 入口 8・出口 155・遅れ 147（P と N の 2 回の起動とも） | **同じ** |
| 雑音の 7 本 | 結果: 全部通過、FLAGS・SAT 0、IF の範囲は式どおり。B1（B 2）と C0（B 4）が同じ線を 2670.94・2670.81 MHz に出した | 同じ形（10-17 は 2072.69・2072.81 MHz の線。雑音の中の最大の線は日で変わる） |
| V2-b（300 s、specd `--wide`） | 受け側: SPEC 52,213・TP 29,837・859 MB、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0、health・flags・sat 0、版 2 だけ。STATUS: miss・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost・drop 0、**bund_r は 7 本とも 1,048,576（2·G）**、loop_slow 0・loop_max 22.51 ms・loop_p99 7.3 ms・**pl_peak 694,656 B**、time_ok 1・forced 0 | 同じ（loop_max 22.5・loop_p99 6.9・pl_peak 694,656 B） |

- **予言との違い（判定の外）**:
  - 入力の電力 tp_dbfs −31.3〜−31.5 dBFS（10-17 は −12.5）。配線 N の中の減衰が 10-17 と違うと見ている（H-1 で入れた PATT・分配器・減衰器が入ったままの見込み。確かめていない）。sat 0 で、判定には効かない
  - TP_JUMP 82 回（ADC ごとに 26・23・20・13）。**全部が START から 264.8〜269.3 s の 4.5 s に、4 ADC そろって**、大きさ 0.012〜0.015 dB（σ 0.002 dB）。4 ADC で同時なので分光計ではなく入力の側（10-17 の V2-b の 2 回、−0.019 dB と同じ型。今回は短い間に続いた）。原因は確かめていない
- **起こし方の誤り（PS の不具合）**: 初めは手順の誤りで `--wide` を付けずに specd を起こし、Fine の取得で起動して止まった（`ERROR: --ns は 4 ADC × 0 窓`）。bits.json の `"kind": "wide"` が効かない不具合（M5 の項目に入れた）。10-17 と同じく `--wide` を付けて起こし直した
- 記録は制御 PC の `~/m2/m4w_v2b.json`・`m4w_v2b_status.txt`（`.s45` は 900 MB、照合が済んだので消してよい）

### 一本化（cmul.v・rec_fr.v）の手順と予言（2026-10-22、回す前）

**変えたもの**: `hw/common/cmul.v`・`rec_fr.v` を proj023 の版（= M1〜M4 の Wide の写し）に替え、写しを消し、Wide の Makefile・build.tcl（7 行）を `../../common/` に向けた。違いは口を足しただけ:
- `cmul.v`: パラメータ SH（既定 16）。丸めと右シフトの 16 を SH に
- `rec_fr.v`: パラメータ W7HI（既定 0）と入力 `w7hi`。語 7 の上位 32 bit を `W7HI ? w7hi[…] : 0` に（今までは 64 bit の定数 32768 の上位で 0）。Fine のセルは `w7hi` を繋がない

**合格**（4 つとも。1 つでも外れたら一本化しない）:
1. **Fine の sim**: `hw/bits/sam45-fine` で `make sim-all sim-ring` を、一本化の前（`sam45-wide/makefile-trim`）と後の 2 つの木で回し、出力がバイト単位で同じ（コンパイル物はパスと番地の読み替えで）。陽性対照が立つ
2. **Wide の sim**: `make sim-all` が 28 個とも通過し、sim のログ 27 個が M2 と同じ
3. **Fine のビルド**: 既定の戦略で作り直し、**FDRI が v1.0.0 と同じ**（`e095fa97…29f9`、hw/bits/sam45-fine/README の表）
4. **Wide のビルド**: `IMPL=Performance_Explore` で作り直し、**FDRI が M3 と同じ**（`abc66e72…4d4736`）

**予言**: 4 つとも同じ。既定のパラメータでは式が同じなので、合成は同じネットリストを作る。外れるとしたら、Fine の `rec_fr` に繋がない入力 `w7hi` が増えたことで、合成が名前・順番の違う部品を作り、配置のタイブレークが動くこと（式は同じでも FDRI が違いうる。proj023 の知見「定数や名前の変更だけで配置が動く」）。そのときは sim は 1・2 で通り、3・4 だけが外れる

### M3 の心配（M3 の前に書いた）

移植元の WNS は +0.0007 ns で、作り直して閉じる保証は無い（proj023 の凍結の決め）。置き場所が変わるだけで配置のタイブレークが動けば負に落ちうる。
Fine の M3 は「ディレクトリだけ違う」作り直しで構成データまで同じになったので、Wide も同じになる見込みが高い。**負に落ちたら RTL も制約も直さずに止め、どうするかを決め直す**（直すと移植ではなくなる）。

### M5（Fine のときと違い、配置に触れない）

Fine の M5b は「RTL は変えず、ビルドで USR_ACCESS に焼き、PS が .bit から読む」形にした（migration.md の M5b）。Wide も同じ形にすれば **FDRI は M3 と同じ**で、タイミングの詰め直しは要らない。M5 でするのは:
- Makefile・build.tcl に Fine の M5b のフック（`USR_ACCESS` を作って焼く・`bitinfo.py` で読み返す）を写す
- `sw/pynq-wide/` を `sw/pynq/` に一本化する: s45core・s45acq・specd・timebase・test_fake.sh は proj023 と Fine の両方が変えているので、中身のマージになる（s45core の既定は今は Wide。bit の BIT_KIND で選ぶ形に）
- **specd の `load_bits()` が bits.json の `"kind"` を捨てる**のを直す（proj023 の README は「bits.json の項目なら `"kind": "wide"`」と書いているが実装されていない。M4 で `--wide` を付けずに起こし、Fine の取得で起動して止まった）。直したら、bits.json だけで Wide が起動することと、`kind` の無い項目が今までどおり Fine で起動することの両方を見る
- 較正の鍵を (BIT_KIND, BIT_REV) = (1, 1) に。timebase の CAL に F-2 の値を入れる: **pps_det_ns ≒ 71.5**・**adc_to_core_ns = A 143.0・B 142.9・C 141.5・D 141.4**（proj026 の (b) の形、proj023 F-2）
- BIT_REV は 1 のまま（Fine の「BIT_REV 3 のまま」と同じ考え）

## SAM45-Fine の M7 との関係（2026-10-21 に決めた）

- 作業ツリーを分ける: Wide は Vivado サーバの `~/git/YATSUGATAKE-wide`（別の clone）で、ブランチ `sam45-wide/*`
- **M7 が書いている文書には、M7 がマージされるまで触らない**: `docs/spec/`（`bits.md` の Wide の行は D-7 の前の「レーン FFT の長さ切り替え」のまま。`interface.md` の D-7 の分）・`docs/design/`・`docs/user/`・`release.md`・`migration.md`。Wide の計画はこの別の文書に書く
- 共有のファイルの一本化（上の 2・3）は Fine の v1.0.0 のタグの後
- Vivado サーバ: Wide の M2（2 コアで 1 時間ほど）・M3（数時間）は、M7 のビルドと重ねない
