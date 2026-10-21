# ビルドと実機の環境

## 版

| | 版 |
|---|---|
| Vivado | 2024.1（ML Enterprise のライセンスが要る） |
| PYNQ イメージ | RFSoC-PYNQ v3.1.1 |
| Board files | RealDigitalOrg/RFSoC4x2-BSP `board_files/rfsoc4x2/1.0`、commit `40e6814a3b62eead76e41a29fdabc43030f89b6c` |
| Part | `xczu48dr-ffvg1517-1-e` でビルドする（[ADR 0004](../decisions/0004-build-with-speed-grade-1.md)）。board file の宣言は `-2` |

版の決定は [ADR 0003](../decisions/0003-platform-rfsoc4x2-pynq.md)。正の表は [`../spec/hardware.md`](../spec/hardware.md)。

## 三か所で作業する

| 場所 | すること |
|---|---|
| 編集の計算機 | ソースの編集・commit・push |
| Vivado の計算機 | GitHub から直接 pull して `make`（sim・合成〜ビットストリーム・タイミングの確認） |
| ボード（PYNQ） | .bit・.hwh・PS のソフトを置いて実機の判定 |

- Vivado の計算機は GitHub から直接 pull する（編集の計算機を中継しない）
- **今どのディレクトリでビルドしたかを必ず確かめる**（[`verification.md`](verification.md)）

## 置き場所の原則

- 環境に依る値（Vivado の場所 `XILINX_VIVADO`・board files の場所 `BOARD_REPO`）は Makefile に持つ。**値そのもの（ホスト名・ユーザ名・パス）はリポジトリに書かない**
- board files は Vivado のインストールツリーの外に clone し、`board.repoPaths` で指す
- ライセンスの Host ID・ベンダのアカウント・`.lic` はリポジトリに入れない（`.gitignore` にも入れてある）

## 実機

- PYNQ v3.1.1 の SD カード。古い版のカードは別に残しておく（古い試行を再現できる唯一の実体）
- 10 MHz（CLK_IN）と 1PPS を観測所から配る。混信の入口になるので配線に注意（[`pitfalls.md`](pitfalls.md)）
