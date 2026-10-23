# PS-3 — TP の跳ねの見張り（EVENT TP_JUMP・step_db）

Wide の TP は Fine と同じ作りで、跳ねの見張り（`tpjump.py`）も同じコードを通る。Fine の PS-3 を Wide の bit で回す。

- **前提**: 共通の前提。specd（`--wide` なし）。配線 N（プログラムアッテネータを使う。ふだんは PATT 13 dB）。PC での試験 `python3 test_tpjump.py`・`bash test_fake.sh tpjump` が通っていること
- **手順**:

```bash
python3 specctl.py --host $B "SET tint=0.04096 fmt=f32 A.b=1 B.b=2 C.b=4 D.b=1 all.shift=7"
python3 specrecv.py --host $B --out ps3.s45 --seconds 120 --json ps3.json | tee ps3.log &
python3 specctl.py --host $B "SEND ON" "START n=0"
sleep 40
python3 -c "from instr import Atten; a = Atten(); a.set(14.0); print('PATT', a.get())"
sleep 40
python3 -c "from instr import Atten; a = Atten(); a.set(13.0); print('PATT', a.get())"
sleep 30; python3 specctl.py --host $B STATUS STOP; wait
grep TP_JUMP ps3.log
```

- **合格**（測る前に決めた条件）:
  - 4 ADC とも、step_db が ≒ ∓0.94 dB の跳ねが 2 回（PATT を 14 dB にした時・13 dB に戻した時）。STATUS の tp_jump は 2 以上（入力の側の小さな跳ねが加わる日がある。下の「予言で書いておくこと」）
  - **step_db −0.94 / +0.94 ± 0.03**（アッテネータの 1 dB の段の実際の値 0.945）、ovr false
  - `db`（ずれの最大）は記録するだけ（PATT の切り替えの瞬断 ≒ 3 ms と TP の区切りの位相で決まる。Fine の M6 の改め）
- **陽性対照**: この判定そのもの（入れた段差が出る）。PATT 固定の運転（V2-b）の跳ねが負の側
- **予言で書いておくこと**: PATT 固定でも、入力の側の小さな跳ね（0.01〜0.05 dB、4 ADC そろって固まって出る）が日によって数十〜百数十回出る（2026-10-23 の M5 で 189 回・Fine で 133 回、「M5 の後」の V2-b で 6 回）。これは入力の側で、跳ねの 2 回の判定は step_db が ≒ 0.94 dB のものだけを数える
- **記録**: なし（Wide では新しい判定）。Fine は YATSUGATAKE M6 で通過（2026-10-17、step_db −0.94 / +0.94）
