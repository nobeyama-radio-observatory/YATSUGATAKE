# リリースと版

- 状態: **確定**（2026-10-21、最初のリリース SAM45-Fine v1.0.0 の前に。[ADR 0018](decisions/0018-release-on-github-releases.md)）

## 何を配るか

GitHub Releases に、bit ごとに次を添付する。**git の履歴には入れない。**

| ファイル | 中身 |
|---|---|
| `<bit>-<版>.bit`・`<bit>-<版>.hwh` | PYNQ の Overlay で読む組。.hwh の絶対パス（SAM45-Wide の ROM の hex ファイル）はファイル名だけにする |
| `<bit>-<版>.timing.txt` | `-1` の WNS / WHS と最悪経路の要約 |
| `<bit>-<版>.utilization.txt` | 資源 |
| `<bit>-<版>.cdc.txt` | `report_cdc` の分類ごとの件数 |
| `<bit>-<版>.bitinfo.txt` | USR_ACCESS（commit・汚れ）と FDRI の sha256 |
| `<bit>-<版>.build.log` | `vivado.log` の**要約**（TIMING・ERROR・CRITICAL WARNING・NOTE の行、絶対パスは `<path>`）。**生のログは配らない** |
| `SHA256SUMS` | 全ファイルの sha256 |

この組は `tools/release_files.py` が作る（USR_ACCESS・FDRI を照らし、公開してはいけない形が無いことを確かめてから書く）。

PS のソフト（specd）と較正ファイルはソースから入れる（版のタグで固定）。

## 版の付け方

| 版 | 例 | 上げるとき |
|---|---|---|
| リポジトリ全体 | `v1.0.0` | インターフェース（IF_VER）・specd・s45proto の互換性が変わるとき（major）、機能を足すとき（minor）、直すとき（patch） |
| bit ごと | `sam45-fine/v1.0.0` | その bit の RTL・係数・制約が変わるとき |

- bit のタグは、その bit を作ったときのリポジトリ全体の commit を指す
- 同じ commit から 2 本の bit を出してよい（bit ごとのタグが 2 つ付く）

## 実機から版を辿る

| どこで | 何で |
|---|---|
| .bit の中 | USR_ACCESS（32 bit）: [31:4] commit の短いハッシュ 7 桁・[3:1] 0・[0] 作業ツリーの汚れ（**M5b で入れた**。`make` が git から作って焼き、`sw/pynq/bitinfo.py` で読み返す。FPGA の中からは読まず、PS が載せる .bit から読む。配置は変わらない: FDRI が焼かない bit と同じ） |
| 自己記述のレジスタ | IF_ID の BIT_KIND・BIT_REV（較正の表を引く鍵） |
| ボードの `bits.json` | 名前 → .bit・.hwh・sha256・期待する IF_ID・較正ファイル |
| s45proto の EVENT LOAD | bit の名前・sha256・IF_ID |

決めること（proj021 と最初のリリースで）:

- [x] USR_ACCESS に何を入れるか → commit の 28 bit ＋ 汚れの 1 bit（2026-10-15、[migration.md](migration.md) の M5）
- [x] 同じ RTL で USR_ACCESS だけ違う 2 本の WNS が一致することを確かめる → WNS・WHS が小数 6 桁まで、FDRI の sha256 まで一致（2026-10-15、M5b）
- [x] BIT_REV と bit ごとの版の対応 → **対応表を bit の README に持つ**（2026-10-21）。下の「BIT_REV と版」
- [x] ビルドを誰がどこで行い、ログから環境に依る値をどう除くか → **開発者が Vivado の計算機で、リリースの commit を GitHub から pull してビルドする。ログは要約だけを配る**（`tools/release_files.py`。2026-10-21）

## BIT_REV と版

- **RTL・係数・制約を変えたら BIT_REV を上げ、bit の版は minor 以上を上げる**（開発の CAL・遅れの定数は (BIT_KIND, BIT_REV) で引くので、古い値が新しい bit に黙って当たらない）。ADC → コアの道や TP の作りを変えたら `timebase.ADC_PATH` に新しい番号を足す（ボードの較正ファイルが当たらなくなる。ADR 0023・0025）
- PS（specd・較正）だけの変更では bit の版を上げない（リポジトリ全体の版を上げる）
- **同じ RTL の作り直し**（リリースの commit で焼き直すなど）は BIT_REV も bit の版も変えない。FDRI の sha256 が前と同じであることで同じものと言う（USR_ACCESS だけが違う。M5b）
- 対応表（版 ↔ BIT_REV ↔ USR_ACCESS ↔ FDRI の sha256）は `hw/bits/<bit>/README.md` に置き、リリースごとに 1 行足す

## リリースの手順

**タグはビルドした commit に付ける**（USR_ACCESS = タグの commit になる）。だからビルドの前に、CHANGELOG と性能評価を main に入れておく。ビルドで初めて決まる値（.bit の sha256）は Release の `SHA256SUMS` が正で、文書には後から足す。

1. CHANGELOG の版の節と性能評価 `docs/performance/<bit>/<版>.md` を書き、PR で main に入れる
2. その main の commit で、Vivado の計算機で GitHub から pull する。作業ツリーが汚れていないこと
3. `-1` でビルドし、タイミング・CDC・資源を確かめる。**ほかのビルドと重ねない**（[`knowledge/pitfalls.md`](knowledge/pitfalls.md)）。make の出力を残すなら作業ツリーの外か `build/` の中に書く（例: `make clean && nohup make JOBS=16 > ~/sam45-fine-build.out 2>&1 &`。作業ツリーに置くと、ホームパスを含むので公開前スキャンが push を止める）
4. `tools/release_files.py <build> <bit> <版> --out dist/<bit>-<版> --commit <7 桁> [--fdri <前の FDRI>]` で添える組を作る（照合が通ること）
5. 判定（`test/acceptance/`）を通す。**同じ RTL の作り直しで FDRI が前と同じなら、前の判定を引き継ぐ**（実機では ID-1 と F-0 だけ確かめる）
6. その commit にタグ（`<bit>/<版>`）を付けて push し、Release を作って 4. の組を添付する
7. 後の PR で、bit の README の対応表に 1 行足し、性能評価に配った .bit の sha256・USR_ACCESS を書く（`python3 tools/prepublish_scan.py` を通す）
