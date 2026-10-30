# ID-1 — 自己記述・係数 URAM の書きと VERIFY・起動の見張り

- **前提**: 共通の前提。specd を起こした直後
- **手順**:

```bash
python3 specctl.py --host $B ID STATUS | tee id1.txt
# ボードの specd のログから「係数 URAM」の行と「CRC:」（libs45fast.so）を写す
```

- **合格**（測る前に決めた条件）:
  - ID: adc_id 02030101・time_id 02030102・proj 00310200・adcs 4・kind g24（START の EVENT の `ids`）
  - specd のログ: **「係数 URAM: 4096 行を 0.6〜1.0 s で書き、VERIFY 通過（CRC 0x891be197、STAT 0x15）」**
  - STATUS: state IDLE・time_ok 1・health 0x0000・flags 0x000
  - 起動の見張り: 4 コアとも FLAGS 0（最初の START の後の STATUS で）
  - AXI_MAX_PIPELINE 0x0102・libs45fast.so は「CRC: 命令」
- **陽性対照**: CU（係数が合わないと START を断る）
- **記録**: proj031 rev 2（2026-10-27）: 0.73 s・CRC 0x891be197・STAT 0x15・ID proj 00310200。proj036 R-4 の ID: lmx_pwr 31（M5 で PWR 3 に）。**YATSUGATAKE M4**（2026-10-28、移植先の bit・`sw/pynq-2g/`）: 0.73 s・CRC 0x891be197・STAT 0x15・ID proj 00310200・kind g24・lmx_pwr 31、STATUS IDLE・time_ok 1・health 0x0000・flags 0x000、AXI_MAX_PIPELINE 0x102・「CRC: 命令」。**YATSUGATAKE M5**（2026-10-28、bit `e3521f51…`・一本化した `sw/pynq/`、bits.json の kind g24 で `--g24`・`--ring-mib`・`--lmx-pwr` なし）: 0.73 s・CRC 0x891be197・STAT 0x15・**usr 7befb740・lmx_pwr 3**・リング 64 MiB・錨は (3, 1) の CAL で通過、STATUS IDLE・time_ok 1・health 0x0000・flags 0x000、AXI_MAX_PIPELINE 0x102・「CRC: 命令」。**YATSUGATAKE M6**（2026-10-30、配線 N/S・ノイズ ON（H-2 だけ道具で OFF）・bit 64dbf45（FDRI は M5 と同じ）・**tcal board**）: 0.73 s・CRC 0x891be197・STAT 0x15・ID proj 00310200・kind g24・usr 64dbf450・lmx_pwr 3・**tcal board**、STATUS IDLE・time_ok 1・health 0x0000・flags 0x000。`GET CAL`: time の a2c_ns A 69.6・B 71.2・C 69.7・D 69.7（bound 5）、TP は adc_path 1 の K（A −69.231・B −69.356・C −69.415・D −69.343、prov 0）。AXI_MAX_PIPELINE 前後 0x102・「CRC: 命令」
