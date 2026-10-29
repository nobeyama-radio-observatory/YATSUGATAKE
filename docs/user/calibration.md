# 時刻の較正（ボードごと、設置の後に 1 回）

データの時刻（`utc_ns`）を、ボードの個体と設置（1PPS の入口の LPF・ケーブル）に合わせる。測った値は**ボードにだけ置き、リポジトリには戻さない**（[ADR 0023](../decisions/0023-time-calibration-per-board.md)）。
測っていないボードは開発の値（暫定）で動く。誤差は数 ns で要求の 100 µs には効かないが、`ID` の `tcal=provisional` で分かる。

## いつ測るか

- ボードを設置したとき（本番に入れる前）
- ボードを替えたとき、1PPS の入口の LPF・ケーブル・分配器を替えたとき
- PS を更新して、bit の ADC → コアの道の番号（`timebase.ADC_PATH`）が変わったとき（`GET CAL` の `tcal` が `provisional` に戻る）

## 要るもの

- SAM45-Wide の bit（`proj023.bit`・`.hwh`）と `sw/pynq/` の全部（[`install.md`](install.md)）
- 1PPS の分配器（5 分配以上）と、分配器から ADC_A〜D までの**同じ長さ**のケーブル 4 本（ケーブルの差は較正にそのまま入る）

## 配線 P

1PPS（45m の +2.5 V / 100 µs）を分配器で分け、**PPS Clk（入口の LPF の手前）と ADC_A〜D** に入れる。10 MHz はいつもどおり CLK_IN へ。
IF はすべて外す。**測り終えたら ADC から 1PPS を外し、IF に戻す**（1PPS を ADC に常時入れない。[`wiring.md`](wiring.md)）。

## 測る

ボードで、specd を止めてから（root）:

```bash
cd ~/sam45-<版>
sudo -E $(which python3) timecal.py --clkin 0 --ref 10
```

- Overlay を 5 回載せ直し、ADC ごとに 1PPS の縁を 5 試行ずつ測る（数分）。記録は `timecal-<日時>/`
- 通れば `/etc/yatsugatake/time_cal.json` を書く。前のファイルは `time_cal.json.<日時>` に残る
- 置き場所を替えるなら `--write <パス>` と、specd を起こすときの環境変数 `YATSUGATAKE_TIME_CAL=<パス>`
- 通らない（`結果: 失敗`）ときはファイルを書かない。よくある原因: 1PPS が ADC に入っていない（縁が見えない）、specd が動いている、Overlay ごとのばらつきが 2 ビートを越えた（もう一度回す）

合格の線（道具が見る）: 各回で 4 ADC × 5 試行とも縁が見える（最大 / σ ≧ 20）・1 回の中の σ ≦ 0.4 ビート・縁の 2 フレーム前では見えない（陽性対照）。ADC ごとの回の間のばらつき ≦ 2 ビート。

## 確かめる

```bash
sudo -E $(which python3) timecal.py --show       # このボードの印と較正ファイルが合っているか
```

specd を起こし直し、制御 PC から `ID` に `tcal=board`、`GET CAL` に `tcal_file`・`tcal_date`・ADC ごとの `a2c_ns` が出ること。
`tcal=provisional` のままなら、specd のログの「時刻の較正は暫定」の行に理由が出る（別のボードのファイル・ボードの印が読めない・道の番号が違う）。

## 保管

`time_cal.json` はボードの個体の値。リポジトリには入れない（`.gitignore` 済み）。SD カードを作り直すと消えるので、ユーザーの手元に写しを持つ。
測りの記録（`timecal-<日時>/`）も同じ扱い。作り直しは `timecal.py --from timecal-<日時>/load*.f2.json`（測らない）。
