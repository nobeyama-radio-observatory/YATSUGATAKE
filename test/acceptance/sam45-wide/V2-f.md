# V2-f — 5.1 の見張り: r = DUMP_T − m·BASE = 2·G が、RUN と Overlay をまたいで一定

Wide の r は D-2（フレームの頭を T の格子に置く）で式から決まる定数 2·G = 1,048,576。Fine の r（Overlay ごとの実測）と違う。

- **前提**: 共通の前提。ボード直（root、specd を止めてから）。配線 N
- **手順**:

```bash
sudo -E $(which python3) wide_v2.py --clkin 0 --ref 10 --v2f --runs 2 --seconds 10 --posctl
for i in 1 2 3; do sudo -E $(which python3) wide_v2.py --clkin 0 --ref 10 --v2f; done      # Overlay をまたぐ
```

- **合格**（測る前に決めた条件）:
  - 7 本（既定: A B 1・B B 2・C B 4・D B 1）の全部の流れ・全部の RUN・4 回の Overlay で **r = 1,048,576**
  - RUN の中で m の飛び・SEQ の飛び・DUMP_T の式の外れ・F0 の飛び・FLAGS・SAT・CRC が 0
- **陽性対照**: `--posctl`: START_AT を格子 ＋ G にずらした RUN で r = 3·G になり、「RUN の間で同じ」の比べが違うと言う
- **記録**: proj023 手順 4c（2026-10-17、ビルド 11）: 全部の流れ・全部の RUN で r = 2·G、陽性対照は 7 本とも 3·G。Overlay 4 回とも r = 2·G・IP の位相 入口 8・出口 155
