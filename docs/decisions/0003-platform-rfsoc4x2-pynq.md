# 0003. ボードは RFSoC 4x2、制御は PYNQ のオーバーレイ。版を固定する

- 状態: 採用
- 決定日: 2026-09-15（Vivado 2024.1 への移行）・2026-09-16（PYNQ v3.1.1 の確認）
- 根拠: study-rfsoc proj001・proj002・VERSIONS.md

## 背景

SAM45 の後継の分光計を、RealDigital RFSoC 4x2（XCZU48DR-FFVG1517）の上に作る。PS（ARM）と PL（FPGA）の間の制御とデータの取り出しを、どの仕組みで行うかと、ツールの版をどう揃えるかを決める必要があった。

## 決定

- **制御系は PYNQ のオーバーレイ**（.bit と同じベース名の .hwh を並べ、`Overlay()` で読む）
- 版を次で固定する

| | 版 |
|---|---|
| Vivado | 2024.1 |
| PYNQ イメージ | RFSoC-PYNQ v3.1.1 |
| Board files | RealDigitalOrg/RFSoC4x2-BSP の `board_files/rfsoc4x2/1.0`、commit `40e6814a3b62eead76e41a29fdabc43030f89b6c` |

- ビルドは project mode（.hwh はブロックデザインからしか出ないため）

## 理由

- BSP の board files と PYNQ v3.1.1 が、いずれも Vivado 2024.1 を前提にしている。イメージ側を v3.1.1 に上げて揃えるのが唯一の整合（逆に Vivado を下げると board files とずれる）
- **board files の版表記 `1.0` は中身が変わっても据え置かれる**（DDR の行アドレス幅の修正が `1.0` のまま入った例がある）。commit でしか識別できない
- RF Data Converter は `xrfdc` / `xrfclk` ドライバと IP の版が結合する。版が食い違うとドライバが当たらない

## 見送った案

- **非プロジェクトモード**: .hwh が出ず、PYNQ から使えない
- **`Overlay(..., ignore_version=True)` で版の不一致を逃げる**: 版の合わない IP が動かない可能性があり、恒久策にならない

## 影響

- 版を上げるときは新しい ADR を書き、全 bit を回帰する
- 環境の作り方は [`../knowledge/environment.md`](../knowledge/environment.md)
