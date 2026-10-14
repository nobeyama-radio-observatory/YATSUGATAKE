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
| M3 | ビルド（`-1`、proj021 と同じ実装の戦略） | 下の「同一性の判定」 |
| M4 | 実機で短い回帰 | ID の読み出し・F-1（RUN_T）・W-0・V2-b を短く（5 分）。proj021 と同じ値 |
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

## 移植の後

- study-rfsoc の README と INDEX に「SAM45-Fine は YATSUGATAKE へ移した（commit）」と 1 行足す
- 以後、SAM45-Fine の変更は YATSUGATAKE の PR で行う。試行が要るときは study-rfsoc に新しい proj を起こす
- 2 本目の bit（SAM45-Wide）で、common と bit の境目を見直す
