# V2-b — ネットワークの tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕）

- **前提**: 共通の前提。配線 N。受けは制御 PC。specd は `--prefault --fast --fast-ring --loop-log-ms 0.1`。窓の組 b5（32 窓）。**終わったら必ず STOP**
- **手順**: 論理の窓 32 本を SET（tint 0.02048・fmt f32）→ START → SEND ON → `specrecv.py --seconds 1800` → STATUS・STOP → `loopsum.py --nwin 32`
- **合格**:
  - 受け: SPEC ≒ 2,812,500（32 窓 × 1,800 s / 20.48 ms）・≒ 25.6 MB/s、**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**、照合 通過、health・flags・sat 0。**レコードの窓の番号が論理の窓**（SET の並び）
  - STATUS（STOP の直前）: miss・pl_drop・pl_crc・pl_err 0、time_ok 1・forced 0、loop_slow ≦ 5
  - 1 周の計（出口の記録 1 本あたり）≦ 16 ms（2G と同じ線）
- **陽性対照**: specd を `--posctl-ring-stall 8` で起こし、40 s 受ける: 受け側 kgap が流れごとに出る・tdev 0・説明のない欠け 0、STATUS の pl_drop > 0、ボードが固まらない
- **記録**: なし（study-rfsoc では specd で回していない。試行の道具の 10.24 ms・30 分は RATE）
- **記録（M6）**: YATSUGATAKE M6（2026-11-04 06:57〜07:28 UTC、M5c の bit、specd `--prefault --fast --fast-ring --loop-log-ms 0.1`、b5 の組 32 窓・tint 0.02048、`runs/m6/v2b`）。受け: SPEC 2,811,778・44.5 GB（24.7 MB/s）・**CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0**・照合 通過・health・flags・sat 0・版 2 だけ・窓の番号は論理の窓（`spw_map` は b5 と同じ）。STATUS（STOP の直前）: miss・pl_drop・pl_crc・pl_err 0、time_ok 1・forced 0。**loop_slow 133（線 ≦ 5）**: 最初の 1 分で 109（周の最長 348.4 ms は周 1,407、pl_peak 33.9 MB もそのとき）、後の 29 分で 24。1 周の計: `loopsum.py` は SpW8 のログを読めない（C の道の周のログで SPEC の記録が 0 と出る）ので、STATUS の取得の時間 1,251.5 s ÷ 束 87,876 = **14.2 ms / 束**（線 16 ms）。陽性対照（`--posctl-ring-stall 8`、40 s、07:43 UTC）: kgap 32（流れ 1 本に 1 つ）・tdev 0・説明のない欠け 0・pl_drop 26,830、ボードは固まらなかった。**不合格**（loop_slow）
