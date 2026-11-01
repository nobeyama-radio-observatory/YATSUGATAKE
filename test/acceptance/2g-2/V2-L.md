# V2-L — tint 20.48 ms で 2 時間（電流・温度・落ちない）

- **前提**: V2-b と同じ。受けは制御 PC で `--out` なし（2 時間で ≒ 177 GB。照合は受けながら同じ）。ボードで AMS・INA220 を 10 s ごとに記録（`amslog.py`）。STATUS と AXI_MAX_PIPELINE を 1 分ごとに読む
- **手順**:

```bash
sudo -E $(which python3) amslog.py --out v2l.ams.log --period 10 --seconds 7800 &     # ボード
python3 specctl.py --host $B ID "SET A0.src=A B0.src=B shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON"
python3 specrecv.py --host $B --seconds 7200 --json v2l.json
python3 specctl.py --host $B STATUS STOP
```

- **合格**: 7,200 s で受けの CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過、STATUS の miss・pl_drop・pl_crc・pl_err 0 が毎分、AXI_MAX_PIPELINE が毎分 0x0102、
  **VCCINT ≦ 21 A で平ら**（proj034 R-3 の 30 分で 18.75〜19.37 A。2G-4・2G-1-Fast の線と同じく、測った値に ≒ 1.5 A の余裕）・PL の温度は平ら（上がり続けない）、ボードが落ちない
- **陽性対照**: V2-b の陽性対照（同じ見張り）
- **記録**: なし（proj025・proj034 とも 30 分まで。**M6 で初めて回す**、M0 の決めること 2）。参考: proj034 R-3（tint 40.96 ms・30 分）の VCCINT 18.75〜19.37 A（中央値 19.08 A）・44〜51 ℃ で平ら
- 注意: 受けが `--seconds` で先に切れると、STOP までの間に specd の溜まりが満ちて STATUS の drop が増える（2G-4 の proj036 R-4 で 903）。drop は受けの終わりの前の STATUS で読む
- **YATSUGATAKE M6**（2026-11-01 02:36:02〜04:36:14 UTC、配線 N・ノイズ ON・A0 A・B0 B、M5 の bit・`--prefault --fast --fast-ring`（`--loop-log-ms` なし、RING の後に specd を起こし直した）・tcal board、amslog 10 s ごと）: **通過**。7,200 s・SPEC 703,081・176.3 GB（24.5 MB/s）・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。毎分の STATUS 119 回とも miss・kgap・drop・pl_drop・pl_crc・pl_err 0・loop_slow 0、AXI 毎分 0x0102（前・後とも）。loop_max 12.49 ms・p99 7.5 ms・pl_peak 2.6 MB。受けの終わりの後の STOP で drop 216・inflight 0（下の注のとおり、受けが先に切れた分。最後の毎分の STATUS（04:35）は drop 0）。**VCCINT 19.50〜20.04 A**（INA220 0x40、721 点、前 1/4 の平均 19.72・後 1/4 19.73 A）、PL の温度（temp20）47.9〜52.2 ℃（前 1/4 49.7・後 1/4 50.2 ℃）で平ら。ボードは落ちなかった
- 1 回目（02:33 UTC）は RING の後に specd を起こし直さずに始め、pl_drop が RING の 153 のまま（specd の一生で数える）だったので 3 分で止めて取り直した（増えてはいなかった）
