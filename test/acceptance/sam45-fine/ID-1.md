# ID-1 — 自己記述（IF_ID・流れの表・番地）

- **前提**: 共通の前提。ボード直（root、specd を止めてから）。配線はどれでも
- **手順**:

```bash
python3 s45core.py --list --clkin 0 --ref 10
```

- **合格**（測る前に決めた条件）:
  - 4 コアとも IF_ID 0x0202_0301、time_core 0x0202_0302、リング 0x0202_0303
  - コア 0 の流れ 2 が RAW（KIND 4）: SID 0x0204_0200・NCH 0・FRAME_BEATS 512・PARAM 13。FULL（KIND 1）の流れは無い
  - 各コアの窓の流れ 2 本（DDC、KIND 2）、番地の幅 64 KiB（.hwh）
- **陽性対照**: なし
- **記録**: **YATSUGATAKE M6 で通過（2026-10-17、M5b の bit `ed6bcf78…`・usr 8eba3480、`~/m2/m6_board/id1.txt`）**: 4 コア 0x0202_0301・time_core 0x0202_0302・RAW の流れの行は移植元と同じ。 proj021 README「手順 2-5 → 実機（S25-3）」の `s45core --list` の行（2026-10-14 通過）
