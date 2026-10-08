# hw — PL の設計

**状態: 空。** study-rfsoc の proj021 が完成したら、その RTL をここへ移す（[`docs/migration.md`](../docs/migration.md)）。

| 場所 | 中身 | 境目の決め方 |
|---|---|---|
| `common/` | どの bit も使う、または使いうるコア（時刻・ギアボックス・total power・全帯域の分光・窓の PFB / DDC / 分光・流れとリング） | 「別の bit で中身が変わるか」。変わらないものをここに |
| `board/` | RFSoC 4x2 に固有で bit に依らないもの（タイミング制約・1PPS のピン・PS のプリセット） | |
| `bits/<bit>/` | bit ごとの組み立て（流れの並び・BIT_KIND・係数の表・FFT の設定・Makefile） | 迷ったら bit 側に置き、2 本目の bit で共通に上げる |

bit の名前とディレクトリの対応は [`bits/README.md`](bits/README.md)。
