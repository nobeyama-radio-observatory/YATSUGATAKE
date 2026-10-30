# V2-L — tint 20.48 ms で 2 時間（電流・温度・落ちない）

- **前提**: V2-b と同じ。受けは制御 PC で `--out` なし（2 時間で ≒ 180 GB。照合は受けながら同じ）。ボードで AMS・INA220 を 10 s ごとに記録（`amslog.py`）。STATUS と AXI_MAX_PIPELINE を 1 分ごとに読む
- **手順**:

```bash
sudo -E $(which python3) amslog.py --out v2l.ams.log --period 10 --seconds 7800 &     # ボード
python3 specctl.py --host $B ID "SET A0.src=A B0.src=B C0.src=C D0.src=D shift=7 tint=0.02048 fmt=f32" GET "START n=0" "SEND ON"
python3 specrecv.py --host $B --seconds 7200 --json v2l.json
python3 specctl.py --host $B STATUS STOP
```

- **合格**: 7,200 s で受けの CRC・欠け・説明のない欠け・kgap・tdev 0・照合 通過、STATUS の miss・pl_drop・pl_crc・pl_err 0 が毎分、AXI_MAX_PIPELINE が毎分 0x0102、
  **VCCINT ≦ 34 A で平ら**（目安 38 A に余裕）・PL の温度は平ら（上がり続けない）、ボードが落ちない
- **陽性対照**: V2-b の陽性対照（同じ見張り）
- **記録**: **proj036 R-4（2026-10-28 06:15〜08:15 UTC）: 通過**。176.8 GB（24.6 MB/s）・SPEC 1,406,164・CRC・欠け・kgap・tdev 0・照合 通過、毎分の miss・pl_drop・pl_crc・pl_err 0・AXI_MAX_PIPELINE 0x0102、loop_slow 1・1 周の最長 23.1 ms・リングの山 3.3 MB、VCCINT 32.6 A（32.3〜33.0）・PL 53.6〜60.0 ℃ で平ら
- 注意: 受けが `--seconds` で先に切れると、STOP までの間に specd の溜まりが満ちて STATUS の drop が増える（R-4 で 903）。drop は受けの終わりの前の STATUS で読む。**YATSUGATAKE M6**（2026-10-30 10:29〜12:29 UTC、配線 N（N/S の SG を切った形）・bit 64dbf45（FDRI は M5 と同じ）・tcal board）: 7,200 s・SPEC 1,406,165・176.8 GB・CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0・照合 通過・health・flags・sat 0。毎分の STATUS 119 回とも miss・pl_drop・pl_crc・pl_err 0、AXI 毎分 0x0102。VCCINT 32.34〜32.96 A（前 1/4 の平均 32.63・後 1/4 32.66 A）、PL の温度（temp20）55.0〜59.0 ℃（前 1/4・後 1/4 とも 56.81 ℃）。ボードは落ちなかった
