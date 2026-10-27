# knowledge — 知見

study-rfsoc の試行（proj001〜020）で分かったことのうち、製品を作り・直し・使う人が知っておくべきものを要約した。
詳しい経緯は、各項目に書いた study-rfsoc の proj を辿る。

| ファイル | 中身 |
|---|---|
| [`verification.md`](verification.md) | **検証の規約。**「動いているように見える失敗」に機械で備える |
| [`judgment.md`](judgment.md) | **判断の型。** 測定を信じてよい条件 |
| [`pitfalls.md`](pitfalls.md) | 踏んだ落とし穴（Vivado・XDC・RFDC・PYNQ・クロック） |
| [`hardware.md`](hardware.md) | RFSoC 4x2 の実測で確定した事実（SMA とタイル・極性・フルスケール・クロック） |
| [`measurement.md`](measurement.md) | 測定の規約（試験音源・減衰量の記録・混信の入口） |
| [`environment.md`](environment.md) | ビルドと実機の環境（版・置き場所・三か所の作業） |
| [`resources.md`](resources.md) | bit ごとの BRAM・URAM・DSP の構成要素ごとの内訳（Fine・Wide・2G-1・2G-2・2G-4） |

**この開発で踏んだ穴は、ほぼすべて「ビルドが通り、実機も動き、症状が出ない」形をしていた。** まず `verification.md` を読む。
