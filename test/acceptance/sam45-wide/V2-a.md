# V2-a — PL の積分器: 10.24 ms × 4 の和 = 40.96 ms（整数で一致）

SAM45-Fine の V2-a は specd の束ね（10.24 ms → 40.96 ms）の比べ。Wide では PL の積分器そのものを比べる（proj023 の H-3「V2-a 相当」）。

- **前提**: 共通の前提。ボード直（root、specd を止めてから）。配線 N
- **手順**:

```bash
sudo -E $(which python3) wide_v2.py --clkin 0 --ref 10 --v2a
```

- **合格**（測る前に決めた条件）:
  - 4 ADC とも（既定: A・C が B 1、B・D が B 2）、流れ 1（N_ACC 5120）のダンプ 10 組が、流れ 0（N_ACC 1280）の 4 個の和と**全 ch で整数として一致**（一致しない ch 0・欠け 0）
  - 2 本の流れの F0 が同じ、RUN_T − START_AT が 8 本とも +1、DUMP_T = K_F ＋ 2048·DUMP_F0、FLAGS・DUMP_SAT 0、SEQ の連続、REC_LATE・DROP_CNT 0
- **陽性対照**: 1 個ずらした和（q = 1..4）は 10 組とも一致しない（道具が出す）
- **記録**: proj023 手順 4c（2026-10-17、ビルド 11）: 4 ADC とも 10 組が全 ch 一致、陽性対照 10/10 で不一致、F0 753152
