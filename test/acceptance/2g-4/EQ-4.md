# EQ-4 — 4 コアに同じ ADC で bit 単位で同じ

- **前提**: 共通の前提
- **手順**:

```bash
python3 specctl.py --host $B "SET A0.src=C B0.src=C C0.src=C D0.src=C shift=7 tint=0.04096 fmt=both" "SEND ON" "START n=50"
python3 specrecv.py --host $B --out eq4.s45 --seconds 10 --json eq4.json
python3 g24cw.py eq4.s45 --src CCCC --same
python3 g24cw.py eq4.s45 --src CCCC --same --posctl-same
```

- **合格**: B0・C0・D0 が A0 と u64 で bit 単位で同じ **50 / 50 組 × 3**・照合 通過（fmt=both の f32 の組も一致）
- **陽性対照**: `--posctl-same`（1 ダンプずらす）で 0 / 49 組 × 3（違う ch が 3 万個台）
- **記録**: proj031 R-1b rev 2: 50 / 50 組 × 3、陽性対照 0 / 49 組 × 3（違う ch 32,738〜32,755）。**YATSUGATAKE M4**（2026-10-28、配線 N）: 50 / 50 組 × 3・照合 通過、陽性対照 0 / 49 組 × 3（違う ch 32,765〜32,768）
