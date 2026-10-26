# SAM45-Wide の設計

4 ADC × 1 コア。全帯域（2048 MHz）を PFB（T = 4）＋ 16 レーンの FFT 32768 点（固定長）で分け、電力の後に細かい ch（125 kHz）を B 個ずつ束ねて SLICE の流れにする。B = 4 / 2 / 1 で全帯域 2048 MHz（500 kHz）/ 1 GHz × 2（250 kHz）/ 512 MHz × 2（125 kHz）、1 本 4096 ch、40.96 ms ＋ ADC ごとの TP 1.024 ms。モードは ADC ごとに独立。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)、SLICE の約束は [`../../spec/interface.md`](../../spec/interface.md) の 2.1・2.5・5.1。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 1・BIT_REV 1・PROJ 0x0023_0100。IF_ID 0x0201_0101（コア）・0x0201_0102（time_core） |
| コア | `s45_core_0..3`（ADC ごとに 1 つ）。SLICE の流れ s = 0・1（B 4 では s = 1 が空の流れ、NCH 0）。`s45_core_0` だけ RAW の流れ（`full_sel` で ADC を選ぶ。F-2・SNAP） |
| 分光 | PFB T = 4 → FFT 32768 点を 16 レーン（FRAME_BEATS 2048 = 8 µs）→ 電力 → B 個の束ね → 流れごとの切り出し（S0 から 4096 ch） |
| 束ね | B は FFT_N（2.4）で選ぶ。FFT は作り直さず、束ねだけを切り替える（2026-10-14 の D-7。レーン FFT の長さ切り替えは LUT ≒ 11 % を余計に使うので見送った） |
| SHIFT | コアに 1 つ（束ねる前の鎖を 2 本の流れで共有する。効くのは流れ 0 の値、D-8） |
| 起動 | 4 ADC のフレームの頭を、Overlay の直後から T の格子の同じ位相にそろえる（D-2）。束ねの見張り r = 2·G は RTL の定数（V2-f） |
| ダンプ | BASE 10.24 ms（PL）、tint は specd で束ねる（既定 40.96 ms） |
| データの道 | レコード → `s45_ring_0` → S_AXI_HP0_FPD → DDR（SAM45-Fine と同じ） |
| クロック | RFDC 341.33 MHz × 12 サンプル → DSP 256 MHz × 16 サンプル（SAM45-Fine と同じギアボックス） |
| 時刻 | SLICE の D_eff = D_S ＋ 1.5·L = 0 ＋ 3072 ビート = 12 µs（sim-wds）。CAL は (1, 1)（[`../../spec/timing.md`](../../spec/timing.md)） |
| ビルド | `hw/bits/sam45-wide/`（`make IMPL=Performance_Explore`。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、Performance_Explore）

| | 値 |
|---|---|
| WNS / WHS | +0.000716 ns / +0.009500 ns |
| LUT / FF | 255,211（60.01 %）/ 492,722（57.93 %） |
| DSP / BRAM タイル / URAM | 2,720 / 817.5 / 40 |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137 |

移植元（study-rfsoc proj023 ビルド 11）と FDRI が同じ（[`../../migration-sam45-wide.md`](../../migration-sam45-wide.md) の M3・M5）。**既定の戦略では閉じない**（その前のビルドで WNS −0.008 ns）。RTL・置き場所を変えたら `-1` で閉じることを必ず確かめる。

## 経緯と詳しい説明

系譜は proj014（レーン FFT）→ proj022（模型と見積もり）→ proj023（RTL、インターフェース v2 の上で）。設計の決め（D-1〜D-8）と sim の照合は study-rfsoc の proj023 の README、係数の原型は `model/wide_model.py`・`model/bin_resp.py`（sim の照合が読む唯一の正）。

## 性能

実機で測った値は [`../../performance/sam45-wide/`](../../performance/sam45-wide/)、判定は [`../../../test/acceptance/sam45-wide/`](../../../test/acceptance/sam45-wide/)。
