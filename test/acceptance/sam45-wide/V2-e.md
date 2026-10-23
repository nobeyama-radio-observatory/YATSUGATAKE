# V2-e — TP のレコード = AXI4-Lite の TP のリング

- **前提**: 共通の前提。ボード直（root、specd を止めてから）。配線 N
- **手順**:

```bash
sudo -E $(which python3) wide_v2.py --clkin 0 --ref 10 --v2e
```

- **合格**（測る前に決めた条件）:
  - 4 ADC とも TP のレコードの個と AXI4-Lite の TP のリングの個が bit 単位で一致（不一致 0）
  - SEQ の飛び 0・DUMP_T = ANCH_T ＋ (DUMP_F0 − ANCH_F)·512 の外れ 0・CRC 0・DROP_CNT 0
- **陽性対照**: なし（TP の作りは Fine の V2-e と同じ。core_cmn は win_core の TP を番地・意味を変えずに写した）
- **記録**: proj023 手順 4c（2026-10-17、ビルド 11）: 4 ADC とも TP のレコード 304 個、照らした 509〜511 個で不一致 0・SEQ の飛び 0・DUMP_T の式の外れ 0・CRC 0
