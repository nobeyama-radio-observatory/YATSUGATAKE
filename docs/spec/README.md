# spec — 仕様の正典

**状態: 正典**（2026-10-21、[ADR 0021](../decisions/0021-spec-canonical-in-yatsugatake.md)）。**全 bit の仕様の正はここ**。
study-rfsoc の `INTERFACE.md`・`BITS.md` はここを指す。study-rfsoc の試行は YATSUGATAKE の版を出発点にし、仕様の変更の案は試行の README に書いて、採用するときにここへ PR で入れる。

| ファイル | 中身 | 状態 |
|---|---|---|
| [`interface.md`](interface.md) | PL ↔ PS ↔ 制御 PC の約束（インターフェース v2: 制御・流れと自己記述・番地・リング・specd の命令・s45proto・未決事項）と、決めた理由 | 2026-10-21 に study-rfsoc の `INTERFACE.md`（6b777bf）から写した。節の番号はそのまま |
| [`bits.md`](bits.md) | 9 本の bit の仕様（ADC・窓・帯域・点数・dt）・時刻の格子を決めた理由・全 bit 共通の要求 | 同じく `BITS.md` から |
| [`timing.md`](timing.md) | 時刻の物差し（ビート・格子・BASE・TP の区切り・錨と UTC の式・D_eff・較正の定数の値） | 2026-10-21 に interface.md・bits.md・`timebase.py` から分けた |
| [`units.md`](units.md) | 強度の単位（abs の式）・dBFS・TP の dBm（ボードの `tp_cal.json`） | 同じく proj019 から |
| [`hardware.md`](hardware.md) | ボード・版・SMA とタイルの対応・入力・クロックと 1PPS・入口の LPF | 同じく study-rfsoc の `VERSIONS.md` と `knowledge/hardware.md` から |

**値は timing・units・hardware が正、決めた理由は interface・bits に残す**（interface・bits の節の番号は study-rfsoc から指されているので動かさない）。食い違ったら値の側を直し、理由の側からそちらを指す。

仕様の行には、根拠になった決定（`decisions/` の ADR 番号）を添える。
