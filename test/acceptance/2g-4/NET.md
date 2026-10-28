# NET — 予算を越える tint を SET で断る

- **前提**: 共通の前提。**M5 の後**（今の specd にはこの照合が無い。interface 4.5 の約束）
- **手順**:

```bash
python3 specctl.py --host $B "SET tint=0.01024" GET "SET tint=0.02048" GET
```

- **合格**: `SET tint=0.01024` が **ERR**（予算 30 MB/s を越えると理由に出る）で GET の tint は変わらない、`SET tint=0.02048` は OK
- **陽性対照**: 照合を外した specd（試験用の引数）で `SET tint=0.01024` が通る ─ M5 で照合を入れるときに試験の形を決める
- **記録**: なし（M5 で入れる）
