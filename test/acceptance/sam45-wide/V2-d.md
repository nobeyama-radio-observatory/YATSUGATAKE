# V2-d — LOAD で Wide ⇄ Fine を往復し、取得の種類（`kind`）・ID・usr が切り替わる

Fine の V2-d（同じ種類の 2 本の bit の往復）を、種類の違う bit の往復にしたもの。bits.json の `kind` で取得の種類が決まること（M5 で直した不具合）も見る。

- **前提**: 共通の前提。specd（`--wide` なし）。配線 N。`bits.json` に 2 件: 既定の `sam45-wide`（`"kind": "wide"`・`sha256`）と、相手の `proj021`（SAM45-Fine の bit、`kind` なし・`sha256`・`tp_cal`）
- **手順**:

```bash
python3 specrecv.py --host $B --out v2d.s45 --seconds 300 --json v2d.json &
python3 specctl.py --host $B BITS ID "SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7" "SEND ON" "START n=50"
sleep 5
python3 specctl.py --host $B "LOAD bit=proj021" ID STATUS "SET tint=0.04096" "START n=50"
sleep 5
python3 specctl.py --host $B "LOAD bit=sam45-wide" ID STATUS "SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7" "START n=50"
wait
```

- **合格**（測る前に決めた条件）:
  - LOAD 1 回 ≦ 30 s。EVENT LOAD 2 個の sha256 が bits.json の値
  - Wide のとき: ID が adc_id 02010101・time_id 02010102・`usr` が Wide の bit の USR_ACCESS・`lmx_pwr=3`、START の EVENT の ids に `kind: wide`
  - Fine のとき: ID が adc_id 02020301・time_id 02020302・`usr` が Fine の bit の USR_ACCESS・`lmx_pwr=3`、`GET CAL` が tp_cal (2, 3)
  - どの START も STOP は「n に達した」・miss 0、time_ok=1
  - 受け側: SPEC 1,100（Wide 7 本 × 50 × 2 回 ＋ Fine 8 窓 × 50）・**版 2 だけ**、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0。SLICE（kind 2）と DDC の記録が 1 本の記録に混ざっても照合が通る
- **陽性対照**: `usr`・adc_id が往復で切り替わること自体（specd が本当に載せ替え、取得の種類を替えた証拠）。`bits.json` の `sha256` を 1 文字変えた LOAD が `ERR LOAD … sha256 が bits.json と違う` で止まり、元の bit のまま動くこと
- **予言で書いておくこと**: SLICE と DDC が混ざった 1 本の記録を specrecv で照合するのは初めて（Fine の V2-d は DDC どうし）。照合が混ざりで落ちたら、分光計の不具合ではなく受け側の道具の限りとして記録し、LOAD ごとに受けを分けて回し直す
- **記録**: **YATSUGATAKE M6 で通過（2026-10-23、`~/m2/m6w/n2/v2d_*.txt`・`v2d.json`）: LOAD 20.6・20.3 s、usr ba456e10 → c56caf60 → ba456e10、SPEC 1,100・版 2 だけ・欠け 0・照合 通過（SLICE と DDC の混ざりも通った）、陽性対照 ERR LOAD sha256**。 YATSUGATAKE M5（2026-10-23、`~/m2/m5/m5f_load.txt`）: Wide の specd から `LOAD bit=proj021` が 21.5 s で載り、ID が Fine・`usr=c56caf60`・tp_cal (2, 3)（片道だけ、受けなし）
