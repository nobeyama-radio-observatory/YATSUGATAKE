# SAM45-Fine の設計

4 ADC × 2 窓（256〜8 MHz）・4096 点・40.96 ms ＋ ADC ごとの TP 1.024 ms。窓の分光に PFB（T = 4）。仕様の行は [`../../spec/bits.md`](../../spec/bits.md)。

## 組み立て

| | 値 |
|---|---|
| ID | BIT_KIND 2・BIT_REV 3・PROJ 0x0021_0200。IF_ID 0x0202_0301（コア）・0x0202_0302（time_core）・0x0202_0303（リング） |
| コア | `s45_core_0..3`（NW = 2、DDC の流れ s = 0・1）。`s45_core_0` だけ RAW の流れ s = 2（`full_sel` で ADC を選ぶ） |
| 窓 | NS 1..6 = 幅 256・128・64・32・16・8 MHz（RTL は 8 段 = 2 MHz まで持つ）。4096 点、PFB T = 4（sinc × Kaiser β 5、≧ 1 ch で −54 dB） |
| ダンプ | BASE 10.24 ms（PL）、tint は specd で束ねる（既定 40.96 ms） |
| データの道 | レコード → `s45_ring_0` → S_AXI_HP0_FPD → DDR（`--ring-mib` 既定 32 MiB） |
| クロック | RFDC 341.33 MHz × 12 サンプル → DSP 256 MHz × 16 サンプル |
| ビルド | `hw/bits/sam45-fine/`（`make`。part は `-1`、USR_ACCESS に commit） |

## 資源とタイミング（`-1`、既定の戦略）

| | 値 |
|---|---|
| WNS / WHS | +0.044057 ns / +0.009766 ns |
| LUT / FF | 168,982（39.73 %）/ 256,455（30.15 %） |
| DSP / BRAM タイル / URAM | 2,096 / 233.5 / 56 |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137 |

移植で同じであることを確かめた値（[`../../migration.md`](../../migration.md) の M3・M5b）。WNS の余裕は小さいので、RTL を変えたら `-1` で閉じることを必ず確かめる。

## 図

| ファイル | 中身 |
|---|---|
| [`block_design.svg`](block_design.svg)（`block_design.py`） | ブロックデザイン |
| [`pfb_chain.html`](pfb_chain.html) | 窓の分光の連鎖（proj020） |
| [`win_chain.html`](win_chain.html) | 窓の 3 段（粗い PFB → DDC → FFT、proj015） |
| `pfb_resp_T4.png`・`pfb_resp_T8.png`・`pfb_T4_vs_T8.png`・`pfb_cand_*.png` | PFB の応答と候補の比べ（T = 4 を選んだ理由、ADR [0012](../../decisions/0012-window-pfb-t4.md)） |
| `floorplan_2-5.png` | 配置（proj021 手順 2-5） |

## 性能

実機で測った値は [`../../performance/sam45-fine/`](../../performance/sam45-fine/)、判定は [`../../../test/acceptance/sam45-fine/`](../../../test/acceptance/sam45-fine/)。
