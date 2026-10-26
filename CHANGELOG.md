# 変更履歴

リリースごとに、何が変わったか・互換性（インターフェースの版）・対応する性能評価を書く。
書き方は [`docs/release.md`](docs/release.md)。

## v1.1.0（`v1.1.0`・`sam45-wide/v1.0.0`、2026-10-26）— SAM45-Wide を足す

study-rfsoc の proj023（ビルド 11、`proj023-m0`）を移した SAM45-Wide を、2 本目の bit として出す。SAM45-Fine の bit は変えない（`sam45-fine/v1.0.0` のまま）。

- **bit**: SAM45-Wide（4 ADC、全帯域の FFT 32768 点・PFB T = 4 を電力の後に B 4・2・1 個ずつ束ねる SLICE。2048 MHz・500 kHz / 1 GHz × 2・250 kHz / 512 MHz × 2・125 kHz、4096 ch、40.96 ms、ADC ごとの TP）。BIT_KIND 1・BIT_REV 1。FDRI は移植元と同じ（`abc66e72…`）。USR_ACCESS にタグの commit。`-1` は Performance_Explore で閉じる（WNS +0.0007 ns）
- **インターフェース**: v2 のまま（SLICE の分は proj023 で確定した約束。[`docs/spec/interface.md`](docs/spec/interface.md)）。Fine と Wide を `LOAD` で往復でき、混ざった記録も受け側の照合を通る
- **較正**: 時刻 `timebase.CAL[(1, 1)]`（形 (b)、pps_det 71.5 ns・adc_to_core 141.4〜143.0 ns）。TP の dBm `tp_cal.json` の `bits` に (1, 1)（K は Fine と同じ）
- **判定**: `test/acceptance/sam45-wide/` の 14 本。12 本が通過、H-1・F-2 は保留（どちらも線のわずかな外で、実用上は問題ないと判断）
- **性能評価**: [`docs/performance/sam45-wide/v1.0.0.md`](docs/performance/sam45-wide/v1.0.0.md)（既知の制限 9 件）
- **文書**: 仕様（`bits.md` の Wide の行・`timing.md` の CAL (1, 1)・`units.md`）・設計（`docs/design/sam45-wide/`）・使い方（`install.md` の bits.json の `"kind": "wide"`・`specd.md` の Wide の SET・`client.md` の SLICE の軸）
- **既知の制限のうち運転に効くもの**: 受け側を閉じる前に STOP する（溜まりの残りが次の受け側に行く）・`s45spur.py rec` は Wide の軸を読まない（`widecomb.py` を使う）・F-2 の Overlay ごとのずれ（≦ 5 ns、bound_ns の内）

このほかに、v1.0.0 の後に入った変更（Fine にも効くもの）:

- **PS（specd）**: 止めた後に共有メモリの溜まり `/dev/shm/psm_*` が残る件を直した（v1.0.0 の既知の制限 3）。送信が時間切れ・切断で抜けたときに記録の memoryview を放さず、片付けの `release` が BufferError になって `unlink` に届いていなかった。Python 3.10 では取得の子が resource_tracker の登録を外すので、残りを誰も消さない。名前を先に消す・SIGHUP でも片付ける形にした。SAM45-Wide も同じ（M5 で `sw/pynq/` に一本化した後も入っている）。`test_fake.sh` に `shm` を足した（直す前の道具では落ちる）
- **文書**: v1.0.0 の既知の制限 11（窓の遅れ D(NS) を PFB 入りの RTL で出し直していない）を閉じた。`make sim-wdelay` を今の RTL で回し、D(NS)・F(NS) は NS 1〜8 とも PS の値と同じ（窓の PFB は z の後なので D に入らない）。bit・PS の値は変えない
- **PS**: SAM45-Wide の PS を `sw/pynq/` に一本化（`sw/pynq-wide/` を消した。Wide の M5）。specd が bits.json の `"kind": "wide"` を捨てていたのを直した。**Fine にも効く変更**: `sg.py` は SG の出力が unleveled なら止まる（低いレベルを使うなら SG の出口に固定減衰器）。Fine の実機の短い回帰（ID-1・V2-b 300 s）は通過
- **PS**: SAM45-Wide の取得と Wide の道具も LMX2594 の出力の強さを PWR 3 に（Fine と同じ。今までは出荷時の 31 のまま）。クロックの櫛 n × 163.84 MHz の強い線が 5〜13 dB 下がる。Wide の記録の ID の `lmx_pwr` が実際の値に。櫛を比べる `widecomb.py` を足した
- **PS（解析）**: `s45allan.py` が流れの帯域を Fine の窓の式（512 / 2^ns）で出し、SAM45-Wide の B 2・B 4 の流れを 1/4・1/16 の帯域と読んでいた（ラジオメーターの予言が B²倍ずれる）。v2 の記録の ch の幅 df_hz を使う（Fine の記録は同じ値）
- **判定**: SAM45-Wide の判定 14 本を `test/acceptance/sam45-wide/` に書き起こした（proj023 の README の中にだけあった）
- **文書**: `docs/user/specd.md` の起こし方を `sudo -E $(which python3)` に直した（`sudo python3` だと pynq の無いシステムの python3 になる）

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
