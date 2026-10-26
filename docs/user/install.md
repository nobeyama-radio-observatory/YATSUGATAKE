# 設置（ボードに SAM45-Fine・SAM45-Wide を置く）

SAM45-Fine・SAM45-Wide の .bit と PS のソフト（specd）を RFSoC 4x2 のボードに置き、起動できる状態にするまで。結線は [`wiring.md`](wiring.md)、起動と命令は [`specd.md`](specd.md)。

## 要るもの

| | |
|---|---|
| ボード | AMD RFSoC 4x2（XCZU48DR-1） |
| SD カード | RFSoC-PYNQ v3.1.1（版の表は [`../knowledge/environment.md`](../knowledge/environment.md)） |
| bit | `.bit` と `.hwh`（同じ名前で同じ場所に置く）。リリースからは GitHub Releases、手元でビルドするなら `hw/bits/sam45-fine/` の `make`・`hw/bits/sam45-wide/` の `make IMPL=Performance_Explore` |
| PS のソフト | このリポジトリの `sw/pynq/` の全部（版のタグで固定する）。**Fine と Wide で同じ** |
| 較正 | `sw/pynq/timebase.py` の `CAL`（時刻）・`sw/pynq/tp_cal.json`（TP の dBm）。**どちらも bit の (BIT_KIND, BIT_REV) で引く** |

**PS は、時刻の式を直した版（commit c3c3ceb、PR #25）より後のものを使う。** 今の較正（形 (b)、`pps_det_ns` が 0 でない）を前の式で使うと、データの時刻が 143 ns ずれる。

## ボードのディレクトリ

bit の版ごとに 1 つのディレクトリにまとめる（前の版と混ぜない）。Fine と Wide を 1 つの specd で `LOAD` で切り替えるなら、同じディレクトリに両方の bit を置く（PS は同じ）。

```
~/sam45-fine-<版>/
  proj021.bit  proj021.hwh          # bit（名前は bits.json で指す）
  specd.py  s45acq.py  timebase.py … # sw/pynq/ の全部
  tp_cal.json
  bits.json                          # このボードで LOAD を許す bit の一覧
```

```bash
# 制御 PC から（<board> はボードの宛先）
ssh xilinx@<board> mkdir -p sam45-fine-<版>
scp <bit>.bit <bit>.hwh xilinx@<board>:sam45-fine-<版>/
scp sw/pynq/*.py sw/pynq/tp_cal.json xilinx@<board>:sam45-fine-<版>/
```

## bits.json

specd が `LOAD` で切り替えてよい bit の一覧。**ネットワークから任意のパスは受けない**（[`../spec/interface.md`](../spec/interface.md) の 5.）。例は `sw/pynq/bits.example.json`。

```json
{
  "default": "sam45-fine",
  "bits": {
    "sam45-fine": {"bit": "proj021.bit", "pydir": ".", "tp_cal": "tp_cal.json",
                   "sha256": "<sha256sum proj021.bit の値>"},
    "sam45-wide": {"bit": "proj023.bit", "pydir": ".", "kind": "wide", "tp_cal": "tp_cal.json",
                   "sha256": "<sha256sum proj023.bit の値>"}
  }
}
```

- `sha256` を書くと、specd は起こすときと `LOAD` のときに照らし、違えば載せない
- **SAM45-Wide には `"kind": "wide"` が要る**（SLICE の流れの取得になる。無い項目は Fine の窓の取得で起こす）。specd に `--wide` は付けない
- 比べの相手（別の bit）を足すときは、`pydir` にその bit の PS の置き場所を書く（PS は bit ごとに違いうる）

## 置いたら確かめる

```bash
cd ~/sam45-fine-<版>
sha256sum proj021.bit                         # リリースの SHA256SUMS・bits.json と同じ
python3 bitinfo.py proj021.bit                # USR_ACCESS = ビルドした commit（汚れの印が無いこと）
python3 test_cal_b.py                         # 時刻の式の試験（PL なし）。「結果: 全部通過」
```

実機の短い確かめは判定の ID-1（自己記述）と F-0（1PPS）: [`../../test/acceptance/sam45-fine/`](../../test/acceptance/sam45-fine/)。SAM45-Wide は ID-1（`wide.py --list`）と、specd の `ID`（`win_id=02020000` = SLICE・usr。`kind: wide` は ID ではなく START の EVENT の ids に出る）・`STATUS` の `time_ok=1`: [`../../test/acceptance/sam45-wide/`](../../test/acceptance/sam45-wide/)。
