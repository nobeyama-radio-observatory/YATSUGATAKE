#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""SpW8 M6: 判定 PS-1（float32・utc_ns の補正）を specd の記録で照らす。PL もボードも要らない（写し取りの準備だけボードの試験用ディレクトリで）

    # 1. 写し取りの準備（ボードの試験用ディレクトリ DIR に sw/pynq を写した後。DIR/plring.py に SPW_TAP の包みを足す）
    python3 spw_ps1.py patch DIR
    #    陽性対照の準備: DIR/timebase.py から (7, 10) の D(NS) の行を外す
    python3 spw_ps1.py patch-nodly DIR
    # 2. ボードで SPW_TAP=tap.npz を付けて specd（--fast・--fast-ring なし）を起こし、窓 16 本・tint 0.01024（n_sum 1）で受ける
    # 3. 照らす
    python3 spw_ps1.py check runs/ps1.s45 --tap tap.npz --map A0:0,A1:1,... --tint 0.01024

照らすもの（test/acceptance/spw8/PS-1.md の合格）:
  - 記録は版 2 だけ・SPEC の kind 3
  - 窓ごとに束の間隔がちょうど tint（±1 ns）
  - 窓ごとに e = utc_ns − dump_t·125/32 ＋ (D(NS) ＋ 1.5·L(NS))·125/32（L = 2^(12+NS) ビート、D は timebase.WIN_DELAY[(7, 10)]）。
    同じ ADC の窓どうしで e が一致（±2 ns）。窓の中の e の幅も出す
  - --tap: n_sum 1 の SPEC の本体が、PL のレコード（写し取った type 5 の本体）を IF の昇順に並べたものとバイト単位で同じ。
    (core, 論理の窓) → 流れ s は --map（STATUS の spw_map）、束は dump_t で引き当てる
  - 陽性対照（道具の中）: D を足さない e・1.5·L を足さない e は、NS の違う窓どうしでずれる（ずれの大きさを出す）
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "sw", "pynq"))
import s45proto as P   # noqa: E402
import timebase as TB  # noqa: E402

NS_PER_BEAT = 125 / 32
KEY = (7, 10)

TAP_CODE = '''

# ---- SpW8 M6 PS-1 の写し取り（hw/bits/spw8/tools/spw_ps1.py patch が足した。試験用のディレクトリだけ。製品の plring には入れない）----
import os as _tap_os
_TAP = _tap_os.environ.get("SPW_TAP")
if _TAP:
    _tap_read0 = Ring.read
    _tap_d = {}
    _tap_n = int(_tap_os.environ.get("SPW_TAP_N", "40"))
    _tap_cnt = [0]

    def _tap_save():
        keys = sorted(_tap_d)
        arr = {}
        for core, s in keys:
            hs, ps = zip(*_tap_d[(core, s)])
            arr[f"h_{core}_{s}"] = np.stack(hs)
            arr[f"p_{core}_{s}"] = np.stack(ps)
        np.savez(_TAP + ".tmp.npz", **arr)
        _tap_os.replace(_TAP + ".tmp.npz", _TAP)

    def _tap_read(self, lazy=None):
        out = _tap_read0(self, lazy)
        for core, s, seq, hw, pay, crc_ok, tail_ok in out:
            if (int(hw[0]) >> 40) & 0xFF != 5 or isinstance(pay, LazyRec) or not crc_ok:
                continue
            l = _tap_d.setdefault((int(core), int(s)), [])
            if len(l) < _tap_n:
                l.append((np.asarray(hw).copy(), np.asarray(pay).copy()))
                _tap_cnt[0] += 1
                if _tap_cnt[0] % 64 == 0:
                    _tap_save()
        return out

    Ring.read = _tap_read
'''


def patch(d):
    p = os.path.join(d, "plring.py")
    s = open(p).read()
    if "SpW8 M6 PS-1 の写し取り" in s:
        print(f"{p}: もう足してある")
        return 0
    open(p, "a").write(TAP_CODE)
    print(f"{p}: SPW_TAP の包みを足した（SPW_TAP=<npz> を付けて起こすと type 5 の本体を流れごとに SPW_TAP_N 本写す）")
    return 0


def patch_nodly(d):
    p = os.path.join(d, "timebase.py")
    s = open(p).read()
    tag = "\n# SpW8 M6 PS-1 の陽性対照（spw_ps1.py patch-nodly）: (7, 10) の D(NS) の行を外す\nWIN_DELAY.pop((7, 10), None)\n"
    if tag in s:
        print(f"{p}: もう外してある")
        return 0
    i = s.index("\ndef win_delay_of")
    open(p, "w").write(s[:i] + tag + s[i:])
    print(f"{p}: (7, 10) の行を外した（GET CAL の wdly_ns が none になるはず）")
    return 0


def read_recs(path):
    f = open(path, "rb").read()
    o = 0
    vers, spec = set(), []
    while o < len(f):
        rt, pl, crc, seq = P.parse_header(f[o:o + 24])
        ver = P.header_ver(f[o:o + 24])
        vers.add(ver)
        if rt == P.T_SPEC:
            d = P.decode(rt, f[o + 24:o + 24 + pl], ver)
            d["_ver"] = ver
            spec.append(d)
        o += 24 + pl
    return vers, spec


U0 = [None]


def e_of(d, wd, use_d=True, use_l=True):
    """e の基準 U0（最初の記録の utc_ns・dump_t の分）を整数のまま引いてから float にする。utc_ns ≒ 1.8e18 は float64 の刻みが 256 ns
    （M6 の 1 回目で、NS 3・4 の窓だけ ±256 ns ずれて見えた）"""
    if U0[0] is None:
        U0[0] = (int(d["utc_ns"]), int(d["dump_t"]))
    ns = d["ns"]
    corr = (wd.get(ns, 0.0) if use_d else 0.0) + (1.5 * 2 ** (12 + ns) if use_l else 0.0)
    return float(int(d["utc_ns"]) - U0[0][0]) - (int(d["dump_t"]) - U0[0][1]) * NS_PER_BEAT + corr * NS_PER_BEAT


def check(a):
    wd = TB.WIN_DELAY.get(KEY, {})
    bad = []
    vers, spec = read_recs(a.file)
    print(f"記録の版: {sorted(vers)}・SPEC {len(spec)} 本・D(NS) {KEY} = {wd}")
    if vers != {2}:
        bad.append(f"版 2 以外の記録がある（{sorted(vers)}）")
    if any(d["kind"] != 3 for d in spec):
        bad.append("SPEC の kind が 3 でない記録がある")
    by = {}
    for d in spec:
        by.setdefault((d["core"], d["s"]), []).append(d)
    tint_ns = round(a.tint * 1e9)
    res = {}
    for key, ds in sorted(by.items()):
        ds.sort(key=lambda d: d["dump_t"])
        u = np.array([d["utc_ns"] for d in ds], dtype=np.int64)
        du = np.diff(u)
        if len(du) and (du.min() < tint_ns - 1 or du.max() > tint_ns + 1):
            bad.append(f"{'ABCD'[key[0]]}{key[1]} の束の間隔 {du.min()}〜{du.max()} ns（tint {tint_ns}）")
        es = {m: np.array([e_of(d, wd, *m) for d in ds]) for m in ((True, True), (False, True), (True, False))}
        efine = np.array([e_of(d, TB.WIN_DELAY[(2, 3)]) for d in ds])
        res[key] = dict(ns=ds[0]["ns"], n=len(ds), du=(int(du.min()), int(du.max())) if len(du) else None,
                        e=float(np.median(es[(True, True)])), ew=float(np.ptp(es[(True, True)])),
                        e_nod=float(np.median(es[(False, True)])), e_nol=float(np.median(es[(True, False)])), e_fine=float(np.median(efine)))
    for c in sorted({k[0] for k in res}):
        ks = sorted(k for k in res if k[0] == c)
        ref = res[ks[0]]
        line = []
        for k in ks:
            r = res[k]
            de = r["e"] - ref["e"]
            line.append(f"{k[1]}（NS {r['ns']}）{de:+.1f}")
            if abs(de) > 2.0:
                bad.append(f"{'ABCD'[c]}{k[1]} の e が窓 {ks[0][1]} と {de:+.1f} ns ずれる")
            if r["ew"] > 2.0:
                bad.append(f"{'ABCD'[c]}{k[1]} の e の幅 {r['ew']:.1f} ns")
        nod = max(res[k]["e_nod"] for k in ks) - min(res[k]["e_nod"] for k in ks)
        nol = max(res[k]["e_nol"] for k in ks) - min(res[k]["e_nol"] for k in ks)
        print(f"{'ABCD'[c]}: e = {ref['e']:.1f} ns（窓 {ks[0][1]}）・窓ごとの差 " + "・".join(line)
              + f"・e の幅の最大 {max(res[k]['ew'] for k in ks):.1f} ns・束の間隔 {sorted({res[k]['du'] for k in ks})}")
        fine = max(res[k]["e_fine"] for k in ks) - min(res[k]["e_fine"] for k in ks)
        print(f"   陽性対照（道具の中）: D を足さない e の窓どうしの幅 {nod:.1f} ns・1.5·L を足さない e の幅 {nol:.1f} ns・"
              f"SAM45-Fine の表 (2, 3) を当てた e の幅 {fine:.1f} ns")
    if a.tap:
        m = dict(x.split(":") for x in a.map.split(","))
        t = np.load(a.tap)
        nsame = ndiff = nmiss = 0
        for (c, s), ds in sorted(by.items()):
            kk = f"{'ABCD'[c]}{s}"
            if kk not in m or f"h_{c}_{m[kk]}" not in t:
                nmiss += len(ds)
                continue
            hs, ps = t[f"h_{c}_{m[kk]}"], t[f"p_{c}_{m[kk]}"]
            pt = {int(h[3]): p for h, p in zip(hs, ps)}
            for d in ds:
                if d["n_sum"] != 1:
                    bad.append("n_sum が 1 でない記録がある（--tap は tint 0.01024 で）")
                    break
                p = pt.get(int(d["dump_t"]))
                if p is None:
                    continue
                pl = np.frombuffer(p.tobytes(), dtype="<f4")
                want = pl[P.IF_ORDER]
                got = np.asarray(d["data"], dtype="<f4")
                if a.posctl_tap:
                    want = pl                          # 陽性対照: IF の昇順に並べ替えずに比べる → 違うはず
                if want.tobytes() == got.tobytes():
                    nsame += 1
                else:
                    ndiff += 1
        print(f"PL のレコードとの比べ（n_sum 1）: バイト単位で同じ {nsame} 本・違う {ndiff} 本・写しの無い流れ {nmiss} 本")
        if ndiff or nsame == 0:
            bad.append(f"PL のレコードと違う（同じ {nsame}・違う {ndiff}）")
    print("結果: " + ("全部通過" if not bad else "不合格: " + "・".join(bad[:8])))
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p1 = sp.add_parser("patch"); p1.add_argument("dir")
    p2 = sp.add_parser("patch-nodly"); p2.add_argument("dir")
    p3 = sp.add_parser("check")
    p3.add_argument("file")
    p3.add_argument("--tint", type=float, required=True)
    p3.add_argument("--tap", default=None)
    p3.add_argument("--map", default="", help="STATUS の spw_map（A0:4,A1:5,...）")
    p3.add_argument("--posctl-tap", action="store_true", help="陽性対照: PL のレコードを並べ替えずに比べる（違うと出るはず）")
    a = ap.parse_args()
    if a.cmd == "patch":
        return patch(a.dir)
    if a.cmd == "patch-nodly":
        return patch_nodly(a.dir)
    return check(a)


if __name__ == "__main__":
    sys.exit(main())
