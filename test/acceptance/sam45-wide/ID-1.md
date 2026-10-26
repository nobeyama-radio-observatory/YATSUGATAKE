# ID-1 — 自己記述と起動の見張り（FLAGS・IP の位相）

- **前提**: 共通の前提。ボード直（root、specd を止めてから）。配線はどれでも
- **手順**:

```bash
sudo -E $(which python3) wide.py --clkin 0 --ref 10 --list
```

- **合格**（測る前に決めた条件）:
  - bit: SAM45-Wide（BIT_KIND 1）rev 1・PROJ 0x0023_0100。4 コアとも IF_ID 0x0201_0101・CAPS 0x003・BASE_BEATS 2,621,440・BUILD 0x50c0000i（コア i）、time_core 0x0201_0102
  - NSTREAM 3 / 2 / 2 / 2。SLICE の流れ 8 本（SID 0x0202_0000・0x0202_0100、NCH 4096・FRAME_BEATS 2048・PARAM 0x0040000f・NFFT_MIN_MAX 0x0f0d）、コア 0 の流れ 2 が RAW（SID 0x0204_0200・NCH 0・FRAME_BEATS 512）
  - FFT_N（効いている・書いた・物理）が 4 コアとも 15・15・15
  - **起動の見張り**: 4 コアとも FLAGS 0x00 → 0x00（Overlay から今まで → 消して 0.5 s 後）、go 1・have_first 1、待たされた 1・待ち行列 2 語、IP の位相 入口 8・出口 155・遅れ 147
  - ログに LMX2594 を PWR 3 で書いた行
- **陽性対照**: なし（起動の見張りの FLAGS は、直す前の RTL で 0x30 / 0x32 が立ったことがある: proj023 手順 4b の 4〜6 回目。sim の wsp-rdy・wsp-stlp が同じ形で落ちる）
- **記録**: **YATSUGATAKE M6 で通過（2026-10-23、bit `54b0dbea…`・usr ba456e10・PWR 3、`~/m2/m6w/n1/n1_id1.txt`）: 予言どおり。N1 の Overlay 9 回とも起動の見張り 0x00 → 0x00・入口 8・出口 155**。 proj023 手順 4b の 7 回目（2026-10-17、ビルド 11）: 4 コアとも 0x00 → 0x00・入口 8・出口 155・遅れ 147、Overlay の読み直し 5 回とも同じ。YATSUGATAKE M4（2026-10-22）・M5（2026-10-23、`w_list.txt`）で同じ値（PWR 31）
