# 付録: SpW8 の移植のファイルの行き先（M0、2026-11-03）

[`migration-spw8.md`](migration-spw8.md) の「置き場所の対応」の 1 つずつの表。study-rfsoc の proj032 で git が追跡している 198 個（`git ls-tree -r proj032`、commit 0e612e9）。
**置く 58・既にある 15・移さない 125**。「既にある」の比べは YATSUGATAKE の main（54ce5e3）と。表は機械で作った（比べは `cmp`）。

| study-rfsoc（proj032） | 扱い | YATSUGATAKE | 備考 |
|---|---|---|---|
| `Makefile` | 移さない | — | proj の README・テンプレートの Makefile・program.tcl |
| `README.md` | 移さない | — | proj の README・テンプレートの Makefile・program.tcl |
| `b1/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/build_post.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/pynq/extref.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/pynq/plring.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/pynq/s45core.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/pynq/spw_b1.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b1/runs/p7_1.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_2.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_cw3574.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_cw3574_p9.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_cw3594.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_ncw3574_p9.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_ncw3594_p9.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_ns_on_sgoff.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r1a.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r1b.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r1c.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r1d.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r2a.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r2b.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r2c.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b1/runs/p7_r2d.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/build_post.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/pynq/extref.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/pynq/plring.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/pynq/s45core.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/pynq/spw_b2.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/runs/p8_A_wg3.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_A_wg4.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_A_wg5.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_B_wg3.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_B_wg4.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_cw2486.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_cw2782.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_cw3308.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8_cw3574.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8r3_A_wg4.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8r4_A_wg4.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8r4_A_wg4b.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/runs/p8r4_B_wg4.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b2/src/board/clk_mon.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/src/board/ddr4.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `b2/src/clk_mon.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/build_post.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/pynq/extref.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/pynq/plring.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/pynq/s45core.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/pynq/spw_b3.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/src/board/clk_mon.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/src/board/ddr4.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `b3/src/clk_mon.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/build_post.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/pynq/extref.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/pynq/plring.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/pynq/s45core.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/pynq/spw_b4.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `b4/runs/p9b4_b1.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/Makefile` | 置く | `hw/bits/spw8/Makefile` | パスだけを直す |
| `b5/build.tcl` | 置く | `hw/bits/spw8/build.tcl` | パスだけを直す |
| `b5/build_post.tcl` | 置く | `hw/bits/spw8/build_post.tcl` | パスだけを直す |
| `b5/pynq/extref.py` | 置く | `hw/bits/spw8/pynq/extref.py` | M4 の試行の道具（決めること 2）。sw/pynq と同じ中身 |
| `b5/pynq/plring.py` | 置く | `hw/bits/spw8/pynq/plring.py` | M4 の試行の道具（決めること 2）。sw/pynq の同名と違う版 |
| `b5/pynq/s45core.py` | 置く | `hw/bits/spw8/pynq/s45core.py` | M4 の試行の道具（決めること 2）。sw/pynq の同名と違う版 |
| `b5/pynq/spw_b5.py` | 置く | `hw/bits/spw8/pynq/spw_b5.py` | M4 の試行の道具（決めること 2） |
| `b5/pynq/spwfast.c` | 置く | `hw/bits/spw8/pynq/spwfast.c` | M4 の試行の道具（決めること 2） |
| `b5/pynq/spwplan.py` | 置く | `hw/bits/spw8/pynq/spwplan.py` | M4 の試行の道具（決めること 2） |
| `b5/runs/p10_plan1.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p10_plan2.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_cw0.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_cw1.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_cw2.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_fast.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_fast2.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_long.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p13_py.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p9b5_b5.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p9b5_b5_2.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `b5/runs/p9b5_b5_ng10.json` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `build.tcl` | 移さない | — | proj の README・テンプレートの Makefile・program.tcl |
| `d1/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/program.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/pynq/ddr_bw.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/pynq/spw_ddr.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/src/board/clk_mon.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/src/board/ddr4.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/src/board/ps_preset.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/src/clk_mon.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/src/ddr_tg.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/tb/tb_clk_mon.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d1/tb/tb_ddr_tg.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/Makefile` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/build.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/program.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/pynq/hp_bw.py` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/src/board/clk_mon.xdc` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/src/board/ps_preset.tcl` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/src/clk_mon.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/src/hp_tg.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `d3/tb/tb_hp_tg.v` | 移さない | — | b5 より前の形・DDR の試験 |
| `model/dump_burst.py` | 移さない | — | 見積もりの模型（K-1・E-4・M-2）。b5 の作りに使わない |
| `model/eng_sched.py` | 移さない | — | 見積もりの模型（K-1・E-4・M-2）。b5 の作りに使わない |
| `model/m2_hist8.py` | 移さない | — | 見積もりの模型（K-1・E-4・M-2）。b5 の作りに使わない |
| `model/pfb4_coef.txt` | 既にある | `model/pfb4_coef.txt` | バイト単位で同じ |
| `model/pfb64_fixed.py` | 置く | `model/pfb64_fixed.py` | sim と test_spwplan が読む |
| `model/win64_fixed.py` | 置く | `model/win64_fixed.py` | sim と test_spwplan が読む |
| `model/win64_model.py` | 置く | `model/win64_model.py` | sim と test_spwplan が読む |
| `program.tcl` | 移さない | — | proj の README・テンプレートの Makefile・program.tcl |
| `runs/d3_hog3_1.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/d3_hp_bw_1.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/d3_hp_bw_hog.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/d3_hp_bw_hog1.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/e1_fine_hier.rpt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/e4_sched.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/k1_burst.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/k2_sink.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/m0_altk.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/m0_coef.json` | 置く | `model/spw8_coef.json` | 名前を替える（係数の設計。模型と sim が読む） |
| `runs/m2_hist8.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `runs/m3_sweep.txt` | 移さない | — | 試行の記録（study-rfsoc に残す） |
| `sim/axi_mem_model.v` | 置く | `hw/bits/spw8/sim/axi_mem_model.v` |  |
| `sim/check_f32cv.py` | 置く | `hw/bits/spw8/sim/check_f32cv.py` |  |
| `sim/check_front.py` | 置く | `hw/bits/spw8/sim/check_front.py` |  |
| `sim/check_head.py` | 置く | `hw/bits/spw8/sim/check_head.py` |  |
| `sim/check_pfb64.py` | 置く | `hw/bits/spw8/sim/check_pfb64.py` |  |
| `sim/check_pfb_chain.py` | 置く | `hw/bits/spw8/sim/check_pfb_chain.py` |  |
| `sim/check_ring.py` | 置く | `hw/bits/spw8/sim/check_ring.py` |  |
| `sim/check_spwdelay.py` | 置く | `hw/bits/spw8/sim/check_spwdelay.py` |  |
| `sim/check_wsb.py` | 置く | `hw/bits/spw8/sim/check_wsb.py` |  |
| `sim/tb_core.v` | 置く | `hw/bits/spw8/sim/tb_core.v` |  |
| `sim/tb_ddcb.v` | 置く | `hw/bits/spw8/sim/tb_ddcb.v` |  |
| `sim/tb_f32cv.v` | 置く | `hw/bits/spw8/sim/tb_f32cv.v` |  |
| `sim/tb_front.v` | 置く | `hw/bits/spw8/sim/tb_front.v` |  |
| `sim/tb_hbmc.v` | 置く | `hw/bits/spw8/sim/tb_hbmc.v` |  |
| `sim/tb_head.v` | 置く | `hw/bits/spw8/sim/tb_head.v` |  |
| `sim/tb_pfb64.v` | 置く | `hw/bits/spw8/sim/tb_pfb64.v` |  |
| `sim/tb_rmux4.v` | 置く | `hw/bits/spw8/sim/tb_rmux4.v` |  |
| `sim/tb_spw_regs.v` | 置く | `hw/bits/spw8/sim/tb_spw_regs.v` |  |
| `sim/tb_spwdelay.v` | 置く | `hw/bits/spw8/sim/tb_spwdelay.v` |  |
| `sim/tb_wsb.v` | 置く | `hw/bits/spw8/sim/tb_wsb.v` |  |
| `sim/win_fft_model.v` | 置く | `hw/bits/spw8/sim/win_fft_model.v` |  |
| `src/.gitkeep` | 移さない | — |  |
| `src/board/pps.xdc` | 既にある | `hw/board/pps.xdc` | バイト単位で同じ |
| `src/board/ps_preset.tcl` | 既にある | `hw/board/ps_preset.tcl` | バイト単位で同じ |
| `src/board/timing.xdc` | 既にある | `hw/board/timing.xdc` | バイト単位で同じ |
| `src/common/adc_ev.v` | 既にある | `hw/common/adc_ev.v` | 注釈 1 行だけ違う |
| `src/common/cmul.v` | 既にある | `hw/common/cmul.v` | 書き方の違い（SH 既定 16 で同じ式） |
| `src/common/core_cmn.v` | 既にある | `hw/common/core_cmn.v` | 注釈 1 行だけ違う |
| `src/common/dft16f.v` | 既にある | `hw/common/dft16f.v` | バイト単位で同じ |
| `src/common/gb_adc.v` | 既にある | `hw/common/gb_adc.v` | 注釈 1 行だけ違う |
| `src/common/gb_gate.v` | 既にある | `hw/common/gb_gate.v` | 注釈 1 行だけ違う |
| `src/common/hb2.v` | 既にある | `hw/common/hb2.v` | バイト単位で同じ |
| `src/common/hb2s.v` | 既にある | `hw/common/hb2s.v` | バイト単位で同じ |
| `src/common/nco_rom.v` | 既にある | `hw/common/nco_rom.v` | バイト単位で同じ |
| `src/common/time_core.v` | 既にある | `hw/common/time_core.v` | 注釈 1 行だけ違う |
| `src/common/tp_core.v` | 既にある | `hw/common/tp_core.v` | 注釈 1 行だけ違う |
| `src/spw/ddcb.v` | 置く | `hw/bits/spw8/src/spw/ddcb.v` | b5 の build.tcl が読む |
| `src/spw/ddrr.v` | 置く | `hw/bits/spw8/src/spw/ddrr.v` | b5 の build.tcl が読む |
| `src/spw/ddrr_mux3.v` | 置く | `hw/bits/spw8/src/spw/ddrr_mux3.v` | sim だけ（tb_core -DRDMUX） |
| `src/spw/ddrw.v` | 置く | `hw/bits/spw8/src/spw/ddrw.v` | b5 の build.tcl が読む |
| `src/spw/dsink.v` | 置く | `hw/bits/spw8/src/spw/dsink.v` | b5 の build.tcl が読む |
| `src/spw/eng.v` | 置く | `hw/bits/spw8/src/spw/eng.v` | b5 の build.tcl が読む |
| `src/spw/f32cv.v` | 置く | `hw/bits/spw8/src/spw/f32cv.v` | b5 の build.tcl が読む |
| `src/spw/hb_coef.vh` | 置く | `hw/bits/spw8/src/spw/hb_coef.vh` | b5 の build.tcl が読む |
| `src/spw/hbmc.v` | 置く | `hw/bits/spw8/src/spw/hbmc.v` | b5 の build.tcl が読む |
| `src/spw/hbmc_ooc.v` | 移さない | — | b2・b3 の DDR の形か OOC の包み。b5 と sim は読まない |
| `src/spw/head_core.v` | 置く | `hw/bits/spw8/src/spw/head_core.v` | b5 の build.tcl が読む |
| `src/spw/ksink_ooc.v` | 移さない | — | b2・b3 の DDR の形か OOC の包み。b5 と sim は読まない |
| `src/spw/pfb4_rom.v` | 置く | `hw/bits/spw8/src/spw/pfb4_rom.v` | b5 の build.tcl が読む |
| `src/spw/pfb64_coef.vh` | 置く | `hw/bits/spw8/src/spw/pfb64_coef.vh` | b5 の build.tcl が読む |
| `src/spw/pfb64_core.v` | 置く | `hw/bits/spw8/src/spw/pfb64_core.v` | b5 の build.tcl が読む |
| `src/spw/ring128.v` | 置く | `hw/bits/spw8/src/spw/ring128.v` | b5 の build.tcl が読む |
| `src/spw/rmux128.v` | 置く | `hw/bits/spw8/src/spw/rmux128.v` | b5 の build.tcl が読む |
| `src/spw/rmux4.v` | 置く | `hw/bits/spw8/src/spw/rmux4.v` | b5 の build.tcl が読む |
| `src/spw/sfifo.v` | 置く | `hw/bits/spw8/src/spw/sfifo.v` | b5 の build.tcl が読む |
| `src/spw/spw_core.v` | 置く | `hw/bits/spw8/src/spw/spw_core.v` | b5 の build.tcl が読む |
| `src/spw/spw_front.v` | 置く | `hw/bits/spw8/src/spw/spw_front.v` | b5 の build.tcl が読む |
| `src/spw/spw_regs.v` | 置く | `hw/bits/spw8/src/spw/spw_regs.v` | b5 の build.tcl が読む |
| `src/spw/spw_s45_core.v` | 置く | `hw/bits/spw8/src/spw/spw_s45_core.v` | b5 の build.tcl が読む |
| `src/spw/spw_s45_core_ddr.v` | 移さない | — | b2・b3 の DDR の形か OOC の包み。b5 と sim は読まない |
| `src/spw/spw_s45_core_ddrm.v` | 移さない | — | b2・b3 の DDR の形か OOC の包み。b5 と sim は読まない |
| `src/spw/wsb.v` | 置く | `hw/bits/spw8/src/spw/wsb.v` | b5 の build.tcl が読む |
| `src/spw/wsb_ooc.v` | 移さない | — | b2・b3 の DDR の形か OOC の包み。b5 と sim は読まない |
| `tools/crc128_masks.py` | 置く | `hw/bits/spw8/tools/crc128_masks.py` | ring128 の CRC の係数を作る |
| `tools/estimate.py` | 移さない | — | OOC・見積もり・電力の試行の道具 |
| `tools/ooc_rtl.tcl` | 移さない | — | OOC・見積もり・電力の試行の道具 |
| `tools/pwr_cal.tcl` | 移さない | — | OOC・見積もり・電力の試行の道具 |
| `tools/rep_util.tcl` | 移さない | — | OOC・見積もり・電力の試行の道具 |
| `tools/test_spwplan.py` | 置く | `hw/bits/spw8/tools/test_spwplan.py` | spwplan の机の上の試験 |

