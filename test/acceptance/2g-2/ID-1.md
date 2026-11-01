# ID-1 — 自己記述・起動の見張り

- **前提**: 共通の前提。specd を起こした直後
- **手順**:

```bash
python3 specctl.py --host $B ID STATUS | tee id1.txt
# --fast を使うなら、ボードの specd のログから「CRC:」（libs45fast.so）の行を写す
```

- **合格**（測る前に決めた条件）:
  - ID: adc_id 020a0101・time_id 020a0102・proj 00340100・kind g22（START の EVENT の `ids`）。M5 の後は `usr`（USR_ACCESS の commit）・`lmx_pwr=3`・`tcal=board` も
  - STATUS: state IDLE・time_ok 1・health 0x0000・flags 0x000
  - 起動の見張り: 2 コアの FLAGS 0（最初の START の後の STATUS で）
  - AXI_MAX_PIPELINE 0x0102。`--fast` なら libs45fast.so は「CRC: 命令」
- **陽性対照**: proj025 の bit（PROJ 0x0025_0100、同じ (10, 1)。ボードの `~/proj025/proj025.bit`）で起こすと、ID の proj が **00250100**・usr none になる。G22Backend は PROJ を照らさない（移植の決めること 3 で案 A、2026-10-31）ので START は通る。M5 で確かめた（proj 00250100・usr none、20 本の取得は照合 通過）
- **記録**: proj034 R-1（2026-10-29 22:43〜22:57 UTC、034 → 025 → 034 → 025）: ID proj 00340100・adc 020a0101・time 020a0102、START が通った（G22Backend の照合）、health 0・flags 0。timebase は「未較正」（proj034 は CAL を R の後に足した）
- **YATSUGATAKE M4**（2026-10-31、ボード `~/2g-2-m4`・M3 の bit・`--fast` なし／あり）: ID adc 020a0101・time 020a0102・proj 00340100・kind g22・usr none・lmx_pwr 3・**tcal board**、IDLE・time_ok 1・health 0x0000・flags 0x000。AXI 0x0102・「CRC: 命令」
- **YATSUGATAKE M6**（2026-11-01 01:54 UTC、ボード `~/2g-2-m6`・M5 の bit（usr b0dc6ea0）・`--prefault --fast --fast-ring --loop-log-ms 0.1`）: **通過**。ID adc 020a0101・time 020a0102・usr b0dc6ea0・lmx_pwr 3・**tcal board**、START の EVENT で proj 00340100・kind g22。STATUS IDLE・time_ok 1・health 0x0000・flags 0x000。AXI 0x0102・「CRC: 命令」。陽性対照は M5（proj025 の bit で proj 00250100、案 A なので START は通る）
