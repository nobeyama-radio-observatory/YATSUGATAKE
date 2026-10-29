# decisions — 決定記録（ADR）

**なぜ今の形なのか**を残す場所。仕様そのもの（今の正しい値）は [`../spec/`](../spec/) に書き、ここには決定・理由・見送った案を書く。

## 規則

- **1 件 1 ファイル。** ファイル名は `NNNN-<短い英語の名前>.md`（番号は 4 桁、詰めて増やす）
- **書いたら書き換えない**（誤字と、リンクの追加は可）。決定が変わったら新しい ADR を足し、古い ADR の状態を「置き換え: NNNN」にする
- **状態**: 提案 / 採用 / 置き換え / 取り下げ
- **根拠**は study-rfsoc の proj を指す。study-rfsoc の proj は完了後に中身を書き換えない運用（追記はある）なので、proj の名前で辿れる。移植のときに、参照した commit を [`../migration.md`](../migration.md) に 1 つ記録する
- 0001〜0020 は、リポジトリを作ったとき（2026-10-08）に study-rfsoc の試行から書き起こした初版。**決定の日付は、study-rfsoc で決めた日**

## ひな形

```markdown
# NNNN. <決定を一文で>

- 状態: 提案 / 採用 / 置き換え（→ NNNN）/ 取り下げ
- 決定日: YYYY-MM-DD
- 根拠: study-rfsoc projNNN（・INTERFACE.md の節など）

## 背景
<何に困っていたか。何が分かっていたか>

## 決定
<何をするか>

## 理由
<なぜそれか。測った数字があれば数字で>

## 見送った案
- <案>: <なぜ採らなかったか>

## 影響
<何がこれに縛られるか。後で見直す条件>
```

## 一覧

| ADR | 決定 | 状態 | 決定日 |
|---|---|---|---|
| [0001](0001-separate-trial-and-product-repositories.md) | 試行（study-rfsoc）と製品（YATSUGATAKE）のリポジトリを分ける | 採用 | 2026-10-08 |
| [0002](0002-migrate-from-proj021-restructure-only.md) | 移植は proj021 を土台にし、構成替えだけを行う | 採用 | 2026-10-08 |
| [0003](0003-platform-rfsoc4x2-pynq.md) | ボードは RFSoC 4x2、制御は PYNQ のオーバーレイ。版を固定する | 採用 | 2026-09-15 |
| [0004](0004-build-with-speed-grade-1.md) | 速度グレード `-1` でビルドし、PS のプリセットを明示して当てる | 採用 | 2026-10-01 |
| [0005](0005-direct-sampling-4096msps-zone2.md) | fs 4096 MSPS・第 2 ナイキストで IF 2〜4 GHz を間引かずに PL へ | 採用 | 2026-09-18 |
| [0006](0006-external-10mhz-reference.md) | 周波数の基準は観測所の 10 MHz（CLK_IN = LMK の CLKin0） | 採用 | 2026-09-17 |
| [0007](0007-no-mts-no-pps-into-adc.md) | MTS を使わず、1PPS を ADC に入れない（時刻の要求 100 µs） | 採用 | 2026-09-18 |
| [0008](0008-time-labels-beat-counter-and-start-at.md) | 時刻は 256 MHz のビートと 1PPS のスタンプで貼り、開始は予約したビートで | 採用 | 2026-10-02 |
| [0009](0009-time-grid-and-integration-time.md) | 時刻の格子 2.048 ms・dt 40.96 / 10.24 ms・TP 1.024 ms | 採用 | 2026-10-02 |
| [0010](0010-nine-bitstreams-switched-by-overlay.md) | 9 本の bit を Overlay で切り替え、bit の中の構成はレジスタで | 採用 | 2026-10-02 |
| [0011](0011-narrowband-windows-coarse-pfb-ddc.md) | 狭帯域の窓は粗い PFB ＋ NCO ＋ 半帯域の縦続 ＋ 複素 4096 点 FFT | 採用 | 2026-09-29 |
| [0012](0012-window-pfb-t4.md) | 窓の分光に PFB（T = 4、sinc × Kaiser β 5・bw 1.198） | 採用 | 2026-10-07 |
| [0013](0013-fft-ip-realtime-and-startup-guards.md) | FFT IP は realtime・資源優先。起動の途切れは多段で守る | 採用 | 2026-09-28 |
| [0014](0014-config-capture-and-health-word.md) | 設定は RUN / WRST で取り込み、CFG_ID と健全性の語をダンプに貼る | 採用 | 2026-10-02 |
| [0015](0015-intensity-unit-and-lmx-power.md) | 強度の単位（abs の式）と LMX の出力 PWR 3 | 採用 | 2026-10-07 |
| [0016](0016-interface-v2.md) | インターフェース v2（流れと自己記述・PL が書くリング・float32・束ね・LOAD） | 採用 | 2026-10-08 |
| [0017](0017-specd-acquisition-server.md) | データ取得サーバー specd の形（行単位の命令・2 プロセス・ACK まで保持） | 採用（一部 0016 で置き換え） | 2026-10-05 |
| [0018](0018-release-on-github-releases.md) | .bit は git に入れず GitHub Releases に。版は 2 段 | 提案 | 2026-10-08 |
| [0019](0019-license-bsd-3-clause.md) | ライセンスは BSD-3-Clause、著作権者は国立天文台 | 採用 | 2026-10-08 |
| [0020](0020-documentation-language.md) | ドキュメントは日本語で書き、英語版は後で足す | 採用 | 2026-10-08 |
| [0021](0021-spec-canonical-in-yatsugatake.md) | 仕様の正典は YATSUGATAKE の docs/spec に置き、全 bit の約束をここで持つ | 採用 | 2026-10-21 |
| [0022](0022-2g-1-fast-and-fine.md) | 2G の 1 ADC を 2G-1-Fast（1 段）と 2G-1-Fine（2 段・DDR の corner turn）の 2 本に | 採用 | 2026-10-28 |
| [0023](0023-time-calibration-per-board.md) | 時刻の較正はボードごとに設置の後で測り、ボードにだけ置く（bit ごとには測らない） | 採用 | 2026-10-29 |
