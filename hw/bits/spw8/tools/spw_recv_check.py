#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""SpW8 M5b: specd（--spw）から受けた記録（specrecv --out の .s45）を論理の窓の番号で照らす（判定 H-0・W-1・TW の specd の版）。PL もボードも要らない

    python3 spw_recv_check.py runs/m5b/w1_0.s45 --win 3900:128,3890:64,... --alt 2,1 --tone 3891.125
    python3 spw_recv_check.py runs/m5b/tw.s45 --win ... --alt 2,1 --twin 2,1
    陽性対照: --posctl-pred 1（予言の ch を 1 ずらす → CW の照らしが落ちる）

予言はこの道具が spwplan で自分で計画して出す（specd の計画・START の EVENT は見ない）。窓の番号 i は利用者の並び（= 記録の s の欄、ADR 0028）。
照らすもの:
  - 記録: kind 3・bit_kind 7・fmt f32・nch 4096・src = core・NS と if_mhz が計画の窓 i と同じ・4 ADC × 窓の数だけの (core, s)・TP の dBFS
  - --tone F: F を含む窓（ピーク / 中央値 ≧ 20 dB）の最大の ch（FFT の ch の順、ch 0 = 窓の中心）が予言の ch とずれ 0（spw_b5.py --tone と同じ）
  - --twin i,j: 双子の比（fftshift の中央 14/16、中心の 5 ch を除く）の中央値 1 ± 0.001・比の相対の揺れ ≦ 独立な雑音 √(2/N) の 1/4（N = 束ねたダンプの数。spw_b5.py と同じ）。TP が --tp-min 以上の ADC だけ合否に
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "sw", "pynq"))
import s45proto as P   # noqa: E402
import spwplan         # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--win", required=True, help="窓の組 IF:幅,IF:幅,...（4 ADC に同じ組）")
    ap.add_argument("--alt", default=None, help="i,j: 窓 i を 2 番目に近い粗い ch で、窓 j を近い ch で計画する（SET の Ai.coarse=alt Aj.coarse=near と同じ）")
    ap.add_argument("--tone", type=float, default=None)
    ap.add_argument("--twin", default=None, help="i,j: 双子の比を照らす窓")
    ap.add_argument("--tp-min", type=float, default=-40.0)
    ap.add_argument("--posctl-pred", type=int, default=0, help="陽性対照: 予言の ch をこの数だけずらす")
    ap.add_argument("--out", default=None, help="要約の .json")
    a = ap.parse_args()
    req = [tuple(float(v) for v in x.split(":")) for x in a.win.split(",")]
    fk = {}
    if a.alt:
        i, j = (int(v) for v in a.alt.split(","))
        fk = {i: "alt", j: "near"}
    plan = spwplan.plan(req, H=8, E=3, S=8, ddr=False, force_k=fk)
    wins = {x["i"]: x for x in plan["wins"]}
    bad = []
    acc, cnt, ndump, tps = {}, {}, {}, {}
    f = open(a.file, "rb").read()
    o = 0
    while o < len(f):
        rt, pl, crc, seq = P.parse_header(f[o:o + 24])
        ver = P.header_ver(f[o:o + 24])
        d = P.decode(rt, f[o + 24:o + 24 + pl], ver)
        o += 24 + pl
        if rt == P.T_TP and len(d["e"]):
            e = d["e"]
            t = tps.setdefault(d["adc"], [0, 0])
            t[0] += int(e["sum"].astype(np.float64).sum()); t[1] += int(e["nfr"].sum())
            continue
        if rt != P.T_SPEC:
            continue
        key = (d["core"], d["s"])
        x = wins.get(d["s"])
        if (x is None or d["kind"] != 3 or d["bit_kind"] != 7 or d["fmt"] != P.FMT_F32 or d["nch"] != 4096 or d["src"] != d["core"]
                or d["ns"] != x["ns"] or abs(d["if_mhz"] - x["if_mhz"]) > 1e-9):
            if len(bad) < 10:
                bad.append(f"記録の頭（core {d['core']} s {d['s']}: kind {d['kind']}・NS {d['ns']}・IF {d['if_mhz']}）が計画と違う")
            continue
        fft = np.empty(4096)
        fft[P.IF_ORDER] = d["data"].astype(np.float64)      # IF の昇順 → FFT の ch の順（ch b = IF_ORDER[i]）
        acc[key] = acc.get(key, 0) + fft
        cnt[key] = cnt.get(key, 0) + 1
        ndump[key] = ndump.get(key, 0) + d["n_sum"]
    want = {(c, i) for c in range(4) for i in wins}
    if set(acc) != want:
        bad.append(f"(core, s) の組が計画と違う（無い {sorted(want - set(acc))[:6]}・余分 {sorted(set(acc) - want)[:6]}）")
    tp_dbfs = {c: float(10 * np.log10(v[0] / (v[1] * 8192) / (8192 ** 2 / 2))) for c, v in tps.items() if v[1]}
    print("TP: " + "・".join(f"{'ABCD'[c]} {v:.2f} dBFS" for c, v in sorted(tp_dbfs.items())))
    print(f"記録: (core, s) {len(acc)} 組・束 {min(cnt.values()) if cnt else 0}〜{max(cnt.values()) if cnt else 0} 個")
    summ = dict(file=os.path.basename(a.file), tp_dbfs=tp_dbfs, n=min(cnt.values()) if cnt else 0, tone={}, twin={})
    if a.tone is not None:
        judged = 0
        for c in range(4):
            for i, x in sorted(wins.items()):
                pr = spwplan.ch_of(a.tone, x)
                if pr is None or (c, i) not in acc:
                    continue
                m = acc[(c, i)] / cnt[(c, i)]
                med = float(np.median(m))
                pk = float(m.max() / med) if med > 0 else 0.0
                am = int(m.argmax())
                pch = (pr[0] + a.posctl_pred) % 4096
                hit = pk >= 100
                judged += hit
                summ["tone"][f"{'ABCD'[c]}{i}"] = dict(pred=pch, argmax=am, pk_db=round(10 * np.log10(pk), 1) if pk > 0 else None, judged=hit)
                print(f"CW IF {a.tone}: {'ABCD'[c]}{i}（s {x['s']}・k {x['k']}{'*' if x['alt'] else ''}・{x['w']:g} MHz）予言 ch {pch}・最大の ch {am}・"
                      f"ピーク / 中央値 {10 * np.log10(pk):.1f} dB" + ("" if hit else "（20 dB 未満、合否にしない）"))
                if hit and am != pch:
                    bad.append(f"CW の ch（{'ABCD'[c]}{i}: {am} ≠ {pch}）")
        if not judged:
            bad.append("CW が立った窓が無い")
        summ["tone_judged"] = judged
    if a.twin:
        wi, wj = (int(v) for v in a.twin.split(","))
        for c in range(4):
            kd, kc = (c, wi), (c, wj)
            if kd not in acc or kc not in acc:
                bad.append(f"{'ABCD'[c]} の双子 {wi}↔{wj} の記録が無い")
                continue
            md, mc = np.fft.fftshift(acc[kd] / cnt[kd]), np.fft.fftshift(acc[kc] / cnt[kc])
            jj = np.arange(256, 4096 - 256)
            jj = jj[np.abs(jj - 2048) > 2]
            r = md[jj] / mc[jj]
            nn = min(ndump[kd], ndump[kc])
            tw = dict(ratio_median=float(np.median(r)), ratio_rel_std=float(np.std(r) / np.mean(r)), indep=float(np.sqrt(2.0 / nn)),
                      corr=float(np.corrcoef(md[jj], mc[jj])[0, 1]), ndump=nn)
            tw["judged"] = tp_dbfs.get(c) is not None and tp_dbfs[c] >= a.tp_min
            summ["twin"]["ABCD"[c]] = tw
            print(f"{'ABCD'[c]} の双子 {wi} ↔ {wj}: 比の中央値 {tw['ratio_median']:.5f}・比の相対の揺れ {tw['ratio_rel_std']:.4f}"
                  f"（独立な雑音なら ≒ {tw['indep']:.4f}、線 {0.25 * tw['indep']:.4f}）・形の相関 {tw['corr']:.5f}・ダンプ {nn}"
                  + ("" if tw["judged"] else "（TP が低いので合否にしない）"))
            if tw["judged"] and (tw["ratio_rel_std"] > 0.25 * tw["indep"] or abs(tw["ratio_median"] - 1) > 1e-3):
                bad.append(f"{'ABCD'[c]} の双子 {wi}↔{wj} が合わない")
    summ["bad"] = bad
    if a.out:
        json.dump(summ, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("結果: " + ("全部通過" if not bad else "不合格: " + "・".join(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
