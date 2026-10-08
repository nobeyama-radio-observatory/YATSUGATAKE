# 開発の進め方

## 試行と製品の分担

このリポジトリは**製品**の置き場です。結果がまだ読めない試行（方式の比較・原因の切り分け・陽性対照の実験など）は、
開発用リポジトリ [study-rfsoc](https://github.com/ars096/study-rfsoc) の projNNN で行います。
理由は [ADR 0001](docs/decisions/0001-separate-trial-and-product-repositories.md)。

| 作業 | 場所 |
|---|---|
| 結果が読めない試行 | study-rfsoc の projNNN（自己完結・失敗も残す） |
| 製品のコード・仕様を変える作業（複数の bit のビルドで見つかった問題の修正を含む） | このリポジトリで issue → ブランチ → PR |
| 試行の結果、仕様が変わるとき | このリポジトリに ADR を 1 本足し、根拠として study-rfsoc の proj を指す |

## 変更の流れ

1. **issue を立てる。** 何を変えるか・なぜか・どの bit に効くか
2. **ブランチで作業する。** main に直接 push しない
3. **変更は一度に一つ。** 構成替え・機能の追加・不具合の修正を同じ PR に混ぜない。ずれたときに原因を切り分けられなくなる
4. **PR に回帰の結果を付ける**（[PR のひな形](.github/pull_request_template.md)）
   - RTL を変えたら、影響する bit すべてで sim（bit 単位の照合と陽性対照）
   - 速度グレード `-1` でタイミングが閉じること（[ADR 0004](docs/decisions/0004-build-with-speed-grade-1.md)）
   - CDC の分類ごとの件数・BRAM・DSP の変化
   - 実機の判定（[`test/acceptance/`](test/acceptance/)）。どれを回したかを書く
5. **仕様が変わるなら**、同じ PR で `docs/spec/` を更新し、ADR を足す

## ドキュメントの規則

- **`docs/spec/` は上書きで更新する**（今の正しい仕様だけを書く）。経緯は書かない
- **`docs/decisions/` は追記だけ。** 決定が変わったら、古い ADR を消さずに「置き換え: ADR NNNN」と書き、新しい ADR を足す
- 測定の結果には、**何で何を測ったか**（信号源・減衰器・分配器・ケーブル）を必ず書く（[`docs/knowledge/measurement.md`](docs/knowledge/measurement.md)）
- 日本語で書く。英語版は後で足す（[ADR 0020](docs/decisions/0020-documentation-language.md)）

## 公開リポジトリであること

**git の履歴は消せません。** commit・push の前に、次を守ってください。

- clone したら最初に `sh tools/install-hooks.sh` を実行する（コミットメッセージの検査が入る）
- push の前に `python3 tools/prepublish_scan.py` を実行する（[`docs/publishing.md`](docs/publishing.md)）
- 書かないもの: ライセンスの Host ID・ベンダのアカウント・`.lic` の中身・個人のホームパス・ホスト名・IP アドレス・内部システムの名前・限定共有の URL
- **AI にコミットさせるときは、コミットメッセージに `Claude-Session:` の行やセッションの URL を入れさせない**（`Co-Authored-By` の行は可）
