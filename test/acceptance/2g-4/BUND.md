# BUND — 束ね（C の道）のレベルが tint をまたいで同じ

- **前提**: 共通の前提（`--fast-ring` は n_sum ≧ 2 の束ねも C で）。**specd は `--net-budget-mbs 0` で起こす**（10.24 ms は予算 30 MB/s を越え、M5 から SET で断られる。NET）。配線 N。**1 回の Overlay の読み込みの中で tint を切り替える**（specd を起こし直さない）。前に 2 分空回し
- **手順**: tint を 10.24 → 30.72 → 20.48 → 10.24 → 30.72 → 20.48 ms と、各 20 s ずつ

```bash
python3 specctl.py --host $B "SET tint=<t> fmt=f32" "START n=0"; python3 specrecv.py --host $B --out bund_<i>.s45 --seconds 20; python3 specctl.py --host $B STOP
python3 level.py bund_*.s45
```

- **合格**: 窓ごとの「中身の平均 / nacc」の中央値が、10.24 ms の 2 回の平均に対して **0.999〜1.001**（4 窓とも）。各区間の照合 通過・miss 0
- **陽性対照**: specd を `--posctl-noacc`（足さずに写す）で起こし、30.72 ms の値が 10.24 ms の **0.333 ± 0.01** 倍
- **記録**: proj036 R-2（2026-10-28）: 0.9995〜1.0004（4 窓とも）、陽性対照 0.330〜0.332 倍。PL なしの照合 P-1（`test_bund_fast.py`: C の道の記録が Python の道と頭・中身・CRC まで bytes で同じ）も通過
