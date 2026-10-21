# study-rfsoc からの移植計画（SAM45-Wide）

- 状態: **M1**（2026-10-21、ブランチ `sam45-wide/m1-place`）。次は M2（sim を全部回す）
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

1. **Makefile から Fine の目標を外す**: proj023 の Makefile には proj021 から引き継いだ Fine の目標（sim-win・sim-ddc・sim-spec-all・sim-ring など、`sim-all` も Fine の 3 つを回す）が残っている。M1 では移さないファイルを指して動かないので、外して `sim-all` を Wide の sim に替える。外した後に M2 をもう一度
2. **`cmul.v`・`rec_fr.v` を `hw/common/` に一本化**（Fine の v1.0.0 のタグの後）: proj023 の版で `hw/common/` を替え、Wide の写しを消す。合格は、Fine の sim（sim-ring・sim-raw を含む）の回帰と、**Fine を作り直して FDRI が M5b の bit と同じ**こと（既定では同じ式なので同じはず。違えば一本化しない）
3. **`sw/pynq-wide/` を `sw/pynq/` に一本化** → Wide の M5 で行う（下）

## 手順

| 手順 | Wide ですること | 合格 |
|---|---|---|
| M0 | 置き場所の表（この文書と付録） | 全ファイルに行き先がある（**済み 2026-10-21**） |
| M1 | 表の行き先に置き、パスだけを直す | `git diff --stat` で中身の変更がパスの行だけ。在ってはいけない側の照合（上）（**2026-10-21**: 下の「M1 の結果」） |
| M2 | sim を全部回す（sim-wpfb 3・wch 6・wsp 9・wco 4・ws45 3・wds 2、model-wide） | proj023 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ |
| M3 | ビルド（`-1`、**Performance_Explore**） | **FDRI が移植元と同じ**（Fine の M3 は構成データまで同じだった）。WNS は移植元と小数 6 桁まで同じ |
| M4 | 実機の短い回帰 | ID（`wide.py --list`）・起動の見張り（FLAGS 0・IP の位相）・雑音の 7 本・V2-b（5 分）が proj023 と同じ値 |
| M5 | Fine の M5a・M5b を Wide に当て、`sw/pynq-wide/` を `sw/pynq/` に一本化 | 下の「M5」 |
| M6 | Wide の判定を `test/acceptance/sam45-wide/` に書き、全部通し、性能評価を書く | `docs/performance/sam45-wide/<版>.md` |
| M7 | spec・design・user の Wide の分を書き、リリース | `release.md` |

### M1 の結果（2026-10-21、ea3409c・7b3512c）

- **置く**（ea3409c）: 付録の 83 個を `git show study-rfsoc@proj023-m0:proj023/…` から取り出して置いた。置いた 83 個と既にある 16 個は、移植元と**バイト単位で同じ**（全部を照合）
- **パスの直し**（7b3512c）: 6 個・106 行（Makefile 63・build.tcl 35・ほか 8）。**違う行はすべてパスの行**: 古い行と新しい行からパスの部分を消して比べ、106 行とも一致（陽性対照: パス以外を 1 文字変えた行は不一致になる）。`sw/pynq-wide/`・`model/` は直していない（移植元のまま）
- **在ってはいけない側**: Wide の Makefile・build.tcl が `hw/common/cmul.v`・`rec_fr.v` を指す行は 0（直す前の版に当てると 2・22 行を拾う = 照合が働いている）。build.tcl が読むファイル（コメントの行を除く）はすべて在る。Wide の sim の目標（WPFB・WCH・WSP・WCO・WDS・WS45）の RTL もすべて在る
- **動かして確かめたこと**（作業用の環境。iverilog と Vivado は使っていない）: `make model-wide`（check_wide.py の自己検査、模型を `../../../model/` から読む）が全部通過。`tools/gen_wide_coef.py`・`gen_wide_tw.py` の出力が `src/wide_coef.hex`・`wide_tw.hex` とバイト単位で同じ。Tcl 10 個が `info complete` で完結、`sw/pynq-wide/` の 44 個が `py_compile` を通る
- **動かないままにしたもの**: Makefile の Fine の目標（sim-win・sim-ddc・sim-spec-all・sim-ring など、`sim-all` も）は、移していないファイル（Fine の試験台・`src/sam45fine/pfb4_rom.v` など）を指すので動かない。外すのは M1 の後の別の PR（「M1 の後にすること」の 1）

### M3 の心配

移植元の WNS は +0.0007 ns で、作り直して閉じる保証は無い（proj023 の凍結の決め）。置き場所が変わるだけで配置のタイブレークが動けば負に落ちうる。
Fine の M3 は「ディレクトリだけ違う」作り直しで構成データまで同じになったので、Wide も同じになる見込みが高い。**負に落ちたら RTL も制約も直さずに止め、どうするかを決め直す**（直すと移植ではなくなる）。

### M5（Fine のときと違い、配置に触れない）

Fine の M5b は「RTL は変えず、ビルドで USR_ACCESS に焼き、PS が .bit から読む」形にした（migration.md の M5b）。Wide も同じ形にすれば **FDRI は M3 と同じ**で、タイミングの詰め直しは要らない。M5 でするのは:
- Makefile・build.tcl に Fine の M5b のフック（`USR_ACCESS` を作って焼く・`bitinfo.py` で読み返す）を写す
- `sw/pynq-wide/` を `sw/pynq/` に一本化する: s45core・s45acq・specd・timebase・test_fake.sh は proj023 と Fine の両方が変えているので、中身のマージになる（s45core の既定は今は Wide。bit の BIT_KIND で選ぶ形に）
- 較正の鍵を (BIT_KIND, BIT_REV) = (1, 1) に。timebase の CAL に F-2 の値を入れる: **pps_det_ns ≒ 71.5**・**adc_to_core_ns = A 143.0・B 142.9・C 141.5・D 141.4**（proj026 の (b) の形、proj023 F-2）
- BIT_REV は 1 のまま（Fine の「BIT_REV 3 のまま」と同じ考え）

## SAM45-Fine の M7 との関係（2026-10-21 に決めた）

- 作業ツリーを分ける: Wide は Vivado サーバの `~/git/YATSUGATAKE-wide`（別の clone）で、ブランチ `sam45-wide/*`
- **M7 が書いている文書には、M7 がマージされるまで触らない**: `docs/spec/`（`bits.md` の Wide の行は D-7 の前の「レーン FFT の長さ切り替え」のまま。`interface.md` の D-7 の分）・`docs/design/`・`docs/user/`・`release.md`・`migration.md`。Wide の計画はこの別の文書に書く
- 共有のファイルの一本化（上の 2・3）は Fine の v1.0.0 のタグの後
- Vivado サーバ: Wide の M2（2 コアで 1 時間ほど）・M3（数時間）は、M7 のビルドと重ねない
