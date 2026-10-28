# V2-b — tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕）

- **前提**: 共通の前提。配線 N。受けは制御 PC（ボードの上ではない）。**終わったら必ず STOP**。specd は `--loop-log-ms 0.1` を足して起こす（1 周の内訳）
- **手順**:

```bash
python3 specctl.py --host $B ID "SET A0.src=A B0.src=B C0.src=C D0.src=D shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON" | tee v2b_id.txt
python3 specrecv.py --host $B --out v2b.s45 --seconds 1800 --json v2b.json
python3 specctl.py --host $B STATUS STOP | tee v2b_status.txt
python3 loopsum.py <specd の 1 周の記録>
```

- **合格**:
  - 受け: SPEC ≒ 4 × 87,890（1,800 s / 20.48 ms）・送り出し ≒ 24〜26 MB/s、**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**、照合 通過、health・flags・sat 0
  - STATUS（STOP の直前）: miss・pl_drop・pl_crc・pl_err 0、time_ok 1・forced 0、loop_slow ≦ 5
  - 1 周の計（出口の記録 1 本あたり）≦ 16 ms（20.48 ms の 78 %）
  - AXI_MAX_PIPELINE が前と後で 0x0102
- **陽性対照**: specd を `--posctl-ring-stall 8` で起こし、40 s 受ける: 受け側 kgap 4（4 窓 × 1 回の見込み。Wide は 7 本で 7）・tdev 0、STATUS の pl_drop > 0
- **記録**: proj036 R-3（2026-10-28 05:33〜06:04 UTC）: 44.6 GB（24.8 MB/s）・SPEC 355,080・CRC・欠け 0・照合 通過・miss・kgap・pl_drop 0・loop_slow 1・1 周の最長 23.2 ms・リングの山 4.2 MB。1 周の計 13.4 ms（R-1、60 s）。**YATSUGATAKE M4 の短い回帰**（2026-10-28、300 s、`--loop-log-ms 0.1`）: 7.36 GB（24.5 MB/s）・SPEC 58,505・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。STATUS: miss・pl_drop・pl_crc・pl_err 0・time_ok 1・forced 0・loop_slow 1・1 周の最長 22.74 ms・p99 11.2 ms・リングの山 3.2 MB。1 周の計 13.10 ms。AXI_MAX_PIPELINE 前後 0x102。**YATSUGATAKE M5 の短い回帰**（2026-10-28、300 s、一本化した `sw/pynq/`・LMX PWR 3・リング 64 MiB は既定）: SPEC 58,505・7.36 GB・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。STATUS: miss・pl_drop・pl_crc・pl_err 0・time_ok 1・forced 0・loop_slow 1・最長 21.82 ms・p99 11.1 ms・pl_peak 3.2 MB。1 周の計 13.03 ms（`loopsum.py --nwin 4`）。AXI_MAX_PIPELINE 前後 0x102
