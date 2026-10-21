# 共通のコア

`hw/common/` の RTL の案内。**各ファイルの冒頭のコメントが正**（仕様・丸め・段数・番地・rev の経緯）。ここは「どれが何をし、どこから読むか」。
bit を組み立てるのは `hw/bits/<bit>/build.tcl`（module reference でブロックデザインに置く）。

対応する模型は `model/`（`win_model.py`・`win_fixed.py`・`pfb4.py`）。**RTL の値は模型と bit 単位で同じ**であることを sim で確かめる（`hw/bits/sam45-fine/sim/`）。

## 置き方（SAM45-Fine）

| セル | モジュール | 数 | 役目 |
|---|---|---|---|
| `s45_core_i`（i = 0..3 = ADC_A..D） | `s45_core` | 4 | ADC 1 本ぶんのコア。**PS はこの名前でコアを見つける** |
| `s45_ring_0` | `s45_ring` | 1 | レコードのリング（CORE_KIND 3） |
| `time_core_0` | `time_core` | 1 | 時刻 |
| `full_sel` | `axis_sel4` | 1 | 4 本から 1 本を選び、`s45_core_0` の RAW の流れへ |
| `gb_adc_i`・`gb_gate_i` | `gb_adc`・`gb_gate` | 4 ずつ | ギアボックスの起動の見張り |

## コアの組み立て

| モジュール | 中身 |
|---|---|
| `s45_core` | win_core ＋（`FULL = 1` なら spec_core / `RAW = 1` なら raw_core）＋ AXI4-Lite の振り分け。番地は 64 KiB（コアの共通 0x0000〜・TP 0x0100〜・流れのブロック 0x4000 ＋ 0x400·s） |
| `win_core` | コアの共通部（自己記述・ギアボックスの制御・TP・時刻の錨）と、DDC の流れ s = 0..NW−1。粗い PFB は NW 窓で共有し、窓ごとに ddc_core・wspec_core。窓の設定（WK・WDPHI・WNS）は WRST で取り込む |
| `rec_fr` | 流れの「凍ったバンク」を持ち主の読みの口から借りて読み、SPEC（と SNAP）のレコードにする。読み遅れは tuser = 1（捨てる）と REC_LATE |
| `rec_arb` | 複数のレコードの流れをレコード単位の順番回しで 1 本に |
| `s45_ring` | レコードを DDR のリングへ（自作の AXI4 の書き手、128 bit、≦ 16 拍のバースト）。空きが足りなければ丸ごと捨てて DROP_CNT。尾に CRC-32（zlib と同じ式） |

## 窓の分光

| モジュール | 中身 |
|---|---|
| `pfb_core` | 粗い PFB（32 点、ホップ 8 サンプル、N = 96 タップ）。1 ビートに 2 フレーム。分岐の和・`dft16f` は共有、ch の選択・(−j)^(k·m)・丸めは窓ごと |
| `ddc_core` | NCO（`nco_rom`、1/4 波の表）→ 半帯域 ÷2 を light × (NS − 1) ＋ final × 1。light の 2 段目より後ろは `hb2s`（時分割）。72 DSP / 窓 |
| `hb2`・`hb2s`・`pair2` | 半帯域 ÷2（並列 / 時分割。値は bit 単位で同じ）・組へのまとめ |
| `wspec_core` | 溜め（5 面の URAM のリング）→ PFB（T = 4、`pfb4_rom`）→ 4096 点 複素 FFT（realtime の IP、tready を守る）→ q = sat18(Y >>> SHIFT)・p = q_re² ＋ q_im² → 64 bit で N_ACC 積む。F0 を時刻の格子に寄せる。PFB のため区切りの重心は矩形より 1.5·L 前 |
| `cmul`・`dft16f`・`tw_rom` | 複素乗算（4 段固定）・16 点 複素 DFT・ひねり係数 |

## 全帯域・生サンプル

| モジュール | 中身 |
|---|---|
| `spec_core` | 8192 点 FFT（16 × 512 に分解、`dft16`）→ 電力 → 積分（4096 ch）。SAM45-Fine の BIT_REV 3 では使わない（`full_kind = fft` で戻せる） |
| `raw_core` | 生サンプルの流れ（KIND 4 RAW）。ダンプごとに頭の 1 フレーム（8192 サンプル）を SNAP のレコードで出す。F-2（1PPS の縁）と specd の SNAP 命令に使う |
| `axis_sel4` | 4 本から 1 本（流れの SRC で選ぶ。変えたら起動し直す） |

## 時刻と健全性

| モジュール | 中身 |
|---|---|
| `time_core` | T（64 bit ビート、1 秒 = 256,000,000）・PPS のスタンプ（TRIG・COMP の 2 系統、同期器 3 段）・START_AT の予約発火・健全性の素。バスの段数 LAT を先に足して、コアの t_loc が T と一致するように出す。MMCM のリセットで T は 0 に戻り、ANCHORED が落ちる |
| `dstamp` | ダンプごとの開始のビート（DUMP_T）と健全性（DUMP_H）。入力側で区切りを数え、出力の commit で渡す |
| `adc_ev` | 振り切れ（\|x\| ≧ 32764）と入力の途切れ |
| `tp_core` | Σx²（14 bit）を TP_N フレームごとに区切ってリングへ。FLAGS[4] 振り切れ |

## ギアボックス

| モジュール | 中身 |
|---|---|
| `gb_adc` | ADC ドメインで RFDC の流れを素通しし、起動のやり直し（GRST）のリセットと位相の選び（adj）、RFDC の tvalid の落ちの数え |
| `gb_gate` | 非同期 FIFO の出口。起動の後、K 語溜まるまで読み出しを止める（書きと読みの語の周期が厳密に等しく、起動直後は余裕 0 のまま定常になって 1 回だけ空振りするため）。入口に 2 語のスキッド |

経緯（なぜこの形か）は study-rfsoc の proj011（ギアボックスの起動）・proj013〜015（窓）・proj016〜017（時刻）・proj020（PFB）・proj021（インターフェース v2）の README。ADR は [`../decisions/`](../decisions/) の 0011〜0016。
