#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""SpW8 M5b（ADR 0029）: s45fast.spw_acc（SpW の f32 のレコードを double の器へ）の PL なしの照合。どこでも回る（numpy と libs45fast.so）

    python3 test_spw_fast.py        # 結果: 全部通過 / 不合格
    python3 test_spw_fast.py -p     # 陽性対照: PC_NOACC（足さずに写す）。落ちるべき

見ること: CRC が zlib.crc32(頭 ＋ 中身) と同じ・器が numpy の float64 の和と bit で同じ・負や inf・NaN を数える・器の形の誤りを断る・
  SpwAcc（番地を先に引く）が spw_acc と同じ・spw_rec（記録の並べ替え・丸め・CRC）が numpy の道と bit で同じ
"""
import sys
import types
import zlib

import numpy as np

import s45fast as F
import s45proto as P

N = 4096


def rec_of(buf, p, n32):
    """plring.LazyRec と同じ欄（addr・n は u64 の数）を持つ偽物"""
    return types.SimpleNamespace(addr=buf.ctypes.data + p, n=n32 // 2)


def main(posctl=0):
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'OK' if cond else 'NG'}  {name}{('  ' + detail) if detail else ''}")

    rng = np.random.default_rng(32)
    nb = 4
    buf = np.zeros((64 + 4 * N) * nb // 8 + 8, np.uint64).view(np.uint8)
    recs, vals = [], []
    for j in range(nb):
        p = j * (64 + 4 * N)
        buf[p:p + 64] = rng.integers(0, 256, 64, dtype=np.uint8)
        v = (rng.random(N) * 2.0 ** rng.integers(0, 50, N)).astype(np.float32)
        buf[p + 64:p + 64 + 4 * N] = v.view(np.uint8)
        recs.append((p, rec_of(buf, p, N)))
        vals.append(v)
    acc = np.empty(N, np.float64)
    want = np.zeros(N, np.float64)
    for j, (p, r) in enumerate(recs):
        cp, bad = F.spw_acc(r, acc, j == 0, posctl)
        want = vals[j].astype(np.float64) if j == 0 else want + vals[j].astype(np.float64)
        chk(f"本 {j}: CRC が zlib と同じ", cp == zlib.crc32(buf[p:p + 64 + 4 * N]))
        chk(f"本 {j}: 悪い値 0", bad == 0, f"{bad}")
    chk(f"{nb} 本の器が numpy の float64 の和と bit で同じ", np.array_equal(acc, want),
        f"最大の差 {np.max(np.abs(acc - want)):.3g}")

    p, r = recs[0]
    v = vals[0].copy()
    v[[3, 100, 4095]] = [-1.0, np.inf, np.nan]
    v[7] = -0.0
    buf[p + 64:p + 64 + 4 * N] = v.view(np.uint8)
    _, bad = F.spw_acc(r, acc, True, posctl)
    chk("負・-0・inf・NaN の 4 個を数える", bad == 4, f"{bad}")
    sa = F.SpwAcc(np.empty(N, np.float64))
    for j, (p, r) in enumerate(recs[1:]):
        cp, bad = sa.add(r, j == 0, posctl)
        cp2, _ = F.spw_acc(r, acc, j == 0, posctl)
        if j == 0:
            chk("SpwAcc（番地を先に引く）が spw_acc と同じ CRC・器", cp == cp2 == zlib.crc32(buf[p:p + 64 + 4 * N]) and np.array_equal(sa.acc, acc))
    chk("SpwAcc の 3 本の器が spw_acc と bit で同じ", np.array_equal(sa.acc, acc))
    hd = bytes(range(88))
    out = np.empty(N, np.float32)
    crc = F.spw_rec(acc, hd, out)
    ref = acc[P.IF_ORDER].astype(np.float32)
    chk("spw_rec: 中身が acc[IF_ORDER].astype(float32) と bit で同じ・CRC が zlib(頭 ＋ 中身) と同じ",
        np.array_equal(out.view(np.uint32), ref.view(np.uint32)) and crc == zlib.crc32(hd + ref.tobytes()))
    for name, a in (("float32 の器", np.empty(N, np.float32)), ("長さ違いの器", np.empty(N - 2, np.float64))):
        try:
            F.spw_acc(r, a, True)
            chk(f"{name}を断る", False)
        except ValueError:
            chk(f"{name}を断る", True)
    print(f"結果: {'全部通過' if ok else '不合格'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(F.PC_NOACC if "-p" in sys.argv[1:] else 0))
