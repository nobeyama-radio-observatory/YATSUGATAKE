# 公開前の確かめ

**git の履歴は消せない。** 公開後に削除しても、コミットは SHA を指定して当面取得でき、fork やキャッシュにも残る。
「公開するときに消す」は成立しないので、commit・push の前に機械で洗う。**目視では見落とす**
（study-rfsoc の初回の公開では、手順の説明の例として書いたライセンスの Host ID そのものが混入していた）。

## 道具

```bash
sh tools/install-hooks.sh              # clone したら最初に 1 回（commit-msg と pre-push のフック）
python3 tools/prepublish_scan.py       # 作業ツリー ＋ 未 push のコミット
python3 tools/prepublish_scan.py --all # 作業ツリー ＋ 全履歴（private → public に切り替える前）
```

手元だけの追加パターン（自分の姓・機器のシリアル・内部のホスト名など）は、根元の `.prepublish-patterns`（`.gitignore` 済み）に
1 行 1 個の正規表現で書く。**パターン自体が公開してはいけない値なので、リポジトリに入れない。**

## スキャンの手順

| 手順 | 何を | パターン（要旨） |
|---|---|---|
| 0 | 置かないもの | `.lic`・`.bit`・`.hwh`・`.xsa`・測定の記録・5 MB を超えるファイル |
| 1 | MAC アドレス・Host ID・機器のシリアル | `xx:xx:xx:xx:xx:xx`・区切りなしの 12 桁の 16 進 |
| 2 | 個人情報・ホームパス | 組織のメールのドメイン・`/home/<user>`・`/Users/<user>`・メールアドレス・手元の追加パターン |
| 3 | 内部システム名・組織内の呼称 | 作業記録・資金の名前など |
| 4 | 私的 URL | `claude.ai`・OneDrive・SharePoint・Google Drive / Docs |
| 5 | IP アドレス | IPv4（ループバック 127.0.0.0/8・0.0.0.0・RFC 5737 の文書用の範囲は除く） |
| 6 | 隠しファイルの残骸 | `.DS_Store`・エディタの設定（`.gitignore`・`.github/` は除く） |
| 7 | 外部リンクの棚卸し | 一覧を出す。**すべて公開の資料かを目で確かめる** |
| 8 | コミットの作者 | 一覧を出す。**作者のメールは全コミットに永久に残る。** 公開してよいアドレスか（GitHub の noreply を使う選択もある） |
| 9 | コミットメッセージ | `claude.ai`・`Claude-Session:`・`session_`・OneDrive・SharePoint・組織のメールのドメイン |

手順 1〜6 は作業ツリーのファイルしか見ない。**コミットメッセージは手順 9 で別に洗う。**

## 置き換えの指針

| 見つかったもの | 置き換え |
|---|---|
| MAC アドレス | RFC 7042 の文書用の範囲 `00:00:5e:00:53:xx` |
| 機器のシリアル | `<serial>` などのプレースホルダ |
| IP アドレス | RFC 5737 の文書用の範囲 `192.0.2.xx`（または `<host>`） |
| ホスト名・ユーザ名 | `<host>` / `<user>` |
| 内部システム名 | 「リポジトリ外の作業記録」などに一般化する |
| 自分の環境の設定値 | 「たとえば」を付けて例示に変える（自分の値だと読めないように） |
| 内部の審議のメモ | 削除 |

## AI にコミットさせるとき

AI エージェントは、コミットメッセージの末尾に `Claude-Session: https://claude.ai/code/session_…` を既定で付けることがある。
**最初に「コミットメッセージに `Claude-Session:` の行や URL を入れない」と伝える。** `Co-Authored-By: Claude …` の行は URL を含まないので可。
`tools/hooks/commit-msg` が機械で止める。

- push の前に見つけたら: `git commit --amend` でその行を消す（最新のコミットなら）
- push 済みなら: 消すには履歴の書き換えと force push が要る。判断して残すなら、残したことを記録する

## 事前の歯止め

- **まず private で作り、内容を確かめてから public に切り替える**
- GitHub でリポジトリを作るとき、「Add a README」「Add .gitignore」「Choose a license」は外す（手元にあるものと履歴が繋がらなくなる）
- メールアドレスを公開したくなければ、GitHub の Settings → Emails の「Block command line pushes that expose my email」を有効にする
