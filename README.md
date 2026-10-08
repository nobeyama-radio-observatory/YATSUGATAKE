# YATSUGATAKE — RFSoC 4x2 電波分光計

野辺山 45m 鏡の分光計 SAM45 の後継として、AMD RFSoC 4x2（XCZU48DR）の上に作る電波分光計です。
このリポジトリは**製品版**の置き場で、配布する .bit とその設計・仕様・性能評価を持ちます。

> **状態: 準備中。** 最初の bit（SAM45-Fine）は開発用リポジトリ
> [study-rfsoc](https://github.com/ars096/study-rfsoc) の proj021 で作っており、完成後にここへ移します
> （[`docs/migration.md`](docs/migration.md)）。
>
> English: YATSUGATAKE is a radio spectrometer for the Nobeyama 45 m telescope built on the
> AMD RFSoC 4x2 board. This repository will hold the released bitstreams, their design and
> specifications. Documentation is currently in Japanese; an English version is planned.

## 何ができるか（予定）

- IF 2〜4 GHz を 4 入力、4096 MSPS で直接サンプリング（第 2 ナイキスト）
- 用途ごとに 9 本の bit を用意し、PYNQ の Overlay で切り替える（全帯域・広帯域・狭帯域の窓）
- 観測所の 10 MHz と 1PPS に同期した時刻ラベル、ADC ごとの total power（1.024 ms）
- ボード上のデータ取得サーバー（specd）から、ネットワーク越しにスペクトルを受け取る

bit ごとの仕様は [`docs/spec/`](docs/spec/) に置きます（移植時に整備）。

## リポジトリの構成

| 場所 | 中身 |
|---|---|
| [`docs/spec/`](docs/spec/) | **仕様の正典**。今の正しい仕様（上書きで更新） |
| [`docs/decisions/`](docs/decisions/) | 決定記録（ADR）。なぜそうしたか・見送った案（追記のみ） |
| [`docs/knowledge/`](docs/knowledge/) | 知見: 検証の規約・落とし穴・ハードウェアの実測値 |
| [`docs/design/`](docs/design/) | 設計の解説（共通コアと bit ごとの中身） |
| [`docs/performance/`](docs/performance/) | 性能評価（bit × リリースごと） |
| [`docs/user/`](docs/user/) | 使い方（設置・結線・specd・クライアント） |
| [`hw/`](hw/) | PL の設計（共通コア・ボード固有・bit ごと） |
| [`sw/`](sw/) | PS のソフト（specd）・制御 PC 側のクライアント・道具 |
| [`test/acceptance/`](test/acceptance/) | 判定（受け入れ試験）の手順 |
| [`tools/`](tools/) | リポジトリの道具（公開前スキャン・git のフック） |

開発の進め方は [`CONTRIBUTING.md`](CONTRIBUTING.md) にあります。

## 入手

リリースされた .bit・.hwh は GitHub Releases に添付します（git の履歴には入れません）。
版の付け方は [`docs/release.md`](docs/release.md) を見てください。

## 関係するリポジトリ

- [study-rfsoc](https://github.com/ars096/study-rfsoc) — 試行の記録（proj001〜）。このリポジトリの設計の根拠の多くはここにあります

## ライセンス

[BSD 3-Clause License](LICENSE)。各ソースファイルには `SPDX-License-Identifier: BSD-3-Clause` を記載し、
著作権者の表記は `LICENSE` の 1 か所にだけ持ちます。
