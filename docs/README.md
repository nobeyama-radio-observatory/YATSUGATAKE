# docs — ドキュメントの地図

ドキュメントを**役割**で分ける。同じことを 2 か所に書かない。

| 場所 | 問い | 更新のしかた |
|---|---|---|
| [`spec/`](spec/) | **今、何が正しいか**（仕様） | 上書き。経緯は書かない |
| [`decisions/`](decisions/) | **なぜそうしたか**（ADR） | 追記だけ。変わったら新しい ADR で置き換える |
| [`knowledge/`](knowledge/) | **何に気をつけるか**（検証の規約・落とし穴・実測値） | 新しい知見が出たら足す |
| [`design/`](design/) | **bit の中はどうなっているか**（設計の解説） | 設計とそろえて更新 |
| [`performance/`](performance/) | **どれだけ出ているか**（性能評価） | リリースごとに 1 本。過去のものは書き換えない |
| [`user/`](user/) | **どう使うか** | 使い方が変わったら更新 |
| [`migration.md`](migration.md) | study-rfsoc からの移植の手順と合否 | 移植が終わったら完了と書いて残す |
| [`migration-sam45-wide.md`](migration-sam45-wide.md)・[`migration-2g-4.md`](migration-2g-4.md) | SAM45-Wide・2G-4 の移植（Fine と違うところだけ） | 同上 |
| [`release.md`](release.md) | リリースと版の付け方 | |
| [`publishing.md`](publishing.md) | 公開前の確かめ | |

## 読む順（初めての人）

1. [`../README.md`](../README.md) — 何のリポジトリか
2. `spec/` — 仕様
3. [`knowledge/verification.md`](knowledge/verification.md) — この開発で守っている検証の規約
4. [`decisions/`](decisions/) の一覧 — なぜ今の形なのか
