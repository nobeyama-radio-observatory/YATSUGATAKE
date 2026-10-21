# 0021. 仕様の正典は YATSUGATAKE の docs/spec に置き、全 bit の約束をここで持つ

- 状態: 採用
- 決定日: 2026-10-21
- 根拠: study-rfsoc の `INTERFACE.md`・`BITS.md`（commit 6b777bf）、YATSUGATAKE の移植の M7

## 背景

PL ↔ PS ↔ 制御 PC の約束（インターフェース v2）と 9 本の bit の仕様は、study-rfsoc の根元の `INTERFACE.md`・`BITS.md` が正だった。
最初の bit（SAM45-Fine）を YATSUGATAKE からリリースするにあたり、仕様の正をどちらに置くかを決める必要があった（正が 2 つになると必ずずれる。`spec/README.md`）。

## 決定

- **全 bit の仕様の正典を YATSUGATAKE の `docs/spec/` に置く**（`interface.md`・`bits.md`。時刻・単位・ハードウェアは後で分ける）。SAM45-Fine の分だけでなく、まだ作っていない bit の約束と未決事項も含む
- study-rfsoc の `INTERFACE.md`・`BITS.md` は、ここを指す短いファイルにする（中身は study-rfsoc の git の履歴に残る）
- **study-rfsoc の新しい試行は、YATSUGATAKE の版（commit かタグ）を出発点として README に書く**。仕様を変える案は、試行の README の「変更案」の節に書き、採用するときに YATSUGATAKE の PR で `docs/spec/` に入れる
- 節の番号は写す前と同じにする（study-rfsoc の README が「INTERFACE 5.2」のように節で指している）

## 理由

- YATSUGATAKE を磨くたびに、それを出発点に study-rfsoc の開発が続く（開発者の方針）。出発点の仕様が製品の側にあれば、試行は常に製品の約束から始まる
- SAM45-Fine の分だけを写す案では、共通の約束（流れ・リング・s45proto）が両方に残り、2 本目の bit で必ずずれる

## 見送った案

- (a) SAM45-Fine の分だけを YATSUGATAKE に写し、残りは study-rfsoc を正のままにする: 共通の約束が二重になる
- study-rfsoc を正のまま、YATSUGATAKE は写しを持つ: リリースした bit の約束が、試行の都合で書き換わりうる

## 影響

- study-rfsoc で `INTERFACE.md`・`BITS.md` を直接書き換えない（試行の README の変更案 → YATSUGATAKE の PR）
- 仕様の変更が PR を通るぶん遅くなる。試行の途中の案は試行の README に置き、bit を YATSUGATAKE に移すときにまとめて入れる（proj024 の「INTERFACE.md の変更案」の型）
