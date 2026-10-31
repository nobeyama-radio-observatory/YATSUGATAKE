# 移植: 2G-2（proj034）のファイルごとの行き先（M0）

[`migration-2g-2.md`](migration-2g-2.md) の「置き場所の対応」の付録。移植元のタグ `proj034-m0`（c8b90cb）で git が追跡している `proj034/` のファイル **148 個**を、1 つずつ行き先に当てる。
**置く 45 個**・**2G-2 の側に写しを置く 1 個**・**既にある 81 個**（YATSUGATAKE の同じ名前を指す）・**移さない 21 個**。

比べの相手は YATSUGATAKE の main（73a6740、2G-1-Fast の M7 の後）。「既にある」の `hw/common/`・`hw/board/`・`model/g2_model.py` は**バイト単位で同じ**ことを確かめた。
「比べ」の列は、同じ名前のファイルが `hw/bits/2g-1-fast/`・`hw/bits/2g-4/`（模型は `model/s2_model_g21.py`・`model/s2_model.py`）にあるときの違い（diff の行）。
PS（`pynq/`）は 2G-4 の M5 で `sw/pynq/` に一本化してあり（G22 の Backend を含む）、2G-1-Fast と同じく `sw/pynq-2g/` の段を置かない（本文の「PS」）。
この表は作業用のスクリプト（リポジトリには入れない）で、git の blob を比べて作った。行き先が重ならないことも確かめた

## 置くもの

| 移植元 | YATSUGATAKE | 比べ | 備考 |
|---|---|---|---|
| `Makefile` | `hw/bits/2g-2/Makefile` | — | パスを直す（M1） |
| `build.tcl` | `hw/bits/2g-2/build.tcl` | — | パスを直す（M1） |
| `build_post.tcl` | `hw/bits/2g-2/build_post.tcl` | — | パスを直す（M1）。2G-4 にはある・2G-1-Fast には無い |
| `model/g22_fixed.py` | `model/g22_fixed.py` | — | パスを直さない（同じディレクトリの g2_model を読む） |
| `model/g22_model.py` | `model/g22_model.py` | — | proj025 の模型（`make model-g22`）。同じディレクトリの g22_fixed を読む |
| `model/s2_model.py` | `model/s2_model_g22.py` | 2G-1-Fast（s2_model_g21）と違う(51)・2G-4 と違う(312) | **名前を替える**（2G-4 の `model/s2_model.py`・2G-1-Fast の `model/s2_model_g21.py` と中身が違う。本文の「模型の名前」） |
| `pynq/g22cw.py` | `sw/pynq/g22cw.py` | — | 2G-2 の判定の道具（import は s45client で、`sw/pynq/` にある） |
| `sim/check_g22.py` | `hw/bits/2g-2/sim/check_g22.py` | — | 模型の道を直す（M1） |
| `sim/check_s2.py` | `hw/bits/2g-2/sim/check_s2.py` | 2G-1-Fast と違う(16)・2G-4 と違う(62) | 模型の道と `import s2_model` を直す（M1） |
| `sim/lane_fft_g22_model.v` | `hw/bits/2g-2/sim/lane_fft_g22_model.v` | — |  |
| `sim/rec_fr_ref.v` | `hw/bits/2g-2/sim/rec_fr_ref.v` | 2G-1-Fast と同じ・2G-4 と同じ |  |
| `sim/tb_g22_acc.v` | `hw/bits/2g-2/sim/tb_g22_acc.v` | — |  |
| `sim/tb_g22_chain.v` | `hw/bits/2g-2/sim/tb_g22_chain.v` | — |  |
| `sim/tb_g22_coef.v` | `hw/bits/2g-2/sim/tb_g22_coef.v` | — |  |
| `sim/tb_g22_core.v` | `hw/bits/2g-2/sim/tb_g22_core.v` | — |  |
| `sim/tb_g22_ds.v` | `hw/bits/2g-2/sim/tb_g22_ds.v` | — |  |
| `sim/tb_g22_pfb.v` | `hw/bits/2g-2/sim/tb_g22_pfb.v` | — |  |
| `sim/tb_g22_s45.v` | `hw/bits/2g-2/sim/tb_g22_s45.v` | — |  |
| `sim/tb_g22_spec.v` | `hw/bits/2g-2/sim/tb_g22_spec.v` | — |  |
| `sim/tb_g22_tw.v` | `hw/bits/2g-2/sim/tb_g22_tw.v` | — |  |
| `sim/tb_g22_x2.v` | `hw/bits/2g-2/sim/tb_g22_x2.v` | — |  |
| `sim/tb_lane_g22.v` | `hw/bits/2g-2/sim/tb_lane_g22.v` | — |  |
| `sim/tb_recfr_eq.v` | `hw/bits/2g-2/sim/tb_recfr_eq.v` | 2G-1-Fast と同じ・2G-4 と同じ |  |
| `sim/tb_s2_all.v` | `hw/bits/2g-2/sim/tb_s2_all.v` | 2G-1-Fast と違う(8)・2G-4 と違う(42) |  |
| `sim/tb_s2_sep.v` | `hw/bits/2g-2/sim/tb_s2_sep.v` | 2G-1-Fast と違う(6)・2G-4 と違う(30) |  |
| `src/g22/g22_acc.v` | `hw/bits/2g-2/src/g22/g22_acc.v` | — |  |
| `src/g22/g22_chain.v` | `hw/bits/2g-2/src/g22/g22_chain.v` | — |  |
| `src/g22/g22_coef.v` | `hw/bits/2g-2/src/g22/g22_coef.v` | — |  |
| `src/g22/g22_coef_hi.hex` | `hw/bits/2g-2/src/g22/g22_coef_hi.hex` | — |  |
| `src/g22/g22_coef_lo.hex` | `hw/bits/2g-2/src/g22/g22_coef_lo.hex` | — |  |
| `src/g22/g22_core.v` | `hw/bits/2g-2/src/g22/g22_core.v` | — |  |
| `src/g22/g22_pfb.v` | `hw/bits/2g-2/src/g22/g22_pfb.v` | — |  |
| `src/g22/g22_pfb_core.v` | `hw/bits/2g-2/src/g22/g22_pfb_core.v` | — |  |
| `src/g22/g22_s45_core.v` | `hw/bits/2g-2/src/g22/g22_s45_core.v` | — |  |
| `src/g22/g22_spec.v` | `hw/bits/2g-2/src/g22/g22_spec.v` | — |  |
| `src/g22/g22_tw.v` | `hw/bits/2g-2/src/g22/g22_tw.v` | — |  |
| `src/g22/g22_tw_a.hex` | `hw/bits/2g-2/src/g22/g22_tw_a.hex` | — |  |
| `src/g22/g22_tw_b.hex` | `hw/bits/2g-2/src/g22/g22_tw_b.hex` | — |  |
| `src/s2_chain.v` | `hw/bits/2g-2/src/s2_chain.v` | 2G-1-Fast と違う(52)・2G-4 と違う(64) |  |
| `src/s2_q.v` | `hw/bits/2g-2/src/s2_q.v` | 2G-1-Fast と違う(15)・2G-4 と違う(35) |  |
| `src/s2_sep.v` | `hw/bits/2g-2/src/s2_sep.v` | 2G-1-Fast と違う(14)・2G-4 と違う(26) |  |
| `tools/gen_g22_tables.py` | `hw/bits/2g-2/tools/gen_g22_tables.py` | — | 模型の道を直す（M1）。`make gen` |
| `tools/ip_impl.tcl` | `hw/bits/2g-2/tools/ip_impl.tcl` | 2G-1-Fast と同じ・2G-4 と同じ |  |
| `tools/ip_survey.tcl` | `hw/bits/2g-2/tools/ip_survey.tcl` | 2G-1-Fast と同じ・2G-4 と同じ |  |
| `tools/ooc_rtl.tcl` | `hw/bits/2g-2/tools/ooc_rtl.tcl` | 2G-1-Fast と同じ・2G-4 と違う(8) |  |

## 2G-2 の側に写しを置くもの

| 移植元 | YATSUGATAKE | 備考 |
|---|---|---|
| `src/common/rec_fr.v` | `hw/bits/2g-2/src/rec_fr.v` | `hw/common/` と違う（6 行）・`hw/bits/2g-1-fast/src/rec_fr.v`・`hw/bits/2g-4/src/rec_fr.v` と同じ |

## 既にあるもの（移さず、YATSUGATAKE の同じ名前を指す）

| 移植元 | YATSUGATAKE |
|---|---|
| `model/g2_model.py` | `model/g2_model.py` |
| `pynq/acqboot.py` | `sw/pynq/acqboot.py` |
| `pynq/bits.example.json` | `sw/pynq/bits.example.json`（違う(10)。`sw/pynq/` の一本化した版を使う） |
| `pynq/extref.py` | `sw/pynq/extref.py` |
| `pynq/g21cw.py` | `sw/pynq/g21cw.py` |
| `pynq/instr.py` | `sw/pynq/instr.py`（違う(105)。`sw/pynq/` の一本化した版を使う） |
| `pynq/plring.py` | `sw/pynq/plring.py`（違う(53)。`sw/pynq/` の一本化した版を使う） |
| `pynq/rectap.py` | `sw/pynq/rectap.py` |
| `pynq/s45acq.py` | `sw/pynq/s45acq.py`（違う(495)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45allan.py` | `sw/pynq/s45allan.py`（違う(5)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45cal.py` | `sw/pynq/s45cal.py`（違う(111)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45client.py` | `sw/pynq/s45client.py` |
| `pynq/s45core.py` | `sw/pynq/s45core.py`（違う(30)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45lin.py` | `sw/pynq/s45lin.py`（違う(33)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45pn.py` | `sw/pynq/s45pn.py` |
| `pynq/s45proto.py` | `sw/pynq/s45proto.py` |
| `pynq/s45resp.py` | `sw/pynq/s45resp.py`（違う(8)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45ring.py` | `sw/pynq/s45ring.py`（違う(27)。`sw/pynq/` の一本化した版を使う） |
| `pynq/s45snap.py` | `sw/pynq/s45snap.py` |
| `pynq/s45snapplot.py` | `sw/pynq/s45snapplot.py` |
| `pynq/s45spur.py` | `sw/pynq/s45spur.py` |
| `pynq/s45tastar.py` | `sw/pynq/s45tastar.py` |
| `pynq/s45v2a.py` | `sw/pynq/s45v2a.py` |
| `pynq/s45v2c.py` | `sw/pynq/s45v2c.py` |
| `pynq/s45v2f.py` | `sw/pynq/s45v2f.py` |
| `pynq/sg.py` | `sw/pynq/sg.py` |
| `pynq/specctl.py` | `sw/pynq/specctl.py` |
| `pynq/specd.py` | `sw/pynq/specd.py`（違う(56)。`sw/pynq/` の一本化した版を使う） |
| `pynq/specrecv.py` | `sw/pynq/specrecv.py` |
| `pynq/spectrometer.py` | `sw/pynq/spectrometer.py`（違う(2)。`sw/pynq/` の一本化した版を使う） |
| `pynq/test_cal_b.py` | `sw/pynq/test_cal_b.py` |
| `pynq/test_fake.sh` | `sw/pynq/test_fake.sh`（違う(162)。`sw/pynq/` の一本化した版を使う） |
| `pynq/test_nch.py` | `sw/pynq/test_nch.py` |
| `pynq/test_regmap.py` | `sw/pynq/test_regmap.py`（違う(3)。`sw/pynq/` の一本化した版を使う） |
| `pynq/test_tpjump.py` | `sw/pynq/test_tpjump.py` |
| `pynq/timebase.py` | `sw/pynq/timebase.py`（違う(206)。`sw/pynq/` の一本化した版を使う） |
| `pynq/timetest.py` | `sw/pynq/timetest.py`（違う(7)。`sw/pynq/` の一本化した版を使う） |
| `pynq/tpjump.py` | `sw/pynq/tpjump.py` |
| `pynq/wide.py` | `sw/pynq/wide.py`（違う(4)。`sw/pynq/` の一本化した版を使う） |
| `pynq/wide_v2.py` | `sw/pynq/wide_v2.py`（違う(1)。`sw/pynq/` の一本化した版を使う） |
| `pynq/widef2.py` | `sw/pynq/widef2.py`（違う(48)。`sw/pynq/` の一本化した版を使う） |
| `pynq/wideresp.py` | `sw/pynq/wideresp.py`（違う(52)。`sw/pynq/` の一本化した版を使う） |
| `pynq/window.py` | `sw/pynq/window.py`（違う(4)。`sw/pynq/` の一本化した版を使う） |
| `src/board/pps.xdc` | `hw/board/pps.xdc` |
| `src/board/ps_preset.tcl` | `hw/board/ps_preset.tcl` |
| `src/board/timing.xdc` | `hw/board/timing.xdc` |
| `src/common/adc_ev.v` | `hw/common/adc_ev.v` |
| `src/common/axis_sel4.v` | `hw/common/axis_sel4.v` |
| `src/common/cmul.v` | `hw/common/cmul.v` |
| `src/common/core_cmn.v` | `hw/common/core_cmn.v` |
| `src/common/ddc_core.v` | `hw/common/ddc_core.v` |
| `src/common/dft16.v` | `hw/common/dft16.v` |
| `src/common/dft16f.v` | `hw/common/dft16f.v` |
| `src/common/dstamp.v` | `hw/common/dstamp.v` |
| `src/common/gb_adc.v` | `hw/common/gb_adc.v` |
| `src/common/gb_gate.v` | `hw/common/gb_gate.v` |
| `src/common/hb2.v` | `hw/common/hb2.v` |
| `src/common/hb2s.v` | `hw/common/hb2s.v` |
| `src/common/nco_rom.v` | `hw/common/nco_rom.v` |
| `src/common/pair2.v` | `hw/common/pair2.v` |
| `src/common/pfb_core.v` | `hw/common/pfb_core.v` |
| `src/common/raw_core.v` | `hw/common/raw_core.v` |
| `src/common/rec_arb.v` | `hw/common/rec_arb.v` |
| `src/common/s45_core.v` | `hw/common/s45_core.v` |
| `src/common/s45_ring.v` | `hw/common/s45_ring.v` |
| `src/common/spec_core.v` | `hw/common/spec_core.v` |
| `src/common/time_core.v` | `hw/common/time_core.v` |
| `src/common/tp_core.v` | `hw/common/tp_core.v` |
| `src/common/tw_rom.v` | `hw/common/tw_rom.v` |
| `src/common/wide_acc.v` | `hw/common/wide_acc.v` |
| `src/common/wide_chain.v` | `hw/common/wide_chain.v` |
| `src/common/wide_coef_rom.v` | `hw/common/wide_coef_rom.v` |
| `src/common/wide_core.v` | `hw/common/wide_core.v` |
| `src/common/wide_pfb.v` | `hw/common/wide_pfb.v` |
| `src/common/wide_s45_core.v` | `hw/common/wide_s45_core.v` |
| `src/common/wide_spec.v` | `hw/common/wide_spec.v` |
| `src/common/wide_tw_rom.v` | `hw/common/wide_tw_rom.v` |
| `src/common/win_coef.vh` | `hw/common/win_coef.vh` |
| `src/common/win_core.v` | `hw/common/win_core.v` |
| `src/common/wspec_core.v` | `hw/common/wspec_core.v` |
| `tools/amslog.py` | `sw/pynq/amslog.py`（中身は違う（注釈 1 行）。`sw/pynq/` の版を使う） |

## 移さないもの

| 移植元 | 理由 |
|---|---|
| `README.md` | 記録（README の結論はこの文書に引く） |
| `pynq/adcstat.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/bench_g21.py` | proj024 の取得の速さの調べ |
| `pynq/bench_ps.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/fcheck.ipynb` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/fine.py` | SAM45-Fine の道具（`sw/pynq/` に入れていない） |
| `pynq/gbboot.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/lockcheck.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/resp_explain.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/s45fcheck.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/tp_cal.json` | ボードに置く較正（ADR 0025。リポジトリに戻さない） |
| `pynq/win16.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winallan.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winlin.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winnoise.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winresp.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winsweep.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winwidths.sh` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `pynq/winwrst.py` | Fine・窓・試行の道具（2G-4・2G-1-Fast の移植でも移さなかった） |
| `tools/power_rpt.tcl` | 電力の見積もりの報告（B-1 の調べ） |
| `tools/shapecmp22.py` | R-2 の proj025 との床の比べ（移植では比べる相手が無い） |
