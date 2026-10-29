# CU — 係数 URAM の見張り

- **前提**: 共通の前提。specd が Overlay を載せた後、別の process（root・pynq-venv）で `cuctl.py`（bit と係数の hex と同じディレクトリ）
- **手順**（proj031 R-2 の (i)〜(iv)）:

```bash
python3 specctl.py --host $B "SET A0.src=A B0.src=B C0.src=C D0.src=D shift=7 tint=0.02048 fmt=f32" "START n=0"
python3 specrecv.py --host $B --out cu1.s45 --seconds 30 &      # 10 s 後に、ボードで:
sudo -E $(which python3) cuctl.py drop                            # (i) 中身は正しいまま OK だけを落とす
python3 specctl.py --host $B STOP "START n=10"                    # (ii) 断られるはず
sudo -E $(which python3) cuctl.py corrupt --row 1234 --bit 5      # (iii)
python3 specctl.py --host $B "START n=10"                         # 断られるはず
sudo -E $(which python3) cuctl.py load                            # (iv) 正しく書き直す
python3 specctl.py --host $B CLEAR "START n=50"; python3 specrecv.py --host $B --out cu4.s45 --seconds 5
python3 g24cw.py cu4.s45 --src ABCD
```

- **合格**:
  - (i) STAT 0x15 → 0x14。**4 窓とも同じダンプから flags の bit 0 が立ち、STOP までずっと 1**。ほかの bit 0・miss 0
  - (ii) `ERR FAIL CuError: 係数 URAM の OK が 0`、IDLE のまま
  - (iii) STAT 0x1c・CRC 0x8d342791、START はまた断られる
  - (iv) load 0.6〜1.0 s で STAT 0x15、START の後 4 窓 × 50・照合 通過・`g24cw` 全部通過・**flags の OR は 4 窓とも 0**（specd を起こし直さずに）
- **陽性対照**: (i)〜(iii) がそれ自体の陽性対照（見張りが立つべきときに立つ）。sim では cuclrno（OK が 0 のまま消すとまた立つ）
- **記録**: proj031 rev 2（2026-10-27 15:18〜15:27 UTC）: 全部予言どおり（(i) ダンプ 239 から bit 0、(iv) flags 0）。**YATSUGATAKE M5**（2026-10-29 00:59〜01:00 UTC、bit `e3521f51…`・一本化した `sw/pynq/`、配線 P）: 全部予言どおり。(i) STAT 0x15 → 0x14・NROW 4096 → 4097、4 窓とも K 727 から bit 0・記録の終わりまで 1・ほかの bit・health・欠け 0。(ii) `ERR FAIL CuError: 係数 URAM の OK が 0（STAT 0x14）`・GET は SET のまま。(iii) STAT 0x1c・CRC 0x8d342791・START は断られた。(iv) load 0.73 s で STAT 0x15、4 窓 × 50・照合 通過・`g24cw` 全部通過・flags の OR 4 窓とも 0。STATUS miss・pl_drop・pl_crc・pl_err 0・time_ok 1、AXI_MAX_PIPELINE 後 0x0102。**手順の注意**: (i) の受けは 30 s で切れ、STOP までの記録が溜まりに残る。(iv) の START の前に **`CLEAR`** を打つ（打たずに取った 1 回目は 222 個が混ざり g24cw が落ちた）
