# 受け側 — 命令を打つ・記録を受ける・照合する

道具は 3 つ。どれも `sw/pynq/` にあり、制御 PC（ダウンロード PC）で動く（Python 3 と numpy。`specctl.py` は標準ライブラリだけ）。

| 道具 | 使いどころ |
|---|---|
| `specctl.py` | 制御の口に命令を打つ（台本・手で） |
| `specrecv.py` | データの口から記録を受けてファイルに書き、照合する（長い観測） |
| `s45client.py` | Jupyter から制御と受け取りを 1 つで（短い試験・目で見る） |

## specctl — 命令を打つ

```bash
python3 specctl.py --host <board> STATUS
python3 specctl.py --host <board> "SET A0.bw=256 A1.bw=8 all.shift=9" "START n=100" "SEND ON"
python3 specctl.py --host <board>                    # 対話（1 行ずつ）
python3 specctl.py --host <board> --wait-idle 600    # IDLE になるまで待つ（台本用）
```

最後の応答が `ERR` なら終了の状態は 1。

## specrecv — 受けて書く

```bash
python3 specrecv.py --host <board> --out run1.s45 --seconds 3600 --json run1.json
python3 specrecv.py --file run1.s45                  # 書いたファイルを読み直して同じ照合
```

- **`--out` は追記する。** 走らせるたびに新しい名前にする（同じ名前に書くと前の記録の後ろに続き、照合が落ちる）
- 書き終えた最後の `seq` を 0.2 秒おきに ACK として返す。specd はそこまでを溜まりから消す。specrecv を止めると溜まりが増える
- 60 秒ごと（`--report`）に数を出す。`--json` で最後のまとめを書く

照合するもの（説明できない欠けが 0 で合格）:

- 記録ごとの CRC-32
- `seq` の欠けが DROP・SKIP の EVENT で全部説明できる
- (ADC, 窓) ごとに DUMP_K が 1 ずつ、DUMP_T が N_ACC·L ずつ進む
- TP は ADC ごとに区切りの頭のビートが 262,144 ずつ進む

受け終えたら、すぐに specd に `STATUS`（`drop`・`miss` を見る）と、`n` を指定していなければ `STOP` を打つ。

## s45client — Jupyter から

```python
from s45client import S45
s = S45("<board>")
s.status()
s.set(A0_bw=256, A1_bw=8, all_shift=9)   # "A0.bw" を "A0_bw" と書ける
d = s.acquire(25)                        # SEND ON → START n=25 → 8 窓とも届くまで待つ
d.spec("A0").shape                       # (25, 4096)、生の積分値、IF の昇順
d.freq("A0")                             # IF [MHz]
d.tp("A")                                # TP（t_beat・utc_ns・sum・nfr・flags）
s.plot("A0"); s.check(); s.close()
```

- 開いている間は制御の口をふさぐ（specctl は `ERR BUSY`）。同じ命令は `s.cmd("…")` で打てる
- `acquire()` は時刻を答えられないとき、警告を出して時刻なしで取る（`force=False` で止める）
- 手元には窓ごとに直近 500 ダンプ（≒ 20 秒）だけ持つ。全部を残すなら `out=` でファイルにも書く（specrecv `--file` で読める）
- ボードの上の Jupyter では動かさない（受けの処理がボードの CPU を使う）

## 記録の中身

記録の形（s45proto v2）は [`../spec/interface.md`](../spec/interface.md) の 6.。時刻（`utc_ns`）は較正込みで、ADC の口に入った時刻を基にした区間の始まり（[`../spec/timing.md`](../spec/timing.md)）。値の単位と dBm への換算は [`../spec/units.md`](../spec/units.md)。

SAM45-Wide の記録（SLICE）は、ch の並びが IF の昇順で、軸は記録の `if_mhz`（送る 2047 番目の ch の IF）と `df_hz`（125 kHz·B）から **IF(i) = if_mhz ＋ (i − 2047)·df** で作る（Fine の窓と同じ式。`ns` の欄は log2 B）。Fine と Wide を `LOAD` で切り替えた記録は 1 本に混ざってよく、受け側は記録ごとに kind を読む。解析の道具のうち `s45spur.py rec` は Wide の軸を読まない（Wide の櫛のスプリアスは `widecomb.py`）

2G-4 の記録（FULL、kind 1）は窓 A0〜D0（コア 0〜3）・nch 32768・df 62.5 kHz で、ch の並びは IF の昇順（送る i = 32767 − c、ch c の IF = 4096 − c·df MHz）。軸は Wide と同じ式 **IF(i) = if_mhz ＋ (i − 2047)·df**（`s45client.if_axis`）。記録の `src` がそのダンプの入力の ADC。s45client が手元に残すダンプの数は ch の数で割る（窓ごとに 62）。受けは tint 20.48 ms で ≒ 25 MB/s（30 分で ≒ 44 GB）なので、`specrecv --out` の置き場所の空きを見る。記録の確かめは `g24cw.py`（頭の欄・床・CW の ch と IF。`--same` で同じ ADC を入れた 4 窓が bit 単位で同じか）、tint をまたいだ束ねのレベルは `level.py`

2G-1-Fast の記録（FULL、kind 1）は窓 A0 の 1 本・nch 131072・df 15.625 kHz で、ch の並びは IF の昇順（送る i = 131071 − c、ch c の IF = 4096 − c·df MHz）。軸は 2G-4 と同じ式 **IF(i) = if_mhz ＋ (i − 2047)·df**（`s45client.if_axis`）。記録の `src` がそのダンプの入力の ADC。s45client が手元に残すダンプの数は ch の数で割る（15）。受けの量は 2G-4 と同じ（tint 20.48 ms で ≒ 25 MB/s）。記録の確かめは `g21cw.py`（頭の欄・床・CW の ch と IF。`--sg-mhz` で CW、`--posctl` で軸の向きの陽性対照）
