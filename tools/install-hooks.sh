#!/bin/sh
# SPDX-License-Identifier: BSD-3-Clause
# この clone の git のフックを tools/hooks に向ける（clone ごとに 1 回）。
set -e
root=$(git rev-parse --show-toplevel)
cd "$root"
chmod +x tools/hooks/* tools/prepublish_scan.py
git config core.hooksPath tools/hooks
echo "フックを tools/hooks に向けました（commit-msg・pre-push）"
