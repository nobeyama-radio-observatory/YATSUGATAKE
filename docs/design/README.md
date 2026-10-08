# design — 設計の解説

**状態: 移植待ち。** bit の中身を、使う人・直す人が読める形で解説する。

置く予定のもの:

- `overview.md` — 全体の流れ（ADC → ギアボックス → 全帯域の分光 / 粗い PFB → 窓の DDC → PFB → FFT → 積分 → リング → specd → 受け側）とブロック図
- `cores/` — 共通コアごとの解説（time_core・gb・tp_core・spec_core・win_core・pfb_core・ddc_core・wspec_core・流れとリング）
- `bits/<bit>.md` — bit ごとの組み立てと資源・タイミング

図は study-rfsoc の proj020 の `docs/` にある描画の道具（ブロック図・PFB の原型の図）を移して使う。
