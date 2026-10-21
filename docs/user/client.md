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

記録の形（s45proto v2）は [`../spec/interface.md`](../spec/interface.md) の 6.。時刻（`utc_ns`）は較正込み（同 5.2）で、ADC の口に入った時刻。値の単位は [`../spec/interface.md`](../spec/interface.md) の 4.5。
