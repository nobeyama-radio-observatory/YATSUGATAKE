# S — specd の SNAP（RAW の生サンプル。S-1・S-2・S-4）

- **前提**: 共通の前提。specd（`--wide` なし）。配線 N。取得は IDLE（START の前）
- **手順**:

```bash
python3 s45snap.py --host $B --adc ABCD --n 16 --every 20 --out snap
python3 specctl.py --host $B "START n=0" "SNAP adc=A n=1" STOP       # 陽性対照
```

- **合格**（測る前に決めた条件）:
  - 4 ADC とも道具の判定が OK: 16 塊、S-1 間隔（dump_t の差・frame の差・k の連続）、S-2 中身（下位 2 bit が 0・振り切れ 0）、S-4 UTC の刻み 20 ms ちょうど
  - 電力が同じ日の V2-b の STATUS の tp_dbfs と ±0.2 dB（今の配線 N で ≒ −31.4 dBFS）
  - 受けた記録の照合: SNAP 64・CRC・欠け・dup 0、版 2 だけ
- **陽性対照**: RUN（ARMED）の間の `SNAP` は `ERR STATE … の間は SNAP できない`
- **記録**: **YATSUGATAKE M6 で通過（2026-10-23、bit `54b0dbea…`・usr ba456e10・PWR 3、`~/m2/m6w/n2/s.txt`・`s_p.txt`）: 4 ADC とも 16 塊・−31.25〜−31.52 dBFS（V2-b の tp_dbfs と 0.01 dB 内）・刻み 20 ms・振り切れ 0、陽性対照 ERR STATE ARMED**。 proj023 手順 4g（2026-10-17、ビルド 11）: 4 ADC とも 16 個・間隔 OK・刻み 20,000,000 ns・振り切れ 0・−12.42〜−12.47 dBFS（その日の配線、V2-b の tp_dbfs と同じ）、陽性対照は ERR STATE ARMED
