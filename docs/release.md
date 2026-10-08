# リリースと版

- 状態: **案**（[ADR 0018](decisions/0018-release-on-github-releases.md)、提案）。最初のリリースまでに確定する

## 何を配るか

GitHub Releases に、bit ごとに次を添付する。**git の履歴には入れない。**

| ファイル | 中身 |
|---|---|
| `<bit>-<版>.bit`・`<bit>-<版>.hwh` | PYNQ の Overlay で読む組 |
| `<bit>-<版>.timing.txt` | `-1` の WNS / WHS と最悪経路の要約 |
| `<bit>-<版>.utilization.txt` | 資源 |
| `<bit>-<版>.build.log` | ビルドのログ（環境に依る値を除いたもの） |
| `SHA256SUMS` | 全ファイルの sha256 |

PS のソフト（specd）と較正ファイルはソースから入れる（版のタグで固定）。

## 版の付け方（案）

| 版 | 例 | 上げるとき |
|---|---|---|
| リポジトリ全体 | `v1.0.0` | インターフェース（IF_VER）・specd・s45proto の互換性が変わるとき（major）、機能を足すとき（minor）、直すとき（patch） |
| bit ごと | `sam45-fine/v1.0.0` | その bit の RTL・係数・制約が変わるとき |

- bit のタグは、その bit を作ったときのリポジトリ全体の commit を指す
- 同じ commit から 2 本の bit を出してよい（bit ごとのタグが 2 つ付く）

## 実機から版を辿る

| どこで | 何で |
|---|---|
| .bit の中 | USR_ACCESS（32 bit）に commit の短いハッシュなど（**案**。配置を変えない方法なので「同じ RTL の作り直しは WNS まで再現する」が保たれる） |
| 自己記述のレジスタ | IF_ID の BIT_KIND・BIT_REV（較正の表を引く鍵） |
| ボードの `bits.json` | 名前 → .bit・.hwh・sha256・期待する IF_ID・較正ファイル |
| s45proto の EVENT LOAD | bit の名前・sha256・IF_ID |

決めること（proj021 と最初のリリースで）:

- [ ] USR_ACCESS に何を入れるか（commit の 28 bit ＋ 汚れの 1 bit など）
- [ ] 同じ RTL で USR_ACCESS だけ違う 2 本の WNS が一致することを確かめる
- [ ] BIT_REV と bit ごとの版の対応
- [ ] ビルドを誰がどこで行い、ログから環境に依る値をどう除くか

## リリースの手順（案）

1. main の commit を決める。作業ツリーが汚れていないこと
2. `-1` でビルドし、タイミング・CDC・資源を確かめる
3. 判定（`test/acceptance/`）を通す
4. 性能評価 `docs/performance/<bit>/<版>.md` を書く
5. CHANGELOG を更新する
6. `python3 tools/prepublish_scan.py` を通す
7. タグを付けて push し、Release を作ってファイルを添付する
