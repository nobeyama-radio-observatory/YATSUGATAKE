# SpW8 の設計

4 ADC × 窓 8 本。窓ごとに IF の中心と幅（128・64・32・16・8 MHz）を選び、4096 ch（31.25〜1.953 kHz）・10.24 ms ＋ TP 1.024 ms。窓は全部チップ内の履歴の枠で、PL の DDR は使わない。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)、窓のキー・記録の約束は [`../../spec/interface.md`](../../spec/interface.md) の 2.・4.5・5.・6.（[ADR 0028](../../decisions/0028-spw-wrst-floor-and-logical-window-keys.md)・[ADR 0029](../../decisions/0029-spw-ring-records-f32.md)）。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 7・BIT_REV 10・PROJ 0x0032_0300。IF_ID 0x0207_0A01（コア 4 個、NSTREAM 8・CAPS 3）・0x0207_0A02（time_core）・0x0207_0A03（リング）。PS は PROJ を照らさない |
| コア | ADC ごとに 1 個（コア c = ADC c）。粗い PFB（64 MHz 間隔、全速 16 標本 / クロック、粗い ch の出力 256 MS/s）→ 窓の頭 8 本（NCO ＋ 半帯域 1 段目。流れ s = 0〜7）→ 全窓で共有の後段（ddcb）→ 時分割の機関 3 本（PFB T = 4 ＋ 4096 点 FFT ＋ 電力 ＋ 積分）→ チップ内の履歴の枠 8 |
| コアの形 | 頭 H 8・機関 E 3・枠 S 8・粗い ch の組 NK 8・G_L2 19。粗い PFB の偶奇（PSPLIT）で頭 0〜3 は偶の粗い ch、4〜7 は奇の粗い ch |
| 窓の計画 | `sw/pynq/spwplan.py`。利用者の窓（IF・幅）→ 中心を ch 幅の格子に丸める → 粗い ch（近い ch、幅 ≦ 64 MHz なら 2 番目に近い ch も）→ 頭（偶奇の組）→ 機関（機関ごとに幅の和 ≦ 256 MHz）→ 枠。計画できない組は SET が組ごと断る。`check()` が PL の WRST の約束 [1]〜[6] と同じ印を返す |
| 窓のキー | **論理の窓** A0〜D7（ADR 0028）。specd が論理の窓 → 流れ s を割り当て、STATUS の `spw_map` に出す。記録の s の欄も論理の窓の番号 |
| WRST | WRST_T の下限は 8 クロック（`spw_regs.v`、既定 64）。短い値は下限に切り上げる |
| ダンプ | BASE 10.24 ms（PL、nacc = 5·2^(7−NS)、L = 2^(12+NS) ビート）。tint は specd が C の道（`--fast-ring`）で束ねる（既定 40.96 ms、32 窓のネットワークの最小 20.48 ms） |
| データの道 | 窓ごとのレコード（type 5、**PL で丸めた f32**、ADR 0029）× 32 / 10.24 ms = 51.2 MB/s →（リング 64 MiB、DDR）。PS はリングの上のレコードを C（`libs45fast.so`）で照らし・f32 を double の器に足し・IF の昇順に並べ・CRC。**束ができたら C が出口の溜まりへ SPEC の記録を直に書く**（M6、`s45fast.c` の `sw_out`。落ちの印・溜まりの端・空きなし・陽性対照のときは Python の道） |
| TP | ADC ごとに 1.024 ms（共通の部品） |
| クロック | RFDC → DSP 256 MHz × 16 サンプル（SAM45-Wide と同じギアボックス。ビルドの `rfdc_params.rpt` がほかの bit と 1 行も違わない。ADC → コアの道は共通の道 1） |
| 時刻 | 窓ごとの D_eff = D(NS) ＋ 1.5·L(NS)。D(NS) は `timebase.WIN_DELAY[(7, 10)]` = NS 1〜5 で 86.03・135.07・231.05・411.01・757.03 ビート（sim-dly。[`../../spec/timing.md`](../../spec/timing.md)） |
| ビルド | `hw/bits/spw8/`（`make build IMPL=Performance_ExplorePostRoutePhysOpt` → `build-PEPRPO/`。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、Performance_ExplorePostRoutePhysOpt）

| | 値 |
|---|---|
| WNS / WHS | +0.015935 ns / +0.009527 ns |
| LUT / FF / CLB | 265,530（62.44 %）/ 308,700（36.29 %）/ 94.51 % |
| DSP / BRAM タイル / URAM | 2,896（67.79 %）/ 982（90.93 %）/ 56（70.0 %） |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137 |

移植元（study-rfsoc proj032-m0 の `b5/build-PEPRPO/`）と FDRI が同じ（[`../../migration-spw8.md`](../../migration-spw8.md) の M3・M5c）。**既定の戦略では WNS −0.024 ns で閉じない**ので PEPRPO で作る。CLB 94.5 %・BRAM 90.9 % で詰まっている。RTL・置き場所を変えたら `-1` で閉じることを必ず確かめる。VCCINT は 30 分・2 時間の運転で ≒ 39.4 A（目安 40 A）。

## 経緯と詳しい説明

系譜は proj032 の b1（1 ADC・窓 6 本）→ b2（PL の DDR の窓）→ b4 rev 8（4 ADC・窓 6 本）→ **b5 rev 10（4 ADC・窓 8 本、チップ内の枠だけ）**。部品の構成（頭・機関・枠）の見積もりと選び方、窓の計画、D(NS) の測り方は study-rfsoc の proj032 の README。模型は `model/win64_model.py`・`win64_fixed.py`・`pfb64_fixed.py`（リポジトリの直下）、係数の設計は `model/spw8_coef.json`。PS は `sw/pynq/` の SpwBackend（`s45acq.py`）・`spwplan.py`・`s45fast.c` の SpW の道。

## 性能

実機で測った値は [`../../performance/spw8/`](../../performance/spw8/)、判定は [`../../../test/acceptance/spw8/`](../../../test/acceptance/spw8/)。
