# spec — 仕様の正典

**状態: 移植待ち。** proj021 が完成するまでは、仕様の正は study-rfsoc の根元のファイルにある。
ここへ写すのは移植のとき（[`../migration.md`](../migration.md)）。**それまでここに仕様を書かない**（正が 2 つになると必ずずれる）。

| ここに置くもの（予定） | 移植元（study-rfsoc） | 中身 |
|---|---|---|
| `bits.md` | `BITS.md` | 9 本の bit の仕様（ADC・窓・帯域・点数・dt）・時刻の格子・全 bit 共通の要求 |
| `interface.md` | `INTERFACE.md`（v2） | PL ↔ PS ↔ 制御 PC の約束（制御・流れと自己記述・番地・リング・specd の命令・s45proto） |
| `timing.md` | `BITS.md`・proj016・proj017 | 時刻の物差し（ビート・1PPS・START_AT・DUMP_T・遅れの定数） |
| `units.md` | proj019 | 強度の単位（abs の式）・TP の dBm |
| `hardware.md` | `VERSIONS.md` | ボード・版・SMA とタイルの対応・クロックの構成 |

仕様の行には、根拠になった決定（`decisions/` の ADR 番号）を添える。
