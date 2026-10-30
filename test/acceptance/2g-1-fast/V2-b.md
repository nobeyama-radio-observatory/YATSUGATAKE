# V2-b — tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕）

- **前提**: 共通の前提。配線 N。受けは制御 PC（ボードの上ではない）。**終わったら必ず STOP**。specd は `--loop-log-ms 0.1` を足して起こす（1 周の内訳）
- **手順**:

```bash
python3 specctl.py --host $B ID "SET src=A shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON" | tee v2b_id.txt
python3 specrecv.py --host $B --out v2b.s45 --seconds 1800 --json v2b.json
python3 specctl.py --host $B STATUS STOP | tee v2b_status.txt
python3 loopsum.py <specd の 1 周の記録>
```

- **合格**:
  - 受け: SPEC ≒ 87,890（1,800 s / 20.48 ms）・送り出し ≒ 24〜26 MB/s、**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**、照合 通過、health・flags・sat 0
  - STATUS（STOP の直前）: miss・pl_drop・pl_crc・pl_err 0、time_ok 1・forced 0、loop_slow ≦ 5
  - 1 周の計（出口の記録 1 本あたり）≦ 16 ms（20.48 ms の 78 %。2G-4 と同じ線。proj033 R-3 の 40.96 ms で loop_max 15.1 ms）
  - AXI_MAX_PIPELINE が前と後で 0x0102
- **陽性対照**: specd を `--posctl-ring-stall 8` で起こし、40 s 受ける: 受け側 kgap 1（流れ 1 本 × 1 回の見込み）・tdev 0・説明のない欠け 0、STATUS の pl_drop > 0、ボードが固まらない（2G-4 の M6 で G21 の `pump()` にも止まりの仕掛けを入れた）
- **記録**: proj033 R-3（2026-10-28 22:31〜23:02 UTC、**tint 40.96 ms**、ノイズ ON・src A、`--fast` なし）: SPEC 43,964・22.04 GB・CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過・health・flags・sat 0、毎分の STATUS で miss・kgap・drop・pl_drop・pl_crc・pl_err・loop_slow 0、loop_max 15.1 ms・pl_peak 3.1 MB、VCCINT 13.27〜13.82 A・40〜46 ℃。**tint 20.48 ms は M6 で初めて回す**（M0 の決めること 3）
