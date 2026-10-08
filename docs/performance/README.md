# performance — 性能評価

リリースした bit ごとに 1 本書く。**ファイル名は `<bit>/<版>.md`**（例: `sam45-fine/v1.0.0.md`）。
過去のものは書き換えない（新しい版で測り直したら新しいファイルを足す）。

## 1 本に書くこと

| 節 | 中身 |
|---|---|
| 対象 | bit の名前・版・.bit の sha256・ID（BIT_KIND・BIT_REV・commit） |
| 測定系 | 信号源の型番と設定・減衰器・分配器・フィルタ・ケーブル・10 MHz と 1PPS の配り方（[`../knowledge/measurement.md`](../knowledge/measurement.md)） |
| 資源・タイミング | LUT・FF・DSP・BRAM・URAM・`-1` の WNS / WHS |
| 判定の結果 | `test/acceptance/` の ID ごとに、合格の条件と測った値 |
| 周波数応答 | ch の形（半 ch・−3 dB 幅・サイドローブ）・窓の平坦さ |
| 強度 | リニアリティ・TP の dBm・単位の照合（窓の和 / TP） |
| 安定度 | アラン分散（ch・分光・TP） |
| スプリアス | 一覧と、運転の条件での Ta* への効き |
| 時刻 | 1PPS との関係・ダンプの区切り・読み落とし |
| 既知の制限 | 分かっていて直していないこと |
