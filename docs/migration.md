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
| M5 | ここで初めて ID を製品の形に変える（別の PR） | [`release.md`](release.md) の手順。変えた後に M2〜M4 をもう一度 |
| M6 | 判定を全部通し、最初の性能評価を書く | `docs/performance/sam45-fine/<版>.md` |
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
