# design — 設計の解説

bit の中身を、使う人・直す人が読める形で。約束の正は [`../spec/`](../spec/)、ここは「どう作ってあり、なぜその形か、どこを読めばよいか」。

| 文書 | 中身 |
|---|---|
| [`overview.md`](overview.md) | 全体の流れ（データ・時刻・クロックのドメイン・健全性） |
| [`cores.md`](cores.md) | `hw/common/` の共通のコアの案内（RTL の冒頭のコメントが正） |
| [`sam45-fine/`](sam45-fine/) | SAM45-Fine の組み立て・資源・タイミング・図 |
| [`sam45-wide/`](sam45-wide/) | SAM45-Wide の組み立て・資源・タイミング |

bit を足したら `<bit>/README.md` を置く。
