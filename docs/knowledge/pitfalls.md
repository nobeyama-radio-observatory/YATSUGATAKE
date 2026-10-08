# 落とし穴

study-rfsoc で実際に踏んだもの。カッコ内は詳しい記録のある proj。

## Vivado・ビルド

- **`settings64.sh` を `.bashrc` で source しない。** 同梱の古い共有ライブラリが `LD_LIBRARY_PATH` の先頭に入り、git・ssh・python が壊れる。`bin/vivado` を絶対パスで叩く
- **`~/.Xilinx/Vivado/Vivado_init.tcl` は全バージョンが読む。** ここに board files の場所を書くと、GUI とバッチで別の board file を見る状態になりうる。`build.tcl` で `set_param board.repoPaths` を明示する
- **board files は Vivado のインストールツリーの中に置かない。** 自動で読まれ、どこに置いたかが記録に残らない。中身の違う同じ名前の board file が同時に見える状態は、どちらが採用されるか不定になる
- **board files の版表記 `1.0` は中身が変わっても据え置かれる。** commit で固定する
- **PS の PL クロックは要求値どおりに出るとは限らない**（200 MHz を要求して 175 MHz になった）。警告も出ない。`CONFIG.FREQ_HZ` を読み返す
- **ボードプリセットは使わない AXI マスタも有効にする。** 使わないものも明示的に 0 にしないと、クロックの無いピンで `validate_bd_design` が落ちる（proj002）
- **.hwh の basename を .bit とそろえる。** PYNQ は同じベース名の .hwh を探す（proj002）
- **Vivado 2024.1 の合成で、OOC の run が「0 errors の後の segfault」で落ちることがある。** 落ちた run だけ回し直す（proj013・proj015）
- `-1` のビルドで board_part を使えない理由は [ADR 0004](../decisions/0004-build-with-speed-grade-1.md)

## RFDC（RF Data Converter）

- **タイル単位の設定は、そのタイルのスライスを有効にするまで黙って無視される**（WARNING 1 行）。順序は「スライス有効化 → スライスの設定 → PLL → Sampling Rate → Refclk → Outclk」。設定後は IP から読み返して検証する（proj003）
- **Outclk（`clk_adcX` の周波数）は AXIS のクロックではない。** AXIS のクロックは IP から出ないので、Clocking Wizard で作る（proj003）
- **Data_Width の範囲外を指定すると、IP は黙って直前の有効値に戻す。** fs 4096 MSPS・Real・デシメーション 1 では 7〜12 で、16 は通らない（proj009）
- **タイル内の AXIS クロックは全スライスで同じでなければならない。** 1 スライスずつ変えると中間状態で弾かれる。まとめて設定する（proj009）
- **制御系（AXI4-Lite）を ADC のクロックに載せない。** `clk_adc` はタイルが起動して初めて出るので、起動のためのレジスタアクセス自体がクロック待ちになる（proj003）
- **ビットストリームを読んだ時点でタイルは起動し、PLL もロックしている。** `StartUp()` や `DynamicPLLConfig()` を呼ぶと動いている状態を壊しうる（proj003）
- **AXIS クロックの源のタイルを先に起動する。** 複数タイルへの `ShutDown()` は順序を直しても成立しない。止めたくなったら Overlay を焼き直す（proj008）
- **Overlay を読んだ直後（数秒）は、インタリーブのイメージが −33〜−39 dBc まで悪い。** 背景較正の収束を待つ（proj009）

## PYNQ

- **`Overlay()` より前に `import xrfdc`。** 忘れると `adc_tiles` が生えない。ドライバが当たったかは `isinstance()` で確かめる。版が食い違うと当たらない
- **`blocks[]` の添字は Vivado のスライス番号と違う。** スライス 0 / 2 → `blocks[0]` / `blocks[1]` に詰まる（proj006。[`hardware.md`](hardware.md)）
- **`xrfclk` の関数名は版で変わる**（v3.1.1 は `set_ref_clks`）
- ADC の取りこぼしは `BlockStatus['IsFIFOFlagsAsserted']` が唯一の検出手段

## クロック・時刻

- **`tile.PLLLockStatus` は LMK の PLL1 ではない。** 外部基準が来ていなくてもロック 2 のまま 90 ppm ずれる。外部基準の確認は ppm で（[ADR 0006](../decisions/0006-external-10mhz-reference.md)）
- **時刻の原点は Overlay ではなく MMCM のロック。** 観測中に MMCM がロックを外すとカウンタが黙って 0 に戻る。原点の番号（epoch）と locked を数える側は、ADC のクロックが落ちても生き残るクロックに置く（proj007 rev2）
- **SG の REF OUT は既定で出ないことがある**（APSYN420: `ROSC:OUTP:STAT ON`）（proj004）
- **ケーブルを挿すと PS のスクリプトの引数を忘れやすい。** 外部基準の指定なしで走らせ、基板の発振器（−15 ppm）で動いた例がある。timebase の見張りが止めた（proj020）

## 混信

- **800 MHz 帯（携帯電話の上り）の混信は、1PPS のケーブルが主な入口**（ボード単体の ≒ 7 倍）。終端のない分配器がさらに ≒ 2 倍。入力を終端しても入る（proj013）
- 1PPS・10 MHz の入口の低域通過フィルタ・遮蔽は未解決（45m では両方とも要る）
