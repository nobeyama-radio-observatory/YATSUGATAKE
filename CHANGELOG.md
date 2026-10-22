# 変更履歴

リリースごとに、何が変わったか・互換性（インターフェースの版）・対応する性能評価を書く。
書き方は [`docs/release.md`](docs/release.md)。

## 未リリース

## v1.0.0（`v1.0.0`・`sam45-fine/v1.0.0`、2026-10-22）— 最初のリリース

study-rfsoc の proj021（手順 2-5）を移した SAM45-Fine を、最初の版として出す。

- **bit**: SAM45-Fine（4 ADC × 2 窓、256〜8 MHz、4096 ch、PFB T = 4、ダンプ 10.24 ms、ADC ごとの TP 1.024 ms）。BIT_KIND 2・BIT_REV 3。FDRI は移植元と同じ（`e095fa97…`）。USR_ACCESS にタグの commit
- **インターフェース**: v2（流れと自己記述・PL が書くリング・s45proto v2）。[`docs/spec/`](docs/spec/) が仕様の正典（ADR 0021）
- **PS**: specd・specrecv・specctl・s45client。時刻の式で pps_det_ns を足すように直した（PR #25）。較正 CAL (2, 3) は形 (b)（1PPS の入口の LPF 71.6 ns ＋ adc_to_core 141.3〜141.7 ns）
- **設置**: 1PPS と 10 MHz の入口に BLP-10.7+ を常設する（[`docs/user/wiring.md`](docs/user/wiring.md)）
- **文書**: 使い方（`docs/user/`）・仕様の値（`docs/spec/timing.md`・`units.md`・`hardware.md`）・設計（`docs/design/`）
- **性能評価**: [`docs/performance/sam45-fine/v1.0.0.md`](docs/performance/sam45-fine/v1.0.0.md)（21 判定すべて通過。既知の制限 11 件）
- **既知の制限のうち運転に効くもの**: specd の後の `/dev/shm/psm_*` の残り（起こす前に消す）・窓の遅れ D(NS) は矩形の sim の値・LPF の混信への効きは未判定

それまでの準備: リポジトリの骨組み・決定記録（ADR）・知見・移植計画（M0〜M6）・公開前スキャン
