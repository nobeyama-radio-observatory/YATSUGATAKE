# sw — ソフトウェア

**状態: 移植中（M1）。** study-rfsoc の proj021（`proj021-m0`）の `pynq/` を `pynq/` にそのまま置いた。下の 3 つに分けるのは M1 の後の別の PR（import を直すので。[`docs/migration.md`](../docs/migration.md)）。

| 場所（予定） | 中身 |
|---|---|
| `specd/` | ボードの PS で動くデータ取得サーバー（取得・束ね・送り出し・LOAD） |
| `client/` | 制御 PC・ダウンロード PC 側のクライアント（命令・受信・記録の照合） |
| `tools/` | 較正・測定の道具（リニアリティ・アラン分散・スプリアスなど） |
