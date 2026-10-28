# RING — リング 64 MiB が PS の 0.3 s の止まりを吸う

- **前提**: 共通の前提（`--ring-mib 64`）。配線 N。tint 20.48 ms で RUN・SEND ON・受けは制御 PC
- **手順**: 2 分走らせてから、ボードで取得のプロセスを止めて再開する（specd の pid のファイルから）

```bash
P=$(cat /tmp/specd.pid); sudo kill -STOP $P; sleep 0.3; sudo kill -CONT $P      # 1 回目
# 1 分おいて STATUS、それから陽性対照
P=$(cat /tmp/specd.pid); sudo kill -STOP $P; sleep 0.8; sudo kill -CONT $P
python3 specctl.py --host $B STATUS
```

- **合格**: 0.3 s の止まりで **pl_drop 0**・受けの kgap 0・照合 通過・リングの山（pl_peak）は 64 MiB 未満（2G-4 は 102.4 MB/s なので 0.3 s で ≒ 31 MB）
- **陽性対照**: 0.8 s の止まり（≒ 82 MB > 64 MiB）で **pl_drop > 0 が数えられ**、受けの kgap が DROP の EVENT で説明される（説明のない欠け 0）
- **記録**: なし（interface 8. の 11 で 2026-10-28 に判定に入れた。M6 で初めて回す。参考: proj030 R-3 で apt の定時の仕事の 313 ms の止まりが 64 MiB の 94 % まで溜まり、落ちは 0）
- 注意: `kill -STOP` を止める先を取り違えない（pid のファイルの値を `ps -p` で確かめてから）。止める区間が `sleep` の精度と ssh の遅れで延びるので、ボードの上の 1 行のコマンドで行う
