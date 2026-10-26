# SAM45-Wide の判定（受け入れ試験）

SAM45-Wide の bit（BIT_KIND 1・BIT_REV 1、study-rfsoc の proj023 ビルド 11 と FDRI が同じ）と、それに載せる PS（`sw/pynq/`）を、リリースの前に実機で通す判定。
1 判定 1 ファイル。書き方は 6 項目（ID・前提・手順・合格・陽性対照・記録）。**合格は測る前に書く**。

proj023 の判定は README の中にだけあった（H-1〜H-4・SNAP・F-2・V2-b など）。移植の M6 の前に、ここへファイルとして書き起こした（2026-10-23）。
判定の ID は proj023 で使ったものをそのまま使う（H-1・H-2・H-4・V2-a・V2-b など）。proj023 で ID の無かったものだけ新しく付けた（H-0 雑音の 7 本）。

## 共通の前提

- **bit**: SAM45-Wide（`proj023.bit`）。`wide.py --list` で IF_ID 0x0201_0101（4 コア）・time_core 0x0201_0102・PROJ 0x0023_0100
- **クロック**: 外部 10 MHz と 1PPS（PPS Clk の入力。入口に LPF を常設）。道具は `--clkin 0 --ref 10`
- **LMX2594 の出力の強さ**: PWR 3（specd と Wide の道具の `--lmx-pwr` の既定。2026-10-23 に Fine と合わせた）。ID の `lmx_pwr` で記録に残る
- **宛先**: 環境変数 `B`（ボード）・`SG`（信号発生器。Wide の道具は `RFSOC_SG` か `--sg`）・`PM`（パワーメーター）・`ATT`（プログラムアッテネータ）に入れる。宛先はファイルに書かない
- **道具の置き場所**: ボードの Wide のディレクトリ（`sw/pynq/` の全部・`proj023.bit`・`proj023.hwh`・`bits.json`）と、制御 PC の `sw/pynq/` の受け側（specctl・specrecv・s45proto・s45client など）
- **bits.json**: 既定は `sam45-wide`（`"kind": "wide"`・`sha256` 付き）。V2-d のために Fine の bit（`kind` なし）を 1 件
- **2 つの動かし方**:
  - 「ボード直」: ボードで root、**specd を止めてから**（Overlay を自分で載せる道具）。`sudo -E $(which python3) <道具>.py …`
  - 「specd」: ボードで `sudo -E $(which python3) specd.py --clkin 0 --ref 10 --bits bits.json`、制御 PC から specctl・specrecv など。**`--wide` は付けない**（bits.json の `kind` で Wide の取得が起きる）
- **SG**: E8257D は −5 dBm より下で unleveled になる（`sg.py` は unleveled なら止まる）。低いレベルが要るなら SG の出口に固定減衰器。**掃引の前に SG を 300 s 温める**（H-1 の 1 回目で、入れた直後の漂い −0.08 dB を見た）
- **配線**（今の実験室。値は配線に依る。2026-10-21 に分配器を替えた後の形）:

| 名前 | 中身 | ADC での強さ |
|---|---|---|
| 配線 N | ノイズソース → BPF 2.1〜3.9 GHz → 2 分配器 A（もう一方の口に SG、出力 OFF）→ PATT 13 dB → 2 分配器 B →（ATT 20 dB → PM）・（ATT 3 dB → 4 分配器 → ADC_A〜D）。**SG は BPF を通らない**（2026-10-23 に実験者が確かめた。はじめ BPF を PATT の後に書いていたのは誤り） | ≒ −31.4 dBFS |
| 配線 NS | 配線 N のまま SG の口を出力 ON（ノイズは入ったまま）。**H-1 だけはノイズソース OFF・PATT 0 dB**（P_off で消えるのは雑音の平均だけで、CW × 雑音の交差項の揺れが残る。H-1 の前提の改め、2026-10-23） | SG 0 dBm で CW が ch の中央値の 21.9・13.9・10.3 dB 上（H-2 の B 1・2・4、2026-10-23。proj023 の 10-17 は分配器を替える前で 25.0・20.5・16.1） |
| 配線 P | 1PPS を分配して PPS Clk と ADC_A〜D に | — |

- BPF の通過域の肩（2.1 GHz・3.9 GHz の近く）は、床の推定に幅のある形として出る（2130 MHz、2026-10-23 の櫛の比べで踏んだ）。線を数える判定では肩を避けるか、そうと書く

## 一覧

| ID | 何を確かめるか | 動かし方 | 配線 | proj023 で |
|---|---|---|---|---|
| [ID-1](ID-1.md) | 自己記述・起動の見張り（FLAGS・IP の位相） | ボード直 | どれでも | 通過（ビルド 11、Overlay 5 回） |
| [H-0](H-0.md) | 雑音の 7 本（B 1・2・4 の混在） | ボード直 | N | 通過 |
| [H-1](H-1.md) | 束ねた ch の応答（半 ch・−3 dB 幅・ENBW） | ボード直 | NS | 通過（2 回目） |
| [H-2](H-2.md) | ch → IF（B 1・2・4） | ボード直 | NS | 通過（2 回目） |
| [H-4](H-4.md) | 運転中のモードの切り替え | ボード直 | N | 通過 |
| [V2-a](V2-a.md) | PL の積分器: 10.24 ms × 4 = 40.96 ms | ボード直 | N | 通過 |
| [V2-e](V2-e.md) | TP のレコード = AXI4-Lite の TP のリング | ボード直 | N | 通過 |
| [V2-f](V2-f.md) | r = DUMP_T − m·BASE = 2·G が Overlay をまたいで一定 | ボード直 | N | 通過 |
| [F-2](F-2.md) | ADC → コアの遅れ（timebase.CAL の (1, 1)） | ボード直 | P | 通過（PWR 31） |
| [V2-b](V2-b.md) | specd の 40.96 ms で 30 分 | specd | N | 通過 |
| [V2-d](V2-d.md) | LOAD で Wide ⇄ Fine を往復（`kind`・usr） | specd | N | なし（M5 で LOAD の片道だけ） |
| [S](S.md) | specd の SNAP（RAW の生サンプル） | specd | N | 通過 |
| [P-8](P-8.md) | TP の線形性・流れ / TP・Wide の tp_cal | specd | N（＋ PM・ATT） | なし（新しく） |
| [PS-3](PS-3.md) | TP の跳ねの見張り | specd | N（＋ ATT） | なし（Fine で通過。TP の作りは同じ） |

**Wide では回さない判定**:
- V2-c（窓の W-G をレコードの道で）: Wide には DDC の窓が無い。SLICE の中身は sim の A2（模型と bit 単位）・H-2・H-0 で見ている（proj023 の手順 4c）
- F-0・F-1・T-4・W-*・P-5・V2-g・PS-1: SAM45-Fine の窓・13 コアに付いた判定。Wide の時刻の見張りは V2-f、ch の形は H-1
- S-W1〜S-W4・D_S（sim）: `hw/bits/sam45-wide` の `make sim-all`（M2 で移植元と同じ出力）。B-1（ビルド）は M3・M5 で FDRI が移植元と同じ
