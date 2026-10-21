# study-rfsoc からの移植計画

- 状態: **M2 済み**（2026-10-14）。次は M3（ビルドして移植元の bit と比べる）
- 決定: [ADR 0002](decisions/0002-migrate-from-proj021-restructure-only.md)（proj021 を土台にし、構成替えだけを行う）

## 原則

1. **変更は一度に一つ。** 移植の PR は「ファイルを置き直す」だけにする。ID・係数・機能・制約を同時に変えない
2. **同じものができたことを、数えて確かめる。** 目で見て「同じはず」で済ませない
3. **study-rfsoc の proj021 は書き換えない。** 移植の後に見つかった問題は、YATSUGATAKE で issue にする

## 始める条件

- [x] proj021 の判定（手順 0・1a・1b・2 の V2-a〜V2-g・F-2）が通り、README に結論が書かれている（2026-10-14。最終の bit は手順 2-5、21 判定とも通過）
- [x] proj021 の手順 1a で、ソースが `src/common/`・`src/sam45fine/`・`src/board/` に分かれている
- [x] proj021 の判定が `test/acceptance/` の書き方（6 項目）で書かれている（study-rfsoc の `proj021/test/acceptance/`、21 判定）
- [x] study-rfsoc の proj021 が push 済みで、移植元の commit を 1 つに決めた → **移植元: `study-rfsoc@proj021-m0`**（注釈つきタグ、commit 7be50ac）

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj021 README「移植元を決める」の節の写し。

| 項目 | 値 |
|---|---|
| bit の sha256 | `a99b7a96b14b51deb8738bed7bce203ca6c753f4eca5a24227da7193bf0814e8`（34,437,476 B） |
| hwh の sha256 | `613ba1aee43c0882d155b11c107a96054fbfbf0cf05411149543d687a294f54d` |
| ID | BIT_KIND 2・BIT_REV 3・PROJ 0x0021_0200。IF_ID 0x0202_0301（コア 4）・0x0202_0302（time_core）・0x0202_0303（リング） |
| `-1` の WNS / WHS（既定の戦略） | +0.044057 ns / +0.009766 ns |
| LUT / FF | 168,982（39.73 %）/ 256,455（30.15 %） |
| DSP / BRAM タイル / URAM | 2,096 / 233.5 / 56 |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137 |

bit そのものは git に入れない（[ADR 0018](decisions/0018-release-on-github-releases.md) の扱い）

## 置き場所の対応（M0 で確定、2026-10-14）

ファイル 1 つずつの行き先は付録 [`migration-files.md`](migration-files.md)（proj021 の 229 個: 移す 156・移さない 73）。

**M1 は「分けずに置く」**: M1 はパスだけを変える（原則 1）。proj021 の中で import・相対パスで結び付いているものを分けると中身を直すことになるので、M1 では一緒に置き、分けるのは M1 の後の別の PR にする（下の「M1 の後に分けるもの」）。

| study-rfsoc | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| proj021 `src/common/` | `hw/common/` | 全帯域の FFT（`spec_core.v`・`tw_rom.v`）も移す。SAM45-Fine の bit では使わない（build.tcl の `full_kind fft` のときだけ入る）が、SAM45-Wide などの共通部品 |
| proj021 `src/board/`・`clocks/` | `hw/board/`・`hw/board/clocks/` | `ps_preset.tcl`・タイミング制約・1PPS のピン。clocks は出荷時の控え（実行時には読まない） |
| proj021 `src/sam45fine/` | `hw/bits/sam45-fine/src/` | FFT IP の設定・PFB の係数の ROM |
| proj021 `build.tcl`・`Makefile`・`program.tcl` | `hw/bits/sam45-fine/` | `src/`・`model/`・`sw/pynq/` の位置だけを直す |
| proj021 `sim/` | `hw/bits/sam45-fine/sim/` | 陽性対照の変種も全部。共通の tb を `hw/sim/` に出すのは後 |
| proj021 `tools/`（Makefile が使うもの） | `hw/bits/sam45-fine/tools/` | フロアマップ・最悪の経路・CDC・係数とひねり係数の生成・PS のプリセット・OOC の見積もり |
| proj021 `model/` | `model/` | 係数を作る模型（pfb4・win_fixed など）。係数の表と一緒に版を持つ |
| proj021 `pynq/`（specd・取得・受け側・制御・判定と測りの道具・`tp_cal.json`・`bits.example.json`） | `sw/pynq/` | specd が window・timetest・spectrometer・plring・sg まで import し、s45client が s45proto・s45cal を import するので、M1 では 1 か所に置く |
| proj021 `docs/`（ブロック図・フロアマップ・PFB と窓の設計の図） | `docs/design/sam45-fine/` | |
| proj021 `test/acceptance/`（21 判定と一覧） | `test/acceptance/sam45-fine/` | 判定の ID は bit ごとに中身が違いうるので bit のディレクトリに分ける |
| proj017〜021 の README の結果 | `docs/performance/sam45-fine/` の最初の 1 本の材料 | 移植後の .bit で測り直す（M6） |

**M1 では移さない共通の文書**（中身を書き直して移すので M7 で）:

| study-rfsoc | YATSUGATAKE（M7） | 備考 |
|---|---|---|
| `BITS.md` | `docs/spec/bits.md` | 仕様の行に ADR の番号を添える |
| `INTERFACE.md`（v2）・`docs/interface_*.svg`・`docs/interface_figs.py` | `docs/spec/interface.md` と図 | 経緯（「見送った案」）は ADR 0016 に寄せ、spec には今の約束だけを残す |
| `VERSIONS.md` | `docs/spec/hardware.md` ＋ `docs/knowledge/` | 固定値は spec、経緯と落とし穴は knowledge（既に要約済み） |
| `proj001/docs/runbook.md` | `docs/knowledge/environment.md` に足す | ライセンスの節は環境に依る部分を除いて一般化する |

**移さないもの**: proj021 の `README.md`（経緯と結果。M6 の材料として指す）・`runs/` と `pynq/` の中の測定の記録（.json・.jsonl・.png・.npz）・`build*/`・使わなくなった試行の道具
（proj014〜019 の窓の試験 `win*`・`fine`・`lockcheck`・`adcstat`・`resp_explain`・`s45fcheck`・`fcheck.ipynb`、手順 0・1b の `bench_ps`・`gbboot`、全帯域の解析 `tools/tp_*`・`tick_analyze`・`ipround_model`・`allan`）。必要なら study-rfsoc を指す。

**M1 の後に分けるもの**（それぞれ別の PR。分けた後に M2〜M4 の回帰を回す）:
1. `sw/pynq/` → `sw/specd/`・`sw/client/`・`sw/tools/`（import の直し。sw/README.md の予定の形）
2. `hw/bits/sam45-fine/build.tcl` の共通の手続き（照合: part・結線・両側）→ `hw/common/tcl/`
3. `hw/bits/sam45-fine/sim/` の共通の tb → `hw/sim/`
4. 較正（`tp_cal.json`・timebase の CAL）を (BIT_KIND, BIT_REV) ごとの較正ファイルに（`bits.json` が指す）

## 手順

| 手順 | すること | 合格 |
|---|---|---|
| M0 | 移植元の commit を決め、上の表を確定する | 表に「移さない」も含めて全ファイルの行き先がある（**済み 2026-10-14**、付録 migration-files.md） |
| M1 | ファイルを置き直し、パスだけを直す（中身は変えない） | `git diff --stat` で中身の変更がパスの行だけ（**済み 2026-10-14**: 156 個のうち 137 個は移植元と同じ、19 個・107 行はすべてパスの行） |
| M2 | sim を全部回す | proj021 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ（**済み 2026-10-14**: 下の「M2 の結果」） |
| M3 | ビルド（`-1`、proj021 と同じ実装の戦略） | 下の「同一性の判定」（**済み 2026-10-14**: 下の「M3 の結果」。構成データまで移植元と同じ） |
| M4 | 実機で短い回帰 | ID の読み出し・F-1（RUN_T）・W-0・V2-b を短く（5 分）。proj021 と同じ値（**済み 2026-10-15**: 下の「M4 の結果」） |
| M5 | ここで初めて ID を製品の形に変える（別の PR） | [`release.md`](release.md) の手順。変えた後に M2〜M4 をもう一度（**済み 2026-10-17**: M5a・M5b、下の「M5」） |
| M6 | 判定を全部通し、最初の性能評価を書く | `docs/performance/sam45-fine/<版>.md`（設計と予言: 下の「M6」） |
| M7 | spec・design・user を書き、最初のリリース | [`release.md`](release.md) |

## M2 の結果（2026-10-14）

同じサーバで、移植元（`study-rfsoc@proj021-m0` の proj021）と移植先（`hw/bits/sam45-fine/`）をそれぞれ別の worktree に出し、同じ sim を回した:
`make sim-all`（sim-spec-all・sim-win-all・sim-t-all）と `make sim-top sim-win4 sim-wdelay sim-tsys sim-tsys-p sim-ring`。

- **2 つの木の `build-sim-*/` の出力 372 個のうち 362 個がバイト単位で同じ**。違う 10 個は中身の値ではない:
  - `build-sim-logs/*.log` 9 個: make のログにコンパイルの命令の行（RTL のパス）が書かれる。パスを読み替えると 9 個とも同じ
  - `build-sim-time/tb1`: iverilog のコンパイル物（中に絶対パスが入る）
- 結果の行（`check*.log`・`build-sim-logs`）は 2 つの木で全部同じ。通過するべき変種は全部通過し、陽性対照（`-p`・`posctl`・`flip`・`snap-nochk`）は全部落ちるべきところで落ちた（`build-sim-time/check1.log` の「失敗（6 件）」・`build-sim-tsys-posctl` の「失敗（1 件）」は陽性対照で、移植元と同じ件数）

## 同一性の判定（M3）

| 項目 | 合格 | 読み |
|---|---|---|
| sim の出力 | bit 単位で同じ | 自作の論理が同じであることの本命の証拠 |
| CDC の分類ごとの件数 | 同じ | 構造の指紋 |
| LUT・FF・DSP・BRAM・URAM | 同じ | 構造の指紋 |
| .hwh の IP の名前と番地 | 同じ | PS から見た約束が同じ |
| `-1` の WNS / WHS | **閉じていること**。小数 6 桁まで同じなら最良 | ファイルの置き場所や名前が変わると、配置のタイブレークが動いて WNS が変わりうる（WNS は構造の指紋にならない）。違ったら上の 4 つで同一性を言い、`-1` で閉じていることを確かめる |

proj021 の手順 1a（同じリポジトリの中でディレクトリだけ分けた）で WNS が小数 6 桁まで一致したかどうかが、M3 の見込みになる。

## M3 の予言（2026-10-14、ビルドの前）

移植元と移植先で違うのはファイルの置き場所（ディレクトリ）だけ。モジュール名・ファイル名・BD・ID・係数・build.tcl の手続きは同じ（M1 で中身の差はパスの行だけ、M2 で sim の出力がバイト単位で同じ）。同じサーバ・同じ Vivado・既定の戦略で作る。

1. 資源は同じ: LUT 168,982・FF 256,455・DSP 2,096・BRAM 233.5・URAM 56
2. `report_cdc` の分類ごとの件数は同じ: CDC-3 105・CDC-6 5・CDC-15 3,137
3. `.hwh` の IP の名前と番地は同じ
4. run の CRITICAL WARNING の一覧は同じ
5. **`-1` の WNS / WHS は小数 6 桁まで同じ（+0.044057 / +0.009766）**。合成と配置を決めるのは読み込むファイルの中身と順で、ディレクトリの名前は入らないと見る。外れたら「置き場所が配置のタイブレークに効く」証拠として記録し、同一性は 1〜4 で言う（閉じていれば合格）
6. **`.bit` の sha256 は違う**: ヘッダに作った日付と時刻が入るため。**ヘッダを除いた構成データの sha256 は、5 が当たれば同じ**（配置・配線が同じなら構成データも同じ）。5 が外れたら構成データも違う
7. `.hwh` の sha256 は違ってよい（日時が入る）。比べるのは 3

## M3 の結果（2026-10-14）

同じサーバで、移植先（`hw/bits/sam45-fine/`、M1 の先端）を既定の戦略で `make` し、移植元（study-rfsoc の proj021 の `build/`、上の表の bit）と比べた。**予言 1〜7 はすべて当たった。**

| 項目 | 移植元 | 移植先 | |
|---|---|---|---|
| LUT / FF | 168,982 / 256,455 | 168,982 / 256,455 | 同じ |
| DSP / BRAM タイル / URAM | 2,096 / 233.5 / 56 | 2,096 / 233.5 / 56 | 同じ |
| `report_cdc` の分類ごとの件数 | CDC-3 105・CDC-6 5・CDC-15 3,137 | 同左 | `vivado.log` の該当の行の diff が空 |
| `vivado.log` の要点（`TIMING (確定)`・DSP48E2 全体・資源の全体・CRITICAL WARNING） | | | diff が空。**`-1` の WNS / WHS は +0.044057 / +0.009766 ns で小数 6 桁まで同じ** |
| `.hwh` の IP の名前と番地（INSTANCE・BASEVALUE・HIGHVALUE） | | | diff が空 |
| `.bit` の sha256 | `a99b7a96…0814e8` | `4f491488…909eae` | 違う（予言 6: ヘッダの日時。2026/10/14 00:40:18 と 22:10:24） |
| **`.bit` の構成データ（ヘッダの後の 34,437,356 B）の sha256** | `f042da9f83aade017af8efc3fd6f16cd4c21b5cd08c9b3640ae349e721cb8633` | 同左 | **同じ** |
| `.hwh` の sha256 | `613ba1ae…`（上の表） | `8ddd7f42…91bdd504` | 違う（予言 7。比べるのは IP と番地） |

読み:
- **構成データがバイト単位で同じ**なので、移植先の bit は移植元の bit と FPGA の上で同じものになる。置き場所（ディレクトリ）は合成・配置・配線に入らなかった
- 以後、**同じ RTL の作り直しの同一性は「`.bit` のヘッダを除いた構成データの sha256」で言える**（WNS の一致より強い。ヘッダの日時だけが違う）。比べ方: `.bit` のヘッダ（長さ付きの欄 a〜d）を読み飛ばし、欄 e の長さぶんの本体の sha256 を取る
- M4（実機の短い回帰）は、構成データが同じなので移植元の結果がそのまま当てはまる見込み。それでも載せる bit・hwh は移植先の build/ のものを使い、ID と PS 側（`sw/pynq/`）の置き場所が通ることを確かめる

## M4 の手順と予言（2026-10-14、実機の前）

**載せるもの**（ボードの新しいディレクトリ `~/sam45-fine-m4/`。study-rfsoc の proj021 の道具のディレクトリとは混ぜない）:
- 移植先の `hw/bits/sam45-fine/build/` の `proj021.bit`・`proj021.hwh`（M3 で構成データが移植元と同じ。ID は変えていないので名前も proj021 のまま）
- `sw/pynq/` の `*.py` と `tp_cal.json`（33 個すべて study-rfsoc@proj021-m0 の `pynq/` とバイト単位で同じ）
- `bits.json`: proj021 の 1 件だけ、`sha256` に移植先の bit の値（`4f491488…909eae`）。LOAD・起動で specd が照らす

**回すもの**（配線 N、外部 10 MHz と 1PPS。合格は各判定のファイルの条件そのまま）:

| 判定 | 動かし方 | 長さ |
|---|---|---|
| [ID-1](../test/acceptance/sam45-fine/ID-1.md) | ボード直 | — |
| [F-1](../test/acceptance/sam45-fine/F-1.md) | ボード直 | 120 s |
| [W-0](../test/acceptance/sam45-fine/W-0.md) | ボード直（A0 窓 0・D3 窓 1） | ダンプ 3 個 |
| [V2-b](../test/acceptance/sam45-fine/V2-b.md) の短縮 | specd | **300 s**（判定の 1,800 s の代わり） |

**予言**:
1. ID-1: 移植元と同じ値（IF_ID 0x0202_0301 × 4・0x0202_0302・0x0202_0303、RAW の流れ SID 0x0204_0200）
2. F-1: 13 コアとも RUN_T = START_AT ＋ 1、≒ 2,930 ダンプでずれ 0、DUMP_H の印なし
3. W-0: ダンプ 3 個・各 6,250 フレーム、FLAGS 0（[4] を除く）、飽和 0
4. V2-b（300 s）: SPEC ≒ 8 × 29,297 ≒ 234,400、CRC・欠け・説明のない欠け・kgap・tdev・tp_gap 0、STATUS の miss・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost 0
5. bit も PS も移植元とバイト単位で同じなので、**外れるとしたら置き場所（ボードのディレクトリ・bits.json・hwh の名前の組）か、その日の配線・クロック**。外れたら同じ日に移植元の道具のディレクトリで同じ判定を回して比べる

## M4 の結果（2026-10-14〜15）: 合格

移植先の bit（sha256 `4f491488…909eae`、hwh `8ddd7f42…`、ボードで確かめた）と `sw/pynq/` を、ボードの新しいディレクトリに載せて回した。外部 10 MHz と 1PPS、PLL は 2 タイルともロック。**予言 1〜4 は当たり**。

| 判定 | 結果 | 移植元との比べ |
|---|---|---|
| ID-1 | **通過**（10-14）: 4 コアとも IF_ID 0x0202_0301、time_core 0x0202_0302、BIT_KIND 2・rev 3・PROJ 0x0021_0200。RAW の流れ SID 0x0204_0200・NCH 0・FRAME_BEATS 512・PARAM 13。窓の流れは各コア 2 本、FULL なし | 同じ値（予言 1） |
| F-1（120 s） | **通過**（10-14）: 13 コアとも RUN_T = START_AT ＋ 1。9 流れとも 2,930 ダンプで DUMP_T のずれ +0〜+0、健全性の印なし | 同じ（予言 2） |
| W-0 | **通過**（10-14 と、配線 N を確かめた 10-15 の 2 回）: A0 窓 0・D3 窓 1 とも ダンプ 3 個・各 6,250 フレーム、FLAGS 0（WRST の直後の [4] は除く）、飽和 pfb 0・ddc 0 | 同じ（予言 3） |
| V2-b（300 s） | **通過**（10-15、配線 N）: 下の表 | 同じ日に移植元でも回して並べた（予言 4） |

**V2-b（10-15、配線 N、移植先と移植元を続けて）**:

| | 移植先（`sam45-fine-m4`） | 移植元（study-rfsoc の proj021） |
|---|---|---|
| SPEC / TP | 240,115 / 28,878（3.8 GB） | 237,817 / 27,363（3.8 GB） |
| CRC・欠け・説明のない欠け・逆戻り・重複・kgap・tdev・tp_gap | すべて 0、版 2、照合 通過 | すべて 0、版 2、照合 通過 |
| EVENT | START だけ（TP_JUMP なし） | START だけ（TP_JUMP なし） |
| STATUS: miss・kgap・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost | すべて 0（**受け始めて 30 s の STATUS**。終わりの STATUS は残せなかった） | すべて 0（受けの後の STATUS） |
| tp_dbfs / tp_ovr | −12.56・−12.54・−12.50・−12.52 / 0 | −12.54・−12.54・−12.50・−12.50 / 0 |
| tp_jump | 0,0,0,0 | 0,0,0,0 |
| loop_p99 | 25.6 ms（30 s 時点） | 19.0 ms |
| drop | 0（30 s 時点） | 80,832（受けが終わった後、STOP までの間に溜まりが溢れた分。V2-b の記録と同じ扱い） |

**10-14 の V2-b の TP_JUMP（30 回）は配線のせいだった**: 10-14 の V2-b（受け側は通過、STATUS は残せなかった）では EVENT TP_JUMP 30 回（ADC_A 8・B 4・C 18・D 0、sigma_db 0.020〜0.053、db +0.13〜+0.38）が出た。移植元の測定（sigma_db 0.003、跳ねは 4 ADC で揃う）と形が違った。この日は SG がつながったままだった見込みで、10-15 に配線 N（ノイズソース → PATT 13 dB）を確かめて回し直すと、移植先・移植元とも tp_jump 0,0,0,0 だった。bit も PS もバイト単位で同じなので、移植からは来ない

**M4 は合格**。ID・時刻・窓・PS の取得と送りが、移植先の置き場所（ボードのディレクトリ・bits.json・hwh）で移植元と同じに動いた。

## M5 ID を製品の形に（決めたこと、2026-10-15）

[`release.md`](release.md) の「決めること」と INTERFACE v2 の 5.2（較正は (BIT_KIND, BIT_REV) ごと、PROJ は記録だけ）から、M5 を一度に一つの変更に分ける:

| | 何を | bit | 回帰 |
|---|---|---|---|
| **M5a** | PS の較正の鍵を PROJ から **(BIT_KIND, BIT_REV)** に替える（timebase の CAL・TP の較正ファイル） | 変わらない | sim-regmap（PS の読み手）・test_fake・実機の ID-1・F-1 |
| **M5b** | **USR_ACCESS** に commit を焼き、time_core に読む番地を 1 つ足す | 変わる | M2〜M4 をもう一度（同じ RTL で USR_ACCESS だけ違う 2 本の WNS が一致することも） |

決めたこと:
- **PROJ（コア 0x04・time_core 0x5C・リング 0x2C）は 0x0021_0200 のまま残す**。「どの試行から来たか」の固定値で、照合にも較正にも使わない（INTERFACE v2 の約束どおり）。リリースごとに RTL の定数を変えない（配置が組み替わる。ADR 0018）
- **BIT_REV は 3 のまま**最初のリリースにする。F-2 の較正（adc_to_core）と sim の遅れの表が (2, 3) にそのまま当たる。RTL を変えたら上げる規則は続ける
- **USR_ACCESS の 32 bit は [31:4] commit の短いハッシュ 7 桁・[0] 作業ツリーの汚れ・[3:1] 0**（M5b）

## M5a 較正の鍵を (BIT_KIND, BIT_REV) に（2026-10-15、書く前）

**今**: `timebase.CAL` は time_core の PROJ（0x5C）が鍵（0x0021_0200 ほか、study-rfsoc の過去の bit の 4 件）。TP の較正ファイル `tp_cal.json` は `bit_id_win`（proj017・proj020 の窓の ID）と、載っている bit の PROJ を照らす。proj021（PROJ 0x0021_0200）は一覧に無いので、**今の bit では TP の較正は使われていない**（STATUS の tp_dbm が `-`）。

**変えること**（PS だけ。bit・RTL は変えない）:
1. `timebase.py`: `TimeCore` が IF_ID から `bit_kind`・`bit_rev` を出す。`CAL` の鍵を `(BIT_KIND, BIT_REV)` にし、**(2, 3) の 1 件だけ**にする（値は今の 0x0021_0200 の F-2 の値そのまま）。過去の proj の 3 件は IF_ID の無い bit のもので、製品の道具では載せられないので持ってこない（study-rfsoc に残る）
2. `s45cal.py`: 較正ファイルの鍵を `bits`（`[[BIT_KIND, BIT_REV], …]`）にし、載っている bit の IF_ID（コア 0、START の `ids.adc`）と照らす。`tp_cal.json` は `bits: []`（**どの製品の bit でも使わない** = 今と同じ振る舞い）にし、測った bit は `measured_on` に記録として残す。`s45lin.py` の暫定の較正の書き出しも `bits` で書く
3. `specd.py` の GET CAL・`test_regmap.py` の照合・注釈を合わせる

**予言**:
1. `make sim-regmap` が通過（test_regmap の「time_core の (BIT_KIND, BIT_REV) と CAL の鍵」が (2, 3)）、陽性対照 `sim-regmap-p` は今までどおり落ちる
2. `bash test_fake.sh all` が 13 試験とも通過（偽物は ID を照らさない）
3. 陽性対照（PC で）: `Timebase` に (2, 2) の time_core を渡すと「較正定数を持っていない」で止まる。`s45cal.check` は `bits: [[2, 2]]` と IF_ID 0x0202_0301 で「使えない」、`[[2, 3]]` で「使える」
4. 実機: ID-1 の表は今と同じ。F-1 の錨の行の較正（adc_to_core 146.0・146.3・147.4・147.5、bound 50）が今と同じ。specd の STATUS の tp_dbm は今と同じ `-`

**PC での結果（2026-10-15、作業用の環境で）**:
- 予言 2: **当たり**。`test_fake.sh all` の 13 試験とも通過
- 予言 3: **当たり**。偽の time_core で (2, 3) は較正あり（adc_to_core 146.0・146.3・147.4・147.5、bound 50）、(2, 2) は「BIT_KIND 2・BIT_REV 2 の較正定数を持っていない（未較正…）」で止まった。`s45cal.check`（IF_ID 0x0202_0301）: `tp_cal.json`（bits 空）は使えない、`[[2, 2]]` は使えない、`[[2, 3]]` は使える、bits の無い旧い形は使えない、偽物は照らさない

**Vivado サーバとボードでの結果（2026-10-15）: 予言 1・4 当たり。M5a は合格**
- 予言 1: `make sim-regmap` は 78 項目とも通過（新しい「time_core の (BIT_KIND, BIT_REV) と CAL の鍵（M5a）」を含む）。陽性対照 `sim-regmap-p` は NG 98 件 / 193 で落ちるべきところで落ちた
- 予言 4（M4 の bit をそのまま、PS だけ差し替えたボードのディレクトリで）:
  - ID-1: `bit: SAM45-Fine（BIT_KIND 2）rev 3 / PROJ 0x00210200`・time_core IF_ID 0x0202_0302・4 コアの行は M4 と同じ
  - F-1: 錨の行の精度 `uncalibrated: []`・bound 50 ns・source は proj021 2-5 の F-2（M4 と同じ。4 ADC とも較正あり）、T-1 通過
  - specd: GET CAL は「bit が違う（較正 なし・載っている (BIT_KIND, BIT_REV) = (2, 3)）」で使わない、START n=50 の後の STATUS は miss 0・tp_dbfs −12.54・−12.53・−12.50・−12.50・**tp_dbm `-`（M4 と同じ）**

## M5b USR_ACCESS に commit を焼く（2026-10-15、書く前）

**形を変えた（2026-10-15）**: time_core に USR_ACCESSE2 を読む番地を足すと RTL が変わり、規則（RTL を変えたら BIT_REV を上げ、F-2 を測り直す）と「BIT_REV 3 のまま」が両立しない。そこで **RTL は変えず、ビルドで焼くだけ**にし、**PS が載せる .bit の構成の流れから USR_ACCESS の語を読む**。FPGA の中からは読まない（動いている bit との結び付きは今どおり bits.json・LOAD の sha256）。RTL で読むのは、次に RTL を変えて BIT_REV を上げるときに一緒に足す。

**変えること**（RTL・制約は変えない）:
1. `Makefile`: `USR_ACCESS` を git から作って `build.tcl` に渡す。値は `[31:4]` = `git rev-parse --short=7 HEAD`・`[0]` = 追跡しているファイルに未コミットの変更がある（`git status --porcelain --untracked-files=no` が空でない）・`[3:1]` = 0。`USR_ACCESS=none` で焼かない（比べのため）
2. `build.tcl`: `STEPS.WRITE_BITSTREAM.TCL.PRE` のフックで `BITSTREAM.CONFIG.USR_ACCESS` を設定し、焼いた値を `vivado.log` に出す（`USR_ACCESS (焼く): 0x…`）
3. `sw/pynq/bitinfo.py`（新）: .bit のヘッダを読み飛ばし、構成の流れのパケット（type 1・type 2）をたどって USR_ACCESS（レジスタ 0x0D）への書き込みを拾う。FDRI（構成のフレームのデータ）の sha256 も出す。`make` は書き出した .bit をこれで読み返し、焼くはずの値と違えば失敗にする（在るかと、値が合うかの両側）
4. PS: `s45acq` が載せた .bit の USR_ACCESS を `ids.usr` に入れる（START・LOAD の EVENT に載る）。specd の ID に `usr`、`s45core --list` に 1 行

**確かめた前提**（書く前に、移植元の bit `a99b7a96…` を手で読んだ）: 今の bit には USR_ACCESS への書き込みが無い。構成の流れは同期語の後に type 1 の書き込み 17 個（IDCODE 0x04AA5093 など）、FDRI の type 2 が 1 個（8,608,824 語、sha256 `e095fa97…`）、最後に CRC など

**予言**:
1. 焼いた bit を `bitinfo.py` で読むと、USR_ACCESS = 作ったときの commit と汚れの bit（`make` の読み返しが通る）。M3 の bit（焼いていない）を読むと「なし」
2. **配置・配線は変わらない**: `-1` の WNS / WHS は M3 と小数 6 桁まで同じ（+0.044057 / +0.009766）、資源・CDC の分類ごとの件数・.hwh の IP と番地も同じ。**FDRI の sha256 は M3 と同じ**（`e095fa977cf9ebaa6f980a7a0f5f8bc0212ae6bed469ecdb047b6e18dfbc29f9`）。構成の流れで違うのは USR_ACCESS の書き込みの 2 語（と CRC の値）だけ
3. sim は RTL が同じなので回さない（M2 の結果がそのまま）
4. 実機: M4 と同じ判定（ID-1・F-1・W-0・V2-b 300 s）が通る。specd の ID と START の EVENT に `usr` が出て、1 と同じ値

**PC での確かめ（2026-10-15、作業用の環境で）**: `bitinfo.py` で移植元の bit を読むと USR_ACCESS なし・FDRI 8,608,824 語・sha256 `e095fa97…`・欄 e の sha256 `f042da9f…`（M3 と同じ）。`--expect none` は通過、`--expect 0x12345670` は失敗（終了状態 1）、.bit でないファイルは「読めない」。陽性対照: 移植元の bit の同期語の直後に USR_ACCESS の書き込み（0xabcdef10）を差し込んだ偽の bit は `commit abcdef1（汚れなし）` と読め、FDRI の sha256 は変わらない。`make -n` で `USR_ACCESS` が git から作られ（`0x` ＋ commit 7 桁 ＋ 汚れ）、vivado の後に読み返しが走ること。`test_fake.sh basic` 通過（s45acq の import）

**ビルドの 1 回目（2026-10-15）: build.tcl の照合で止まった**。`ERROR: USR_ACCESS 1278564400 が 0x と 16 進 8 桁でない`（合成の前、OOC の後）。1278564400 = 0x4C355830 で、make が渡した値そのもの。build.tcl で環境変数を `expr {… ? $::env(USR_ACCESS) : ""}` で受けたため、Tcl の expr が `0x…` を数として読み、10 進の文字列にして返した（tclsh で再現）。`if` で受けるように直した（tclsh で、直した節を切り出して `0x4c355830` と `none` の両方で回し、フックの中身が `set_property BITSTREAM.CONFIG.USR_ACCESS 0x4c355830 [current_design]` になることを確かめた）。形の照合を置いていたので、黙って違う値を焼かずに止まった

**ビルドの 2 回目（2026-10-15、commit 8eba348、汚れなし）: 予言 1・2 当たり**

| 項目 | M3（移植元と同じ） | M5b |
|---|---|---|
| USR_ACCESS（bitinfo） | なし | **8eba3480 = commit 8eba348（汚れなし）**。make の読み返しの照合 通過、vivado.log と impl_1 の runme.log にも `USR_ACCESS: 0x8eba3480` |
| `-1` の WNS / WHS | +0.044057 / +0.009766 ns | **同じ（小数 6 桁まで）** |
| LUT / FF / DSP / BRAM / URAM | 168,982 / 256,455 / 2,096 / 233.5 / 56 | 同じ |
| CDC-3 / CDC-6 / CDC-15 | 105 / 5 / 3,137 | 同じ |
| vivado.log の要点（CRITICAL WARNING を含む）・.hwh の IP と番地 | | diff が空 |
| **FDRI（構成のフレームのデータ）の sha256** | `e095fa977cf9ebaa6f980a7a0f5f8bc0212ae6bed469ecdb047b6e18dfbc29f9`（8,608,824 語） | **同じ** |
| 構成の流れ（欄 e）の sha256 | `f042da9f…` | `de33b5bc…`（USR_ACCESS の書き込みと CRC の分だけ違う。長さは同じ 34,437,476 B の .bit） |
| `.bit` / `.hwh` の sha256 | `4f491488…` / `8ddd7f42…`（M3） | `ed6bcf787e4f821364f04b036d855ae742a6aae6f817b8387b174cc384d7bce6` / `0a40365e25e0488ae4fe4ff4c099a3c5429fa774efd8324d4fbc37deee28ce4b` |

- **FDRI が同じ = 配置・配線は M3 とビットまで同じ**。USR_ACCESS を焼いても配置に触れない（ADR 0018 の「確かめること」）を、WNS より強い形で確かめた
- OOC の合成で `system_s45_core_0_0_synth_1` が 1 回落ち、build.tcl の回し直し（Vivado が落ちた run だけを回し直す既存の仕組み）で通った。M3 では落ちていない。結果の値には効いていない（上の表）

**実機（2026-10-17、配線 N、ボードの新しいディレクトリに bit `ed6bcf78…`・hwh `0a40365e…` と `sw/pynq/`）: 予言 4 当たり。M5b は合格**

| 判定 | 結果 |
|---|---|
| ID-1 | 4 コア・time_core の IF_ID、RAW の流れの行は M4 と同じ。`USR_ACCESS（proj021.bit）: 8eba3480 = commit 8eba348（汚れなし）` |
| F-1（120 s） | 13 コアとも RUN_T = START_AT ＋ 1、9 流れ × 2,930 ダンプでずれ +0〜+0、健全性の印なし、T-1 通過 |
| W-0 | A0 窓 0・D3 窓 1 とも FLAGS 0・飽和 0・ダンプ 3 個 × 6,250 フレーム、RESULT OK |
| specd の ID | `usr=8eba3480`（adc_id 02020301・time_id 02020302） |
| V2-b（300 s） | SPEC 237,657・TP 27,264・3.8 GB、CRC・欠け・説明のない欠け・逆戻り・重複・kgap・tdev・tp_gap 0、版 2、照合 通過。START の EVENT の `ids.usr` = `8eba3480`。STATUS（受けの後）: miss・kgap・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost 0、tp_dbfs −12.46・−12.45・−12.41・−12.41、tp_ovr 0、tp_jump 0,0,0,0、loop_p99 19.2 ms。drop 72,095 は受けが終わってから STOP までの間に溜まりが溢れた分（M4 と同じ扱い） |

- 載せる .bit から読んだ commit が、specd の ID・START の EVENT（受け側の記録）まで届いた。動いている bit との結び付きは bits.json の sha256（`ed6bcf78…`）で、起動の照合は通っている

## M6 判定を全部通し、最初の性能評価を書く（2026-10-17、測る前）

**対象の bit**: M5b の bit（`.bit` `ed6bcf787e4f821364f04b036d855ae742a6aae6f817b8387b174cc384d7bce6`・`.hwh` `0a40365e25e0488ae4fe4ff4c099a3c5429fa774efd8324d4fbc37deee28ce4b`、USR_ACCESS `8eba3480` = commit 8eba348、BIT_KIND 2・BIT_REV 3）と、それに載せる `sw/pynq/`。ボードの `~/sam45-fine-m5b/`。FDRI が移植元と同じなので、**判定の値は移植元（proj021 2-5）の記録と同じ範囲に出るはず**。外れたら置き場所・その日の配線を先に疑い、同じ日に移植元の道具のディレクトリでも回して並べる（M4 の型）。

### 決めたこと

1. **V2-d の往復の相手は M4 の bit**（`~/sam45-fine-m4/proj021.bit`、`4f491488…909eae`、USR_ACCESS なし）。製品には 2 本目の bit が無い。道具は同じ `sw/pynq/`（`pydir` は同じ）。**LOAD の仕組みと usr の切り替わり（`8eba3480` ↔ `none`）を見る。版をまたぐ往復（版 1 ↔ 2）は見ない**（`test_fake.sh load` の `LOAD_PEER` なしと同じ考え）。[V2-d](../test/acceptance/sam45-fine/V2-d.md) の前提・手順・合格をこの形に書き直す（測る前）。2 本目の製品の bit（SAM45-Wide など）ができたら、それを相手にする
2. **P-8 の比べの相手は study-rfsoc の proj020 の bit**（ボードの `~/proj020/`、LOAD で切り替えて同じ日に同じ配線で）。比べの相手は**測定の対照**で、製品の bit ではない。判定のファイルの条件（窓の和 / TP が proj020 と ±0.5 %）はそのまま
3. **(2, 3) の TP の dBm 換算を M6 で入れる**（`tp_cal.json` の `bits` に `[2, 3]`）。決め方は proj020 を足したときと同じ形（`tp_cal.json` の `note_proj020`）:
   - P-8 の `s45lin --analyze` が出す `dBFS = PM + c`（ADC ごと）を、(2, 3) と同じ日の proj020 で比べる。**4 ADC とも差 ≦ 0.07 dB なら、TP の経路が較正を測った bit（proj017・020）と同じとみなし、K は測り直さずに `bits` に `[2, 3]` を足す**（`measured_on` は今のまま、`note` に根拠を 1 行）
   - 0.07 dB を越える ADC があれば、その ADC を `adc_port_cal`（PM を ADC の口で、2 回）で測り直してから足す
   - 足した後、specd を起動し直して STATUS の `tp_dbm` が数で出ること、GET CAL が「使う」になることを確かめる
4. **性能評価の 1 本目は `docs/performance/sam45-fine/v1.0.0.md`**。版の名前（bit のタグ `sam45-fine/v1.0.0`）は M7 で確定する。M6 の間は「案」と書き、M7 でタグを付けるときに直す
5. **判定に無い性能の項目は「測り」として足す**（合否を付けない。予言は書く）:
   - **A（安定度）**: 配線 N・P-8 と同じ 8 窓（256 MHz で 2048〜4096 MHz）・tint 40.96 ms で 1 時間受け、`s45allan.py`（アラン分散、ch・分光・TP）。`s45allan` は τ0 = 40.96 ms を前提にしているので、V2-b（10.24 ms）の記録は使わない
   - **V（スプリアス）**: `s45spur.py lin`（P-8 の `.lin.jsonl`・`.spec.npz`、レベル対スプリアス）と `s45spur.py rec`（A の記録、線の一覧と時間の揺れ）。新しい測りは要らない
   - **R（窓の平坦さ）**: 配線 S で `s45resp.py` を `--span` の既定（±0.75 W）で回す（P-5 は `--span 0` で ch の形だけ）

### 回す順（配線ごとの塊）

宛先は環境変数 `B`・`SG`・`PM`・`ATT`。ボードのディレクトリは `~/sam45-fine-m5b/`、記録は制御 PC の `~/m2/m6_*`。**どの塊の前にも `ps aux | grep specd` でほかの specd が動いていないことを確かめる**。

| 塊 | 配線 | 動かし方 | 中身 | 長さの目安 |
|---|---|---|---|---|
| N1 | N | ボード直 | ID-1・F-0・F-1・T-4・W-0（2）・W-G（2）・V2-c・V2-e・V2-f（3）・V2-g（3） | ≒ 20 分 |
| N2 | N | specd | V2-a・S・PS-1・PS-2（10 分）・V2-d・V2-b（30 分） | ≒ 50 分 |
| N3 | N ＋ PM・ATT | specd | PS-3・P-8（(2, 3) と proj020）・tp_cal の決め・A（1 時間） | ≒ 1 時間 40 分 |
| P | P | ボード直 | F-2（2 回、ケーブルを入れ替えて） | ≒ 15 分 |
| S | S（ノイズソースを外す） | ボード直・specd | W-1（2）・P-5・R | ≒ 30 分 |

- 配線の付け替えは N → P → S の 1 回ずつ。**S の後に N に戻すときは SG を外す**（M4 の 10-14 の型）
- `bits.json`（ボードの `~/sam45-fine-m5b/`）は 3 件: `sam45-fine`（既定、M5b の bit、`sha256` 付き）・`m4`（`../sam45-fine-m4/proj021.bit`、`pydir` は `.`、`sha256` 付き）・`proj020`（`../proj020/proj020.bit`、`pydir` `../proj020`、`tp_cal` `../proj020/tp_cal.json`）
- `.s45` は V2-b で ≒ 22 GB、A で ≒ 22 GB。制御 PC の空きを先に確かめ、V2-b の記録は照合が済んだら消す（A の記録は `s45allan`・`s45spur rec` が済むまで残す）
- 受けが終わったら**すぐ** `STATUS STOP` を `tee` で残す
- specd の SET は起こし直すまで残る。V2-b の `tint=0.01024` が後の判定に残らないよう、V2-b を N2 の最後に置き、PS-2 と N3 の SET には `tint=0.04096`（既定の値）を明示する

### 予言

判定の合格の条件は各ファイルのとおり（V2-d だけ書き直す）。値の予言:

1. **N1**: すべて移植元の記録と同じ値。ID-1 に `USR_ACCESS 8eba3480`。F-1 は 13 コアとも RUN_T = START_AT ＋ 1。V2-f の r − G は 138 / 188 / 277 / 450 / 788 / 1454 / 2776 / 5410 ビートが 2 回とも同じ。V2-g の陽性対照 2 つが立つ
2. **N2**: V2-a は 400 組で不一致 0・r = 524,426。PS-1 は e(窓 0) − e(窓 1) = −1.1 ± 2 ns。V2-b（30 分）は SPEC ≒ 8 × 175,800 で欠け・CRC 0、STATUS の miss などすべて 0。PS-2 は loop_p99 ≦ 11.5 ms（M5b の V2-b は 10.24 ms で 19.2 ms だったが、PS-2 は tint 既定の 40.96 ms）。tp_jump は数えるだけ
3. **V2-d**: LOAD 2 回とも ≦ 30 s。ID は 2 本とも adc_id 02020301・time_id 02020302 で同じ、**usr だけが `8eba3480` → `none` → `8eba3480` と変わる**。EVENT LOAD 2 個の sha256 が `4f491488…` と `ed6bcf78…`。SPEC 800・**版 2 だけ**・欠け 0・照合 通過
4. **N3**: PS-3 は step_db −0.94 / +0.94 ± 0.03、tp_jump 2,2,2,2。P-8 は窓の和 / TP が proj020 と ±0.5 %（移植元は +0.06 %）、L-1 は PATT 10〜20 dB で最大 ≦ 0.05 dB。**L-2 は移植元で B0 が 0.0206 dB（±0.02 を 0.0006 越え）だったので、ATT 6〜40 の全段では同じく越える見込み**。PATT 10〜20 dB に絞った L-2 も出し、両方を記録する（合否は判定のファイルの条件どおり全段で付け、越えたら既知の制限に書く）。tp_cal の決め: `dBFS − PM` は proj020 と 0.07 dB 内（TP の経路は同じ RTL の見込み）→ K は測り直さない
5. **P（F-2）**: 4 ADC とも縁が見え、2 回の差 ≦ 1 ビート、平均が今の CAL（146.0・146.3・147.4・147.5 ns）から ±2.5 ns 内。FDRI が同じなので、CAL の値は変えない（差は記録だけ）
6. **S**: W-1 は W 256 で ch 3928・|ppm| ≦ 0.5、飽和 0。P-5 は 8 窓とも半 ch −3.00 ± 0.01 dB・幅 1.000 ± 0.002 ch
7. **測り A・V・R**: 予言の形は道具の注釈のとおり（A: ch ごとは 1/(Δν·τ) に沿い、アラン時間は測った範囲で出す。V: 線の一覧と Ta* への効き r。R: 窓の中央 90 % の平坦さ）。数の予言は無い（最初の測り）。study-rfsoc の proj019〜021 に同じ道具の記録があれば並べる

### 書くもの

- 判定ごとに、この節の下に「M6 の結果」を足す（判定の ID・合格の条件・測った値）
- 判定のファイルの「記録」に、製品の bit で通った日と記録の名前を 1 行足す（移植元の記録は消さない）
- 全部が通ったら `docs/performance/sam45-fine/v1.0.0.md` を `docs/performance/README.md` の節で書く

### M6 の結果: 塊 N1（2026-10-17、配線 N、ボード直）: 予言 1 当たり、10 判定とも通過

外部 10 MHz と 1PPS、PLL は 2 タイルともロック。記録は制御 PC の `~/m2/m6_board/`（ボードの `~/sam45-fine-m5b/m6/` の写し）。

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| ID-1 | IF_ID 0x0202_0301 × 4・time_core 0x0202_0302・リング 0x0202_0303、RAW の流れ、FULL なし、窓の流れ各 2 本 | 4 コアとも 0x0202_0301、time_core 0x0202_0302（リング 0x0202_0303 は V2-c・V2-e・V2-g の表示）。RAW ADC_A2: SID 0x0204_0200・NCH 0・FRAME_BEATS 512・PARAM 13。DDC 各 2 本、FULL なし。`USR_ACCESS（proj021.bit）: 8eba3480 = commit 8eba348（汚れなし）`。**通過** |
| F-0（30 s） | PLL ロック、間隔 − 1 s が ±1 ビート、GLITCH・BAD・MISS 0 | trig 30 個 +0〜+0、comp 30 個 −1〜+1 ビート、GLITCH 0・0・BAD 0・MISS 0。**通過** |
| F-1（120 s） | 13 コアとも RUN_T = START_AT ＋ 1、9 流れのずれ 0、印なし | 13 コアとも +1、9 流れ × 2,930 ダンプでずれ +0〜+0、健全性の印なし。錨の較正 `uncalibrated: []`・bound 50 ns。**通過** |
| T-4 | DUMP_CFG 0x1234・RUN_SHIFT 4 が RUN の後の書き換えに動かない | 窓（A0）・RAW とも 8 ダンプ DUMP_CFG 0x1234、RUN_SHIFT 4、和の比 1.0。**通過** |
| W-0 | ダンプ 3 個 × 6,250 フレーム、FLAGS 0（[4] を除く）、飽和 0 | A0 窓 0・D3 窓 1 とも ダンプ 3 個 × 6,250、FLAGS 0、飽和 pfb 0・ddc 0、RESULT OK。**通過** |
| W-G | 許容を超えた ch 0、SNAP_F = DUMP_F0 | W 256: 超えた ch 0（許容 2.8、最悪の差 1.4）・17920 = 17920。W 8: 超えた ch 0（許容 2.1、最悪の差 1.4）・556 = 556。**通過** |
| V2-c | 8 窓とも SHIFT 7 で超えた ch 0、RAW は飛ばす、DROP 0 | 8 窓とも 超えた ch 0（許容 2.8〜3.0、最悪の差 1.4）、RAW は飛ばした、REC_CNT 17・DROP_CNT 0・ERR 0。**通過** |
| V2-e | 4 ADC とも TP のレコード ≒ 300・照らした個 ≧ 500・不一致 0、SEQ の飛び・式の外れ 0 | 4 ADC とも レコード 304・照らした個 509〜511・不一致 0・SEQ の飛び 0・式の外れ 0・CRC 0、DROP_CNT 0。**通過** |
| V2-f | r − G = 138 / 188 / 277 / 450 / 788 / 1454 / 2776 / 5410 が 2 回の RUN と Overlay のやり直しで同じ、RAW のずれ 0、陽性対照で A0 だけ r_bad 1 | 2 回（それぞれ 60 s × 2 RUN）とも予言の値で RUN の間も同じ、RAW のずれ 0・SEQ の飛び 0、DROP_CNT 0。`--posctl`: A0 だけ m の飛び 1・r_bad 1・束ねを止めた、他の 7 窓は r_bad 0。**通過** |
| V2-g | soak: 13 流れで飛び・DROP・LATE・CRC・尾 0、PEAK ≦ 5 %。`--pause 3`: 飛び = DROP > 0。`--no-inval`: 古い行 > 0 | soak 60 s: 13 流れとも飛び 0・DROP 0・LATE 0・CRC 0・尾 0、PEAK 0.9 %、1 回の読み p99 1.55 ms。`--pause 3`: 飛び 2,507 = DROP_CNT 2,507、CRC 0。`--no-inval`: 頭の magic の不一致 1（古い行を読んだ）。**通過** |

- ID-1 の「番地の幅 64 KiB（.hwh）」は `s45core --list` の表示に出ない（移植元の判定でも同じ形で通過にしている）。.hwh の番地は M5b で M3 と diff が空
- W 8 の W-G で FLAGS [4]（IP に待たされた）が立つのは判定の除外どおり（狭い窓で FFT IP がフレームごとに 1 クロック待たせる: 560 フレームで 560 クロック）

### M6 の結果: 塊 N2（2026-10-17、配線 N、specd）

specd は `--bits bits.json`（`sam45-fine`・`m4`・`proj020` の 3 件）で起こした。ID は `usr=8eba3480`・adc_id 02020301・time_id 02020302・proto 2。記録は制御 PC の `~/m2/m6/`。

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| V2-a | 4 ADC × 100 組で中身・nacc の不一致 0・k の飛び 0、r = 524,426、照合の欠け 0、ずらすと一致 0 / 99 | 4 ADC とも 100 組で不一致 0・nacc 2560・k の飛び 0、ずらすと 0 / 99、bund_r 524,426、SPEC 800・CRC・欠け・kgap・tdev 0、版 2 だけ、pl_dumps 2000・bdrop・r_bad・miss 0。**通過** |
| S | 4 ADC とも 16 塊・間隔・中身（下位 2 bit 0・振り切れ 0・≒ −12.5 dBFS）・UTC の刻み 20 ms、CRC・欠け 0 | 4 ADC とも OK: 16 塊・−12.45 / −12.47 / −12.42 / −12.42 dBFS・振り切れ 0・間隔 True/True・刻み 20,000,000 ns。SNAP 64・CRC・欠け 0。**通過** |
| PS-1 | 組 400・不一致 0・最大 0.5 ulp・版 2、欠け 0、束の間隔 40,960,000 ns・e の幅 0、e(窓 0) − e(窓 1) = −1.1 ± 2 ns、補正なしで +746,697 ns | 組 400・不一致 0・最大 0.5 ulp・版 {2: 1006}・CRC・欠け・kgap・tdev 0。8 窓とも間隔 40,960,000 ns・e の幅 0.0 ns。4 ADC とも −1.1 ns、補正なしで +746,697 ns（陽性対照）。**通過** |
| PS-2（600 s） | 受け側の欠け 0・照合 通過、STATUS の miss などが 0・loop_slow 0・loop_p99 ≦ 11.5 ms、tp_ovr 0・tp_dbfs ≒ −12.5、tp_jump は数えるだけ | SPEC 118,048・TP 59,027・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0、版 2 だけ。STATUS（受けの後）: miss・kgap・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost 0、**loop_slow 0・loop_p99 11 ms**（loop_max 21.25 ms）、tp_ovr 0、tp_dbfs −12.46・−12.46・−12.42・−12.42、**tp_jump 0,0,0,0**、drop 0。**通過** |
| V2-d | 下の表 | **通過**（受け側の SPEC の数は下の注のとおり、START ごとに数えた） |

**V2-d**（相手 `m4`、`v2d.txt`・`v2d_recv.txt`・`v2d.json`）:

| 条件 | 測った値 |
|---|---|
| LOAD ≦ 30 s、EVENT LOAD の sha256 | `m4` 20.6 s（`4f491488…909eae`）・`sam45-fine` 21.3 s（`ed6bcf78…7bce6`）。bits.json と同じ |
| `m4` のとき ID・usr・time_ok | adc_id 02020301・time_id 02020302・**usr none**、STATUS time_ok=1 |
| 戻ったとき ID・usr・pl_*・START の EVENT | 同じ adc_id・time_id・**usr 8eba3480**、time_ok=1、pl_drop・pl_crc 0、START の EVENT に proto 2・fmt f32・read ring・ids.usr 8eba3480（`m4` の START は ids.usr none） |
| どの START も n に達した・8 窓 × 50・miss 0、TP の anch_dev・gap 0 | 2 回とも「n に達した」・dumps 50 × 8・miss 0、4 ADC とも anch_dev 0・gap 0 |
| 受け側: SPEC 800・版 2 だけ・欠け 0・照合 通過 | 2 回の START の中の SPEC は **400 ＋ 400 = 800**（受けた全体は 832）、版 {2: 1264} だけ、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0、照合 通過 |

- **受けた SPEC が 832 になったのは、直前の PS-2 の残り**（測った後に記録を開いて確かめた）: 受けの頭に、seq 179362〜179405 の SPEC 32 個（8 窓 × 4 ダンプ、n_sum 4）・TP 17 個と、PS-2 の STOP（why「命令」、dumps 14,760）がある。PS-2 の specrecv が 600 s で閉じてから STOP までの間に溜まった記録で、specd は次につないだ受け手（V2-d の specrecv）に送った。PS-2 の受けの last_seq 179360 から V2-d の受けが 179361 で続き、**番号は受け手をまたいでも欠けていない**。V2-d の条件の「SPEC 800」は 2 回の START の分を言っているので、START ごとに数えて判定した
- seq は LOAD をまたいで続く（STOP 179410 → START 179411、STOP 180016 → START 180017）。LOAD の EVENT は通信の側の seq 0
- 判定のファイルの手順は、前の運転の溜まりが空のことを前提にしている。次からは手順の頭で受けを 1 度つないで溜まりを捨てるか、START ごとに数える（判定のファイルに測った後の注として書いた）

**N2 の続き（2026-10-17）**:

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| V2-d の陽性対照 | sha256 を 1 文字変えた bits.json で LOAD が止まり、元の bit のまま | specd を `--bits bits_bad.json` で起こし、`LOAD bit=m4` → `ERR LOAD m4 の sha256 が bits.json と違う（4f491488…）`、その後の ID は `usr=8eba3480`（M5b の bit のまま）。**通過** |
| V2-b（1,800 s、10.24 ms） | SPEC ≒ 8 × 175,800、CRC・欠け・説明のない欠け・kgap・tdev・tp_gap 0、版 2 だけ、照合 通過。STATUS の miss・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost 0。STATUS の行を残す | SPEC 1,406,015（8 × 175,752）・TP 164,634・22.3 GB、CRC・欠け・説明のない欠け・逆戻り・dup・kgap・tdev・tp_gap 0、版 {2: 1,570,650} だけ、START の EVENT の ids.usr 8eba3480・tint 0.01024。STATUS（受けの後、`v2b_status.txt`）: dumps 175,767・miss・kgap・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_bad・tp_rec_lost 0、tp_ovr 0・tp_jump 0,0,0,0・tp_dbfs −12.47・−12.45・−12.41・−12.41、**drop 0**（受けの後すぐに STOP した）、loop_p99 16.6 ms（30 s 時点 22.9 ms）・loop_slow 84,613 / 113,119 周（数えるだけ）。**通過** |

- V2-b の drop が 0 になったのは、受けが終わってすぐ `STATUS STOP` を打ったため（M4・M5b は 72,000〜81,000）。手順の型（受けの後すぐ STOP）が効いた
- これで塊 N1・N2 の 16 判定（V2-d の陽性対照を含む）が通過

### M6 の結果: 塊 N3（2026-10-17、配線 N ＋ ATT・PM、specd）

**specd の取得のプロセスが RUN から ≒ 22 s で止まった件（PS-3 の 1・2 回目）: ボードの `/dev/shm` が溢れていた**

- 症状: PS-3 を 2 回続けて、RUN から 22〜23 s で specd が「取得のプロセスが止まった」で終わった。子のプロセスは Traceback を出さず（シグナルで止まった形）、specd の終わりに resource_tracker の `KeyError: '/psm_…'` と「leaked semaphore」の警告。1 回目の受けは 69.2 MB（SPEC 4,232）・照合 通過
- 診断（測る前に予言を書いてから確かめた）: specd の溜まり（256 MB の共有メモリ `/dev/shm/psm_*`）が、**specd が終わるたびに消されずに残っていた**。`free -m` の shared 1,898 MB、`df -h /dev/shm` は 2.0G のうち 1.9G 使用・残り 70M、`psm_*` が 8 個（10-14 〜 10-17 の日付。移植元の proj021・proj023 の運転と、今日の V2-b の specd の分を含む）。新しい specd の溜まりは書いたページからメモリを取るので、残りの ≒ 70 MB を書き終えたところで SIGBUS で止まる（1 回目の受けの 69.2 MB と合う）
- 処置: specd が動いていないことを確かめて `rm -f /dev/shm/psm_*` → `/dev/shm` 0 %・shared 3 MB。その後の PS-3（3 回目）は 120 s を通した
- **直していない**（M6 の中では判定に使う PS を変えない）。specd が普通に止まったときも共有メモリを消し損ねる（今日の V2-b の分が残っていた）。study-rfsoc の specd（proj021 由来の同じコード）も同じ。別の issue にする。性能評価の「既知の制限」に書き、当面の運転の手順に「specd を起こす前に `df -h /dev/shm` を見る、止まっている間に `psm_*` を消す」を足す

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| PS-3（3 回目、`ps3.log`・`ps3_status.txt`） | 4 ADC とも跳ね 2 回・tp_jump 2,2,2,2、step_db −0.94 / +0.94 ± 0.03、ovr false、n 400〜700、`db` は瞬断で −46〜−49 dB | 4 ADC とも跳ね 2 回（PATT 13 → 14 dB と 14 → 13 dB）・STATUS の tp_jump 2,2,2,2。**step_db −0.9409〜−0.9434 / +0.9386〜+0.9408**、ovr false、n 540・522、sigma_db 0.0029〜0.0035。`db` は 1 回目 −41.8〜−42.1、2 回目 −23.4〜−23.5 dB（**条件の範囲の外**、下の注）。受け側 SPEC 21,448・CRC・欠け 0・照合 通過、STATUS の miss などすべて 0・loop_slow 0・loop_p99 11.4 ms。**通過**（`db` の条件を除く） |
| P-8 の窓の和 / TP（`lin_m6`・`lin_m6_p20`） | 中央 90 % の窓の和 / TP が、同じ配線で測った proj020 と ±0.5 % | (2, 3) **0.89299**・proj020 0.89288 → **+0.012 %**（移植元の記録は 0.8912 / 0.8907 = +0.06 %）。窓ごとの比も 8 窓とも 0.0002 以内で同じ。**通過** |
| P-8 の L-2 | 窓 / TP がレベルによらず一定（±0.02 dB） | (2, 3): 8 窓とも最大 0.0055〜0.0154 dB（B0 が最大）、proj020: 0.0066〜0.0148 dB。**通過**（予言では移植元の B0 0.0206 dB と同じく越える見込みだったが、越えなかった） |
| P-8 の L-1 | PATT 10〜20 dB で TP 4 本・8 窓とも、床を引いた値がパワーメーターに比例（残差 ≦ 0.05 dB） | **判定できていない**: パワーメーターの読みが ATT 6〜100 dB のどの段でも −55.5〜−56.0 dBm で動かず（2 本とも）、PM 基準の点が 0 個。TP は ATT の 2 dB の段ごとに ≒ 2 dB 動き、ATT 13 dB で −12.4 dBFS。PM に信号が届いていない（配線の側）。PM をつないで測り直す |

- PS-3 の `db` の外れ（測った後に TP のレコードを開いて確かめた）: 瞬断は 2 回とも ≒ 3 ms で、TP の区切り（1.024 ms = 262,144 ビート）3 個にかかる。1 回目は区切り 1 個がほぼ丸ごと瞬断に入り −42.1 dB（前後 −23.6・−5.9 dB）、2 回目は瞬断が 2 個の区切りにまたがり −24.5・−19.0 dB に割れた。`db` は区切り 1 個の深さの最大なので、**瞬断と区切りの位相で決まり、分光計の性質ではない**（アッテネータの瞬断の性質）。移植元の −46〜−49 dB は 1 回の測りの値を条件にしたもの。判定のファイルの `db` の行は「記録するだけ」に改める（測った後の改め）
- tp_cal (2, 3) の決め（dBFS − PM の比べ）も、PM の測り直しの後に

**L-1 の測り直しの前に（2026-10-21、測る前）**: 分配器の交換で ADC までの損失が ≒ 18 dB 増え（PATT 13 dB で −30.9 dBFS）、前の L-1 の範囲（PATT 10〜20 dB ≒ −9.5〜−19.5 dBFS）が作れない。
[P-8](../test/acceptance/sam45-fine/P-8.md) の L-1 の範囲を **TP −18〜−28 dBFS（PATT 0〜10 dB）** に改め、掃引を `--lo 0` にした（高い側は proj021 2-5 の L-1 で支える。FDRI が同じ）。
同じ日に 1PPS・10 MHz の入口に LPF を入れた（study-rfsoc proj026）: F-2（LPF あり、A↔D・B↔C の入れ替えで 2 回）は M = A 70.0・B 70.1・C 69.7・D 69.7 ns、LPF の遅れ ≒ 71.5 ± 2 ns。
CAL は adc_to_core_ns を bit の値（LPF なし）のまま、LPF の分を pps_det_ns に入れる形 (b) に決めた（西村さん）。**塊 P の F-2 はこの測りで済ませ、CAL を (b) で入れるときに結果をこの節の下に書く**

**M6 の結果: P-8 の測り直し（2026-10-21 13:20〜13:40、`~/m2/m6/lin_m6b`・`lin_m6b_p20`、上の改めの範囲で）**

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| P-8 の L-1 | TP −18〜−28 dBFS の段で TP 4 本・8 窓とも、床を引いた値がパワーメーターに比例（残差 ≦ 0.05 dB） | (2, 3): 10 段（PATT 0〜8、D は 2〜10）で最大 **0.0450 dB**（D1、ほかは ≦ 0.023 dB）・proj020 も最大 0.0470 dB（D1）。**通過**。PM は 2 dB ずつ動いた（前回の「信号が届いていない」は解消） |
| P-8 の窓の和 / TP | 中央 90 % の窓の和 / TP が proj020 と ±0.5 % | (2, 3) **0.90506**・proj020 0.90494 → **+0.013 %**。窓ごとの比も 8 窓とも 0.0004 以内。**通過** |
| P-8 の L-2 | 窓 / TP がレベルによらず一定（±0.02 dB、全段・床の 100 倍以上の点） | (2, 3): 7 窓は 0.0036〜0.0176 dB、**D1 0.0489 dB で NG**。proj020 も **D1 0.0467 dB で NG**（ほか ≦ 0.0157）。TP −18〜−28 dBFS に絞っても D1 は 0.036 / 0.027 dB |
| tp_cal (2, 3) の決め | dBFS − PM が proj020 と 0.07 dB 内なら K を測り直さずに `bits` に足す | (2, 3) −0.68・−0.65・−0.64・−0.54・proj020 −0.73・−0.68・−0.68・−0.57 dB → 差 0.03〜0.05 dB。**`tp_cal.json` の `bits` に `[2, 3]` を足した**（`note_m6`） |

- L-1 の解析は `s45lin --analyze` が全段で当てはめるので、範囲 −18〜−28 dBFS の判定は同じ式を範囲に絞って計算した（その ADC の TP の dBFS で段を選ぶ）。全段の `--analyze` では A0・A1・D1 が 0.056〜0.066 dB で NG と出るが、それは範囲の外（−28 dBFS より下、床に近い段）
- **L-2 の D1 は 2 本の bit で同じだけ外れた**（0.0489 / 0.0467 dB）。D1（3840〜4096 MHz）は BPF（2.1〜3.9 GHz）の肩で、窓 / TP が 1.4 % しかない。分光計の差ではなく入力の形（PATT の段ごとの周波数特性が BPF の肩で効く）と見ている（確かめていない）。10-17（前の配線・高いレベル）では D1 も通っていた
- **扱い（2026-10-21、西村さん）: D1 の L-2 は「判定できない」とし、性能評価の既知の制限に書く**（比べの proj020 も同じだけ外れる。条件は測った後に変えない）。7 窓は通過

**塊 S の配線を改める（2026-10-21、測る前。西村さんの配線に決めた）**: 配線 N と S を 1 つにした **配線 N/S**:
ノイズソース → BPF 2.1〜3.9 GHz → 2 分配器 A ← SG／2 分配器 A → PATT → 2 分配器 B →（ATT 20 dB → PM）・（ATT 3 dB → 4 分配器 → ADC_A〜D）。分配器は ZFRSC-42-S+（2 分配）・ZFRSC-4-842-S+（4 分配）。
ノイズの経路の損失は P-8 の測り直しのとき（BPF が PATT の後）と同じ（P-8 の改めの範囲 PATT 0〜10 dB のまま）。SG は BPF を通らない。ADC で ≒ SG − 33 dB − PATT（dBFS、見積もり）。
- W-1: 手順どおり SG −0.9 dBm・PATT 0 dB（≒ −34 dBFS、前は −21.5）。条件（ch・ppm・飽和 0）は変えない
- P-5: 条件「ADC で ≒ −20 dBFS（± 3 dB）」を満たすよう **SG +12 dBm・PATT 0 dB**（手順の −0.9 dBm から変える。条件は dBFS なので変えない）。unleveled なら +10 dBm（−23 dBFS）。先に TP で確かめてから掃引する
  - **確かめ（13:54）: SG +12 dBm で TP −23.10・−22.84・−22.41・−22.59 dBFS、sat 0、unleveled の警告なし。A が下限 −23 を 0.1 dB 外れた（見込みより損失が ≒ 2 dB 大きい）→ SG +13 dBm に上げて回す**（+12 dBm で始めた P-5 は止める。流れきったものは判定に使わない）
- R: P-5 と同じ SG のレベル（+13 dBm）。BPF の帯域外の反射（抵抗型の 2 分配器の分離は 6 dB）が SG の経路に凹凸を乗せうる（A0・D1 の窓）。出たら R の結果に書く

**M6 の結果: 塊 S（2026-10-21 13:50〜14:40、配線 N/S、ノイズソース OFF・PATT 0 dB）: W-1・P-5 は通過、測り R を取った**

| 判定 | 合格の条件 | 測った値 |
|---|---|---|
| W-1（ボード直、SG −0.9 dBm） | 山の ch が予言・\|SG との差\| ≦ 0.5 ppm・窓・pfb・ddc の飽和 0 | W 256: ch **3928**・**−0.05 ppm**・隣 −52.3 / −52.1 dB／W 64: ch **3424**・**−0.01 ppm**・隣 −51.5 / −51.4 dB。飽和 0（窓・pfb・ddc）。**通過** |
| P-5（specd、SG +13 dBm、`~/m2/m6/resp_p5b`） | ADC で −20 dBFS ± 3・飽和 0・8 窓とも半 ch −3.00 ± 0.01 dB・−3 dB 幅 1.000 ± 0.002 ch・ref 0.9913〜0.9916 | TP −21.40〜−22.09 dBFS・飽和 0。半 ch **−2.9977〜−3.0010 dB**・幅 **0.9999 ch**（8 窓とも）・ref **0.9913〜0.9915**。**通過** |

- W-1 の隣の ch は 10-14（−53.5 / −53.4 dB）より ≒ 1.2 dB 高い。CW が ≒ 12 dB 弱く（≒ −34 dBFS）、隣の ch に床が乗った分と見ている（条件の外）。W 64 の FLAGS 0x10 は判定に入れない表示（10-14 と同じ）
- **測り R（`~/m2/m6/resp_rb`、SG +13 dBm、±0.75 W・972 点・21 分）**: 通過域（中央 90 %）の p-p **0.021〜0.033 dB**（W 256 の A0・D0 が最大）、−3 dB の端 ±0.487 W（8 窓とも）、窓の外の CW の折り返し最大 **−58.9〜−61.3 dB**（D0 が最大）、ch の形は P-5 と同じ（半 ch −2.992〜−3.001 dB・幅 0.9997〜0.9999 ch）
- **予言の外れ（前提の誤り）**: R で「BPF の帯域外の反射が A0・D1 に出るかも」と書いたが、s45resp の窓の並びは 8 窓とも IF 3000 MHz の周り（幅 256〜8 MHz）で、2048〜4096 MHz に敷き詰める P-8 の並びではない。掃引は 2808〜3192 MHz で BPF の肩にかからない。予言は道具の窓の並びを読まずに書いた

**測り A の形を改めた（2026-10-17、測る前）**: 1 時間の予定を **8 時間**（`START n=703125`、40.96 ms、P-8 と同じ 8 窓を 256 MHz で 2048〜4096 MHz に敷き詰め、PATT 13 dB 固定、SG の出力は切った、PM はつないでいない）にした。夜の空き時間に回せたため。最初の 1 時間は元の測り A と同じものとして読める。記録は ≒ 93 GB（`~/m2/m6/allan.s45`）、STATUS は 30 s・4 時間・終わりに残す。

測り A（8 時間）の予言（結果を見る前。数の予言は無いので形で）:
1. **運転**: 8 時間を通して miss・kgap・bdrop・r_bad・pl_drop・pl_crc・tp_lost・tp_rec_lost・drop 0、受け側の CRC・欠け 0。loop_p99 は 30 s 時点（11.1 ms）と 4 時間・終わりで変わらない（±2 ms）。ボードの `/dev/shm` は溜まり 1 個（256 MB）だけ
2. **アラン分散（`s45allan`）**: 短い τ では (b) ch ごと・(t) TP とも予言の 1/(Δν·τ)・1/(B·τ) に沿う（最短の τ で予言の 0.8〜1.3 倍）。(a) 帯域の電力・(t) TP は入力（ノイズソース・PATT・室温）の利得の揺らぎで、(c)・(d) より短い τ で予言から離れる。**(c) 共通の利得を除いた ch ごと・(d) 下半分 / 上半分の比のアラン時間は、(a)・(t) より長い**（入力の利得の揺らぎが打ち消し合う）。8 時間で τ の上限は ≒ 2.5 時間で、(d) が数百 s 以上でも予言に沿っているかを見る
3. **4 ADC の比べ**: (t) TP の長い τ の揺らぎは 4 ADC で揃う（入力が共通）。揃わなければ ADC・ケーブルの側
4. **スプリアス（`s45spur rec`）**: 線の一覧は proj019〜021 の記録と同じ種類（k·fs/8 の線 3072 MHz など、W-0 の「注意」に出るもの）で、新しい線は出ない。線の時間の揺れ（ratio）は、線の無い ch のラジオメータの揺れと同じ程度（ratio ≒ 1）

**測り A・V の結果（2026-10-17 夜〜10-18、8 時間、`~/m2/m6/allan.*`・`spur_rec.txt`・`lin_m6.spur.json`・`lin_m6_p20.spur.json`）**

予言 1（運転）: **当たり**
- 受け側: SPEC 5,625,000 = 8 × 703,125、TP 2,812,504・92.0 GB、CRC・欠け・説明のない欠け・逆戻り・dup・kgap・tdev・tp_gap 0、版 2 だけ、照合 通過。STOP の EVENT は「n に達した」・8 窓 × 703,125・miss 0・4 ADC とも anch_dev 0・gap 0
- STATUS（30 s・4 時間・終わり）: miss・kgap・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_bad・tp_rec_lost・drop 0、tp_ovr 0、loop_slow 0、**loop_p99 11.1 → 10.8 → 10.8 ms**（増えない）、loop_max 22 ms、pl_peak 793,344 B のまま、tp_dbfs −12.39〜−12.47
- **所見: tp_jump 0,0,2,2**。2 回とも **ADC_C と D で同じ t_beat**（開始から 6,714 s と 11,813 s）、区切り 1 個（n 1 = 1.024 ms）だけ −0.019・+0.018 dB、step_db 0、sigma_db 0.003（≒ 6σ）。A・B には無い。2 本で同時なので雑音の偶然ではなく、C・D に共通なもの（タイル 224、または 2 段目の分配器の C・D の枝）。窓（40.96 ms）に直すと ≒ 0.0005 dB で判定には効かない。出どころは確かめていない

予言 2（アラン分散、`s45allan --chan-bin 250`。ch ごとの τ は 10.24 s から）: **おおむね当たり。TP の比は外れ（理由は分かっている）**

| 量 | 最短の τ で予言との比（8 窓 / 4 ADC） | アラン時間（予言の 2 倍を越える τ） | proj019 の allan2（1 時間、−17 dBFS） |
|---|---|---|---|
| (b) ch ごと | **1.00**（10.24 s） | 512 s（D1 だけ 205 s） | 1.00・1024 s |
| (c) ch ごと・共通の利得を除く | **1.00** | **8 窓とも 5,120 s まで越えない**（A0 で 1,024 s 1.00・2,048 s 1.07・5,120 s 1.76） | 1.00・1024 s まで越えない |
| (d) 分光（下半分 / 上半分） | 1.16〜1.18 | 205 s（A0・B0・B1・C1・D0）・82 s（C0）・41 s（A1・D1） | 1.00・205 s |
| (a) 帯域の電力 | 1.46〜1.59 | 2.05 s（D1 0.82 s） | 1.37・2.05 s |
| (t) TP（1.024 ms、B = 1800 MHz） | **0.50〜0.51** | 0.010 s | 0.31・0.020 s |

- (c)・(d) のアラン時間は (a)・(t) より 1〜3 桁長い（予言どおり）。**分光計の ch ごとの安定度は、入力の利得の揺らぎを除けば 8 時間の中で 5,120 s までラジオメータの式どおり**
- **(t) TP の 0.50 倍は予言（0.8〜1.3）から外れた**が、proj019 で決着した「入力のノイズソースがガウスでない」と同じもの: 今日の S の判定で測った尖度 κ = 2.04〜2.05 から、Σx² の揺れの予言との比 (κ − 1)/2 = **0.52** で、測った 0.50 と合う（proj019 は −17 dBFS で κ 2.47〜2.49・0.31 倍。ATT を絞ったぶんノイズソースの圧縮が強い）。TP の積み方・単位は正しい（分光には効かない: (b)・(c) は 1.00）
- 予言 3（4 ADC の比べ）: **当たり**。TP の長い τ の揺れは 4 ADC で揃う（√σ² が 1,024 s で 2.40〜2.58e-4・5,120 s で 6.07〜6.28e-4）。窓の (a) も 4 ADC で同じ形（D0・D1 が 1.2 倍ほど大きい）
- (d) の 1.16〜1.18 倍（短い τ）と A1・D1 の短いアラン時間は、窓の中の線と入力のスペクトルの傾きの揺れが効いていると見ている（確かめていない）

予言 4（スプリアス）: **一部外れ**
- `s45spur lin`（P-8 の記録、(2, 3) と proj020）: 線は **fs/25 = 163.84 MHz の櫛**（2457.6・2621.44・2785.28・2949.12・3440.64・3604.48・3768.32・3932.16 MHz、proj019 の一覧と同じ種類）と入力に比例する 2457.6 MHz（A1、r ≒ 0.08、両方の bit で同じ → 入力の側）。予言に書いた k·fs/8（3072 MHz）は窓の端の 5 % に落ちて見ていない。**強さは bit で違う**: 運転のレベル（−15.9 dBFS）で (2, 3) は最大 1.68 K 相当（D0 3604.5 MHz）、proj020 は 0.86 K（D0 3768.3 MHz）。D1 3932.2 MHz は r 8.4e-3 / 1.7e-3。どれも入力によらない加算的な線で、配置・配線の違いでクロックの漏れ方が変わったと見ている
- `s45spur rec`（8 時間の記録、10.24 s ずつ）: 櫛の線（3604.5・3768.3・3932.2 MHz など）は**線の無い ch と同じ程度にしか揺れない**（アラン分散の比 0.7〜1.8）→ チョッパーホイールの式で消える（予言どおり）。r は D0 3604.5 MHz が 5.1e-3（0.71 K 相当）で最大
- **予言の外**: A1 に **2426.0 MHz（r 9e-4・0.13 K 相当）と 2402.1 MHz（r 4e-4・0.06 K）の弱い線が出て、時間で大きく揺れる**（アラン分散の比 102 s で 166 倍・29 倍）。櫛の上には無い。2402・2426 MHz は Bluetooth LE の告知のチャネル（37・38）と同じ周波数なので、**実験室の外からの電波が入力の側に入っている**見込み（確かめていない）。分光計の線ではない

## M1 から持ち越した直し: `test_fake.sh` の `load` が proj020 の道具を要る（2026-10-14）

**問題**: `sw/pynq/test_fake.sh` の `t_load`（proj021 2-3d、LOAD で bit を往復）は、往復の相手に study-rfsoc の `../../proj020/pynq`（s45proto 版 1 の道具）を使う。YATSUGATAKE には無いので、`bash test_fake.sh load`・`all` が NG になる（2026-10-14 に確かめた: `cd: ../../proj020/pynq: No such file or directory`・「判定: NG」）。

**直し方**: 往復の相手の道具の場所を環境変数 `LOAD_PEER` で渡す。
- `LOAD_PEER` なし（YATSUGATAKE の既定）: 相手は同じ `sw/pynq/`（別の名前 `peer`・別の .bit）。LOAD の仕組み（取得のプロセスの起こし直し・番号が続く・説明のない欠け 0・送り直しとみなした記録 0・EVENT LOAD 2・`bad` は元に戻る）を見る。**版をまたぐ往復（版 1 と 2）は見ない**ので、判定の行に「版 2 だけ」と出す
- `LOAD_PEER=<proj020 の pynq>`: 今までと同じく版 1 と 2 の両方を求める
- 製品の 2 本目の bit ができたら、その道具を相手にする（V2-d と同じ。M6 で見直す）

**予言**:
1. `LOAD_PEER` なしで `load` が通過（SPEC 320・説明のない欠け 0・送り直し 0・EVENT LOAD 2・版は 2 だけ）
2. `LOAD_PEER=<study-rfsoc の proj020/pynq>` で `load` が通過（版 1 と 2 の両方、proj021 と同じ）
3. 陽性対照: `LOAD_PEER` に同じ `sw/pynq/`（版 2）を渡すと、版 1 を求めるので NG
4. `all` の 13 試験が全部通過（`LOAD_PEER` なし）

**結果（2026-10-14、作業用の環境で）: 予言 1〜4 当たり**
1. `LOAD_PEER` なし: **通過**。SPEC 320・説明のない欠け 0・送り直し 0・EVENT LOAD 2・版 {2: 487}・bad は元に戻る
2. `LOAD_PEER=study-rfsoc の proj020/pynq`: **通過**。版 {2: 366, 1: 122}（版をまたぐ往復も今までどおり）
3. 陽性対照（`LOAD_PEER` に同じ `sw/pynq/`）: **NG**（版 {2: 488}、求める版 1 2）。落ちるべきところで落ちた
4. `all`: 13 試験とも通過（`test_fake: 全部通過`）

ついでの直し: `t_load` の判定の式に `|| echo 0` を足した（`t_idle` と同じ形）。無いと、NG のときに判定の行の説明が空になる（直す前の NG も説明が空だった）
## M1 から持ち越した直し: 係数の生成の道具の既定の書き出し先（2026-10-14）

**問題**（proj021 の手順 1a から。Makefile は書き出し先を明示して渡すので、ビルドと sim には効いていない）:
- `model/pfb4.py gen` の書き出し先が `model/../src/pfb4_rom.v`（＝リポジトリの直下の `src/`、無い）。実際の置き場所は `hw/bits/sam45-fine/src/pfb4_rom.v`。直す前に回すと `FileNotFoundError`（係数の表 `model/pfb4_coef.txt` は書き終えた後で落ちる。中身は同じだった）
- `hw/bits/sam45-fine/tools/gen_coef.py` を引数なしで回すと `hw/bits/sam45-fine/src/` に `win_coef.vh`・`nco_rom.v` を書く。実際の置き場所は `hw/common/`。直す前に回して確かめた: 2 個とも `hw/common/` のものとバイト単位で同じ中身が、間違った場所に新しく出来た（消した）

**直し方**: 2 つの道具の既定の書き出し先と、使い方の注釈の中のパスだけを直す（`pfb4.py` は `HERE/../hw/bits/sam45-fine/src/pfb4_rom.v`、`gen_coef.py` は `tools/../../../common/win_coef.vh`）。係数・生成の中身・Makefile は変えない。

**予言**:
1. 直した後、`python3 model/pfb4.py gen` は `model/pfb4_coef.txt` と `hw/bits/sam45-fine/src/pfb4_rom.v` をバイト単位で同じに書き直す（`git status` が空）
2. 直した後、`python3 hw/bits/sam45-fine/tools/gen_coef.py`（引数なし）は `hw/common/win_coef.vh`・`hw/common/nco_rom.v` をバイト単位で同じに書き直し、ほかの場所にファイルを作らない
3. bit・sim には効かない（Makefile は前から明示して渡している）

**結果（2026-10-14）: 予言 1・2 当たり**。直した後、2 つの道具をリポジトリの外のディレクトリから引数なしで回した: `pfb4.py gen` は `model/pfb4_coef.txt`・`hw/bits/sam45-fine/src/pfb4_rom.v` を、`gen_coef.py` は `hw/common/win_coef.vh`・`hw/common/nco_rom.v` を書き、`git status` に出たのは直した 2 つの道具だけ（生成物はバイト単位で同じ、ほかの場所にファイルは出来ない）。予言 3 は Makefile を変えていないことによる（sim・ビルドは回していない）

## 移植の後

- study-rfsoc の README と INDEX に「SAM45-Fine は YATSUGATAKE へ移した（commit）」と 1 行足す
- 以後、SAM45-Fine の変更は YATSUGATAKE の PR で行う。試行が要るときは study-rfsoc に新しい proj を起こす
- 2 本目の bit（SAM45-Wide）で、common と bit の境目を見直す
