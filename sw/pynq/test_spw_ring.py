#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""SpW8 M5b: SpW の窓のレコード（type 5・f32、ADR 0029）を、本物の plring.Ring.read・SpwBackend.pump・poll_win・release・Bundler（f32）に通す PL なしの照合。
どこでも回る（numpy と libs45fast.so）。リングは numpy の配列（test_ring_fast.fake_ring）

    python3 test_spw_ring.py        # 結果: 全部通過 / 不合格
    python3 test_spw_ring.py -p     # 陽性対照: --posctl-spw-map（論理の窓と s の対応を入れ替える）。束が別の窓の和になり、落ちるべき

見ること:
  1. 32 窓 × 8 ダンプ（n_sum 4 で 2 束ずつ）が、計画の対応 (コア, s) → 論理の窓で束ねられ、器が numpy の float64 の和と bit で同じ（C の道・Python の道の両方）
  2. コアごとの SEQ の飛び 0・頭の不一致 0・動いていない流れのレコード 0
  3. 中身を 1 byte 壊したレコードは C の道で CRC の誤りになり、その束を捨てる（理由 CRC）
  4. 頭の NS が計画と違うレコードは捨てて数える（hdr_bad）
  5. C の道（--fast --fast-ring の SpwBackend.cmode、s45_spw_scan）で 1〜4 が Python の道と同じ（束・捨てた束・数え）。間に TP のレコードを挟み、Python に戻って読む
  6. SpW8 M6: できた束を C が出口の溜まり（s45ring.Ring）へ直に書く道と、Acq._spw_ev → _spec_record_spw → _put の道で、
     溜まりから読んだ記録（SPEC・DROP・BDROP の EVENT）の bytes・seq・Acq の数え（seq・drop・n_dump・kgap・health・flags・sat）が同じ。
     溜まりは小さく（端の折り返し・溢れて捨てる・1/4 まで戻るのを両方の道で通る）。陽性対照 -p では、直に書く道の時刻の錨を 1 ビートずらす
"""
import sys
import types
import zlib

import numpy as np

import plring as PR
import s45acq as A
import s45fast as F
from test_ring_fast import fake_ring

BASE = A.BASE_BEATS


def put5(r, core, s, seq, k, t, ns, shift, pay, cfg=0, bad_byte=False):
    """PL の形の type 5 のレコード（頭の語 4 = log2N 12・NS・SHIFT・G 0・fmt 1・src）"""
    pb = pay.nbytes
    L = 64 + pb + 64
    p = r.w % r.size
    if p + L > r.size:
        h = np.zeros(8, np.uint64)
        h[0] = PR.MAGIC_R | (PR.TYPE_PAD << 40)
        h[7] = r.size - p
        r.a64[p >> 3:(p >> 3) + 8] = h
        r.w += r.size - p
        p = 0
    h = np.zeros(8, np.uint64)
    h[0] = PR.MAGIC_R | (A.TYPE_SPW << 40) | (core << 48) | (s << 56)
    h[1] = seq | (k << 32)
    h[2] = (t - 101) // A.spw_frame(ns)
    h[3] = t
    h[4] = 12 | (ns << 8) | (shift << 16) | (1 << 32) | (core << 40)
    h[5] = BASE // A.spw_frame(ns)
    h[6] = cfg
    h[7] = pb
    i = p >> 3
    r.a64[i:i + 8] = h
    r.a8[p + 64:p + 64 + pb] = pay.view(np.uint8)
    crc = zlib.crc32(r.a8[p:p + 64 + pb])
    if bad_byte:
        r.a8[p + 64 + 1000] ^= 1                   # CRC を取った後に壊す
    tl = np.zeros(8, np.uint64)
    tl[0] = PR.MAGIC_E | (seq << 32)
    tl[1] = crc
    r.a64[(p + 64 + pb) >> 3:((p + 64 + pb) >> 3) + 8] = tl
    r.w += L
    r.m.regs[PR.R_W] = r.w & 0xFFFFFFFF


class _Tp:
    def __init__(self):
        self.n = 0

    def feed(self, seq, n, pay, k):
        self.n += 1


def put_tp(r, core, seq, pay):
    pb = pay.nbytes
    p = r.w % r.size
    if p + 128 + pb > r.size:
        h = np.zeros(8, np.uint64)
        h[0] = PR.MAGIC_R | (PR.TYPE_PAD << 40)
        h[7] = r.size - p
        r.a64[p >> 3:(p >> 3) + 8] = h
        r.w += r.size - p
        p = 0
    h = np.zeros(8, np.uint64)
    h[0] = PR.MAGIC_R | (PR.TYPE_TP << 40) | (core << 48) | (0xFF << 56)
    h[1] = seq
    h[5] = 1
    h[7] = pb
    r.a64[p >> 3:(p >> 3) + 8] = h
    r.a8[p + 64:p + 64 + pb] = pay.view(np.uint8)
    tl = np.zeros(8, np.uint64)
    tl[0] = PR.MAGIC_E | (seq << 32)
    tl[1] = zlib.crc32(r.a8[p:p + 64 + pb])
    r.a64[(p + 64 + pb) >> 3:((p + 64 + pb) >> 3) + 8] = tl
    r.w += 128 + pb
    r.m.regs[PR.R_W] = r.w & 0xFFFFFFFF


def make_be(ring, lazy, posctl, cmode=False):
    be = A.SpwBackend.__new__(A.SpwBackend)
    be.o = types.SimpleNamespace(posctl_spw_map=posctl)
    be.cmode, be.on_spw, be.discard = cmode, None, False
    be.tps = [_Tp() for _ in range(4)]
    ring.a8p = ring.a8.ctypes.data
    be.logs = []
    be.log = lambda *x: be.logs.append(" ".join(map(str, x)))
    be.ring, be.use_ring = ring, True
    be.amap = {a: a for a in range(4)}
    be.running, be.n_pump, be.stall_at, be.ring_crc, be.n_mat = True, 0, 0.0, 0, 0
    st = A.default_settings_spw()
    be.cfgs = A.spw_cfgs(st, A.spw_plan(st))
    be._spw_init(be.cfgs)
    be.lazy_wins = {j for j, cf in enumerate(be.cfgs) if cf["active"]} if lazy else set()
    if cmode:
        be._c_init()
    return be


def run(lazy, posctl, corrupt=None, bad_ns=None, ndump=8, cmode=False):
    rng = np.random.default_rng(5)
    r = fake_ring(16 << 20)
    be = make_be(r, lazy, posctl, cmode)
    plans = A.spw_plan(A.default_settings_spw())
    want = {}                                      # 論理の窓 j → 束ごとの numpy の float64 の和
    seq = [0] * 4
    bund = {j: A.Bundler(cf["n_sum"], cf["pl_nacc"], fast=F, f32=True) for j, cf in enumerate(be.cfgs) if cf["active"]}
    got = {j: [] for j in bund}
    drops = []
    if cmode:
        def on_spw(e):
            j = int(e["j"])
            if e["kind"] == 1:
                got[j].append((int(e["k"]), be.sc.acc[j].copy()))
            else:
                drops.append((j, (int(e["jb"]), F.SPW_WHY[int(e["why"])], int(e["have"]))))
        be.on_spw = on_spw
    t0 = 1000 * 4 * BASE                           # tint の格子（n_sum 4）
    for n in range(ndump):
        for a in range(4):
            for x in plans[a]["wins"]:
                j = a * A.SPW_NW + x["i"]
                pay = (rng.random(A.P.NCH) * 2.0 ** rng.integers(10, 40)).astype(np.float32)
                ns = x["ns"] if (a, x["s"], n) != bad_ns else x["ns"] % 5 + 1
                put5(r, a, x["s"], seq[a], n, t0 + n * BASE + 101 + x["s"], ns, A.SPW_SHIFT, pay, bad_byte=(a, x["s"], n) == corrupt)
                seq[a] += 1
                b = want.setdefault(j, {}).setdefault(n // 4, np.zeros(A.P.NCH))
                b += pay.astype(np.float64)
            tp = np.zeros(20, np.uint64)              # TP のレコード（C の道は Python に戻って読む）
            put_tp(r, a, n, tp)
        if n % 3 == 2 or n == ndump - 1:           # 何回かに分けて読む（周をまたぐ束）
            be.pump()
            for j, bu in ({} if cmode else bund).items():
                while True:
                    rr = be.poll_win(j)
                    if rr is None:
                        break
                    m, spec, miss = rr
                    g, d = bu.add(m, spec)
                    if d is not None:
                        drops.append((j, d))
                    if g is not None:
                        got[j].append((g[0]["k"], g[1].copy()))
            be.release()
    return be, want, got, drops, bund


class _O:
    spw = fast = fast_ring = True
    posctl_corrupt = posctl_gap = 0
    proto = 2

    def __getattr__(self, k):
        return None


def run_out(direct, posctl, ndump=48, cap=None):
    """6.: C のなめ（cmode）を本物の Acq につなぎ、出口の溜まりに書かせて、読み手の代わりに周ごとに読み出す"""
    import s45ring as R
    rng = np.random.default_rng(7)
    r = fake_ring(16 << 20)
    be = make_be(r, True, False, cmode=True)
    rec = 24 + A.P.SPEC2_H.size + 4 * A.P.NCH
    out = R.Ring(cap or int(20.5 * rec))
    try:
        acq = A.Acq(None, out, _O())
        tb = types.SimpleNamespace(_anchor=dict(utc_sec=1793778000, stamp=10**10 + (1 if (direct and posctl) else 0)),
                                   cal=dict(pps_det_ns=12.3, adc_to_core_ns={0: 1.0, 1: 2.0, 2: 3.0, 3: 4.0}))
        be.clock = A.Clock(tb, {1: 86.03, 2: 135.07, 3: 231.05, 4: 411.01, 5: 757.03})
        acq.be = be
        acq.bund = [A._CBund(be.sc, j) if cf["active"] else None for j, cf in enumerate(be.cfgs)]
        be.on_spw = acq._spw_ev
        be.out_acq = acq if direct else None
        plans = A.spw_plan(A.default_settings_spw())
        seq = [0] * 4
        recs = []
        t0 = 1000 * 4 * BASE
        for n in range(ndump):
            if n == 21:
                continue                               # 欠けたダンプ（全部の窓で、束を捨てる・k が飛ぶ）
            for a in range(4):
                for x in plans[a]["wins"]:
                    pay = (rng.random(A.P.NCH) * 2.0 ** rng.integers(10, 40)).astype(np.float32)
                    put5(r, a, x["s"], seq[a], n, t0 + n * BASE + 101 + x["s"], x["ns"], A.SPW_SHIFT, pay)
                    seq[a] += 1
                put_tp(r, a, n, np.zeros(20, np.uint64))
            if n % 3 == 2 or n == ndump - 1:
                be.pump()
                while True:                            # 読み手の代わり
                    xx = out.next_record()
                    if xx is None:
                        break
                    mv, sq, end = xx
                    recs.append((sq, bytes(mv)))
                    del mv
                    out.advance(end)
                    out.ack_to(end)
        # _loop_once は PL が要るので回さない。kgap・n_dump は _loop_once と同じく win から写す
        acq.kgap[:] = be.sc.win["kgap"].tolist()
        acq.n_dump[:] = be.sc.win["ndump"].tolist()
        cnt = dict(seq=acq.seq, drop=acq.drop["n"], n_dump=list(acq.n_dump), kgap=list(acq.kgap), h=acq.h_or, fl=acq.fl_or, sat=acq.sat)
        return recs, cnt, acq.n_out
    finally:
        out.close()


def main(posctl=False):
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'OK' if cond else 'NG'}  {name}{('  ' + detail) if detail else ''}")

    for lazy, cm in ((True, False), (False, False), (True, True)):
        nm = "C のなめ（SpwScan）" if cm else "C の道（LazyRec・spw_acc）" if lazy else "Python の道（写す）"
        be, want, got, drops, _ = run(lazy, posctl, cmode=cm)
        if cm:
            chk(f"{nm}: TP のレコードを Python で読んだ（4 コア × 8）", [t.n for t in be.tps] == [8] * 4, f"{[t.n for t in be.tps]}")
        nb = sum(len(v) for v in got.values())
        same = all(len(got[j]) == 2 and all(np.array_equal(acc, want[j][k]) for k, acc in got[j]) for j in got)
        chk(f"{nm}: 32 窓 × 2 束が numpy の float64 の和と bit で同じ", nb == 64 and same, f"束 {nb}・捨てた {len(drops)}")
        st = {k: be.spw_stat()[k] for k in ("seq_gap", "hdr_bad", "stray")}
        chk(f"{nm}: SEQ の飛び・頭の不一致・動いていない流れ 0", st == dict(seq_gap=0, hdr_bad=0, stray=0) and be.ring_crc == 0, f"{st}・CRC {be.ring_crc}")
    p0 = A.spw_plan(A.default_settings_spw())[1]["wins"][3]
    j = 8 + p0["i"]
    for cm in (False, True):
        nm = "C のなめ" if cm else "C の道"
        be, want, got, drops, bund = run(True, posctl, corrupt=(1, p0["s"], 5), cmode=cm)
        cb = int(be.sc.win["crc_bad"][j]) if cm else bund[j].crc_bad
        chk(f"{nm}: 壊したレコード（B の窓 3・ダンプ 5）で CRC の誤り 1・その束（1）を捨てる・ほかの束は残る",
            cb == 1 and [k for k, _ in got[j]] == [0] and any(jj == j and d[1] == "CRC" for jj, d in drops)
            and sum(len(v) for v in got.values()) == 63, f"crc_bad {cb}・残った束 {[k for k, _ in got[j]]}・捨てた {drops}")
        be, want, got, drops, bund = run(True, posctl, bad_ns=(2, p0["s"], 1), cmode=cm)
        chk(f"{nm}: 頭の NS が計画と違うレコード 1 本を捨てて hdr_bad 1・その束は欠け", be.hdr_bad == 1 and len(got[16 + p0["i"]]) == 1
            and any(jj == 16 + p0["i"] and d[1] == "欠け" for jj, d in drops), f"hdr_bad {be.hdr_bad}・捨てた {drops}")
    import s45proto as P
    for cap, nm in ((None, "小さい溜まり（折り返し・溢れ）"), (64 << 20, "大きい溜まり")):
        r1, c1, n1 = run_out(True, posctl, cap=cap)
        r2, c2, n2 = run_out(False, posctl, cap=cap)
        ty = {}
        for _, b in r1:
            t = P.T_NAMES[P.parse_header(b[:24])[0]]
            ty[t] = ty.get(t, 0) + 1
        chk(f"直に書く道（{nm}）: 読んだ記録の bytes・seq と Acq の数えが今までの道と同じ",
            r1 == r2 and c1 == c2 and n2 == 0 and n1 > 0 and c1["kgap"] == [1 if cf["active"] else 0 for cf in A.spw_cfgs(A.default_settings_spw(), A.spw_plan(A.default_settings_spw()))],
            f"記録 {len(r1)} / {len(r2)}（{ty}）・直に {n1}・drop {c1['drop']} / {c2['drop']}・seq {c1['seq']} / {c2['seq']}")
    print(f"結果: {'全部通過' if ok else '不合格'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(posctl="-p" in sys.argv[1:]))
