# WRST — 約束を破る窓の組を断る

- **前提**: 共通の前提。配線はどれでも
- **手順**:

```bash
# M4（PL の WRST の約束を、spwplan の check() と照らす）
sudo -E $(which python3) spw_b5.py --clkin 0 --ref 10 --win 3900:128,3890:64,3890:64,3892:16,3891:8,3300:128,3290:32,2650:128 --alt 2,1 --wrst-test --ng 10 --sec 10 --out runs/wrst
# M5b の後: 計画できない組を SET して ERR、直後の GET・STATUS の spw_map が変わらない。その後の START の WRST が通り、記録が照らしを通る
python3 specctl.py --host $B "GET" "STATUS" > before.txt
python3 specctl.py --host $B "SET B1.bw=128 B3.bw=128 B4.bw=128 B6.bw=128" "SET A0.coarse=alt" "GET" "STATUS"
python3 specctl.py --host $B "CLEAR" "START n=50" "SEND ON"; python3 specrecv.py --host $B --report 0 --seconds 6 --out runs/wrst.s45
```

- **合格**:
  - M4: コア 0 に約束 [1]〜[6] を 1 つずつ破る設定を書いて WRST、**PL の WRST_BAD が check() と 6 つとも同じ**・CORE_FLAGS[0] が立つ・WRST_CNT は増えない。破らない設定は通る（WRST_CNT ＋1）
  - M5b の後: 計画できない組は **組ごと ERR**（理由つき）で、効いている窓の組・レコードは変わらない。PL に約束を破る設定が届かない（WRST_BAD 0・CORE_FLAGS[0] 0）
  - WRST_T に 1〜7 を書くと 8 クロックに切り上がる（interface の WRST_T、S の PR）。WRST_T は PS が書かないので、M4 で一度だけ書いて WRST が通ることを見る
- **陽性対照**: 破らない設定が通ること（上）。机の上では `tools/test_spwplan.py` の陽性対照 3 つ（R0 512・機関を全部 lane 0・2 番目に近い ch を使わない）が落ちる
- **記録**: proj032 P-10b（2026-11-02、b5 rev 10）: 6 つとも同じ印・CORE_FLAGS[0]・WRST_CNT 増えず、破らない設定は通った
- **記録（specd、M5b）**: YATSUGATAKE M5b（2026-11-04）: 計画できない組 3 つ（ADC_B の偶奇の組の頭が埋まる・ADC_B の 128 MHz の窓の alt・ADC_A の 128 MHz の alt）とも ERR で理由つき、GET と spw_map は元のまま。次の START は WRST を通り（specd が CORE_FLAGS[0] 0・WRST_CNT ＋1・WCUR の読み返しを見る）、記録は `spw_recv_check.py` で全部通過。PL なしでは `test_fake.sh spwp`
