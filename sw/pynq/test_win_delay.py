#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""窓の遅れ D(NS) の表（timebase.WIN_DELAY、鍵は (BIT_KIND, BIT_REV)、SpW8 の M5a）の試験。PL なし。

    python3 test_win_delay.py        # 結果: 全部通過 / 不合格
    python3 test_win_delay.py -p     # 陽性対照: どの bit にも SAM45-Fine の行を当てる（M5a より前の形）。落ちるべき

見ること:
  1. SAM45-Fine (2, 3) の値が M5a の前（全 bit 共通の WIN_DELAY_BEATS）と同じ
  2. SpW8 rev 10 (7, 10) が引け、NS 1〜5 が proj032 P-12 の値（hw/bits/spw8/tools/dly_cmp.py の表と同じ）
  3. Timebase が載っている bit の鍵で表を選び、sample_utc_ns が D を引く・accuracy() が表に無い NS を「未較正」と出す
  4. 表に無い bit（2G-4 (3, 1)・SpW8 の別の REV）はどの NS も「未較正」で、D を引かない
"""
import sys
import types

import timebase as TB

# M5a より前の timebase.WIN_DELAY_BEATS（全 bit 共通）
OLD = {1: 57.56, 2: 87.21, 3: 136.06, 4: 229.02, 5: 408.09, 6: 748.27, 7: 1427.80, 8: 2781.10}
SPW8 = {1: 86.03, 2: 135.07, 3: 231.05, 4: 411.01, 5: 757.03}
ANCHOR = dict(utc_sec=1_792_557_829, stamp=1_488_900_165, epoch=1, count=0)
CAL = dict(pps_det_ns=71.6, adc_to_core_ns={0: 141.6, 1: 141.7, 2: 141.3, 3: 141.3}, bound_ns=5, source="試験")


def make_tb(key, positive=False):
    """Timebase.__init__ を通す（鍵から表を選ぶところを試す）。TimeCore は鍵だけを持つ偽物、較正ファイルは読まない"""
    if positive:
        orig = TB.win_delay_of
        TB.win_delay_of = lambda k: dict(TB.WIN_DELAY[(2, 3)])
    try:
        tc = types.SimpleNamespace(bit_kind=key[0], bit_rev=key[1])
        tb = TB.Timebase(tc, cal={key: CAL, TB.CAL_PROVISIONAL_KEY: CAL}, time_cal=None, log=lambda s: None)
    finally:
        if positive:
            TB.win_delay_of = orig
    tb._anchor = dict(ANCHOR)
    tb.check = lambda: None
    return tb


def main(positive=False):
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'OK' if cond else 'NG'}  {name}{('  ' + detail) if detail else ''}")

    # 1・2. 表の中身
    chk("SAM45-Fine (2, 3) の D(NS) が M5a の前と同じ", TB.win_delay_of((2, 3)) == OLD, f"{TB.win_delay_of((2, 3))}")
    chk("WIN_DELAY_BEATS（SAM45-Fine だけの道具が使う）が (2, 3) の行", TB.WIN_DELAY_BEATS == OLD)
    chk("SpW8 rev 10 (7, 10) の D(NS) が P-12 の値（NS 1〜5）", TB.win_delay_of((7, 10)) == SPW8, f"{TB.win_delay_of((7, 10))}")
    # 3・4. Timebase が鍵で選ぶ
    b = ANCHOR["stamp"] + 1_000_000_007
    for key, want, name in (((2, 3), OLD, "SAM45-Fine"), ((7, 10), SPW8, "SpW8 rev 10"),
                            ((3, 1), {}, "2G-4（窓なし）"), ((7, 11), {}, "SpW8 の表に無い REV")):
        tb = make_tb(key, positive)
        t0 = tb.sample_utc_ns(b, adc=1)
        for ns in range(1, 10):
            d = t0 - tb.sample_utc_ns(b, ns=ns, adc=1)
            unc = f"WIN_DELAY[{key}][{ns}]" in tb.accuracy(ns=ns, adc=1)["uncalibrated"]
            if ns in want:
                good = d == int(round(want[ns] * 125 / 32)) and not unc
                chk(f"{name} {key} NS {ns}: D を引く（{want[ns]:.2f} ビート = {d} ns）・未較正に出ない", good, f"差 {d} ns・未較正 {unc}")
            else:
                chk(f"{name} {key} NS {ns}: 表に無い → 未較正・D を引かない", d == 0 and unc, f"差 {d} ns・未較正 {unc}")
    print(f"結果: {'全部通過' if ok else '不合格'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(positive="-p" in sys.argv[1:]))
