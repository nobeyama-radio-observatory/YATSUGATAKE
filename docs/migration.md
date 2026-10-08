# study-rfsoc からの移植計画

- 状態: **準備中**（proj021 の完成を待つ）
- 決定: [ADR 0002](decisions/0002-migrate-from-proj021-restructure-only.md)（proj021 を土台にし、構成替えだけを行う）

## 原則

1. **変更は一度に一つ。** 移植の PR は「ファイルを置き直す」だけにする。ID・係数・機能・制約を同時に変えない
2. **同じものができたことを、数えて確かめる。** 目で見て「同じはず」で済ませない
3. **study-rfsoc の proj021 は書き換えない。** 移植の後に見つかった問題は、YATSUGATAKE で issue にする

## 始める条件

- [ ] proj021 の判定（手順 0・1a・1b・2 の V2-a〜V2-g・F-2）が通り、README に結論が書かれている
- [ ] proj021 の手順 1a で、ソースが `src/common/`・`src/sam45fine/`・`src/board/` に分かれている
- [ ] proj021 の判定が `test/acceptance/` の書き方（6 項目）で書かれている
- [ ] study-rfsoc の proj021 が push 済みで、移植元の commit を 1 つに決めた → **移植元: `study-rfsoc@________`**（ここに記録する）

## 置き場所の対応（案）

| study-rfsoc | YATSUGATAKE | 備考 |
|---|---|---|
| `BITS.md` | `docs/spec/bits.md` | 仕様の行に ADR の番号を添える |
| `INTERFACE.md`（v2） | `docs/spec/interface.md` | 経緯（「見送った案」）は ADR 0016 に寄せ、spec には今の約束だけを残す。図（`docs/interface_*.svg`）も移す |
| `VERSIONS.md` | `docs/spec/hardware.md` ＋ `docs/knowledge/` | 固定値は spec、経緯と落とし穴は knowledge（既に要約済み） |
| `proj001/docs/runbook.md` | `docs/knowledge/environment.md` に足す | ライセンスの節は環境に依る部分を除いて一般化する |
| proj021 `src/common/` | `hw/common/` | |
| proj021 `src/board/` | `hw/board/` | `ps_preset.tcl`・タイミング制約・1PPS のピン |
| proj021 `src/sam45fine/` | `hw/bits/sam45-fine/` | |
| proj021 `build.tcl`・`Makefile`・`program.tcl`・`clocks/` | 共通の部分は `hw/common/tcl/` ＋ bit ごとの Makefile | 照合（part・結線・両側）を共通の手続きにする |
| proj021 `sim/` | `hw/sim/`（共通の tb）＋ `hw/bits/sam45-fine/sim/` | 陽性対照の変種も移す |
| proj021 `model/` | `model/` | 係数を作る模型（pfb4・win_fixed など）。係数の表と一緒に版を持つ |
| proj021 `pynq/`（specd・s45proto・s45ring・timebase・取得の道具） | `sw/specd/` | |
| proj021 `pynq/`（s45client・specrecv・照合の道具） | `sw/client/` | |
| proj021 `pynq/`・`tools/`（s45lin・s45allan・s45spur・s45tastar など） | `sw/tools/` | 較正・測定の道具 |
| proj021 `pynq/tp_cal.json`・timebase の CAL | 較正ファイル（`bits.json` が指す） | (BIT_KIND, BIT_REV) ごと |
| proj021 `docs/`（ブロック図の描画） | `docs/design/` | |
| proj021 README の判定 | `test/acceptance/<ID>.md` | |
| proj017〜021 の README の結果 | `docs/performance/sam45-fine/` の最初の 1 本の材料 | 移植後の .bit で測り直す |

移さないもの: `runs/`（測定の記録）・`build*/`・試行の途中の道具（使わなくなったもの）。必要なら study-rfsoc を指す。

## 手順

| 手順 | すること | 合格 |
|---|---|---|
| M0 | 移植元の commit を決め、上の表を確定する | 表に「移さない」も含めて全ファイルの行き先がある |
| M1 | ファイルを置き直し、パスだけを直す（中身は変えない） | `git diff --stat` で中身の変更がパスの行だけ |
| M2 | sim を全部回す | proj021 と同じ変種がすべて通過し、**出力が bit 単位で同じ**。陽性対照が立つ |
| M3 | ビルド（`-1`、proj021 と同じ実装の戦略） | 下の「同一性の判定」 |
| M4 | 実機で短い回帰 | ID の読み出し・F-1（RUN_T）・W-0・V2-b を短く（5 分）。proj021 と同じ値 |
| M5 | ここで初めて ID を製品の形に変える（別の PR） | [`release.md`](release.md) の手順。変えた後に M2〜M4 をもう一度 |
| M6 | 判定を全部通し、最初の性能評価を書く | `docs/performance/sam45-fine/<版>.md` |
| M7 | spec・design・user を書き、最初のリリース | [`release.md`](release.md) |

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
