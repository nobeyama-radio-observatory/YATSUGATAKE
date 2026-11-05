# ID-1 — 自己記述・起動の見張り

- **前提**: 共通の前提。起こした直後
- **手順**:

```bash
# M4（試行の道具。ID の照らしは起動の中にある）
sudo -E $(which python3) spw_b5.py --clkin 0 --ref 10 --sec 10 --cfg b5 --ng 10 --out runs/id1
# M5b の後
python3 specctl.py --host $B ID STATUS | tee id1.txt
```

- **合格**:
  - コア 4 個とも IF_ID 0x0207_0A01・PROJ 0x0032_0300・NSTREAM 8・CAPS 3・CORE_PORT がコアの ADC、time_core 0x0207_0A02（256,000,000 ビート / s）、リング 0x0207_0A03
  - ギアボックス: GB_STAT の開始・空振り 0、ADC_STAT の valid を見た・落ち 0
  - specd（M5b の後）: ID の adc_id 02070a01・time_id 02070a02・proj 00320300・kind は M5b の名前、M5c の後は `usr`・`tcal=board`。STATUS は IDLE・time_ok 1・health 0x0000・flags 0x000
- **陽性対照**: 試行の道具を `--rev 9` で起こすと、ID の照らしで止まる（.bit は rev 10 なので）
- **記録**: proj032 P-9（2026-11-02、b5 rev 10、`runs/p9b5_b5_ng10`）: 4 コアとも ID・ギアボックスが通過
- **記録（specd、M5c）**: YATSUGATAKE M5c（2026-11-04、`hw/bits/spw8/runs/m5c/`）: USR_ACCESS を焼いた bit で ID の adc_id 02070a01・time_id 02070a02・**usr 6ed58430**（commit 6ed5843）・tcal board、STATUS は IDLE・time_ok 1・health 0x0000・flags 0x000。陽性対照: USR_ACCESS の無い M3 の bit で起こすと usr none
- **記録（M6）**: YATSUGATAKE M6（2026-11-04 06:54 UTC、M5c の bit `6b38f918…`、`hw/bits/spw8/runs/m6/id1.txt`）: adc_id 02070a01・time_id 02070a02・**usr 6ed58430**・tcal board・lmx_pwr 3・adcs 4・nw 8。STATUS IDLE・time_ok 1・health 0x0000・flags 0x000。`GET CAL` に `wdly=7.10`・`wdly_ns=1:86.03,2:135.07,3:231.05,4:411.01,5:757.03`（M6 で足した）。試行の道具の形（`h0_tool`）でも 4 コア・time_core・リングの ID が通過。**通過**
- **記録（M6 の回し直し）**: YATSUGATAKE M6 の回し直し（2026-11-04、M5c の bit のまま。ソフトは commit 808f398 の `sw/pynq/`（できた束を C が出口の溜まりへ直に SPEC の記録として書く）をボードの `~/spw8-m6b` に写し sha256 で同じ。specd `--prefault --fast --fast-ring --loop-log-ms 0.1`、`runs/m6b/`）。11:42 UTC: adc_id 02070a01・time_id 02070a02・**usr 6ed58430**・tcal board・lmx_pwr 3・adcs 4・nw 8。**通過**
