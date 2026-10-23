# V2-b — specd の 40.96 ms で 30 分（欠け・CRC・束ね・PS の負荷）

- **前提**: 共通の前提。specd（`--wide` なし、bits.json の `kind` で Wide）。配線 N。**終わったら必ず STOP**（RUN のまま残すと specd の溜まりが溢れる）
- **手順**:

```bash
python3 specctl.py --host $B ID "SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7" GET "START n=0" "SEND ON" | tee v2b_id.txt
python3 specrecv.py --host $B --out v2b.s45 --seconds 1800 --json v2b.json
python3 specctl.py --host $B STATUS STOP | tee v2b_status.txt
```

- **合格**（測る前に決めた条件）:
  - 受け側: SPEC ≒ 7 × 43,945（1,800 s / 40.96 ms）・TP ≒ 4 × 43,945、**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**、記録は全部 版 2、health・flags・sat 0
  - STATUS（STOP の直前）: miss・bdrop・r_bad・pl_drop・pl_crc・pl_err・tp_lost・tp_rec_lost 0、**bund_r は 7 本とも 1,048,576（2·G）**、C1（B 4 の空の流れ）は「-」、time_ok 1・forced 0、loop_slow 0
  - ID・START の EVENT に `kind: wide`・`usr`（載せた bit の commit）・`lmx_pwr: 3`
  - STATUS の行を必ず残す
- **陽性対照**: specd を `--posctl-ring-stall 8` で起こし、40 s 受ける: 受け側 kgap 7（7 本 × 1 回）・tdev 0、STATUS の bdrop > 0・pl_drop > 0・r_bad 0・bund_r は 7 本とも 2·G のまま
- **記録**: proj023 手順 4d（2026-10-17、ビルド 11、30 分）: SPEC 308,210・TP 176,121・5.07 GB、欠け・CRC など 0、bund_r 7 本とも 2·G、loop_slow 0・loop_p99 6.9 ms。陽性対照 kgap 7・tdev 0・bdrop 8。YATSUGATAKE M4・M5（300 s の短縮、PWR 31）・「M5 の後」（300 s、PWR 3）: 同じ（M5 の後: SPEC 51,191、loop_p99 7.2 ms）
