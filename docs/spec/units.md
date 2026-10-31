# 強度の単位

> **仕様の正典**（[ADR 0021](../decisions/0021-spec-canonical-in-yatsugatake.md)）。単位の式と TP の dBm の換算はここが正。出どころは study-rfsoc proj019。
> [`interface.md`](interface.md) の 1.（単位の行）・5.1（束ね）はここを指す。

## 記録の値

- 受け側に届く SPEC の中身は **生の積分値**: Σ_{N_ACC} (q_re² ＋ q_im²)（PL の 64 bit の和を束ね、最も近い float32 に丸めたもの。[`interface.md`](interface.md) の 4.5）
- ch の並びは **IF の昇順**（第 2 ナイキストで反転しているので FFT の ch の順とは逆）
- TP は Σx²（x = ADC の 16 bit を 2 bit 右へ = 14 bit）とフレーム数

**生の値を残し、換算は受け側でする**（係数を測り直したら過去の記録も直せる）。

## 絶対の単位: ADC 14 bit の LSB²

1 ch の電力を、その ch が入力の分散 σ_x² に寄与する量で表す:

**abs[ch] = (Σp / N_ACC − 2/3) · 4^SHIFT · 4^(4 − G) / 2³¹**

| 記号 | 意味（記録の鍵） |
|---|---|
| Σp | 記録の値（SPEC の中身） |
| N_ACC | 束の総フレーム数 ΣDUMP_N（`nacc`。束ねたときは束全体） |
| SHIFT | 窓の SHIFT（`shift`） |
| G | FFT の入力の小数のビット数（`g`、4 か 5） |
| 2/3 | SHIFT の切り捨ての偏り（成分ごとに +1/3 LSB²）。**引かないと、入力が LSB に近い窓（狭い窓・無入力）で平均が膨らむ** |

- SHIFT にも窓の幅にもよらない固定の係数（アナログの利得を除いて）
- 白色雑音: 2048 MHz 全体の abs の和 = σ_x²。CW（振幅 A）: abs = A²/2
- **窓の abs の和 = 同じ帯域の TP**（0.5 % で一致、proj019）

TP の abs: **σ_x² = Σx² / (フレーム数 · 8192)**

## dBFS・dBm

| 量 | 式 |
|---|---|
| dBFS | 10·log10(σ_x²) − 10·log10(8192²/2)（= − 75.27 dB。0 dBFS = 14 bit の満杯の正弦波） |
| dBm（ADC の口、SMA） | 10·log10(σ_x²) ＋ K_adc |

- K_adc は ADC ごとの係数。**ボードの較正ファイル `/etc/yatsugatake/tp_cal.json`**（[ADR 0025](../decisions/0025-tp-calibration-per-board.md)。リポジトリには置かない。鍵はボードの印と ADC の道。ADC ごとの `k_db`・不確かさ・線形が成り立つ範囲 `valid_dbfs`・日付・出どころ）。換算は `sw/pynq/s45cal.py`。ファイルが無い・当たらないボードでは dBm を出さない（dBFS は出る）
- 開発のボードの値（参考。2026-10-06、PM を ADC の口で）: K = −69.23（A）・−69.36（B）・−69.42（C）・−69.34（D）dB（0 dBFS ≒ +5.85〜+6.04 dBm）、線形の範囲 −47〜−7 dBFS。**SAM45-Fine (2, 3) と SAM45-Wide (1, 1) で同じ値**（TP の作りが同じ。同じ日・同じ配線で dBFS − PM の差 0.03〜0.06 dB）。**2G-4 (3, 1) も同じ値**（ADC の道 1 で引く。2026-10-30 に同じ日・同じ配線で Wide との dBFS − PM の差 0.01〜0.03 dB）。2G-1-Fast (11, 1) も道 1 で同じ値を引く（パワーメーターとの照合は測っていない）
- specd は START の EVENT に係数を載せ、`GET CAL`・STATUS の `tp_dbm` で出す。`valid_dbfs` の外の値は線形を確かめていない（換算はするが、使うときに範囲を見る）
- 用途はレベル合わせ・健全性・ログでの換算。**観測の強度の較正はチョッパーホイール（R − SKY）がする**ので、科学の値には要らない

## 運転のレベル

[`hardware.md`](hardware.md) の「入力」。HOT ≦ −10 dBFS（振り切れ）、運転は HOT ≒ −16 dBFS・SKY ≒ −21 dBFS。
