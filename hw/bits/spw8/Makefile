# SPDX-License-Identifier: BSD-3-Clause
# proj032 P-9 — 4 ADC・窓 8 本 / ADC・PL の DDR なしの .bit（b5）。Vivado は絶対パスで叩く（settings64.sh を .bashrc で source しない。d3/Makefile の注）
XILINX_VIVADO ?= /tools/Xilinx/Vivado/2024.1
VIVADO        := $(XILINX_VIVADO)/bin/vivado
BOARD_REPO ?= $(HOME)/src/RFSoC4x2-BSP/board_files
# 実機と同じ -1 だけを作る（PS は ../src/board/ps_preset.tcl を当てる）
PART ?= xczu48dr-ffvg1517-1-e
OUTDIR := build
JOBS ?= 8
# 実装の戦略（impl_1 の strategy）。空なら既定。例: make IMPL=Performance_Explore → build-PE/（proj031 と同じ）
IMPL ?=
ifneq ($(IMPL),)
  OUTDIR := $(OUTDIR)-$(shell echo $(IMPL) | tr -cd 'A-Z')
endif

export BOARD_REPO PART OUTDIR IMPL

.PHONY: all build post clean

# 成果物は build/proj032b5.bit・.hwh。成否は make の終了状態でなく build/vivado.log の「TIMING (確定)」「CRITICAL WARNING: n 件」「=== wrote」で読む
build:
	mkdir -p $(OUTDIR)
	VIVADO_LOG=$(OUTDIR)/vivado.log $(VIVADO) -mode batch -nojournal -log $(OUTDIR)/vivado.log -source build.tcl -tclargs $(JOBS)

all: build

clean:
	rm -rf build build-* .Xil *.jou *.log

# impl_1 の後で親の Vivado が落ちたとき、後段（build_post.tcl）だけを回す
post:
	VIVADO_LOG=$(OUTDIR)/vivado_post.log RESUME=1 $(VIVADO) -mode batch -nojournal -log $(OUTDIR)/vivado_post.log -source build_post.tcl

# ======================================================================== sim（YATSUGATAKE で足した、spw8/sim-targets）
# proj032 には sim の目標が無く、各 sim は README（P-1〜P-13）に書いた手で回した。その形を目標に書き起こした（docs/migration-spw8.md の「sim の組」）。
# 変種は試験台の既定に CFG・TB_S などだけを渡す。iverilog の $random は既定の種で決まるので、同じ版なら毎回同じ入力になる。
# 試験台は記録を今のディレクトリに書くので、vvp は出力のディレクトリ（build-sim/<変種>/）の中で回す。成否は各目標の最後の行「sim-…: 全部通過」で読む
PYTHON   ?= python3
IVERILOG ?= iverilog
VVP      ?= vvp
SIMDIR   := build-sim
SPW_Y    := -I src/spw -I ../../common -y src/spw -y ../../common
SIM_M    := sim/win_fft_model.v sim/axi_mem_model.v

.PHONY: sim-all model-plan model-pfb64 model-win sim-pfb64 sim-head sim-hbmc sim-ddcb sim-front sim-wsb sim-core sim-regs sim-f32cv sim-rmux4 sim-dly sim-rdmux

# ---- 模型（机の上）----
model-plan:
	@$(PYTHON) tools/test_spwplan.py | tail -1 | grep -q '結果: 全部通過' \
	  && echo "model-plan: 全部通過" || (echo "model-plan: NG"; exit 1)
model-pfb64:
	@$(PYTHON) ../../../model/pfb64_fixed.py | grep -q 'pfb64_coef.vh と一致' && echo "model-pfb64: 全部通過" || (echo "model-pfb64: NG"; exit 1)
model-win:
	@$(PYTHON) ../../../model/win64_model.py | tail -1 | grep -q '結果: 全部通過' && echo "model-win: 全部通過" || (echo "model-win: NG"; exit 1)

# ---- 粗い PFB の単体（P-5）: PSPLIT 0・1 × 雑音 ＋ CW・満杯の方形波（LOUD）。陽性対照: RTL（PFB64_POSCTL: フレームの番号を 1 ずらす）と照合（PFB64_POSCTL_MODEL）----
PFB64_V := n ps loud psloud posrtl posmodel
sim-pfb64:
	@for v in $(PFB64_V); do \
	  o=$(SIMDIR)/pfb64_$$v; mkdir -p $$o; d=""; ps=0; loud=0; pm=0; \
	  case $$v in ps) d="-DPSPLIT"; ps=1;; loud) loud=1;; psloud) d="-DPSPLIT"; ps=1; loud=1;; posrtl) d="-DPFB64_POSCTL";; posmodel) pm=1;; esac; \
	  ( (cd $$o && LOUD=$$loud $(PYTHON) ../../sim/check_pfb64.py gen x_in.hex > gen.log 2>&1) && \
	    $(IVERILOG) -g2012 $$d -DXIN=\"x_in.hex\" -DYOUT=\"y_out.txt\" $(SPW_Y) -o $$o/tb sim/tb_pfb64.v > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > tb.log 2>&1 && PSPLIT=$$ps LOUD=$$loud PFB64_POSCTL_MODEL=$$pm $(PYTHON) ../../sim/check_pfb64.py check x_in.hex y_out.txt > check.log 2>&1) ) & \
	done; wait; \
	for v in $(PFB64_V); do printf '%-16s %s\n' "pfb64_$$v" "$$(grep '結果:' $(SIMDIR)/pfb64_$$v/check.log || echo '結果の行が無い')"; done
	@(for v in n ps loud psloud; do grep -q '結果: 全部通過' $(SIMDIR)/pfb64_$$v/check.log || exit 1; done) \
	  && grep -q '結果: 失敗' $(SIMDIR)/pfb64_posrtl/check.log && grep -q '結果: 失敗' $(SIMDIR)/pfb64_posmodel/check.log \
	  && echo "sim-pfb64: 全部通過（陽性対照 2 本は落ちた）" || (echo "sim-pfb64: NG"; exit 1)

# ---- 窓の頭（E-2b）: 複素の CW の出口の周波数と振幅 ----
sim-head:
	@o=$(SIMDIR)/head; mkdir -p $$o; \
	$(IVERILOG) -g2012 -DZOUT=\"z.txt\" $(SPW_Y) -o $$o/tb sim/tb_head.v > $$o/iverilog.log 2>&1 && \
	(cd $$o && $(VVP) -n tb > tb.log 2>&1 && $(PYTHON) ../../sim/check_head.py z.txt > check.log 2>&1); \
	printf '%-16s %s\n' head "$$(grep '結果:' $$o/check.log || echo '結果の行が無い')"
	@grep -q '結果: 全部通過' $(SIMDIR)/head/check.log && echo "sim-head: 全部通過" || (echo "sim-head: NG"; exit 1)

# ---- 多 ch の半帯域（E-3）: light・final。陽性対照 HBMC_POSCTL（書き戻しの ch を 1 つずらす）----
HBMC_V := light final pos
sim-hbmc:
	@for v in $(HBMC_V); do \
	  o=$(SIMDIR)/hbmc_$$v; mkdir -p $$o; d=""; [ $$v = final ] && d="-DFINAL"; [ $$v = pos ] && d="-DHBMC_POSCTL"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_hbmc.v > $$o/iverilog.log 2>&1 && (cd $$o && $(VVP) -n tb > tb.log 2>&1) ) & \
	done; wait; \
	for v in $(HBMC_V); do printf '%-16s %s\n' "hbmc_$$v" "$$(grep '結果:' $(SIMDIR)/hbmc_$$v/tb.log || echo '結果の行が無い')"; done
	@grep -q '結果: 全部通過' $(SIMDIR)/hbmc_light/tb.log && grep -q '結果: 全部通過' $(SIMDIR)/hbmc_final/tb.log \
	  && grep -q '結果: 不合格' $(SIMDIR)/hbmc_pos/tb.log && echo "sim-hbmc: 全部通過（陽性対照は落ちた）" || (echo "sim-hbmc: NG"; exit 1)

# ---- 共有の後段 ddcb（E-3）: CFG 0〜3。陽性対照 DDCB_POSCTL（CFG 3 で final の lane が 2 クロックに 1 回しか受けない）----
DDCB_V := 0 1 2 3 pos
sim-ddcb:
	@for v in $(DDCB_V); do \
	  o=$(SIMDIR)/ddcb_$$v; mkdir -p $$o; d="-DCFG=$$v"; [ $$v = pos ] && d="-DCFG=3 -DDDCB_POSCTL"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_ddcb.v > $$o/iverilog.log 2>&1 && (cd $$o && $(VVP) -n tb > tb.log 2>&1) ) & \
	done; wait; \
	for v in $(DDCB_V); do printf '%-16s %s\n' "ddcb_$$v" "$$(grep '結果:' $(SIMDIR)/ddcb_$$v/tb.log || echo '結果の行が無い')"; done
	@(for v in 0 1 2 3; do grep -q '結果: 全部通過' $(SIMDIR)/ddcb_$$v/tb.log || exit 1; done) \
	  && grep -q '結果: 不合格' $(SIMDIR)/ddcb_pos/tb.log && echo "sim-ddcb: 全部通過（陽性対照は落ちた）" || (echo "sim-ddcb: NG"; exit 1)

# ---- 前段 spw_front（P-1・P-5）: ddcb の出口を整数の模型と、粗い PFB を鎖の中で模型と bit 単位で。陽性対照 FRONT_POSCTL（窓 3 の NCO の増分を 1 変える）----
sim-front:
	@for v in n pos; do \
	  o=$(SIMDIR)/front_$$v; mkdir -p $$o; d=""; [ $$v = pos ] && d="-DFRONT_POSCTL"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_front.v > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > tb.log 2>&1 && $(PYTHON) ../../sim/check_front.py . > check.log 2>&1; $(PYTHON) ../../sim/check_pfb_chain.py . > chain.log 2>&1) ) & \
	done; wait; \
	for v in n pos; do printf '%-16s %s / 鎖 %s\n' "front_$$v" "$$(grep '結果:' $(SIMDIR)/front_$$v/check.log || echo '結果の行が無い')" "$$(grep '結果:' $(SIMDIR)/front_$$v/chain.log || echo '結果の行が無い')"; done
	@grep -q '結果: 全部通過' $(SIMDIR)/front_n/check.log && grep -q '結果: 全部通過' $(SIMDIR)/front_n/chain.log \
	  && grep -q '結果: 不合格' $(SIMDIR)/front_pos/check.log && echo "sim-front: 全部通過（陽性対照は落ちた）" || (echo "sim-front: NG"; exit 1)

# ---- 後段 wsb（E-4・D-2・K-2）: 機関 ＋ 枠 ＋ 積分 → dsink → ring128。CFG・TB_S の 4 通り。陽性対照 ENG_POSCTL（機関の選びの NS の優先を外す）。
#      vvp の出力は sim.log（check_ring が ring の行を読む）----
WSB_V := c0 c0s6 c1s6 c2s1 pos
sim-wsb:
	@for v in $(WSB_V); do \
	  o=$(SIMDIR)/wsb_$$v; mkdir -p $$o; \
	  case $$v in c0) d="-DCFG=0";; c0s6) d="-DCFG=0 -DTB_S=6";; c1s6) d="-DCFG=1 -DTB_S=6";; c2s1) d="-DCFG=2 -DTB_S=1";; pos) d="-DCFG=0 -DENG_POSCTL";; esac; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_wsb.v $(SIM_M) > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > sim.log 2>&1 && $(PYTHON) ../../sim/check_wsb.py . > check.log 2>&1; $(PYTHON) ../../sim/check_ring.py . > ring.log 2>&1) ) & \
	done; wait; \
	for v in $(WSB_V); do printf '%-16s %s / リング %s\n' "wsb_$$v" "$$(grep '結果:' $(SIMDIR)/wsb_$$v/check.log || echo '結果の行が無い')" "$$(grep '結果:' $(SIMDIR)/wsb_$$v/ring.log || echo '結果の行が無い')"; done
	@(for v in c0 c0s6 c1s6 c2s1; do grep -q '結果: 全部通過' $(SIMDIR)/wsb_$$v/check.log && grep -q '結果: 全部通過' $(SIMDIR)/wsb_$$v/ring.log || exit 1; done) \
	  && grep -q '結果: 不合格' $(SIMDIR)/wsb_pos/check.log && echo "sim-wsb: 全部通過（陽性対照は落ちた）" || (echo "sim-wsb: NG"; exit 1)

# ---- コアの通し spw_core ＋ ring128 ＋ DDR の模型（P-2〜P-7）: そのまま・CORE_STOP。
#      陽性対照: CORE_POSCTL（窓 1 の NCO → check_front）・IPQ_POSCTL（FFT の tready の溜めを通さない → check_wsb）・TPX_POSCTL（TP の模型の和 → check_ring）----
CORE_V := n stop pos ipqpos tpxpos
core-run = for v in $(1); do \
	  o=$(SIMDIR)/core_$$v; mkdir -p $$o; \
	  case $$v in n) d="";; stop) d="-DCORE_STOP";; rdmux) d="-DRDMUX";; pos) d="-DCORE_POSCTL";; ipqpos) d="-DIPQ_POSCTL";; tpxpos) d="-DTPX_POSCTL";; muxpos) d="-DRDMUX -DDDRR_MUX_POSCTL";; esac; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_core.v $(SIM_M) > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > sim.log 2>&1 && $(PYTHON) ../../sim/check_front.py . > front.log 2>&1; $(PYTHON) ../../sim/check_pfb_chain.py . > chain.log 2>&1; \
	     $(PYTHON) ../../sim/check_wsb.py . > check.log 2>&1; $(PYTHON) ../../sim/check_ring.py . > ring.log 2>&1) ) & \
	done; wait; \
	for v in $(1); do o=$(SIMDIR)/core_$$v; printf '%-16s 読み %s / 前段 %s / 鎖 %s / wsb %s / リング %s\n' "core_$$v" \
	  "$$(grep -o '結果: [^（]*' $$o/sim.log | tail -1)" "$$(grep '結果:' $$o/front.log)" "$$(grep '結果:' $$o/chain.log)" "$$(grep '結果:' $$o/check.log)" "$$(grep '結果:' $$o/ring.log)"; done
sim-core:
	@$(call core-run,$(CORE_V))
	@(for v in n stop; do o=$(SIMDIR)/core_$$v; grep -q 'レジスタの読み: 結果: 全部通過' $$o/sim.log || exit 1; for f in front chain check ring; do grep -q '結果: 全部通過' $$o/$$f.log || exit 1; done; done) \
	  && grep -q '結果: 不合格' $(SIMDIR)/core_pos/front.log && grep -q '結果: 不合格' $(SIMDIR)/core_ipqpos/check.log \
	  && grep -q '結果: 不合格' $(SIMDIR)/core_tpxpos/ring.log \
	  && echo "sim-core: 全部通過（陽性対照 3 本は落ちた）" || (echo "sim-core: NG"; exit 1)

# ---- 読み手のまとめ ddrr_mux3（b3 rev 6、b5 の bit には入っていない）: tb_core の -DRDMUX と陽性対照 -DDDRR_MUX_POSCTL。
#      proj032 README の rev 6 の記録（山の帯域が足りず DDR の窓を通る記録が崩れる・前段の記録は既定と bit で同じ・陽性対照も同じ理由で落ちる）を
#      そのまま照らす: 前段の記録（front_y・wsb_in・wsb_t・tp_x）が core_n と同じ、wsb は 2 本とも不合格。sim-all には入れない（core_n が要る）----
sim-rdmux:
	@test -f $(SIMDIR)/core_n/front_y.log || (echo "sim-rdmux: 先に make sim-core"; exit 1)
	@$(call core-run,rdmux muxpos)
	@(for v in rdmux muxpos; do for f in front_y.log wsb_in.log wsb_t.log tp_x.log; do cmp -s $(SIMDIR)/core_n/$$f $(SIMDIR)/core_$$v/$$f || exit 1; done; \
	   grep -q '結果: 不合格' $(SIMDIR)/core_$$v/check.log || exit 1; done) \
	  && echo "sim-rdmux: 記録どおり（前段は既定と同じ・DDR の窓は崩れる。b5 の bit には入っていない）" || (echo "sim-rdmux: 記録と違う"; exit 1)

# ---- レジスタ spw_regs（R-1b・P-3・P-4）: 照らし 41 か所。陽性対照 REGS_POSCTL（lane の和を数えない）----
sim-regs:
	@for v in n pos; do \
	  o=$(SIMDIR)/regs_$$v; mkdir -p $$o; d=""; [ $$v = pos ] && d="-DREGS_POSCTL"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_spw_regs.v > $$o/iverilog.log 2>&1 && (cd $$o && $(VVP) -n tb > tb.log 2>&1) ) & \
	done; wait; \
	for v in n pos; do printf '%-16s %s\n' "regs_$$v" "$$(grep '^結果:' $(SIMDIR)/regs_$$v/tb.log || echo '結果の行が無い')"; done
	@grep -q '^結果: 全部通過' $(SIMDIR)/regs_n/tb.log && grep -q '^結果: 陽性対照は落ちた' $(SIMDIR)/regs_pos/tb.log \
	  && echo "sim-regs: 全部通過（陽性対照は落ちた）" || (echo "sim-regs: NG"; exit 1)

# ---- u64 → f32 の f32cv（K-2）: 端の値と乱数。陽性対照 POSCTL（入力 1 個を変える）----
sim-f32cv:
	@for v in n pos; do \
	  o=$(SIMDIR)/f32cv_$$v; mkdir -p $$o; d=""; [ $$v = pos ] && d="-DPOSCTL"; \
	  ( (cd $$o && $(PYTHON) ../../sim/check_f32cv.py gen f32cv_in.txt > gen.log 2>&1) && \
	    $(IVERILOG) -g2012 $$d -DIN_FILE=\"f32cv_in.txt\" -DOUT_FILE=\"f32cv_out.txt\" $(SPW_Y) -o $$o/tb sim/tb_f32cv.v > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > tb.log 2>&1 && $(PYTHON) ../../sim/check_f32cv.py check f32cv_in.txt f32cv_out.txt > check.log 2>&1) ) & \
	done; wait; \
	for v in n pos; do printf '%-16s %s\n' "f32cv_$$v" "$$(grep '結果:' $(SIMDIR)/f32cv_$$v/check.log || echo '結果の行が無い')"; done
	@grep -q '結果: 全部通過' $(SIMDIR)/f32cv_n/check.log && grep -q '結果: 不合格' $(SIMDIR)/f32cv_pos/check.log \
	  && echo "sim-f32cv: 全部通過（陽性対照は落ちた）" || (echo "sim-f32cv: NG"; exit 1)

# ---- コアの口をまとめる rmux4（P-9）。陽性対照 RMUX4_POSCTL（レコードの途中で口を放す）----
sim-rmux4:
	@for v in n pos; do \
	  o=$(SIMDIR)/rmux4_$$v; mkdir -p $$o; d=""; [ $$v = pos ] && d="-DRMUX4_POSCTL"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_rmux4.v > $$o/iverilog.log 2>&1 && (cd $$o && $(VVP) -n tb > tb.log 2>&1) ) & \
	done; wait; \
	for v in n pos; do printf '%-16s %s\n' "rmux4_$$v" "$$(grep '結果:' $(SIMDIR)/rmux4_$$v/tb.log || echo '結果の行が無い')"; done
	@grep -q '結果: 全部通過' $(SIMDIR)/rmux4_n/tb.log && grep -q '結果: 陽性対照は落ちた' $(SIMDIR)/rmux4_pos/tb.log \
	  && echo "sim-rmux4: 全部通過（陽性対照は落ちた）" || (echo "sim-rmux4: NG"; exit 1)

# ---- 窓の遅れ D(NS)（P-12）: そのまま・入口に 1 段・64 段。tools/dly_cmp.py が表の値と ＋1・＋64 の動きを照らす（各 ≒ 20 分）----
DLY_V := base p1 p64
sim-dly:
	@for v in $(DLY_V); do \
	  o=$(SIMDIR)/dly_$$v; mkdir -p $$o; d=""; [ $$v = p1 ] && d="-DDLY_POSCTL=1"; [ $$v = p64 ] && d="-DDLY_POSCTL=64"; \
	  ( $(IVERILOG) -g2012 $$d $(SPW_Y) -o $$o/tb sim/tb_spwdelay.v > $$o/iverilog.log 2>&1 && \
	    (cd $$o && $(VVP) -n tb > tb.log 2>&1 && $(PYTHON) ../../sim/check_spwdelay.py . > check.log 2>&1) ) & \
	done; wait; \
	$(PYTHON) tools/dly_cmp.py $(SIMDIR)/dly_base/check.log $(SIMDIR)/dly_p1/check.log $(SIMDIR)/dly_p64/check.log | tee $(SIMDIR)/dly_cmp.log
	@grep -q '結果: 全部通過' $(SIMDIR)/dly_cmp.log && echo "sim-dly: 全部通過（D(NS) が表の値・陽性対照で ＋1・＋64 動いた）" || (echo "sim-dly: NG"; exit 1)

# ---- 全部 ----
# 模型 3 本と sim 11 本。ログは build-sim-logs/ に目標ごとに 1 個、14 個。成否は各ログの最後の行「<目標>: 全部通過」で読む（make の成功を信用しない）
# 目標は SIM_J 本ずつ並べる（各目標の中でも変種を並べる）。sim-dly・sim-core・sim-wsb が重いので先に
SPW_MODELS := model-plan model-pfb64 model-win
SPW_SIMS   := sim-dly sim-core sim-wsb sim-front sim-pfb64 sim-ddcb sim-hbmc sim-head sim-regs sim-f32cv sim-rmux4
SIM_J      ?= 4
sim-all:
	@mkdir -p build-sim-logs; rm -f build-sim-logs/*.log
	@echo $(SPW_MODELS) $(SPW_SIMS) | tr ' ' '\n' | xargs -P $(SIM_J) -I{} sh -c '$(MAKE) --no-print-directory {} > build-sim-logs/{}.log 2>&1'
	@echo "---- sim-all ----"
	@for t in $(SPW_MODELS) $(SPW_SIMS); do printf '%-14s %s\n' "$$t" "$$(grep "^$$t: " build-sim-logs/$$t.log | tail -1 || true)"; done
	@n=0; for t in $(SPW_MODELS) $(SPW_SIMS); do grep -q "^$$t: 全部通過" build-sim-logs/$$t.log || n=$$((n + 1)); done; \
	  [ $$n = 0 ] && echo "sim-all: 全部通過（14 個）" || (echo "sim-all: NG $$n 個"; exit 1)
