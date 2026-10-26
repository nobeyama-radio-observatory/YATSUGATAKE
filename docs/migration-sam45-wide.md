# study-rfsoc からの移植計画（SAM45-Wide）

- 状態: **M5 済み**（2026-10-23、ブランチ `sam45-wide/m5`）。Wide の焼き直し・Wide と Fine の実機の回帰とも予言どおり（下の「M5 の手順と予言」）。Wide の LMX の出力の強さを Fine と同じ PWR 3 にした（下の「M5 の後」）。**M6 の判定を書いた**（下の「M6」、実機はこれから）
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
2. **`cmul.v`・`rec_fr.v` を `hw/common/` に一本化**（ブランチ `sam45-wide/common-unify`、**2026-10-23 に済み**。下の「一本化の手順と予言」「一本化の結果」）: proj023 の版で `hw/common/` を替え、Wide の写しを消す。合格は、Fine の sim（sim-ring・sim-raw を含む）の回帰と、**Fine を作り直して FDRI が M5b の bit と同じ**こと（既定では同じ式なので同じはず。違えば一本化しない）
3. **`sw/pynq-wide/` を `sw/pynq/` に一本化** → Wide の M5 で行う（下）

## 手順

| 手順 | Wide ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録） | 全ファイルに行き先がある（**済み 2026-10-21**） |
| M1 | 表の行き先に置き、パスだけを直す | `git diff --stat` で中身の変更がパスの行だけ。在ってはいけない側の照合（上）（**2026-10-21**: 下の「M1 の結果」） |
| M2 | sim を全部回す（sim-wpfb 3・wch 6・wsp 9・wco 4・ws45 3・wds 2、model-wide） | proj023 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**済み 2026-10-21**: 下の「M2 の結果」） |
| M3 | ビルド（`-1`、**Performance_Explore**） | **FDRI が移植元と同じ**（Fine の M3 は構成データまで同じだった）。WNS は移植元と小数 6 桁まで同じ（**済み 2026-10-22**: 下の「M3 の結果」） |
| M4 | 実機の短い回帰 | ID（`wide.py --list`）・起動の見張り（FLAGS 0・IP の位相）・雑音の 7 本・V2-b（5 分）が proj023 と同じ値（**済み 2026-10-22**: 下の「M4 の結果」） |
| M5 | Fine の M5a・M5b を Wide に当て、`sw/pynq-wide/` を `sw/pynq/` に一本化 | 下の「M5」（**済み 2026-10-23**: 「M5 の手順と予言」の結果） |
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

### 一本化（cmul.v・rec_fr.v）の結果（2026-10-23）: 合格、予言どおり

Vivado サーバで、一本化の後（c56caf6）と前（main の 927bfc9 を別の木に出したもの）を回した。

1. **Fine の sim**（`make sim-all sim-ring`、2 つの木で同時に）: 出力 399 個のうち **347 個がバイト単位で同じ**。違う 52 個はすべて iverilog のコンパイル物（`tb*`）で、31 個はパス（木の名前）と番地（`0x…`）の読み替えで同じ、21 個は読み替えても違う。**21 個はどれも `cmul` か `rec_fr` を含むもの**（RTL の文が変わったので、コンパイル物が変わるのは当然）。sim の出力（ダンプ・照合のログ・結果の行）は全部同じで、`build-sim-logs` の 9 個は全部「結果: 全部通過」、sim-ring は「総合: 通過」。陽性対照は前と同じ件数で落ちた（time の check1 の 6 件・wstamp-posctl の 8 件など。Fine の M2 と同じ）
2. **Wide の sim**（`make sim-all`）: 28 個とも通過、sim のログ 27 個が M2（= 移植元）とバイト単位で同じ
3. **Fine の作り直し**（既定の戦略・`JOBS=8`）: **FDRI `e095fa97…29f9` が v1.0.0 と同じ**。WNS / WHS +0.044057 / +0.009766 ns（M3・M5b と同じ）。USR_ACCESS は c56caf6（汚れなし）。utilization・cdc・timing・net_check が M7 の作業ツリーの v1.0.0 の build と日付の行を除いて同じ。`JOBS=8` でも FDRI が変わらないことも確かめた
4. **Wide の作り直し**（`IMPL=Performance_Explore JOBS=8`）: `impl_1` は配置・配線・`write_bitstream` まで完走（配線後 WNS 0.001・WHS 0.010 ns）し、**その bit の FDRI `abc66e72…4d4736` と構成の流れの sha256 が M3 と同じ**。ただし build.tcl が報告のために配線後の設計を開き直すところ（`open_run impl_1`）で **Vivado が segfault** した（空きメモリ 91 GB、ネットリストを組む途中。proj023 で配線後の dcp を開いて落ちたのと同じ型）。そのため build.tcl の後半の報告（timing・資源・CDC・`build-PE/` の直下の bit と hwh）は出ていない。構成データがビットまで同じなので、出ていない報告も M3 と同じと見る。落ちる前の照合（結線・番地・RFDC の設定・ROM の中身・ドライバの無いネット）は M3 と同じだった

### M5 の手順と予言（2026-10-23）

**PS の一本化**（`sw/pynq-wide/` を消し、`sw/pynq/` に入れた）。proj021-m0 を土台に、Fine（M1 の後の変更）と Wide（proj023）の両側を比べて分けた:

| 分け | ファイル | 扱い |
|---|---|---|
| 同じ | acqboot・extref・instr・rectap・s45allan・s45pn・s45proto・s45resp・s45ring・s45snap・s45snapplot・s45spur・s45tastar・s45v2a・s45v2c・s45v2f・specctl・test_cal_b・test_tpjump・tpjump・window・bits.example.json | そのまま（bits.example.json に Wide の例を 1 件足した） |
| Fine だけ変えた | s45cal・s45lin・test_regmap・timetest・tp_cal.json | Fine のまま |
| Wide だけ変えた | s45client（v2 の df_hz で IF の軸）・specrecv（SLICE のフレーム 2048 ビート）・sg（unleveled なら止める） | Wide の版に。**sg.py の変更は Fine にも効く**: SG の出力が unleveled（E8257D は 3.94 GHz で −10 dBm 以下）なら止まる。Fine の手順で低いレベルを使うなら SG の出口に固定減衰器 |
| | plring・spectrometer | Wide の変更は既定の bit の名前（proj023.bit）だけなので、Fine のまま（Wide の道具は自分で bit を渡す） |
| 両方変えた | s45acq・s45core・specd・test_fake.sh・timebase | 3 方向のマージ。衝突 4 か所（コメント 2・timebase の CAL の表・time_core の ID の一覧）は Fine の形に Wide の分を足した |
| Wide だけ | wide・wide_v2・widef2・wideresp・h2peek・sgstat | 足した。gbboot は Fine と同じく移さない（Wide の手順も使っていない） |
| Fine だけ | bitinfo | そのまま（Wide も使う） |

足した直し:
- **s45core**: 既定（`discover()` の BIT_KIND・BIT_REV の下限・`--bitfile`）は Fine のまま（proj023 は既定を Wide にしていた）。Wide の道具は `bit_kind=1, bit_rev_min=1` を渡す（proj023 のまま）。`--list` はどちらの bit も読む（BIT_KIND ごとの下限 {1: 1, 2: 2}）
- **specd**: `load_bits()` が bits.json の `kind` を捨てていたのを直した（M4 で踏んだ）。`test_fake.sh widekind` を足した: `kind: wide` だけで Wide の取得が起き、`kind` の無い項目へ LOAD すると Fine に戻る。**直す前の specd ではこの試験が NG になる**（陽性対照）
- **s45acq**: Wide の取得の ID にも `usr`（M5b の USR_ACCESS）
- **timebase**: CAL に **(1, 1)**: pps_det_ns 71.5・adc_to_core_ns A 143.0・B 142.9・C 141.5・D 141.4・bound_ns 5（proj023 の F-2、(2, 3) と同じ形 (b)）。time_core の ID の一覧に 0x0201_0102

作業用の環境で通したもの: `test_fake.sh all` **17 試験とも通過**（Fine 13・Wide 4）・`wide.py --selftest`・`wide_v2.py --selftest`・`test_cal_b.py`・`test_tpjump.py`・`py_compile`、Fine の sim-regmap の regs.txt（一本化の結果のときの Fine の sim の出力）に当てた `test_regmap.py` が 78 項目で全部通過

**M5b のフック**: Fine の Makefile・build.tcl（4c35583・8eba348）の USR_ACCESS の部分を、そのまま Wide に写した（Makefile 13 行・build.tcl 22 行）。RTL・制約・配置には触れない

**残り（予言）**:
1. **Wide の焼き直し**（`make IMPL=Performance_Explore`）: USR_ACCESS に commit が焼かれ、`bitinfo.py` の読み返しが通る。**FDRI は M3 と同じ**（`abc66e72…`）。BIT_REV は 1 のまま（release.md: 同じ RTL の作り直し）
2. **実機（Wide、一本化した `sw/pynq/`）**: `wide.py --list`（M4 と同じ値）、specd を **`--wide` なしで bits.json の `kind` だけで**起こし、V2-b 300 s（M4 と同じ）。START の EVENT の `ids.usr` が 1 の commit、錨の較正が (1, 1) で「未較正」でない
3. **実機（Fine、同じ `sw/pynq/`）**: PS が変わったので短い回帰（ID-1・`s45core --list`・V2-b 300 s）。Fine の M4 と同じ値

**焼き直しの結果**（2026-10-23、ba456e1 で `make IMPL=Performance_Explore`、`build-PE/`）: **予言 1 は当たった**
- `bitinfo.py`: USR_ACCESS `0xba456e10` = commit ba456e1（汚れなし・書き込み 1 回）、`--expect` の照合が通過
- **FDRI 8,608,824 語・sha256 `abc66e72…4d4736` が M3 と同じ**。構成の流れ（欄 e）の sha256 は `80c0e5be…3f922d91` で M3（`f5cd867f…`）と違うが、USR_ACCESS を焼いたぶんの違い（FDRI の外）
- WNS / WHS **+0.000716 / +0.009500 ns**（M3 と小数 6 桁まで同じ）。BIT_REV 1・BUILD_TAG も同じ
- 報告 15 個を study-rfsoc の proj023 の `build-PE/`（移植元）と比べ、日付などの行を除いて 14 個が同じ。drc.rpt の 2 行は M3 と同じ RTSTAT-10 の並びの入れ替わり。run の CRITICAL WARNING はなし（移植元も同じ）
- `impl_1` の 1 回目は、run の中で設計を開くところ（OOC の dcp を繋ぐ途中）で **Vivado が segfault**（`hs_err_pid255457.log`、10:00）。build.tcl の回し直し（1 回目）で完走した。common-unify の作り直しで落ちたのと同じ型（ネットリストを組む途中）。今回は build.tcl の後半の報告まで出た

**実機の結果（Wide、2026-10-23）**: ボードの `~/sam45-wide-m5/`（今回の bit `54b0dbea…`・一本化した `sw/pynq/`・bits.json の既定は `sam45-wide`、`"kind": "wide"`）、配線 N。**予言 2 は当たった**
- `wide.py --list`: IF_ID 0x02010101 × 4・PROJ 0x00230100・time_core 0x02010102・NSTREAM 3/2/2/2・CAPS 0x003・NCH 4096・FRAME_BEATS 2048・FFT_N 15（効いている・書いた・物理とも）、起動の見張りは 4 コアとも 0x00 → 0x00・待たされた 1・待ち行列 2・入口 8・出口 155・遅れ 147。**M4 と同じ**
- specd を **`--wide` なし**（`--clkin 0 --ref 10 --bits bits.json`）で起こし、**bits.json の `kind` だけで Wide の取得が起きた**（リング「Wide: SLICE 8 本」、ID の `kind: wide`）。M4 で踏んだ不具合が直った
- START の EVENT の `ids.usr` = **ba456e10**（`ID` の `usr` も同じ）
- 錨: `[acq] 錨: UTC … （EPOCH 1）`、START は force なしで通り `time_ok=1`・`forced=0`。timebase は (BIT_KIND, BIT_REV) の CAL が無いと錨の前に例外で止まるので、**(1, 1) の CAL が効いている**
- `GET CAL` は `cal=none`（「bit が違う（較正 [(2, 3)]・載っている (1, 1)）」）。これは **TP の dBm の較正（tp_cal.json）** で、Wide の tp_cal は M6 で足す予定どおり（錨の較正とは別。手順を書いたときに取り違えた）
- V2-b 300 s（`SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7`）: 受け側 SPEC 51,191・TP 29,253・842 MB、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0、health・flags・sat 0、版 2 だけ。STATUS: miss・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost・drop 0、**bund_r は 7 本とも 1,048,576**、loop_slow 0・loop_max 22.15 ms・loop_p99 7.3 ms・pl_peak 464,384 B、time_ok 1・forced 0。M4 と同じ（pl_peak は M4 の 694,656 B より小さい。溜まりの山の高さで、判定の外）
- 判定の外: TP_JUMP 189 回（ADC ごとに 50・49・50・40）。**4 ADC そろって 220〜230 s に 114 回・280〜290 s に 63 回**の固まり（ほかは 120 s 台 6・230〜270 s 6）、大きさ 0.012〜0.039 dB（σ 0.002 dB）・ovr なし。M4 の固まり（264.8〜269.3 s に 82 回、0.012〜0.015 dB）と同じ型で、入力の側と見る。tp_dbfs −31.3〜−31.5 dBFS も M4 と同じ
- 起こし方の誤り（手順の誤り）: 初めは `sudo python3 specd.py` で起こし、システムの python3 に pynq が無く止まった（`ModuleNotFoundError: No module named 'pynq'`）。`sudo -E $(which python3)` で起こし直した。**`docs/user/specd.md` の起こし方が同じ書き方**（ほかの判定の文書は「root で `python3`」）。この PR で `sudo -E $(which python3)` に直した。`sw/pynq/` の spectrometer・window・extref の docstring にも `sudo python3` が残るが、実機で確かめた PS を変えないため、ここでは直さない
- 記録: 制御 PC（ビルドサーバ）の `~/m2/m5/m5w_id.txt`・`m5w_v2b.json`・`m5w_v2b_status.txt`、ボードの `~/sam45-wide-m5/w_list.txt`・`specd_wide.log`（`.s45` は 883 MB、照合が済んだので消してよい）
- **LOAD で Fine に戻る**（実機、2026-10-23）: Wide の specd に `LOAD bit=proj021`（bits.json の `kind` の無い項目）→ 21.5 s で載り、`ID` が win 02030000・adc 02020301・time 02020302・`usr=c56caf60`、`GET CAL` が tp_cal (2, 3)（A −69.231・B −69.356・C −69.415・D −69.343）。`test_fake.sh widekind` の後半を実機でも見た（`~/m2/m5/m5f_load.txt`）。`version` は specd の版なので proj023-0.1 のまま
- **見つけたこと（M5 の外）: Wide の取得は LMX2594 の出力の強さを出荷時の 31 のままにする**。Fine の取得は specd の `--lmx-pwr`（既定 3、proj019 で櫛 n×163.84 MHz の和が −5.7 dB）を書くが、Wide のバックエンド（`s45acq.py` の Wide の `open()`）は `--lmx-pwr` を見ず、ID の `lmx_pwr` も "31" の固定。proj023 から引き継いだ振る舞い（M1〜M4 の PS は proj023 とバイト単位で同じ）で、M4・M5 の Wide の値は 31 のもの。LOAD の後の `ID` で `lmx_pwr` が 31 → 3 に変わって気づいた。合わせるとスペクトルが変わるので、一本化（M5）では直さず、M6 の前に決める

**実機の結果（Fine、同じ `sw/pynq/`、2026-10-23）**: ボードの `~/sam45-wide-m5/` で specd を `--bit proj021`（c56caf6 の作り直し、FDRI は v1.0.0 と同じ）で起こし直した。配線 N のまま。**予言 3 は当たった**
- ID-1（`s45core --list`）: bit SAM45-Fine（BIT_KIND 2）rev 3・PROJ 0x00210200、4 コアとも 0x02020301・NSTREAM 3/2/2/2・CAPS 0x007、time_core 0x02020302、RAW の流れ SID 0x02040200・NCH 0・FRAME_BEATS 512・PARAM 0x0d、窓の流れは各コア 2 本（DDC・NCH 4096・FRAME_BEATS 4096）。`USR_ACCESS（proj021.bit）: c56caf60 = commit c56caf6（汚れなし）`。Fine の M5b の実機と同じ（USR_ACCESS だけ c56caf6 の作り直しの値）
- specd の ID: win 02030000・adc 02020301・time 02020302・`usr=c56caf60`・lmx_pwr 3。`GET CAL` は tp_cal (2, 3)
- V2-b 300 s（`SET tint=0.01024 fmt=f32 A0.bw=256 A1.bw=8 all.shift=9`）: 受け側 SPEC 234,033・TP 27,992・3.7 GB、CRC・欠け・説明のない欠け・逆戻り・重複・kgap・tdev・tp_gap 0、health・flags・sat 0、版 2 だけ。START の EVENT の `ids.usr` = `c56caf60`・proj 00210200・tp_cal (2, 3)。STATUS: miss・kgap・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost・drop 0、time_ok 1・forced 0、**loop_p99 19.3 ms**（Fine の M5b の実機 19.2 ms）・loop_max 28.35 ms・loop_slow 14,322（10.24 ms では毎周越えるのが普通、V2-b の判定）・pl_peak 1,056,512 B、bund_r 524,426 / 525,742 の交互（V2-a の r = 524,426 と同じ形）。**Fine の M5b の実機と同じ**
- 判定の外: tp_dbfs −31.27〜−31.43（tp_dbm −25.26〜−25.53）。M5b の −12.4 との差は Wide の M4 と同じ配線 N の中の減衰。TP_JUMP 133 回（42・29・33・29）、4 ADC そろって 150〜170 s に 90 回の固まりほか、−0.022〜+0.053 dB。同じ日の Wide と同じ型（入力の側）
- 記録: `~/m2/m5/m5f_id.txt`・`m5f_v2b.json`・`m5f_v2b_status.txt`（`.s45` は 3.9 GB、照合が済んだので消してよい）、ボードの `f_list.txt`・`specd_fine.log`

### M5 の後: LMX の出力の強さを Fine と合わせる（2026-10-23、手順と予言。ブランチ `sam45-wide/lmx-pwr`）

**決めたこと**: Wide の取得と Wide の道具も、LMX2594 の出力の強さを Fine と同じ **PWR 3** にする（M5 の実機で見つけた）。M6 の判定と Wide の tp_cal を測る前に替える。

**比べたこと**（proj019 の記録から）:
- 櫛 n × 163.84 MHz は LMX の出力 491.52 MHz（タイルの基準）の経路から出る。bit ではなくボードの性質で、**12 本（n = 13〜24）とも Wide の帯域の中**
- PWR 31 → 3 で櫛の和 −5.7 dB（一番強い 3768.32 は −4.8 dB、PWR 10 で最小になる癖）。ロック・位相雑音（差 0.2 dB 以内）・無入力の床は PWR 0 まで変わらない
- 31 のままだと、LOAD で Fine ⇄ Wide を替えるたびにクロックの状態が変わる（同じ日の Fine と Wide のデータで櫛の強さが違う）
- 31 を残す利点は今までの記録（proj023 の判定・M4・M5、F-2 の (1, 1)）と続くことだけ。下げる側の副作用は見つかっていない
- **2G も同じ**: study-rfsoc の proj025 の G21・G22 のバックエンドは WideBackend を写していて 31。ここで決めた値を study-rfsoc 側にも当てる

**変えたもの**（PS だけ。ビルドは要らない）:
- `s45acq.py`: LMX を書く部分を HwBackend の `_setup_lmx()`・`_lmx_ids()` にまとめ、Fine と Wide の両方で呼ぶ（ずれの原因は WideBackend の写し漏れなので、写さずに共有する）。Fine の動きは変わらない（同じ行を関数に移しただけ）。ID の `lmx_pwr` は Wide でも実際の値
- `wide.py` の `open_board()` と `wide.py`・`wide_v2.py`・`widef2.py`・`wideresp.py`: `--lmx-pwr`（既定 3、specd と同じ）。`--lmx-pwr 31` で出荷時と同じ強さを書く
- `widecomb.py`（新）: 櫛の 12 本の E（超過の電力、s45spur と同じ量）を .s45 どうしで比べる（Fine の `s45spur.py` は Wide の SLICE の軸を読まない）
- 手元で: `test_fake.sh all` 全部通過・`wide.py` / `wide_v2.py` / `widecomb.py --selftest` 通過。`widecomb.py` は M5 の Wide の V2-b（PWR 31）で櫛を拾えた（ADC_B の 3768.4 MHz で r 0.13・2293.7 MHz で 0.10）。偽の裏は LMX を書かないので、`_setup_lmx()` を通るのは実機だけ

**手順と予言**（実機。1・2 は配線 N のまま、3 は配線 P）:
1. **櫛**: specd を `--lmx-pwr 31` → 既定（3）→ 31 → 3 と交互に 4 回起こし、各回 `SET tint=0.04096 fmt=f32 all.b=4 all.shift=7` で 120 s 受ける（B 4 なら流れ 0 が 2048〜4096 MHz の全部で、4 ADC とも 12 本が入る）。`widecomb.py --pair` で 2 組を比べる。
   **予言**: 4 ADC の櫛の和の E が 2 組とも **−4〜−8 dB**（proj019 の −5.7 dB）。強い線（2785.28・3440.64・2293.76・2949.12・2457.6）は下がる。2621.44・3604.48 は下がらない（別の経路）。3768.32 は下がり方が小さい（PWR 10 で最小）。ID の `lmx_pwr` が 31 / 3 で替わる。外れたら、同じ日に Fine（`--bit proj021`）でも 31 / 3 を取り、bit に付く違いかを分ける
2. **回帰**: 既定（3）で V2-b 300 s（M5 と同じ設定）。**予言**: M5 と同じ（CRC・欠け・kgap・tdev・miss・bdrop・pl_drop 0、bund_r 7 本とも 1,048,576、time_ok 1）。Fine も `--bit proj021` で起こし、ID の `lmx_pwr=3`（Fine の動きは変わらない）
3. **時刻の較正**（配線 P）: `widef2.py --lmx-pwr 31` と `--lmx-pwr 3`（既定）を交互に 2 回ずつ（ケーブルの入れ替えなし。差だけを見る）。**予言**: adc_to_core の差が 4 ADC とも **1 ビート以内**（2 回の差の線と同じ）。ADC の遅れはクロックの数で決まり、基準の強さで動くのは ps 級のはず。外れたら (1, 1) の CAL を PWR 3 で測り直す（ケーブルを入れ替えた 2 回）

**1 の結果（2026-10-23、配線 N、c1 31 → c2 3 → c3 31 → c4 3、各 120 s）: 予言は外れた**（向きは合っていて、量が足りない）
- 4 回とも受け側の CRC・欠け・kgap・tdev・sat 0、STATUS の miss・bdrop・pl_drop 0・time_ok 1。ID の `lmx_pwr` は 31・3・31・3（**Wide の裏が LMX を書き直した**）。tp_dbfs は 4 回で ±0.03 dB（入力の電力は PWR で変わらない）
- **4 ADC の櫛の和: −2.3 dB・−2.2 dB**（予言 −4〜−8 dB）。2 組がよくそろっていて、測りは再現している
- 外れの中身:
  - **n = 13 は櫛ではなかった**: 拾った山は 2130.81 MHz（櫛の 2129.92 から 0.9 MHz ずれ）で、4 ADC とも同じ大きさ（E ≒ 3,600〜4,100・r ≒ 0.011）で、PWR で動かない。±4 ch にわたって r が +0.003〜+0.011 と続く幅のある形で、配線 N の BPF の通過域の肩（2060 MHz で床の 0.28 倍 → 2130 MHz で 1.3 倍）を床の推定が拾ったもの。和の 1/4 を占めて和を薄めていた。**n = 13 を除くと −3.4 dB・−3.4 dB**（それでも予言の外）
  - **ADC ごとに違う**（n = 13 を除く）: 櫛の強い B・D は **−5.4・−4.1 / −4.7・−5.0 dB**（予言の範囲。proj019 の −5.7 dB に近い）、櫛の弱い A・C は −1.5・−0.8 / −0.9・−1.0 dB。A・C は PWR 31 でも線が弱く（r ≦ 0.03）、和が PWR で動かない形（3931〜3932・3440 の幅のある山など）に占められている
  - 強い線は下がる: 2293.8 は 4 ADC とも −5〜−10 dB、3276.8 は −6〜−13 dB、B・D の 2785.3 は −5〜−6.5 dB、**B・D の 3768.3 は −5.5〜−7.9 dB**（予言「下がり方が小さい」は外れ。proj019 の 31 → 3 の −4.8 dB とは合う。「PWR 10 で最小」は 3 と 10 の比べで、31 → 3 の比べに持ち込んだのが誤り）
  - **2621.3・3604.3 は上がる**（+0.5〜+3.8 dB、予言どおり。proj019 も +3 dB）。PWR 3 で一番強い線は D の 3604.3（r 0.034）か 3932.3（0.033）
  - **r の最大**: PWR 31 は B の 3768.3 で 0.106・0.100 → PWR 3 は 0.034・0.033（約 1/3）
- 予言の立て方の誤り: proj019 の −5.7 dB は「線ごとに一番強い ADC」の和（表の ADC の欄）で、ここでは 4 ADC の全部の線の和にした。櫛の弱い ADC と、櫛でない形が混ざる分だけ薄まる。比べるなら proj019 と同じ数え方で予言を書くべきだった
- 道具の限り（`widecomb.py`）: 帯域の肩や幅のある形を線として拾う。結果を見た後に「幅のある山を和から外す」判定を試したが、櫛の線（B の 3440.8・D の 2457.8 など）まで組によって外れたので採らなかった（結果を見てから基準を足して和を予言に寄せることになる）。直すなら、無入力（配線の BPF なし）で取り直すのが筋
- **結論は変えない（PWR 3 にする）**: 下がる側の線は 5〜13 dB 下がり、r の最大は約 1/3。上がるのは 2621・3604 の 2 本（+2〜4 dB）だけで、proj019 と同じ。Fine と同じ強さにする理由（bit で状態を替えない・M6 の前）も残る
- 記録: 制御 PC の `~/m2/lmx/c{1..4}_*`（.s45 は 1 本 ≒ 200 MB）

**2 の結果（2026-10-23、配線 N）: 予言どおり**
- Wide（PWR 3、既定）: ID `lmx_pwr=3`・`usr=ba456e10`、START の EVENT の ids も `lmx_pwr: 3`。V2-b 300 s（M5 と同じ設定）: 受け側 SPEC 51,191・TP 29,253・842 MB、CRC・欠け・説明のない欠け・kgap・tdev・tp_gap・sat 0、版 2 だけ。STATUS: miss・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost・drop 0、**bund_r は 7 本とも 1,048,576**、time_ok 1・forced 0、loop_max 22.64 ms・loop_p99 7.2 ms・loop_slow 0・pl_peak 694,656 B。**M5（SPEC 51,191）・M4 と同じ**。tp_dbfs −31.33〜−31.50（M5 と ±0.02 dB）
- Fine（`--bit proj021`）: ID `adc_id=02020301`・`usr=c56caf60`・**`lmx_pwr=3`**、`GET CAL` は (2, 3)。LMX を書く部分を共有の関数にした後も Fine は同じ
- 判定の外: TP_JUMP 6 回（1・4・1・0）。M5 の 189 回・Fine の 133 回より少ない（入力の側の揺れの日内の違い。PWR とは結び付けない）
- 記録: `~/m2/lmx/l2w_*`・`l2f_id.txt`

**3 の結果（2026-10-23、配線 P、`widef2.py` を 31 → 3 → 31 → 3、各 4 ADC × 5 試行）: 予言どおり**
- 4 回ともログの LMX の強さが名前どおり（`widef2` の `--lmx-pwr` が効いた）。縁は 4 ADC × 5 試行とも見え（最大 / σ 59〜81）、陽性対照（p）は全部見えない（3.4〜5.6）。1 回の中の σ 0.03〜0.19 ビート（≦ 0.4）
- 縁の位置の平均 [ビート]: A 31 は 17.36・17.69 / 3 は 17.58・17.41、B 18.35・17.79 / 17.53・17.36、C 17.78・18.10 / 17.43・17.33、D 17.80・18.11 / 17.50・17.39
- **差（3 − 31）: A −0.03・B −0.62・C −0.56・D −0.51 ビート。4 ADC とも 1 ビート以内**
- ただし B・C・D は 3 でそろって ≒ 0.5 ビート（≒ 2 ns）小さい。同じ PWR 31 の 2 回の差（0.33〜0.56 ビート）と同じ程度なので、各 2 回では本当のずれかを分けられない（PWR 3 の 2 回の差は 0.10〜0.21 ビートと小さい）。bound_ns 5 の内なので **(1, 1) の CAL は替えない**。M6 の F-2 を PWR 3 でケーブルの入れ替えありで回し、CAL を決める（M6 で回す判定なので、その結果で替える）
- 記録: `~/m2/lmx/f2_*`（ボードの `~/sam45-wide-lmx/` にも）

**まとめ**: 予言 1（櫛の量）は外れ（向きは合う）、2（回帰）・3（時刻の較正）は当たった。Wide の取得と Wide の道具は PWR 3 で動き、Fine と同じになった。**2G（study-rfsoc の proj025・027 の G21・G22 の裏）は 31 のまま**で、こちらの決めを当てるのは study-rfsoc 側の作業

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

## M6 判定を全部通し、最初の性能評価を書く（2026-10-23、測る前）

**対象**: main の PS（`sw/pynq/`、M5 の一本化 ＋ #39 ＋ PWR 3、d795a14 以降）と M5 の bit（`proj023.bit` `54b0dbea…`、USR_ACCESS `ba456e10`、FDRI は M3・移植元と同じ）。ボードの `~/sam45-wide-m6/`、制御 PC の `~/m2/m6w/`。
**判定**: [`test/acceptance/sam45-wide/`](../test/acceptance/sam45-wide/README.md) の 14 本（2026-10-23 に proj023 の README から書き起こした。合格は proj023 の判定の線、値は今の配線 N（≒ −31.4 dBFS）と PWR 3 に合わせた）

### 決めたこと

1. **main の PS の実機の確認は済み**（2026-10-23、`~/m2/m6w/smoke_*`）: ID に `usr=ba456e10`・`lmx_pwr=3`、30 s の受けで欠け・CRC・kgap・miss・pl_drop 0、SHUTDOWN の後に `psm_*` を残さない（残っていた `psm_00473e0f` は 04:32 UTC、#39 の前の PS の Fine の回の残り）。そのときの配線は P のままで、tp_dbfs −59〜−61 dBFS（判定の外）
2. **F-2 は PWR 3 で測った M を (1, 1) の CAL に入れ直す**（±2.5 ns の内でも）。LMX の強さを替えた後の最初の測りのため。「M5 の後」で B・C・D が ≒ 0.5 ビート小さく出た件はここで決まる
3. **Wide の tp_cal は P-8 で決める**（Fine の (2, 3) と同じ形: 同じ日の Fine の bit と dBFS − PM の差 ≦ 0.07 dB なら `bits` に [1, 1] を足す）。足すのは PS のデータの変更なので、別の PR
4. **判定に無い性能の項目は「測り」**（合否なし、予言は書く）:
   - **A（安定度）**: 配線 N、V2-b と同じ 7 本・tint 40.96 ms で 1 時間受け、`s45allan.py --no-plot`（このサーバに matplotlib が無い）。**`s45allan` を直した**: 流れの帯域を Fine の式（512 / 2^ns）で出していて、Wide の B 2・B 4 を 1/4・1/16 に読んでいた。v2 の記録の df_hz を使う（Fine の記録は同じ値）。M5 の V2-b（300 s）で ch ごとの揺れが B 1・2・4 で予言の 1.04・1.09・1.13 倍
   - **V（スプリアス）**: A の記録で `widecomb.py`（櫛 n × 163.84 MHz）。`s45spur.py rec` は周波数の軸が Fine の窓の式で Wide を読まない（使わない）
   - R（流れの平坦さ）は回さない（ch の形は H-1、Wide には窓の肩が無い）
5. **道具の確かめ（PC、実機の前）**: `s45lin` は `all.b=2` で Wide の流れを読める（`all.b=4` では acquire が空の流れを待って止まる。P-8 の手順は B 2 で書いた）

### 回す順（配線ごとの塊）

宛先は環境変数 `B`・`SG`（Wide の道具は `RFSOC_SG` も）・`PM`・`ATT`。**どの塊の前にも `pgrep -af specd` でほかの specd が動いていないことを確かめる**。

| 塊 | 配線 | 動かし方 | 中身 | 長さの目安 |
|---|---|---|---|---|
| N1 | N | ボード直 | ID-1・H-0・H-4・V2-a・V2-e・V2-f（陽性対照つき ＋ Overlay 3 回） | ≒ 15 分 |
| N2 | N | specd | S・V2-d・V2-b（30 分）・V2-b の陽性対照（specd を起こし直す） | ≒ 45 分 |
| N3 | N ＋ PM・ATT | specd | PS-3・P-8（Wide と Fine）・tp_cal の決め・A（1 時間） | ≒ 1 時間 40 分 |
| NS | NS（SG ON） | ボード直 | H-1（`--warm 300`）・H-2（B 1・2・4） | ≒ 20 分 |
| P | P | ボード直 | F-2（2 回、ケーブルを入れ替えて） | ≒ 15 分 |

- 配線の付け替えは N → NS → P の順（NS は SG の出力を ON にするだけ）。**今は P のまま**（2026-10-23 の smoke）なので、まず N に戻す
- V2-b の `.s45` は ≒ 5 GB、A は ≒ 10 GB。制御 PC の空き 296 GB
- specd の SET は起こし直すまで残る。V2-d は LOAD ごとに SET を明示する

### 予言

1. **N1**: すべて proj023 の値（各判定の「記録」）。ID-1 の起動の見張り 0x00 → 0x00・入口 8・出口 155、V2-f の r = 1,048,576 が 4 回の Overlay で同じ、V2-a は 10 組とも全 ch 一致
2. **N2**: S の電力が V2-b の tp_dbfs と ±0.2 dB（≒ −31.4）。V2-d の LOAD ≦ 30 s・usr が ba456e10 ↔ c56caf60。**SLICE と DDC が混ざった記録の照合は初めて**で、落ちるなら受け側の道具の限り。V2-b は SPEC ≒ 307,600・欠け 0・bund_r 2·G・loop_slow 0
3. **N3**: PS-3 の step_db ∓0.94 ± 0.03。P-8 の Wide と Fine の `c` の差 ≦ 0.07 dB（TP の作りが同じなので）、L-1 ≦ 0.05 dB・L-2 ±0.02 dB。A は ch ごとが 1 / (Δν·τ) に沿う（M5 の 300 s で 1.04〜1.13 倍）
4. **NS**: H-1 は proj023 の 2 回目と同じ値（C0 の半 ch の両側の差 ≒ 0.036 dB も出る。PWR 3 で変わるとは見ていない）。H-2 は 3 つの B で ±0.1 ch
5. **P**: 縁の位置は「M5 の後」の PWR 3 の値（17.3〜17.6 ビート）と ±0.4 ビート、2 回の差 ≦ 1 ビート。M は今の CAL から −2〜0 ns（B・C・D が小さい側）で ±2.5 ns の内

### 書くもの

- 判定ごとに、この節の下に「M6 の結果」を足す（判定の ID・合格の条件・測った値）
- 判定のファイルの「記録」に、製品の bit で通った日と記録の名前を 1 行足す
- 全部が通ったら `docs/performance/sam45-wide/<版>.md`（版の名前は M7 で決める。それまでは「案」）

### M6 の結果: 塊 N1（2026-10-23、配線 N、ボード直、`~/m2/m6w/n1/`）: 予言 1 当たり、6 判定とも通過

| 判定 | 結果 |
|---|---|
| ID-1 | IF_ID 0x0201_0101 × 4・time_core 0x0201_0102・PROJ 0x0023_0100・NSTREAM 3/2/2/2・CAPS 0x003・BASE_BEATS 2,621,440・BUILD 0x50c0000i、SLICE 8 本・RAW（SID 0x0204_0200）、FFT_N 15・15・15。起動の見張り 4 コアとも 0x00 → 0x00・待たされた 1・待ち行列 2・入口 8・出口 155・遅れ 147。ログに LMX を PWR 3（OUTA・OUTB 31 → 3）で書いた行 |
| H-0 | 結果: 全部通過。7 本とも SEQ 1〜3・SAT 0・FLAGS 0x0、IF の範囲は式どおり。B1（B 2）と C0（B 4）が同じ線を 2669.69・2666.31 MHz に、A0・D0 が 3590.125 MHz に |
| H-4 | 30 回の切り替えで NG 0 件 |
| V2-a | 4 ADC とも 10 組が全 ch 一致（一致しない ch 0・欠け 0）、陽性対照 10/10 で不一致、2 本の流れの F0 753152 |
| V2-e | 4 ADC とも TP のレコード 304 個・照らした 509〜511 個で不一致 0・SEQ の飛び 0・DUMP_T の式の外れ 0・CRC 0 |
| V2-f | 7 本・2 RUN × 4 回の Overlay（陽性対照の回を含む）で r = 1,048,576、陽性対照の RUN は 7 本とも 1,572,864（3·G）で「違う」と言った |

- 道具を 9 回起こし（Overlay 9 回）、9 回とも起動の見張り 0x00 → 0x00・IP の位相 入口 8・出口 155（proj023 の Overlay 5 回・M4・M5 と同じ）。FIN − FOUT は 0 か 1（表示の時点の差）
- すべて PWR 3。proj023（PWR 31）の値と変わらない（PL の中の判定なので、変わる理由も無い）

### M6 の結果: 塊 N2（2026-10-23、配線 N、specd、`~/m2/m6w/n2/`）: 予言 2 当たり、4 判定とも通過（陽性対照 3 つも）

| 判定 | 結果 |
|---|---|
| S | 4 ADC とも 16 塊・間隔 True/True・UTC の刻み 20,000,000 ns・振り切れ 0、−31.43・−31.52・−31.37・−31.25 dBFS（同じ日の V2-b の tp_dbfs −31.42・−31.52・−31.38・−31.26 と 0.01 dB 内）、尖度 2.49〜2.51・DC −0.05〜+0.68 LSB。SNAP 64・CRC・欠け 0。**陽性対照**: ARMED の間の SNAP は `ERR STATE ARMED の間は SNAP できない` |
| V2-d | LOAD 20.6・20.3 s。usr ba456e10 → c56caf60 → ba456e10、adc_id 02010101 → 02020301 → 02010101、Fine のとき `GET CAL` が (2, 3)、どこでも `lmx_pwr=3`・time_ok 1。3 回の START とも「n に達した」・miss 0・TP の anch_dev 0・gap 0。受け側 **SPEC 1,100**（Wide 350 ＋ Fine 400 ＋ Wide 350）・版 2 だけ・CRC・欠け・dup・kgap・tdev・tp_gap 0・**照合 通過**（SLICE と DDC が 1 本の記録に混ざっても通った。予言の心配は外れた）。**陽性対照**: sha256 を 1 文字変えた bits.json で `LOAD bit=proj021` → `ERR LOAD proj021 の sha256 が bits.json と違う`、ID は Wide のまま |
| V2-b | 30 分: SPEC **307,538**（予言 ≒ 307,600）・TP 175,737・5.06 GB、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap・health・flags・sat 0、版 2 だけ、照合 通過。STATUS: miss・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost・drop 0、**bund_r 7 本とも 1,048,576**・C1 は「-」、time_ok 1・forced 0、loop_slow 0・loop_max 21.77 ms・loop_p99 6.9 ms・pl_peak 694,656 B。START の EVENT の ids に `kind: wide`・`usr: ba456e10`・`lmx_pwr: 3` |
| V2-b の陽性対照 | `--posctl-ring-stall 8`、40 s: 受け側 **kgap 7・tdev 0**・tp_gap 4・CRC 0（照合は「失敗」= 期待どおり）。STATUS: bdrop 13・pl_drop 7,243・pl_peak 33,554,176 B（リングが満ちた）・**r_bad 0・bund_r 7 本とも 2·G のまま**。BDROP 13（proj023 は 8。止まりの前後の束の数で、リングが満ちた位置による） |

- 判定の外: V2-b の TP_JUMP 285 回（83・72・71・59）。入力の側の型（M5 と同じ）。PS-3 の判定は step_db で数える
- 予言との違い: V2-d の「混ざりで落ちるかもしれない」は外れて通った（受け側は記録ごとに kind を読む）
- N2 で specd を 3 回止めた（V2-b・陽性対照・sha256 違い）後、ボードの `/dev/shm` は空（#39 の直しが Wide の実機でも効いた）

### M6 の結果: 塊 N3（2026-10-23、配線 N ＋ PM・ATT、specd、`~/m2/m6w/n3/`）: 予言 3 当たり、P-8・PS-3 通過。測り A は予言どおり、測り V は予言 2 が外れ

| 判定 | 結果 |
|---|---|
| P-8（Wide） | `lin_w`、TP が −18〜−28 dBFS の 10 段（PATT 0〜8）: L-1 最大 0.010〜0.014 dB（TP 4 本・流れ 8 本）・L-2 最大 0.0008〜0.0018 dB。dBFS − PM（analyze）−0.85・−0.95・−0.82・−0.73 dB |
| P-8（Fine、proj021 usr c56caf60） | `lin_f`、同じ範囲: L-1 最大 0.009〜0.014 dB・L-2 最大 0.0012〜0.0140 dB（D1）。dBFS − PM −0.81・−0.89・−0.77・−0.68 dB |
| tp_cal の決め | 差 0.04〜0.06 dB（−18〜−28 dBFS の段だけの平均でも 0.046〜0.063）で 4 本とも ≦ 0.07 → `bits` に [1, 1]（PR #46、K は測り直していない）。ボードに置いて specd を起こし直し、`GET CAL` bits=2,3,1,1・STATUS の `tp_dbm` が 4 本とも数 |
| PS-3 | 4 ADC とも跳ね 2 回、step_db −0.9395〜−0.9410 / +0.9379〜+0.9388・ovr false、tp_jump 2,2,2,2、受け側の照合 通過 |
| A（測り） | `a.s45`、V2-b と同じ 7 本・40.96 ms・`START n=87890`（3600 s）: 受け側 SPEC 616,658・CRC・欠け・kgap・tdev・tp_gap・sat 0・照合 通過、STATUS miss・bdrop・pl_drop 0・loop_slow 0・loop_p99 6.8 ms・tp_jump 7,2,3,2。`s45allan`: **(b) ch ごとが最短の τ で予言の B 1 1.00〜1.02・B 2 1.09・B 4 1.13 倍**（M5 の 300 s の 1.04・1.09・1.13 と同じ）、予言の 2 倍を越える τ 102〜205 s。(c) 共通利得を除くと 1.00〜1.12 倍・512 s〜（1024 s まで越えない流れが 3 本）。(a) 帯域 0.84〜1.51 倍・(d) 下/上 1.10〜1.46 倍。TP 4 本は予言（B = 1800 MHz）の 0.34〜0.36 倍（記録だけ。migration.md の (t) と同じ型: 入力のノイズソースがガウスでない） |
| V（測り） | `widecomb.py ~/m2/lmx/l2w_v2b.s45 a.s45`（「M5 の後」の V2-b 300 s、同じ設定・PWR 3 → A）。予言は回す前に `n3/v_predict.txt` に書いた。**4 ADC の櫛の和 1.269e4 → 1.257e4（−0.0 dB）**、ADC ごと A 0.0・B −1.2・C +0.2・D −0.0 dB（B は 2457.7 の線が r 0.021 → 0.004 で −7.0 dB）。r の最大は D の 3768.4 で 0.084（前 0.038）、ほか D の 3932.1 0.046〜0.064・3604.5 0.025〜0.054 |

- 4 ADC とも Wide の c が Fine より同じ向きに 0.04〜0.06 dB 低い。2 つの測りの間 11 分の PM・入力の漂いと区別できない（記録だけ）
- s45lin 自身の OK/NG は −45 dBm までの全段で見ていて、判定ファイルの範囲と違う（記録だけ。範囲を絞った計算は `n3/l1range.py`）
- 最初の P-8 の失敗した試み（Fine を lin_w の名前で測ったもの等）は `n3/bad/` に寄せ、判定に使っていない
- **予言との違い（V）**: 1（4 ADC の櫛の和 ±1 dB）は当たり。**2（r ≦ 0.04）は外れ**（D の 3768.4 で 0.084）。予言の 0.034 は「M5 の後」の c2・c4（B 4、ch 500 kHz）の r で、ここの D0 は B 1（ch 125 kHz）。狭い線の r は ch が細いほど大きく出るので、ch の幅の違う記録の r を持ち込んだのが予言の誤り（ch の幅に依らない E で書くべきだった）。D の 3768.4 は E でも 266 → 648（+3.9 dB）で、同じ PWR 3 の 2 回の間で動いている。3（2621・3604 の線が前後とも出る）は「出ている」の量を決めていなかった: 3604 は 4 ADC とも r > 0（0.0002〜0.025）、2621 は流れが覆う B・C だけで B は r 0.0001（床に近い）。判定できないとして残す
- 記録の混ざり: `a.s45` の頭に PS-3 の RUN の終わり（STOP の EVENT で dumps 3016、ps3.s45 が受けたのはその手前まで）が ≒ 204 ダンプ入っていた。PS-3 の受けが閉じてから STOP までに溜まった分を、specd が次の受け側に送った。`s45allan` は DUMP_K の連続の一番長い区間だけを使うので A の RUN だけ（87,890 ダンプ）。`widecomb` は全部を平均するが、同じ設定・同じ PATT の 0.2 % なので櫛の比には効かない。次からは受けを閉じる前に STOP する
- 予言との違い: PS-3 で入力の側の小さな跳ねが 0 回（N2 の V2-b では 30 分で 285 回）。日と時間帯で出方が変わる型で、判定は step_db で数えるので影響しない

### M6 の結果: 塊 NS（2026-10-23、配線 NS、ボード直、`~/m2/m6w/ns/`）: H-2 通過、H-1 は失敗（C0 の半 ch が線の 0.001 dB 外）

| 判定 | 結果 |
|---|---|
| H-2 | B 1・2・4 とも最大の ch 1234・ずれ +0.000 ch・中心の IF が式どおり、境目の比 +0.00・+0.01・+0.04 dB。**予言 4 当たり**。CW / 中央値 21.9・13.9・**10.3** dB（境目 18.9・11.0・**7.6**）で、B 4 は線（10・7）の 0.3〜0.6 dB 上しか余裕が無い（proj023 の 10-17 は 25.0・20.5・16.1、分配器を替える前） |
| H-1 `h1` | ノイズ ON・PATT 13（判定ファイルの前提のまま）: 繰り返しの揺れ 0.036〜0.041 dB・C0 −3.055 で NG |
| H-1 `h1n` | ノイズ OFF・PATT 0（改めた前提、proj023 の合格回 h1b と同じ）: 揺れ 0.002〜0.011 dB、半 ch・幅・ENBW は h1b と ±0.003 dB。**C0 の下側 −3.031（線 −3.030）で NG** |
| H-1 `h1r` | 対照（ノイズ ON・PATT 13、SG ≒ 50 分 ON）: 揺れ 0.021〜0.034 dB で NG に戻った |

- **H-1 の前提の誤り**: 判定ファイルに「ノイズは入ったまま（P_off を引いて消す）」と書いたが、proj023 の合格回はノイズソース OFF・PATT 0（CW / 床 62〜69 dB）だった。P_off で消えるのは雑音の平均だけで、CW × 雑音の交差項 2·Re(C N*) の揺れが残る（相対の σ ≒ √(2 (N/C) / (Δν τ)) ≒ 0.011 dB、B に依らない）。CW と雑音は分配器 A の後で同じ経路を通るので、4 ADC で同じ形に出る。1 回目の後、h1rep.py で 4 本の相関 0.96〜0.99・予言 σ 0.0107 と測った σ 0.0114〜0.0133 を確かめ、**測る前に**前提を改めた（線は変えない）
- **見立ての取り違えとその検証**: 1 回目の直後は「SG の温まり（寒い日、何時間も OFF の後に 300 s）」と見立てた。交差項に気づいて取り下げ、h1r（SG を長く温め、ノイズだけ戻す）で分けた: 揺れが戻ったので交差項が正しく、温まりは外れ。最初に「SG の電力は足りている」と答えたのは、雑音の電力の揺れ（≒ 0.001 dB）だけを数えて交差項を落とした誤り
- **C0（B 4）の半 ch の非対称**: h1n で 0.040 dB（proj023 h1b 0.036）。揺れの小さい測りで同じ値が出るので測りの乱れではない。B 1 0.009・B 2 0.016・B 4 0.040 と B とともに増える。周波数のずれ（u のずれ）なら B に依らない形になるはずで、それとも合わない。原因は未解明。**2026-10-26 の解析（測った後、未検証）**: 両側の差は |u| ≦ 0.5 で u に比例し（直線からの残り ≦ 0.003 dB）、周波数に直すと 4 本とも −0.06〜−0.08 dB/MHz（h1b も −0.05〜−0.07）で B に依らない。B とともに増えるのは束ねた ch の幅（Hz）が B に比例するためで、束ねる前の入力のスペクトルの傾きと合う（「模型の束ね方と実機の違い」の見立ては取り下げる）。−0.07 dB/MHz は全体の傾きとしては急で、定在波の局所の傾きを疑うが確かめていない
- **H-1 の扱いは保留**（2026-10-26、実験者の判断）: h1n は proj023 の h1b を ±0.003 dB で再現し、足りないのは 0.001 dB で実用上は問題ない。記録の判定（失敗）と線は変えない。確かめるなら、配線 N の記録の IF 3000 MHz 付近の雑音の傾き・PM での SG の ±5 MHz の掃引・別の IF での H-1（どれも予言を先に書く）
- 予言 4 の H-1（proj023 と同じ値、C0 の差 ≒ 0.036 も出る）は、値は当たり、判定（通過）は外れ: proj023 は線の 0.002 dB 内、今日は 0.001 dB 外
- 配線の表（README）の誤り: BPF は ノイズソース → BPF → 分配器 A で、SG は BPF を通らない（実験者が確かめた）
- 記録: `h1*.h1.npz`・`h1*.log`・`h2_b*.log`・`h1rep.py`・`h1_retry_predict.txt`（予言と改めを時刻つきで）

## SAM45-Fine の M7 との関係（2026-10-21 に決めた）

- 作業ツリーを分ける: Wide は Vivado サーバの `~/git/YATSUGATAKE-wide`（別の clone）で、ブランチ `sam45-wide/*`
- **M7 が書いている文書には、M7 がマージされるまで触らない**: `docs/spec/`（`bits.md` の Wide の行は D-7 の前の「レーン FFT の長さ切り替え」のまま。`interface.md` の D-7 の分）・`docs/design/`・`docs/user/`・`release.md`・`migration.md`。Wide の計画はこの別の文書に書く
- 共有のファイルの一本化（上の 2・3）は Fine の v1.0.0 のタグの後
- Vivado サーバ: Wide の M2（2 コアで 1 時間ほど）・M3（数時間）は、M7 のビルドと重ねない
