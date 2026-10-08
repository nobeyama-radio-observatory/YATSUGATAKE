# tools — リポジトリの道具

| ファイル | 用途 |
|---|---|
| `prepublish_scan.py` | 公開前スキャン（[`../docs/publishing.md`](../docs/publishing.md) の手順 1〜9） |
| `install-hooks.sh` | clone したら最初に 1 回。git のフックを `hooks/` に向ける |
| `hooks/commit-msg` | コミットメッセージにセッションの URL などが入っていたら止める |
| `hooks/pre-push` | push の前に公開前スキャンを走らせる |
