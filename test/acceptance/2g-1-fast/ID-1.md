# ID-1 — 自己記述・起動の見張り

- **前提**: 共通の前提。specd を起こした直後
- **手順**:

```bash
python3 specctl.py --host $B ID STATUS | tee id1.txt
# --fast を使うなら、ボードの specd のログから「CRC:」（libs45fast.so）の行を写す
```

- **合格**（測る前に決めた条件）:
  - ID: adc_id 020b0101・time_id 020b0102・proj 00330100・kind g21（START の EVENT の `ids`）。M5 の後は `usr`（USR_ACCESS の commit）・`lmx_pwr=3`・`tcal=board` も
  - STATUS: state IDLE・time_ok 1・health 0x0000・flags 0x000
  - 起動の見張り: コアの FLAGS 0（最初の START の後の STATUS で）
  - AXI_MAX_PIPELINE 0x0102。`--fast` なら libs45fast.so は「CRC: 命令」
- **陽性対照**: proj024 の bit（PROJ 0x0024_0100、同じ (11, 1)。ボードの `~/proj024/proj024.bit`）で起こすと、ID の proj が **00240100**・usr none になる。G21Backend は PROJ を照らさない（移植の M5 の決めること 4 で案 A、2026-10-31）ので START は通る。M5 で確かめた（proj 00240100・usr none、20 本の取得は照合 通過）
- **記録**: proj033 R-1（2026-10-28、4 回）: ID proj 00330100・adc 020b0101・time 020b0102、START が通った、health 0・flags 0x0。timebase は「未較正」（proj033 は CAL を R-5 の後に足した）
