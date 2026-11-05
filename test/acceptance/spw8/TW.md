# TW — 2 番目に近い粗い ch の窓と、近い ch の窓の双子

- **前提**: 共通の前提。配線 N。窓の組 plan2（窓 2 = 2 番目に近い粗い ch、窓 1 = 同じ IF・幅で近い ch）
- **手順**:

```bash
# M4
sudo -E $(which python3) spw_b5.py --clkin 0 --ref 10 --win 3900:128,3890:64,3890:64,3892:16,3891:8,3300:128,3290:32,2650:128 --alt 2,1 --ng 10 --sec 10 --out runs/tw
# M5b の後（specd --spw --fast --fast-ring）: 決め打つ口 coarse で同じ組を SET、ノイズだけで 250 束
python3 specctl.py --host $B "SET tint=0.04096 A2.coarse=alt B2.coarse=alt C2.coarse=alt D2.coarse=alt A1.coarse=near B1.coarse=near C1.coarse=near D1.coarse=near" "CLEAR" "START n=250" "SEND ON"
python3 specrecv.py --host $B --report 0 --seconds 14 --out runs/tw.s45
python3 hw/bits/spw8/tools/spw_recv_check.py runs/tw.s45 --win 3900:128,3890:64,3890:64,3892:16,3891:8,3300:128,3290:32,2650:128 --alt 2,1 --twin 2,1
```

- **合格**: 4 コアとも、双子の比（ch ごと、fftshift の中央 14/16）の中央値が 1 ± 0.001、**比の揺れ ≦ 独立な雑音の 1/4**（P-10b の 2 回目で 0.016）。TP が `--tp-min` 以上のコアだけを合否に
- **陽性対照**: 計画の R0 を 512 にする（P-10b の 1 回目の誤り）と、双子の形が合わない（相関 ≒ 0、比の揺れ ≫ 線）
- **記録**: proj032 P-10b（2026-11-02、`runs/p10_plan2`）: 比の中央値 0.99996〜1.00004・比の揺れ 0.011、4 コアとも通過。1 回目（`runs/p10_plan1`、R0 512）は相関 −0.004・比の揺れ 41 で落ちた
- **記録（specd、M5b）**: YATSUGATAKE M5b（2026-11-04、`hw/bits/spw8/runs/m5b/tw`）: 4 ADC とも比の中央値 1.00003〜1.00004・比の揺れ 0.0016（線 0.0112、束ねたダンプ 1000 で独立な雑音 0.0447）・相関 0.99998、通過。陽性対照（spwplan の R0 を 512 にした specd を別の場所で起こした）は比の中央値 1.34〜1.40・揺れ 0.45・相関 −0.86〜−0.91 で落ちた
- **記録（M6）**: YATSUGATAKE M6（2026-11-04 06:55 UTC、M5c の bit、specd、`runs/m6/tw`）: 4 ADC とも比の中央値 1.00003〜1.00004・比の揺れ 0.0016（線 0.0112）・相関 0.99998〜0.99999。陽性対照（spwplan の R0 512 の specd、07:29 UTC）は比の中央値 1.35〜1.41・揺れ 0.45〜0.47・相関 −0.84〜−0.90 で落ちた。**通過**
