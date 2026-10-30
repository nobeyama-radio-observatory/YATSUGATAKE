# NET — 予算を越える tint を SET で断る

- **前提**: 共通の前提（specd は既定の引数。`--net-budget-mbs` を渡さない）。M5 で入れた照合（`s45acq.check_net`、interface 4.5 の約束）。量は float32 の SPEC の中身（頭・TP は数えない）で、2G-4 は 4 × 32768 ch × 4 B / tint
- **手順**:

```bash
python3 specctl.py --host $B "SET tint=0.01024" GET "SET tint=0.02048" GET
```

- **合格**: `SET tint=0.01024` が **ERR**（理由に「51.2 MB/s」「予算 30 MB/s を越える」「この構成の tint の最小は 0.02048 s」）で、直後の GET の tint は変わらない（起動の既定 0.04096）。`SET tint=0.02048` は OK で GET が 0.02048
- **陽性対照**: specd を **`--net-budget-mbs 0`**（照合を外す）で起こし直し、同じ手順で `SET tint=0.01024` が OK・GET が 0.01024
- **PL なしの照合**: `bash test_fake.sh net`（2G-4・2G-2・2G-1 の 10.24 ms が ERR・20.48 ms が OK、Fine・Wide の 10.24 ms は OK）と `netp`（照合なしで通る）。照合の定数を 0 にした s45acq では `net` が NG になる（陽性対照の陽性対照、M5 で確かめた）
- **記録**: **YATSUGATAKE M5**（2026-10-28、bit `e3521f51…`）: `SET tint=0.01024` → `ERR ARG tint 0.01024 s では float32 で 51.2 MB/s（予算 30 MB/s を越える。INTERFACE 4.5）。この構成の tint の最小は 0.02048 s`、直後の GET は tint 0.04096 のまま、`SET tint=0.02048` が OK・GET 0.02048。陽性対照（`--net-budget-mbs 0`）で `SET tint=0.01024` が OK・GET 0.01024。PL なしの `test_fake.sh net`・`netp` も通過。**YATSUGATAKE M6**（2026-10-30、配線 N/S・ノイズ ON（H-2 だけ道具で OFF）・bit 64dbf45（FDRI は M5 と同じ）・**tcal board**）: `SET tint=0.01024` が `ERR ARG …51.2 MB/s（予算 30 MB/s を越える…）。この構成の tint の最小は 0.02048 s`、直後の GET は 0.02048 のまま（同じ specd で CU が先に 0.02048 にしていた）。`SET tint=0.02048` は OK。陽性対照（`--net-budget-mbs 0` で起こし直し）で 0.01024 が OK
