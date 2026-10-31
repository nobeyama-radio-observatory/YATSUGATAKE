# V2-b — tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕）

- **前提**: 共通の前提。配線 N。受けは制御 PC（ボードの上ではない）。**終わったら必ず STOP**。specd は `--loop-log-ms 0.1` を足して起こす（1 周の内訳）
- **手順**:

```bash
python3 specctl.py --host $B ID "SET A0.src=A B0.src=B shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON" | tee v2b_id.txt
python3 specrecv.py --host $B --out v2b.s45 --seconds 1800 --json v2b.json
python3 specctl.py --host $B STATUS STOP | tee v2b_status.txt
python3 loopsum.py <specd の 1 周の記録> --nwin 2
```

- **合格**:
  - 受け: SPEC ≒ 175,780（2 窓 × 1,800 s / 20.48 ms）・送り出し ≒ 24〜26 MB/s、**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**、照合 通過、health・flags・sat 0
  - STATUS（STOP の直前）: miss・pl_drop・pl_crc・pl_err 0、time_ok 1・forced 0、loop_slow ≦ 5
  - 1 周の計（出口の記録 1 本あたり）≦ 16 ms（20.48 ms の 78 %。2G-4・2G-1-Fast と同じ線）
  - AXI_MAX_PIPELINE が前と後で 0x0102
- **陽性対照**: specd を `--posctl-ring-stall 8` で起こし、40 s 受ける: 受け側 kgap が流れ 2 本 × 1 回の見込み・tdev 0・説明のない欠け 0、STATUS の pl_drop > 0、ボードが固まらない（2G-4 の M6 で G22 の `pump()` にも止まりの仕掛けを入れた。2G-4 の M6 ではこの陽性対照でボードが固まったことがある）
- **記録**: proj034 R-3（2026-10-29 23:02〜23:32 UTC、**tint 40.96 ms**、入力は ADC の床だけ・src C・D・TP 4 本、`--fast` なし）: SPEC 87,938（2 窓 × 43,969）・22.2 GB・CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過・health・flags・sat 0、毎分の STATUS で miss・kgap・drop・pl_drop・pl_crc・pl_err・loop_slow 0、**loop_max 29.7 ms・p99 28.7 → 22.0 ms**（1 周で 2 ダンプを抱える形）・pl_peak 4.6 MB、VCCINT 18.75〜19.37 A・44〜51 ℃。**tint 20.48 ms は M6 で初めて回す**（M0 の決めること 2）。
  **YATSUGATAKE M4 の短い回帰**（2026-10-31、300 s、src C・D・TP 4 本）: `--fast` なしは取りこぼし 0 だが loop_max 68.7 ms・p99 57.4 ms・loop_slow 5,453（線に入らない）。**`--fast` ありは SPEC 29,261・7.36 GB・CRC・欠け・kgap・tdev 0・照合 通過・loop_max 22.1 ms・p99 7.5 ms・loop_slow 1・pl_peak 3.2 MB・1 周の計 11.71 ms**（`loopsum.py --nwin 2`）
