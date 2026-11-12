#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""時刻の照合の累計の許容（Timebase の pps_tol・specd の --pps-tol-ns、2026-11-13）の試験。PL なし。

錨からの PPS の数とスタンプの差を ±pps_tol ビートで照らす。既定は ±2 ビート（今までどおり）。
45m で錨から 34893 発で −3 ビート（PPS と 10 MHz の位相の漂い）で時刻を失ったので、許容を ns で広げられるようにした。

    python3 test_ppstol.py            # 結果: 全部通過 / 不合格
陽性対照: 既定の許容では 45m の −3 ビートが落ちること、広げても PPS の取りこぼし（1 秒ぶん）は落ちることを確かめる。
"""
import sys

import timebase as TB

BPS = TB.BEATS_PER_SEC
ANCHOR = dict(utc_sec=1_794_000_000, stamp=1_000_000_000, epoch=1, count=100)


class FakeTC:
    """check() が読むものだけ（status・counters・pps）。"""

    def __init__(self, d_count, d_stamp):
        self.p = dict(count=ANCHOR["count"] + d_count, stamp=ANCHOR["stamp"] + d_stamp)

    def status(self):
        return {"anchored": True, "trig_alive": True}

    def counters(self):
        return {"epoch": ANCHOR["epoch"]}

    def pps(self, path):
        return dict(self.p)


def checks(tol, d_count, d_stamp):
    tb = TB.Timebase.__new__(TB.Timebase)
    tb.tc, tb.path, tb.pps_tol, tb._anchor = FakeTC(d_count, d_stamp), "trig", tol, dict(ANCHOR)
    try:
        tb.check()
        return True
    except TB.TimebaseError:
        return False


def main():
    ok = True

    def judge(cond, msg):
        nonlocal ok
        print(("OK  " if cond else "NG  ") + msg)
        ok = ok and cond

    n = 34893
    judge(TB.pps_tol_beats(None) == 2, "既定の許容は ±2 ビート")
    judge(TB.pps_tol_beats(1000) == 256, "1000 ns = 256 ビート（125/32 ns ちょうど）")
    judge(TB.pps_tol_beats(1001) == 257, "ns は切り上げてビートに")
    judge(TB.pps_tol_beats(0) == 2, "2 ビートより狭くはしない")
    d = TB.pps_tol_beats(None)
    judge(checks(d, n, n * BPS - 2), "既定: −2 ビートは通る")
    judge(not checks(d, n, n * BPS - 3), "既定: 45m の −3 ビート（34893 発）は落ちる（陽性対照）")
    t = TB.pps_tol_beats(1000)
    judge(checks(t, n, n * BPS - 3), "1000 ns: 45m の −3 ビートは通る")
    judge(checks(t, n, n * BPS + 256) and checks(t, n, n * BPS - 256), "1000 ns: ±256 ビートは通る")
    judge(not checks(t, n, n * BPS + 257), "1000 ns: +257 ビートは落ちる")
    judge(not checks(t, n - 1, n * BPS), "1000 ns: PPS を 1 発取りこぼすと落ちる（陽性対照）")
    tb = TB.Timebase.__new__(TB.Timebase)
    tb.tc, tb.path, tb.pps_tol, tb._anchor = FakeTC(n, n * BPS - 3), "trig", t, dict(ANCHOR)
    judge(tb.drift() == dict(n=n, beats=-3, tol=256), "drift: 錨から 34893 発・−3 ビート・許容 256（STATUS の pps_n・pps_drift・pps_tol）")
    tb.tc = FakeTC(n, n * BPS + 300)
    judge(tb.drift()["beats"] == 300, "drift: 許容を越えても例外にせず今のずれを返す")
    tb._anchor = None
    judge(tb.drift() is None, "drift: 錨が無ければ None")
    try:
        TB.pps_tol_beats(-1)
        judge(False, "負の許容は断る")
    except ValueError:
        judge(True, "負の許容は断る")
    print("結果: " + ("全部通過" if ok else "不合格"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
