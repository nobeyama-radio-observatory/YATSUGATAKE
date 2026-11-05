#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""proj029 1: libs45fast.so（s45fast.c）の ctypes の包み。正解は s45acq.Acq._spec_record_full の中身と CRC（README の 1.）

- spec_f32(spec, hd) → (f32 の配列（IF の昇順 = spec の逆順）, crc)。2^53 以上なら P.f32_round と同じ ValueError
- spec_u64(spec, hd) → (u64 の配列（逆順）, crc)
- out を渡すとそこに書く（周ごとの確保を避ける）。posctl は陽性対照（1 = 0 への切り捨て、2 = 逆順にしない）
- ring_acc(rec, acc, first) → crc_pl（proj036: 束ねの 1 本をリングの上から器へ写す・足す）
- spw_acc(rec, acc, first) → (crc_pl, bad)（SpW8 M5b・ADR 0029: SpW の f32 のレコードを double の器へ写す・足す）
  SpwAcc(acc): 器の番地を先に引いておく spw_acc（ndarray.ctypes.data は 1 回 ≒ 18 µs（ボード）。1 本ごとに引くと C の 48 µs が 100 µs になった）
- spw_rec(acc, hd, out) → crc（SpW8 M5b: 器を IF の昇順の float32 に 1 回丸め、CRC は頭 ＋ 中身）
- SpwScan: SpW8 M5b のリングの C の道（s45_spw_scan）。[R, W) を 1 回なめ、振り分け・照らし・束ね・足し込みを C で。束ができた・捨てた・TP で Python に戻る
"""
import ctypes
import os

import numpy as np

PC_TRUNC, PC_NOREV = 1, 2
PC_NOACC = 1                     # proj036: ring_acc の陽性対照（足さずに写す）

_L = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs45fast.so"))
_vp, _sz, _u32p = ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32)
for _f in (_L.s45_spec_f32, _L.s45_spec_u64):
    _f.argtypes = [_vp, _sz, ctypes.c_char_p, _sz, _vp, _u32p, ctypes.c_int]
    _f.restype = ctypes.c_int
_L.s45_ring_spec.argtypes = [_vp, _sz, ctypes.c_char_p, _sz, _vp, ctypes.c_int, _u32p, _u32p, ctypes.c_int]
_L.s45_ring_spec.restype = ctypes.c_int
_L.s45_ring_acc.argtypes = [_vp, _sz, _vp, ctypes.c_int, _u32p, ctypes.c_int]
_L.s45_ring_acc.restype = None
_L.s45_spw_acc.argtypes = [_vp, _sz, _vp, ctypes.c_int, _u32p, ctypes.c_int]
_L.s45_spw_acc.restype = ctypes.c_int
_L.s45_spw_rec.argtypes = [_vp, _sz, ctypes.c_char_p, _sz, _vp, _u32p]
_L.s45_spw_rec.restype = None
_L.s45_spw_scan.argtypes = [_vp, ctypes.c_uint64, ctypes.c_uint32, ctypes.c_uint32, _vp, _vp, _vp, _vp, _vp, _vp, _vp, ctypes.c_int64, ctypes.c_int, _vp]
_L.s45_spw_scan.restype = ctypes.c_int
SPW_WIN = np.dtype([(k, np.uint64 if k in ("w4", "acc", "hd") else np.int64) for k in (
    "n_sum", "pl_nacc", "w4", "dk", "r0", "has_r0", "dead", "jb0", "has_jb0", "cur", "jb", "cnt", "m_first", "m_last", "bad",
    "cfg", "sat", "flags", "h", "n", "t0", "seq0", "acc", "nf", "miss", "crc_bad", "val_bad", "pl_dumps", "r_bad", "drop",
    "lk", "kgap", "ndump", "hd", "uoff")])   # s45fast.c の spw_win_t
SPW_OUT = np.dtype([(k, np.uint64 if k in ("buf", "cap", "w", "r") else np.int64) for k in (
    "buf", "cap", "w", "r", "seq", "ver", "on", "clock_ok", "stamp", "h_add", "h_or", "fl_or", "sat", "n_out")])   # spw_out_t（SpW8 M6）
SPW_EV = np.dtype([(k, np.int64) for k in ("kind", "j", "why", "jb", "have", "k", "t", "n", "sat", "flags", "h", "cfg", "seq")])   # spw_ev_t
SPW_WHY = {1: "欠け", 2: "r", 3: "順", 4: "CFG", 5: "N", 6: "CRC", 7: "値", 8: "頭"}   # s45acq.Bundler の理由と同じ
_L.s45_crc32.argtypes = [ctypes.c_uint32, _vp, _sz]
_L.s45_crc32.restype = ctypes.c_uint32
_L.s45_hw_crc.restype = ctypes.c_int
_L.s45_nop.restype = None

HW_CRC = bool(_L.s45_hw_crc())


def _in(spec):
    a = np.asarray(spec)
    if a.dtype != np.uint64 or not a.flags.c_contiguous:
        a = np.ascontiguousarray(a, np.uint64)
    return a


def spec_f32(spec, hd, out=None, posctl=0):
    a = _in(spec)
    if out is None:
        out = np.empty(a.size, np.float32)
    c = ctypes.c_uint32()
    if _L.s45_spec_f32(a.ctypes.data, a.size, hd, len(hd), out.ctypes.data, ctypes.byref(c), posctl):
        raise ValueError("u64 が 2^53 以上（float64 で厳密でない）")
    return out, c.value


def spec_u64(spec, hd, out=None, posctl=0):
    a = _in(spec)
    if out is None:
        out = np.empty(a.size, np.uint64)
    c = ctypes.c_uint32()
    _L.s45_spec_u64(a.ctypes.data, a.size, hd, len(hd), out.ctypes.data, ctypes.byref(c), posctl)
    return out, c.value


def ring_spec(rec, hd, fmt, out=None, posctl=0):
    """proj029 2: PL のリングの上のレコード（plring.LazyRec）から記録を作る。fmt "f32" / "u64"。
    → (data（逆順）, crc（頭 hd ＋ data）, crc_pl（PL の頭 ＋ 中身。尾の CRC と照らすのは呼び手）)"""
    f = 1 if fmt == "f32" else 0
    if out is None:
        out = np.empty(rec.n, np.float32 if f else np.uint64)
    c, cp = ctypes.c_uint32(), ctypes.c_uint32()
    if _L.s45_ring_spec(rec.addr, rec.n, hd, len(hd), out.ctypes.data, f, ctypes.byref(c), ctypes.byref(cp), posctl):
        raise ValueError("u64 が 2^53 以上（float64 で厳密でない）")
    return out, c.value, cp.value


def ring_acc(rec, acc, first, posctl=0):
    """proj036: PL のリングの上のレコード（plring.LazyRec）を器 acc（np.uint64 × rec.n、C の連続）へ。first なら写す、でなければ足す。
    → crc_pl（PL の頭 ＋ 中身の CRC。尾の CRC と照らすのは呼び手）"""
    if acc.dtype != np.uint64 or acc.size != rec.n or not acc.flags.c_contiguous:
        raise ValueError(f"器は np.uint64 × {rec.n} の連続な配列")
    cp = ctypes.c_uint32()
    _L.s45_ring_acc(rec.addr, rec.n, acc.ctypes.data, 1 if first else 0, ctypes.byref(cp), posctl)
    return cp.value


def spw_acc(rec, acc, first, posctl=0):
    """SpW8 M5b（ADR 0029）: PL のリングの上の SpW のレコード（plring.LazyRec、中身は f32 × 2·rec.n）を器 acc（np.float64 × 2·rec.n、C の連続）へ。
    first なら写す、でなければ足す。→ (crc_pl, bad)。bad は中身の負か有限でない値の数（0 = よし）"""
    n = 2 * rec.n
    if acc.dtype != np.float64 or acc.size != n or not acc.flags.c_contiguous:
        raise ValueError(f"器は np.float64 × {n} の連続な配列")
    cp = ctypes.c_uint32()
    bad = _L.s45_spw_acc(rec.addr, n, acc.ctypes.data, 1 if first else 0, ctypes.byref(cp), posctl)
    return cp.value, bad


class SpwAcc:
    """SpW8 M5b: 1 つの器（np.float64 × n、C の連続）への spw_acc。番地と CRC の受け皿を先に用意する（Bundler が窓ごとに 1 つ持つ）"""

    def __init__(self, acc):
        if acc.dtype != np.float64 or not acc.flags.c_contiguous:
            raise ValueError("器は np.float64 の連続な配列")
        self.acc, self.n, self.p = acc, acc.size, acc.ctypes.data
        self.cp = ctypes.c_uint32()
        self.cpr = ctypes.byref(self.cp)

    def add(self, rec, first, posctl=0):
        """rec: plring.LazyRec（中身は f32 × 2·rec.n）。→ (crc_pl, bad)"""
        if 2 * rec.n != self.n:
            raise ValueError(f"器は {self.n} 個（レコードは f32 × {2 * rec.n}）")
        bad = _L.s45_spw_acc(rec.addr, self.n, self.p, 1 if first else 0, self.cpr, posctl)
        return self.cp.value, bad


class SpwRec:
    """SpW8 M5b: spw_rec の速い形。出口（np.float32 × n）と CRC の受け皿を 1 つ持ち、器は番地で受ける（ctypes.data を 1 本ごとに引かない）。
    出口は次の rec で上書きする（呼び手は溜まりへ写してから次を呼ぶ。s45acq の _put は写す）"""

    def __init__(self, n):
        self.out = np.empty(n, np.float32)
        self.n, self.op = n, self.out.ctypes.data
        self.cp = ctypes.c_uint32()
        self.cpr = ctypes.byref(self.cp)

    def rec(self, acc_p, hd):
        """acc_p: 器（np.float64 × n）の番地。→ (出口, crc)"""
        _L.s45_spw_rec(acc_p, self.n, hd, len(hd), self.op, self.cpr)
        return self.out, self.cp.value


class SpwScan:
    """SpW8 M5b: s45_spw_scan の包み。窓の状態（SPW_WIN × nwin）・器（float64 × nwin × nf）・smap（4 × 256 の int8、−1 = 動いていない）を持つ。
    番地は先に引く。scan(ring_p, size, r, w) → (状態, r, ev の並び)。状態は s45fast.c の s45_spw_scan の戻り値"""

    def __init__(self, nwin, nf=4096, base=2621440, posctl=0):
        self.win = np.zeros(nwin, SPW_WIN)
        self.acc = np.zeros((nwin, nf), np.float64)
        self.smap = np.full(4 * 256, -1, np.int8)
        self.cseq = np.full(4, -1, np.int64)
        self.ctr = np.zeros(4, np.int64)
        self.ev = np.zeros(2, SPW_EV)
        self.nev = np.zeros(1, np.int64)
        self.rout = np.zeros(1, np.uint32)
        self.base, self.posctl = base, posctl
        a0 = self.acc.ctypes.data
        self.win["acc"] = [a0 + i * nf * 8 for i in range(nwin)]
        self.win["nf"] = nf
        self.win["dk"] = -1
        self.win["lk"] = -1
        self.out = np.zeros(1, SPW_OUT)            # SpW8 M6: 出口の溜まりへ直に書く（out["on"] 1 で。0 なら今までどおり束ごとに ev）
        self.p = [x.ctypes.data for x in (self.smap, self.win, self.cseq, self.ctr, self.ev, self.nev, self.rout)]
        self.po = self.out.ctypes.data

    def scan(self, ring_p, size, r, w):
        ps = self.p
        st = _L.s45_spw_scan(ring_p, size, r, w, *ps, self.base, self.posctl, self.po)
        return st, int(self.rout[0]), (self.ev[:int(self.nev[0])] if st == 1 else ())


def spw_rec(acc, hd, out):
    """SpW8 M5b: 器 acc（np.float64 × n、FFT の ch の順）→ out（np.float32 × n、IF の昇順 = s45proto.IF_ORDER）。戻り値 zlib.crc32(hd ＋ out)"""
    if acc.dtype != np.float64 or out.dtype != np.float32 or acc.size != out.size or acc.size % 2:
        raise ValueError("器は np.float64・出口は np.float32 の同じ長さ（偶数）")
    c = ctypes.c_uint32()
    _L.s45_spw_rec(acc.ctypes.data, acc.size, hd, len(hd), out.ctypes.data, ctypes.byref(c))
    return c.value


def crc32(buf, init=0):
    """zlib.crc32(buf, init) と同じ（buf は C の連続な bytes-like）"""
    b = np.frombuffer(memoryview(buf).cast("B"), np.uint8)
    return int(_L.s45_crc32(init, b.ctypes.data, b.size))


def nop():
    _L.s45_nop()
