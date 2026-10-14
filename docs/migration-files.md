# 移植: proj021 のファイルごとの行き先（M0 で確定）

[`migration.md`](migration.md) の「置き場所の対応」の付録。移植元 `study-rfsoc@proj021-m0` で git が追跡している proj021 のファイル **229 個**を、1 つずつ行き先に当てる。
移す **156 個**・移さない **73 個**。左は proj021 の中のパス。

M1 では表の行き先へ**置き直してパスだけを直す**（中身は変えない）。直すパスは `Makefile`・`build.tcl`・`tools/` の生成の道具・`sim/` の照合の道具（`src/` の位置、`model/` と `sw/pynq/` の位置）。

## 移すもの

| proj021 | YATSUGATAKE | 備考 |
|---|---|---|
| `Makefile` | `hw/bits/sam45-fine/Makefile` | 共通の手続きを hw/common/tcl/ に出すのは M1 の後の別 PR |
| `build.tcl` | `hw/bits/sam45-fine/build.tcl` | 共通の手続きを hw/common/tcl/ に出すのは M1 の後の別 PR |
| `clocks/LMK04828_245.76_stock.txt` | `hw/board/clocks/LMK04828_245.76_stock.txt` | 出荷時の控え（実行時には読まない） |
| `clocks/LMX2594_491.52_stock.txt` | `hw/board/clocks/LMX2594_491.52_stock.txt` | 出荷時の控え（実行時には読まない） |
| `clocks/README.md` | `hw/board/clocks/README.md` | 出荷時の控え（実行時には読まない） |
| `docs/block_design.py` | `docs/design/sam45-fine/block_design.py` |  |
| `docs/block_design.svg` | `docs/design/sam45-fine/block_design.svg` |  |
| `docs/floorplan_2-5.png` | `docs/design/sam45-fine/floorplan_2-5.png` |  |
| `docs/pfb_T4_vs_T8.png` | `docs/design/sam45-fine/pfb_T4_vs_T8.png` |  |
| `docs/pfb_cand_50_40dB.png` | `docs/design/sam45-fine/pfb_cand_50_40dB.png` |  |
| `docs/pfb_cand_60dB.png` | `docs/design/sam45-fine/pfb_cand_60dB.png` |  |
| `docs/pfb_chain.html` | `docs/design/sam45-fine/pfb_chain.html` |  |
| `docs/pfb_resp_T4.png` | `docs/design/sam45-fine/pfb_resp_T4.png` |  |
| `docs/pfb_resp_T8.png` | `docs/design/sam45-fine/pfb_resp_T8.png` |  |
| `docs/win_chain.html` | `docs/design/sam45-fine/win_chain.html` |  |
| `model/pfb4.py` | `model/pfb4.py` |  |
| `model/pfb4_coef.txt` | `model/pfb4_coef.txt` |  |
| `model/pfb_proto.py` | `model/pfb_proto.py` |  |
| `model/pfb_proto2.py` | `model/pfb_proto2.py` |  |
| `model/win_fixed.py` | `model/win_fixed.py` |  |
| `model/win_model.py` | `model/win_model.py` |  |
| `program.tcl` | `hw/bits/sam45-fine/program.tcl` | 共通の手続きを hw/common/tcl/ に出すのは M1 の後の別 PR |
| `pynq/acqboot.py` | `sw/pynq/acqboot.py` | specd の実行に要る（specd が import する） |
| `pynq/bits.example.json` | `sw/pynq/bits.example.json` | 較正・bit の一覧のひな形 |
| `pynq/extref.py` | `sw/pynq/extref.py` | specd の実行に要る（specd が import する） |
| `pynq/instr.py` | `sw/pynq/instr.py` | 判定・試験 |
| `pynq/plring.py` | `sw/pynq/plring.py` | specd の実行に要る（specd が import する） |
| `pynq/rectap.py` | `sw/pynq/rectap.py` | specd の実行に要る（specd が import する） |
| `pynq/s45acq.py` | `sw/pynq/s45acq.py` | specd の実行に要る（specd が import する） |
| `pynq/s45allan.py` | `sw/pynq/s45allan.py` | 性能の測り（M6） |
| `pynq/s45cal.py` | `sw/pynq/s45cal.py` | specd の実行に要る（specd が import する） |
| `pynq/s45client.py` | `sw/pynq/s45client.py` | 受け側・制御 |
| `pynq/s45core.py` | `sw/pynq/s45core.py` | specd の実行に要る（specd が import する） |
| `pynq/s45lin.py` | `sw/pynq/s45lin.py` | 判定・試験 |
| `pynq/s45pn.py` | `sw/pynq/s45pn.py` | 性能の測り（M6） |
| `pynq/s45proto.py` | `sw/pynq/s45proto.py` | specd の実行に要る（specd が import する） |
| `pynq/s45resp.py` | `sw/pynq/s45resp.py` | 判定・試験 |
| `pynq/s45ring.py` | `sw/pynq/s45ring.py` | specd の実行に要る（specd が import する） |
| `pynq/s45snap.py` | `sw/pynq/s45snap.py` | 判定・試験 |
| `pynq/s45snapplot.py` | `sw/pynq/s45snapplot.py` | 性能の測り（M6） |
| `pynq/s45spur.py` | `sw/pynq/s45spur.py` | 性能の測り（M6） |
| `pynq/s45tastar.py` | `sw/pynq/s45tastar.py` | 性能の測り（M6） |
| `pynq/s45v2a.py` | `sw/pynq/s45v2a.py` | 判定・試験 |
| `pynq/s45v2c.py` | `sw/pynq/s45v2c.py` | 判定・試験 |
| `pynq/s45v2f.py` | `sw/pynq/s45v2f.py` | 判定・試験 |
| `pynq/sg.py` | `sw/pynq/sg.py` | specd の実行に要る（specd が import する） |
| `pynq/specctl.py` | `sw/pynq/specctl.py` | 受け側・制御 |
| `pynq/specd.py` | `sw/pynq/specd.py` | specd の実行に要る（specd が import する） |
| `pynq/specrecv.py` | `sw/pynq/specrecv.py` | 受け側・制御 |
| `pynq/spectrometer.py` | `sw/pynq/spectrometer.py` | specd の実行に要る（specd が import する） |
| `pynq/test_fake.sh` | `sw/pynq/test_fake.sh` | 判定・試験 |
| `pynq/test_regmap.py` | `sw/pynq/test_regmap.py` | 判定・試験 |
| `pynq/test_tpjump.py` | `sw/pynq/test_tpjump.py` | 判定・試験 |
| `pynq/timebase.py` | `sw/pynq/timebase.py` | specd の実行に要る（specd が import する） |
| `pynq/timetest.py` | `sw/pynq/timetest.py` | specd の実行に要る（specd が import する） |
| `pynq/tp_cal.json` | `sw/pynq/tp_cal.json` | 較正・bit の一覧のひな形 |
| `pynq/tpjump.py` | `sw/pynq/tpjump.py` | specd の実行に要る（specd が import する） |
| `pynq/window.py` | `sw/pynq/window.py` | specd の実行に要る（specd が import する） |
| `sim/check.py` | `hw/bits/sam45-fine/sim/check.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_ddc.py` | `hw/bits/sam45-fine/sim/check_ddc.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_pfb.py` | `hw/bits/sam45-fine/sim/check_pfb.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_pfbm.py` | `hw/bits/sam45-fine/sim/check_pfbm.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_ring.py` | `hw/bits/sam45-fine/sim/check_ring.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_top.py` | `hw/bits/sam45-fine/sim/check_top.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_tp.py` | `hw/bits/sam45-fine/sim/check_tp.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_win.py` | `hw/bits/sam45-fine/sim/check_win.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_win4.py` | `hw/bits/sam45-fine/sim/check_win4.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/check_wspec.py` | `hw/bits/sam45-fine/sim/check_wspec.py` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/lane_fft_model.v` | `hw/bits/sam45-fine/sim/lane_fft_model.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/rec_sink.v` | `hw/bits/sam45-fine/sim/rec_sink.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_ddc.v` | `hw/bits/sam45-fine/sim/tb_ddc.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_gearbox.v` | `hw/bits/sam45-fine/sim/tb_gearbox.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_hb2s.v` | `hw/bits/sam45-fine/sim/tb_hb2s.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_pfb.v` | `hw/bits/sam45-fine/sim/tb_pfb.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_pfbm.v` | `hw/bits/sam45-fine/sim/tb_pfbm.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_raw.v` | `hw/bits/sam45-fine/sim/tb_raw.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_regmap.v` | `hw/bits/sam45-fine/sim/tb_regmap.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_ring.v` | `hw/bits/sam45-fine/sim/tb_ring.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_ring_u.v` | `hw/bits/sam45-fine/sim/tb_ring_u.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_spec_core.v` | `hw/bits/sam45-fine/sim/tb_spec_core.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_t4adc.v` | `hw/bits/sam45-fine/sim/tb_t4adc.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_time.v` | `hw/bits/sam45-fine/sim/tb_time.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_top.v` | `hw/bits/sam45-fine/sim/tb_top.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_tp_core.v` | `hw/bits/sam45-fine/sim/tb_tp_core.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_tsys.v` | `hw/bits/sam45-fine/sim/tb_tsys.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_wdelay.v` | `hw/bits/sam45-fine/sim/tb_wdelay.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_wgrid.v` | `hw/bits/sam45-fine/sim/tb_wgrid.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_win.v` | `hw/bits/sam45-fine/sim/tb_win.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_win4.v` | `hw/bits/sam45-fine/sim/tb_win4.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_wspec.v` | `hw/bits/sam45-fine/sim/tb_wspec.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/tb_wstamp.v` | `hw/bits/sam45-fine/sim/tb_wstamp.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `sim/win_fft_model.v` | `hw/bits/sam45-fine/sim/win_fft_model.v` | 共通の tb を hw/sim/ に出すのは M1 の後の別 PR |
| `src/board/pps.xdc` | `hw/board/pps.xdc` |  |
| `src/board/ps_preset.tcl` | `hw/board/ps_preset.tcl` |  |
| `src/board/timing.xdc` | `hw/board/timing.xdc` |  |
| `src/common/adc_ev.v` | `hw/common/adc_ev.v` |  |
| `src/common/axis_sel4.v` | `hw/common/axis_sel4.v` |  |
| `src/common/cmul.v` | `hw/common/cmul.v` |  |
| `src/common/ddc_core.v` | `hw/common/ddc_core.v` |  |
| `src/common/dft16.v` | `hw/common/dft16.v` |  |
| `src/common/dft16f.v` | `hw/common/dft16f.v` |  |
| `src/common/dstamp.v` | `hw/common/dstamp.v` |  |
| `src/common/gb_adc.v` | `hw/common/gb_adc.v` |  |
| `src/common/gb_gate.v` | `hw/common/gb_gate.v` |  |
| `src/common/hb2.v` | `hw/common/hb2.v` |  |
| `src/common/hb2s.v` | `hw/common/hb2s.v` |  |
| `src/common/nco_rom.v` | `hw/common/nco_rom.v` |  |
| `src/common/pair2.v` | `hw/common/pair2.v` |  |
| `src/common/pfb_core.v` | `hw/common/pfb_core.v` |  |
| `src/common/raw_core.v` | `hw/common/raw_core.v` |  |
| `src/common/rec_arb.v` | `hw/common/rec_arb.v` |  |
| `src/common/rec_fr.v` | `hw/common/rec_fr.v` |  |
| `src/common/s45_core.v` | `hw/common/s45_core.v` |  |
| `src/common/s45_ring.v` | `hw/common/s45_ring.v` |  |
| `src/common/spec_core.v` | `hw/common/spec_core.v` | 全帯域の FFT（SAM45-Fine の bit では使わない、SAM45-Wide など） |
| `src/common/time_core.v` | `hw/common/time_core.v` |  |
| `src/common/tp_core.v` | `hw/common/tp_core.v` |  |
| `src/common/tw_rom.v` | `hw/common/tw_rom.v` | 全帯域の FFT（SAM45-Fine の bit では使わない、SAM45-Wide など） |
| `src/common/win_coef.vh` | `hw/common/win_coef.vh` |  |
| `src/common/win_core.v` | `hw/common/win_core.v` |  |
| `src/common/wspec_core.v` | `hw/common/wspec_core.v` |  |
| `src/sam45fine/fft_cfg.tcl` | `hw/bits/sam45-fine/src/fft_cfg.tcl` |  |
| `src/sam45fine/pfb4_rom.v` | `hw/bits/sam45-fine/src/pfb4_rom.v` |  |
| `test/acceptance/F-0.md` | `test/acceptance/sam45-fine/F-0.md` |  |
| `test/acceptance/F-1.md` | `test/acceptance/sam45-fine/F-1.md` |  |
| `test/acceptance/F-2.md` | `test/acceptance/sam45-fine/F-2.md` |  |
| `test/acceptance/ID-1.md` | `test/acceptance/sam45-fine/ID-1.md` |  |
| `test/acceptance/P-5.md` | `test/acceptance/sam45-fine/P-5.md` |  |
| `test/acceptance/P-8.md` | `test/acceptance/sam45-fine/P-8.md` |  |
| `test/acceptance/PS-1.md` | `test/acceptance/sam45-fine/PS-1.md` |  |
| `test/acceptance/PS-2.md` | `test/acceptance/sam45-fine/PS-2.md` |  |
| `test/acceptance/PS-3.md` | `test/acceptance/sam45-fine/PS-3.md` |  |
| `test/acceptance/README.md` | `test/acceptance/sam45-fine/README.md` |  |
| `test/acceptance/S.md` | `test/acceptance/sam45-fine/S.md` |  |
| `test/acceptance/T-4.md` | `test/acceptance/sam45-fine/T-4.md` |  |
| `test/acceptance/V2-a.md` | `test/acceptance/sam45-fine/V2-a.md` |  |
| `test/acceptance/V2-b.md` | `test/acceptance/sam45-fine/V2-b.md` |  |
| `test/acceptance/V2-c.md` | `test/acceptance/sam45-fine/V2-c.md` |  |
| `test/acceptance/V2-d.md` | `test/acceptance/sam45-fine/V2-d.md` |  |
| `test/acceptance/V2-e.md` | `test/acceptance/sam45-fine/V2-e.md` |  |
| `test/acceptance/V2-f.md` | `test/acceptance/sam45-fine/V2-f.md` |  |
| `test/acceptance/V2-g.md` | `test/acceptance/sam45-fine/V2-g.md` |  |
| `test/acceptance/W-0.md` | `test/acceptance/sam45-fine/W-0.md` |  |
| `test/acceptance/W-1.md` | `test/acceptance/sam45-fine/W-1.md` |  |
| `test/acceptance/W-G.md` | `test/acceptance/sam45-fine/W-G.md` |  |
| `tools/dump_ps_preset.tcl` | `hw/bits/sam45-fine/tools/dump_ps_preset.tcl` | Makefile が使う |
| `tools/floorplan.py` | `hw/bits/sam45-fine/tools/floorplan.py` | Makefile が使う |
| `tools/floorplan.tcl` | `hw/bits/sam45-fine/tools/floorplan.tcl` | Makefile が使う |
| `tools/gb_cdc.tcl` | `hw/bits/sam45-fine/tools/gb_cdc.tcl` | Makefile が使う |
| `tools/gb_slow.tcl` | `hw/bits/sam45-fine/tools/gb_slow.tcl` | Makefile が使う |
| `tools/gen_coef.py` | `hw/bits/sam45-fine/tools/gen_coef.py` | Makefile が使う |
| `tools/gen_tw_rom.py` | `hw/bits/sam45-fine/tools/gen_tw_rom.py` | Makefile が使う |
| `tools/ip_survey.tcl` | `hw/bits/sam45-fine/tools/ip_survey.tcl` | Makefile が使う |
| `tools/ooc_ddc.tcl` | `hw/bits/sam45-fine/tools/ooc_ddc.tcl` | Makefile が使う |
| `tools/postroute_physopt.tcl` | `hw/bits/sam45-fine/tools/postroute_physopt.tcl` | Makefile が使う |
| `tools/worst_paths.tcl` | `hw/bits/sam45-fine/tools/worst_paths.tcl` | Makefile が使う |

## 移さないもの（必要なら study-rfsoc の proj021 を指す）

| proj021 | 理由 |
|---|---|
| `README.md` | 経緯と結果。docs/performance の最初の 1 本の材料（M6） |
| `pynq/adcstat.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/bench_ps.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/fcheck.ipynb` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/fine.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/gbboot.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/lin_p25.lin.json` | 測定の記録 |
| `pynq/lin_p25.lin.jsonl` | 測定の記録 |
| `pynq/lin_p25.lin.png` | 測定の記録 |
| `pynq/lin_p25_p20.lin.json` | 測定の記録 |
| `pynq/lin_p25_p20.lin.jsonl` | 測定の記録 |
| `pynq/lin_p25_p20.lin.png` | 測定の記録 |
| `pynq/lin_p25b.lin.json` | 測定の記録 |
| `pynq/lin_p25b.lin.jsonl` | 測定の記録 |
| `pynq/lin_p25b.lin.png` | 測定の記録 |
| `pynq/lockcheck.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/ps2.json` | 測定の記録 |
| `pynq/r22d.json` | 測定の記録 |
| `pynq/r23a.json` | 測定の記録 |
| `pynq/r23a2.json` | 測定の記録 |
| `pynq/r23a3.json` | 測定の記録 |
| `pynq/r23ap.json` | 測定の記録 |
| `pynq/r23b.json` | 測定の記録 |
| `pynq/r23b2.json` | 測定の記録 |
| `pynq/r23c.json` | 測定の記録 |
| `pynq/r23cp.json` | 測定の記録 |
| `pynq/r23d.json` | 測定の記録 |
| `pynq/r24.json` | 測定の記録 |
| `pynq/r25.json` | 測定の記録 |
| `pynq/rb2.json` | 測定の記録 |
| `pynq/rb2p.json` | 測定の記録 |
| `pynq/rb3.json` | 測定の記録 |
| `pynq/rb4.json` | 測定の記録 |
| `pynq/rb5.json` | 測定の記録 |
| `pynq/rb6.json` | 測定の記録 |
| `pynq/rb7.json` | 測定の記録 |
| `pynq/rb8.json` | 測定の記録 |
| `pynq/resp_explain.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/resp_p23a.resp.band.png` | 測定の記録 |
| `pynq/resp_p23a.resp.chan.png` | 測定の記録 |
| `pynq/resp_p23a.resp.json` | 測定の記録 |
| `pynq/resp_p23a.resp.npz` | 測定の記録 |
| `pynq/resp_p25.resp.band.png` | 測定の記録 |
| `pynq/resp_p25.resp.chan.png` | 測定の記録 |
| `pynq/resp_p25.resp.json` | 測定の記録 |
| `pynq/resp_p25.resp.npz` | 測定の記録 |
| `pynq/s45fcheck.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/snap23a.snap.npz` | 測定の記録 |
| `pynq/snap25.snap.npz` | 測定の記録 |
| `pynq/v2b.json` | 測定の記録 |
| `pynq/v2bp.json` | 測定の記録 |
| `pynq/v2d.json` | 測定の記録 |
| `pynq/win16.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winallan.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winlin.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winnoise.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winresp.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winsweep.py` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winwidths.sh` | proj014〜019・手順 0・1b の試行の道具 |
| `pynq/winwrst.py` | proj014〜019・手順 0・1b の試行の道具 |
| `runs/g3.gbboot.json` | 測定の記録 |
| `runs/g4.gbboot.json` | 測定の記録 |
| `runs/resp_p21.resp.band.png` | 測定の記録 |
| `runs/resp_p21.resp.chan.png` | 測定の記録 |
| `runs/resp_p21.resp.json` | 測定の記録 |
| `src/.gitkeep` | 空のディレクトリの印 |
| `tools/allan.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/ipround_model.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tick_analyze.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_burst.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_mock.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_rfi.py` | 全帯域（proj013）の解析・使わなくなった道具 |
| `tools/tp_spec_analyze.py` | 全帯域（proj013）の解析・使わなくなった道具 |
