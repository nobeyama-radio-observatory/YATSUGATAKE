# RFSoC 4x2 の実測で確定した事実

出典はリファレンスマニュアル Rev A6 と、study-rfsoc の実測。**SMA のラベルから設計を書かない。** 間違えても「DMA は完走するのに中身がノイズだけ」になるだけで、原因が遠い。

## ADC の SMA とタイル・スライス

| SMA | RF-ADC | PYNQ | 確定 |
|---|---|---|---|
| ADC_A | Tile 226 / slice 2 | `adc_tiles[2].blocks[1]` | proj006 |
| ADC_B | Tile 226 / slice 0 | `adc_tiles[2].blocks[0]` | proj003・006 |
| ADC_C | Tile 224 / slice 2 | `adc_tiles[0].blocks[1]` | proj006 |
| ADC_D | Tile 224 / slice 0 | `adc_tiles[0].blocks[0]` | proj006 |

- **A → D の順にタイル番号もスライス番号も下がる**（ラベルと完全に逆）
- PYNQ の `blocks[]` は有効なスライスを 0 から詰める（スライス 0 / 2 → 0 / 1）
- **Tile 224 と 226 の入力極性は反転している**（厳密な 180°・周波数に依らない）。自己相関では見えないが、相互相関・合成・位相を使う処理では符号を揃える
- タイル内のずれは 0.02 サンプル以内で起動ごとに変わらない。タイル間は 180° ＋ 1〜1.5 サンプル RMS

## レベル

| | 値 | 確定 |
|---|---|---|
| ADC のフルスケール | **0 dBFS ≒ +5.8 dBm**（100 MHz・バラン込み） | proj005 |
| ADC のデータ形式 | 14 bit を 16 bit の上位に寄せる（下位 2 bit は常に 0） | proj003 |
| 入力のバラン | MABA-011118（10 MHz〜10 GHz）。DC 結合ではない | RefMan |
| ch 間の利得差 | 0.2 dB 以内（4 分配・3 GHz） | proj009 |
| 運転の入力レベル | HOT ≦ −10 dBFS（振り切れ）。HOT −10 dBm ≒ −16 dBFS・SKY ≒ −21 dBFS でよい | proj019 |

## クロック

| | 値 | 確定 |
|---|---|---|
| CLK_IN（SMA）の行き先 | LMK04828 の **CLKin0** | proj004 |
| 出荷時の PLL1 の基準 | CLKin1（基板の Si5395 の 10 MHz）。`0x0147` = `0x1A` | proj004 |
| RFDC の基準 | LMX2594 の 491.52 MHz。**出力の強さ PWR 3**（31 だとクロックの櫛 n × 163.84 MHz が立つ） | proj019 |
| fs | 4096.0 MSPS（タイル PLL R 1 / N 25 / M 3） | proj009 |
| 1PPS の入力 | 45m の +2.5 V / 100 µs をそのまま受ける（TRIG・COMP の 2 系統）。外付けのレベル変換も PULLUP も要らない | proj007 |
| 自走の PL クロック | SYS_CLK_100M 100 MHz（Si5395）。RFDC のサンプリングクロックとは別経路 | proj001 |

## 固定のスプリアス

- k·fs/8（512・1024・1536 MHz、IF では 2560・3072・3584 MHz）: 8 並列インタリーブ。較正の収束後で −53〜−66 dBc、取得ごとに 5〜10 dB 揺れる
- n × 163.84 MHz: LMX の 491.52 MHz の経路のクロックの櫛。PWR 3 で下がる
- どちらも運転のレベルでは揺れず、チョッパーホイールの Ta* では消える（proj019）

## その他

- 書き込みは PROG UART（microUSB）。USB DEVICE のポートに挿すと JTAG が見えない
- ZU48DR のビルドには Vivado ML Enterprise のライセンスが要る（無償版は対象外）
