# 設置（ボードに SAM45-Fine・SAM45-Wide・2G-4・2G-1-Fast・2G-2 を置く）

SAM45-Fine・SAM45-Wide・2G-4・2G-1-Fast・2G-2 の .bit と PS のソフト（specd）を RFSoC 4x2 のボードに置き、起動できる状態にするまで。結線は [`wiring.md`](wiring.md)、起動と命令は [`specd.md`](specd.md)。

## 要るもの

| | |
|---|---|
| ボード | AMD RFSoC 4x2（XCZU48DR-1） |
| SD カード | RFSoC-PYNQ v3.1.1（版の表は [`../knowledge/environment.md`](../knowledge/environment.md)） |
| bit | `.bit` と `.hwh`（同じ名前で同じ場所に置く）。リリースからは GitHub Releases、手元でビルドするなら `hw/bits/sam45-fine/` の `make`・`hw/bits/sam45-wide/` の `make IMPL=Performance_Explore`・`hw/bits/2g-4/` の `make build`・`hw/bits/2g-1-fast/` の `make build IMPL=Performance_Explore`・`hw/bits/2g-2/` の `make build`。**2G-4 は bit の隣に係数の hex**（`g24_coef_lo.hex`・`g24_coef_hi.hex`、`hw/bits/2g-4/src/g24/` の 2 個。specd が起動のときに PL の係数 URAM に書く） |
| PS のソフト | このリポジトリの `sw/pynq/` の全部（版のタグで固定する）。**Fine・Wide・2G-4・2G-1-Fast・2G-2 で同じ**。2G-4・2G-1-Fast・2G-2 は `s45fast.c`・`build_fast.sh` も置き、ボードで `libs45fast.so` を作る（下の「ボードの準備（2G-4・2G-1-Fast・2G-2）」） |
| 較正 | 時刻: **設置の後にボードで測る**（`timecal.py`、[`calibration.md`](calibration.md)）。測るまでは `sw/pynq/timebase.py` の `CAL` が暫定で当たる。TP の dBm: ボードの `/etc/yatsugatake/tp_cal.json`（ボードごとに測る。無ければ dBm は出ない） |

**PS は、時刻の式を直した版（commit c3c3ceb、PR #25）より後のものを使う。** 今の較正（形 (b)、`pps_det_ns` が 0 でない）を前の式で使うと、データの時刻が 143 ns ずれる。

## ボードのディレクトリ

bit の版ごとに 1 つのディレクトリにまとめる（前の版と混ぜない）。Fine・Wide・2G-4・2G-1-Fast・2G-2 を 1 つの specd で `LOAD` で切り替えるなら、同じディレクトリに全部の bit を置く（PS は同じ。2G-4 は係数の hex も）。

```
~/sam45-fine-<版>/
  proj021.bit  proj021.hwh          # bit（名前は bits.json で指す）
  specd.py  s45acq.py  timebase.py … # sw/pynq/ の全部
  bits.json                          # このボードで LOAD を許す bit の一覧
```

```bash
# 制御 PC から（<board> はボードの宛先）
ssh xilinx@<board> mkdir -p sam45-fine-<版>
scp <bit>.bit <bit>.hwh xilinx@<board>:sam45-fine-<版>/
scp sw/pynq/*.py xilinx@<board>:sam45-fine-<版>/
scp sw/pynq/s45fast.c sw/pynq/build_fast.sh hw/bits/2g-4/src/g24/g24_coef_lo.hex hw/bits/2g-4/src/g24/g24_coef_hi.hex xilinx@<board>:sam45-fine-<版>/   # 2G-4（2G-1-Fast・2G-2 は s45fast.c・build_fast.sh だけ。係数は bit に焼いてある）
```

## bits.json

specd が `LOAD` で切り替えてよい bit の一覧。**ネットワークから任意のパスは受けない**（[`../spec/interface.md`](../spec/interface.md) の 5.）。例は `sw/pynq/bits.example.json`。

```json
{
  "default": "sam45-fine",
  "bits": {
    "sam45-fine": {"bit": "proj021.bit", "pydir": ".",
                   "sha256": "<sha256sum proj021.bit の値>"},
    "sam45-wide": {"bit": "proj023.bit", "pydir": ".", "kind": "wide",
                   "sha256": "<sha256sum proj023.bit の値>"},
    "2g-4":       {"bit": "proj031.bit", "pydir": ".", "kind": "g24",
                   "sha256": "<sha256sum proj031.bit の値>"},
    "2g-1-fast":  {"bit": "proj033.bit", "pydir": ".", "kind": "g21",
                   "sha256": "<sha256sum proj033.bit の値>"},
    "2g-2":       {"bit": "proj034.bit", "pydir": ".", "kind": "g22",
                   "sha256": "<sha256sum proj034.bit の値>"}
  }
}
```

- `sha256` を書くと、specd は起こすときと `LOAD` のときに照らし、違えば載せない
- **SAM45-Wide には `"kind": "wide"` が要る**（SLICE の流れの取得になる。無い項目は Fine の窓の取得で起こす）。specd に `--wide` は付けない
- **2G-4 には `"kind": "g24"` が要る**（FULL の流れ 4 本の取得。specd の `--g24` と同じ）。specd は `--fast --fast-ring` で起こす（[`specd.md`](specd.md)）
- **2G-1-Fast には `"kind": "g21"` が要る**（FULL の流れ 1 本の取得。specd の `--g21` と同じ）。specd は `--prefault --fast --fast-ring` で起こす。2G-4 と 2G-1-Fast を同じ specd で `LOAD` で切り替えてよい（どちらも `--fast --fast-ring`）
- **2G-2 には `"kind": "g22"` が要る**（FULL の流れ 2 本の取得。specd の `--g22` と同じ）。specd は `--prefault --fast --fast-ring` で起こす（**`--fast` なしでは tint 20.48 ms が回らない**: 1 周の p99 57 ms）。2G-4・2G-1-Fast と同じ specd で `LOAD` で切り替えてよい
- 比べの相手（別の bit）を足すときは、`pydir` にその bit の PS の置き場所を書く（PS は bit ごとに違いうる）

## ボードの準備（2G-4・2G-1-Fast・2G-2）

2G-4・2G-1-Fast・2G-2 は PL → PS が 102.4 MB/s で、次の 2 つが無いと tint 20.48 ms の取得が追いつかない。ボードに 1 回（2 は PS を置き直すたびに）。PS を置いた後、specd を起こす前に。

1. **GEM1 の AXI_MAX_PIPELINE（0xFF0C0054）を 0x0102 にする**（読みの要求 2 本）。起動時に書く systemd のユニットを入れて有効にする（ユニットと手順は study-rfsoc の `proj035/board/`・`proj001/docs/runbook.md` の 09）。送り出しの頭打ちも除く（194 → 348 Mbit/s）。**4 本以上（0x0104〜）にしない**: CPU の DDR の読みが遅れ、取得が追いつかない
2. **`libs45fast.so` をボードで作る**（`.so` はリポジトリに無い）。最後の行が `CRC: 命令`（ARMv8 の CRC 命令）であること。`CRC: 表` では作り直す

```bash
cd ~/sam45-fine-<版>
bash build_fast.sh                            # 最後の行「libs45fast.so: CRC: 命令」
```

## 置いたら確かめる

```bash
cd ~/sam45-fine-<版>
sha256sum proj021.bit                         # リリースの SHA256SUMS・bits.json と同じ
python3 bitinfo.py proj021.bit                # USR_ACCESS = ビルドした commit（汚れの印が無いこと）
python3 test_cal_b.py                         # 時刻の式の試験（PL なし）。「結果: 全部通過」
python3 test_timecal.py                       # 時刻の較正ファイルの試験（PL なし）。「結果: 全部通過」
python3 test_tpcal.py                         # TP の較正ファイルの試験（PL なし）。「結果: 全部通過」
```

実機の短い確かめは判定の ID-1（自己記述）と F-0（1PPS）: [`../../test/acceptance/sam45-fine/`](../../test/acceptance/sam45-fine/)。SAM45-Wide は ID-1（`wide.py --list`）と、specd の `ID`（`win_id=02020000` = SLICE・usr。`kind: wide` は ID ではなく START の EVENT の ids に出る）・`STATUS` の `time_ok=1`: [`../../test/acceptance/sam45-wide/`](../../test/acceptance/sam45-wide/)。2G-4 は ID-1: specd のログの「係数 URAM」の行が VERIFY 通過（CRC 0x891be197）、`ID` の `adc_id=02030101`・usr（`kind: g24` は START の EVENT の ids）・`STATUS` の `time_ok=1`、AXI_MAX_PIPELINE 0x0102・「CRC: 命令」: [`../../test/acceptance/2g-4/`](../../test/acceptance/2g-4/)。2G-1-Fast は ID-1: `ID` の `adc_id=020b0101`・usr（`kind: g21` と `proj 00330100` は START の EVENT の ids・specd のログ）・`STATUS` の `time_ok=1`、AXI_MAX_PIPELINE 0x0102・「CRC: 命令」: [`../../test/acceptance/2g-1-fast/`](../../test/acceptance/2g-1-fast/)。2G-2 は ID-1: `ID` の `adc_id=020a0101`・usr（`kind: g22` と `proj 00340100` は START の EVENT の ids・specd のログ）・`STATUS` の `time_ok=1`、AXI_MAX_PIPELINE 0x0102・「CRC: 命令」: [`../../test/acceptance/2g-2/`](../../test/acceptance/2g-2/)。

置いたら、本番に入れる前に**時刻の較正**を測る: [`calibration.md`](calibration.md)。
