#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""proj018 — 取得のプロセス。PL（proj017 の bit）を持ち、8 窓のダンプと 4 ADC の TP を読み落としなく読み、記録にして溜まりに置く。

通信のプロセス（specd.py）とは、溜まり（s45ring）と命令のパイプ（辞書を送って辞書を受ける）だけでつながる。
読み出しの環は proj017 `fine.py` の F-4 と同じ（SEQ を見て閉じたダンプを seqlock で読む・TP のリングを TP_WP まで読む）。
違うのは、**記録を Python のリストに溜めない**こと（GC と伸びるリストが 1 周の最大を延ばす疑い。README）。

遅れの対策（README の方針）: GC を止める（gc.freeze の後 gc.disable）・CPU 1 つに固定・可能なら SCHED_FIFO。

裏（backend）は 2 つ: HwBackend（PYNQ・proj017 の bit）と FakeBackend（PL なしで同じ間隔・同じ形の記録を作る。通信の試験用）。

proj021 手順 2-3a: HwBackend の読み口を **PL が書くリング**（s45_ring_0。plring.Ring）に替えた（`--read ring`、既定）。
  SPEC・TP・SNAP をレコードで受け、記録の形（s45proto v1）は今のまま。2-3a〜2-3d にあった `--read axi`（仮の読み窓を seqlock で）は
  2-2d で外した（bit に仮の読み窓が無い）

proj023 手順 4d: **SAM45-Wide（BIT_KIND 1）の裏 WideBackend**（`--wide`。bits.json の項目なら "kind": "wide"）。窓の代わりに
  8 本の SLICE の流れ（A0〜D1、コアごとに束ね B と流れごとの S0）。PL のダンプは BASE（10.24 ms = 1280 フレーム × 2048 ビート）で、
  specd が tint / BASE 個を束ねる（Bundler はそのまま。r = 2·G は H-3 の V2-f で見た式の定数）。SPEC は s45proto v2 の kind 2（SLICE）:
  ns の欄 = log2 B、中身は IF の昇順（流れの ch の逆順）、if_mhz = 送る 2047 番目の ch の IF（DDC と同じく IF = if_mhz ＋ (i − 2047)·df）。
  utc_ns = beat_utc(dump_t) − adc_to_core − (D_S ＋ 1.5·L)、L = 2048。**D_S = 0**（手順 4e の sim-wds: SLICE と RAW は同じサンプルに同じ T を付ける）。
  SNAP は RAW の流れ（コア 0 の s 2）で、SAM45-Fine と同じ HwBackend._snap_ring（proj023 4g）
"""
import collections
import gc
import os
import resource
import time
import traceback
import zlib

import numpy as np

import bitinfo
import s45cal
import s45proto as P
from tpjump import TpJump

BEATS_PER_SEC = 256_000_000
G_BEATS = 1 << 19                          # 時刻の格子 2.048 ms（BITS.md）
BASE_BEATS = 5 * G_BEATS                   # proj021 2-3b: 基本の単位 10.24 ms（INTERFACE 4.4・5.1。コアの BASE_BEATS と照らす）
TP_N = 512                                 # 1.024 ms
TP_BEATS = TP_N * 512
TP_FLUSH = 40                              # TP をまとめて 1 記録にする区切りの数（40 × 1.024 ms = 40.96 ms）
TPF_RUN, TPF_OVR = 2, 16
ADC_NAMES = ("ADC_A", "ADC_B", "ADC_C", "ADC_D")
NW = 2
NS_OF_BW = {256: 1, 128: 2, 64: 3, 32: 4, 16: 5, 8: 6}
FLAGS_OK_MASK = 0x7EF                      # 窓の FLAGS で異常に数えるもの（[4] FFT IP に待たされた は正常。fine.py と同じ）
VERSION = "proj027-0.1"                 # proj027: 2G-4（--g24、FULL の流れ 4 本）を足した。2G-2 の道を形（G2Geom）の表で広げた。proj025: 2G-2（--g22、FULL の流れ 2 本）を足した。proj024: 2G-1 の写しの起こし（中身は proj023-0.1 と同じ）。proj023: SAM45-Wide（SLICE の流れ、--wide）。proj019-0.2: SNAP・LMX の出力の強さ


def malloc_tune(mmap_threshold=32 << 20, trim_threshold=1 << 30):
    """proj024 3d: glibc に 1 MiB 級の配列を mmap で取らせず（閾値 32 MiB = 64 bit の上限）、解放したメモリを OS に返させない（trim 1 GiB）。
    2G-1 の 1 MiB のレコードでは、周ごとに mmap・munmap とゼロ埋めのページフォルトが起き、まれに 57 ms の嵐になった（bench_g21 3a）。
    設定は環境変数 MALLOC_MMAP_THRESHOLD_・MALLOC_TRIM_THRESHOLD_ と同じ（mallopt。M_TRIM_THRESHOLD −1・M_MMAP_THRESHOLD −3）。戻り値 (成功, 説明)"""
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        ok = libc.mallopt(-3, int(mmap_threshold)) == 1 and libc.mallopt(-1, int(trim_threshold)) == 1
        return ok, f"mallopt M_MMAP_THRESHOLD {mmap_threshold}・M_TRIM_THRESHOLD {trim_threshold}: {'OK' if ok else '失敗'}"
    except Exception as e:  # noqa: BLE001
        return False, f"mallopt を呼べない（{type(e).__name__}: {e}）"


def default_settings():
    wins = []
    for i in range(4):
        wins.append(dict(if_mhz=3000.0, ns=1, shift=9, bundle=1))     # 窓 0: 256 MHz
        wins.append(dict(if_mhz=3000.0, ns=6, shift=9, bundle=1))     # 窓 1: 8 MHz
    return dict(tint=0.04096, cfg=0, fmt="f32", wins=wins)


# ---- proj023: SAM45-Wide（SLICE の流れ）
W_FS_MHZ, W_NPHYS, W_FRAME = 4096.0, 32768, 2048
W_PL_NACC = BASE_BEATS // W_FRAME          # 1280
W_DS_BEATS = 0                             # D_S（RTL の遅れ）。proj023 4e の sim-wds で 0（SLICE の T = RAW の T。adc_to_core は RAW で測る）
W_LB = {1: 0, 2: 1, 4: 2}
W_SID_CTRL_ARMRUN, W_CTRL_ARMWRST, W_CTRL_DISARM = 1 << 2, 1 << 13, 1 << 3
W_FFT_N = 0x80


def w_s0_max(b):
    return W_NPHYS // b // 2 - P.NCH


def w_if_mhz(s0, i, b):
    """流れの ch i の IF（INTERFACE 2.1、ナイキストゾーン 2）"""
    n = W_NPHYS // b
    return W_FS_MHZ - (s0 + i + (b - 1) / (2 * b)) * W_FS_MHZ / n


def default_settings_wide():
    wins = []
    for i in range(4):
        for s in range(NW):
            wins.append(dict(b=1, s0=0 if s == 0 else 4096, shift=7))
    return dict(kind="wide", tint=0.04096, cfg=0, fmt="f32", wins=wins)


def check_wide(st):
    """SET の後の照合（Wide）。b・shift はコアで 1 つ（流れ 0・1 にそろえて持つ）"""
    for i in range(4):
        a, b_ = st["wins"][NW * i], st["wins"][NW * i + 1]
        if a["b"] != b_["b"] or a["shift"] != b_["shift"]:
            raise ValueError(f"{'ABCD'[i]}: b・shift はコアで 1 つ")
        if a["b"] not in W_LB:
            raise ValueError(f"{'ABCD'[i]}.b は 1・2・4")
        for s, ws in enumerate((a, b_)):
            if a["b"] == 4 and s == 1:
                continue                         # B 4 の流れ 1 は空
            if not 0 <= ws["s0"] <= w_s0_max(a["b"]):
                raise ValueError(f"{'ABCD'[i]}{s}.s0 {ws['s0']}（B {a['b']} では 0〜{w_s0_max(a['b'])}）")


def wide_cfgs(st):
    """START の設定（流れごと）。B 4 の流れ 1 は active False（レコードが来ない）"""
    n_sum = check_tint(st["tint"])
    out = []
    for j, ws in enumerate(st["wins"]):
        b = ws["b"]
        act = not (b == 4 and j % NW == 1)
        out.append(dict(kind="slice", b=b, lb=W_LB[b], s0=ws["s0"], shift=ws["shift"], active=act,
                        nacc=n_sum * W_PL_NACC, n_sum=n_sum, pl_nacc=W_PL_NACC, bundle=1, g=0, ns=W_LB[b],
                        if_mhz=float(w_if_mhz(ws["s0"], 2048, b)), df_hz=W_FS_MHZ * 1e6 * b / W_NPHYS))
    return out


# ---- proj024: 2G-1（FULL の流れ 1 本、131072 ch、BIT_KIND 11）
G_NCH, G_FRAME = 131072, 16384
G_PL_NACC = BASE_BEATS // G_FRAME          # 160（PL のダンプ = BASE 10.24 ms）
G_DS_BEATS = 1                             # D_S（RTL の遅れ）。proj024 2e: FULL の DUMP_T はデータの T より 1 ビート後（axis_sel4 の 1 段）。RAW は 0
G_DF_HZ = W_FS_MHZ * 1e6 / (2 * G_NCH)     # 15,625 Hz（fs / N、N = 262144）


def g_if_mhz(c):
    """FULL の ch c の IF（ナイキストゾーン 2。Wide の w_if_mhz の B 1 と同じ形）"""
    return W_FS_MHZ - np.asarray(c, np.float64) * (G_DF_HZ / 1e6)


G_RING_MIB = 64                            # proj024 3e（西村さん、2026-10-18）: allocate の上限 64 MiB = 63 BASE ≒ 0.65 s（INTERFACE 4.1 の 1 s は 2G で読み替え）


def ring_mib_of(o, default):
    """--ring-mib（指定が無ければ bit ごとの既定）"""
    v = getattr(o, "ring_mib", None)
    return default if v is None else int(v)


def default_settings_g21():
    return dict(kind="g21", tint=0.04096, cfg=0, fmt="f32", src=0, shift=7, wins=[dict() for _ in range(4 * NW)])


def check_g21(st):
    if st.get("src") not in range(4):
        raise ValueError(f"src {st.get('src')}（A〜D = 0〜3）")
    if st.get("shift") not in range(16):
        raise ValueError(f"shift {st.get('shift')}（0..15）")


def g21_cfgs(st):
    """START の設定（窓 8 本の枠。A0 = FULL の流れ、残りは空）。送る i ↔ ch c = G_NCH − 1 − i（IF の昇順）"""
    n_sum = check_tint(st["tint"])
    out = [dict(kind="full", src=st["src"], shift=st["shift"], active=True, nacc=n_sum * G_PL_NACC, n_sum=n_sum, pl_nacc=G_PL_NACC,
                bundle=1, g=0, ns=0, nch=G_NCH, if_mhz=float(g_if_mhz(G_NCH - 1 - 2047)), df_hz=G_DF_HZ)]
    for _ in range(4 * NW - 1):
        out.append(dict(kind="none", active=False, bundle=0, n_sum=1, pl_nacc=0, nacc=0, ns=0, g=0, shift=0))
    return out


# ---- proj025: 2G-2（FULL の流れ 2 本 = コア 0・1 の s 0、65536 ch、BIT_KIND 10）
G2_NCH, G2_FRAME = 65536, 8192
G2_PL_NACC = BASE_BEATS // G2_FRAME        # 320（PL のダンプ = BASE 10.24 ms）
G2_DS_BEATS = 1                            # D_S。proj025 4d-2 の sim: FULL の DUMP_T はデータの T より 1 ビート後（axis_sel4 の 1 段、2G-1 と同じ）
G2_DF_HZ = W_FS_MHZ * 1e6 / (2 * G2_NCH)   # 31,250 Hz（fs / N、N = 131072）
G2_NCORE = 2
G2_WIN = [c * NW for c in range(G2_NCORE)] # 窓 A0 = コア 0 の FULL、B0 = コア 1 の FULL（窓 j = 2·コア ＋ s）


def g2_if_mhz(c):
    """2G-2 の FULL の ch c の IF（ナイキストゾーン 2。g_if_mhz と同じ形で df が 2 倍）"""
    return W_FS_MHZ - np.asarray(c, np.float64) * (G2_DF_HZ / 1e6)


class G2Geom:
    """proj027 3c: 多コアの 2G の形（2G-2・2G-4）。G22Backend・FakeG22Backend・Acq はこの表を読む（2G-2 の値は上の G2_* と同じ）。
    窓 j = 2·コア ＋ s（FULL は s 0）。raws はコアごとの RAW の流れの本数（2G-2 はコア 0 だけ、2G-4 は 4 コアとも = F-5）"""

    def __init__(self, name, kind, bit_kind, ncore, nch, frame, raws, ds=1):
        self.name, self.kind, self.bit_kind, self.ncore, self.nch, self.frame, self.raws, self.ds = name, kind, bit_kind, ncore, nch, frame, list(raws), ds
        self.pl_nacc = BASE_BEATS // frame             # PL のダンプ = BASE 10.24 ms
        self.df_hz = W_FS_MHZ * 1e6 / (2 * nch)        # fs / N
        self.win = [c * NW for c in range(ncore)]
        self.keys = [f"{'ABCD'[c]}0" for c in range(ncore)]

    def if_mhz(self, c):
        """FULL の ch c の IF（ナイキストゾーン 2）"""
        return W_FS_MHZ - np.asarray(c, np.float64) * (self.df_hz / 1e6)


G2_GEOM = G2Geom("2G-2", "g22", 10, G2_NCORE, G2_NCH, G2_FRAME, raws=[1, 0], ds=G2_DS_BEATS)
# proj027: 2G-4（BIT_KIND 3、FULL の流れ 4 本 = コア 0〜3 の s 0、32768 ch・FRAME 4096・PL_NACC 640）。D_S は 4d-2 の sim（D_eff 6,145 = 1 ＋ 1.5·4096）
G4_GEOM = G2Geom("2G-4", "g24", 3, 4, 32768, 4096, raws=[1, 1, 1, 1], ds=1)
G2_GEOMS = {g.kind: g for g in (G2_GEOM, G4_GEOM)}


def default_settings_g22(g=G2_GEOM):
    return dict(kind=g.kind, tint=0.04096, cfg=0, fmt="f32", src=list(range(g.ncore)), shift=[7] * g.ncore, wins=[dict() for _ in range(4 * NW)])


def check_g22(st, g=G2_GEOM):
    src, sh = st.get("src"), st.get("shift")
    if not isinstance(src, list) or len(src) != g.ncore or any(x not in range(4) for x in src):
        raise ValueError(f"src {src}（コアごとに A〜D = 0〜3）")
    if not isinstance(sh, list) or len(sh) != g.ncore or any(x not in range(16) for x in sh):
        raise ValueError(f"shift {sh}（コアごとに 0..15）")


def g22_cfgs(st, g=G2_GEOM):
    """START の設定（窓 8 本の枠。A0・B0（2G-4 は C0・D0 も）= コア 0・1（〜3）の FULL、残りは空）。送る i ↔ ch c = nch − 1 − i（IF の昇順）"""
    n_sum = check_tint(st["tint"])
    out = [dict(kind="none", active=False, bundle=0, n_sum=1, pl_nacc=0, nacc=0, ns=0, g=0, shift=0) for _ in range(4 * NW)]
    for c, j in enumerate(g.win):
        out[j] = dict(kind="full", core=c, src=st["src"][c], shift=st["shift"][c], active=True, nacc=n_sum * g.pl_nacc, n_sum=n_sum,
                      pl_nacc=g.pl_nacc, bundle=1, g=0, ns=0, nch=g.nch, frame=g.frame, ds=g.ds,
                      if_mhz=float(g.if_mhz(g.nch - 1 - 2047)), df_hz=g.df_hz)
    return out


def g22_tp_slots(src):
    """TP の欄（ADC）の割り付け {(コア, s): 欄}。s 0 = FULL の TP（SRC の ADC）、0xFF = コアの TP（コアの ADC = c）。コアの数は len(src)。
    同じ ADC の 2 本を 1 つの欄に混ぜない: コア c の FULL → src[c]（空いていれば。コアの順に）、その後にコア c のコアの TP → c（空いていれば）"""
    out, used = {}, set()
    nc = len(src)
    for key, slot in [((c, 0), src[c]) for c in range(nc)] + [((c, 0xFF), c) for c in range(nc)]:
        if slot not in used:
            out[key] = slot
            used.add(slot)
    return out


def win_key(j, nw=NW):
    i, w = divmod(j, nw)
    return f"{'ABCD'[i]}{w}"


def frame_beats(ns):
    return 4096 << (ns - 1)


def nacc_of(tint, ns):
    L = frame_beats(ns)
    n = int(round(tint * BEATS_PER_SEC / L))
    if n < 1 or (n * L) % G_BEATS or abs(n * L - tint * BEATS_PER_SEC) > 0.5:
        raise ValueError(f"tint {tint} s は 2.048 ms の倍数でない（NS {ns} の L = {L} ビート）")
    return n


NET_BUDGET_MBS = 30.0                      # INTERFACE 4.5・8. の 10: 1 ボードのネットワークの予算（MB/s = 1e6 B/s）


def net_mbs(st, nch_sent):
    """INTERFACE 4.5: ネットワークに出す SPEC の量（運転の形 float32 の中身。頭・TP は数えない）[MB/s]。nch_sent = 1 ダンプで送る ch の合計"""
    return nch_sent * 4 / float(st["tint"]) / 1e6


def check_net(st, nch_sent, budget_mbs=NET_BUDGET_MBS):
    """INTERFACE 4.5: float32 でも予算に入らない tint は SET で断る（PL は 10.24 ms のまま。tint を延ばせば入る）。
    budget_mbs ≦ 0 で照らさない（陽性対照・試験用。specd の --net-budget-mbs 0）。fmt u64・both は試験の形なので float32 の量で照らす"""
    if budget_mbs is None or budget_mbs <= 0:
        return
    r = net_mbs(st, nch_sent)
    if r > budget_mbs:
        base = BASE_BEATS / BEATS_PER_SEC
        n = 1
        while net_mbs(dict(tint=n * base), nch_sent) > budget_mbs:
            n += 1
        raise ValueError(f"tint {st['tint']} s では float32 で {r:.1f} MB/s（予算 {budget_mbs:g} MB/s を越える。INTERFACE 4.5）。"
                         f"この構成の tint の最小は {n * base:.5f} s")


def check_tint(tint):
    """proj021 2-3b: tint は BASE（10.24 ms）の倍数（INTERFACE 5.1）。戻り値 n_sum"""
    b = tint * BEATS_PER_SEC
    n = int(round(b / BASE_BEATS))
    if n < 1 or abs(n * BASE_BEATS - b) > 0.5:
        raise ValueError(f"tint {tint} s は 10.24 ms の倍数でない（INTERFACE 5.1）")
    return n


class Bundler:
    """proj021 2-3b: 1 窓の束ね（INTERFACE 5.1）。PL のダンプ（BASE ごと）を n_sum 個ずつ u64 で足す。
    m = round(DUMP_T / BASE)・r = DUMP_T − m·BASE（1 回の RUN で一定 ±1 のはず）・束 jb = m // n_sum。
    束が揃う条件: n_sum 個の m が jb·n_sum から続いている・DUMP_N がどれも pl_nacc・DUMP_CFG が同じ。欠けた束は丸ごと捨てる
    proj036: fast（s45fast）を渡すと、n_sum ≧ 2 の LazyRec（リングの上のレコード）を C で器へ写す・足す（PL の CRC も同じなめで照らす）。
    器は窓ごとに 1 つで使い回す（束を返した周のうちに記録を作るので足りる）。CRC が合わない 1 本を含む束は丸ごと捨てる（理由 "CRC"）
    SpW8 M5b（ADR 0029）: f32 = True で SpW の f32 のダンプを double の器 self.buf に足す（n_sum 1 でも器へ。束の値は float64 の配列）。
    LazyRec は fast.spw_acc（CRC・負か有限でない値の数え）、ndarray（偽物・写したレコード。u64 の配列なら f32 の bit として読む）は numpy で。
    負か有限でない値を含む束は丸ごと捨てる（理由 "値"）"""

    def __init__(self, n_sum, pl_nacc, fast=None, posctl=0, f32=False):
        self.n_sum, self.pl_nacc = n_sum, pl_nacc
        self.fast, self.posctl = fast, posctl
        self.f32 = f32
        self.buf = None
        self.crc_bad = 0              # proj036: PL の CRC が合わなかった 1 本の数
        self.val_bad = 0              # SpW8 M5b: 中身に負か有限でない値があった 1 本の数
        self.r0 = None
        self.r_bad = 0
        self.dead = False             # r が動いた（以後この RUN では束ねない）
        self.jb0 = None
        self.drop = 0                 # 捨てた束
        self.drop_why = {}
        self.cur = None

    def _close(self, why):
        if self.cur is not None:
            self.drop += 1
            self.drop_why[why] = self.drop_why.get(why, 0) + 1
            out = (self.cur["jb"], why, len(self.cur["ms"]))
            self.cur = None
            return out
        return None

    def add(self, m, spec):
        """戻り値 (できた束 (meta, u64 の和) または None, 捨てた束 (jb, 理由, 持っていた数) または None)"""
        t = int(m["t"])
        mi = (t + BASE_BEATS // 2) // BASE_BEATS
        r = t - mi * BASE_BEATS
        if self.dead:
            return None, None
        if self.r0 is None:
            self.r0 = r
        elif abs(r - self.r0) > 1:
            self.r_bad += 1
            self.dead = True
            return None, self._close("r") or (mi // self.n_sum, "r", 0)     # 束の途中でなくても ERROR の EVENT を出す
        jb = mi // self.n_sum
        if self.jb0 is None:
            self.jb0 = jb
        dropped = None
        if self.cur is not None and self.cur["jb"] != jb:
            dropped = self._close("欠け")
        bad = int(m["n"]) != self.pl_nacc
        lazy = not isinstance(spec, np.ndarray) and hasattr(spec, "crc_exp")
        if self.f32:
            return self._add_f32(m, spec, mi, jb, bad, lazy, dropped)
        crc_bad = False
        if lazy and self.n_sum > 1:                # proj036: リングの上から C で器へ（写さない・numpy を通さない）
            first = self.cur is None
            if first and (self.buf is None or self.buf.size != spec.n):
                self.buf = np.empty(spec.n, np.uint64)
            crc_bad = self.fast.ring_acc(spec, self.buf, first, self.posctl) != spec.crc_exp
            if crc_bad:
                self.crc_bad += 1
        if self.cur is None:
            if lazy and self.n_sum > 1:
                acc = self.buf
            else:
                acc = spec if (self.n_sum == 1 and lazy) else np.array(spec, dtype=np.uint64)   # proj029 2: LazyRec は写さない
            self.cur = dict(jb=jb, ms=[mi], acc=acc, m=dict(m), sat=int(m["sat"]),
                            flags=int(m["flags"]), h=int(m["h"]), n=int(m["n"]), bad="N" if bad else None)
            if crc_bad:
                self.cur["bad"] = "CRC"
        else:
            c = self.cur
            if mi != c["ms"][-1] + 1:
                c["bad"] = c["bad"] or "順"
            if int(m["cfg"]) != int(c["m"]["cfg"]):
                c["bad"] = c["bad"] or "CFG"
            if bad:
                c["bad"] = c["bad"] or "N"
            if crc_bad:
                c["bad"] = c["bad"] or "CRC"
            c["ms"].append(mi)
            if not (lazy and self.n_sum > 1):
                c["acc"] += spec
            c["sat"] += int(m["sat"]); c["flags"] |= int(m["flags"]); c["h"] |= int(m["h"]); c["n"] += int(m["n"])
        c = self.cur
        if len(c["ms"]) < self.n_sum:
            return None, dropped
        if c["bad"] or c["ms"][0] != jb * self.n_sum:
            d2 = self._close(c["bad"] or "頭")
            return None, dropped or d2
        mm = dict(c["m"])
        mm.update(k=jb - self.jb0, n=c["n"], sat=c["sat"], flags=c["flags"], h=c["h"])
        self.cur = None
        return (mm, c["acc"]), dropped

    def _add_f32(self, m, spec, mi, jb, bad, lazy, dropped):
        """SpW8 M5b: add の f32 の道（器はいつも self.buf）"""
        first = self.cur is None
        crc_bad = val_bad = False
        if lazy:
            n = 2 * spec.n
            if self.buf is None or self.buf.size != n:
                if not first:
                    raise ValueError("束の途中でダンプの長さが変わった")
                self.buf = np.empty(n, np.float64)
                self.sacc = self.fast.SpwAcc(self.buf)   # 器の番地を先に引く（1 本ごとに引くと 1 本 100 µs、ボード）
                self.bufp = self.sacc.p
            crc, nbad = self.sacc.add(spec, first, self.posctl)
            crc_bad, val_bad = crc != spec.crc_exp, nbad != 0
        else:
            x = np.asarray(spec)
            if x.dtype == np.uint64:
                x = x.view(np.float32)
            if self.buf is None or self.buf.size != x.size:
                if not first:
                    raise ValueError("束の途中でダンプの長さが変わった")
                self.buf = np.empty(x.size, np.float64)
                self.bufp = self.buf.ctypes.data
            val_bad = bool(np.any(~np.isfinite(x)) or np.any(np.signbit(x)))
            if first or (self.posctl & 1):
                self.buf[:] = x
            else:
                self.buf += x
        self.crc_bad += crc_bad
        self.val_bad += val_bad
        why = "CRC" if crc_bad else "値" if val_bad else "N" if bad else None
        if first:
            self.cur = dict(jb=jb, ms=[mi], acc=self.buf, m=m, sat=int(m["sat"]),
                            flags=int(m["flags"]), h=int(m["h"]), n=int(m["n"]), bad=why)
        else:
            c = self.cur
            if mi != c["ms"][-1] + 1:
                c["bad"] = c["bad"] or "順"
            if int(m["cfg"]) != int(c["m"]["cfg"]):
                c["bad"] = c["bad"] or "CFG"
            c["bad"] = c["bad"] or why
            c["ms"].append(mi)
            c["sat"] += int(m["sat"]); c["flags"] |= int(m["flags"]); c["h"] |= int(m["h"]); c["n"] += int(m["n"])
        c = self.cur
        if len(c["ms"]) < self.n_sum:
            return None, dropped
        if c["bad"] or c["ms"][0] != jb * self.n_sum:
            d2 = self._close(c["bad"] or "頭")
            return None, dropped or d2
        mm = c["m"]                                # f32 の道の m は poll_win が 1 本ごとに作る辞書（写さずに使う）
        mm.update(k=jb - self.jb0, n=c["n"], sat=c["sat"], flags=c["flags"], h=c["h"], accp=self.bufp)   # accp: 器の番地（記録の C の道）
        self.cur = None
        return (mm, c["acc"]), dropped

    def stop(self):
        return self._close("STOP")


def g_of(ns):
    return 5 if ns >= 7 else 4


# ================================================================ 時刻（timebase の式を、確かめは 1 秒に 1 回に分けて）
def _b2ns_i(d):
    """_b2ns の Python の整数の版（SpW8 M5b: スカラーに np.where を通すと 1 回 63 µs、ボード）"""
    return (d * 125 + 16) // 32 if d >= 0 else -((-d * 125 + 16) // 32)


def _b2ns(d):
    """timebase.beats_to_ns と同じ（最近接に丸める。負は対称）。numpy の配列も可"""
    d = np.asarray(d, np.int64)
    return np.where(d >= 0, (d * 125 + 16) // 32, -((-d * 125 + 16) // 32))


class Clock:
    """timebase.Timebase.sample_utc_ns と同じ式。check()（PPS の照合、MMIO を数語読む）は poll で 1 秒に 1 回だけ打ち、
    落ちたら ok = False（記録に H_NOTIME、utc_ns = 0）。錨を打ち直すまで戻らない"""

    def __init__(self, tb, win_delay):
        self.tb, self.wd = tb, win_delay
        self.ok = tb is not None and tb._anchor is not None
        self.err = None
        self.t_next = 0.0

    def poll(self):
        if self.tb is None or not self.ok or time.time() < self.t_next:
            return
        self.t_next = time.time() + 1.0
        try:
            self.tb.check()
        except Exception as e:                  # TimebaseError
            self.ok, self.err = False, str(e)

    def utc_ns(self, beat, ns=None, adc=0):
        if not self.ok:
            return 0
        a, c = self.tb._anchor, self.tb.cal
        t = a["utc_sec"] * 10**9 + _b2ns_i(int(beat) - a["stamp"]) + int(round(c["pps_det_ns"] or 0))   # pps_det は足す（2026-10-21、test_cal_b.py）
        v = c["adc_to_core_ns"]
        t -= int(round((v.get(adc) if isinstance(v, dict) else v) or 0))
        if ns is not None and ns in self.wd:
            t -= int(round(self.wd[ns] * 125 / 32))
        return t

    def utc_ns_arr(self, beats, adc=0):
        """utc_ns(beat, None, adc) を配列で（TP の区切り）"""
        a, c = self.tb._anchor, self.tb.cal
        v = c["adc_to_core_ns"]
        off = a["utc_sec"] * 10**9 + int(round(c["pps_det_ns"] or 0)) - int(round((v.get(adc) if isinstance(v, dict) else v) or 0))
        return off + _b2ns(np.asarray(beats, np.int64) - a["stamp"])

    def beat_of_utc_ns(self, utc_ns):
        a = self.tb._anchor
        p = int(round(self.tb.cal["pps_det_ns"] or 0))      # beat_utc_ns の逆（pps_det を足した分を戻す）
        return a["stamp"] + ((int(utc_ns) - a["utc_sec"] * 10**9 - p) * 32) // 125


# ================================================================ TP のリングの読み手（記録を溜めず、TP_FLUSH ごとに渡す）
def make_tp_reader(S):
    class TpStream(S.TpReader):
        def __init__(self, sp, tp_n, run_f0):
            super().__init__(sp, tp_n, run_f0)
            self.buf = np.zeros(4 * S.TP_DEPTH, P.TP_E)
            self.n = 0
            self.n_ovr = 0
            self.total = 0
            self.overflow = 0         # 手元の箱（4 × 512 個）が溢れて捨てた区切り（flush が 2 秒来ない。0 のはず）
            self.rec_lost = 0         # proj021 2-3a: 落ちた TP のレコードの数（個の番号の飛びを K で割って切り上げた見積り）

        def feed(self, seq, n, pay, k):
            """proj021 2-3a: TP のレコード（type 2）の個を受ける。seq = 最初の個の番号（TP_WP の数え）、pay = u64 × 2·n…
            個 = {和 u64, [31:0] F0 の下位・[55:32] フレーム数・[63:56] FLAGS}（AXI4-Lite の TP のリングと同じ 16 バイト）"""
            if self.wp is not None:
                g = (seq - self.wp) & 0xFFFFFFFF
                if g >= 1 << 31:
                    return                    # 古い（前の RUN の残り）
                if g and self.started:
                    self.lost += g
                    self.rec_lost += -(-g // k)
            self.wp = (seq + n) & 0xFFFFFFFF
            v = pay[:2 * n].tolist()                  # numpy の要素を 1 個ずつ int にするより速い
            for i in range(n):
                x = v[2 * i + 1]
                self._take(v[2 * i], x & 0xFFFFFFFF, x >> 56, (x >> 32) & 0xFFFFFF)

        def _take(self, tsum, f0lo, fl, nfr):
            if not self.started:
                if (fl & TPF_RUN) and f0lo == (self.run_f0 & 0xFFFFFFFF):
                    self.started = True
                    f0 = self.run_f0
                else:
                    self.pre += 1
                    return
            else:
                exp = self.last_f0 + self.last_nfr
                f0 = exp + ((f0lo - (exp & 0xFFFFFFFF) + (1 << 31)) % (1 << 32)) - (1 << 31)
                if f0 != exp:
                    self.bad_seq += 1
                if fl & ~TPF_OVR:
                    self.bad_flag += 1
            if fl & TPF_OVR:
                self.n_ovr += 1
            if nfr != self.tp_n:
                self.bad_nfr += 1
            self.last_f0, self.last_nfr = f0, nfr
            if self.n < len(self.buf):
                # t_beat はフレームの番号（flush でビートに直す）・utc_ns は flush で書く。1 つの組で書く（欄ごとに 4 回書くと 1 個 ≒ 20 µs、ボード。SpW8 M5b）
                self.buf[self.n] = (f0, 0, tsum, nfr, fl)
                self.n += 1
            else:
                self.overflow += 1
            self.total += 1
    return TpStream


# ================================================================ 実機
REC_ALL, REC_SNAP = 1, 4
TP_REC_CTRL, TP_REC_K = 0x11C, 10           # proj021 2-2b: TP のレコード（[0] EN・[12:8] K）。TP_FLUSH（40 個）は手元で束ねる
TYPE_SPEC, TYPE_TP, TYPE_SNAP = 1, 2, 4


def rec_meta(hw):
    """レコードの頭 w1..w6（INTERFACE 4.4）→ 今の meta と同じ鍵"""
    w = hw.tolist() if hasattr(hw, "tolist") else [int(x) for x in hw]    # SpW8 M5b: tolist は 1 回 3 µs（int() を 7 回は 27 µs、ボード）
    return dict(seq=w[1] & 0xFFFFFFFF, k=w[1] >> 32, f0=w[2] & ((1 << 48) - 1), t=w[3], h=(w[4] >> 48) & 0xFFFF,
                n=w[5] & 0xFFFFFFFF, sat=w[5] >> 32, cfg=w[6] & 0xFFFFFFFF, flags=w[6] >> 32)


class HwBackend:
    def __init__(self, opts, log):
        self.o, self.log = opts, log
        self.running = False
        if getattr(opts, "read", "ring") != "ring":
            raise RuntimeError("proj021 2-2d: 読み口はリングだけ（--read axi の道は外した。仮の読み窓の無い bit）")
        self.use_ring = True
        self.ring = None
        self.ring_crc = 0
        self.stall_at = getattr(opts, "posctl_ring_stall", 0.0)
        self.n_pump = 0
        self.lazy_wins = set()                     # proj029 2: SPEC を写さずに渡す窓（--fast-ring・n_sum 1 の FULL。START で決める）
        self.n_mat = 0                             # proj029 2: 周の終わりに写した LazyRec の数（使い切れなかった分）

    def release(self):
        """proj029 2: 周の終わり。列に残った LazyRec（その周で使い切れなかった分）を写して CRC を照らし、リングの R を進める。
        **R を進めた後にリングの上を指すものを残さない**（PL が上書きしてよい場所になる）"""
        rg = self.ring
        if rg is None or not rg.hold:
            return
        for d in self.q:
            if not any(not isinstance(x[2], np.ndarray) for x in d):
                continue
            keep = []
            for seq, hw, pay in d:
                if not isinstance(pay, np.ndarray):
                    pay, ok = pay.materialize()
                    self.n_mat += 1
                    if not ok:
                        self.ring_crc += 1
                        continue
                keep.append((seq, hw, pay))
            d.clear()
            d.extend(keep)
        rg.release()

    def _usr_access(self):
        """YATSUGATAKE M5b: 載せた .bit の USR_ACCESS（16 進 8 桁、焼いていなければ none、読めなければ ?）。FPGA の中からは読まない（.bit の構成の流れから）"""
        try:
            return bitinfo.fmt(bitinfo.usr_access(self.o.bitfile))
        except (OSError, bitinfo.BitError):
            return "?"

    def _setup_lmx(self):
        """proj019: LMX の VCO・出力の強さを動かす（既定は specd の --lmx-pwr 3、櫛 n × 163.84 MHz を下げる）。出力 491.52 は同じ。
        setup_clocks の後、Overlay() の前に呼ぶ。SAM45-Wide も同じ（YATSUGATAKE: Wide の裏が写し漏れて 31 のままだった）"""
        self.lmx = None
        chdiv = getattr(self.o, "lmx_chdiv", 16)
        pwr = getattr(self.o, "lmx_pwr", None)
        if chdiv != 16 or pwr is not None:
            import extref
            self.lmx = extref.rewrite_lmx(chdiv, pwr)

    def _lmx_ids(self):
        return dict(lmx_vco=f"{self.lmx['vco_mhz']:.2f}" if self.lmx else "7864.32",
                    lmx_pwr=str(self.lmx.get("outa_pwr", 31)) if self.lmx else "31")

    def open(self):
        import spectrometer as S
        import timetest as T
        import window as W
        import timebase as TB
        self.S, self.T, self.W, self.TB = S, T, W, TB
        from pynq import Overlay
        import xrfdc                               # Overlay() より前に import する（VERSIONS.md）
        S.setup_clocks(self.o.clkin, self.o.ref)
        self._setup_lmx()
        self.ol = Overlay(self.o.bitfile)
        if not isinstance(self.ol.rfdc, xrfdc.RFdc):
            raise RuntimeError("RFDC に xrfdc のドライバが当たっていない")
        S.check_tiles(self.ol.rfdc, 2)
        time.sleep(self.o.settle)
        ns_list = [1] * (4 * NW)
        self.tc, self.wms, self.wins, self.full = T.open_all(self.ol, ns_list)   # 照合は自己記述（s45core.discover。open_all の中）
        import s45core as SC
        self.cores, _ = SC.discover(self.ol)
        for wm in self.wms:
            prm = int(wm.read(W.A_BASE + S.R_TP_PARAM)) & 0xFFFFFFFF
            if prm != S.TP_PARAM_EXPECT:
                raise RuntimeError(f"TP_PARAM {prm:08x}（期待 {S.TP_PARAM_EXPECT:08x}）")
        self.tc.configure(src=self.o.path, tol=1)
        self.tb = TB.Timebase(self.tc, path=self.o.path, log=self.log)
        self.TpStream = make_tp_reader(S)
        c0 = self.cores[0]
        self.ids = dict(win=f"{self.wins[0].rd(W.R_ID):08x}", adc=f"{c0.if_id:08x}", time=f"{self.tc.rd(0x00):08x}",   # proj021 2-2d: 載っている time_core の IF_ID（BIT_REV 1 / 2）
                        proj=f"{c0.proj:08x}",
                        usr=self._usr_access(),                                   # YATSUGATAKE M5b: 載せた .bit の USR_ACCESS（commit）
                        **self._lmx_ids())
        self.clock = Clock(None, TB.WIN_DELAY_BEATS)
        if self.use_ring:
            self._open_ring()
        self.ids["read"] = "ring" if self.use_ring else "axi"
        self.ids["tcal"] = self.tb.cal_state                      # ADR 0023: board（ボードの較正）/ provisional（開発の値）
        self.ids["board"] = (self.tb.board or {}).get("id", "-")  # ADR 0025: TP の較正ファイルを照らす
        self.bit_kind = (self.cores[0].if_id >> 16) & 0xFF        # proj021 2-3c: v2 の SPEC の bit_kind
        self.anchor()

    # ---- proj021 2-3a: リング ----
    def _open_ring(self):
        import plring as PR
        import s45core as SC
        self.SC = SC
        bad = [c.name for c in self.cores if (c.caps & 7) != 7]
        if bad:
            raise RuntimeError(f"CAPS の [0]〜[2]（SPEC・TP・SNAP のレコード）が無いコア {bad}。2-2c 以降の .bit を")
        rip = getattr(self.ol, "s45_ring_0", None)
        if rip is None:
            raise RuntimeError("ol.s45_ring_0 が無い（2-2a 以降の .bit ではない）")
        self.ring = PR.Ring(rip.mmio, ring_mib_of(self.o, 32) << 20)
        self.ring.enable(True)
        self.jmap = {(self.cores[c.adc].adc, c.widx): j for j, c in enumerate(self.wins)}   # レコードの core = CORE_PORT の ADC
        self.amap = {c.adc: i for i, c in enumerate(self.cores)}
        self.q = [collections.deque() for _ in self.wins]
        fs = SC.snap_stream(self.cores)            # proj021 2-5: SNAP は RAW の流れ（2-4 までは FULL）
        self.fkey = (fs.core.adc, fs.s)
        self.log(f"リング: BASE {self.ring.base:#x} / SIZE {self.ring.size}（範囲の invalidate {'あり' if self.ring.bo_sync else 'なし'}）")

    def _rec_off(self):
        """REC_CTRL・TP_REC_CTRL を 0（窓・FULL・4 ADC）"""
        SC = self.SC
        for c in self.wins:
            c.wr(SC.S_REC_CTRL, 0)
        self.full.wr(SC.S_REC_CTRL, 0)
        for wm in self.wms:
            wm.write(TP_REC_CTRL, TP_REC_K << 8)

    def _drain(self):
        self.ring.read()
        for d in self.q:
            d.clear()
        self.ring.release()                        # proj029 2: 列を空にしたので、写していないレコードも残っていない

    def _posctl_stall(self):
        """陽性対照（--posctl-ring-stall）: RUN の 100 周目にリングを stall_at 秒読まない。pump を上書きする裏（2G）も呼ぶ
        （2G-4 の M6 で、G21・G22 の pump がこれを持たず、陽性対照が黙って空振りしていた）"""
        if self.stall_at and self.n_pump == 100:
            self.log(f"陽性対照: リングを {self.stall_at} 秒読まない")
            time.sleep(self.stall_at)

    def pump(self):
        """1 周の頭に 1 回: リングを [R, W) まで読み、SPEC は窓ごとの列へ、TP は TpStream へ"""
        if not self.use_ring:
            return 0
        self.n_pump += 1
        self._posctl_stall()
        t0 = time.perf_counter()
        recs = self.ring.read()
        t1 = time.perf_counter()
        for core, s, seq, hw, pay, crc_ok, tail_ok in recs:
            if not (crc_ok and tail_ok):
                self.ring_crc += 1
                continue
            ty = int(hw[0]) >> 40 & 0xFF
            if ty == TYPE_SPEC:
                j = self.jmap.get((core, s))
                if j is not None:
                    self.q[j].append((seq, hw, pay))
            elif ty == TYPE_TP and s == 0xFF and core in self.amap and self.running:   # 2-2d: FULL の TP（s = FULL の流れ）は使わない
                self.tps[self.amap[core]].feed(seq, int(hw[5]) & 0xFFFFFFFF, pay, TP_REC_K)
        self.last_pump = (t1 - t0, time.perf_counter() - t1)      # 遅い周の内訳（リングの読み・振り分け）
        return len(recs)

    def ring_stat(self):
        if self.ring is None:
            return None
        r = self.ring.regs()
        return dict(w=r["w"], r=r["r"], drop=r["drop"], rec=r["rec"], peak=r["peak"], err=r["err"], crc=self.ring_crc, mat=self.n_mat,
                    tp_rec_lost=sum(t.rec_lost for t in getattr(self, "tps", [])))

    def close(self):
        if self.ring is None:
            return
        try:
            self._rec_off()
        finally:
            self.ring.close(())
            self.ring = None

    def anchor(self):
        try:
            a = self.tb.anchor()
            self.clock = Clock(self.tb, self.tb.win_delay)
            self.log(f"錨: UTC {a['utc_sec']} 秒 = スタンプ {a['stamp']}（EPOCH {a['epoch']}）")
            return True, None
        except Exception as e:
            self.clock = Clock(None, self.TB.WIN_DELAY_BEATS)
            self.log(f"錨を打てない: {e}")
            return False, str(e)

    def now_beat(self):
        return self.tc.t()

    def grid_after(self, beat):
        """proj021 2-3b: START_AT（WRST・RUN・TP_ARM）は T の tint の倍数（INTERFACE 5.1。tint は BASE = 5G の倍数なので G の格子にも乗る）"""
        q = getattr(self, "tint_beats", G_BEATS)
        return -(-int(beat) // q) * q

    def start(self, st, at_beat, force):
        """WRST（格子の点で一斉）→ N_ACC・SHIFT・TP_N → 窓と TP 4 本を格子の START_AT で同時に ARM。戻り値 START_AT"""
        T, W = self.T, self.W
        if self.clock.ok:
            try:
                self.tb.check()
            except Exception as e:                 # IDLE の間は Clock.poll が回らないので、ここで初めて分かることがある
                self.clock.ok, self.clock.err = False, str(e)
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.disarm()
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        bb = {c.base_beats for c in self.cores}
        if bb != {BASE_BEATS}:
            raise RuntimeError(f"コアの BASE_BEATS {bb}（{BASE_BEATS} を期待）")
        self.cfgs = []
        for j, c in enumerate(self.wins):
            ws = st["wins"][j]
            ns = ws["ns"]
            _, k, dphi, ns_, if_act = W.window_params(ws["if_mhz"], 512.0 / (1 << ns))
            c.ns, c.L = ns, frame_beats(ns)
            c.wr(W.R_WK, k); c.wr(W.R_WDPHI, dphi); c.wr(W.R_WNS, ns_)
            c.wr(T.R_CFG, st["cfg"])
            c.wr(W.R_CTRL, T.CTRL_ARM_WRST)
            c.want = (k, dphi, ns_)
            bund = int(ws.get("bundle", 1))
            self.cfgs.append(dict(if_mhz=if_act, ns=ns, shift=ws["shift"], nacc=nacc_of(st["tint"], ns), g=g_of(ns),
                                  bundle=bund, n_sum=check_tint(st["tint"]) if bund else 1,
                                  pl_nacc=BASE_BEATS // c.L if bund else nacc_of(st["tint"], ns)))
        sa_w = self.grid_after(self.now_beat() + BEATS_PER_SEC // 2)
        T.arm_tc(self.tc, self.wins, self.full, self.wms, sa_w)
        self._wait_fired(5.0)
        time.sleep(0.01)
        ws_ = []
        for c in self.wins:
            while c.rd(W.R_CTRL) & (1 << 4):
                time.sleep(0.001)
            cur = c.rd(T.R_WCUR)
            k, dphi, ns_ = c.want
            if (cur & 31) != k or ((cur >> 8) & 15) != ns_ or c.rd(W.R_WCUR_DPHI) != dphi:
                raise RuntimeError(f"{c.name}: WRST の後の WCUR {cur:#x} が書いた値と違う")
            ws_.append(c.rd(T.R_WSTART))
        for i in range(4):
            wi = [ws_[j] for j in range(len(self.wins)) if self.wins[j].adc == i]
            if len(set(wi)) != 1:
                raise RuntimeError(f"{ADC_NAMES[i]}: 窓の WSTART が揃っていない {wi}")
        for c, cf in zip(self.wins, self.cfgs):
            c.wr(W.R_NACC, cf["pl_nacc"]); c.wr(W.R_NDUMP, 0); c.wr(W.R_SHIFT, cf["shift"])   # proj021 2-3b: 束ねる窓は BASE
        for wm in self.wms:
            wm.write(W.A_BASE + T.RA_TP_N, TP_N)
        if self.use_ring:                          # proj021 2-3a: 窓は ALL・TP は K 個 / レコード。前の残りは読み捨てる
            for c in self.wins:
                c.wr(self.SC.S_REC_CTRL, REC_ALL)
            for wm in self.wms:
                wm.write(TP_REC_CTRL, (TP_REC_K << 8) | 1)
            self._drain()
        sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        T.arm_all(self.tc, self.wins, self.full, self.wms, sa, tp=True, with_full=False)
        self.sa = sa
        self.armed = True
        return sa

    def _wait_fired(self, timeout):
        t_e = time.time() + timeout
        while not self.tc.status()["fired"]:
            if time.time() > t_e:
                raise RuntimeError("予約の発火が来ない")
            time.sleep(0.01)

    def fired(self):
        return bool(self.tc.status()["fired"])

    def begin(self):
        """発火の後: RUN_T の照合・SEQ と TP の読み手の起点・錨の組（TANCH）"""
        S, T, W = self.S, self.T, self.W
        runts = [c.rd64(c.r["run_t"]) for c in self.wins] + [T.tp_run_t(wm) for wm in self.wms]
        bad = [i for i, t in enumerate(runts) if t != self.sa + 1]
        for c, cf in zip(self.wins, self.cfgs):
            rs = c.rd(T.R_RUN_SHIFT)
            if rs != cf["shift"]:
                raise RuntimeError(f"{c.name}: RUN_SHIFT {rs}（書いた値 {cf['shift']}）")
        self.seq = [c.rd(W.R_SEQ) for c in self.wins]
        self.tps = []
        self.anch = []
        for wm in self.wms:
            tp = _WinTp(wm, W.A_BASE)
            tf0 = tp.rd(S.R_TP_F0_LO) | (tp.rd(S.R_TP_F0_HI) << 32)
            self.tps.append(self.TpStream(tp, TP_N, tf0))
            self.anch.append(self._tanch(wm))
        self.gap0 = [int(wm.read(W.A_BASE + T.RA_GAP)) for wm in self.wms]
        self.running = True
        return dict(run_t_bad=bad)

    def _tanch(self, wm, timeout=0.5):
        W, T = self.W, self.T
        wm.write(W.A_BASE + T.RA_TP_CTRL, T.TP_ANCH)
        t_e = time.time() + timeout
        while not (int(wm.read(W.A_BASE + T.RA_ANCH_ST)) & 2):
            if time.time() > t_e:
                raise RuntimeError("TANCH が残らない")
            time.sleep(0.001)
        af = int(wm.read(W.A_BASE + T.RA_ANCH_F)) | (int(wm.read(W.A_BASE + T.RA_ANCH_F + 4)) << 32)
        at = int(wm.read(W.A_BASE + T.RA_ANCH_T)) | (int(wm.read(W.A_BASE + T.RA_ANCH_T + 4)) << 32)
        return af, at

    def poll_win(self, j):
        """窓 j に閉じたダンプがあれば (メタ, uint64 の 4096 個の FFT の順, 読み落とした数) を返す。無ければ None"""
        W = self.W
        if self.use_ring:
            q = self.q[j]
            while q:
                seq, hw, pay = q.popleft()
                d = (seq - self.seq[j]) & 0xFFFFFFFF
                if d == 0 or d >= 1 << 31:
                    continue                       # 前の RUN の残り・同じ SEQ
                self.seq[j] = seq
                return rec_meta(hw), pay, d - 1
            return None
        raise RuntimeError("proj021 2-2d: 仮の読み窓の道は外した")

    def poll_tp(self, i):
        if not self.use_ring:
            self.tps[i].poll()                     # ring: pump が個を渡している
        return self.tps[i]

    def tp_time(self, i, f):
        af, at = self.anch[i]
        return at + (f - af) * 512

    def snap(self, adc, n, nacc, timeout=5.0):
        """全帯域コア（spec_core_0）を ADC adc につないで N_ACC = nacc・N_DUMP = n で走らせ、ダンプごとの最初のフレームの
        生サンプル 8192 個を読む（IDLE のときだけ。窓・TP の RUN には触らない: specd は全帯域コアを RUN に入れていない）。
        戻り値 [(meta, int16 の 8192 個)]。SNAP_F ≠ DUMP_F0（別のフレームを読んだ）・読む間に閉じたものは読み直す"""
        return self._snap_ring(adc, n, nacc, timeout)     # proj021 2-2d: 仮の読み窓の道は外した

    def _snap_ring(self, adc, n, nacc, timeout):
        """proj021 2-3a: FULL の流れを REC_CTRL = ALL | SNAP・N_DUMP = n で走らせ、SNAP のレコード（type 4）を n 個集める。
        2-5: RAW の流れ（SNAP のレコードだけを出す。SNAP の bit は意味が無いが害も無い）でも同じ手順。
        上書きの見張りは PL（2-2c の snap_ok）。ここは SEQ の飛び・DUMP_K・CRC を見る"""
        S, T, SC = self.S, self.T, self.SC
        full = self.full
        T.select_full(self.wms, full, adc)
        full.wr(SC.S_REC_CTRL, 0)
        self._drain()
        full.wr(S.R_NACC, nacc)
        full.wr(S.R_NDUMP, n)
        full.wr(SC.S_REC_CTRL, REC_ALL | REC_SNAP)
        full.wr(S.R_CTRL, S.CTRL_CLR | S.CTRL_RUN)
        out = []
        last = None
        t_end = time.time() + timeout + n * nacc * 2e-6
        try:
            while len(out) < n:
                if time.time() > t_end:
                    raise RuntimeError(f"SNAP: {len(out)}/{n} 個で時間切れ（REC_LATE {full.rd(SC.S_REC_LATE)}・リングの DROP {self.ring.regs()['drop']}）")
                for core, s, seq, hw, pay, crc_ok, tail_ok in self.ring.read():
                    if (core, s) != self.fkey or (int(hw[0]) >> 40 & 0xFF) != TYPE_SNAP:
                        continue
                    if not (crc_ok and tail_ok):
                        raise RuntimeError(f"SNAP: CRC・尾の不一致（SEQ {seq}）")
                    m = rec_meta(hw)
                    if last is not None and seq != (last + 1) & 0xFFFFFFFF:
                        raise RuntimeError(f"SNAP: ダンプを読み落とした（SEQ {last} → {seq}。every を長く）")
                    if m["k"] != len(out):
                        raise RuntimeError(f"SNAP: DUMP_K {m['k']}（{len(out)} であるべき）")
                    last = seq
                    out.append((m, pay.view(np.int16).copy()))
                time.sleep(0.0005)
        finally:
            full.wr(S.R_CTRL, S.CTRL_STOP)
            full.wr(SC.S_REC_CTRL, 0)
        return out

    def disarm(self):
        T = self.T
        T.disarm_all(self.wins, self.full, self.wms)

    def stop(self):
        W = self.W
        if not self.running:
            # ARMED のまま止める: コアの予約は time_core の取り消しでは消えない（timetest.disarm_all の注意）。両方消し、TANCH は比べない
            self.disarm()
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            if self.use_ring:
                self._rec_off()
            return []
        for c in self.wins:
            c.wr(W.R_CTRL, W.CTRL_STOP)
        if self.use_ring:
            self.pump()                            # 止める前に閉じたぶんを TP に渡す（SPEC の残りは次の START で捨てる）
            self._rec_off()
        self.running = False
        out = []
        for i, wm in enumerate(self.wms):
            try:
                af1, at1 = self._tanch(wm)
                af, at = self.anch[i]
                gap1 = int(wm.read(self.W.A_BASE + self.T.RA_GAP))
                out.append(dict(adc=i, anch_dev=(at1 - at) - (af1 - af) * 512, gap=gap1 - self.gap0[i]))
            except Exception as e:
                out.append(dict(adc=i, err=str(e)))
        return out


class _WinTp:
    def __init__(self, mmio, base):
        self.m, self.b = mmio, base

    def rd(self, a):
        return int(self.m.read(self.b + a)) & 0xFFFFFFFF

    def block(self, base, nwords):
        i0 = (self.b + base) // 4
        return np.array(self.m.array[i0:i0 + nwords], dtype=np.uint32)


# ================================================================ 偽物（PL なし。同じ間隔・同じ形）
class FakeBackend:
    """T = (time.time() − t0)·256e6 のビート。ダンプは tint ごとに 8 窓、TP は 1.024 ms ごと。中身は乱数（k で変わる）"""

    def __init__(self, opts, log):
        self.o, self.log = opts, log
        self.running = False

    def open(self):
        import types
        self.t0 = time.time() - 100.0                # 偽の時刻: T = (time − t0)·256e6、UTC = t0 + T / 256e6
        self.ids = dict(win="fake", adc="fake", time="fake", tcal="fake", board="fake")
        rng = np.random.default_rng(1)
        self.base = rng.integers(1 << 40, 1 << 41, (4 * NW, P.NCH), dtype=np.uint64)
        tb = types.SimpleNamespace(cal=dict(pps_det_ns=0, adc_to_core_ns=0), check=lambda: None,
                                   _anchor=dict(utc_sec=int(self.t0), stamp=-int(round((self.t0 - int(self.t0)) * BEATS_PER_SEC))))
        self.clock = Clock(tb, {})
        if self.o.fake_notime:                       # 1PPS が無い（錨が打てない）実機の振る舞いを真似る
            self.clock = Clock(None, {})
            self.clock.err = "偽物: 1PPS なし（--fake-notime）"

    def anchor(self):
        return True, None

    def now_beat(self):
        return int((time.time() - self.t0) * BEATS_PER_SEC)

    def grid_after(self, beat):
        return -(-int(beat) // G_BEATS) * G_BEATS

    def start(self, st, at_beat, force):
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.cfgs = [dict(if_mhz=ws["if_mhz"], ns=ws["ns"], shift=ws["shift"], nacc=nacc_of(st["tint"], ws["ns"]), g=g_of(ws["ns"]),
                          bundle=0, n_sum=1, pl_nacc=nacc_of(st["tint"], ws["ns"]))      # 偽物は束ねない（ダンプ = tint）
                     for ws in st["wins"]]
        self.cfg = st["cfg"]
        self.tint_beats = int(round(st["tint"] * BEATS_PER_SEC))
        self.sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        return self.sa

    def fired(self):
        return self.now_beat() > self.sa

    def begin(self):
        self.k_next = [0] * (4 * NW)
        self.tp_next = [0] * 4
        self.tps = []
        for _ in range(4):
            t = type("T", (), {})()
            t.buf = np.zeros(4 * 512, P.TP_E); t.n = 0; t.lost = 0; t.bad_seq = 0; t.bad_flag = 0; t.bad_nfr = 0
            t.n_ovr = 0; t.total = 0; t.started = True; t.overflow = 0
            self.tps.append(t)
        self.running = True
        return dict(run_t_bad=[])

    def poll_win(self, j):
        k = self.k_next[j]
        t_end = self.sa + 1 + (k + 1) * self.tint_beats
        if self.now_beat() < t_end + 20000:        # 閉じてから読めるまで ≒ 80 µs
            return None
        if self.o.fake_stall and k and k % self.o.fake_stall == 0 and j == 0:
            time.sleep(0.05)                       # 陽性対照: 読み出しを 50 ms 止める → 次の面で読み落とす
        self.k_next[j] = k + 1
        cf = self.cfgs[j]
        m = dict(seq=k + 1, k=k, n=cf["nacc"], t=self.sa + 1 + k * self.tint_beats, h=0, cfg=self.cfg, sat=0, flags=0)
        spec = self.base[j] + np.uint64(k)
        # 実機は面が 2 つで、1 周が tint を越えると次のダンプを上書きする。偽物も同じに数える
        lag = (self.now_beat() - t_end) // self.tint_beats
        miss = 0
        if lag >= 1:
            miss = int(lag)
            self.k_next[j] = k + 1 + miss
        return m, spec, miss

    def poll_tp(self, i):
        t = self.tps[i]
        f_now = (self.now_beat() - self.sa - 1) // 512
        while (self.tp_next[i] + 1) * TP_N <= f_now and t.n < len(t.buf):
            e = t.buf[t.n]
            e["t_beat"] = self.tp_next[i] * TP_N
            e["sum"] = 3_000_000_000 + self.tp_next[i]; e["nfr"] = TP_N; e["flags"] = TPF_RUN if self.tp_next[i] == 0 else 0
            pj = getattr(self.o, "posctl_tp_jump", 0)
            if pj and self.tp_next[i] and self.tp_next[i] % pj == 0:
                e["sum"] = int(e["sum"]) * 105 // 100            # 陽性対照（B2）: この個だけ +0.21 dB
            t.n += 1; t.total += 1
            self.tp_next[i] += 1
        return t

    def tp_time(self, i, f):
        return self.sa + 1 + f * 512

    def pump(self):
        return 0

    def release(self):
        pass

    def snap(self, adc, n, nacc, timeout=5.0):
        """偽物: 3000.25 MHz（第 2 ナイキストで 1095.75 MHz に見える）の正弦波 ＋ ガウス雑音、16 bit の上位 14 bit"""
        rng = np.random.default_rng(adc)
        out = []
        t0 = self.now_beat()
        for k in range(n):
            t = t0 + k * nacc * 512
            i = np.arange(P.SNAP_N) + (t * 16)
            x = 1000 * np.sin(2 * np.pi * (1095.75 / 4096.0) * i) + 800 * rng.standard_normal(P.SNAP_N)
            out.append((dict(seq=k + 1, k=k, n=nacc, f0=t // 512, t=t, h=0, cfg=0),
                        (np.clip(np.round(x), -8191, 8191).astype(np.int16) * 4)))
            time.sleep(nacc * 2e-6)
        return out

    def disarm(self):
        pass

    def stop(self):
        was, self.running = self.running, False
        return [dict(adc=i, anch_dev=0, gap=0) for i in range(4)] if was else []


# ================================================================ proj023: SAM45-Wide
class WideBackend(HwBackend):
    """SAM45-Wide（BIT_KIND 1）の裏。8 本の SLICE の流れを窓 j = 2·ADC + s の位置に。TP・リング・束ね・時刻は HwBackend と同じ"""

    def open(self):
        import spectrometer as S
        import timetest as T
        import window as W
        import timebase as TB
        import s45core as SC
        self.S, self.T, self.W, self.TB, self.SC = S, T, W, TB, SC
        from pynq import Overlay
        import xrfdc                               # Overlay() より前に import する（VERSIONS.md）
        S.setup_clocks(self.o.clkin, self.o.ref)
        self._setup_lmx()
        self.ol = Overlay(self.o.bitfile)
        if not isinstance(self.ol.rfdc, xrfdc.RFdc):
            raise RuntimeError("RFDC に xrfdc のドライバが当たっていない")
        S.check_tiles(self.ol.rfdc, 2)
        time.sleep(self.o.settle)
        self.cores, tmm = SC.discover(self.ol, bit_kind=1, bit_rev_min=1)
        self.tc = TB.TimeCore(tmm)
        self.wms = [c.m for c in self.cores]
        self.wins = []
        for c in self.cores:
            ss = c.slices()
            if [x.s for x in ss] != [0, 1]:
                raise RuntimeError(f"{c.name} の SLICE の流れが s = 0・1 でない")
            self.wins += ss
        for wm in self.wms:
            prm = int(wm.read(W.A_BASE + S.R_TP_PARAM)) & 0xFFFFFFFF
            if prm != S.TP_PARAM_EXPECT:
                raise RuntimeError(f"TP_PARAM {prm:08x}（期待 {S.TP_PARAM_EXPECT:08x}）")
        self.tc.configure(src=self.o.path, tol=1)
        self.tb = TB.Timebase(self.tc, path=self.o.path, log=self.log)
        self.TpStream = make_tp_reader(S)
        c0 = self.cores[0]
        self.ids = dict(win=f"{self.wins[0].rd(SC.S_SID):08x}", adc=f"{c0.if_id:08x}", time=f"{self.tc.rd(0x00):08x}",
                        proj=f"{c0.proj:08x}", kind="wide", usr=self._usr_access(),   # YATSUGATAKE M5b（Wide も同じ）
                        **self._lmx_ids())
        self.clock = Clock(None, {})
        self._open_ring()
        self.ids["read"] = "ring"
        self.ids["tcal"] = self.tb.cal_state                      # ADR 0023
        self.ids["board"] = (self.tb.board or {}).get("id", "-")  # ADR 0025
        self.bit_kind = c0.bit_kind
        self.anchor()

    def _open_ring(self):
        import plring as PR
        SC = self.SC
        bad = [c.name for c in self.cores if (c.caps & 3) != 3]
        if bad:
            raise RuntimeError(f"CAPS の [0]〜[1]（レコード・TP）が無いコア {bad}")
        rip = getattr(self.ol, "s45_ring_0", None)
        if rip is None:
            raise RuntimeError("ol.s45_ring_0 が無い")
        self.ring = PR.Ring(rip.mmio, ring_mib_of(self.o, 32) << 20)
        self.ring.enable(True)
        self.jmap = {(st.core.adc, st.s): j for j, st in enumerate(self.wins)}
        self.amap = {c.adc: i for i, c in enumerate(self.cores)}
        self.q = [collections.deque() for _ in self.wins]
        self.raws = [st for c in self.cores for st in c.raw()]
        # proj023 4g: SNAP は RAW の流れ（コア 0 の s 2、入口は axis_sel4 で 4 ADC から選ぶ）。HwBackend._snap_ring をそのまま使う
        #   （SRC → WRST・N_ACC・N_DUMP・REC_CTRL = ALL | SNAP・RUN、SNAP のレコードを集める。番地と意味は SAM45-Fine の RAW と同じ）
        self.full = SC.snap_stream(self.cores)
        if self.full.kind != SC.KIND_RAW:
            raise RuntimeError("RAW の流れが無い（SNAP を取れない）")
        self.fkey = (self.full.core.adc, self.full.s)
        self.log(f"リング: BASE {self.ring.base:#x} / SIZE {self.ring.size}（Wide: SLICE {len(self.wins)} 本）")

    def _rec_off(self):
        SC = self.SC
        for st in self.wins + self.raws:
            st.wr(SC.S_REC_CTRL, 0)
        for wm in self.wms:
            wm.write(TP_REC_CTRL, TP_REC_K << 8)

    def disarm(self):
        SC, T, W = self.SC, self.T, self.W
        for st in self.wins:
            st.wr(SC.S_CTRL, W_CTRL_DISARM)
        for wm in self.wms:
            wm.write(W.A_BASE + T.RA_TP_CTRL, T.TP_DISARM)

    def _arm_tc(self, sa):
        try:
            self.tc.arm(sa)
        except Exception:
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self.disarm()
            raise

    def start(self, st, at_beat, force):
        """FFT_N・S0・SHIFT・CFG → ARM_WRST（tint の格子で 4 コア一斉）→ 読み返し → N_ACC 1280・REC ALL・TP → ARM_RUN と TP_ARM を tint の格子で"""
        SC, T, W = self.SC, self.T, self.W
        if self.clock.ok:
            try:
                self.tb.check()
            except Exception as e:
                self.clock.ok, self.clock.err = False, str(e)
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.disarm()
        check_wide(st)
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        bb = {c.base_beats for c in self.cores}
        if bb != {BASE_BEATS}:
            raise RuntimeError(f"コアの BASE_BEATS {bb}（{BASE_BEATS} を期待）")
        self.cfgs = wide_cfgs(st)
        for st_ in self.wins:
            st_.wr(SC.S_CTRL, 1 << 1)              # STOP
            st_.wr(SC.S_REC_CTRL, 0)
        for i, c in enumerate(self.cores):
            cf0 = self.cfgs[NW * i]
            c.wr(W_FFT_N, 15 - cf0["lb"])
            for s in range(NW):
                cf, st_ = self.cfgs[NW * i + s], self.wins[NW * i + s]
                st_.wr(SC.S_S0, cf["s0"]); st_.wr(SC.S_SHIFT, cf["shift"]); st_.wr(SC.S_CFG, st["cfg"])
            self.wins[NW * i].wr(SC.S_CTRL, W_CTRL_ARMWRST)     # どちらの流れでもコアの WRST
        sa_w = self.grid_after(self.now_beat() + BEATS_PER_SEC // 2)
        self._arm_tc(sa_w)
        self._wait_fired(5.0)
        time.sleep(0.01)
        for i, c in enumerate(self.cores):
            lb = self.cfgs[NW * i]["lb"]
            fr = c.rd(W_FFT_N)
            if (fr & 0xFF, fr >> 8 & 0xFF) != (15 - lb, 15 - lb):
                raise RuntimeError(f"{c.adc_name}: WRST の後の FFT_N {fr:#x}（書いた {15 - lb}）")
            for s in range(NW):
                cf, st_ = self.cfgs[NW * i + s], self.wins[NW * i + s]
                if cf["active"] and st_.rd(SC.S_S0_CUR) != cf["s0"]:
                    raise RuntimeError(f"{win_key(NW * i + s)}: S0_CUR {st_.rd(SC.S_S0_CUR)}（書いた {cf['s0']}）")
                if st_.rd(SC.S_NCH) != (P.NCH if cf["active"] else 0):
                    raise RuntimeError(f"{win_key(NW * i + s)}: NCH {st_.rd(SC.S_NCH)}")
        for cf, st_ in zip(self.cfgs, self.wins):
            if cf["active"]:
                st_.wr(SC.S_NACC, cf["pl_nacc"]); st_.wr(SC.S_NDUMP, 0)
                st_.wr(SC.S_REC_CTRL, REC_ALL)
        for wm in self.wms:
            wm.write(W.A_BASE + T.RA_TP_N, TP_N)
            wm.write(TP_REC_CTRL, (TP_REC_K << 8) | 1)
        self._drain()
        sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        for cf, st_ in zip(self.cfgs, self.wins):
            if cf["active"]:
                st_.wr(SC.S_CTRL, (1 << 8) | W_SID_CTRL_ARMRUN)
        for wm in self.wms:
            wm.write(W.A_BASE + T.RA_TP_CTRL, T.TP_ARM)
        self._arm_tc(sa)
        self.sa = sa
        self.armed = True
        return sa

    def begin(self):
        S, T, W, SC = self.S, self.T, self.W, self.SC
        act = [st for st, cf in zip(self.wins, self.cfgs) if cf["active"]]
        rd64 = lambda st, a: st.rd(a) | (st.rd(a + 4) << 32)
        runts = [rd64(st, SC.S_RUN_T) for st in act] + [T.tp_run_t(wm) for wm in self.wms]
        bad = [i for i, t in enumerate(runts) if t != self.sa + 1]
        for st, cf in zip(self.wins, self.cfgs):
            if cf["active"] and st.rd(SC.S_RUN_SHIFT) != cf["shift"]:
                raise RuntimeError(f"{st.name}: RUN_SHIFT {st.rd(SC.S_RUN_SHIFT)}（書いた値 {cf['shift']}）")
        self.seq = [st.rd(SC.S_SEQ) for st in self.wins]
        self.tps, self.anch = [], []
        for wm in self.wms:
            tp = _WinTp(wm, W.A_BASE)
            tf0 = tp.rd(S.R_TP_F0_LO) | (tp.rd(S.R_TP_F0_HI) << 32)
            self.tps.append(self.TpStream(tp, TP_N, tf0))
            self.anch.append(self._tanch(wm))
        self.gap0 = [int(wm.read(W.A_BASE + T.RA_GAP)) for wm in self.wms]
        self.running = True
        return dict(run_t_bad=bad)

    def snap(self, adc, n, nacc, timeout=5.0):
        """proj023 4g: RAW の流れで（IDLE のときだけ。Acq._snap が見る）"""
        return self._snap_ring(adc, n, nacc, timeout)

    def stop(self):
        SC = self.SC
        if not self.running:
            self.disarm()
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self._rec_off()
            return []
        for st in self.wins:
            st.wr(SC.S_CTRL, 1 << 1)
        self.pump()
        self._rec_off()
        self.running = False
        out = []
        for i, wm in enumerate(self.wms):
            try:
                af1, at1 = self._tanch(wm)
                af, at = self.anch[i]
                gap1 = int(wm.read(self.W.A_BASE + self.T.RA_GAP))
                out.append(dict(adc=i, anch_dev=(at1 - at) - (af1 - af) * 512, gap=gap1 - self.gap0[i]))
            except Exception as e:
                out.append(dict(adc=i, err=str(e)))
        return out


class FakeWideBackend(FakeBackend):
    """PL なしの Wide（偽物は束ねない: ダンプ = tint。中身の形・鍵・IF の軸・DUMP_T の進み 2048·nacc を受け側で確かめる）"""

    def start(self, st, at_beat, force):
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        check_wide(st)
        self.cfgs = wide_cfgs(st)
        for cf in self.cfgs:
            cf.update(bundle=0, n_sum=1, pl_nacc=cf["nacc"])
        self.cfg = st["cfg"]
        self.tint_beats = int(round(st["tint"] * BEATS_PER_SEC))
        self.sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        return self.sa

    def poll_win(self, j):
        if not self.cfgs[j]["active"]:
            return None
        return super().poll_win(j)


# ================================================================ proj024: 2G-1（FULL の流れ 1 本、131072 ch）
class G21Backend(HwBackend):
    """2G-1（BIT_KIND 11）の裏。コア 1 個（ADC_A）の FULL の流れ（s 0、SRC で 4 ADC から選ぶ）を窓 A0 に置く（残りの 7 窓は空）。
    TP は FULL の TP（流れの 0x100〜、SRC の ADC。D-12）を欄 src に、コアの TP（コアの ADC）を欄 core.adc に（src と同じなら使わない）。
    束ね・時刻・リングは HwBackend・WideBackend と同じ。SNAP は RAW の流れ（s 1、0x4400。自分の SRC を持つ、D-14）"""

    def open(self):
        import spectrometer as S
        import timetest as T
        import window as W
        import timebase as TB
        import s45core as SC
        self.S, self.T, self.W, self.TB, self.SC = S, T, W, TB, SC
        from pynq import Overlay
        import xrfdc                               # Overlay() より前に import する（VERSIONS.md）
        S.setup_clocks(self.o.clkin, self.o.ref)
        self._setup_lmx()                          # YATSUGATAKE（2G-4 の M5）: Fine・Wide と同じ強さ（proj024〜036 は書かず出荷時の 31 のままだった）
        self.ol = Overlay(self.o.bitfile)
        if not isinstance(self.ol.rfdc, xrfdc.RFdc):
            raise RuntimeError("RFDC に xrfdc のドライバが当たっていない")
        S.check_tiles(self.ol.rfdc, 2)
        time.sleep(self.o.settle)
        self.cores, tmm = SC.discover(self.ol, bit_kind=SC.BIT_KIND_G21, ncore=1, bit_rev_min=1)
        self.tc = TB.TimeCore(tmm)
        c0 = self.cores[0]
        self.core = c0
        self.wms = [c0.m]
        fs = c0.full()
        if [x.s for x in fs] != [0]:
            raise RuntimeError(f"{c0.name} の FULL の流れが s = 0 の 1 本でない（{[x.s for x in fs]}）")
        self.fst = fs[0]
        for a, want in ((SC.S_NCH, G_NCH), (SC.S_FRAME_BEATS, G_FRAME)):
            if self.fst.rd(a) != want:
                raise RuntimeError(f"FULL の流れの {a:#x} が {self.fst.rd(a)}（期待 {want}）")
        self.wins = [self.fst]                     # 窓 j = 0 だけ（poll_win は j ≠ 0 を見ない）
        prm = int(c0.m.read(W.A_BASE + S.R_TP_PARAM)) & 0xFFFFFFFF
        if prm != S.TP_PARAM_EXPECT:
            raise RuntimeError(f"コアの TP_PARAM {prm:08x}（期待 {S.TP_PARAM_EXPECT:08x}）")
        self.ftp = _WinTp(c0.m, self.fst.base)     # FULL の TP のレジスタ（流れのブロックの 0x100〜 = コアの 0x100〜 と同じ並び）
        self.tc.configure(src=self.o.path, tol=1)
        self.tb = TB.Timebase(self.tc, path=self.o.path, log=self.log)
        self.TpStream = make_tp_reader(S)
        self.ids = dict(win=f"{self.fst.rd(SC.S_SID):08x}", adc=f"{c0.if_id:08x}", time=f"{self.tc.rd(0x00):08x}",
                        proj=f"{c0.proj:08x}", kind="g21", usr=self._usr_access(),   # YATSUGATAKE M5b（2G も同じ）
                        **self._lmx_ids())
        self.clock = Clock(None, {})
        self._open_ring()
        self.ids["read"] = "ring"
        self.ids["tcal"] = self.tb.cal_state                      # ADR 0023
        self.ids["board"] = (self.tb.board or {}).get("id", "-")  # ADR 0025
        self.bit_kind = c0.bit_kind
        self.anchor()

    def _open_ring(self):
        import plring as PR
        SC = self.SC
        c0 = self.core
        if (c0.caps & 3) != 3:
            raise RuntimeError(f"CAPS の [0]〜[1]（レコード・TP）が無い（{c0.caps:#x}）")
        rip = getattr(self.ol, "s45_ring_0", None)
        if rip is None:
            raise RuntimeError("ol.s45_ring_0 が無い")
        self.ring = PR.Ring(rip.mmio, ring_mib_of(self.o, G_RING_MIB) << 20)
        self.ring.enable(True)
        self.jmap = {(c0.adc, 0): 0}
        self.amap = {}                             # TP の欄は start で決める（src による）
        self.q = [collections.deque() for _ in range(4 * NW)]
        self.raws = c0.raw()
        self.full = SC.snap_stream(self.cores)     # SNAP の流れ = RAW（s 1）
        if self.full.kind != SC.KIND_RAW or self.full.s != 1:
            raise RuntimeError(f"RAW の流れが s 1 に無い（{self.full.name}）")
        self.fkey = (c0.adc, self.full.s)
        self.log(f"リング: BASE {self.ring.base:#x} / SIZE {self.ring.size}（2G-1: FULL 1 本・1 MiB のレコード）")

    def poll_win(self, j):
        if j != 0:
            return None
        return super().poll_win(j)

    def pump(self):
        """リングを [R, W) まで読み、SPEC は窓 A0 の列へ、TP は FULL の TP（s 0）とコアの TP（s 0xFF）をそれぞれの欄へ"""
        self.n_pump += 1
        self._posctl_stall()
        t0 = time.perf_counter()
        c0 = self.core.adc
        lazy = ((lambda core, s, ty: ty == TYPE_SPEC and core == c0 and s == 0)       # proj029 2: 窓 A0 の SPEC を写さずに
                if 0 in self.lazy_wins and self.running else None)
        recs = self.ring.read(lazy)
        t1 = time.perf_counter()
        for core, s, seq, hw, pay, crc_ok, tail_ok in recs:
            if crc_ok is False or not tail_ok:     # crc_ok None = LazyRec（PL の CRC は記録のときに C で照らす）
                self.ring_crc += 1
                continue
            if core != c0:
                continue
            ty = int(hw[0]) >> 40 & 0xFF
            if ty == TYPE_SPEC and s == 0:
                self.q[0].append((seq, hw, pay))
            elif ty == TYPE_TP and self.running:
                i = self.tp_slot.get(s)
                if i is not None:
                    self.tps[i].feed(seq, int(hw[5]) & 0xFFFFFFFF, pay, TP_REC_K)
        self.last_pump = (t1 - t0, time.perf_counter() - t1)
        return len(recs)

    def _rec_off(self):
        SC = self.SC
        for st in [self.fst] + self.raws:
            st.wr(SC.S_REC_CTRL, 0)
        self.core.wr(TP_REC_CTRL, TP_REC_K << 8)
        self.fst.wr(TP_REC_CTRL, TP_REC_K << 8)

    def disarm(self):
        SC, T, W = self.SC, self.T, self.W
        self.fst.wr(SC.S_CTRL, W_CTRL_DISARM)
        self.core.m.write(W.A_BASE + T.RA_TP_CTRL, T.TP_DISARM)

    def _arm_tc(self, sa):
        try:
            self.tc.arm(sa)
        except Exception:
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self.disarm()
            raise

    def start(self, st, at_beat, force):
        """STOP・REC 0 → SRC・SHIFT・CFG → ARM_WRST（tint の格子）→ SRC の読み返し → N_ACC 160・REC ALL・FULL の TP・コアの TP →
        ARM_RUN（FULL の TP は FULL の RUN で走る）と コアの TP_ARM を tint の格子で"""
        SC, T, W = self.SC, self.T, self.W
        if self.clock.ok:
            try:
                self.tb.check()
            except Exception as e:
                self.clock.ok, self.clock.err = False, str(e)
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.disarm()
        check_g21(st)
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        if self.core.base_beats != BASE_BEATS:
            raise RuntimeError(f"コアの BASE_BEATS {self.core.base_beats}（{BASE_BEATS} を期待）")
        self.cfgs = g21_cfgs(st)
        cf = self.cfgs[0]
        fst = self.fst
        fst.wr(SC.S_CTRL, 1 << 1)                  # STOP
        fst.wr(SC.S_REC_CTRL, 0)
        fst.wr(SC.S_SRC, cf["src"]); fst.wr(SC.S_SHIFT, cf["shift"]); fst.wr(SC.S_CFG, st["cfg"])
        fst.wr(SC.S_CTRL, W_CTRL_ARMWRST)
        sa_w = self.grid_after(self.now_beat() + BEATS_PER_SEC // 2)
        self._arm_tc(sa_w)
        self._wait_fired(5.0)
        time.sleep(0.01)
        got = fst.rd(SC.S_SRC)
        if got != (0x8000_0000 | cf["src"]):
            raise RuntimeError(f"WRST の後の SRC {got:#010x}（書いた {cf['src']}。期待 {0x8000_0000 | cf['src']:#010x}）")
        if fst.rd(SC.S_NCH) != G_NCH or fst.rd(SC.S_FRAME_BEATS) != G_FRAME:
            raise RuntimeError(f"NCH {fst.rd(SC.S_NCH)}・FRAME_BEATS {fst.rd(SC.S_FRAME_BEATS)}")
        fst.wr(SC.S_NACC, cf["pl_nacc"]); fst.wr(SC.S_NDUMP, 0)
        fst.wr(SC.S_REC_CTRL, REC_ALL)
        fst.wr(T.RA_TP_N, TP_N)                    # FULL の TP（流れの 0x100）
        fst.wr(TP_REC_CTRL, (TP_REC_K << 8) | 1)
        self.use_core_tp = cf["src"] != self.core.adc
        cm = self.core.m
        cm.write(W.A_BASE + T.RA_TP_N, TP_N)
        cm.write(TP_REC_CTRL, (TP_REC_K << 8) | (1 if self.use_core_tp else 0))
        self._drain()
        sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        fst.wr(SC.S_CTRL, (1 << 8) | W_SID_CTRL_ARMRUN)
        if self.use_core_tp:
            cm.write(W.A_BASE + T.RA_TP_CTRL, T.TP_ARM)
        self._arm_tc(sa)
        self.sa = sa
        self.armed = True
        return sa

    def begin(self):
        S, T, W, SC = self.S, self.T, self.W, self.SC
        fst, cf = self.fst, self.cfgs[0]
        rd64 = lambda a: fst.rd(a) | (fst.rd(a + 4) << 32)
        runts = [rd64(SC.S_RUN_T)] + ([T.tp_run_t(self.core.m)] if self.use_core_tp else [])
        bad = [i for i, t in enumerate(runts) if t != self.sa + 1]
        if fst.rd(SC.S_RUN_SHIFT) != cf["shift"]:
            raise RuntimeError(f"RUN_SHIFT {fst.rd(SC.S_RUN_SHIFT)}（書いた値 {cf['shift']}）")
        run_f0 = rd64(SC.S_RUN_F0)
        self.seq = [fst.rd(SC.S_SEQ)] + [0] * (4 * NW - 1)
        self.tps = [_EmptyTp() for _ in range(4)]
        self.anch = [None] * 4
        self.tp_slot = {}
        ftf0 = self.ftp.rd(S.R_TP_F0_LO) | (self.ftp.rd(S.R_TP_F0_HI) << 32)
        if ftf0 != run_f0 * (G_FRAME // 512):
            raise RuntimeError(f"FULL の TP の F0 {ftf0}（FULL の RUN_F0 {run_f0} × 32 = {run_f0 * 32} を期待）")
        src = cf["src"]
        self.tps[src] = self.TpStream(self.ftp, TP_N, ftf0)
        self.tp_slot[0] = src
        self.tp_kind = {src: "full"}
        if self.use_core_tp:
            a = self.core.adc
            tp = _WinTp(self.core.m, W.A_BASE)
            tf0 = tp.rd(S.R_TP_F0_LO) | (tp.rd(S.R_TP_F0_HI) << 32)
            self.tps[a] = self.TpStream(tp, TP_N, tf0)
            self.anch[a] = self._tanch(self.core.m)
            self.tp_slot[0xFF] = a
            self.tp_kind[a] = "core"
        self.gap0 = int(self.core.m.read(W.A_BASE + T.RA_GAP))
        self.running = True
        return dict(run_t_bad=bad)

    def tp_time(self, i, f):
        if self.tp_kind.get(i) == "full":
            return f * 512 - G_DS_BEATS              # 小フレーム f の頭（K_F 0）。FULL のデータは DUMP_T より 1 ビート前（2e）
        return super().tp_time(i, f)

    def snap(self, adc, n, nacc, timeout=5.0):
        """RAW の流れで（IDLE のときだけ。Acq._snap が見る）"""
        return self._snap_ring(adc, n, nacc, timeout)

    def stop(self):
        SC = self.SC
        if not self.running:
            self.disarm()
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self._rec_off()
            return []
        self.fst.wr(SC.S_CTRL, 1 << 1)
        self.pump()
        self._rec_off()
        self.running = False
        out = []
        for i, k in sorted(self.tp_kind.items()):
            if k != "core":
                out.append(dict(adc=i, tp="full"))
                continue
            try:
                af1, at1 = self._tanch(self.core.m)
                af, at = self.anch[i]
                gap1 = int(self.core.m.read(self.W.A_BASE + self.T.RA_GAP))
                out.append(dict(adc=i, tp="core", anch_dev=(at1 - at) - (af1 - af) * 512, gap=gap1 - self.gap0))
            except Exception as e:
                out.append(dict(adc=i, err=str(e)))
        return out


class _EmptyTp:
    """使わない TP の欄（Acq は 4 欄を回す）"""

    def __init__(self):
        self.buf = np.zeros(0, P.TP_E); self.n = 0; self.lost = 0; self.bad_seq = 0; self.bad_flag = 0; self.bad_nfr = 0
        self.n_ovr = 0; self.total = 0; self.started = False; self.overflow = 0; self.rec_lost = 0


class FakeG21Backend(FakeBackend):
    """PL なしの 2G-1（偽物は束ねない: ダンプ = tint。中身の形・鍵・IF の軸・DUMP_T の進み 16384·nacc・TP の欄を受け側で確かめる）"""

    def open(self):
        super().open()
        rng = np.random.default_rng(2)
        self.base = [rng.integers(1 << 40, 1 << 41, G_NCH, dtype=np.uint64)] + [None] * (4 * NW - 1)   # 窓 A0 だけ

    def start(self, st, at_beat, force):
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        check_g21(st)
        self.cfgs = g21_cfgs(st)
        cf = self.cfgs[0]
        cf.update(bundle=0, n_sum=1, pl_nacc=cf["nacc"])
        self.cfg = st["cfg"]
        self.tint_beats = int(round(st["tint"] * BEATS_PER_SEC))
        self.sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        self.tp_use = {cf["src"], 0}               # FULL の TP（src）とコアの TP（A。src = A なら 1 本）
        return self.sa

    def begin(self):
        r = super().begin()
        for i in range(4):
            if i not in self.tp_use:
                self.tps[i] = _EmptyTp()
        return r

    def poll_win(self, j):
        if j != 0:
            return None
        return super().poll_win(0)

    def poll_tp(self, i):
        if i not in self.tp_use:
            return self.tps[i]
        return super().poll_tp(i)


# ================================================================ proj025: 2G-2（FULL の流れ 2 本、65536 ch × 2）
class G22Backend(HwBackend):
    """2G-2（BIT_KIND 10）の裏。コア 0（ADC_A）・コア 1（ADC_B）の FULL の流れ（どちらも s 0、SRC で 4 ADC から選ぶ）を窓 A0・B0 に置く（残りの 6 窓は空）。
    G21Backend をコア 2 個に広げたもの。TP の欄は g22_tp_slots（同じ ADC の 2 本を混ぜない）。SNAP はコア 0 の RAW の流れ（s 1）。コア 1 は RAW を持たない（E-5）。
    proj027: 形（コアの数・NCH・FRAME・RAW の本数）は self.G から読む（G24Backend は G だけを替えた子）"""
    G = G2_GEOM

    def open(self):
        import spectrometer as S
        import timetest as T
        import window as W
        import timebase as TB
        import s45core as SC
        self.S, self.T, self.W, self.TB, self.SC = S, T, W, TB, SC
        from pynq import Overlay
        import xrfdc                               # Overlay() より前に import する（VERSIONS.md）
        S.setup_clocks(self.o.clkin, self.o.ref)
        self._setup_lmx()                          # YATSUGATAKE（2G-4 の M5）: Fine・Wide と同じ強さ（proj024〜036 は書かず出荷時の 31 のままだった）
        self.ol = Overlay(self.o.bitfile)
        if not isinstance(self.ol.rfdc, xrfdc.RFdc):
            raise RuntimeError("RFDC に xrfdc のドライバが当たっていない")
        S.check_tiles(self.ol.rfdc, 2)
        time.sleep(self.o.settle)
        self._load_coef()                          # proj031: 2G-4 は共有の係数 URAM を書く（G22Backend は何もしない）
        self.cores, tmm = SC.discover(self.ol, bit_kind=self.G.bit_kind, ncore=self.G.ncore, bit_rev_min=1)
        if [c.adc for c in self.cores] != list(range(self.G.ncore)):
            raise RuntimeError(f"コアの CORE_PORT が {[c.adc for c in self.cores]}（期待 {list(range(self.G.ncore))}）")
        self.tc = TB.TimeCore(tmm)
        self.wms = [c.m for c in self.cores]
        self.fsts = []
        for c in self.cores:
            fs = c.full()
            if [x.s for x in fs] != [0]:
                raise RuntimeError(f"{c.name} の FULL の流れが s = 0 の 1 本でない（{[x.s for x in fs]}）")
            for a, want in ((SC.S_NCH, self.G.nch), (SC.S_FRAME_BEATS, self.G.frame)):
                if fs[0].rd(a) != want:
                    raise RuntimeError(f"{c.name} の FULL の流れの {a:#x} が {fs[0].rd(a)}（期待 {want}）")
            prm = int(c.m.read(W.A_BASE + S.R_TP_PARAM)) & 0xFFFFFFFF
            if prm != S.TP_PARAM_EXPECT:
                raise RuntimeError(f"{c.name} の TP_PARAM {prm:08x}（期待 {S.TP_PARAM_EXPECT:08x}）")
            self.fsts.append(fs[0])
        nraw = [len(c.raw()) for c in self.cores]
        if nraw != self.G.raws or any(c.nstream != 1 + r for c, r in zip(self.cores, self.G.raws)):
            raise RuntimeError(f"RAW の流れの本数が {nraw}・NSTREAM {[c.nstream for c in self.cores]}（期待 {self.G.raws}・{[1 + r for r in self.G.raws]}）")
        self.wins = list(self.fsts)
        self.ftps = [_WinTp(c.m, f.base) for c, f in zip(self.cores, self.fsts)]   # FULL の TP（流れのブロックの 0x100〜）
        self.tc.configure(src=self.o.path, tol=1)
        self.tb = TB.Timebase(self.tc, path=self.o.path, log=self.log)
        self.TpStream = make_tp_reader(S)
        c0 = self.cores[0]
        self.ids = dict(win="/".join(f"{f.rd(SC.S_SID):08x}" for f in self.fsts), adc=f"{c0.if_id:08x}", time=f"{self.tc.rd(0x00):08x}",
                        proj=f"{c0.proj:08x}", kind=self.G.kind, usr=self._usr_access(),   # YATSUGATAKE M5b（2G も同じ）
                        **self._lmx_ids())
        self.clock = Clock(None, {})
        self._open_ring()
        self.ids["read"] = "ring"
        self.ids["tcal"] = self.tb.cal_state                      # ADR 0023
        self.ids["board"] = (self.tb.board or {}).get("id", "-")  # ADR 0025
        self.bit_kind = c0.bit_kind
        self.anchor()

    def _load_coef(self):
        self.cu = None

    def _open_ring(self):
        import plring as PR
        SC = self.SC
        for c in self.cores:
            if (c.caps & 3) != 3:
                raise RuntimeError(f"{c.name} の CAPS の [0]〜[1]（レコード・TP）が無い（{c.caps:#x}）")
        rip = getattr(self.ol, "s45_ring_0", None)
        if rip is None:
            raise RuntimeError("ol.s45_ring_0 が無い")
        self.ring = PR.Ring(rip.mmio, ring_mib_of(self.o, G_RING_MIB) << 20)
        self.ring.enable(True)
        self.jmap = {(c.adc, 0): j for c, j in zip(self.cores, self.G.win)}
        self.amap = {}
        self.q = [collections.deque() for _ in range(4 * NW)]
        self.raws = self.cores[0].raw()
        self.full = self.raws[0]                   # SNAP の流れ = コア 0 の RAW（s 1）。proj027: 2G-4 は 4 コアとも RAW があり snap_stream（1 本の前提）が使えないので直に
        if self.full.kind != SC.KIND_RAW or self.full.s != 1:
            raise RuntimeError(f"RAW の流れが s 1 に無い（{self.full.name}）")
        self.fkey = (self.cores[0].adc, self.full.s)
        self.log(f"リング: BASE {self.ring.base:#x} / SIZE {self.ring.size}（{self.G.name}: FULL {self.G.ncore} 本・{self.G.nch * 8 >> 10} KiB のレコード × {self.G.ncore}）")

    def poll_win(self, j):
        if j not in self.G.win:
            return None
        return super().poll_win(j)

    def pump(self):
        """リングを [R, W) まで読み、SPEC は窓 A0・B0（2G-4 は〜D0）の列へ、TP は (コア, s) の欄へ（tp_slot）"""
        self.n_pump += 1
        self._posctl_stall()
        t0 = time.perf_counter()
        lw, jm = self.lazy_wins, self.jmap
        lazy = ((lambda core, s, ty: ty == TYPE_SPEC and jm.get((core, s)) in lw)    # proj029 2: その窓の SPEC を写さずに
                if lw and self.running else None)
        recs = self.ring.read(lazy)
        t1 = time.perf_counter()
        for core, s, seq, hw, pay, crc_ok, tail_ok in recs:
            if crc_ok is False or not tail_ok:     # crc_ok None = LazyRec（PL の CRC は記録のときに C で照らす）
                self.ring_crc += 1
                continue
            ty = int(hw[0]) >> 40 & 0xFF
            if ty == TYPE_SPEC:
                j = self.jmap.get((core, s))
                if j is not None:
                    self.q[j].append((seq, hw, pay))
            elif ty == TYPE_TP and self.running:
                i = self.tp_slot.get((core, s))
                if i is not None:
                    self.tps[i].feed(seq, int(hw[5]) & 0xFFFFFFFF, pay, TP_REC_K)
        self.last_pump = (t1 - t0, time.perf_counter() - t1)
        return len(recs)

    def _rec_off(self):
        SC = self.SC
        for st in self.fsts + self.raws:
            st.wr(SC.S_REC_CTRL, 0)
        for c, f in zip(self.cores, self.fsts):
            c.wr(TP_REC_CTRL, TP_REC_K << 8)
            f.wr(TP_REC_CTRL, TP_REC_K << 8)

    def disarm(self):
        SC, T, W = self.SC, self.T, self.W
        for f in self.fsts:
            f.wr(SC.S_CTRL, W_CTRL_DISARM)
        for c in self.cores:
            c.m.write(W.A_BASE + T.RA_TP_CTRL, T.TP_DISARM)

    def _arm_tc(self, sa):
        try:
            self.tc.arm(sa)
        except Exception:
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self.disarm()
            raise

    def start(self, st, at_beat, force):
        """2 本とも STOP・REC 0 → SRC・SHIFT・CFG → ARM_WRST（tint の格子 1 つ）→ SRC の読み返し → N_ACC 320・REC ALL・FULL の TP・コアの TP →
        ARM_RUN × 2（FULL の TP は FULL の RUN で走る）と使うコアの TP_ARM を tint の格子で"""
        SC, T, W = self.SC, self.T, self.W
        if self.clock.ok:
            try:
                self.tb.check()
            except Exception as e:
                self.clock.ok, self.clock.err = False, str(e)
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.disarm()
        check_g22(st, self.G)
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        for c in self.cores:
            if c.base_beats != BASE_BEATS:
                raise RuntimeError(f"{c.name} の BASE_BEATS {c.base_beats}（{BASE_BEATS} を期待）")
        self.cfgs = g22_cfgs(st, self.G)
        cfs = [self.cfgs[j] for j in self.G.win]
        for f, cf in zip(self.fsts, cfs):
            f.wr(SC.S_CTRL, 1 << 1)                # STOP
            f.wr(SC.S_REC_CTRL, 0)
            f.wr(SC.S_SRC, cf["src"]); f.wr(SC.S_SHIFT, cf["shift"]); f.wr(SC.S_CFG, st["cfg"])
        for f in self.fsts:
            f.wr(SC.S_CTRL, W_CTRL_ARMWRST)
        sa_w = self.grid_after(self.now_beat() + BEATS_PER_SEC // 2)
        self._arm_tc(sa_w)
        self._wait_fired(5.0)
        time.sleep(0.01)
        for c, f, cf in zip(self.cores, self.fsts, cfs):
            got = f.rd(SC.S_SRC)
            if got != (0x8000_0000 | cf["src"]):
                raise RuntimeError(f"{c.name}: WRST の後の SRC {got:#010x}（書いた {cf['src']}。期待 {0x8000_0000 | cf['src']:#010x}）")
            if f.rd(SC.S_NCH) != self.G.nch or f.rd(SC.S_FRAME_BEATS) != self.G.frame:
                raise RuntimeError(f"{c.name}: NCH {f.rd(SC.S_NCH)}・FRAME_BEATS {f.rd(SC.S_FRAME_BEATS)}")
        self.slots = g22_tp_slots([cf["src"] for cf in cfs])
        for i, (c, f, cf) in enumerate(zip(self.cores, self.fsts, cfs)):
            f.wr(SC.S_NACC, cf["pl_nacc"]); f.wr(SC.S_NDUMP, 0)
            f.wr(SC.S_REC_CTRL, REC_ALL)
            f.wr(T.RA_TP_N, TP_N)                  # FULL の TP（流れの 0x100）
            f.wr(TP_REC_CTRL, (TP_REC_K << 8) | (1 if (i, 0) in self.slots else 0))
            c.m.write(W.A_BASE + T.RA_TP_N, TP_N)
            c.m.write(TP_REC_CTRL, (TP_REC_K << 8) | (1 if (i, 0xFF) in self.slots else 0))
        self._drain()
        sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        for f in self.fsts:
            f.wr(SC.S_CTRL, (1 << 8) | W_SID_CTRL_ARMRUN)
        for i, c in enumerate(self.cores):
            if (i, 0xFF) in self.slots:
                c.m.write(W.A_BASE + T.RA_TP_CTRL, T.TP_ARM)
        self._arm_tc(sa)
        self.sa = sa
        self.armed = True
        return sa

    def begin(self):
        S, T, W, SC = self.S, self.T, self.W, self.SC
        cfs = [self.cfgs[j] for j in self.G.win]
        runts, f0s = [], []
        for f, cf in zip(self.fsts, cfs):
            rd64 = lambda a, f=f: f.rd(a) | (f.rd(a + 4) << 32)
            runts.append(rd64(SC.S_RUN_T))
            if f.rd(SC.S_RUN_SHIFT) != cf["shift"]:
                raise RuntimeError(f"RUN_SHIFT {f.rd(SC.S_RUN_SHIFT)}（書いた値 {cf['shift']}）")
            f0s.append(rd64(SC.S_RUN_F0))
        runts += [T.tp_run_t(self.cores[i].m) for i in range(self.G.ncore) if (i, 0xFF) in self.slots]
        bad = [i for i, t in enumerate(runts) if t != self.sa + 1]
        if len(set(f0s)) != 1:
            raise RuntimeError(f"{len(f0s)} 本の RUN_F0 が揃っていない {f0s}（同じ格子で RUN に入っていない）")
        run_f0 = f0s[0]
        self.seq = [0] * (4 * NW)
        for f, j in zip(self.fsts, self.G.win):
            self.seq[j] = f.rd(SC.S_SEQ)
        self.tps = [_EmptyTp() for _ in range(4)]
        self.anch = [None] * 4
        self.tp_slot, self.tp_kind, self.tp_core = {}, {}, {}
        for (i, s), slot in sorted(self.slots.items()):
            if s == 0:
                ftp = self.ftps[i]
                ftf0 = ftp.rd(S.R_TP_F0_LO) | (ftp.rd(S.R_TP_F0_HI) << 32)
                if ftf0 != run_f0 * (self.G.frame // 512):
                    raise RuntimeError(f"コア {i} の FULL の TP の F0 {ftf0}（FULL の RUN_F0 {run_f0} × {self.G.frame // 512} = {run_f0 * (self.G.frame // 512)} を期待）")
                self.tps[slot] = self.TpStream(ftp, TP_N, ftf0)
                self.tp_kind[slot] = "full"
            else:
                m = self.cores[i].m
                tp = _WinTp(m, W.A_BASE)
                tf0 = tp.rd(S.R_TP_F0_LO) | (tp.rd(S.R_TP_F0_HI) << 32)
                self.tps[slot] = self.TpStream(tp, TP_N, tf0)
                self.anch[slot] = self._tanch(m)
                self.tp_kind[slot] = "core"
            self.tp_slot[(i, s)] = slot
            self.tp_core[slot] = i
        self.gap0 = [int(c.m.read(W.A_BASE + T.RA_GAP)) for c in self.cores]
        self.running = True
        return dict(run_t_bad=bad)

    def tp_time(self, i, f):
        if self.tp_kind.get(i) == "full":
            return f * 512 - self.G.ds             # 小フレーム f の頭（K_F 0）。FULL のデータは DUMP_T より 1 ビート前
        return super().tp_time(i, f)

    def snap(self, adc, n, nacc, timeout=5.0):
        """コア 0 の RAW の流れで（IDLE のときだけ。Acq._snap が見る）"""
        return self._snap_ring(adc, n, nacc, timeout)

    def stop(self):
        SC = self.SC
        if not self.running:
            self.disarm()
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self._rec_off()
            return []
        for f in self.fsts:
            f.wr(SC.S_CTRL, 1 << 1)
        self.pump()
        self._rec_off()
        self.running = False
        out = []
        for i, k in sorted(self.tp_kind.items()):
            ci = self.tp_core[i]
            if k != "core":
                out.append(dict(adc=i, tp="full", core=ci))
                continue
            try:
                m = self.cores[ci].m
                af1, at1 = self._tanch(m)
                af, at = self.anch[i]
                gap1 = int(m.read(self.W.A_BASE + self.T.RA_GAP))
                out.append(dict(adc=i, tp="core", core=ci, anch_dev=(at1 - at) - (af1 - af) * 512, gap=gap1 - self.gap0[ci]))
            except Exception as e:
                out.append(dict(adc=i, err=str(e)))
        return out


class G24Backend(G22Backend):
    """proj027: 2G-4（BIT_KIND 3）の裏。コア 0〜3（ADC_A〜D）の FULL の流れ（どれも s 0、SRC で 4 ADC から選ぶ）を窓 A0・B0・C0・D0 に置く。
    G22Backend と形だけが違う（4 コアとも RAW 1 本 = NSTREAM 2。SNAP はコア 0 の RAW）。
    proj031: Overlay の後に**共有の係数 URAM（g24_cu_0）を書いて VERIFY する**（URAM は初期値を持てない。書くまでコアの口は開かない）。
    係数の補間の表の hex は .bit と同じ場所（g24_coef_lo.hex・g24_coef_hi.hex）。START の前に OK を読み直す"""
    G = G4_GEOM

    def _load_coef(self):
        import g24cu
        ip = getattr(self.ol, "g24_cu_0", None)
        if ip is None:
            raise RuntimeError("ol.g24_cu_0 が無い（proj031 より前の 2G-4 の .bit。proj030 以前の PS を使う）")
        d = os.path.dirname(os.path.abspath(self.o.bitfile))
        self.cu = ip.mmio
        self.cu_info = g24cu.load(self.cu, os.path.join(d, "g24_coef_lo.hex"), os.path.join(d, "g24_coef_hi.hex"), self.SC.PROJ_G24,
                                  log=lambda m: print(m, flush=True))

    def start(self, st, at_beat, force):
        import g24cu
        g24cu.check_ok(self.cu)
        return super().start(st, at_beat, force)


class FakeG22Backend(FakeBackend):
    """PL なしの 2G-2（偽物は束ねない: ダンプ = tint。2 窓の中身の形・鍵・IF の軸・DUMP_T の進み 8192·nacc・TP の欄の割り付けを受け側で確かめる）。
    proj027: 形は self.G から（FakeG24Backend は G だけを替えた子）"""
    G = G2_GEOM

    def open(self):
        super().open()
        rng = np.random.default_rng(3)
        self.base = [None] * (4 * NW)
        for j in self.G.win:
            self.base[j] = rng.integers(1 << 40, 1 << 41, self.G.nch, dtype=np.uint64)
        self.bit_kind = self.G.bit_kind

    def start(self, st, at_beat, force):
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        check_g22(st, self.G)
        self.cfgs = g22_cfgs(st, self.G)
        for j in self.G.win:
            cf = self.cfgs[j]
            cf.update(bundle=0, n_sum=1, pl_nacc=cf["nacc"])
        self.cfg = st["cfg"]
        self.tint_beats = int(round(st["tint"] * BEATS_PER_SEC))
        self.sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        self.tp_use = set(g22_tp_slots(st["src"]).values())
        return self.sa

    def begin(self):
        r = super().begin()
        for i in range(4):
            if i not in self.tp_use:
                self.tps[i] = _EmptyTp()
        return r

    def poll_win(self, j):
        if j not in self.G.win:
            return None
        return super().poll_win(j)

    def poll_tp(self, i):
        if i not in self.tp_use:
            return self.tps[i]
        return super().poll_tp(i)


class FakeG24Backend(FakeG22Backend):
    """proj027: PL なしの 2G-4（4 窓 A0〜D0・32768 ch・DUMP_T の進み 4096·nacc）"""
    G = G4_GEOM


# ================================================================ YATSUGATAKE M5b: SpW8（BIT_KIND 7、study-rfsoc proj032 b5 rev 10）
# 窓のキーは論理の窓（ADR 0028）: A0〜A7 は ADC_A の窓 0〜7（利用者の並び）。spwplan が流れ s（頭）・粗い ch・機関・枠に割り当てる。
# リングのレコードは type 5・fmt 1（PL が丸めた f32、ADR 0029）。束ねは double の器（Bundler の f32）。RUN・WRST はコアで 1 つ
SPW_KIND = "spw8"
SPW_NW = 8                                  # 論理の窓 / ADC
SPW_H, SPW_E, SPW_S = 8, 3, 8               # 頭・機関・チップ内の履歴の枠（b5 に PL の DDR は無い）
SPW_BIT_KIND, SPW_BIT_REV = 7, 10
SPW_BW = (128, 64, 32, 16, 8)               # NS 1〜5
SPW_NG = BASE_BEATS // G_BEATS              # 5: コアの NG（G の数）。PL のダンプ = BASE 10.24 ms
SPW_SHIFT = 4                               # proj032 の既定
SPW_PLAN2 = ((3900.0, 128), (3890.0, 64), (3890.0, 64), (3892.0, 16), (3891.0, 8), (3300.0, 128), (3290.0, 32), (2650.0, 128))   # 判定の窓の組 plan2
SPW_COARSE = ("auto", "near", "alt")        # 粗い ch: 計画の既定・近い ch・2 番目に近い ch（試験のために決め打つ口、ADR 0028）
TYPE_SPW = 5
C_CORE_FLAGS, C_NG, C_NDUMP, C_WRST_BAD, C_WRST_CNT = 0x80, 0x84, 0x88, 0x8C, 0x90
S_WCUR, S_WCUR_DPHI, S_WFL, S_WSL, S_WG, S_WCUR2 = 0x10C, 0x110, 0x120, 0x124, 0x128, 0x12C
SPW_REGS = (("WK", 0x100), ("WDPHI", 0x104), ("WNS", 0x108), ("WFL", S_WFL), ("WSL", S_WSL), ("WG", S_WG))
SPW_CT_STOP, SPW_CT_ARMRUN, SPW_CT_CANCEL, SPW_CT_FCLR, SPW_CT_ARMWRST = 1 << 1, 1 << 2, 1 << 3, 1 << 8, 1 << 13   # どの流れの CTRL でもコアに効く


def spw_frame(ns):
    """SpW の窓のフレーム L = 2^(12+NS) ビート（= 256e6 / df）"""
    return 1 << (12 + ns)


def default_settings_spw():
    """4 ADC とも plan2（窓 8 本、チップ内の枠 0..7 を全部使う）"""
    wins = [dict(if_mhz=f, bw=w, shift=SPW_SHIFT, on=1, coarse="auto") for _ in range(4) for f, w in SPW_PLAN2]
    return dict(kind=SPW_KIND, tint=0.04096, cfg=0, fmt="f32", wins=wins)


def spw_plan(st):
    """4 ADC とも窓の組を計画する（interface 5. の「SpW の窓のキーは論理の窓」）。→ ADC ごとの spwplan.plan の結果（wins の各々に論理の番号 i）。
    計画できない組は ValueError（どの ADC の組かと理由）。計画が WRST の約束を破るのは spwplan の誤り（同じく断る）"""
    import spwplan
    out = []
    for a in range(4):
        ws = st["wins"][a * SPW_NW:(a + 1) * SPW_NW]
        on = [i for i, w in enumerate(ws) if w["on"]]
        req = [(ws[i]["if_mhz"], ws[i]["bw"]) for i in on]
        fk = {n: ws[i]["coarse"] for n, i in enumerate(on) if ws[i]["coarse"] != "auto"}
        try:
            p = spwplan.plan(req, H=SPW_H, E=SPW_E, S=SPW_S, ddr=False, force_k=fk)
        except spwplan.PlanError as e:
            raise ValueError(f"{ADC_NAMES[a]} の窓の組を計画できない（組ごと断る。今の組のまま）: {e}") from None
        bad = spwplan.check(p["streams"], E=SPW_E, S=SPW_S)
        if bad:
            raise ValueError(f"{ADC_NAMES[a]} の計画が WRST の約束を破る（印 {bad:#x}。spwplan の誤り）")
        for x, i in zip(p["wins"], on):
            x["i"] = i                             # 計画の番号（on の窓だけの並び）→ 論理の窓の番号
        out.append(p)
    return out


def spw_cfgs(st, plans):
    """論理の窓 j = 8·ADC ＋ i ごとの cfg（START の EVENT の wins・記録の頭）。使わない窓（on 0）は active False"""
    n_sum = check_tint(st["tint"])
    cfgs = []
    for a, p in enumerate(plans):
        by_i = {x["i"]: x for x in p["wins"]}
        for i in range(SPW_NW):
            ws = st["wins"][a * SPW_NW + i]
            x = by_i.get(i)
            if x is None:
                cfgs.append(dict(kind="spw", active=False, bundle=0, n_sum=n_sum, s=None, ns=0, shift=ws["shift"], if_mhz=ws["if_mhz"], bw=ws["bw"]))
                continue
            L = spw_frame(x["ns"])
            cfgs.append(dict(kind="spw", active=True, bundle=1, n_sum=n_sum, pl_nacc=BASE_BEATS // L, nacc=n_sum * (BASE_BEATS // L),
                             s=x["s"], k=x["k"], alt=bool(x["alt"]), dphi=x["dphi"], fl=x["fl"], sl=x["sl"], g=x["wg"],
                             w4=12 | (x["ns"] << 8) | (ws["shift"] << 16) | (1 << 32),   # レコードの頭の語 4 の期待（src は振り分けで足す）
                             ns=x["ns"], bw=x["w"], frame=L, shift=ws["shift"], if_mhz=x["if_mhz"], df_hz=x["w"] * 1e6 / P.NCH))
    return cfgs


def spw_map(plans):
    """STATUS の対応（論理の窓 → 流れ s）。使わない窓は -"""
    out = []
    for a, p in enumerate(plans):
        by_i = {x["i"]: x for x in p["wins"]}
        out += [f"{win_key(a * SPW_NW + i, SPW_NW)}:{by_i[i]['s'] if i in by_i else '-'}" for i in range(SPW_NW)]
    return ",".join(out)


class _SpwRoute:
    """SpW の実機と偽物で同じ振り分け: レコード (core, s) → 論理の窓 j（smap）、頭の照らし、DUMP_K からの読み落とし、コアごとの SEQ の飛び。
    陽性対照 --posctl-spw-map: ADC ごとに同じ NS・SHIFT の 2 本の論理の窓の s を入れ替える（頭の照らしは通り、受け側の IF の照らしが落ちるはず）"""

    def _spw_init(self, cfgs):
        self.smap = {}
        for j, cf in enumerate(cfgs):
            if cf["active"]:
                self.smap[(j // SPW_NW, cf["s"])] = j
        if getattr(self.o, "posctl_spw_map", False):
            for a in range(4):                     # 同じ NS・SHIFT の 2 本（頭の照らしを通り、中身の IF でだけ見える取り違え）
                ss = sorted((s for (c, s) in self.smap if c == a), key=lambda s: self.smap[(a, s)])
                kind = lambda s: (cfgs[self.smap[(a, s)]]["ns"], cfgs[self.smap[(a, s)]]["shift"])
                pr = next(((x, y) for n, x in enumerate(ss) for y in ss[n + 1:] if kind(x) == kind(y)), None)
                if pr:
                    x, y = pr
                    self.smap[(a, x)], self.smap[(a, y)] = self.smap[(a, y)], self.smap[(a, x)]
            self.log("陽性対照: 論理の窓と流れ s の対応を ADC ごとに 2 本（同じ NS・SHIFT）入れ替える（--posctl-spw-map）")
        self.q = [collections.deque() for _ in range(4 * SPW_NW)]
        self.dk = [None] * (4 * SPW_NW)
        self.cseq = [None] * 4
        self.seq_gap = self.hdr_bad = self.stray = 0

    def _spw_route(self, core, s, seq, hw, pay):
        """type 5 のレコード 1 本（CRC・尾は照らした後）"""
        if 0 <= core < 4:
            last = self.cseq[core]
            if last is not None and seq != (last + 1) & 0xFFFFFFFF:
                self.seq_gap += 1
            self.cseq[core] = seq
        j = self.smap.get((core, s))
        if j is None:
            self.stray += 1                        # 動いていない流れ・知らないコアのレコード
            return
        self.q[j].append((core, hw, pay))

    def poll_win(self, j):
        """窓 j の閉じたダンプ（BASE ごと）→ (メタ, 中身（f32 の LazyRec か ndarray）, 読み落とした数 = DUMP_K の飛び)。頭が cfg と合わないレコードは捨てて数える"""
        q = self.q[j]
        cf = self.cfgs[j]
        while q:
            core, hw, pay = q.popleft()
            hw = hw.tolist() if hasattr(hw, "tolist") else hw            # 1 回 3 µs（ボード）。以下は Python の int で
            w4 = hw[4]
            if w4 & 0xFFFF00FFFFFF != cf["w4"] | (core << 40):           # log2N 12・NS・SHIFT・fmt 1・src（G と DUMP_H は見ない）
                l2n, ns, sh, _g, fmt, src = [(w4 >> (8 * i)) & 0xFF for i in range(6)]
                self.hdr_bad += 1
                if self.hdr_bad <= 5:
                    self.log(f"{win_key(j, SPW_NW)}（s {cf['s']}）: レコードの頭 log2N {l2n}・NS {ns}・SHIFT {sh}・fmt {fmt}・src {src}"
                             f"（期待 12・{cf['ns']}・{cf['shift']}・1・{core}）。捨てる")
                continue
            w1, w5, w6 = hw[1], hw[5], hw[6]
            k, last = w1 >> 32, self.dk[j]
            if last is not None and k <= last:
                continue                           # 前の RUN の残り
            self.dk[j] = k
            m = {"seq": w1 & 0xFFFFFFFF, "k": k, "t": hw[3], "h": w4 >> 48, "n": w5 & 0xFFFFFFFF, "sat": w5 >> 32,   # rec_meta と同じ鍵（f0 は使わない）
                 "cfg": w6 & 0xFFFFFFFF, "flags": w6 >> 32}
            return m, pay, (0 if last is None else k - last - 1)
        return None

    def spw_stat(self):
        return dict(seq_gap=self.seq_gap, hdr_bad=self.hdr_bad, stray=self.stray)

    def snap(self, adc, n, nacc, timeout=5.0):
        raise RuntimeError("SpW8 に RAW の流れは無い（SNAP は使えない）")


class _CBund:
    """SpW8 M5b の C の道の窓の束ね（状態は s45fast.SpwScan の win[j]）。Acq が Bundler に求める欄だけを持つ"""

    def __init__(self, sc, j):
        self.sc, self.j, self.drop_why = sc, j, {}

    def _g(self, k):
        return int(self.sc.win[k][self.j])

    n_sum = property(lambda self: self._g("n_sum"))
    drop = property(lambda self: self._g("drop"))
    r_bad = property(lambda self: self._g("r_bad"))
    val_bad = property(lambda self: self._g("val_bad"))
    crc_bad = property(lambda self: self._g("crc_bad"))

    @property
    def r0(self):
        return self._g("r0") if self._g("has_r0") else None

    def stop(self):
        w = self.sc.win
        if not w["cur"][self.j]:
            return None
        w["cur"][self.j] = 0
        w["drop"][self.j] += 1
        self.drop_why["STOP"] = self.drop_why.get("STOP", 0) + 1
        return (self._g("jb"), "STOP", self._g("cnt"))


class SpwBackend(_SpwRoute, HwBackend):
    """SpW8（BIT_KIND 7・BIT_REV 10）の裏。コア 4 個（ADC_A〜D）× DDC の流れ 8 本。RAW の流れは無い（SNAP は断る）。
    --fast --fast-ring で C の道（cmode）: pump がリングの [R, W) を s45fast.SpwScan で 1 回なめ、束ができる・捨てるたびに on_spw（Acq）を呼ぶ。
    Python の道（Ring.read → 列 → poll_win → Bundler）は 32 窓 × 10.24 ms に追いつかない（M5b の実機: 1 本 ≒ 270 µs、20.48 ms で 60 s 回すと溢れた）"""

    def __init__(self, opts, log):
        super().__init__(opts, log)
        self.cmode = bool(getattr(opts, "fast", False) and getattr(opts, "fast_ring", False))
        self.on_spw = None
        self.discard = False

    def open(self):
        import spectrometer as S
        import timetest as T
        import window as W
        import timebase as TB
        import s45core as SC
        self.S, self.T, self.W, self.TB, self.SC = S, T, W, TB, SC
        from pynq import Overlay
        import xrfdc                               # Overlay() より前に import する（VERSIONS.md）
        S.setup_clocks(self.o.clkin, self.o.ref)
        self._setup_lmx()
        self.ol = Overlay(self.o.bitfile)
        if not isinstance(self.ol.rfdc, xrfdc.RFdc):
            raise RuntimeError("RFDC に xrfdc のドライバが当たっていない")
        S.check_tiles(self.ol.rfdc, 2)
        time.sleep(self.o.settle)
        self.cores, tmm = SC.discover(self.ol, bit_kind=SPW_BIT_KIND, ncore=4, bit_rev_min=SPW_BIT_REV)
        if [c.adc for c in self.cores] != [0, 1, 2, 3]:
            raise RuntimeError(f"コアの CORE_PORT が {[c.adc for c in self.cores]}（期待 [0, 1, 2, 3]）")
        for c in self.cores:
            if c.nstream != SPW_H or any(x.kind != SC.KIND_DDC for x in c.streams):
                raise RuntimeError(f"{c.name} の流れが DDC × {SPW_H} でない（NSTREAM {c.nstream}・KIND {[x.kind for x in c.streams]}）")
            if (c.caps & 3) != 3:
                raise RuntimeError(f"{c.name} の CAPS の [0]〜[1]（レコード・TP）が無い（{c.caps:#x}）")
            if c.base_beats != BASE_BEATS:
                raise RuntimeError(f"{c.name} の BASE_BEATS {c.base_beats}（{BASE_BEATS} を期待）")
            prm = int(c.m.read(W.A_BASE + S.R_TP_PARAM)) & 0xFFFFFFFF
            if prm != S.TP_PARAM_EXPECT:
                raise RuntimeError(f"{c.name} の TP_PARAM {prm:08x}（期待 {S.TP_PARAM_EXPECT:08x}）")
        self.wms = [c.m for c in self.cores]
        self.tc = TB.TimeCore(tmm)
        self.tc.configure(src=self.o.path, tol=1)
        self.tb = TB.Timebase(self.tc, path=self.o.path, log=self.log)
        self.TpStream = make_tp_reader(S)
        c0 = self.cores[0]
        self.ids = dict(win=f"{c0.streams[0].sid:08x}", adc=f"{c0.if_id:08x}", time=f"{self.tc.rd(0x00):08x}", proj=f"{c0.proj:08x}",
                        kind=SPW_KIND, usr=self._usr_access(), **self._lmx_ids())
        self.clock = Clock(None, {})
        import plring as PR
        rip = getattr(self.ol, "s45_ring_0", None)
        if rip is None:
            raise RuntimeError("ol.s45_ring_0 が無い")
        self.ring = PR.Ring(rip.mmio, ring_mib_of(self.o, G_RING_MIB) << 20)
        self.ring.enable(True)
        self.amap = {c.adc: i for i, c in enumerate(self.cores)}
        self._spw_init(spw_cfgs(default_settings_spw(), spw_plan(default_settings_spw())))
        self.log(f"リング: BASE {self.ring.base:#x} / SIZE {self.ring.size}（SpW8: 窓 32 本 × 16 KiB の f32 のレコード / 10.24 ms）")
        self.ids["read"] = "ring"
        self.ids["tcal"] = self.tb.cal_state
        self.ids["board"] = (self.tb.board or {}).get("id", "-")
        self.bit_kind = c0.bit_kind
        self.anchor()

    def _ctrl(self, c, v):
        c.streams[0].wr(self.SC.S_CTRL, v)        # コアに効く（spw_regs: どの流れの CTRL でも）

    def _rec_off(self):
        for c in self.cores:
            c.wr(TP_REC_CTRL, TP_REC_K << 8)       # 窓のレコードは RUN の間だけ出る（流れの REC_CTRL は無い）

    def _drain(self):
        self.ring.read()
        for d in self.q:
            d.clear()
        self.ring.release()

    def disarm(self):
        T, W = self.T, self.W
        for c in self.cores:
            self._ctrl(c, SPW_CT_CANCEL)
            c.m.write(W.A_BASE + T.RA_TP_CTRL, T.TP_DISARM)

    def _arm_tc(self, sa):
        try:
            self.tc.arm(sa)
        except Exception:
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self.disarm()
            raise

    def start(self, st, at_beat, force):
        """4 コアとも STOP → 窓の設定（計画の流れ 8 本）・SHIFT・NG・NDUMP・CFG_ID → ARM_WRST（tint の格子）→ 約束・WRST_CNT・WCUR の読み返し →
        TP → ARM_RUN と TP_ARM を tint の格子で。戻り値 START_AT"""
        SC, T, W = self.SC, self.T, self.W
        if self.clock.ok:
            try:
                self.tb.check()
            except Exception as e:
                self.clock.ok, self.clock.err = False, str(e)
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        self.disarm()
        if st.get("fmt", "f32") != "f32":
            raise RuntimeError("SpW の bit は fmt=f32 だけ（ADR 0029）")
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        plans = spw_plan(st)
        self.cfgs = spw_cfgs(st, plans)
        sh = {}
        for j, cf in enumerate(self.cfgs):
            if cf["active"]:
                sh[(j // SPW_NW, cf["s"])] = cf["shift"]
        n0 = []
        for a, c in enumerate(self.cores):
            self._ctrl(c, SPW_CT_STOP)
            for s, r in enumerate(plans[a]["streams"]):
                x = c.streams[s]
                for name, off in SPW_REGS:
                    x.wr(off, r[name])
                x.wr(SC.S_SHIFT, sh.get((a, s), SPW_SHIFT))
            c.streams[0].wr(SC.S_CFG, st["cfg"])  # CFG_ID はコアで 1 つ
            c.wr(C_NG, SPW_NG)
            c.wr(C_NDUMP, 0)
            self._ctrl(c, SPW_CT_FCLR)
            n0.append(c.rd(C_WRST_CNT))
            self._ctrl(c, SPW_CT_ARMWRST)
        sa_w = self.grid_after(self.now_beat() + BEATS_PER_SEC // 2)
        self._arm_tc(sa_w)
        self._wait_fired(5.0)
        time.sleep(0.01)
        for a, c in enumerate(self.cores):
            t_e = time.time() + 1.0
            while c.streams[0].rd(SC.S_CTRL) & (1 << 4):
                if time.time() > t_e:
                    raise RuntimeError(f"{c.name}: WRST が明けない（CTRL {c.streams[0].rd(SC.S_CTRL):#x}）")
                time.sleep(0.001)
            bad, cf, n1 = c.rd(C_WRST_BAD), c.rd(C_CORE_FLAGS), c.rd(C_WRST_CNT)
            if (cf & 1) or n1 != (n0[a] + 1) & 0xFFFFFFFF:
                raise RuntimeError(f"{c.name}: WRST が通らない（CORE_FLAGS {cf:#x}・WRST_BAD {bad:#x}・WRST_CNT {n0[a]} → {n1}）")
            for s, r in enumerate(plans[a]["streams"]):
                x = c.streams[s]
                want = ((r["WK"] & 0x3F) | ((r["WNS"] & 7) << 8), r["WDPHI"], (r["WFL"] & 3) | ((r["WSL"] & 0xF) << 4) | ((r["WG"] & 0xF) << 8))
                got = (x.rd(S_WCUR), x.rd(S_WCUR_DPHI), x.rd(S_WCUR2))
                if got != want:
                    raise RuntimeError(f"{c.name} の流れ {s}: WRST の後の WCUR・WCUR_DPHI・WCUR2 {[hex(v) for v in got]}（書いた値 {[hex(v) for v in want]}）")
        for c in self.cores:
            c.m.write(W.A_BASE + T.RA_TP_N, TP_N)
            c.wr(TP_REC_CTRL, (TP_REC_K << 8) | 1)
        self._spw_init(self.cfgs)
        if self.cmode:
            self._c_init()
        self._drain()
        sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        for c in self.cores:
            self._ctrl(c, SPW_CT_FCLR | SPW_CT_ARMRUN)
            c.m.write(W.A_BASE + T.RA_TP_CTRL, T.TP_ARM)
        self._arm_tc(sa)
        self.sa = sa
        self.armed = True
        return sa

    def begin(self):
        S, T, W, SC = self.S, self.T, self.W, self.SC
        runts = []
        for c in self.cores:
            x = c.streams[0]
            runts.append(x.rd(SC.S_RUN_T) | (x.rd(SC.S_RUN_T + 4) << 32))
            if not x.rd(SC.S_CTRL) & 1:
                raise RuntimeError(f"{c.name} が RUN に入っていない（CTRL {x.rd(SC.S_CTRL):#x}・CORE_FLAGS {c.rd(C_CORE_FLAGS):#x}）")
        runts += [T.tp_run_t(c.m) for c in self.cores]
        bad = [i for i, t in enumerate(runts) if t != self.sa + 1]
        for j, cf in enumerate(self.cfgs):
            if cf["active"]:
                x = self.cores[j // SPW_NW].streams[cf["s"]]
                if x.rd(SC.S_RUN_SHIFT) != cf["shift"]:
                    raise RuntimeError(f"{win_key(j, SPW_NW)}（s {cf['s']}）: RUN_SHIFT {x.rd(SC.S_RUN_SHIFT)}（書いた値 {cf['shift']}）")
        self.tps, self.anch = [], []
        for c in self.cores:
            tp = _WinTp(c.m, W.A_BASE)
            tf0 = tp.rd(S.R_TP_F0_LO) | (tp.rd(S.R_TP_F0_HI) << 32)
            self.tps.append(self.TpStream(tp, TP_N, tf0))
            self.anch.append(self._tanch(c.m))
        self.gap0 = [int(c.m.read(W.A_BASE + T.RA_GAP)) for c in self.cores]
        self.running = True
        return dict(run_t_bad=bad)

    def _c_init(self):
        """C の道の窓の状態（START ごと）。smap は _spw_init の対応（陽性対照の入れ替えも）"""
        import s45fast as F
        sc = F.SpwScan(4 * SPW_NW, P.NCH, BASE_BEATS, posctl=1 if getattr(self.o, "posctl_noacc", False) else 0)
        for j, cf in enumerate(self.cfgs):
            if cf["active"]:
                sc.win["n_sum"][j], sc.win["pl_nacc"][j] = cf["n_sum"], cf["pl_nacc"]
                sc.win["w4"][j] = cf["w4"] | ((j // SPW_NW) << 40)
        for (a, s_), j in self.smap.items():
            sc.smap[a * 256 + s_] = j
        self.sc = sc
        self.accp = sc.win["acc"].tolist()        # 器の番地（Acq._spw_ev が記録の C の道に渡す）
        self.crc_py = 0
        self.discard = False
        self.c_t = [0.0, 0.0, 0.0]                 # 診断: C のなめ・束の知らせ（記録を含む）・Python で読んだレコード [s]
        self.c_n = [0, 0]

    def _one(self, r):
        """C の道が止まった type 5 でないレコード 1 本（TP など）を Python で読む。→ 次の R"""
        import plring as PR
        rg = self.ring
        p = r % rg.size
        i = p >> 3
        h = rg.a64[i:i + 8].tolist()
        pb = h[7] & 0xFFFFFFFF
        nb = 64 + pb
        t0w, t1w = rg.a64[(p + nb) >> 3:((p + nb) >> 3) + 2].tolist()
        seq, ty, core, s = h[1] & 0xFFFFFFFF, h[0] >> 40 & 0xFF, h[0] >> 48 & 0xFF, h[0] >> 56 & 0xFF
        ok = (t0w & 0xFFFFFFFF) == PR.MAGIC_E and (t0w >> 32) == seq and zlib.crc32(rg.a8[p:p + nb]) == (t1w & 0xFFFFFFFF)
        if not ok:
            self.crc_py += 1
        elif ty == TYPE_TP and s == 0xFF and core in self.amap and self.running:
            self.tps[self.amap[core]].feed(seq, h[5] & 0xFFFFFFFF, rg.a64[i + 8:i + 8 + (pb >> 3)].copy(), TP_REC_K)
        else:
            self.stray += 1
        return (r + nb + 64) & 0xFFFFFFFF

    def _pump_c(self):
        import plring as PR
        rg = self.ring
        t0 = time.perf_counter()
        w = rg.rd(PR.R_W)
        n_all = (w - rg.r) & 0xFFFFFFFF
        if n_all:                                  # Ring.read と同じに [R, W) のキャッシュをまとめて捨てる
            p0 = rg.r % rg.size
            k = min(n_all, rg.size - p0)
            rg._invalidate(p0, k)
            if n_all > k:
                rg._invalidate(0, n_all - k)
        t1 = time.perf_counter()
        r, sc, nrec = rg.r, self.sc, 0
        pc = time.perf_counter
        while True:
            ta = pc()
            st, r, evs = sc.scan(rg.a8p, rg.size, r, w)
            tb = pc()
            self.c_t[0] += tb - ta
            if st == 1:
                if self.on_spw is not None and not self.discard:
                    for e in evs:
                        self.on_spw(e)
                self.c_t[1] += pc() - tb
                self.c_n[1] += len(evs)
            elif st == 2:
                r = self._one(r)
                self.c_t[2] += pc() - tb
                nrec += 1
            elif st == 0:
                break
            else:
                raise RuntimeError(f"リングの C の道: {'magic が違う' if st == -1 else 'PAD の長さが違う'}（位置 {r}、W {w}）")
        rg.r = r
        rg.wr(PR.R_R, r)
        self.seq_gap, self.stray_c, self.hdr_bad = int(sc.ctr[0]), int(sc.ctr[1]), int(sc.ctr[2])
        self.ring_crc = int(sc.ctr[3]) + self.crc_py
        self.last_pump = (t1 - t0, time.perf_counter() - t1)
        return nrec

    def spw_stat(self):
        d = super().spw_stat()
        if self.cmode and hasattr(self, "sc"):
            d["stray"] = self.stray + getattr(self, "stray_c", 0)
            d.update(c_scan_s=round(self.c_t[0], 2), c_ev_s=round(self.c_t[1], 2), c_one_s=round(self.c_t[2], 2), c_ev=self.c_n[1],
                     c_rec=int(self.sc.win["pl_dumps"].sum()))
        return d

    def pump(self):
        """リングを [R, W) まで読み、窓のレコード（type 5）は論理の窓の列へ（C の道は束ねまで）、TP（s 0xFF）は ADC の欄へ"""
        if self.cmode and hasattr(self, "sc"):
            self.n_pump += 1
            self._posctl_stall()
            return self._pump_c()
        self.n_pump += 1
        self._posctl_stall()
        t0 = time.perf_counter()
        sm = self.smap
        lazy = (lambda core, s, ty: ty == TYPE_SPW and (core, s) in sm) if self.lazy_wins and self.running else None
        recs = self.ring.read(lazy)
        t1 = time.perf_counter()
        route = self._spw_route
        for core, s, seq, hw, pay, crc_ok, tail_ok in recs:
            if crc_ok is False or not tail_ok:     # crc_ok None = LazyRec（PL の CRC は束ねのときに C で照らす）
                self.ring_crc += 1
                continue
            ty = int(hw[0]) >> 40 & 0xFF
            if ty == TYPE_SPW:
                route(core, s, seq, hw, pay)
            elif ty == TYPE_TP and s == 0xFF and core in self.amap and self.running:
                self.tps[self.amap[core]].feed(seq, int(hw[5]) & 0xFFFFFFFF, pay, TP_REC_K)
        self.last_pump = (t1 - t0, time.perf_counter() - t1)
        return len(recs)

    def release(self):
        """列に残った LazyRec を写してから R を進める（HwBackend.release と同じ。列の要素は (core, hw, pay)）"""
        rg = self.ring
        if rg is None or not rg.hold:
            return
        for d in self.q:
            if not any(not isinstance(x[2], np.ndarray) for x in d):
                continue
            keep = []
            for core, hw, pay in d:
                if not isinstance(pay, np.ndarray):
                    pay, ok = pay.materialize()
                    self.n_mat += 1
                    if not ok:
                        self.ring_crc += 1
                        continue
                keep.append((core, hw, pay))
            d.clear()
            d.extend(keep)
        rg.release()

    def stop(self):
        if not self.running:
            self.disarm()
            self.tc.wr(0x08, self.TB.TimeCore.CTRL_CANCEL)
            self._rec_off()
            return []
        for c in self.cores:
            self._ctrl(c, SPW_CT_STOP)
        self.discard = True                        # 止めた後に閉じた束は記録しない（Python の道も列に置くだけ）
        self.pump()
        self._rec_off()
        self.running = False
        out = []
        for i, c in enumerate(self.cores):
            try:
                af1, at1 = self._tanch(c.m)
                af, at = self.anch[i]
                gap1 = int(c.m.read(self.W.A_BASE + self.T.RA_GAP))
                out.append(dict(adc=i, anch_dev=(at1 - at) - (af1 - af) * 512, gap=gap1 - self.gap0[i]))
            except Exception as e:
                out.append(dict(adc=i, err=str(e)))
        return out

    def close(self):
        if self.ring is None:
            return
        try:
            for c in self.cores:
                self._ctrl(c, SPW_CT_STOP)
        finally:
            super().close()


class FakeSpwBackend(_SpwRoute, FakeBackend):
    """PL なしの SpW8。計画の流れのレジスタ（WK・WDPHI）から窓の中心の IF を出し、BASE ごとのダンプ（type 5 の頭の語と f32 × 4096）を
    流れ (コア, s) ごとに作って、実機と同じ振り分け（smap）に通す。中身はどの ch も「レジスタから出した窓の中心の IF [MHz]」、
    ch 1 だけその 2 倍（IF の昇順では i 2046）。受け側は束の値 / n_sum を記録の頭の if_mhz と照らす（読み替えの誤りが見える）"""

    def open(self):
        super().open()
        self.ids["kind"] = SPW_KIND
        self.bit_kind = SPW_BIT_KIND
        self.lazy_wins = set()
        self._spw_init(spw_cfgs(default_settings_spw(), spw_plan(default_settings_spw())))

    def grid_after(self, beat):
        q = getattr(self, "tint_beats", G_BEATS)
        return -(-int(beat) // q) * q

    def start(self, st, at_beat, force):
        import spwplan
        if not self.clock.ok and not force:
            raise RuntimeError("時刻を答えられない（錨が無い・PPS が来ていない）。ANCHOR か force=1")
        if st.get("fmt", "f32") != "f32":
            raise RuntimeError("SpW の bit は fmt=f32 だけ（ADR 0029）")
        self.tint_beats = check_tint(st["tint"]) * BASE_BEATS
        plans = spw_plan(st)
        self.cfgs = spw_cfgs(st, plans)
        self.cfg = st["cfg"]
        self.fl = []                               # 動く流れ: (コア, s, NS, SHIFT, 中身)
        sh = {(j // SPW_NW, cf["s"]): cf["shift"] for j, cf in enumerate(self.cfgs) if cf["active"]}
        for a, p in enumerate(plans):
            for s, r in enumerate(p["streams"]):
                if r["WFL"] >= SPW_E:
                    continue                       # 止める窓
                c = spwplan.SC * r["WK"] + spwplan.d_of(r["WDPHI"])
                x = np.full(P.NCH, spwplan.FS - c, np.float32)
                x[1] *= 2
                self.fl.append((a, s, r["WNS"], sh[(a, s)], x))
        self._spw_init(self.cfgs)
        self.sa = self.grid_after(max(at_beat or 0, self.now_beat() + BEATS_PER_SEC // 2))
        return self.sa

    def begin(self):
        r = super().begin()
        self.n_next = 0                            # 次の BASE のダンプの番号（全部の流れで同じ格子）
        self.pseq = [0] * 4
        return r

    def pump(self):
        if not self.running:
            return 0
        now = self.now_beat()
        n = 0
        while self.sa + 1 + (self.n_next + 1) * BASE_BEATS + 20000 <= now:   # 閉じてから読めるまで ≒ 80 µs
            for a, s, ns, sh, x in self.fl:
                L = spw_frame(ns)
                kf = 100 + s                       # K_F（鎖の遅れ）。偽物は流れごとに一定
                t = self.sa + 1 + self.n_next * BASE_BEATS + kf
                hw = np.array([TYPE_SPW << 40, self.pseq[a] | (self.n_next << 32), (t - kf) // L, t,
                               12 | (ns << 8) | (sh << 16) | (1 << 32) | (a << 40), BASE_BEATS // L, self.cfg, 0], np.uint64)
                self._spw_route(a, s, self.pseq[a], hw, x)
                self.pseq[a] = (self.pseq[a] + 1) & 0xFFFFFFFF
                n += 1
            self.n_next += 1
        return n

    def ring_stat(self):
        return None


# ================================================================ 取得の本体
class Acq:
    IDLE, ARMED, RUN, ERROR = "IDLE", "ARMED", "RUN", "ERROR"

    def __init__(self, conn, ring, opts):
        self.conn, self.ring, self.o = conn, ring, opts
        self.wide = bool(getattr(opts, "wide", False))               # proj023: SAM45-Wide（SLICE の流れ）
        self.g21 = bool(getattr(opts, "g21", False))                 # proj024: 2G-1（FULL の流れ 1 本）
        self.g22 = bool(getattr(opts, "g22", False))                 # proj025: 2G-2（FULL の流れ 2 本）
        self.g24 = bool(getattr(opts, "g24", False))                 # proj027: 2G-4（FULL の流れ 4 本）
        self.spw = bool(getattr(opts, "spw", False))                 # YATSUGATAKE M5b: SpW8（論理の窓 8 本 / ADC）
        if self.wide + self.g21 + self.g22 + self.g24 + self.spw > 1:
            raise SystemExit("--wide・--g21・--g22・--g24・--spw は同時に使えない")
        self.nw = SPW_NW if self.spw else NW                         # 窓 / ADC（鍵 A0〜A{nw−1}）
        self.nslot = 4 * self.nw
        self.g2 = G4_GEOM if self.g24 else G2_GEOM if self.g22 else None   # proj027: 多コアの 2G の形（2G-2・2G-4 は同じ道）
        nb = getattr(opts, "net_budget_mbs", None)
        self.net_budget = NET_BUDGET_MBS if nb is None else float(nb)   # 2G-4 の M5: SET の tint の照合（INTERFACE 4.5）。0 で照らさない
        self.st = (default_settings_spw() if self.spw else default_settings_g22(self.g2) if self.g2 else default_settings_g21() if self.g21 else
                   default_settings_wide() if self.wide else default_settings())
        self.plans = spw_plan(self.st) if self.spw else None          # SpW: 今の組の計画（STATUS の対応）
        self.state = self.IDLE
        self.seq = 0
        self.drop = dict(n=0, first=None, last=None, pending=None)
        self.err = None
        self.forced = False
        self.posctl = dict(corrupt=opts.posctl_corrupt, gap=opts.posctl_gap)
        self.proto = int(getattr(opts, "proto", P.VERSION))          # proj021 2-3c: 送る版（1 = 今までの v1）
        self.f32_trunc = bool(getattr(opts, "posctl_f32_trunc", False))
        self.fast = None                                            # proj029 1: --fast で SPEC の記録（FULL）の中身と CRC を C で（s45fast）
        if getattr(opts, "fast", False):
            import s45fast
            self.fast = s45fast
        self.posctl_noacc = 1 if getattr(opts, "posctl_noacc", False) else 0   # proj036: 陽性対照（束ねで足さずに写す）
        self.fast_ring = bool(getattr(opts, "fast_ring", False))   # proj029 2: --fast-ring で SPEC のレコードを写さずにリングの上から（n_sum 1 の FULL）
        if self.fast_ring and self.fast is None:
            raise SystemExit("--fast-ring は --fast と一緒に")
        self.hist = np.zeros(1001, np.int64)      # 1 周の時間（0.1 ms 刻み、100 ms で頭打ち）
        self.cal = getattr(opts, "tp_cal", None)    # TP の dBm の較正（s45cal、specd が起動時に読む）。bit の ID は open の後で照らす
        self.cal_msg = "較正ファイルが無い" if self.cal is None else "未確認"
        self.tp_last = [None] * 4                  # ADC ごとの直近の TP（σ_x²、最後に書き出した記録の平均）
        self.tpj = [TpJump(phase=250 * i) for i in range(4)]    # proj021 B2: TP の跳ねの見張り（tpjump.py。START で初めから。B2b: σ の計算し直しを ADC ごとにずらす）
        self.tpj_on = not getattr(opts, "no_tp_jump", False)   # --no-tp-jump: 見張りを止める（1 周の重さの比べ）
        self.t_put = 0.0                            # proj029 1c: その周の put の時間の和
        self.f_put = 0                              # proj029 1d: その周の put の中のページフォルト
        self._reset_counters()

    def log(self, *a):
        print("[acq]", *a, flush=True)

    def _reset_counters(self):
        self.n_dump = [0] * self.nslot
        self.active = [True] * self.nslot          # proj023: B 4 の流れ 1 は空（数えない）
        self.n_miss = [0] * self.nslot
        self.kgap = [0] * self.nslot
        self.last_k = [None] * self.nslot
        self.h_or = 0
        self.fl_or = 0
        self.sat = 0
        self.loop_max = 0.0
        self.loop_max_at = 0                       # proj021 2-3a: 最大だった周の番号（RUN から）
        self.bund = [None] * self.nslot            # proj021 2-3b: 窓ごとの Bundler（START で作る）
        self.pl_dumps = [0] * self.nslot
        self.loop_slow = 0                         # 1 周が tint を越えた回数
        self.n_loop_log = 0                        # proj025 4c: --loop-log-ms で残した周の数
        self.hist[:] = 0
        self.n_loop = 0
        self.ndump_target = 0
        self.start_at = None
        self.stop_info = None

    # ---- 溜まりへ
    def _next_seq(self):
        self.seq += 1
        return self.seq

    def _put(self, rtype, payload_parts, crc):
        """記録を溜まりに置く。入らなければ捨てて数える。**一度溢れたら、空きが溜まりの 1/4 に戻るまで捨て続ける**
        （空きの縁で 1 個おきに入る・捨てるを繰り返し、DROP の EVENT が細切れになるのを避ける）。DROP の EVENT は再開の直前に置く"""
        d = self.drop
        if d["pending"] is not None:
            if rtype == P.T_EVENT or self.ring.cap - self.ring.used() >= self.ring.cap // 4:
                self._flush_drop()                    # EVENT（小さく、START・STOP を落としたくない）は空きがあれば割り込む
        t_put0 = time.perf_counter()               # proj029 1c: 窓の記録の内訳（put）
        f_put0 = resource.getrusage(resource.RUSAGE_SELF).ru_minflt    # proj029 1d: put の中のページフォルト
        try:
            self._put1(rtype, payload_parts, crc, d)
        finally:
            self.t_put += time.perf_counter() - t_put0
            self.f_put += resource.getrusage(resource.RUSAGE_SELF).ru_minflt - f_put0

    def _put1(self, rtype, payload_parts, crc, d):
        seq = self._next_seq()
        if self.posctl["gap"] and seq % self.posctl["gap"] == 0:
            return                                    # 陽性対照: 番号だけ進めて黙って捨てる（受け側の「説明のない欠け」が数えるはず）
        plen = sum(memoryview(p).nbytes for p in payload_parts)
        if self.posctl["corrupt"] and seq % self.posctl["corrupt"] == 0:
            payload_parts = list(payload_parts)
            b = bytearray(payload_parts[-1]); b[len(b) // 2] ^= 0x01
            payload_parts[-1] = bytes(b)              # 陽性対照: CRC を計算した後に 1 bit 反転（受け側の CRC の不一致が数えるはず）
        ok = (d["pending"] is None or rtype == P.T_EVENT) and self.ring.put([P.header(rtype, plen, crc, seq, self.proto)] + list(payload_parts))
        if not ok:
            d["n"] += 1
            if d["pending"] is None:
                d["pending"] = [seq, seq, 1]
            else:
                d["pending"][1] = seq; d["pending"][2] += 1

    def _flush_drop(self):
        a, b, n = self.drop["pending"]
        p = P.event_payload(dict(ev="DROP", **{"from": a, "to": b, "n": n}))
        seq = self.seq + 1
        if self.ring.put([P.header(P.T_EVENT, len(p), P.crc32(p), seq, self.proto), p]):
            self.seq = seq
            self.drop["pending"] = None
            self.log(f"溜まりが溢れて捨てた: seq {a}〜{b}（{n} 個）")

    def event(self, d):
        p = P.event_payload(d)
        self._put(P.T_EVENT, [p], P.crc32(p))

    # ---- 命令
    def handle(self, cmd):
        op = cmd.get("op")
        try:
            if op == "status":
                return dict(ok=True, **self.status())
            if op == "id":
                return dict(ok=True, ids=self.be.ids, version=VERSION, adcs=4, nw=self.nw, fake=bool(self.o.fake))
            if op == "get":
                return dict(ok=True, settings=self.st)
            if op == "cal":
                return dict(ok=True, cal=self._cal_pub(), msg=self.cal_msg, time=self._tcal_pub())
            if op == "set":
                if self.state not in (self.IDLE, self.ERROR):
                    return dict(ok=False, code="STATE", msg=f"{self.state} の間は SET できない（STOP の後に）")
                st = self.st
                new = dict(tint=st["tint"], cfg=st["cfg"], fmt=st.get("fmt", "f32"), wins=[dict(w) for w in st["wins"]])
                if self.spw:
                    new["kind"] = SPW_KIND
                    for k, v in cmd["kv"].items():
                        self._set1_spw(new, k, v)
                    check_tint(new["tint"])
                    if new["fmt"] != "f32":
                        raise ValueError(f"fmt={new['fmt']}: SpW の bit のリングは PL が丸めた f32 で、u64 が無い（fmt=f32 だけ。ADR 0029）")
                    plans = spw_plan(new)                       # 計画できない組は ADC ごとの理由つきで断る（今の組のまま。ADR 0028）
                    check_net(new, sum(1 for w in new["wins"] if w["on"]) * P.NCH, self.net_budget)
                    self.st, self.plans = new, plans
                    return dict(ok=True)
                if self.g2 is not None:
                    new.update(kind=self.g2.kind, src=list(st["src"]), shift=list(st["shift"]))
                    for k, v in cmd["kv"].items():
                        self._set1_g22(new, k, v)
                    check_tint(new["tint"])
                    check_g22(new, self.g2)
                    check_net(new, self.g2.ncore * self.g2.nch, self.net_budget)   # 2G-4 の M5: 予算を越える tint を断る
                    self.st = new
                    return dict(ok=True)
                if self.g21:
                    new.update(kind="g21", src=st["src"], shift=st["shift"])
                    for k, v in cmd["kv"].items():
                        self._set1_g21(new, k, v)
                    check_tint(new["tint"])
                    check_g21(new)
                    check_net(new, G_NCH, self.net_budget)
                    self.st = new
                    return dict(ok=True)
                if self.wide:
                    new["kind"] = "wide"
                    for k, v in cmd["kv"].items():
                        self._set1_wide(new, k, v)
                    check_tint(new["tint"])
                    check_wide(new)
                    check_net(new, 4 * NW * P.NCH, self.net_budget)
                    self.st = new
                    return dict(ok=True)
                for k, v in cmd["kv"].items():
                    self._set1(new, k, v)
                check_tint(new["tint"])
                check_net(new, 4 * NW * P.NCH, self.net_budget)
                for ws in new["wins"]:
                    nacc_of(new["tint"], ws["ns"])
                    import window as W
                    W.window_params(ws["if_mhz"], 512.0 / (1 << ws["ns"]))
                self.st = new
                return dict(ok=True)
            if op == "anchor":
                if self.state in (self.ARMED, self.RUN):
                    return dict(ok=False, code="STATE", msg="RUN の間は錨を打ち直さない")
                ok, e = self.be.anchor()
                return dict(ok=ok, code="TIME", msg=e) if not ok else dict(ok=True)
            if op == "start":
                return self._start(cmd)
            if op == "snap":
                return self._snap(cmd)
            if op == "stop":
                if self.state not in (self.ARMED, self.RUN):
                    return dict(ok=False, code="STATE", msg=f"{self.state} なので止めるものが無い")
                self._stop("命令")
                return dict(ok=True)
            if op == "quit":
                if self.state in (self.ARMED, self.RUN):
                    self._stop("終了")
                return dict(ok=True, quit=True)
            return dict(ok=False, code="CMD", msg=f"知らない命令 {op}")
        except (ValueError, KeyError, SystemExit) as e:
            return dict(ok=False, code="ARG", msg=str(e))
        except Exception as e:
            self.log(traceback.format_exc())
            return dict(ok=False, code="FAIL", msg=f"{type(e).__name__}: {e}")

    def _set1_g21(self, new, k, v):
        """proj024: tint・fmt・cfg と、src（FULL の入力の ADC: A〜D か 0〜3。次の WRST で効く）・shift（RUN で効く）。
        A0.src・A0.shift・all.shift も同じ（流れは A0 の 1 本だけ。A1〜D1 は ERR）"""
        if k in ("tint", "fmt", "cfg"):
            return self._set1(new, k, v)
        name, _, field = k.partition(".")
        if field:
            if name.upper() not in ("A0", "ALL") or (name.upper() == "ALL" and field != "shift"):
                raise ValueError(f"知らない設定 {k}（2G-1 の流れは A0 の 1 本: src・shift・A0.src・A0.shift・all.shift）")
        else:
            field = name
        if field == "src":
            u = str(v).upper()
            if u in ("A", "B", "C", "D"):
                new["src"] = "ABCD".index(u)
            elif u in ("0", "1", "2", "3"):
                new["src"] = int(u)
            else:
                raise ValueError(f"{k}: src は A〜D（0〜3）")
        elif field == "shift":
            x = int(v)
            if x not in range(16):
                raise ValueError(f"{k}: SHIFT は 0..15")
            new["shift"] = x
        else:
            raise ValueError(f"知らない設定 {k}（tint・fmt・cfg・src・shift）")

    def _set1_g22(self, new, k, v):
        """proj025: tint・fmt・cfg と、A0.src・B0.src（コア 0・1 の FULL の入力の ADC: A〜D か 0〜3。次の WRST で効く。2 コアに同じ ADC も可 = E-4）・
        A0.shift・B0.shift（RUN で効く）・all.shift・shift（両方）。src だけ（窓なし）と、流れの無い窓（A1・C0 など）は ERR。
        proj027: 2G-4 は A0〜D0（コア 0〜3）。窓の鍵とコアの数は self.g2 から"""
        g = self.g2
        if k in ("tint", "fmt", "cfg"):
            return self._set1(new, k, v)
        name, _, field = k.partition(".")
        nu = name.upper()
        keys = "・".join(f"{w}.src・{w}.shift" for w in g.keys)
        if not field:
            if nu == "SHIFT":
                cs, field = list(range(g.ncore)), "shift"
            else:
                raise ValueError(f"知らない設定 {k}（{g.name} は {keys}・all.shift・shift。src は窓を付ける）")
        elif nu == "ALL" and field == "shift":
            cs = list(range(g.ncore))
        elif nu in g.keys:
            cs = [g.keys.index(nu)]
        else:
            raise ValueError(f"知らない設定 {k}（{g.name} の流れは {'・'.join(g.keys)} の {g.ncore} 本）")
        if field == "src":
            u = str(v).upper()
            if u in ("A", "B", "C", "D"):
                x = "ABCD".index(u)
            elif u in ("0", "1", "2", "3"):
                x = int(u)
            else:
                raise ValueError(f"{k}: src は A〜D（0〜3）")
        elif field == "shift":
            x = int(v)
            if x not in range(16):
                raise ValueError(f"{k}: SHIFT は 0..15")
        else:
            raise ValueError(f"知らない設定 {k}（src・shift）")
        for c in cs:
            new[field][c] = x

    def _set1_wide(self, new, k, v):
        """proj023: tint・fmt・cfg と、A.b / A0.b（束ね B、コアで 1 つ）・A.shift / A0.shift（コアで 1 つ）・A0.s0 / A0.ch0（流れの最初の ch）。all.b・all.shift も"""
        if k in ("tint", "fmt", "cfg"):
            return self._set1(new, k, v)
        name, _, field = k.partition(".")
        nu = name.upper()
        if nu == "ALL":
            js = list(range(4 * NW))
        elif len(nu) == 1 and nu in "ABCD":
            js = [NW * "ABCD".index(nu) + s for s in range(NW)]
        elif len(nu) == 2 and nu[0] in "ABCD" and nu[1] in "01":
            js = [NW * "ABCD".index(nu[0]) + int(nu[1])]
        else:
            raise ValueError(f"知らない設定 {k}（tint・fmt・cfg・A.b・A.shift・A0.s0・all.b・all.shift …）")
        if field in ("b", "shift"):
            js = sorted({NW * (j // NW) + s for j in js for s in range(NW)})     # コアで 1 つ
            x = int(v)
            if field == "b" and x not in W_LB:
                raise ValueError(f"{k}: B は 1・2・4")
            if field == "shift" and x not in range(16):
                raise ValueError(f"{k}: SHIFT は 0..15")
            for j in js:
                new["wins"][j][field] = x
        elif field in ("s0", "ch0"):
            if len(nu) != 2:
                raise ValueError(f"{k}: s0 は流れごと（A0.s0 のように）")
            new["wins"][js[0]]["s0"] = int(v)
        else:
            raise ValueError(f"知らない流れの設定 {k}（b・shift・s0）")

    def _set1_spw(self, new, k, v):
        """YATSUGATAKE M5b（ADR 0028）: tint・fmt・cfg と、論理の窓の A0.if・A0.bw（128/64/32/16/8）・A0.ns（1〜5）・A0.shift・A0.on（0/1）・
        A0.coarse（auto / near / alt: 粗い ch を決め打つ試験の口）。A.shift のように ADC だけ・all.shift・shift（全部）も。鍵は A0〜D7"""
        if k in ("tint", "fmt", "cfg"):
            return self._set1(new, k, v)
        name, _, field = k.partition(".")
        nu = name.upper()
        if not field and nu in ("SHIFT", "ON", "COARSE"):
            js, field = range(4 * SPW_NW), name.lower()
        elif nu == "ALL" and field:
            js = range(4 * SPW_NW)
        elif len(nu) == 1 and nu in "ABCD" and field:
            js = [SPW_NW * "ABCD".index(nu) + i for i in range(SPW_NW)]
        elif len(nu) == 2 and nu[0] in "ABCD" and nu[1] in "01234567" and field:
            js = [SPW_NW * "ABCD".index(nu[0]) + int(nu[1])]
        else:
            raise ValueError(f"知らない設定 {k}（SpW8: tint・fmt・cfg・A0.if・A0.bw・A0.ns・A0.shift・A0.on・A0.coarse（窓は A0〜D7）・A.shift・all.shift・shift）")
        if field == "if":
            x = float(v)
        elif field == "bw":
            x = int(float(v))
            if x not in SPW_BW or float(v) != x:
                raise ValueError(f"{k}: SpW8 の幅は 128 / 64 / 32 / 16 / 8 MHz")
        elif field == "ns":
            n = int(v)
            if n not in range(1, 6):
                raise ValueError(f"{k}: NS は 1..5（SpW8）")
            field, x = "bw", 256 >> n
        elif field == "shift":
            x = int(v)
            if x not in range(16):
                raise ValueError(f"{k}: SHIFT は 0..15")
        elif field == "on":
            if str(v) not in ("0", "1"):
                raise ValueError(f"{k}: on は 1（使う）/ 0（使わない）")
            x = int(v)
        elif field == "coarse":
            x = str(v).lower()
            if x not in SPW_COARSE:
                raise ValueError(f"{k}: coarse は auto（計画の既定）/ near（近い粗い ch）/ alt（2 番目に近い粗い ch）")
        else:
            raise ValueError(f"知らない窓の設定 {k}（if・bw・ns・shift・on・coarse）")
        for j in js:
            new["wins"][j]["if_mhz" if field == "if" else field] = x

    def _set1(self, new, k, v):
        if k == "tint":
            new["tint"] = float(v)
        elif k == "fmt":                           # proj021 2-3c: v2 の SPEC の形（f32 = 運転 / u64 = 試験 / both = 同じ束を両方。照合用）
            if v not in ("f32", "u64", "both"):
                raise ValueError("fmt は f32・u64・both")
            new["fmt"] = v
        elif k == "cfg":
            new["cfg"] = int(v, 0) & 0xFFFFFFFF
        else:
            name, _, field = k.partition(".")
            if name.lower() == "all":
                js = range(4 * NW)
            elif len(name) == 2 and name[0].upper() in "ABCD" and name[1] in "01":
                js = [("ABCD".index(name[0].upper())) * NW + int(name[1])]
            else:
                raise ValueError(f"知らない設定 {k}（tint・cfg・A0.if・A0.ns・A0.bw・A0.shift・all.shift …）")
            for j in js:
                ws = new["wins"][j]
                if field == "if":
                    ws["if_mhz"] = float(v)
                elif field == "ns":
                    n = int(v)
                    if n not in range(1, 7):
                        raise ValueError(f"{k}: NS は 1..6（SAM45-Fine）")
                    ws["ns"] = n
                elif field == "bw":
                    b = int(float(v))
                    if b not in NS_OF_BW:
                        raise ValueError(f"{k}: 幅は 256 / 128 / 64 / 32 / 16 / 8 MHz")
                    ws["ns"] = NS_OF_BW[b]
                elif field == "shift":
                    s = int(v)
                    if s not in range(16):
                        raise ValueError(f"{k}: SHIFT は 0..15")
                    ws["shift"] = s
                elif field == "bundle":
                    b = int(v)
                    if b not in (0, 1):
                        raise ValueError(f"{k}: bundle は 1（PL は 10.24 ms・specd が束ねる。既定）/ 0（PL が tint を 1 個で。V2-a の比べ用）")
                    ws["bundle"] = b
                else:
                    raise ValueError(f"知らない窓の設定 {k}（if・ns・bw・shift・bundle）")

    def _start(self, cmd):
        if self.state in (self.ARMED, self.RUN):
            return dict(ok=False, code="STATE", msg=f"{self.state} の間は START できない")
        force = bool(cmd.get("force"))
        at_beat = None
        if cmd.get("at_utc_ns") is not None:
            if not self.be.clock.ok:
                return dict(ok=False, code="TIME", msg="時刻を答えられないので at= は使えない")
            at_beat = self.be.clock.beat_of_utc_ns(cmd["at_utc_ns"])
            if at_beat < self.be.now_beat() + BEATS_PER_SEC:
                return dict(ok=False, code="ARG", msg="at= は今から 1 秒以上後に")
        self._reset_counters()
        for t in self.tpj:
            t.reset()                              # B2: スキャンの状態（CFG_ID）は RUN ごとなので、R の段差は RUN の境で除ける
        self.state = self.ARMED
        try:
            sa = self.be.start(self.st, at_beat, force)
        except Exception:
            self.state = self.IDLE
            raise
        self.forced = force and not self.be.clock.ok
        self.start_at = sa
        self.active = [bool(cf.get("active", True)) for cf in self.be.cfgs]
        fr = self.fast if self.fast_ring else None   # proj036: --fast-ring なら n_sum ≧ 2 の束ねも C で（リングの上から器へ）
        self.bund = [Bundler(cf["n_sum"], cf["pl_nacc"], fast=fr, posctl=self.posctl_noacc, f32=cf.get("kind") == "spw") if cf.get("bundle") else None
                     for cf in self.be.cfgs]
        if getattr(self.be, "cmode", False):       # SpW8 M5b: 束ねは C（SpwScan）。Acq は束ができた・捨てたの知らせ（_spw_ev）を受ける
            self.bund = [_CBund(self.be.sc, j) if cf["active"] else None for j, cf in enumerate(self.be.cfgs)]
            self.be.on_spw = self._spw_ev
        if hasattr(self.be, "lazy_wins"):          # proj029 2: --fast-ring の窓（FULL。proj036: n_sum ≧ 2 も。SpW8 M5b: SpW の窓も）
            self.be.lazy_wins = {j for j, (cf, b) in enumerate(zip(self.be.cfgs, self.bund))
                                 if self.fast_ring and b is not None and cf.get("kind") in ("full", "spw")}
        self.ndump_target = int(cmd.get("n") or 0)
        utc = self.be.clock.utc_ns(sa)
        self.event(dict(ev="START", start_at=sa, utc_ns=utc, n=self.ndump_target, forced=self.forced, version=VERSION,
                        proto=self.proto, fmt=self.st.get("fmt", "f32") if self.proto == 2 else "u64",
                        ids=self.be.ids, tint=self.st["tint"], cfg=self.st["cfg"], tp_cal=self._cal_pub(), time_cal=self._tcal_pub(),
                        wins=[dict(key=win_key(j, self.nw), adc=j // self.nw, win=j % self.nw, **cf) for j, cf in enumerate(self.be.cfgs)]))
        self.log(f"START: START_AT {sa}（格子 {sa // G_BEATS}·G、UTC {utc / 1e9:.6f}）n = {self.ndump_target}")
        return dict(ok=True, start_at=sa, utc_ns=utc)

    SNAP_MAX = 256

    def _snap(self, cmd):
        """ADC の生サンプル（全帯域コアのスナップショット 8192 個 = 2 µs）を n 個、every_ms おきに取り、T_SNAP の記録で溜まりへ。
        IDLE のときだけ（RUN の窓・TP には触らない）。記録の前後に EVENT（SNAP / SNAP_END）"""
        if self.state not in (self.IDLE, self.ERROR):
            return dict(ok=False, code="STATE", msg=f"{self.state} の間は SNAP できない（STOP の後に）")
        adc, n, every = int(cmd["adc"]), int(cmd.get("n", 1)), float(cmd.get("every_ms", 20.0))
        if not 0 <= adc < 4:
            raise ValueError("adc は A〜D（0〜3）")
        if not 1 <= n <= self.SNAP_MAX:
            raise ValueError(f"n は 1〜{self.SNAP_MAX}")
        if not 5.0 <= every <= 10000.0:
            raise ValueError("every は 5〜10000 ms（読み出しに数 ms かかる）")
        nacc = int(round(every * 1e-3 / 2.0e-6))           # 1 フレーム = 8192 サンプル = 512 ビート = 2.000 µs
        self.event(dict(ev="SNAP", adc=adc, n=n, every_ms=every, nacc=nacc))
        got = self.be.snap(adc, n, nacc)
        for k, (m, x) in enumerate(got):
            h = int(m["h"]) | (0 if self.be.clock.ok else P.H_NOTIME)
            utc = self.be.clock.utc_ns(m["t"], None, adc)
            hd = P.SNAP_H.pack(adc, 0, 0, len(x), int(m["t"]), int(utc), int(m["f0"]), h, k)
            data = np.ascontiguousarray(x, "<i2")
            self._put(P.T_SNAP, [hd, data], P.crc32(hd, data))
        self.event(dict(ev="SNAP_END", adc=adc, n=len(got)))
        return dict(ok=True, n=len(got), nacc=nacc, every_ms=every)

    def _stop(self, why):
        info = []
        try:
            info = self.be.stop()
        except Exception as e:
            info = [dict(err=str(e))]
        if self.state == self.RUN:
            for b in self.bund:
                if b is not None:
                    b.stop()                       # 半端な束は捨てる（INTERFACE 5.1 の 4）
            for i in range(4):
                try:
                    self._flush_tp(i, final=True)
                except Exception as e:             # 止める理由が TP・時刻の誤りのとき、ここでもう一度落ちないように
                    self.log(f"STOP の TP の書き出しで: {type(e).__name__}: {e}")
        self.state = self.IDLE if why != "ERROR" else self.ERROR
        self.stop_info = info
        self.event(dict(ev="STOP", why=why, dumps=self.n_dump, miss=self.n_miss, tp=[t.total for t in self.be.tps] if hasattr(self.be, "tps") else [],
                        tp_info=info, err=self.err))
        self.log(f"STOP（{why}）: ダンプ {sum(self.n_dump)}・読み落とし {sum(self.n_miss)}・TP の錨の組 {info}")

    def status(self):
        tl = self.hist
        tot = int(tl.sum())
        p99 = float(np.searchsorted(np.cumsum(tl), 0.99 * tot) * 0.1) if tot else 0.0
        tps = getattr(self.be, "tps", [])
        w, r = self.ring.positions()
        return dict(state=self.state, time_ok=self.be.clock.ok, time_err=self.be.clock.err, start_at=self.start_at,
                    dumps=self._dumps_min(), dumps_each=self.n_dump, miss=sum(self.n_miss), kgap=sum(self.kgap),
                    tp=[t.total for t in tps], tp_lost=sum(t.lost + t.overflow for t in tps), tp_bad=sum(t.bad_seq + t.bad_flag + t.bad_nfr for t in tps),
                    tp_ovr=sum(t.n_ovr for t in tps), tp_jump=[t.count for t in self.tpj], health=self.h_or, flags=self.fl_or, sat=self.sat,
                    loop_max_ms=round(self.loop_max * 1e3, 2), loop_p99_ms=p99, loops=self.n_loop,
                    loop_max_at=self.loop_max_at, loop_slow=self.loop_slow,
                    pl_dumps=sum(self.pl_dumps), bdrop=sum(b.drop for b in self.bund if b is not None),
                    r_bad=sum(b.r_bad for b in self.bund if b is not None),
                    bund_r=[None if b is None else b.r0 for b in self.bund],
                    seq=self.seq, drop=self.drop["n"], ring_used=w - r, ring_cap=self.ring.cap, err=self.err, forced=self.forced,
                    tp_dbfs=[None if v is None else round(float(s45cal.dbfs(v)), 2) for v in self.tp_last],
                    tp_dbm=[None if v is None or self.cal is None else round(float(s45cal.dbm(v, self.cal, "ABCD"[i])), 2)
                            for i, v in enumerate(self.tp_last)],
                    ring=self.be.ring_stat() if hasattr(self.be, "ring_stat") else None,
                    **(dict(spw_map=spw_map(self.plans), spw=self.be.spw_stat(),
                            val_bad=sum(b.val_bad for b in self.bund if b is not None)) if self.spw else {}))

    def _dumps_min(self):
        v = [n for n, a in zip(self.n_dump, self.active) if a]
        return min(v) if v else 0

    # ---- 読み出しの 1 周
    def _cal_pub(self):
        """START の EVENT・GET CAL に出す較正（使えないときは None）"""
        if self.cal is None:
            return None
        return {k: v for k, v in self.cal.items() if not k.startswith("_")} | {"file": self.cal.get("_file")}

    def _tcal_pub(self):
        """START の EVENT・GET CAL に出す時刻の較正（ADR 0023。偽物は None）"""
        tb = getattr(self.be, "tb", None)
        if tb is None:
            return None
        c = tb.cal
        return dict(state=tb.cal_state, why=tb.cal_why, file=c.get("_file"), date=c.get("date"), board=(tb.board or {}).get("id"),
                    pps_det_ns=c["pps_det_ns"], adc_to_core_ns=c["adc_to_core_ns"], bound_ns=c["bound_ns"])

    def _spec_record(self, j, m, spec):
        cf = self.be.cfgs[j]
        h = int(m["h"]) | (0 if self.be.clock.ok else P.H_NOTIME) | (P.H_FORCED if self.forced else 0)
        if cf.get("kind") == "slice":
            self._spec_record_slice(j, m, spec, cf, h)
            return
        if cf.get("kind") == "full":
            self._spec_record_full(j, m, spec, cf, h)
            return
        if cf.get("kind") == "spw":
            self._spec_record_spw(j, m, spec, cf, h)
            return
        utc = self.be.clock.utc_ns(m["t"], cf["ns"], j // NW)
        if self.proto == 2:
            self._spec_record2(j, m, spec, cf, h, utc)
            return
        hd = P.SPEC_H.pack(j // NW, j % NW, cf["ns"], cf["shift"], P.FMT_RAW, cf["g"], 0, m["cfg"], m["k"], cf["nacc"],
                           m["sat"], m["flags"], h, m["t"], utc, cf["if_mhz"])
        data = np.ascontiguousarray(spec[P.IF_ORDER])
        self._put(P.T_SPEC, [hd, data], P.crc32(hd, data))
        self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]) & FLAGS_OK_MASK; self.sat += int(m["sat"])

    def _spec_record2(self, j, m, spec, cf, h, utc):
        """proj021 2-3c: s45proto v2 の SPEC（INTERFACE 6.）。utc_ns は実効の区間の始まり（5.2）: v1 の utc（D(NS) を引いたもの）から、
        さらに PFB の重心のずれ 1.5·L(NS) を引く。fmt = f32（既定）/ u64 / both（同じ束を u64 と f32 の 2 つで。受け側の照合）"""
        ns = cf["ns"]
        L = 4096 << (ns - 1)
        if utc:
            utc -= (3 * L * 125) // 64                 # 1.5·L ビート → ns（1 ビート = 125/32 ns）
        df = 512e6 / (1 << ns) / P.NCH
        raw = np.ascontiguousarray(spec[P.IF_ORDER])
        fm = self.st.get("fmt", "f32")
        for f in (("u64", "f32") if fm == "both" else (fm,)):
            if f == "u64":
                data, code = raw, P.FMT_RAW
            else:
                data, code = P.f32_round(raw), P.FMT_F32
                if self.f32_trunc:                     # 陽性対照: 0 へ切り捨て（最も近い値でない）→ 受け側の照合が落ちる
                    up = data.astype(np.float64) > raw.astype(np.float64)
                    data[up] = np.nextafter(data[up], np.float32(0))
            hd = P.SPEC2_H.pack(j // NW, j % NW, j // NW, 3, ns, cf["shift"], code, int(getattr(self.be, "bit_kind", 0)),
                                P.NCH, int(cf.get("n_sum", 1)), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, cf["g"], 0,
                                m["t"], utc, P.BASE_NS, cf["if_mhz"], df)
            self._put(P.T_SPEC, [hd, data], P.crc32(hd, data))
        self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]) & FLAGS_OK_MASK; self.sat += int(m["sat"])

    def _spec_record_spw(self, j, m, acc, cf, h):
        """YATSUGATAKE M5b: SpW8 の SPEC（s45proto v2、kind 3 = DDC）。core = src = ADC・s = 論理の窓の番号（ADR 0028）・ns 1〜5・g = 計画の WG（b5 は 0）。
        中身は double の器（束ね）を IF の昇順（P.IF_ORDER、SAM45-Fine と同じ）に並べ、float32 に 1 回丸める（ADR 0029）。df = 幅 / 4096。
        utc_ns = beat_utc(dump_t) − adc_to_core − D(NS)（timebase.WIN_DELAY[(7, 10)]）− 1.5·L、L = 2^(12+NS)"""
        adc, i = divmod(j, SPW_NW)
        ns = cf["ns"]
        utc = self.be.clock.utc_ns(m["t"], ns, adc)
        if utc:
            utc -= (3 * cf["frame"] * 125) // 64       # 1.5·L ビート → ns
        hd = P.SPEC2_H.pack(adc, i, adc, 3, ns, cf["shift"], P.FMT_F32, int(getattr(self.be, "bit_kind", SPW_BIT_KIND)),
                            P.NCH, int(cf["n_sum"]), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, cf["g"], 0,
                            m["t"], utc, P.BASE_NS, cf["if_mhz"], cf["df_hz"])
        if self.fast is not None and "accp" in m:      # 並べ替え・丸め・CRC を C の 1 回のなめで（numpy の道と bit で同じ。test_spw_fast.py）
            if getattr(self, "spw_rec", None) is None:
                self.spw_rec = self.fast.SpwRec(P.NCH)
            data, crc = self.spw_rec.rec(m["accp"], hd)
        else:
            data = np.asarray(acc, np.float64)[P.IF_ORDER].astype(np.float32)
            crc = P.crc32(hd, data)
        self._put(P.T_SPEC, [hd, data], crc)
        self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]); self.sat += int(m["sat"])   # SpW の機関の FLAGS は全部が異常

    def _spec_record_slice(self, j, m, spec, cf, h):
        """proj023: SLICE の SPEC（s45proto v2、kind 2）。ns の欄 = log2 B。中身は IF の昇順（流れの ch i の逆順）。
        utc_ns = beat_utc(dump_t) − adc_to_core − (D_S ＋ 1.5·L)、L = 2048 ビート（D_S = 0、sim-wds）"""
        adc, s = j // NW, j % NW
        utc = self.be.clock.utc_ns(m["t"], None, adc)
        if utc:
            utc -= ((W_DS_BEATS + 3 * W_FRAME // 2) * 125) // 32
        raw = np.ascontiguousarray(np.asarray(spec, np.uint64)[::-1])
        fm = self.st.get("fmt", "f32")
        for f in (("u64", "f32") if fm == "both" else (fm,)):
            if f == "u64":
                data, code = raw, P.FMT_RAW
            else:
                data, code = P.f32_round(raw), P.FMT_F32
                if self.f32_trunc:
                    up = data.astype(np.float64) > raw.astype(np.float64)
                    data[up] = np.nextafter(data[up], np.float32(0))
            hd = P.SPEC2_H.pack(adc, s, adc, 2, cf["lb"], cf["shift"], code, int(getattr(self.be, "bit_kind", 1)),
                                P.NCH, int(cf["n_sum"]), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, 0, 0,
                                m["t"], utc, P.BASE_NS, cf["if_mhz"], cf["df_hz"])
            self._put(P.T_SPEC, [hd, data], P.crc32(hd, data))
        self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]); self.sat += int(m["sat"])   # Wide の FLAGS は全部が異常

    def _spec_record_full(self, j, m, spec, cf, h):
        """proj024: 2G-1 の FULL の SPEC（s45proto v2、kind 1）。ns の欄 0（B 1）・nch 131072。中身は IF の昇順（ch c の逆順、送る i ↔ c = 131071 − i）。
        if_mhz = 送る 2047 番目の IF・df = 15.625 kHz。utc_ns = beat_utc(dump_t) − adc_to_core[src] − (D_S ＋ 1.5·L)、L = 16384・D_S = 1
        proj025: 2G-2 も同じ式（nch 65536・L 8192・D_S 1）。L・D_S は cfg の frame・ds（無ければ 2G-1 の値）、nch は中身の長さ"""
        src = cf["src"]
        utc = self.be.clock.utc_ns(m["t"], None, src)
        if utc:
            utc -= ((cf.get("ds", G_DS_BEATS) + 3 * cf.get("frame", G_FRAME) // 2) * 125) // 32
        fm = self.st.get("fmt", "f32")
        if not isinstance(spec, np.ndarray) and hasattr(spec, "crc_exp"):
            # proj029 2: PL のリングの上のレコード（LazyRec）。PL の CRC の照らし・逆順・丸め・出口の CRC を C で（写さない）
            F = self.fast
            first = True
            for f in (("u64", "f32") if fm == "both" else (fm,)):
                code = P.FMT_RAW if f == "u64" else P.FMT_F32
                hd = P.SPEC2_H.pack(j // NW, j % NW, src, 1, 0, cf["shift"], code, int(getattr(self.be, "bit_kind", 11)),
                                    spec.n, int(cf["n_sum"]), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, 0, 0,
                                    m["t"], utc, P.BASE_NS, cf["if_mhz"], cf["df_hz"])
                pc = F.PC_TRUNC if (self.f32_trunc and f == "f32") else 0
                if first:
                    data, crc, crc_pl = F.ring_spec(spec, hd, f, posctl=pc)
                    if crc_pl != spec.crc_exp:     # 今までの道（Ring.read で捨てる）と同じく、記録を出さずに数える
                        self.be.ring_crc += 1
                        self.n_miss[j] += 1
                        if self.be.ring_crc <= 5:
                            self.log(f"{win_key(j)}: PL のレコードの CRC が合わない（seq {m['seq']}）。記録を出さない")
                        return
                    first = False
                else:
                    v = spec.view()
                    data, crc = F.spec_u64(v, hd) if f == "u64" else F.spec_f32(v, hd, posctl=pc)
                self._put(P.T_SPEC, [hd, data], crc)
            self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]); self.sat += int(m["sat"])
            return
        if self.fast is not None:
            # proj029 1: 逆順・float32 への丸め・CRC を C の 1 回のなめで（出す bytes は下の Python の道と同じ。test_s45fast.py で照合）
            F = self.fast
            spec = np.asarray(spec, np.uint64)
            for f in (("u64", "f32") if fm == "both" else (fm,)):
                code = P.FMT_RAW if f == "u64" else P.FMT_F32
                hd = P.SPEC2_H.pack(j // NW, j % NW, src, 1, 0, cf["shift"], code, int(getattr(self.be, "bit_kind", 11)),
                                    spec.size, int(cf["n_sum"]), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, 0, 0,
                                    m["t"], utc, P.BASE_NS, cf["if_mhz"], cf["df_hz"])
                if f == "u64":
                    data, crc = F.spec_u64(spec, hd)
                else:
                    data, crc = F.spec_f32(spec, hd, posctl=F.PC_TRUNC if self.f32_trunc else 0)
                self._put(P.T_SPEC, [hd, data], crc)
            self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]); self.sat += int(m["sat"])
            return
        raw = np.ascontiguousarray(np.asarray(spec, np.uint64)[::-1])
        for f in (("u64", "f32") if fm == "both" else (fm,)):
            if f == "u64":
                data, code = raw, P.FMT_RAW
            else:
                data, code = P.f32_round(raw), P.FMT_F32
                if self.f32_trunc:
                    up = data.astype(np.float64) > raw.astype(np.float64)
                    data[up] = np.nextafter(data[up], np.float32(0))
            hd = P.SPEC2_H.pack(j // NW, j % NW, src, 1, 0, cf["shift"], code, int(getattr(self.be, "bit_kind", 11)),
                                raw.size, int(cf["n_sum"]), m["cfg"], m["k"], cf["nacc"], m["sat"], m["flags"], h, 0, 0,
                                m["t"], utc, P.BASE_NS, cf["if_mhz"], cf["df_hz"])
            self._put(P.T_SPEC, [hd, data], P.crc32(hd, data))
        self.h_or |= int(m["h"]); self.fl_or |= int(m["flags"]); self.sat += int(m["sat"])

    def _spw_ev(self, e):
        """SpW8 M5b の C の道: 束ができた（kind 1）→ 記録、捨てた（kind 2）→ BDROP。e は s45fast.SPW_EV の 1 つ"""
        kind, j, why, jb, have, k, t, n, sat, flags, h, cfg, seq = e.tolist()    # SPW_EV の並び（欄ごとに int() は 9 回で 41 µs、ボード）
        if kind == 2:
            why = self.fast.SPW_WHY[why] if self.fast else str(why)
            b = self.bund[j]
            b.drop_why[why] = b.drop_why.get(why, 0) + 1
            self._bdrop(j, (jb, why, have))
            return
        sc = self.be.sc
        m = dict(seq=seq, k=k, t=t, h=h, n=n, sat=sat, cfg=cfg, flags=flags, accp=self.be.accp[j])
        if self.last_k[j] is not None and m["k"] != self.last_k[j] + 1:
            self.kgap[j] += 1
        self.last_k[j] = m["k"]
        self.n_dump[j] += 1
        self._spec_record(j, m, sc.acc[j])

    def _bdrop(self, j, d):
        """束を捨てた（INTERFACE 5.1 の 4）。EVENT は最初の 20 回まで（止まりの後に窓ごとに続くので）"""
        jb, why, have = d
        tot = sum(b.drop for b in self.bund if b is not None)
        if tot <= 20 and why != "STOP":
            self.event(dict(ev="BDROP", key=win_key(j, self.nw), bundle=int(jb), why=why, have=int(have), n_sum=self.bund[j].n_sum))
        if why == "r":
            self.event(dict(ev="ERROR", msg=f"{win_key(j, self.nw)}: DUMP_T − m·BASE が RUN の中で動いた（r0 {self.bund[j].r0}）。この窓は束ねない"))

    def _flush_tp(self, i, final=False):
        t = self.be.tps[i]
        n = t.n
        if n == 0 or (n < TP_FLUSH and not final):
            if final and n == 0 and self.tpj_on:
                self._tp_jump(i, self.tpj[i].finish())     # B2: 最後の区切りで開いたままの跳ねも閉じる（溜まりが空でも）
            return
        e = t.buf[:n].copy()
        self.tp_last[i] = float(np.mean(e["sum"].astype(np.float64) / (e["nfr"].astype(np.float64) * 8192.0)))
        e["t_beat"] = self.be.tp_time(i, e["t_beat"].astype(np.int64))      # フレームの番号 → ビート
        if self.tpj_on:
            evs = self.tpj[i].feed(e["t_beat"], e["sum"].astype(np.float64) / (e["nfr"].astype(np.float64) * 8192.0), e["flags"])
            if final:
                evs += self.tpj[i].finish()
            self._tp_jump(i, evs)
        if self.be.clock.ok:
            e["utc_ns"] = self.be.clock.utc_ns_arr(e["t_beat"], i)
        else:
            e["utc_ns"] = 0
            e["flags"] |= P.TPF_NOTIME
        t.n = 0
        hd = P.TP_H.pack(i, 0, 0, n)
        b = e.tobytes()
        pad = b"\0" * (P.pad8(len(hd) + len(b)) - len(hd) - len(b))
        self._put(P.T_TP, [hd, b + pad], P.crc32(hd, b + pad))

    TP_JUMP_EV_MAX = 100                           # B2: EVENT は ADC ごとに RUN あたりこれまで（STATUS の tp_jump は全部数える）

    def _tp_jump(self, i, evs):
        for ev in evs:
            t = self.tpj[i]
            if t.count > self.TP_JUMP_EV_MAX:
                continue
            utc = self.be.clock.utc_ns(ev["t_beat"], None, i)
            self.event(dict(ev="TP_JUMP", adc=i, t_beat=ev["t_beat"], utc_ns=int(utc), n=ev["n"], db=ev["db"], step_db=ev["step_db"], sigma_db=ev["sigma_db"],
                            ovr=ev["ovr"], **({"last": True} if t.count == self.TP_JUMP_EV_MAX else {})))

    def _loop_once(self):
        ts = time.perf_counter()
        f_loop0 = resource.getrusage(resource.RUSAGE_SELF).ru_minflt    # proj029 1d: この周のページフォルト
        be = self.be
        nrec = be.pump()                           # proj021 2-3a: リングを 1 回読んで振り分ける（axi・偽物では何もしない）
        if getattr(be, "cmode", False) and hasattr(be, "sc"):   # SpW8 M5b: 読み落とし・PL のダンプの数は C の窓の状態から
            self.n_miss[:] = be.sc.win["miss"].tolist()
            self.pl_dumps[:] = be.sc.win["pl_dumps"].tolist()
        t_p = time.perf_counter()
        n_spec = 0                                 # proj025 4c: この周で書いた SPEC の記録（束）の数
        t_poll = t_bund = t_rec = 0.0              # proj029 1c: 窓の記録の内訳（poll_win・束ね・記録（put を含む）。put は self.t_put）
        self.t_put = 0.0
        self.f_put = 0
        for j in range(self.nslot):
            for _ in range(64):                    # 溜まったぶんを全部（リングでは止まりの後に何個も来る）
                ta = time.perf_counter()
                r = be.poll_win(j)
                t_poll += time.perf_counter() - ta
                if r is None:
                    break
                m, spec, miss = r
                self.n_miss[j] += miss
                self.pl_dumps[j] += 1
                bu = self.bund[j]
                if bu is not None:                 # proj021 2-3b: 束ねる（INTERFACE 5.1）
                    ta = time.perf_counter()
                    cb0 = bu.crc_bad
                    got, dropped = bu.add(m, spec)
                    t_bund += time.perf_counter() - ta
                    if bu.crc_bad != cb0:          # proj036: PL の CRC が合わない 1 本（今までの道では pump で捨てて読み落としに数えていた）
                        be.ring_crc += 1
                        self.n_miss[j] += 1
                        if be.ring_crc <= 5:
                            self.log(f"{win_key(j, self.nw)}: PL のレコードの CRC が合わない（seq {m.get('seq')}）。その束は記録しない")
                    if dropped is not None:
                        self._bdrop(j, dropped)
                    if got is None:
                        continue
                    m, spec = got
                if self.last_k[j] is not None and m["k"] != self.last_k[j] + 1:
                    self.kgap[j] += 1
                self.last_k[j] = m["k"]
                self.n_dump[j] += 1
                ta = time.perf_counter()
                self._spec_record(j, m, spec)
                t_rec += time.perf_counter() - ta
                n_spec += 1
        be.release()                               # proj029 2: 使い切れなかった LazyRec を写してから R を進める
        t_w = time.perf_counter()
        t_wput = self.t_put                        # 窓の記録の中の put（TP の put は数えない）
        f_wput = self.f_put
        for i in range(4):
            be.poll_tp(i)
            self._flush_tp(i)
        t_t = time.perf_counter()
        be.clock.poll()
        t_c = time.perf_counter()
        dt = t_c - ts
        self.hist[min(1000, int(dt * 1e4))] += 1
        if dt > self.loop_max:
            self.loop_max, self.loop_max_at = dt, self.n_loop
        slow = dt > self.st["tint"]
        if slow:
            self.loop_slow += 1
        lim = float(getattr(self.o, "loop_log_ms", 0) or 0)    # proj025 4c: 診断（指定したときだけ。loop_slow の数え方は変えない）
        diag = lim > 0 and dt * 1e3 > lim and self.n_loop_log < 300
        if (slow and self.loop_slow <= 20) or diag:  # どの周が遅いかを残す（2-3a の 1 回目: 最大 115 ms・p99 14.5 ms）
            if diag:
                self.n_loop_log += 1
            lp = getattr(be, "last_pump", (0.0, 0.0))
            self.log(f"1 周が {dt * 1e3:.1f} ms（周 {self.n_loop}・リングのレコード {nrec}・SPEC の記録 {n_spec}）: リングの読み {lp[0] * 1e3:.1f}・振り分け {lp[1] * 1e3:.1f}・"
                     f"窓の記録 {(t_w - t_p) * 1e3:.1f}・TP {(t_t - t_w) * 1e3:.1f}・時刻の確かめ {(t_c - t_t) * 1e3:.1f} ms"
                     f"（窓の記録の内訳: poll {t_poll * 1e3:.2f}・束ね {t_bund * 1e3:.2f}・記録 {(t_rec - t_wput) * 1e3:.2f}・put {t_wput * 1e3:.2f} ms）"
                     f"（フォルト: 周 {resource.getrusage(resource.RUSAGE_SELF).ru_minflt - f_loop0}・put {f_wput}）")
        self.n_loop += 1
        if self.ndump_target and self._dumps_min() >= self.ndump_target:
            self._stop("n に達した")

    # ---- 本体
    def run(self):
        self._rt()
        if self.spw:
            self.be = (FakeSpwBackend if self.o.fake else SpwBackend)(self.o, self.log)
        elif self.g24:
            self.be = (FakeG24Backend if self.o.fake else G24Backend)(self.o, self.log)
        elif self.g22:
            self.be = (FakeG22Backend if self.o.fake else G22Backend)(self.o, self.log)
        elif self.g21:
            self.be = (FakeG21Backend if self.o.fake else G21Backend)(self.o, self.log)
        elif self.wide:
            self.be = (FakeWideBackend if self.o.fake else WideBackend)(self.o, self.log)
        else:
            self.be = (FakeBackend if self.o.fake else HwBackend)(self.o, self.log)
        try:
            self.be.open()
        except BaseException as e:
            self.conn.send(dict(ok=False, msg=f"起動できない: {type(e).__name__}: {e}"))
            raise
        if self.cal is not None:
            ok, self.cal_msg = s45cal.check(self.cal, self.be.ids)
            if not ok:
                self.log(f"TP の較正を使わない: {self.cal_msg}（{self.cal.get('_file')}）")
                self.cal = None
            else:
                self.log(f"TP の較正: {self.cal.get('_file')}（" + "・".join(
                    f"{a} K {c['k_db']:+.2f}{' 暫定' if c.get('provisional') else ''}" for a, c in sorted(self.cal["adc"].items())) + "）")
        if (self.g21 or self.g2 or self.spw) and not getattr(self.o, "no_malloc_tune", False):
            self.log(malloc_tune()[1])               # proj024 3d: 2G-1 の 1 MiB の配列（Fine・Wide の道は今までどおり）
        if getattr(self.o, "prefault", False):        # proj029 1d: 溜まりのページを先に触る（運転の最初の ≒ 5 秒のページフォルトを起動に寄せる）
            t0 = time.perf_counter()
            n = self.ring.prefault(write=True)
            self.log(f"溜まりのページを先に触った: {n} ページ・{time.perf_counter() - t0:.2f} 秒")
        if self.fast is not None:
            self.log(f"SPEC の記録（FULL）・SpW の束ねは C（s45fast、CRC {'命令' if self.fast.HW_CRC else '表'}）"
                     + ("・リングの SPEC のレコードは写さずに（--fast-ring、n_sum 1 は記録へ・2 以上は C で器へ）" if self.fast_ring else ""))
        gc.collect(); gc.freeze(); gc.disable()
        self.conn.send(dict(ok=True, ids=self.be.ids, version=VERSION))
        self.log(f"準備完了（{'偽物' if self.o.fake else '実機'}、ID {self.be.ids}）")
        quit_ = False
        while not quit_:
            if self.state == self.RUN:
                try:
                    self._loop_once()
                except Exception as e:
                    self.err = f"{type(e).__name__}: {e}"
                    self.log(traceback.format_exc())
                    self.event(dict(ev="ERROR", msg=self.err))
                    self._stop("ERROR")
                wait = 0.0 if self.state == self.RUN else 0.05
            elif self.state == self.ARMED:
                try:
                    if self.be.fired():
                        info = self.be.begin()
                        if info["run_t_bad"]:
                            self.event(dict(ev="WARN", msg=f"RUN_T が START_AT + 1 でないコア {info['run_t_bad']}"))
                        self.state = self.RUN
                        self.log("RUN")
                except Exception as e:
                    self.err = f"{type(e).__name__}: {e}"
                    self.log(traceback.format_exc())
                    self.event(dict(ev="ERROR", msg=self.err))
                    self._stop("ERROR")
                wait = 0.005
            else:
                wait = 0.1
                if self.drop["pending"] is not None:
                    self._flush_drop()                # 止まった後に残った DROP を、空きができたら置く
            if self.conn.poll(wait if self.state != self.RUN else 0):
                cmd = self.conn.recv()
                rep = self.handle(cmd)
                self.conn.send(rep)
                quit_ = bool(rep.get("quit"))
            if self.state == self.RUN:
                time.sleep(self.o.loop_sleep)
        gc.enable()
        if hasattr(self.be, "close"):
            self.be.close()                        # proj021 2-3a: PL が書き終えてからリングのバッファを返す

    def _rt(self):
        if self.o.cpu is not None:
            try:
                os.sched_setaffinity(0, {self.o.cpu})
            except OSError as e:
                self.log(f"CPU の固定ができない: {e}")
        if self.o.rt:
            try:
                os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(self.o.rt))
            except (OSError, AttributeError) as e:
                self.log(f"SCHED_FIFO にできない（{e}）。普通の優先度で続ける")


def main(conn, ring, opts):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)   # 端末の Ctrl-C は親だけが受け、親が quit で止める（README）
    try:
        Acq(conn, ring, opts).run()
    except BaseException:
        traceback.print_exc()
