# SpW8 の判定（受け入れ試験）

SpW8 の bit（BIT_KIND 7・BIT_REV 10・PROJ 0x0032_0300、study-rfsoc の proj032 の `b5/build-PEPRPO/` と FDRI が同じ）と、それに載せる PS を、リリースの前に実機で通す判定。
1 判定 1 ファイル。書き方は 6 項目（ID・前提・手順・合格・陽性対照・記録）。**合格は測る前に書く**。

proj032 の判定は README の中にだけあった（P-9・P-10b・P-12・P-13・P-13b）。2G と同じく**移植の M0 で書き起こした**（2026-11-03）。
ID は SAM45-Fine（窓）・2G（specd・リング・予算）の判定と同じ意味のものは同じ ID にした（ID-1・H-0・W-1・PS-1・V2-b・V2-L・RING・NET）。**TW**（双子）・**WRST**（約束）・**RATE**（10.24 ms × 32 窓の取得）は SpW8 で足した。

**動かし方は 2 通り**: M4 までは移植元の試行の道具（`hw/bits/spw8/pynq/spw_b5.py`、ボード直）、M5b の後は specd（SpW の Backend）。
specd の SET の書き方は M5b で決まる（[`docs/migration-spw8.md`](../../../docs/migration-spw8.md) の S・M5b）。**下の specd の手順は M5b で書き方を直してよいが、合格は変えない**。

## 共通の前提

- **bit**: SpW8（`proj032b5.bit` を M3 で作り直したもの、M5c の後は USR_ACCESS を焼いたもの）。コア 4 個（s45_core_0〜3 = ADC_A〜D）、各 H 8・E 3・S 8（窓 8 本、チップ内の枠だけ）。IF_ID 0x0207_0A01（コア）・0x0207_0A02（time_core）・0x0207_0A03（リング）
- **ファン**: proj027 4f の配置のまま（SpW8 は VCCINT ≒ 38.5 A・62 ℃、P-13 の 30 分。2G-4 の 43 A より低い）
- **クロック**: 外部 10 MHz と 1PPS（入口に LPF を常設）。`--clkin 0 --ref 10`
- **ボードと器は別の作業と分け合っている**: 起こす前に、別の作業の specd・試行の道具が動いていないか（`pgrep -af "[s]pecd|[s]pw_b5"`）と `ATT?` を読む。ATT が 13 dB でなければ、戻す前に開発者に聞く（100 dB のままだと入力が来ない）。SG を使う判定は、使う前の状態を記録し、終わったら戻す
- **宛先**: 環境変数 `B`（ボード）・`SG`・`PM`・`ATT`・`RFSOC_NS`。宛先はファイルに書かない。STATUS の `data_client`・`data_drop` には受け手の IP が出るので、記録に残すときは伏せる
- **ノイズソースはいつも ON**（[ADR 0024](../../../docs/decisions/0024-noise-source-always-on-remote-off.md)）
- **時刻の較正**（[ADR 0023](../../../docs/decisions/0023-time-calibration-per-board.md)）: ボードの `time_cal.json`。TP の dBm もボードの `tp_cal.json`（ADR 0025）。記録には `tcal` を書く
- **既定の窓の組 b5**（P-9）: 1 コアに 8 本（128・64・64・16 / 128・64・32・8 MHz）。**計画の窓の組 plan2**（P-10b の 2 回目・P-13b）: `3900:128,3890:64,3890:64,3892:16,3891:8,3300:128,3290:32,2650:128`（IF:幅 MHz）、窓 2 を 2 番目に近い粗い ch で作り窓 1 と双子にする（`--alt 2,1`）
- **ネットワークの tint**: SpW8 の最小は **20.48 ms**（32 窓 × 4096 ch × 4 B で 25.6 MB/s、interface 4.5、予算 1 ボード 30 MB/s）。PL と PS の取得は 10.24 ms のまま（RATE）
- **配線**: N（ノイズ ON）・N/S（SG の CW を足す）。P は使わない（F-2 を回さない）

## 一覧

| ID | 何を確かめるか | 動かし方 | 配線 | study-rfsoc で |
|---|---|---|---|---|
| [ID-1](ID-1.md) | 自己記述・起動の見張り | 道具 → specd | どれでも | 通過（P-9 b5 rev 10） |
| [H-0](H-0.md) | 立ち上げ（32 窓のレコード・K_F の格子・照合・平らさ） | 道具 → specd | N | 通過（P-9） |
| [W-1](W-1.md) | SG の CW の ch（8 窓 × 4 コア） | 道具 → specd | N/S | 通過（P-13b） |
| [TW](TW.md) | 2 番目に近い粗い ch の窓と近い ch の窓の双子 | 道具 → specd | N | 通過（P-10b） |
| [WRST](WRST.md) | 約束を破る窓の組を断る | 道具 → specd | どれでも | 通過（P-10b） |
| [RATE](RATE.md) | PL と PS の取得 10.24 ms × 32 窓で 30 分 | 道具 → specd | N | 通過（P-13） |
| [PS-1](PS-1.md) | float32・utc_ns の補正（D(NS) の表） | specd | N | なし（D(NS) は P-12 の sim） |
| [V2-b](V2-b.md) | ネットワークの tint 20.48 ms で 30 分 | specd | N | なし |
| [V2-L](V2-L.md) | tint 20.48 ms で 2 時間 | specd | N | なし |
| [RING](RING.md) | リング 64 MiB が PS の 0.3 s の止まりを吸う | specd | N | なし |
| [NET](NET.md) | 予算を越える tint を SET で断る | specd | どれでも | なし |

**回さない判定**: F-2（ADR 0023）・PL の DDR の窓（b5 に無い）・EQ（4 コアとも ADC が決まっている）。
