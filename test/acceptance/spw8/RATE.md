# RATE — PL と PS の取得 10.24 ms × 32 窓で 30 分

- **前提**: 共通の前提。配線 N・SG 出力 OFF。リング 64 MiB。C の読み手（M4: `libspwfast.so` をボードで `gcc -O3 -march=armv8-a+crc` で作る。M5b の後: specd の `--fast --fast-ring`）。AMS の温度と VCCINT を 10 s ごとに記録
- **手順**:

```bash
# M4
sudo -E $(which python3) spw_b5.py --clkin 0 --ref 10 --cfg b5 --fast --ng 5 --sec 1800 --out runs/rate
# M5b の後: PL の tint 10.24 ms・ネットワークの tint 20.48 ms（specd が 2 つずつ束ねる）で 30 分。受けは V2-b と同じ
```

- **合格**: 30 分で **DROP 0・照らしの誤り 0・CORE_FLAGS 0・窓の FLAGS 0**、輪の中の時間の割合 ≦ 70 %（P-13 の 55 % に余裕を見る）、リングの PEAK が運転中に増えない、VCCINT ≦ 40 A・温度が平ら（30 分の後半で ±1 ℃）
- **陽性対照**: `--fast-posctl`（C の CRC の期待値を 1 bit 反転）で窓のレコードが全部 CRC の誤りになる。Python の読み手（`--fast` なし）では DROP が出る（P-9・P-13 の 1 行目）
- **記録**: proj032 P-13（2026-11-03、`runs/p13_long`）: 1800 s・51.6 MB/s・DROP 0・輪の中の時間 55.0 %・1 本 176 µs・PEAK 40.1 MB（30 s と同じ）・窓のレコード 5,626,480 本・照らしの誤り 0、VCCINT 38.5 A・temp20 62.2〜62.6 ℃。**全部通過**
