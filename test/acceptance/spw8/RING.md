# RING — リング 64 MiB が PS の 0.3 s の止まりを吸う

- **前提**: V2-b と同じ（tint 20.48 ms・32 窓）。2G-4 の RING と同じ仕掛け（specd の `--posctl-ring-stall` を 0.3 s に）
- **手順**: specd を 0.3 s の止まりを入れる形で起こし、60 s 受ける
- **合格**: pl_drop 0・受けの kgap 0・説明のない欠け 0。pl_peak ≦ 64 MiB の 1/2（PL は PS へ ≒ 51 MB/s、0.3 s で ≒ 15 MB）
- **陽性対照**: 止まりを 8 s にすると pl_drop > 0（V2-b の陽性対照）
- **記録**: なし（2G-4 で入れた判定）
