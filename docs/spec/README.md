# spec — 仕様の正典

**状態: 正典**（2026-10-21、[ADR 0021](../decisions/0021-spec-canonical-in-yatsugatake.md)）。**全 bit の仕様の正はここ**。
study-rfsoc の `INTERFACE.md`・`BITS.md` はここを指す。study-rfsoc の試行は YATSUGATAKE の版を出発点にし、仕様の変更の案は試行の README に書いて、採用するときにここへ PR で入れる。

| ファイル | 中身 | 状態 |
|---|---|---|
| [`interface.md`](interface.md) | PL ↔ PS ↔ 制御 PC の約束（インターフェース v2: 制御・流れと自己記述・番地・リング・specd の命令・s45proto・未決事項） | 2026-10-21 に study-rfsoc の `INTERFACE.md`（6b777bf）から写した。節の番号はそのまま |
| [`bits.md`](bits.md) | 9 本の bit の仕様（ADC・窓・帯域・点数・dt）・時刻の格子・全 bit 共通の要求 | 同じく `BITS.md` から |

以下は分ける予定（今は `interface.md`・`bits.md` の中にある）:

| ここに置くもの（予定） | 移植元（study-rfsoc） | 中身 |
|---|---|---|
| `timing.md` | `BITS.md`・proj016・proj017 | 時刻の物差し（ビート・1PPS・START_AT・DUMP_T・遅れの定数） |
| `units.md` | proj019 | 強度の単位（abs の式）・TP の dBm |
| `hardware.md` | `VERSIONS.md` | ボード・版・SMA とタイルの対応・クロックの構成 |

仕様の行には、根拠になった決定（`decisions/` の ADR 番号）を添える。
