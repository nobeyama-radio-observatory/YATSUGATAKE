# 0025. TP の dBm の較正もボードごとに持ち、ボードにだけ置く（リポジトリの tp_cal.json をやめる）

- 状態: 採用
- 決定日: 2026-10-29
- 根拠: [ADR 0023](0023-time-calibration-per-board.md)、YATSUGATAKE の P-8（SAM45-Wide M6、2026-10-23）、study-rfsoc proj019

## 背景

TP の dBm の換算の係数 K（ADC の口の dBm = 10·log10(σ_x²) ＋ K）は、`sw/pynq/tp_cal.json` としてリポジトリにあった。鍵は bit の (BIT_KIND, BIT_REV) の一覧（`bits`）。
K は PM を ADC の口に付けて測った、**開発のボードの個体の値**。別のボードに置けば、そのボードの値ではないものが黙って当たる。
時刻の較正は [ADR 0023](0023-time-calibration-per-board.md) でボードごとにし、ボードにだけ置くことにした。

分かっていたこと: SAM45-Fine (2, 3) と SAM45-Wide (1, 1) の K は同じ（TP の作りが同じ。同じ日・同じ配線で dBFS − PM の差 0.03〜0.06 dB、P-8）。

## 決定

- **TP の較正ファイルはボードの `/etc/yatsugatake/tp_cal.json`（環境変数 `YATSUGATAKE_TP_CAL`）にだけ置き、リポジトリに戻さない。** `sw/pynq/tp_cal.json` は消し、`.gitignore` に入れる
- 鍵は**ボードの印**（`timebase.board_id()`、specd の `ID` の `board`）と **ADC の道**（`timebase.ADC_PATH`、時刻と同じ表）。bit の一覧（`bits`）では引かない
- 作るのは今までどおり `s45lin.py`（`make_cal`・`adc_port_cal`）。記録の specd の `ID` からボードの印を取って書く。別のボードのファイルは書き換えない
- 前の形のファイル（ボードの印の無い `bits` の形）は使わない。**そのボードで測ったものなら** `python3 s45cal.py adopt <前のファイル>` で、印と道を付けて置く（K は変えない）
- 当たらないとき（ファイルが無い・別のボード・道が違う）は、今までどおり TP の dBm を出さない（dBFS は出る）。理由は specd のログと `GET CAL` に出る

## 理由

- K はボードの個体の値で、bit の値ではない。ADR 0023 と同じ理由で、本番のボードではそのボードで測ったものだけを当てる
- 公開のリポジトリに個体の値を置かない
- bit の一覧で引くと、新しい bit のたびにファイルを書き直すことになる。TP の作りが同じ bit には同じ K が当たる（Fine と Wide で確かめた）ので、道で引く

## 見送った案

- **リポジトリの tp_cal.json を開発のボードの既定として残す**: 別のボードに黙って当たる。TP の dBm は科学の値には使わない（チョッパーホイールが較正する）ので、無ければ出さないほうが誤解が無い
- **時刻と同じく暫定の値で動かす**: 時刻は 0 にできない（ずれが ns で済む値を当てる）が、TP の dBm は無くても dBFS で運転できる

## 影響

- 開発のボードは、今までのファイルを一度 `adopt` する（値は git の履歴にもある）
- specd の `ID` に `board`（ボードの印）が出る
- **TP の作り（tp_core）や RFDC の設定を変えた bit は、`ADC_PATH` に新しい番号を足す**（時刻と同じ表。足せば時刻も TP も暫定・不使用になり、測り直しが要る）
- 2G の PS（`sw/pynq-2g/`）は M5 で一本化するまで今の形のまま
