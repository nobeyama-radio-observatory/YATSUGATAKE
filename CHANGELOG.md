# 変更履歴

リリースごとに、何が変わったか・互換性（インターフェースの版）・対応する性能評価を書く。
書き方は [`docs/release.md`](docs/release.md)。

## v1.3.0（`v1.3.0`・`2g-1-fast/v1.0.0`、2026-10-31）— 2G-1-Fast を足す

study-rfsoc の proj033（`proj033-m0`）を移した 2G-1-Fast を、4 本目の bit として出す。SAM45-Fine・SAM45-Wide・2G-4 の bit は変えない（`sam45-fine/v1.0.0`・`sam45-wide/v1.0.0`・`2g-4/v1.0.0` のまま）。

- **bit**: 2G-1-Fast（1 ADC × 1 コア、全帯域の FFT 131,072 ch・15.625 kHz、2-for-1 のレーン FFT（16384 点、IP 8 個）、PFB とひねり係数は bit の ROM。ダンプ 10.24 ms を束ねて tint、SRC で 4 ADC から選ぶ）。BIT_KIND 11・BIT_REV 1・PROJ 0x0033_0100。**Performance_Explore で作る**（既定の戦略では閉じない）。FDRI は移植元と同じ（`6bdecddf…`）。USR_ACCESS にタグの commit
- **インターフェース**: v2 のまま。2G-1-Fast の FULL（kind 1）は窓 A0 の 1 本・nch 131072。ネットワークの予算の照合は 2G-4 と同じ（tint の最小 20.48 ms）
- **PS**: `s45core.PROJ_G21` を 0x0033_0100 に（追跡のため。G21Backend は PROJ を照らさない）。`g21cw.py`（2G-1 の記録の頭の欄・床・CW の確かめ）を足した。bits.json の例に `"2g-1-fast"`（`"kind": "g21"`）。2G-1-Fast の ADC → コアの道は共通の道 1（時刻・TP の較正ファイルがそのまま当たる）
- **ボードの準備**: 2G-4 と同じ（AXI_MAX_PIPELINE 0x0102・`build_fast.sh` で「CRC: 命令」）。specd は `--prefault --fast --fast-ring`
- **判定**: `test/acceptance/2g-1-fast/` の 7 本（ID-1・H-0・H-2・NET・RING・V2-b・V2-L）がすべて通過。2 時間で取りこぼし 0、VCCINT 13.3〜13.8 A
- **性能評価**: [`docs/performance/2g-1-fast/v1.0.0.md`](docs/performance/2g-1-fast/v1.0.0.md)（既知の制限 4 件）
- **文書**: 仕様（`bits.md`・`timing.md`・`units.md`・`interface.md` の 2G-1-Fast の分）・設計（`docs/design/2g-1-fast/`）・使い方（`install.md` の bits.json の `"kind": "g21"`・`specd.md` の 2G-1-Fast の SET・`client.md` の記録・`calibration.md`）
- **既知の制限のうち運転に効くもの**: ネットワークの tint の最小 20.48 ms。`-1` の WNS +0.025 ns（RTL を変えるときは閉じるかを必ず確かめる）

## v1.2.0（`v1.2.0`・`2g-4/v1.0.0`、2026-10-31）— 2G-4 を足す・較正をボードごとのファイルに

study-rfsoc の proj031 rev 2（`proj031-m0`）と proj036 の PS を移した 2G-4 を、3 本目の bit として出す。SAM45-Fine・SAM45-Wide の bit は変えない（`sam45-fine/v1.0.0`・`sam45-wide/v1.0.0` のまま。`hw/common/` の一本化の後に作り直して FDRI まで同じことを確かめた）。

- **bit**: 2G-4（4 ADC、コアごとに全帯域の FFT 32,768 ch・62.5 kHz、2-for-1 のレーン FFT、PFB の係数は共有の URAM に PS が書いて VERIFY。ダンプ 10.24 ms を束ねて tint、ADC ごとの TP）。BIT_KIND 3・BIT_REV 1。FDRI は移植元と同じ（`f05e1f62…`）。USR_ACCESS にタグの commit
- **インターフェース**: v2 のまま。**ネットワークの予算 1 ボード 30 MB/s を specd が SET で照らす**（interface 4.5。越える tint は `ERR ARG` で断る。2G-4 の tint の最小は 20.48 ms。試験は `--net-budget-mbs 0`）。2G のリングは 64 MiB が既定。specd の `ID` に `tcal`・`board`、`GET CAL` に時刻の較正と `board`・`adc_path`
- **ボードの準備（2G-4 に要る）**: GEM1 の AXI_MAX_PIPELINE を 0x0102 にする（起動時の systemd のユニット。4 本以上にしない）・ボードで `build_fast.sh` を回して `libs45fast.so` を作る（最後の行が「CRC: 命令」）。手順は [`docs/user/install.md`](docs/user/install.md)
- **較正（Fine・Wide にも効く）**: 時刻の較正（ADR 0023）と TP の dBm の較正（ADR 0025）を、**ボードごとの較正ファイル** `/etc/yatsugatake/time_cal.json`・`tp_cal.json` にした。設置の後に `timecal.py`（時刻）・`s45cal.py`（TP）で作り、リポジトリには戻さない。ファイルが無い・当たらないときは開発の値を「暫定」（`tcal provisional`）で当てて止めない。鍵はボードの印（eth0 の MAC、ADR 0026）。bit ごとの F-2 はやめ、ADC → コアの道（`timebase.ADC_PATH`）ごとに同じ値を使う。手順は [`docs/user/calibration.md`](docs/user/calibration.md)
- **測り方（ADR 0024）**: ノイズソースはいつも ON。OFF の要る測りは道具が遠隔で切って入れ直す（`instr.py ns off|on`・`--ns-off`。電源 KIKUSUI PMX18-2A、宛先は `RFSOC_NS`）
- **判定**: `test/acceptance/2g-4/` の 11 本。10 本が通過、F-2 は ADR 0023 で 2G-4 では回さない（最後の F-2 の M はボードの較正と ±1.0 ns）
- **性能評価**: [`docs/performance/2g-4/v1.0.0.md`](docs/performance/2g-4/v1.0.0.md)（既知の制限 6 件）
- **文書**: 仕様（`bits.md`・`timing.md`・`units.md`・`interface.md` の 2G-4 の分）・設計（`docs/design/2g-4/`）・使い方（`install.md` のボードの準備と bits.json の `"kind": "g24"`・`specd.md` の 2G-4 の SET・`client.md` の FULL の流れ・`calibration.md`）
- **既知の制限のうち運転に効くもの**: ネットワークの tint の最小 20.48 ms・リングのゆとり（102.4 MB/s で、空のリングから PS が ≒ 0.65 s 止まると落ちる）・M6 の途中で 1 回、原因の分からないボードの固まり（電源の入れ直しで戻った）

このほかに、v1.1.0 の後に入った変更:

- **PS**: 2G の PS（`sw/pynq-2g/`）を `sw/pynq/` に一本化した（2G-1・2G-2・2G-4 の取得と `s45fast.c`）。2G の取得も LMX2594 を PWR 3 で書き、ID に `usr` を出す。陽性対照 `--posctl-ring-stall` が 2G の取得で黙って空振りしていたのを直した
- **HW**: `hw/common/` の `core_cmn.v`・`tp_core.v`・`rec_fr.v` を 2G-4 の版（口 `F0_EXT`・`NCH` を足したもの）に一本化。rec_fr の `np − 1` を `np − 1'b1` にして Fine・Wide の合成を v1.0.0 と同じに保った。2G-4 は rec_fr だけ `hw/bits/2g-4/src/` の写しを読む（`hw/common/` の版ではどの戦略でもタイミングが閉じなかった）
- **リリースの道具**: `release_files.py` が .hwh の絶対パスをファイル名だけにする
- **仕様**: 2G-1 を 2G-1-Fast / 2G-1-Fine の 2 本に（ADR 0022）、2G-1-Fine の流れの形・時刻・丸め（ADR 0027、docs だけ）。ネットワークの予算 1 ボード 30 MB/s・2G のリング 64 MiB（interface 4.1・4.5・8. の 10〜12）
- **知見**: 資源の内訳（BRAM・URAM・DSP を構成要素ごとに）
- **判定の F-2 の読み方**: 2G-4 の `g24f2.py` は 1 回の値を最多の山で読む（1PPS のスタンプがビートの境目に乗る回の平均と σ を避ける）。Fine・Wide の F-2 は変えていない

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
