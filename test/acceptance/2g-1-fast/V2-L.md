# V2-L — tint 20.48 ms で 2 時間（電流・温度・落ちない）

- **前提**: V2-b と同じ。受けは制御 PC で `--out` なし（2 時間で ≒ 177 GB。照合は受けながら同じ）。ボードで AMS・INA220 を 10 s ごとに記録（`amslog.py`）。STATUS と AXI_MAX_PIPELINE を 1 分ごとに読む
- **手順**:

```bash
sudo -E $(which python3) amslog.py --out v2l.ams.log --period 10 --seconds 7800 &     # ボード
python3 specctl.py --host $B ID "SET src=A shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON"
python3 specrecv.py --host $B --seconds 7200 --json v2l.json
python3 specctl.py --host $B STATUS STOP
```

- **合格**: 7,200 s で受けの CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過、STATUS の miss・pl_drop・pl_crc・pl_err 0 が毎分、AXI_MAX_PIPELINE が毎分 0x0102、
  **VCCINT ≦ 15 A で平ら**（proj033 R-3 の 30 分で 13.3〜13.8 A。2G-4 の線と同じく、測った値に ≒ 1.5 A の余裕）・PL の温度は平ら（上がり続けない）、ボードが落ちない
- **陽性対照**: V2-b の陽性対照（同じ見張り）
- **記録**: なし（proj024・proj033 とも 30 分まで。**M6 で初めて回す**、M0 の決めること 3）。参考: proj033 R-3（tint 40.96 ms・30 分）の VCCINT 13.27〜13.82 A・40〜46 ℃ で平ら
- 注意: 受けが `--seconds` で先に切れると、STOP までの間に specd の溜まりが満ちて STATUS の drop が増える（2G-4 の proj036 R-4 で 903）。drop は受けの終わりの前の STATUS で読む
- **YATSUGATAKE M6**（2026-10-31 03:32〜05:32 UTC、配線 N/S・ノイズ ON・src A、M5 の bit・`--prefault --fast --fast-ring`・tcal board、amslog 10 s ごと）: **通過**。7,200 s・SPEC 351,541・176.0 GB（24.4 MB/s）・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。毎分の STATUS 118 回とも miss・drop・pl_drop・pl_crc・pl_err 0・loop_slow 0、AXI 毎分 0x0102（前・後とも）。loop_max 7.05 ms・p99 5.4 ms・pl_peak 2.1 MB。受けの終わりの直後の STATUS で drop 0・inflight 0。**VCCINT 13.27〜13.81 A**（INA220 0x40、前 1/4 の平均 13.53・後 1/4 13.51 A）、PL の温度（temp20）41.9〜45.6 ℃（前 1/4 43.84・後 1/4 43.69 ℃）。ボードは落ちなかった
