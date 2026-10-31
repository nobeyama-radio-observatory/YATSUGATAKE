# RING — リング 64 MiB が PS の 0.3 s の止まりを吸う

- **前提**: 共通の前提（リング 64 MiB は 2G の既定）。配線 N。tint 20.48 ms で RUN・SEND ON・受けは制御 PC
- **手順**: 2 分走らせてから、ボードで取得のプロセス（s45acq、specd の子の `multiprocessing.spawn`）を止めて再開する。2G-4 の M6 と同じく、止める先は `ps` で確かめてから

```bash
P=<取得の子の pid>; sudo kill -STOP $P; sleep 0.3; sudo kill -CONT $P      # 1 回目
# 1 分おいて STATUS、それから陽性対照
P=<取得の子の pid>; sudo kill -STOP $P; sleep 0.8; sudo kill -CONT $P
python3 specctl.py --host $B STATUS
```

- **合格**: 0.3 s の止まりで **pl_drop 0**・受けの kgap 0・照合 通過・リングの山（pl_peak）は 64 MiB 未満（PL の書きは 1 ダンプ 131,072 ch を dt 10.24 ms ごとで、2G-4 と同じ ≒ 102.4 MB/s の見込み。0.3 s で ≒ 31 MB、2G-4 の M6 は ssh と sleep の遅れで 48.3 MB）
- **陽性対照**: 0.8 s の止まり（≒ 82 MB > 64 MiB）で **pl_drop > 0 が数えられ**、受けの kgap が DROP か BDROP の EVENT で説明される（説明のない欠け 0）
- **記録**: なし（M6 で初めて回す）。参考: 2G-4 の M6（2026-10-30）: 0.3 s で pl_drop 0・pl_peak 48.3 MB、0.8 s で pl_drop 385・kgap 4 がすべて BDROP で説明された
- 注意: 止める区間が `sleep` の精度と ssh の遅れで延びるので、ボードの上の 1 行のコマンドで行う
- **YATSUGATAKE M6**（2026-10-31 03:25〜03:29 UTC、V2-b と同じ specd）: **通過**。0.3 s の止まりで pl_drop 0・kgap 0・miss 0・pl_peak 40.9 MB・loop_max 87.4 ms。陽性対照 0.8 s で pl_drop 66・miss 33・kgap 1・bdrop 1・pl_peak 64 MiB、受けの kgap 1 は BDROP の EVENT で説明された（説明のない欠け 0・tp_gap 1）。STATUS の data_drop は受け手の宛先なので伏せた
