# EQ-2 — 2 コアに同じ ADC で bit 単位で同じ

- **前提**: 共通の前提。配線 N か N/S
- **手順**:

```bash
rm -f eq2.s45
python3 specctl.py --host $B "SET A0.src=C B0.src=C shift=7 tint=0.04096 fmt=both" "SEND ON" "START n=50"
python3 specrecv.py --host $B --out eq2.s45 --seconds 10 --json eq2.json
python3 g22cw.py eq2.s45 --src CC --same
python3 g22cw.py eq2.s45 --src CC --same --posctl-same
python3 specctl.py --host $B STATUS
```

- **合格**: 同じ DUMP_T の B0 が A0 と u64 で bit 単位で同じ **50 / 50 組**・照合 通過（fmt=both の f32 の組も一致）。STATUS の miss・drop 0（fmt=both の loop_max・loop_slow は記録だけ。下の注）
- **陽性対照**: `--posctl-same`（B0 を 1 ダンプずらす）で 0 / 49 組（違う ch が 6 万個台）
- **記録**: proj034 R-1c（2026-10-29、1 回目の 034 の Overlay の中）: 50 / 50 組、陽性対照 0 / 49 組（違う ch 65,392〜65,440）。TP の ADC {A, B, C}。対照の proj025 も 51 / 51 組。sim では P-4a・sim-g22x2 で 2 コアのダンプが 0 / 8,192 行違い
- **YATSUGATAKE M4**（2026-10-31、配線 N）: `--fast` なし・ありとも 50 / 50 組・照合 通過、陽性対照 0 / 49 組（違う ch 65,527〜65,536）。miss・drop 0。loop_max は `--fast` なし 106.4 ms・loop_slow 26、**あり 16.7 ms・loop_slow 0**
- 注: fmt=both の運転は proj034・proj025 とも loop_max 72〜76 ms・loop_slow 26〜28（tint 40.96 ms、miss・drop 0）。PS の側の持ち越しだったが、`--fast` ありでは消えた（M4）
