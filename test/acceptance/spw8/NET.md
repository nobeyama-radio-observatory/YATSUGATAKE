# NET — 予算を越える tint を SET で断る

- **前提**: 共通の前提（specd は既定の引数。`--net-budget-mbs` を渡さない）。照合は `s45acq.check_net`（interface 4.5）。量は float32 の SPEC の中身で、SpW8 の 32 窓は 32 × 4,096 ch × 4 B / tint
- **手順**: 32 窓の組で `SET tint=0.01024` → GET → `SET tint=0.02048` → GET
- **合格**: `SET tint=0.01024` が **ERR**（理由に「51.2 MB/s」「予算 30 MB/s を越える」「この構成の tint の最小は 0.02048 s」）で、直後の GET の tint は変わらない。`SET tint=0.02048` は OK で GET が 0.02048。**窓の数で量が変わる**（窓 16 本なら 0.01024 が OK になる）ことも見る
- **陽性対照**: specd を `--net-budget-mbs 0` で起こし直し、`SET tint=0.01024` が OK
- **PL なしの照合**: `bash test_fake.sh net`（SpW8 の 10.24 ms が ERR・20.48 ms が OK を M5b で足す）
- **記録**: YATSUGATAKE SpW8 M5b（2026-11-04、実機）: 32 窓の `SET tint=0.01024` は ERR（「51.2 MB/s」「予算 30 MB/s を越える」「この構成の tint の最小は 0.02048 s」）・GET は 0.04096 のまま、0.02048 は OK、`C.on=0 D.on=0` の 16 窓なら 0.01024 が OK。陽性対照（`--net-budget-mbs 0`）で 32 窓の 0.01024 が OK。PL なしの `test_fake.sh net`・`netp` も通過
- **記録（M6）**: YATSUGATAKE M6（2026-11-04 06:56 UTC、M5c の bit）: 32 窓の `SET tint=0.01024` は ERR（51.2 MB/s・最小 0.02048 s）で GET は 0.04096 のまま、0.02048 は OK、`C.on=0 D.on=0` の 16 窓で 0.01024 が OK。陽性対照（`--net-budget-mbs 0` の specd、07:29 UTC）で 32 窓の 0.01024 が OK。**通過**
