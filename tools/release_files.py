#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""bit のビルドの出力から、GitHub Release に添える組を作る（docs/release.md。標準ライブラリだけ）

    python3 tools/release_files.py hw/bits/sam45-fine/build sam45-fine v1.0.0 --out dist/sam45-fine-v1.0.0 \\
        --commit $(git rev-parse --short=7 HEAD) --fdri <前の版の FDRI の sha256>

作るもの（--out の下）:
  <bit>-<版>.bit / .hwh         ビルドの .bit・.hwh の写し（名前だけ変える。.hwh の絶対パスはファイル名だけに）
  <bit>-<版>.bitinfo.txt        USR_ACCESS（commit・汚れ）・FDRI の sha256（sw/pynq/bitinfo.py）
  <bit>-<版>.timing.txt         -1 の WNS / WHS（vivado.log の TIMING (確定)）と timing.rpt の Design Timing Summary
  <bit>-<版>.utilization.txt    utilization.rpt（頭の Date・Host・Command を除く）
  <bit>-<版>.cdc.txt            cdc.rpt の分類ごとの件数
  <bit>-<版>.build.log          vivado.log の要約（TIMING・ERROR・CRITICAL WARNING・NOTE の行。生のログは配らない）
  SHA256SUMS

照らすもの（どれか外れたら終了状態 1、何も書かない）:
  - .bit の USR_ACCESS が --commit と同じで、汚れの印が無い
  - --fdri を渡したら、FDRI の sha256 が同じ（RTL を変えていない作り直しなら同じになる。M5b）
  - 書いた文（.hwh を含む）に、絶対パス・ホスト名の行・IP アドレス・.prepublish-patterns の語が無い
"""
import argparse
import hashlib
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sw", "pynq"))
import bitinfo  # noqa: E402

HEAD_DROP = re.compile(r"^\|\s*(Date|Host|Command)\s*:")
LOG_KEEP = re.compile(r"^(TIMING|ERROR:|CRITICAL WARNING|NOTE:|segfault in|Vivado v|\*\*\*\* Vivado v)")
ABS_PATH = re.compile(r"(?<![\w.])/(?:home|tools|opt|root|mnt|Users|tmp|usr|var|srv|data|sessions)/\S*")
# .hwh の属性値の中の絶対パス（SAM45-Wide の COEF_FILE・TW_FILE）。XML に < は置けないのでファイル名だけを残す
HWH_PATH = re.compile(r"(?<![\w.])/(?:home|tools|opt|root|mnt|Users|tmp|usr|var|srv|data|sessions)/[^\s\"'<>]*/")
BAD = [re.compile(r"^\|\s*Host\s*:", re.M), re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), ABS_PATH]


def scrub(t):
    return ABS_PATH.sub("<path>", t)


def head_free(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return "".join(x for x in f if not HEAD_DROP.match(x))


def timing(build):
    with open(os.path.join(build, "vivado.log"), encoding="utf-8", errors="replace") as f:
        tl = [x for x in f if x.startswith("TIMING (確定)")]
    if not tl:
        raise SystemExit("vivado.log に TIMING (確定) の行が無い（ビルドが終わっていない）")
    with open(os.path.join(build, "timing.rpt"), encoding="utf-8", errors="replace") as f:
        r = f.read().splitlines(keepends=True)
    i = next((k for k, x in enumerate(r) if x.startswith("| Design Timing Summary")), None)
    if i is None:
        raise SystemExit("timing.rpt に Design Timing Summary が無い")
    j = next((k for k in range(i + 3, len(r)) if r[k].startswith("-----")), len(r))
    return tl[-1] + "\n" + "".join(r[i:j])


def cdc(build):
    with open(os.path.join(build, "cdc.rpt"), encoding="utf-8", errors="replace") as f:
        r = f.read().splitlines(keepends=True)
    i = next((k for k, x in enumerate(r) if x.startswith("ID") and "Severity" in x and "Count" in x), None)
    if i is None:
        raise SystemExit("cdc.rpt に分類ごとの件数の表が無い")
    j = next((k for k in range(i + 2, len(r)) if not r[k].strip()), len(r))
    return "".join(r[i:j])


def buildlog(build):
    with open(os.path.join(build, "vivado.log"), encoding="utf-8", errors="replace") as f:
        keep = [x for x in f if LOG_KEEP.match(x)]
    note = ("# vivado.log の要約（tools/release_files.py）。TIMING・ERROR・CRITICAL WARNING・NOTE の行だけ。絶対パスは <path> に。\n"
            "# OOC の合成の segfault と、その run の回し直しは既知（docs/knowledge/pitfalls.md）。output_width の ERROR は build.tcl の読みの試し（下のポート幅で照らす）\n")
    return note + "".join(keep)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("build", help="ビルドの出力のディレクトリ（proj021.bit・vivado.log・*.rpt）")
    p.add_argument("bit", help="bit の名前（sam45-fine）")
    p.add_argument("ver", help="版（v1.0.0）")
    p.add_argument("--out", required=True)
    p.add_argument("--bitfile", default="proj021")
    p.add_argument("--commit", required=True, help="リリースの commit の短いハッシュ 7 桁")
    p.add_argument("--fdri", default=None, help="同じであるはずの FDRI の sha256（RTL を変えていないとき）")
    a = p.parse_args()

    stem = f"{a.bit}-{a.ver}"
    bit = os.path.join(a.build, a.bitfile + ".bit")
    hwh = os.path.join(a.build, a.bitfile + ".hwh")
    r = bitinfo.read(bit)
    ng = []
    v = r["usr_access"]
    want = int(a.commit[:7], 16)
    if v is None or v >> 4 != want or v & 1:
        ng.append(f"USR_ACCESS {bitinfo.fmt(v)} = {bitinfo.describe(v)}（要求 commit {a.commit[:7]}・汚れなし）")
    if a.fdri and r["fdri_sha256"] != a.fdri:
        ng.append(f"FDRI の sha256 {r['fdri_sha256']} が要求 {a.fdri} と違う（配置・配線が変わった）")

    texts = {
        f"{stem}.bitinfo.txt": (f"bit: {stem}.bit\n設計 {r['design']} / part {r['part']}\n"
                                f"USR_ACCESS: {bitinfo.fmt(v)} = {bitinfo.describe(v)}\n"
                                f"FDRI: {r['fdri_words']} 語 / sha256 {r['fdri_sha256']}\n"),
        f"{stem}.timing.txt": timing(a.build),
        f"{stem}.utilization.txt": head_free(os.path.join(a.build, "utilization.rpt")),
        f"{stem}.cdc.txt": cdc(a.build),
        f"{stem}.build.log": buildlog(a.build),
    }
    texts = {k: scrub(t) for k, t in texts.items()}
    with open(hwh, encoding="utf-8") as f:
        texts[f"{stem}.hwh"] = HWH_PATH.sub("", f.read())
    pats = list(BAD)
    pp = os.path.join(HERE, "..", ".prepublish-patterns")
    if os.path.exists(pp):
        with open(pp, encoding="utf-8") as f:
            pats += [re.compile(x.strip()) for x in f if x.strip() and not x.startswith("#")]
    for k, t in texts.items():
        for q in pats:
            m = q.search(t)
            if m:
                ng.append(f"{k}: 公開してはいけない形 {q.pattern!r} に当たる: {m.group(0)[:60]!r}")
    if ng:
        for x in ng:
            print("NG:", x)
        return 1

    os.makedirs(a.out, exist_ok=True)
    shutil.copyfile(bit, os.path.join(a.out, stem + ".bit"))
    for k, t in texts.items():
        with open(os.path.join(a.out, k), "w", encoding="utf-8") as f:
            f.write(t)
    sums = []
    for k in sorted(os.listdir(a.out)):
        if k == "SHA256SUMS":
            continue
        with open(os.path.join(a.out, k), "rb") as f:
            sums.append(f"{hashlib.sha256(f.read()).hexdigest()}  {k}\n")
    with open(os.path.join(a.out, "SHA256SUMS"), "w") as f:
        f.writelines(sums)
    print(f"release_files: {a.out} に {len(sums)} 個と SHA256SUMS")
    print(f"  USR_ACCESS {bitinfo.fmt(v)}（{bitinfo.describe(v)}）・FDRI {r['fdri_sha256']}")
    print("  照合: 通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
