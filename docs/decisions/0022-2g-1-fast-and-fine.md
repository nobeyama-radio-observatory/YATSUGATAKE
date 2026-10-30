# 0022. 2G の 1 ADC を 2G-1-Fast（1 段）と 2G-1-Fine（2 段・DDR の corner turn）の 2 本に

- 状態: 採用
- 決定日: 2026-10-28
- 根拠: study-rfsoc proj024（2G-1）・proj028（2 段分光）・proj030（レーン FFT の 2-for-1）・proj031（PFB の係数を URAM で共有）・[`../knowledge/resources.md`](../knowledge/resources.md)

## 背景

2G-1（proj024、1 ADC × 131072 ch・dt 10.24 ms）は DSP 22 % で、点数の壁はチップ内の記憶だった（前段 PFB の履歴 BRAM ≒ 307・積分器 URAM 48 がどちらも ch 数に比例）。
proj028 は実験枠（YATSUGATAKE とは別）として、荒い PFB の後に PL の DDR4 で corner turn をする 2 段の分光を作り、1 ADC × 3670016 ch（df 0.558 kHz）・dt 286.72 ms が実機で実時間に回ることを確かめた（DSP 1,835・BRAM 440・URAM 66 = 82.5 %、DDR 9.45 GB/s に対して実測の同時の上限 17.66 GB/s）。

## 決定

- 2G の 1 ADC を 2 本にする。**2G-1-Fast**（今の 2G-1 の名前を変えたもの、BIT_KIND 11 のまま）と **2G-1-Fine**（proj028 の形、BIT_KIND 12）
- 2G-1-Fine の既定は N_f 131072（3670016 ch）・dt 286.72 ms。dt は 14.336 ms の倍数、df = fs / (56 · N_f)
- 2G-4 は proj031（2-for-1 ＋ PFB の係数を URAM で 4 コア共有）を土台にする

## 理由

- 用途が違う: Fast は dt 10.24 ms（OTF など速い走査）、Fine は分解能（dt と引き換え）。出口の量はどちらも 12.8 M ch/s で同じ
- 1 段の形では、どの 2G も全 ADC の ch の合計 131072 が上限（履歴と積分器が合計の ch に比例し、FFT の長さは 2 のべき乗なので増やすなら 2 倍）。2-for-1 と URAM の係数は DSP・LUT・電流を減らすが、この壁は動かさない
- 2 段の形は 1 ADC あたり DSP ≒ 1,835・DDR ≒ 9.45 GB/s が要るので、1 ADC でしか入らない（2 ADC で DSP ≒ 86 %・DDR 18.9 GB/s が上限 17.66 GB/s を越える）

## 見送った案

- 2G-2・2G-4 を 2 段にする: DSP と DDR の帯域で入らない（上）
- 2G-1-Fine の N_f 262144（734 万 ch）: 積分器が URAM 88 個になり、dt 573 ms では DDR が 2 面で 5 GB と 4 GB を越える
- 2G-1 を 1 本にして 1 段と 2 段をレジスタで切り替える: 2 段の部品（荒い段・MIG・corner turn）と 1 段の履歴・積分器が同じチップに入らない

## 影響

- 2G-1-Fine は、dt が 10.24 ms・40.96 ms の倍数でなく df が fs / 2^k でない唯一の bit になる。dt はダンプの区切りが時刻の格子 G（2.048 ms）に乗るので時刻の約束（[0009](0009-time-grid-and-integration-time.md)）は守る。Overlay をまたいだ区切りの一致はもともと求めていない
- 移すまでに: 1PPS・DUMP_T を載せる、流れの形（レコードを荒い ch ごとに分ける案）、荒い段の丸めの線（f ± k·fs/56）を下げるかを決める → [ADR 0027](0027-2g-1-fine-records-time-rounding.md) で決めた
