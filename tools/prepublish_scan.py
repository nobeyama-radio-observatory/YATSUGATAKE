#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""公開前スキャン（docs/publishing.md の手順 1〜9 を機械的に行う）。

git の履歴は消せないので、commit・push の前に、公開してはいけないものが
入っていないかを機械で洗う。目視では見落とす。

使い方:
    python3 tools/prepublish_scan.py            # 作業ツリー ＋ 未 push のコミット
    python3 tools/prepublish_scan.py --all      # 作業ツリー ＋ 全履歴のコミット（公開に切り替える前）
    python3 tools/prepublish_scan.py --quiet    # ヒットだけを出す（フックから）

手元だけの追加パターン（自分の姓・機器のシリアル・内部のホスト名など）は、
リポジトリの根元の .prepublish-patterns（.gitignore 済み）に 1 行 1 個の正規表現で書く。
環境変数 PREPUBLISH_PATTERNS（| 区切り）でも足せる。

終了コード: 0 = ヒットなし、1 = ヒットあり（要確認）、2 = 実行の誤り
"""
import argparse
import os
import re
import subprocess
import sys

# 検査の正規表現そのものを含むファイル。手順 2〜4 と 9 の対象から外す（手順 1・5 は当てる）
SELF_FILES = {
    "tools/prepublish_scan.py",
    "tools/hooks/commit-msg",
    "docs/publishing.md",
}

# 手順 1: MAC アドレス・区切りなしの 12 桁の 16 進（Host ID の典型）
RE_MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b|\b[0-9a-f]{12}\b")
RE_MAC_OK = re.compile(r"00[:-]00[:-]5[eE][:-]00[:-]53[:-][0-9A-Fa-f]{2}")  # RFC 7042 の文書用

# 手順 2: 個人情報・ホームパス
RE_PERSONAL = re.compile(
    r"nao\.ac\.jp|/home/[a-z]|/Users/[a-z]|C:\\Users\\|@[a-z0-9.-]+\.(?:jp|com|org|net)\b",
    re.IGNORECASE,
)
# 手順 3: 内部システム名・組織内の呼称
RE_INTERNAL = re.compile(r"業務ログ|業務ノート|トラブル記録|科研費|worklog", re.IGNORECASE)
# 手順 4: 私的 URL
RE_PRIVATE_URL = re.compile(
    r"claude\.ai|onedrive|sharepoint|CloudStorage|drive\.google|docs\.google", re.IGNORECASE
)
# 手順 5: IPv4 アドレス
RE_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
# 公開してよい番地: ループバック 127.0.0.0/8・「全部の口」0.0.0.0（--host の既定値など）・RFC 5737 の文書用
RE_IPV4_OK = re.compile(r"127\.\d{1,3}\.\d{1,3}\.\d{1,3}|0\.0\.0\.0|192\.0\.2\.\d{1,3}|198\.51\.100\.\d{1,3}|203\.0\.113\.\d{1,3}")
# 手順 7: 外部リンク
RE_URL = re.compile(r"https?://[^\s)>\]`\"'|]+")
# 手順 9: コミットメッセージ
RE_COMMIT_MSG = re.compile(
    r"claude\.ai|session_|^Claude-Session:|onedrive|sharepoint|nao\.ac\.jp", re.IGNORECASE | re.MULTILINE
)

# 置いてはいけない拡張子
FORBIDDEN_EXT = (".lic", ".bit", ".hwh", ".xsa", ".bin", ".npy", ".npz", ".s45")
HIDDEN_OK = {".gitignore", ".gitattributes", ".gitkeep"}
BIG_BYTES = 5 * 1024 * 1024


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def extra_patterns(root):
    pats = []
    path = os.path.join(root, ".prepublish-patterns")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            pats += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    env = os.environ.get("PREPUBLISH_PATTERNS", "")
    pats += [p for p in env.split("|") if p]
    return re.compile("|".join(pats), re.IGNORECASE) if pats else None


def read_text(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None  # 2 進のファイル
    return data.decode("utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="コミットメッセージを全履歴で調べる")
    ap.add_argument("--quiet", action="store_true", help="ヒットだけを出す（手順 7・8 の一覧は出さない）")
    args = ap.parse_args()

    try:
        root = git("rev-parse", "--show-toplevel").strip()
    except RuntimeError as e:
        print(f"git のリポジトリの中で実行してください: {e}", file=sys.stderr)
        return 2
    os.chdir(root)

    files = [f for f in git("ls-files", "-co", "--exclude-standard").splitlines() if os.path.isfile(f)]
    extra = extra_patterns(root)
    hits = []  # (手順, 場所, 中身)

    def hit(step, where, text):
        hits.append((step, where, text.strip()[:200]))

    urls = set()
    for f in files:
        base = os.path.basename(f)
        if f.lower().endswith(FORBIDDEN_EXT):
            hit("0 置かないもの", f, "この拡張子はリポジトリに入れない（.gitignore を確かめる）")
        if base.startswith(".") and base not in HIDDEN_OK and not f.startswith(".github/"):
            hit("6 隠しファイル", f, base)
        if os.path.getsize(f) > BIG_BYTES:
            hit("0 大きいファイル", f, f"{os.path.getsize(f)} バイト")
        text = read_text(f)
        if text is None:
            continue
        is_self = f in SELF_FILES
        for n, line in enumerate(text.splitlines(), 1):
            where = f"{f}:{n}"
            for m in RE_MAC.finditer(line):
                if not RE_MAC_OK.fullmatch(m.group(0)):
                    hit("1 MAC・Host ID", where, line)
                    break
            for m in RE_IPV4.finditer(line):
                if not RE_IPV4_OK.fullmatch(m.group(0)):
                    hit("5 IP アドレス", where, line)
                    break
            if is_self:
                continue
            urls.update(u.rstrip(".,;:") for u in RE_URL.findall(line))
            if RE_PERSONAL.search(line):
                hit("2 個人情報・ホームパス", where, line)
            if RE_INTERNAL.search(line):
                hit("3 内部の名前", where, line)
            if RE_PRIVATE_URL.search(line):
                hit("4 私的 URL", where, line)
            if extra and extra.search(line):
                hit("2+ 手元の追加パターン", where, line)

    # 手順 8・9: コミット
    authors = set()
    try:
        has_head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True).returncode == 0
        if has_head:
            if args.all:
                rng = ["--all"]
            else:
                upstream = subprocess.run(
                    ["git", "rev-parse", "--verify", "-q", "@{upstream}"], capture_output=True, text=True
                )
                rng = ["@{upstream}..HEAD"] if upstream.returncode == 0 else ["HEAD"]
            log = git("log", *rng, "--format=%x1e%h%x1f%an <%ae> | %cn <%ce>%x1f%B")
            for rec in log.split("\x1e"):
                if not rec.strip():
                    continue
                h, who, body = (rec.split("\x1f") + ["", ""])[:3]
                authors.add(who)
                for line in body.splitlines():
                    if RE_COMMIT_MSG.search(line) or (extra and extra.search(line)):
                        hit("9 コミットメッセージ", f"commit {h}", line)
    except RuntimeError as e:
        print(f"コミットを読めませんでした: {e}", file=sys.stderr)

    for step, where, text in sorted(hits):
        print(f"[{step}] {where}: {text}")

    if not args.quiet:
        print()
        print(f"調べたファイル: {len(files)} 個")
        print("手順 7 外部リンク（すべて公開の資料か、目で確かめる）:")
        for u in sorted(urls):
            print(f"  {u}")
        print("手順 8 コミットの作者（公開してよいアドレスか、目で確かめる）:")
        for a in sorted(authors) or ["（コミットなし）"]:
            print(f"  {a}")
        print()
        print("ヒットなし" if not hits else f"ヒット {len(hits)} 件。docs/publishing.md の置き換えの指針に従って直す")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
