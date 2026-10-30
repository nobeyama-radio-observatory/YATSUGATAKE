# 時刻の物差し

> **仕様の正典**（[ADR 0021](../decisions/0021-spec-canonical-in-yatsugatake.md)）。時刻の単位・格子・式・遅れの定数の**値**はここが正。
> 決めた理由と経緯は [`interface.md`](interface.md) の 1.・5.1・5.2 と [`bits.md`](bits.md) の「時刻の格子と dt」に残してある（節の番号を変えないため、あちらの文はそのまま）。食い違ったらここを直し、あちらからここを指す。

## 単位

| 量 | 値 | 備考 |
|---|---|---|
| fs | 4096 MSPS | タイル PLL（[`hardware.md`](hardware.md)） |
| ビート | DSP のクロック 1 個 = 16 サンプル = **125/32 ns = 3.90625 ns ちょうど** | 時刻の最小単位。T は 64 bit のビートの数 |
| 1 秒 | **256,000,000 ビートちょうど** | time_core が 1PPS の間隔を数えて確かめる（F-0） |
| ADC のフレーム | 8192 サンプル = 512 ビート = 2 µs | TP は ADC のフレームの頭でしか切れない |
| 格子 G | **524,288 ビート = 2.048 ms** | PL の START_AT（WRST・RUN・TP_ARM）は G の倍数 |
| 基本の単位 BASE | **10.24 ms = 5·G = 2,621,440 ビート** | PL のダンプの長さ（SAM45-Fine） |
| tint | BASE の倍数（n_sum = tint / BASE）。SAM45-Fine の既定 40.96 ms | 1 回の取得で全体に 1 つ |
| TP の区切り | **1.024 ms = 512 フレーム = 262,144 ビート** | TP のレコードは区切り 10 個 = BASE |
| 窓のフレーム L(NS)（SAM45-Fine） | L = 4096 点 / BW、BW = 256 / 2^(NS−1) MHz → **L = 16·2^(NS−1) µs**（NS 1 = 16 µs 〜 NS 6 = 512 µs） | |

数え方は整数で行う: ns = ビート × 125 / 32（四捨五入、`timebase.beats_to_ns`）。

## 始まりの置き方

- specd は RUN・WRST・TP_ARM の START_AT を **T の tint の倍数**に置く（BASE は G の倍数なので G の格子にも乗る）。`START at=` を指定したときは、その時刻以後の最初の tint の倍数
- RUN は START_AT ＋ 1 ビートで全コアが同時に始まる（RUN_T = START_AT ＋ 1）
- 秒とは揃えない（1 秒は 2.048 ms の倍数でない）。Overlay をまたいだ格子の一致も求めない（T の原点は Overlay ごと）

## 錨と UTC

1PPS の縁で time_core が T をスタンプする（スタンプ）。specd は 1PPS の後に UTC の秒を対にして**錨**（utc_sec, stamp）を持つ。

**beat_utc(B) = utc_sec·10⁹ ＋ (B − stamp)·125/32 ＋ pps_det_ns**

- スタンプは本当の 1PPS の縁より pps_det_ns だけ後に打たれるので、**足す**（2026-10-21 まで引いていた誤りを直した。`sw/pynq/test_cal_b.py`）
- 錨が無い・1PPS が来ていない間は時刻を答えない（`time_ok = 0`。START は断る。`force=1` なら utc_ns = 0 と健全性の印）

## 送る時刻（s45proto v2 の utc_ns）

**サンプルの時刻**（ADC の口に入った時刻）: t_adc(B) = beat_utc(B) − adc_to_core_ns[src]

**SPEC の utc_ns = beat_utc(dump_t) − adc_to_core_ns[src] − D_eff(KIND, NS)** ＝ 実効の区間の始まり。区間の中心 = utc_ns ＋ tint/2

| KIND | D_eff | 状態 |
|---|---|---|
| FULL | 0（矩形の FFT。フレームの最初のビート） | 決定 |
| RAW | 0（生サンプルのフレームの最初のビート） | 決定 |
| DDC（PFB T = 4、SAM45-Fine の窓） | D(NS) ＋ 1.5·L(NS) | 決定。D(NS) は `timebase.WIN_DELAY_BEATS`（`hw/bits/sam45-fine` の `make sim-wdelay`）。窓の PFB は wspec の中（z の後）にあるので D(NS) に入らず、そのずれは 1.5·L(NS) で足す |
| SLICE（PFB T = 4、SAM45-Wide） | D_S ＋ 1.5·L = 0 ＋ 3072 ビート = 12 µs | 決定（proj023 の sim-wds） |
| STAGE2（2G-1-Fine） | 1.5·N_f·56 ＋ 836 サンプル ＋ D_S = 688,180.25 ビート（2.688204 ms）＋ D_S | 式は決定（study-rfsoc proj037 T-4、[ADR 0027](../decisions/0027-2g-1-fine-records-time-rounding.md)）。D_S は移植の RTL の sim で |

TP の utc_ns = beat_utc(t_beat) − adc_to_core_ns[adc]（区切りの最初のフレームの頭）。

## 較正の定数

**ボードの較正ファイル**（[ADR 0023](../decisions/0023-time-calibration-per-board.md)）が正。無ければ `sw/pynq/timebase.py` の `CAL`（開発の値）を**暫定**として当てる。

| どれを当てるか | 条件 | 印（`ID` の `tcal`） |
|---|---|---|
| ボードの較正ファイル（既定 `/etc/yatsugatake/time_cal.json`、環境変数 `YATSUGATAKE_TIME_CAL`） | ファイルのボードの印 = このボード（eth0 の MAC、[ADR 0026](../decisions/0026-board-id-mac.md)）、かつ測った bit と載っている bit の ADC → コアの道（`ADC_PATH`）が同じ | `board` |
| `CAL[(BIT_KIND, BIT_REV)]`。無い bit は `CAL[(1, 1)]` | 上に当たらないとき | `provisional` |

- 較正ファイルは `timecal.py` が作る（[`../user/calibration.md`](../user/calibration.md)）。形 (a): `pps_det_ns` 0・`adc_to_core_ns` = M。Overlay 5 回の平均、`bound_ns` = max(5, ⌈ばらつきの半分 ＋ 2 ns⌉)
- ADC → コアの道（`ADC_PATH`、(BIT_KIND, BIT_REV) → 番号）: 表に無い bit は共通コアの道 1。**RFDC の設定・ギアボックスを変えた bit は新しい番号を足す**
- 較正ファイルはリポジトリに入れない（ボードの個体の値）

`CAL`（開発の値）の鍵は bit の **(BIT_KIND, BIT_REV)**。

| 定数 | 意味 | 性質 | 測り方 |
|---|---|---|---|
| `pps_det_ns` | 1PPS の縁 → スタンプ。**入口の LPF の遅れ**を入れる（形 (b)） | 設置の性質（LPF・ケーブル） | F-2 を LPF ありとなしで測った差 |
| `adc_to_core_ns[ADC]` | ADC のサンプル → コアの入口（RFDC ＋ ギアボックス） | bit の性質 | F-2（配線 P、1PPS を ADC にも）で M = adc_to_core − pps_det を測り、pps_det を足す |
| `bound_ns` | 定数の不確かさの見積もり | | |

今の値:

| (BIT_KIND, BIT_REV) | pps_det_ns | adc_to_core_ns（A・B・C・D） | bound_ns | 出どころ |
|---|---|---|---|---|
| (2, 3) SAM45-Fine | 71.6（BLP-10.7+） | 141.6・141.7・141.3・141.3 | 5 | 2026-10-21 F-2（LPF あり 2 回・なし 1 回）。[`../../test/acceptance/sam45-fine/F-2.md`](../../test/acceptance/sam45-fine/F-2.md) |
| (1, 1) SAM45-Wide | 71.5（BLP-10.7+） | 143.0・142.9・141.5・141.4 | 5 | 2026-10-21 study-rfsoc proj023 の F-2（LPF あり 2 回、LMX PWR 31）。2026-10-26 の M6（PWR 3）の M は −1.7〜−0.1 ns で据え置き（判定は保留）。[`../../test/acceptance/sam45-wide/F-2.md`](../../test/acceptance/sam45-wide/F-2.md) |

- 本番のボードで LPF・ケーブル・分配を替えたら、`timecal.py` で測り直す。`CAL` の値は開発のボードのもので、本番の較正の代わりにしない
- RTL を変える → BIT_REV を上げ、D を出し直す。ADC → コアの道を変えたときだけ `ADC_PATH` に新しい番号を足し、開発のボードで F-2 を回して `CAL` に足す
- 要求は 100 µs。定数はどれもそれより 3 桁小さいが、黙って 0 にしない

## 持ち越し

- DDC の D(NS) を (BIT_KIND, BIT_REV) の表に移す（今は全 bit 共通の `WIN_DELAY_BEATS`。DDC の窓を持つ bit が SAM45-Fine だけの間は値が当たる。[`interface.md`](interface.md) の 5.2）
- 幅の違う窓の区切りの差 X(NS)（NS 1 と 6 で 2.4 µs）は受け入れている（utc_ns はそれを含んだ正しい時刻）
- 起こした直後の 1PPS の取り込みの異常・PPS のスタンプの量子化（±0.5 ビート）の見立ては調べている途中
- F-2 の M は Overlay ごとに 4 ADC 共通でずれる（≒ 0.9 ビート、SAM45-Wide の M6 では 1.18 ビート ≒ 4.6 ns）。原因は確かめていない。`bound_ns` 5 はこれを含む
