# NET — 予算を越える tint を SET で断る

- **前提**: 共通の前提（specd は既定の引数。`--net-budget-mbs` を渡さない）。照合は 2G-4 の M5 で入れた `s45acq.check_net`（interface 4.5）。量は float32 の SPEC の中身（頭・TP は数えない）で、2G-2 は 2 × 65,536 ch × 4 B / tint（2G-4・2G-1-Fast と同じ量）
- **手順**:

```bash
python3 specctl.py --host $B "SET tint=0.01024" GET "SET tint=0.02048" GET
```

- **合格**: `SET tint=0.01024` が **ERR**（理由に「51.2 MB/s」「予算 30 MB/s を越える」「この構成の tint の最小は 0.02048 s」）で、直後の GET の tint は変わらない（起動の既定 0.04096）。`SET tint=0.02048` は OK で GET が 0.02048
- **陽性対照**: specd を **`--net-budget-mbs 0`**（照合を外す）で起こし直し、同じ手順で `SET tint=0.01024` が OK・GET が 0.01024
- **PL なしの照合**: `bash test_fake.sh net`（2G-2 の `--g22` で 10.24 ms が ERR・20.48 ms が OK を含む）と `netp`（照合なしで通る）
- **記録**: なし（2G-2 の bit では M6 で初めて回す）。参考: 2G-4 の M5・M6、2G-1-Fast の M5・M6 で同じ文の ERR
