# SPDX-License-Identifier: BSD-3-Clause
# SAM45-Wide（YATSUGATAKE hw/bits/sam45-wide）。study-rfsoc の proj023 の Makefile から、proj021 までに引き継いだ SAM45-Fine の目標を外したもの。
# `make sim-all` = Wide の sim（模型の自己検査 ＋ sim-wpfb・wch・wsp・wco・ws45・wds）。成否は各ログの「結果: 全部通過」で読む
# Vivado のインストール先をここで持つ。
# settings64.sh を .bashrc で source しないこと（Xilinx 同梱の古い共有ライブラリが
# LD_LIBRARY_PATH の先頭に入り、git / ssh / python が壊れる）。
# bin/vivado は起動スクリプト自身が環境を組み立てるので、絶対パスで叩けば動く。
XILINX_VIVADO ?= /tools/Xilinx/Vivado/2024.1
VIVADO        := $(XILINX_VIVADO)/bin/vivado

# RealDigitalOrg/RFSoC4x2-BSP を clone した先の board_files ディレクトリ。
# Vivado のインストールツリーの中には置かない（VERSIONS.md 参照）。
BOARD_REPO ?= $(HOME)/src/RFSoC4x2-BSP/board_files

# part。proj015: **既定を -1 に**（実機の .bit を -1 で配置配線する。PS には ../../board/ps_preset.tcl を当てる。build.tcl の冒頭）。
# -2（board_part ＋ プリセット、proj014 までの build/ の作り）は PART=xczu48dr-ffvg1517-2-e → build-2-e/
PART_DEFAULT := xczu48dr-ffvg1517-1-e
PART         ?= $(PART_DEFAULT)

# FFT IP の変種（src/fft_cfg.tcl）。proj011 はこれを振って測る。
#   res  = realtime + 乗算器 use_mults_resources  + バタフライ use_luts            （本命・既定）
#   perf = realtime + 乗算器 use_mults_performance + バタフライ use_xtremedsp_slices（proj010 と乗算器が同じ。realtime の効きだけを見る）
FFT_OPT ?= res

# rev6: gb_gate のしきい値のハードのリセットでの既定値（spec_core の GB_K_RST）。0 = 素通し（rev5 までと同じ起動）。
# proj012 rev3: 既定値を 2 にした。rev2 のビット列の GRST で、K = 0 は 55 / 150 回途切れ、K = 1・2・4 は 450 回とも 0（README の rev3）。
# 既定以外は別ディレクトリ（build-k0/ など）に出す
GB_K_DEFAULT := 2
GB_K ?= $(GB_K_DEFAULT)

# 既定以外の part・変種は別ディレクトリに出し、検証済みの成果物を上書きしない。
#   build/            -1・res（proj015 から）   build-perf/      -1・perf
#   build-2-e/        -2・res                   build-2-e-perf/  -2・perf
ifeq ($(PART),$(PART_DEFAULT))
  OUTDIR := build
else
  OUTDIR := build-$(patsubst xczu48dr-ffvg1517-%,%,$(PART))
endif
ifneq ($(FFT_OPT),res)
  ifeq ($(OUTDIR),build)
    OUTDIR := build-$(FFT_OPT)
  else
    OUTDIR := $(OUTDIR)-$(FFT_OPT)
  endif
endif
ifneq ($(GB_K),$(GB_K_DEFAULT))
  OUTDIR := $(OUTDIR)-k$(GB_K)
endif
# rev6 の検証ビルド: GB_SLOW=b で gb_fifo の gray の bit b の同期段を GB_SLOW_SITE に固定して、わざと遅らせる（tools/gb_slow.tcl）。build-slow1/ など
GB_SLOW    ?=
GB_SLOW_SITE ?= SLICE_X46Y109
ifneq ($(GB_SLOW),)
  OUTDIR := $(OUTDIR)-slow$(GB_SLOW)
endif

# proj015 rev2: 実装の戦略（impl_1 の strategy）。空なら Vivado の既定。例: make IMPL=Performance_Explore → build-pe/ など
# **`-1` が閉じないときの次の手**。戦略を変えても RTL は同じなので ID は変わらない（BUILD_TAG も同じ）。PS は build/ の .bit を使う
IMPL ?=
ifneq ($(IMPL),)
  OUTDIR := $(OUTDIR)-$(shell echo $(IMPL) | tr -cd 'A-Z')
endif

# 同時に走らせる run の数（launch_runs -jobs）。効くのは IP の OOC 合成だけ。
# proj010 から lane_fft（FFT IP）の OOC 合成が 1 本増えている（proj011 も同じ）。ビルドサーバの nproc = 32 に合わせてある。
# コア数やメモリの少ない機械では `make JOBS=8` に下げること。
JOBS ?= 30

export BOARD_REPO PART OUTDIR FFT_OPT GB_K GB_SLOW GB_SLOW_SITE IMPL

# ---- シミュレーション（Vivado もライセンスも要らない。RTL を触ったらまずこれ。下の sim-all）----
IVERILOG  ?= iverilog
VVP       ?= vvp
PYTHON    ?= python3

.PHONY: all sim-all gb-cdc worst-paths survey prog id timing-check ps-preset clean

all: $(OUTDIR)
	$(VIVADO) -mode batch -nojournal -log $(OUTDIR)/vivado.log -source build.tcl -tclargs $(JOBS)

# ---- 配置配線後の dcp で gb_fifo の gray ポインタの乗り換えをビットごとに測る（rev6。ビルド不要、数分）----
# DCP を指定しなければ build/ の dcp。結果は dcp と同じ場所の gb_cdc.txt
# proj021: proj016.runs のままだった。**proj の名前は build.tcl の `set proj` から読む**（唯一の正）。
#   1b の直後に `*.runs` で拾う形にしたら、同じ build/ に残っていた 1a の proj020.runs を拾い、古い dcp を読んだ（2026-10-08）。
#   名前で指定し、その run の dcp がちょうど 1 個であることを確かめる
PROJ := $(shell sed -n 's/^set proj  *\([A-Za-z0-9_]*\).*/\1/p' build.tcl)
DCP ?= $(wildcard $(OUTDIR)/vivado/$(PROJ).runs/impl_1/*_routed.dcp)
DCP_CHECK = @test -n "$(PROJ)" || { echo "build.tcl から proj の名前を読めない"; exit 1; }; \
	test $(words $(DCP)) -eq 1 || { echo "dcp が 1 個でない（$(words $(DCP)) 個: $(DCP)）。make ... DCP=... で指定する"; exit 1; }; \
	echo "DCP: $(DCP)"
gb-cdc:
	$(DCP_CHECK)
	$(VIVADO) -mode batch -nojournal -nolog -source tools/gb_cdc.tcl -tclargs $(DCP) $(dir $(DCP))gb_cdc.txt

# ---- 配置配線後の dcp で setup / hold の最悪経路の中身を読む（rev3。ビルド不要、数分）----
# DCP は gb-cdc と同じ既定（$(OUTDIR) の dcp）。proj015 から既定の build/ が -1（-2 は PART=xczu48dr-ffvg1517-2-e）。
# 結果は dcp の run と同じ階層の $(OUTDIR)/worst_paths/。WP_N = 上位の本数、WP_THR = 束ねるしきい値（ns）
WP_N   ?= 200
WP_THR ?= 0.30
worst-paths:
	$(DCP_CHECK)
	$(VIVADO) -mode batch -nojournal -nolog -source tools/worst_paths.tcl -tclargs $(DCP) $(OUTDIR)/worst_paths $(WP_N) $(WP_THR)

# ---- proj021 2-2b: 配線後の物理最適化だけを掛け直す（負けが数十 ps・数本のとき。数十分）----
# DCP は worst-paths と同じ既定（$(OUTDIR) の dcp）。結果は $(OUTDIR)-po/（proj021.bit・元の proj021.hwh のコピー・timing.rpt）
physopt:
	$(DCP_CHECK)
	$(VIVADO) -mode batch -nojournal -log $(OUTDIR)-po.log -source tools/postroute_physopt.tcl -tclargs $(DCP) $(OUTDIR)-po
	cp $(OUTDIR)/proj023.hwh $(OUTDIR)-po/proj023.hwh

# ---- 配置配線後の dcp からフロアマップ（proj021、2026-10-09。ビルド不要、数分）----
# DCP は worst-paths と同じ既定。tools/floorplan.tcl が位置を CSV に、tools/floorplan.py が図に。結果は FP_OUT（既定 $(OUTDIR)/floorplan/）
#   floorplan.png（ブロックの種類で色分け・setup の上位 FP_PATHS 本の経路）/ floorplan_wo_arrow.png（矢印なし）/ floorplan_detail.png（深さ FP_DEPTH の階層ごと）/ blocks.txt
#   2 つ並べて比べる: python3 tools/floorplan.py build/floorplan build-PE/floorplan --title 既定 --title PE（→ build/floorplan/compare.png、縦に並べる）
FP_OUT   ?= $(OUTDIR)/floorplan
FP_DEPTH ?= 5
FP_PATHS ?= 20
.PHONY: floorplan
floorplan:
	$(DCP_CHECK)
	$(VIVADO) -mode batch -nojournal -nolog -source tools/floorplan.tcl -tclargs $(DCP) $(FP_OUT) $(FP_DEPTH) 50
	$(PYTHON) tools/floorplan.py $(FP_OUT) --paths $(FP_PATHS)

prog:
	$(VIVADO) -mode batch -nojournal -nolog -source program.tcl

# JTAG チェーンのデバイスを表示するだけ（合成ライセンス不要）
id:
	$(VIVADO) -mode batch -nojournal -nolog -source program.tcl -tclargs id

# 速度グレード -1 で通るかを確かめる。成果物は build-1-e/（FFT_OPT=perf なら build-1-e-perf/）に出るので build/ は無傷。
# `make timing-check FFT_OPT=perf` のように変種を引き継ぐ（コマンドラインの変数は再帰 make に渡る）。
# proj015: 既定が -1 になったので `make` と同じ（build/）。互換のために残す
timing-check:
	$(MAKE)

# ボードプリセットが PS に当てる設定を ../../board/ps_preset.tcl に書き出す（proj015。BOARD_REPO が要る。数分）。
# 書き直したら git diff で中身を見てからコミットする
ps-preset:
	mkdir -p build-ps-preset
	$(VIVADO) -mode batch -nojournal -log build-ps-preset/vivado.log -source tools/dump_ps_preset.tcl

$(OUTDIR):
	mkdir -p $(OUTDIR)

clean:
	rm -rf build build-* .Xil *.jou *.log

# FFT IP 単体の資源（ライセンスが要る。並列で 10〜20 分の見込み）。結果は build-survey/survey.txt
survey:
	mkdir -p build-survey
	$(VIVADO) -mode batch -nojournal -log build-survey/vivado.log -source tools/ip_survey.tcl -tclargs $(JOBS)

# SAM45-Wide の sim を全部（模型の自己検査 ＋ 6 組 27 本、2 コアで 20 分ほど）。組の中は変種を並べて走らせる。
# **成否は make の終了状態ではなく各ログの「結果: 全部通過」で判定する**。ログは build-sim-logs/（28 個）。
# `make sim-all &` で `make`（ビルド）と並べて走らせてよい（出力先が別）
WIDE_SIMS := sim-wpfb sim-wch sim-wsp sim-wco sim-ws45 sim-wds
sim-all:
	@mkdir -p build-sim-logs
	@rm -f build-sim-logs/*.log
	-$(MAKE) --no-print-directory model-wide > build-sim-logs/model-wide.log 2>&1
	@for t in $(WIDE_SIMS); do $(MAKE) --no-print-directory $$t || true; done
	@echo "---- sim-all ----"
	@for f in build-sim-logs/*.log; do r=$$(grep '結果:' $$f | tail -1); printf '%-36s %s\n' "$$f" "$${r:-結果の行が無い（途中で落ちた）}"; done
	@n=$$(ls build-sim-logs/*.log | wc -l); fail=$$(grep -L '結果: 全部通過' build-sim-logs/*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; \
	  elif [ $$n -ne 28 ]; then echo "FAIL: ログが $$n 個（28 個のはず）"; exit 1; else echo "sim-all: 全部通過（28 個）"; fi


# ---- proj023 手順 2a: SAM45-Wide の sim の模型の自己検査（RTL なし。1 秒かからない）----
# 模型どうしの突き合わせ（wide_model.fixed_chain と bit 単位・浮動小数点と振幅）と陽性対照。成否は「結果: 全部通過」で読む
.PHONY: model-wide
model-wide:
	$(PYTHON) sim/check_wide.py selftest

# ---- proj023 手順 2b: wide_pfb ＋ wide_coef_rom の単体の sim（判定 A1。iverilog で 1 本数秒）----
# 3 本を並べる: 本番（A1 が通るべき）/ -p: ROM の番地を 1 ずらす（coef_mis が立ち A1 が落ちるべき）/
# -nm: 起動の直後のマスクを外す（最初の 3 フレームが履歴のごみを拾い A1 が落ちるべき）。
# **成否は make の終了状態ではなく、各ログの「結果: 全部通過」で読む**（陽性対照は「落ちるべきところで落ちた」で通過）
WPFB_RTL := ../../common/wide_coef_rom.v ../../common/wide_pfb.v sim/tb_wide_pfb.v
WPFB_COEF := src/wide_coef.hex
.PHONY: sim-wpfb wide-coef
sim-wpfb:
	@mkdir -p build-sim-logs
	@for v in "wpfb::" "wpfb-p:-DPOSCTL:posctl" "wpfb-nm:-DPFB_NOMASK:posctl"; do \
	  nm=$${v%%:*}; r=$${v#*:}; def=$${r%%:*}; pc=$${r#*:}; d=build-sim-$$nm; \
	  ( mkdir -p $$d && $(PYTHON) sim/check_wide.py gen $$d 6 && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DCOEF=\"$(WPFB_COEF)\" -o $$d/tb $(WPFB_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_wide.py pfb $$d $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-wpfb*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-wpfb*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-wpfb: 全部通過"; fi

# 係数 ROM の中身を作り直す（../../../model/wide_model.py の原型を変えたときだけ。生成物もコミットする）
wide-coef:
	$(PYTHON) tools/gen_wide_coef.py > $(WPFB_COEF)

# ---- proj023 手順 2c-1: wide_chain ＋ wide_tw_rom の単体の sim（判定 A2 の後半: ひねり係数〜束ね。iverilog で 1 本 20 秒ほど）----
# IP の出口を模型で作って与え（lanes_in.txt）、束ねの出口を模型と bit 単位で比べる。変種は 名前:LB:SHIFT:定義:posctl
#   wch-b1・b2・b4: 束ね B 1・2・4（SHIFT 7、飽和なし）/ wch-sat: B 4・SHIFT 4（強い線が飽和、束ごとの飽和の数を比べる）/
#   wch-p: ROM の番地を 1 ずらす（tw_mis が立ち A2 が落ちるべき）/ wch-skew: 束ねの区切りを 1 ずらす（B 4。A2 が落ちるべき）
# **成否は各ログの「結果: 全部通過」で読む**
WCH_RTL := ../../common/cmul.v ../../common/dft16.v ../../common/wide_tw_rom.v ../../common/wide_chain.v sim/tb_wide_chain.v
WCH_TW  := src/wide_tw.hex
WCH_VARIANTS ?= wch-b1:0:7:: wch-b2:1:7:: wch-b4:2:7:: wch-sat:2:4:: wch-p:2:7:-DPOSCTL:posctl wch-skew:2:7:-DBIN_SKEW:posctl
.PHONY: sim-wch wide-tw
sim-wch:
	@mkdir -p build-sim-logs
	@for v in $(WCH_VARIANTS); do \
	  nm=$$(echo "$$v" | cut -d: -f1); lb=$$(echo "$$v" | cut -d: -f2); sh=$$(echo "$$v" | cut -d: -f3); \
	  def=$$(echo "$$v" | cut -d: -f4); pc=$$(echo "$$v" | cut -d: -f5); d=build-sim-$$nm; \
	  ( mkdir -p $$d && $(PYTHON) sim/check_wide.py genchain $$d 4 && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DTWF=\"$(WCH_TW)\" -DLB=$$lb -DSHIFT=$$sh -o $$d/tb $(WCH_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_wide.py chain $$d $$lb $$sh $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-wch*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-wch*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-wch: 全部通過"; fi

# ひねり係数 ROM の中身を作り直す（生成物もコミットする）
wide-tw:
	$(PYTHON) tools/gen_wide_tw.py > $(WCH_TW)

# ---- proj023 手順 2c-2: wide_spec（PFB → IP の行動模型 → 鎖 → 束ね → 切り出しの積分器 → 帳簿）の sim（判定 A1'・A2・B・C）----
# iverilog で 1 本 4〜5 分（IP の行動模型の倍精度 FFT と鎖が重い）。変種は 名前:LB:S0_0:S0_1:SHIFT:定義:posctl（N_ACC 5・N_DUMP 2・格子 2^2 フレーム）
#   wsp-b1: B 1（512 MHz）、S0 100（銀行の途中から）・12288（上の端）/ wsp-b2: B 2（1 GHz）、S0 1000・4096（上の端）/
#   wsp-b4: B 4（全帯域、流れ 1 は空）/ wsp-sat: B 4・SHIFT 4（飽和、DUMP_SAT を比べる）/
#   wsp-pg: K_F を 1 ずらした DUT（D-2 のフレームの区切りの陽性対照。A1' が落ちるべき）/
#   wsp-pa: B 1 で積分器の番地の上の bit を見ない（書き込みの衝突の陽性対照。flags[7] と A2 が落ちるべき）
#   wsp-rdy: B 2、IP の行動模型の tready をリセットから 5000 クロック上げない（実機の「IP が受けない」の模型。口が tready を待つので通るべき。
#            proj023 4b の前の RTL では flags[5]・[4] と A1' が落ちた）
#   wsp-stl: B 2、IP の行動模型が受けたビート 7 個目の後に tready を 1 クロック下げる（実機 5 回目の「最初の入力の近くで 1 回待たせる」の模型。
#            IP の手前の待ち行列が吸うので通るべき）/ wsp-stlp: 同じ模型で待ち行列を外した DUT（-DIPQ_POSCTL。陽性対照。flags[5]・[4] と A1' が落ちるべき）
#   定義を 2 つ以上渡すときは __ でつなぐ（空白の代わり）
# **成否は各ログの「結果: 全部通過」で読む**。Vivado サーバで流すときは WSP_VARIANTS を全部（既定）、手元で急ぐときは 1 本ずつ
WSP_RTL := ../../common/wide_coef_rom.v ../../common/wide_tw_rom.v ../../common/wide_spec.v ../../common/wide_pfb.v ../../common/wide_chain.v \
           ../../common/wide_acc.v ../../common/cmul.v ../../common/dft16.v sim/lane_fft_w_model.v sim/tb_wide_spec.v
WSP_VARIANTS ?= wsp-b1:0:100:12288:7:: wsp-b2:1:1000:4096:7:: wsp-b4:2:0:0:7:: wsp-sat:2:0:0:4:: \
                wsp-pg:2:0:0:7:-DPOSCTL_GRID:posctl wsp-pa:0:100:12288:7:-DACC_POSCTL:posctl \
                wsp-rdy:1:1000:4096:7:-DFFT_READY_DELAY=5000: wsp-stl:1:1000:4096:7:-DFFT_STALL_AT=7: \
                wsp-stlp:1:1000:4096:7:-DFFT_STALL_AT=7__-DIPQ_POSCTL:posctl
.PHONY: sim-wsp
sim-wsp:
	@mkdir -p build-sim-logs
	@for v in $(WSP_VARIANTS); do \
	  nm=$$(echo "$$v" | cut -d: -f1); lb=$$(echo "$$v" | cut -d: -f2); a=$$(echo "$$v" | cut -d: -f3); b=$$(echo "$$v" | cut -d: -f4); \
	  sh=$$(echo "$$v" | cut -d: -f5); def=$$(echo "$$v" | cut -d: -f6 | sed "s/__/ /g"); pc=$$(echo "$$v" | cut -d: -f7); d=build-sim-$$nm; \
	  ( mkdir -p $$d && $(PYTHON) sim/check_wide.py gen $$d 6 && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DCOEF=\"$(WPFB_COEF)\" -DTWF=\"$(WCH_TW)\" -DLB=$$lb -DS00=$$a -DS01=$$b -DSHIFT=$$sh \
	      -DNACC=5 -DGF=2 -o $$d/tb $(WSP_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_wide.py spec $$d $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-wsp*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-wsp*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-wsp: 全部通過"; fi

# ---- proj023 手順 2c-3: wide_core（流れのブロック × 2・FFT_N・ARM_WRST / ARM_RUN・DUMP_H・SPEC のレコード）の sim ----
# iverilog で 1 本 5 分ほど。変種は 名前:LB:S0_0:S0_1:SHIFT:定義:posctl（N_ACC 5・N_DUMP 2・格子 2^2 フレーム）
#   wco-b1: B 1、S0 100・12288、時刻の健全性をダンプ 1 にだけ立てる（DUMP_H）/ wco-b2: B 2、出口をときどき止める（rec_fr の FIFO）/
#   wco-b4: B 4（流れ 1 は空: NCH 0・レコードを出さない）/ wco-p: 語 7 の S0_CUR を入れない（陽性対照。頭の照合が落ちるべき）
WCO_RTL := ../../common/wide_coef_rom.v ../../common/wide_tw_rom.v ../../common/wide_core.v ../../common/wide_spec.v ../../common/wide_pfb.v \
           ../../common/wide_chain.v ../../common/wide_acc.v ../../common/cmul.v ../../common/dft16.v ../../common/rec_fr.v ../../common/adc_ev.v \
           sim/lane_fft_w_model.v sim/tb_wide_core.v
WCO_VARIANTS ?= wco-b1:0:100:12288:7:-DTEV: wco-b2:1:1000:4096:7:-DSTALL: wco-b4:2:0:0:7:: wco-p:1:1000:4096:7:-DW7_POSCTL:posctl
.PHONY: sim-wco
sim-wco:
	@mkdir -p build-sim-logs
	@for v in $(WCO_VARIANTS); do \
	  nm=$$(echo "$$v" | cut -d: -f1); lb=$$(echo "$$v" | cut -d: -f2); a=$$(echo "$$v" | cut -d: -f3); b=$$(echo "$$v" | cut -d: -f4); \
	  sh=$$(echo "$$v" | cut -d: -f5); def=$$(echo "$$v" | cut -d: -f6); pc=$$(echo "$$v" | cut -d: -f7); d=build-sim-$$nm; \
	  ( mkdir -p $$d && $(PYTHON) sim/check_wide.py gen $$d 6 && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DCOEF=\"$(WPFB_COEF)\" -DTWF=\"$(WCH_TW)\" -DLB=$$lb -DS00=$$a -DS01=$$b -DSHIFT=$$sh \
	      -DNACC=5 -DGF=2 -o $$d/tb $(WCO_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_wide.py core $$d $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-wco*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-wco*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-wco: 全部通過"; fi

# ---- proj023 手順 4e: SLICE の遅れ D_S（INTERFACE 5.2）。wide_s45_core に孤立したサンプルを 12 個、RAW の口は axis_sel4 の 1 段ぶん遅らせて入れ、
#   SLICE が付ける T（IP の出口の位相とフレームのラベル）と RAW の SNAP の T を比べる。iverilog で 1 本 4 分ほど
#   wds: 実機の配線（D_S = 0 のはず）/ wds-p: RAW の口を遅らせない（陽性対照。D_S = +1 で落ちるべき）
WDS_RTL := ../../common/wide_coef_rom.v ../../common/wide_tw_rom.v ../../common/wide_s45_core.v ../../common/core_cmn.v ../../common/tp_core.v \
           ../../common/raw_core.v ../../common/rec_arb.v ../../common/wide_core.v ../../common/wide_spec.v ../../common/wide_pfb.v ../../common/wide_chain.v \
           ../../common/wide_acc.v ../../common/cmul.v ../../common/dft16.v ../../common/rec_fr.v ../../common/adc_ev.v sim/lane_fft_w_model.v sim/tb_wide_ds.v
WDS_VARIANTS ?= wds:: wds-p:-DDS_NODELAY:posctl
.PHONY: sim-wds
sim-wds:
	@mkdir -p build-sim-logs
	@for v in $(WDS_VARIANTS); do \
	  nm=$$(echo "$$v" | cut -d: -f1); def=$$(echo "$$v" | cut -d: -f2); pc=$$(echo "$$v" | cut -d: -f3); d=build-sim-$$nm; \
	  ( mkdir -p $$d && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DCOEF=\"$(WPFB_COEF)\" -DTWF=\"$(WCH_TW)\" -DNIMP=12 -o $$d/tb $(WDS_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_ds.py $$d $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-wds*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-wds*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-wds: 全部通過"; fi

# ---- proj023 手順 3: wide_s45_core（コアの共通 core_cmn ＋ wide_core ＋ RAW ＋ レコードの束ね）の sim ----
# iverilog で 1 本 5 分ほど。変種は 名前:LB:S0_0:S0_1:SHIFT:定義:posctl（N_ACC 5・N_DUMP 2・格子 2^2 フレーム。RAW は N_ACC 20 フレーム × 2）
#   ws45-b2: B 2、時刻の健全性をダンプ 1 にだけ / ws45-b4: B 4、出口をときどき止める /
#   ws45-p: コアの FFT_N（0x80）の書きを wide_core に渡さない（陽性対照。束ねが既定のまま → FFT_N・頭・A2 が落ちるべき）
WS45_RTL := ../../common/wide_coef_rom.v ../../common/wide_tw_rom.v ../../common/wide_s45_core.v ../../common/core_cmn.v ../../common/tp_core.v \
            ../../common/raw_core.v ../../common/rec_arb.v ../../common/wide_core.v ../../common/wide_spec.v ../../common/wide_pfb.v ../../common/wide_chain.v \
            ../../common/wide_acc.v ../../common/cmul.v ../../common/dft16.v ../../common/rec_fr.v ../../common/adc_ev.v sim/lane_fft_w_model.v sim/tb_wide_s45.v
WS45_VARIANTS ?= ws45-b2:1:1000:4096:7:-DTEV: ws45-b4:2:0:0:7:-DSTALL: ws45-p:1:1000:4096:7:-DFFTN_POSCTL:posctl
.PHONY: sim-ws45
sim-ws45:
	@mkdir -p build-sim-logs
	@for v in $(WS45_VARIANTS); do \
	  nm=$$(echo "$$v" | cut -d: -f1); lb=$$(echo "$$v" | cut -d: -f2); a=$$(echo "$$v" | cut -d: -f3); b=$$(echo "$$v" | cut -d: -f4); \
	  sh=$$(echo "$$v" | cut -d: -f5); def=$$(echo "$$v" | cut -d: -f6); pc=$$(echo "$$v" | cut -d: -f7); d=build-sim-$$nm; \
	  ( mkdir -p $$d && $(PYTHON) sim/check_wide.py gen $$d 6 && \
	    $(IVERILOG) -g2005 $$def -DOUT=\"$$d\" -DCOEF=\"$(WPFB_COEF)\" -DTWF=\"$(WCH_TW)\" -DLB=$$lb -DS00=$$a -DS01=$$b -DSHIFT=$$sh \
	      -DNACC=5 -DGF=2 -o $$d/tb $(WS45_RTL) && \
	    $(VVP) -n $$d/tb && $(PYTHON) sim/check_wide.py s45 $$d $$pc ) > build-sim-logs/sim-$$nm.log 2>&1 & \
	done; wait
	@for f in build-sim-logs/sim-ws45*.log; do printf '%-36s %s\n' "$$f" "$$(grep '結果:' $$f || echo '結果の行が無い（途中で落ちた）')"; done
	@fail=$$(grep -L '結果: 全部通過' build-sim-logs/sim-ws45*.log); \
	  if [ -n "$$fail" ]; then echo "FAIL: $$fail"; exit 1; else echo "sim-ws45: 全部通過"; fi
