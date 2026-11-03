#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""SpW8 sim-dly の照らし — tb_spwdelay の 3 本（そのまま・入口に 1 段・64 段）の check_spwdelay.py の出力を比べる

    python3 tools/dly_cmp.py BASE.log P1.log P64.log

check_spwdelay.py の「NS ごと:」の行（NS ごとに窓の D の平均、小数 2 桁）を読む。判定:
  - 3 本とも「結果: 全部通過」
  - そのままの D(NS) が、ADR 0028・timing の表に入れる値（proj032 P-12）と小数 2 桁まで同じ: NS 1〜5 = 86.03・135.07・231.05・411.01・757.03
  - 1 段の陽性対照: どの窓も D がちょうど ＋1 動く（±0.06 = 標本の位置と位相の組み合わせで残る ±0.04（P-12）＋ 小数 2 桁の丸めの 2 本分）
  - 64 段の陽性対照: どの窓も D がちょうど ＋64.00 動く（系の周期が 64 ビートを割る）
"""
import re
import sys

WANT = {1: 86.03, 2: 135.07, 3: 231.05, 4: 411.01, 5: 757.03}


def read(path):
    txt = open(path).read()
    ok = "結果: 全部通過" in txt
    m = re.search(r"^NS ごと: (.*)$", txt, re.M)
    ns = {}
    if m:
        for part in m.group(1).split("・"):
            k, v = part.split(":")
            ns[int(k.split()[1])] = [float(x) for x in v.split(",")]
    return ok, ns


def main(base, p1, p64):
    bad = []
    runs = {"そのまま": read(base), "1 段": read(p1), "64 段": read(p64)}
    for name, (ok, ns) in runs.items():
        if not ok or not ns:
            bad.append(f"{name}: check_spwdelay が通過していない")
    if bad:
        return bad
    b = runs["そのまま"][1]
    for n, want in WANT.items():
        got = sorted(set(b.get(n, [])))
        print(f"NS {n}: D = {', '.join(f'{x:.2f}' for x in b.get(n, []))}（表の値 {want:.2f}）")
        if got != [want]:
            bad.append(f"NS {n} の D {got} が表の値 {want:.2f} と違う")
    for name, shift, tol in (("1 段", 1.0, 0.06), ("64 段", 64.0, 0.005)):
        p = runs[name][1]
        for n in WANT:
            for d0, d1 in zip(b.get(n, []), p.get(n, [])):
                if abs(d1 - d0 - shift) > tol:
                    bad.append(f"{name}: NS {n} の D が {d1 - d0:+.2f} 動いた（{shift:+.0f} のはず）")
        print(f"{name}: " + "・".join(f"NS {n} {', '.join(f'{d1 - d0:+.2f}' for d0, d1 in zip(b.get(n, []), p.get(n, [])))}" for n in WANT))
    return bad


if __name__ == "__main__":
    bad = main(*sys.argv[1:4])
    print("結果: " + ("全部通過" if not bad else "不合格: " + "・".join(bad)))
    sys.exit(1 if bad else 0)
