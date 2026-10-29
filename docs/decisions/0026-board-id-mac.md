# 0026. ボードの印は eth0 の MAC にする（eFuse の DNA は読めない）

- 状態: 採用
- 決定日: 2026-10-29
- 根拠: [ADR 0023](0023-time-calibration-per-board.md)・[ADR 0025](0025-tp-calibration-per-board.md)、開発のボード（RFSoC-PYNQ v3.1.1）での実測（2026-10-29）

## 背景

ADR 0023 は、較正ファイルの鍵のボードの印を「eFuse の DNA、読めなければ eth0 の MAC」とした。DNA が読めるかは実機で確かめていなかった。

開発のボードで確かめたこと（root で）:

- `/sys/bus/nvmem/devices/zynqmp-nvmem0/nvmem` は、頭の 4 バイト（SoC の版）しか読めない。eFuse の範囲（0x0C〜）は `EOPNOTSUPP`（PMU のファームウェアが応じない）
- eFuse の制御器を `/dev/mem` で読むと Bus error（PS の保護で止まる）
- eth0 の MAC は `addr_assign_type` 0（固定のアドレス）。上位 3 バイトはボードの EEPROM の製造元の番号で、再起動の前後で同じ。root でなくても読める

## 決定

- **ボードの印は eth0 の MAC だけにする**（`timebase.board_id()` → `mac:<アドレス>`）。DNA は読みにいかない
- eth0 が読めなければ印は無し（今までどおり、時刻は暫定・TP の dBm は出さない。`timecal.py` は書かない）

## 理由

- DNA は今の SD カードでは読めず、いつも MAC に落ちていた。読みにいく道を残すと、SD カードの版を上げて DNA が読めるようになったときに印が黙って変わり、そのボードで測った較正ファイルが当たらなくなる
- MAC はボードの EEPROM の固定の値で、ボードに付いて回る。root でなくても同じ値になる（specd と、制御 PC から `ID` で読む道具とで食い違わない）

## 見送った案

- **DNA を先に、読めなければ MAC（ADR 0023 の形）**: 上の理由で、版の更新で印が変わる
- **PL に DNA_PORTE2 を入れて読む**: bit ごとに RTL が要る。較正は bit によらないボードの値なので、PL に置く筋ではない

## 影響

- `timebase.board_id()` は `mac:…` だけを返す。ADR 0023・0025 の較正ファイルの鍵の形は変わらない（`board.id` の文字列）
- **SD カードを替えずに eth0 のアドレスを設定で替えると、印が変わる**（そのときは測り直すか、ファイルの `board.id` を直す）
