# 移植: 2G-4（proj031・proj036）のファイルごとの行き先（M0）

[`migration-2g-4.md`](migration-2g-4.md) の「置き場所の対応」の付録。移植元で git が追跡しているファイル **247 個**（`proj031:` は proj031 の 172 個 = RTL・ビルド・sim・模型、`proj036:` は proj036 の 75 個 = PS）を、1 つずつ行き先に当てる。
**置く 103 個**・**2G-4 の側に写しを置く 3 個**・**既にある 35 個**（YATSUGATAKE に同じ中身があり、そのまま指す）・**移さない 106 個**。

比べの相手は YATSUGATAKE の main（c83cc0a）。「sw/pynq と」の欄は、PS の 1 個ずつを Wide の M5 で一本化した `sw/pynq/` の同じ名前と比べた中身（M5 の一本化の量の見当）。「既にある」35 個は `hw/common/`・`hw/board/` と**バイト単位で同じ**ことを確かめた。
この表は作業用の `classify.py`（リポジトリには入れない）で作り、行き先が重ならないこと、`sw/pynq-2g/` の 51 個の import が 51 個の中で閉じることを確かめた。移植元は今の study-rfsoc の main の木（タグ `proj031-m0`・`proj036-m0` を付けたら、その木と同じことを確かめ直す）

## 置くもの

| 移植元 | YATSUGATAKE | sw/pynq と | 備考 |
|---|---|---|---|
| `proj031:Makefile` | `hw/bits/2g-4/Makefile` | — | パスを直す（M1） |
| `proj031:build.tcl` | `hw/bits/2g-4/build.tcl` | — | パスを直す（M1） |
| `proj031:build_post.tcl` | `hw/bits/2g-4/build_post.tcl` | — |  |
| `proj031:model/cu_model.py` | `model/cu_model.py` | — | cu_model.py は pynq・tools のパスを直す（M1） |
| `proj031:model/g24_fixed.py` | `model/g24_fixed.py` | — |  |
| `proj031:model/g24_model.py` | `model/g24_model.py` | — |  |
| `proj031:model/g2_model.py` | `model/g2_model.py` | — |  |
| `proj031:model/s2_model.py` | `model/s2_model.py` | — |  |
| `proj031:sim/check_cu.py` | `hw/bits/2g-4/sim/check_cu.py` | — |  |
| `proj031:sim/check_g24.py` | `hw/bits/2g-4/sim/check_g24.py` | — |  |
| `proj031:sim/check_s2.py` | `hw/bits/2g-4/sim/check_s2.py` | — |  |
| `proj031:sim/cu_src.v` | `hw/bits/2g-4/sim/cu_src.v` | — |  |
| `proj031:sim/lane_fft_g24_model.v` | `hw/bits/2g-4/sim/lane_fft_g24_model.v` | — |  |
| `proj031:sim/rec_fr_ref.v` | `hw/bits/2g-4/sim/rec_fr_ref.v` | — |  |
| `proj031:sim/tb_g24_acc.v` | `hw/bits/2g-4/sim/tb_g24_acc.v` | — |  |
| `proj031:sim/tb_g24_chain.v` | `hw/bits/2g-4/sim/tb_g24_chain.v` | — |  |
| `proj031:sim/tb_g24_coef.v` | `hw/bits/2g-4/sim/tb_g24_coef.v` | — |  |
| `proj031:sim/tb_g24_core.v` | `hw/bits/2g-4/sim/tb_g24_core.v` | — |  |
| `proj031:sim/tb_g24_cu.v` | `hw/bits/2g-4/sim/tb_g24_cu.v` | — |  |
| `proj031:sim/tb_g24_ds.v` | `hw/bits/2g-4/sim/tb_g24_ds.v` | — |  |
| `proj031:sim/tb_g24_pfb.v` | `hw/bits/2g-4/sim/tb_g24_pfb.v` | — |  |
| `proj031:sim/tb_g24_s45.v` | `hw/bits/2g-4/sim/tb_g24_s45.v` | — |  |
| `proj031:sim/tb_g24_spec.v` | `hw/bits/2g-4/sim/tb_g24_spec.v` | — |  |
| `proj031:sim/tb_g24_tw.v` | `hw/bits/2g-4/sim/tb_g24_tw.v` | — |  |
| `proj031:sim/tb_g24_x4.v` | `hw/bits/2g-4/sim/tb_g24_x4.v` | — |  |
| `proj031:sim/tb_lane_g24.v` | `hw/bits/2g-4/sim/tb_lane_g24.v` | — |  |
| `proj031:sim/tb_recfr_eq.v` | `hw/bits/2g-4/sim/tb_recfr_eq.v` | — |  |
| `proj031:sim/tb_s2_all.v` | `hw/bits/2g-4/sim/tb_s2_all.v` | — |  |
| `proj031:sim/tb_s2_sep.v` | `hw/bits/2g-4/sim/tb_s2_sep.v` | — |  |
| `proj031:src/g24/crc32_d32.vh` | `hw/bits/2g-4/src/g24/crc32_d32.vh` | — |  |
| `proj031:src/g24/g24_acc.v` | `hw/bits/2g-4/src/g24/g24_acc.v` | — |  |
| `proj031:src/g24/g24_chain.v` | `hw/bits/2g-4/src/g24/g24_chain.v` | — |  |
| `proj031:src/g24/g24_coef.v` | `hw/bits/2g-4/src/g24/g24_coef.v` | — |  |
| `proj031:src/g24/g24_coef_hi.hex` | `hw/bits/2g-4/src/g24/g24_coef_hi.hex` | — |  |
| `proj031:src/g24/g24_coef_lo.hex` | `hw/bits/2g-4/src/g24/g24_coef_lo.hex` | — |  |
| `proj031:src/g24/g24_core.v` | `hw/bits/2g-4/src/g24/g24_core.v` | — |  |
| `proj031:src/g24/g24_cu.v` | `hw/bits/2g-4/src/g24/g24_cu.v` | — |  |
| `proj031:src/g24/g24_pfb.v` | `hw/bits/2g-4/src/g24/g24_pfb.v` | — |  |
| `proj031:src/g24/g24_pfb_core.v` | `hw/bits/2g-4/src/g24/g24_pfb_core.v` | — |  |
| `proj031:src/g24/g24_s45_core.v` | `hw/bits/2g-4/src/g24/g24_s45_core.v` | — |  |
| `proj031:src/g24/g24_spec.v` | `hw/bits/2g-4/src/g24/g24_spec.v` | — |  |
| `proj031:src/g24/g24_tw.v` | `hw/bits/2g-4/src/g24/g24_tw.v` | — |  |
| `proj031:src/g24/g24_tw_a.hex` | `hw/bits/2g-4/src/g24/g24_tw_a.hex` | — |  |
| `proj031:src/g24/g24_tw_b.hex` | `hw/bits/2g-4/src/g24/g24_tw_b.hex` | — |  |
| `proj031:src/s2_chain.v` | `hw/bits/2g-4/src/s2_chain.v` | — |  |
| `proj031:src/s2_q.v` | `hw/bits/2g-4/src/s2_q.v` | — |  |
| `proj031:src/s2_sep.v` | `hw/bits/2g-4/src/s2_sep.v` | — |  |
| `proj031:tools/cuctl.py` | `sw/pynq-2g/cuctl.py` | — | 係数 URAM の見張りの陽性対照（ボード、判定で使う） |
| `proj031:tools/gen_crc32.py` | `hw/bits/2g-4/tools/gen_crc32.py` | — | crc32_d32.vh の生成（make gen-crc）・cu_model が import |
| `proj031:tools/gen_g24_tables.py` | `hw/bits/2g-4/tools/gen_g24_tables.py` | — | 係数・ひねり係数の hex の生成（make gen） |
| `proj031:tools/ip_impl.tcl` | `hw/bits/2g-4/tools/ip_impl.tcl` | — | FFT IP の設定（build.tcl の fft_req と同じ） |
| `proj031:tools/ip_survey.tcl` | `hw/bits/2g-4/tools/ip_survey.tcl` | — | make survey の IP 単体の調査 |
| `proj031:tools/ooc_rtl.tcl` | `hw/bits/2g-4/tools/ooc_rtl.tcl` | — | 部品の OOC（ooc-sep・ooc-cu ほか） |
| `proj036:pynq/acqboot.py` | `sw/pynq-2g/acqboot.py` | 同じ |  |
| `proj036:pynq/bits.example.json` | `sw/pynq-2g/bits.example.json` | 違う |  |
| `proj036:pynq/build_fast.sh` | `sw/pynq-2g/build_fast.sh` | 無い | ボードで libs45fast.so を作る |
| `proj036:pynq/extref.py` | `sw/pynq-2g/extref.py` | 同じ |  |
| `proj036:pynq/g24cu.py` | `sw/pynq-2g/g24cu.py` | 無い | 係数 URAM の値（make build・sim の CU_WORDS もこれを読む） |
| `proj036:pynq/g24cw.py` | `sw/pynq-2g/g24cw.py` | 無い |  |
| `proj036:pynq/instr.py` | `sw/pynq-2g/instr.py` | 同じ |  |
| `proj036:pynq/plring.py` | `sw/pynq-2g/plring.py` | 違う |  |
| `proj036:pynq/rectap.py` | `sw/pynq-2g/rectap.py` | 同じ |  |
| `proj036:pynq/s45acq.py` | `sw/pynq-2g/s45acq.py` | 違う | proj031 の版に束ねの C |
| `proj036:pynq/s45allan.py` | `sw/pynq-2g/s45allan.py` | 違う |  |
| `proj036:pynq/s45cal.py` | `sw/pynq-2g/s45cal.py` | 違う |  |
| `proj036:pynq/s45client.py` | `sw/pynq-2g/s45client.py` | 違う |  |
| `proj036:pynq/s45core.py` | `sw/pynq-2g/s45core.py` | 違う |  |
| `proj036:pynq/s45fast.c` | `sw/pynq-2g/s45fast.c` | 無い | proj031 の版に s45_ring_acc |
| `proj036:pynq/s45fast.py` | `sw/pynq-2g/s45fast.py` | 無い | proj031 の版に s45_ring_acc の包み |
| `proj036:pynq/s45lin.py` | `sw/pynq-2g/s45lin.py` | 違う |  |
| `proj036:pynq/s45pn.py` | `sw/pynq-2g/s45pn.py` | 同じ |  |
| `proj036:pynq/s45proto.py` | `sw/pynq-2g/s45proto.py` | 同じ |  |
| `proj036:pynq/s45resp.py` | `sw/pynq-2g/s45resp.py` | 同じ |  |
| `proj036:pynq/s45ring.py` | `sw/pynq-2g/s45ring.py` | 違う |  |
| `proj036:pynq/s45snap.py` | `sw/pynq-2g/s45snap.py` | 同じ |  |
| `proj036:pynq/s45snapplot.py` | `sw/pynq-2g/s45snapplot.py` | 同じ |  |
| `proj036:pynq/s45spur.py` | `sw/pynq-2g/s45spur.py` | 同じ |  |
| `proj036:pynq/s45tastar.py` | `sw/pynq-2g/s45tastar.py` | 同じ |  |
| `proj036:pynq/s45v2a.py` | `sw/pynq-2g/s45v2a.py` | 同じ |  |
| `proj036:pynq/s45v2c.py` | `sw/pynq-2g/s45v2c.py` | 同じ |  |
| `proj036:pynq/s45v2f.py` | `sw/pynq-2g/s45v2f.py` | 同じ |  |
| `proj036:pynq/sg.py` | `sw/pynq-2g/sg.py` | 同じ |  |
| `proj036:pynq/specctl.py` | `sw/pynq-2g/specctl.py` | 同じ |  |
| `proj036:pynq/specd.py` | `sw/pynq-2g/specd.py` | 違う | proj031 の版に束ねの C（--fast-ring を n_sum ≧ 2 に） |
| `proj036:pynq/specrecv.py` | `sw/pynq-2g/specrecv.py` | 違う |  |
| `proj036:pynq/spectrometer.py` | `sw/pynq-2g/spectrometer.py` | 違う |  |
| `proj036:pynq/test_bund_fast.py` | `sw/pynq-2g/test_bund_fast.py` | 無い | proj036 の新しい試験 |
| `proj036:pynq/test_cal_b.py` | `sw/pynq-2g/test_cal_b.py` | 同じ |  |
| `proj036:pynq/test_fake.sh` | `sw/pynq-2g/test_fake.sh` | 違う |  |
| `proj036:pynq/test_nch.py` | `sw/pynq-2g/test_nch.py` | 無い |  |
| `proj036:pynq/test_regmap.py` | `sw/pynq-2g/test_regmap.py` | 違う |  |
| `proj036:pynq/test_ring_fast.py` | `sw/pynq-2g/test_ring_fast.py` | 無い |  |
| `proj036:pynq/test_s45fast.py` | `sw/pynq-2g/test_s45fast.py` | 無い |  |
| `proj036:pynq/test_tpjump.py` | `sw/pynq-2g/test_tpjump.py` | 同じ |  |
| `proj036:pynq/timebase.py` | `sw/pynq-2g/timebase.py` | 違う |  |
| `proj036:pynq/timetest.py` | `sw/pynq-2g/timetest.py` | 違う |  |
| `proj036:pynq/tp_cal.json` | `sw/pynq-2g/tp_cal.json` | 違う |  |
| `proj036:pynq/tpjump.py` | `sw/pynq-2g/tpjump.py` | 同じ |  |
| `proj036:pynq/widef2.py` | `sw/pynq-2g/widef2.py` | 違う | F-2（adc_to_core）の道具 |
| `proj036:pynq/window.py` | `sw/pynq-2g/window.py` | 同じ | specd・widef2 が import する（中身は Fine の窓の道具） |
| `proj036:tools/amslog.py` | `sw/pynq-2g/amslog.py` | — | VCCINT・温度の記録（ボード） |
| `proj036:tools/level.py` | `sw/pynq-2g/level.py` | — | tint をまたぐレベルの比べ（proj036 R-2） |
| `proj036:tools/loopsum.py` | `sw/pynq-2g/loopsum.py` | — | specd の 1 周の内訳（--loop-log-ms） |

## 2G-4 の側に写しを置くもの（hw/common と違う。一本化は M1 の後）

| 移植元 | YATSUGATAKE | hw/common と | 備考 |
|---|---|---|---|
| `proj031:src/common/core_cmn.v` | `hw/bits/2g-4/src/core_cmn.v` | 違う | proj024 2d で tp_core の f0_ext を繋いだ（2 行） |
| `proj031:src/common/rec_fr.v` | `hw/bits/2g-4/src/rec_fr.v` | 違う | proj024 2d で NCH を引数に（2G-4 は NCH 32768）。NCH 4096（既定）では今と同じ幅・同じ値 |
| `proj031:src/common/tp_core.v` | `hw/bits/2g-4/src/tp_core.v` | 違う | proj024 2d で F0_EXT を足した（2G-4 は F0_EXT 1）。F0_EXT 0（既定）では今と同じ |

## 既にあるもの（そのまま指す）

| 移植元 | YATSUGATAKE | 中身 |
|---|---|---|
| `proj031:src/board/pps.xdc` | `hw/board/pps.xdc` | 同じ |
| `proj031:src/board/ps_preset.tcl` | `hw/board/ps_preset.tcl` | 同じ |
| `proj031:src/board/timing.xdc` | `hw/board/timing.xdc` | 同じ |
| `proj031:src/common/adc_ev.v` | `hw/common/adc_ev.v` | 同じ |
| `proj031:src/common/axis_sel4.v` | `hw/common/axis_sel4.v` | 同じ |
| `proj031:src/common/cmul.v` | `hw/common/cmul.v` | 同じ |
| `proj031:src/common/ddc_core.v` | `hw/common/ddc_core.v` | 同じ |
| `proj031:src/common/dft16.v` | `hw/common/dft16.v` | 同じ |
| `proj031:src/common/dft16f.v` | `hw/common/dft16f.v` | 同じ |
| `proj031:src/common/dstamp.v` | `hw/common/dstamp.v` | 同じ |
| `proj031:src/common/gb_adc.v` | `hw/common/gb_adc.v` | 同じ |
| `proj031:src/common/gb_gate.v` | `hw/common/gb_gate.v` | 同じ |
| `proj031:src/common/hb2.v` | `hw/common/hb2.v` | 同じ |
| `proj031:src/common/hb2s.v` | `hw/common/hb2s.v` | 同じ |
| `proj031:src/common/nco_rom.v` | `hw/common/nco_rom.v` | 同じ |
| `proj031:src/common/pair2.v` | `hw/common/pair2.v` | 同じ |
| `proj031:src/common/pfb_core.v` | `hw/common/pfb_core.v` | 同じ |
| `proj031:src/common/raw_core.v` | `hw/common/raw_core.v` | 同じ |
| `proj031:src/common/rec_arb.v` | `hw/common/rec_arb.v` | 同じ |
| `proj031:src/common/s45_core.v` | `hw/common/s45_core.v` | 同じ |
| `proj031:src/common/s45_ring.v` | `hw/common/s45_ring.v` | 同じ |
| `proj031:src/common/spec_core.v` | `hw/common/spec_core.v` | 同じ |
| `proj031:src/common/time_core.v` | `hw/common/time_core.v` | 同じ |
| `proj031:src/common/tw_rom.v` | `hw/common/tw_rom.v` | 同じ |
| `proj031:src/common/wide_acc.v` | `hw/common/wide_acc.v` | 同じ |
| `proj031:src/common/wide_chain.v` | `hw/common/wide_chain.v` | 同じ |
| `proj031:src/common/wide_coef_rom.v` | `hw/common/wide_coef_rom.v` | 同じ |
| `proj031:src/common/wide_core.v` | `hw/common/wide_core.v` | 同じ |
| `proj031:src/common/wide_pfb.v` | `hw/common/wide_pfb.v` | 同じ |
| `proj031:src/common/wide_s45_core.v` | `hw/common/wide_s45_core.v` | 同じ |
| `proj031:src/common/wide_spec.v` | `hw/common/wide_spec.v` | 同じ |
| `proj031:src/common/wide_tw_rom.v` | `hw/common/wide_tw_rom.v` | 同じ |
| `proj031:src/common/win_coef.vh` | `hw/common/win_coef.vh` | 同じ |
| `proj031:src/common/win_core.v` | `hw/common/win_core.v` | 同じ |
| `proj031:src/common/wspec_core.v` | `hw/common/wspec_core.v` | 同じ |

## 移さないもの（必要なら study-rfsoc の proj031・proj036 を指す）

| 移植元 | 理由 |
|---|---|
| `proj031:.gitignore` | YATSUGATAKE の .gitignore が覆う（build-*/・*.bit・*.hwh） |
| `proj031:README.md` | 経緯と結果。2G-4 の性能評価（M6）の材料として指す |
| `proj031:pynq/acqboot.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/adcstat.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/bench_g21.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/bench_ps.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/bits.example.json` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/build_fast.sh` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/extref.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/f2pair.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/fcheck.ipynb` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/fine.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/g21cw.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/g22cw.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/g24cu.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/g24cw.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/gbboot.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/instr.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/lockcheck.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/plring.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/rectap.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/resp_explain.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45acq.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45allan.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45cal.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45client.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45core.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45fast.c` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45fast.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45fcheck.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45lin.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45pn.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45proto.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45resp.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45ring.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45snap.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45snapplot.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45spur.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45tastar.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45v2a.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45v2c.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/s45v2f.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/sg.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/specctl.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/specd.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/specrecv.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/spectrometer.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_cal_b.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_fake.sh` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_nch.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_regmap.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_ring_fast.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_s45fast.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/test_tpjump.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/timebase.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/timetest.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/tp_cal.json` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/tpjump.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/wide.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/wide_v2.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/widef2.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/wideresp.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/win16.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winallan.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/window.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winlin.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winnoise.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winresp.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winsweep.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winwidths.sh` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:pynq/winwrst.py` | proj036 の pynq/ に同じものか新しい版がある（PS は proj036 から） |
| `proj031:ref/dft16.v` | proj030 の OOC の比べの旧版（試行の目標 ooc-ref） |
| `proj031:ref/g24_chain.v` | proj030 の OOC の比べの旧版（試行の目標 ooc-ref） |
| `proj031:runs/model.txt` | 模型の出力（make model・model-cu が作り直す。make build は model-cu を回して runs/model_cu.txt の COEF_CRC を読む） |
| `proj031:runs/model_cu.txt` | 模型の出力（make model・model-cu が作り直す。make build は model-cu を回して runs/model_cu.txt の COEF_CRC を読む） |
| `proj031:tools/amslog.py` | proj036 の tools/ の同じ中身を置く |
| `proj031:tools/coef_ooc.tcl` | proj025 の g22_coef との比べ（試行の目標。Makefile の coef-ooc は study-rfsoc の git を読む） |
| `proj031:tools/loopsum.py` | proj036 の tools/ の同じ中身を置く |
| `proj031:tools/run4c30b.sh` | proj027 4c-b の試行の手順（ボードのパスが書いてある） |
| `proj031:tools/shapecmp.py` | proj030 R-4 の試行の道具 |
| `proj031:tools/wide_hier.tcl` | proj023 のチェックポイントを読む試行の目標（Makefile の wide-hier） |
| `proj036:.gitignore` | YATSUGATAKE の .gitignore が覆う |
| `proj036:README.md` | 経緯と結果（束ねの C の P-1・R-1〜R-3） |
| `proj036:pynq/adcstat.py` | proj019 の試行の道具 |
| `proj036:pynq/bench_g21.py` | 2G-1 の試行の道具 |
| `proj036:pynq/bench_ps.py` | proj021 手順 0 の試行の道具 |
| `proj036:pynq/f2pair.py` | proj027 4d-y の試行の道具（F-2 は widef2.py） |
| `proj036:pynq/fcheck.ipynb` | proj018 の試行の帳面 |
| `proj036:pynq/fine.py` | SAM45-Fine の道具（sw/pynq にある） |
| `proj036:pynq/g21cw.py` | 2G-1-Fast の道具（2G-1-Fast の移植で） |
| `proj036:pynq/g22cw.py` | 2G-2 の道具（2G-2 の移植で） |
| `proj036:pynq/gbboot.py` | proj021 手順 1b の判定の道具（2G-4 の手順は使わない） |
| `proj036:pynq/lockcheck.py` | proj019 の試行の道具 |
| `proj036:pynq/resp_explain.py` | proj014 の試行の道具 |
| `proj036:pynq/s45fcheck.py` | proj018 の試行の道具 |
| `proj036:pynq/wide.py` | SAM45-Wide の道具（sw/pynq にある） |
| `proj036:pynq/wide_v2.py` | SAM45-Wide の道具（sw/pynq にある） |
| `proj036:pynq/wideresp.py` | SAM45-Wide の道具（sw/pynq にある） |
| `proj036:pynq/win16.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winallan.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winlin.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winnoise.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winresp.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winsweep.py` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winwidths.sh` | 窓（Fine）の試行の道具 |
| `proj036:pynq/winwrst.py` | 窓（Fine）の試行の道具 |

