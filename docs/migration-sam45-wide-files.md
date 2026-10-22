# 移植: SAM45-Wide（proj023）のファイルごとの行き先（M0）

[`migration-sam45-wide.md`](migration-sam45-wide.md) の「置き場所の対応」の付録。移植元 `study-rfsoc@proj023-m0` で git が追跡している proj023 のファイル **208 個**を、1 つずつ行き先に当てる。
**置く 83 個**（新しく置く・Wide の側に写しを置く 3 を含む）・**既にある 16 個**（YATSUGATAKE に同じ中身があり、そのまま指す）・**移さない 109 個**。左は proj023 の中のパス。

「proj021-m0 と」の欄は、移植元の土台（proj021-m0 の同じパス）と比べた中身。「既にある」16 個は、YATSUGATAKE の main（1868528）の中身と**バイト単位で同じ**ことを確かめた（M1 の後に YATSUGATAKE で変わったものは無い）。この表は `classify.py`・`mapwide.py`（作業用、リポジトリには入れない）で作り、Wide の Makefile の sim の目標と build.tcl が読むファイル 39 個がすべて「置く」「写し」「既にある」に当たること、`sw/pynq-wide/` の import が閉じていることを確かめた

## 置くもの

| proj023 | YATSUGATAKE | proj021-m0 と | 備考 |
|---|---|---|---|
| `Makefile` | `hw/bits/sam45-wide/Makefile` | 変更 |  |
| `build.tcl` | `hw/bits/sam45-wide/build.tcl` | 変更 |  |
| `model/bin_resp.py` | `model/bin_resp.py` | 新規 |  |
| `model/wide_model.py` | `model/wide_model.py` | 新規 |  |
| `program.tcl` | `hw/bits/sam45-wide/program.tcl` | 同じ |  |
| `pynq/acqboot.py` | `sw/pynq-wide/acqboot.py` | 同じ |  |
| `pynq/bits.example.json` | `sw/pynq-wide/bits.example.json` | 同じ |  |
| `pynq/extref.py` | `sw/pynq-wide/extref.py` | 同じ |  |
| `pynq/gbboot.py` | `sw/pynq-wide/gbboot.py` | 変更 | Fine では移さなかったが、Wide の実機の手順（wide.py の前のギアボックスの起動）が使う |
| `pynq/instr.py` | `sw/pynq-wide/instr.py` | 同じ |  |
| `pynq/plring.py` | `sw/pynq-wide/plring.py` | 変更 |  |
| `pynq/rectap.py` | `sw/pynq-wide/rectap.py` | 同じ |  |
| `pynq/s45acq.py` | `sw/pynq-wide/s45acq.py` | 変更 | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/s45allan.py` | `sw/pynq-wide/s45allan.py` | 同じ |  |
| `pynq/s45cal.py` | `sw/pynq-wide/s45cal.py` | 同じ | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/s45client.py` | `sw/pynq-wide/s45client.py` | 変更 |  |
| `pynq/s45core.py` | `sw/pynq-wide/s45core.py` | 変更 | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/s45lin.py` | `sw/pynq-wide/s45lin.py` | 同じ | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/s45pn.py` | `sw/pynq-wide/s45pn.py` | 同じ |  |
| `pynq/s45proto.py` | `sw/pynq-wide/s45proto.py` | 同じ |  |
| `pynq/s45resp.py` | `sw/pynq-wide/s45resp.py` | 同じ |  |
| `pynq/s45ring.py` | `sw/pynq-wide/s45ring.py` | 同じ |  |
| `pynq/s45snap.py` | `sw/pynq-wide/s45snap.py` | 同じ |  |
| `pynq/s45snapplot.py` | `sw/pynq-wide/s45snapplot.py` | 同じ |  |
| `pynq/s45spur.py` | `sw/pynq-wide/s45spur.py` | 同じ |  |
| `pynq/s45tastar.py` | `sw/pynq-wide/s45tastar.py` | 同じ |  |
| `pynq/s45v2a.py` | `sw/pynq-wide/s45v2a.py` | 同じ |  |
| `pynq/s45v2c.py` | `sw/pynq-wide/s45v2c.py` | 同じ |  |
| `pynq/s45v2f.py` | `sw/pynq-wide/s45v2f.py` | 同じ |  |
| `pynq/sg.py` | `sw/pynq-wide/sg.py` | 変更 |  |
| `pynq/specctl.py` | `sw/pynq-wide/specctl.py` | 同じ |  |
| `pynq/specd.py` | `sw/pynq-wide/specd.py` | 変更 | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/specrecv.py` | `sw/pynq-wide/specrecv.py` | 変更 |  |
| `pynq/spectrometer.py` | `sw/pynq-wide/spectrometer.py` | 変更 |  |
| `pynq/test_cal_b.py` | `sw/pynq-wide/test_cal_b.py` | 新規 |  |
| `pynq/test_fake.sh` | `sw/pynq-wide/test_fake.sh` | 変更 | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/test_regmap.py` | `sw/pynq-wide/test_regmap.py` | 同じ | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/test_tpjump.py` | `sw/pynq-wide/test_tpjump.py` | 同じ |  |
| `pynq/timebase.py` | `sw/pynq-wide/timebase.py` | 変更 | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/timetest.py` | `sw/pynq-wide/timetest.py` | 同じ | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/tp_cal.json` | `sw/pynq-wide/tp_cal.json` | 同じ | Fine の sw/pynq は M1 の後に変わっている（M5a・M5b・pps の符号）。一本化は Wide の M5 |
| `pynq/tpjump.py` | `sw/pynq-wide/tpjump.py` | 同じ |  |
| `pynq/wide.py` | `sw/pynq-wide/wide.py` | 新規 |  |
| `pynq/wide_v2.py` | `sw/pynq-wide/wide_v2.py` | 新規 |  |
| `pynq/widef2.py` | `sw/pynq-wide/widef2.py` | 新規 |  |
| `pynq/wideresp.py` | `sw/pynq-wide/wideresp.py` | 新規 |  |
| `pynq/window.py` | `sw/pynq-wide/window.py` | 同じ |  |
| `sim/check_ds.py` | `hw/bits/sam45-wide/sim/check_ds.py` | 新規 |  |
| `sim/check_wide.py` | `hw/bits/sam45-wide/sim/check_wide.py` | 新規 |  |
| `sim/lane_fft_w_model.v` | `hw/bits/sam45-wide/sim/lane_fft_w_model.v` | 新規 |  |
| `sim/tb_wide_chain.v` | `hw/bits/sam45-wide/sim/tb_wide_chain.v` | 新規 |  |
| `sim/tb_wide_core.v` | `hw/bits/sam45-wide/sim/tb_wide_core.v` | 新規 |  |
| `sim/tb_wide_ds.v` | `hw/bits/sam45-wide/sim/tb_wide_ds.v` | 新規 |  |
| `sim/tb_wide_pfb.v` | `hw/bits/sam45-wide/sim/tb_wide_pfb.v` | 新規 |  |
| `sim/tb_wide_s45.v` | `hw/bits/sam45-wide/sim/tb_wide_s45.v` | 新規 |  |
| `sim/tb_wide_spec.v` | `hw/bits/sam45-wide/sim/tb_wide_spec.v` | 新規 |  |
| `src/common/core_cmn.v` | `hw/common/core_cmn.v` | 新規 |  |
| `src/common/wide_acc.v` | `hw/common/wide_acc.v` | 新規 |  |
| `src/common/wide_chain.v` | `hw/common/wide_chain.v` | 新規 |  |
| `src/common/wide_coef_rom.v` | `hw/common/wide_coef_rom.v` | 新規 |  |
| `src/common/wide_core.v` | `hw/common/wide_core.v` | 新規 |  |
| `src/common/wide_pfb.v` | `hw/common/wide_pfb.v` | 新規 |  |
| `src/common/wide_s45_core.v` | `hw/common/wide_s45_core.v` | 新規 |  |
| `src/common/wide_spec.v` | `hw/common/wide_spec.v` | 新規 |  |
| `src/common/wide_tw_rom.v` | `hw/common/wide_tw_rom.v` | 新規 |  |
| `src/sam45wide/wide_coef.hex` | `hw/bits/sam45-wide/src/wide_coef.hex` | 新規 |  |
| `src/sam45wide/wide_tw.hex` | `hw/bits/sam45-wide/src/wide_tw.hex` | 新規 |  |
| `tools/dump_ps_preset.tcl` | `hw/bits/sam45-wide/tools/dump_ps_preset.tcl` | 同じ |  |
| `tools/estimate.py` | `hw/bits/sam45-wide/tools/estimate.py` | 新規 |  |
| `tools/floorplan.py` | `hw/bits/sam45-wide/tools/floorplan.py` | 同じ |  |
| `tools/floorplan.tcl` | `hw/bits/sam45-wide/tools/floorplan.tcl` | 同じ |  |
| `tools/gb_cdc.tcl` | `hw/bits/sam45-wide/tools/gb_cdc.tcl` | 同じ |  |
| `tools/gb_slow.tcl` | `hw/bits/sam45-wide/tools/gb_slow.tcl` | 同じ |  |
| `tools/gen_wide_coef.py` | `hw/bits/sam45-wide/tools/gen_wide_coef.py` | 新規 |  |
| `tools/gen_wide_tw.py` | `hw/bits/sam45-wide/tools/gen_wide_tw.py` | 新規 |  |
| `tools/h2peek.py` | `sw/pynq-wide/h2peek.py` | 新規 | ボードで sg.py と一緒に使う道具 |
| `tools/ip_survey.tcl` | `hw/bits/sam45-wide/tools/ip_survey.tcl` | 同じ |  |
| `tools/postroute_physopt.tcl` | `hw/bits/sam45-wide/tools/postroute_physopt.tcl` | 変更 |  |
| `tools/sgstat.py` | `sw/pynq-wide/sgstat.py` | 新規 | ボードで sg.py と一緒に使う道具 |
| `tools/worst_paths.tcl` | `hw/bits/sam45-wide/tools/worst_paths.tcl` | 同じ |  |

## Wide の側に写しを置くもの（Fine と共有のファイル。一本化は M1 の後）

| proj023 | YATSUGATAKE | proj021-m0 と | 備考 |
|---|---|---|---|
| `src/common/cmul.v` | `hw/bits/sam45-wide/src/cmul.v` | 変更 | proj023 で口を足した（既定では今までと同じ式）。Fine は hw/common の版を使い続ける |
| `src/common/rec_fr.v` | `hw/bits/sam45-wide/src/rec_fr.v` | 変更 | proj023 で口を足した（既定では今までと同じ式）。Fine は hw/common の版を使い続ける |
| `src/sam45fine/fft_cfg.tcl` | `hw/bits/sam45-wide/src/fft_cfg.tcl` | 同じ | 中身は hw/bits/sam45-fine/src/fft_cfg.tcl と同じ。bit のディレクトリを自分で閉じるために写す |

## 既にあるもの（そのまま指す）

| proj023 | YATSUGATAKE | proj021-m0 と | 備考 |
|---|---|---|---|
| `clocks/LMK04828_245.76_stock.txt` | `hw/board/clocks/LMK04828_245.76_stock.txt` | 同じ |  |
| `clocks/LMX2594_491.52_stock.txt` | `hw/board/clocks/LMX2594_491.52_stock.txt` | 同じ |  |
| `clocks/README.md` | `hw/board/clocks/README.md` | 同じ |  |
| `src/board/pps.xdc` | `hw/board/pps.xdc` | 同じ |  |
| `src/board/ps_preset.tcl` | `hw/board/ps_preset.tcl` | 同じ |  |
| `src/board/timing.xdc` | `hw/board/timing.xdc` | 同じ |  |
| `src/common/adc_ev.v` | `hw/common/adc_ev.v` | 同じ |  |
| `src/common/axis_sel4.v` | `hw/common/axis_sel4.v` | 同じ |  |
| `src/common/dft16.v` | `hw/common/dft16.v` | 同じ |  |
| `src/common/gb_adc.v` | `hw/common/gb_adc.v` | 同じ |  |
| `src/common/gb_gate.v` | `hw/common/gb_gate.v` | 同じ |  |
| `src/common/raw_core.v` | `hw/common/raw_core.v` | 同じ |  |
| `src/common/rec_arb.v` | `hw/common/rec_arb.v` | 同じ |  |
| `src/common/s45_ring.v` | `hw/common/s45_ring.v` | 同じ |  |
| `src/common/time_core.v` | `hw/common/time_core.v` | 同じ |  |
| `src/common/tp_core.v` | `hw/common/tp_core.v` | 同じ |  |

## 移さないもの（必要なら study-rfsoc の proj023 を指す）

| proj023 | proj021-m0 と | 理由 |
|---|---|---|
| `README.md` | 変更 | 経緯と結果。Wide の性能評価（M6）の材料として指す |
| `docs/block_design.py` | 同じ | Fine のブロック図の道具（Wide では描き直していない） |
| `model/pfb4.py` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `model/pfb4_coef.txt` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `model/pfb_proto.py` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `model/pfb_proto2.py` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `model/win_fixed.py` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `model/win_model.py` | 同じ | Fine の模型（model/ に同じものがある。Wide は使わない） |
| `pynq/adcstat.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/bench_ps.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/fcheck.ipynb` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/fine.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/lockcheck.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/resp_explain.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/s45fcheck.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/snap23.snap.npz` | 新規 | 測定の記録 |
| `pynq/v2b.json` | 変更 | 測定の記録 |
| `pynq/v2bp.json` | 変更 | 測定の記録 |
| `pynq/win16.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winallan.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winlin.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winnoise.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winresp.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winsweep.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winwidths.sh` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winwrst.py` | 同じ | proj014〜019・手順 0・1b の試行の道具 |
| `runs/h1a.h1.npz` | 新規 | 測定の記録 |
| `sim/check.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_ddc.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_pfb.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_pfbm.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_ring.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_top.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_tp.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_win.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_win4.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/check_wspec.py` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/lane_fft_model.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/rec_sink.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_ddc.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_gearbox.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_hb2s.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_pfb.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_pfbm.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_raw.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_regmap.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_ring.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_ring_u.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_spec_core.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_t4adc.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_time.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_top.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_tp_core.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_tsys.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_wdelay.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_wgrid.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_win.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_win4.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_wspec.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/tb_wstamp.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `sim/win_fft_model.v` | 同じ | Fine の試験台・照合（Wide の目標は使わない） |
| `src/.gitkeep` | 同じ | 空のディレクトリの印 |
| `src/common/ddc_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/dft16f.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/dstamp.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/hb2.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/hb2s.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/nco_rom.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/pair2.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/pfb_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/s45_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/spec_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/tw_rom.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/win_coef.vh` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/win_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/common/wspec_core.v` | 同じ | Wide では使わない Fine の部品（hw/common に同じものがある） |
| `src/sam45fine/pfb4_rom.v` | 同じ | Fine の PFB の係数 ROM（Wide は使わない） |
| `test/acceptance/F-0.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/F-1.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/F-2.md` | 変更 | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/ID-1.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/P-5.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/P-8.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/PS-1.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/PS-2.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/PS-3.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/README.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/S.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/T-4.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-a.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-b.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-c.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-d.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-e.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-f.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/V2-g.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/W-0.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/W-1.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `test/acceptance/W-G.md` | 同じ | Fine の判定の写し。Wide の判定は M6 の前に test/acceptance/sam45-wide/ に書く |
| `tools/allan.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/gen_coef.py` | 同じ | Fine の係数・DDC の道具（Wide は使わない） |
| `tools/gen_tw_rom.py` | 同じ | Fine の係数・DDC の道具（Wide は使わない） |
| `tools/ipround_model.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/ooc_ddc.tcl` | 同じ | Fine の係数・DDC の道具（Wide は使わない） |
| `tools/tick_analyze.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_burst.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_mock.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_rfi.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_spec_analyze.py` | 同じ | 全帯域（proj013）の解析・使わなくなった道具 |
