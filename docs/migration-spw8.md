# study-rfsoc からの移植計画（SpW8）

- 状態: **M0**（2026-11-03、ブランチ `spw8/m0-map`）。置き場所の表・`hw/common/` との違い・移植元の bit を数え、判定を `test/acceptance/spw8/` に書き起こした（PR #98）。仕様の S は PR #99（ADR 0028）。**M1 済み**（2026-11-03、ブランチ `spw8/m1-place`。表の行き先に置き、パスと係数の名前だけを直した。下の「M1 の結果」）。**M2 済み**（2026-11-03、ブランチ `spw8/sim-targets`。sim を Makefile の目標に書き起こし、同じ目標を proj032-m0 に当てて出力がバイト単位で同じ。下の「M2 の結果」）。**M3 済み**（2026-11-04、ブランチ `spw8/m3-build`。PEPRPO の作り直しで FDRI・構成の流れ・WNS / WHS まで移植元と同じ。下の「M3 の結果」）。**M4 済み**（2026-11-04、ブランチ `spw8/m4-board`。ID・NG 10・`--fast` の NG 5・計画の窓と WRST の約束・SG の CW の ch の位置が P-9・P-13・P-10b・P-13b と同じ。下の「M4 の結果」）。**M5a 済み**（2026-11-04、ブランチ `spw8/m5a-delay-table`。D(NS) を (BIT_KIND, BIT_REV) の表 `timebase.WIN_DELAY` にし、(7, 10) を足した。下の「M5a の結果」）。**M5b 済み**（2026-11-04、ブランチ `spw8/m5b-specd`。specd の SpW Backend（論理の窓・計画・C のリングの道）で、実機の W-1・TW・WRST・NET が通った。下の「M5b の結果」）
- 移植元: **`study-rfsoc@proj032-m0`**（注釈つきタグ、commit a80cee7。push は下の「始める条件」）。proj032 の **b5 rev 10**（4 ADC × 窓 8 本、チップ内の枠だけ・PL の DDR なし）
  - proj032 は b1〜b5 が `src/` を共有する形で、b5 rev 10 は `b5/` の Makefile・build.tcl・build_post.tcl が `../src/` を読む。**移すのは b5 と、b5 と sim が読むものだけ**（b1〜b4・d1・d3 は移さない）
  - **実装の戦略は Performance_ExplorePostRoutePhysOpt**（`b5/build-PEPRPO/`、WNS +0.016 ns）。P-9 の実機の判定はこの bit で通った。既定（PND）の rev 10 は WNS −0.024 ns で閉じていない
- 土台にする決め方: SAM45-Fine の [`migration.md`](migration.md) の M0〜M7（2G-2 の [`migration-2g-2.md`](migration-2g-2.md) と同じ段取り）。違うところだけをここに書く
- 仕様の決め（2026-11-03、開発者、proj032 README の「決めた」）: WRST_T の下限は bit ごと・specd の SpW の窓のキーは論理の窓・D(NS) は (BIT_KIND, BIT_REV) の表に。入れる先は下の「手順」の S・M5a・M5b

## 原則（2G-2 と違うところ）

1. 2G-2 の原則 1〜3 はそのまま（変更は一度に一つ・数えて確かめる・**study-rfsoc の proj032 は書き換えない**）
2. **PS は新しく書く。** YATSUGATAKE の specd には SpW の Backend が無い（これまでの bit は、移植元の PS がほぼそのまま `sw/pynq/` に入っていた）。
   そこで **M4 までは移植元の試行の道具（`b5/pynq/`）を `hw/bits/spw8/pynq/` に移植元のまま置いて回し**、specd の SpW Backend は M5b で機能を足す PR として書く。M5b は「同じものができたか」ではなく「決めた仕様どおりに動くか」で判定する
3. **M1〜M4 は `sw/pynq/`・`hw/common/`・ほかの bit のファイルに触らない。** `sw/pynq/` にある同じ名前の `plring.py`・`s45core.py` は移植元と中身が違う（下）ので、試行の道具の側に写しを置く
4. **仕様は M0 の直後に別の PR（S）で入れる**（決め 1・2 の文書）。決め 3 の文書は、コード（`timebase` の表）と同じ PR（M5a）で入れる

## 始める条件

- [x] proj032 の判定（P-9 b5 rev 10・P-10b・P-12・P-13・P-13b）が通り、README に結論が書かれている（2026-11-03）
- [x] SpW8 の運用に使う bit を決めた → **`b5/build-PEPRPO/`**（下の「移植元の bit」）
- [x] YATSUGATAKE に移すときの仕様を決めた（2026-11-03、開発者。上の 3 点）
- [x] **判定を `test/acceptance/spw8/` の書き方で書き起こした**（2026-11-03、M0 で）: 11 判定。specd を通す判定（V2-b・V2-L・RING・NET など）は study-rfsoc で回していない（M6 で初めて）
- [x] **タグ** `proj032-m0`（a80cee7、proj032 の README に「移植元を決める」の節を足した commit）を push した（2026-11-03）

### 移植元の bit（M3 の比べの相手）

study-rfsoc の proj032 の `b5/build-PEPRPO/`（2026-11-02 18:13 に書いた .bit）。sha256・FDRI・CDC は手元の `proj032/b5/build-PEPRPO/` で数えた（2026-11-03）。

| 項目 | 値 |
|---|---|
| bit の sha256 | `232c92fe758a1ffc69c60eec1478a48e2762bf093984524d1b502f7b55b2cb5f`（34,437,476 B） |
| hwh の sha256 | `b761c6d59effd8f4d551d60db975444f4d49b6055bd3e5ffb3de8af7ab877b5b` |
| FDRI（`sw/pynq/bitinfo.py`） | 8,608,824 語・sha256 `de7e9d882f560f05b288a591edf8e3a8a7c5e42099e059d69c3b58036a7b3225` |
| 構成の流れ（欄 e）の sha256 | `57bb27ea1efb0b5ae0b7d623733f592f74e6e94935e218e9ff2a92bd9e3a0a97` |
| ID | **BIT_KIND 7・BIT_REV 10・PROJ 0x0032_0300**。IF_ID 0x0207_0A01（コア 4 個、NSTREAM 8・CAPS 3）・0x0207_0A02（time_core）・0x0207_0A03（リング）。USR_ACCESS なし |
| コアの形 | H 8・E 3・S 8・NK 8・G_L2 19。WRST_T の下限 8 クロック（rev 10 の `spw_regs.v`、既定 64） |
| 実装の戦略 | **Performance_ExplorePostRoutePhysOpt**（`make IMPL=Performance_ExplorePostRoutePhysOpt`、出力は `build-PEPRPO/`） |
| `-1` の WNS / WHS | **+0.015935 ns / +0.009527 ns**（vivado.log の「TIMING (確定)」）。CRITICAL WARNING 0 |
| LUT / FF / CLB | 265,530（62.44 %）/ 308,700（36.29 %）/ 50,243（94.51 %） |
| DSP / BRAM タイル / URAM | 2,896（67.79 %）/ 982（90.93 %）/ 56 |
| `report_cdc` | CDC-3 Info 105・CDC-6 Warning 5・CDC-15 Warning 3,137（配線後の dcp に `report_cdc -details` を当てて数えた。build.tcl は CDC を出さない）。Critical 0 |
| Vivado | 2024.1 |
| F-2 | 回していない（ADR 0023） |

- **ビルドは commit の前の作業ツリーから走った**（.bit 18:13、rev 10 を入れた commit e8ff602 は 22:25）。e8ff602 から今（0e612e9）までに `src/`・`b5/` の Tcl と Makefile は変わっていない（`git diff --stat`）。
  ただし P-11（粗い PFB の書き換え、捨てた）は「b5 のビルドと並べて」試したので、**ビルドが読んだ `pfb64_core.v` が e8ff602 の版と同じかは記録から言えない**。M3 の FDRI の比べがそのまま確かめになる（下の「M3 の心配」）
- bit そのものは git に入れない（ADR 0018）

## 置き場所の対応（M0、2026-11-03）

ファイル 1 つずつの行き先は付録 [`migration-spw8-files.md`](migration-spw8-files.md)（proj032 の 198 個: 置く 58・既にある 15・移さない 125）。

| study-rfsoc（proj032-m0） | YATSUGATAKE（M1） | 備考 |
|---|---|---|
| `b5/Makefile`・`build.tcl`・`build_post.tcl` | `hw/bits/spw8/` | パスだけを直す（下の「M1 で直すパス」） |
| `src/spw/`（27 個のうち 22 個） | `hw/bits/spw8/src/spw/` | b5 の build.tcl が読む 21 個（.v 19・.vh 2）と sim だけが読む `ddrr_mux3.v`。**`spw/` の下に置く**ので build.tcl の `$S/spw/…` と sim の `-I src/spw -y src/spw` は直さない |
| `src/spw/` の残り 5 個 | 移さない | `spw_s45_core_ddr.v`・`spw_s45_core_ddrm.v`（b2・b3 の PL の DDR の形）・`hbmc_ooc.v`・`ksink_ooc.v`・`wsb_ooc.v`（OOC の包み） |
| `src/common/` 11 個・`src/board/` 3 個 | **既にある** `hw/common/`・`hw/board/` | 7 個がバイト単位で同じ。違う 7 個は注釈 1 行か書き方だけ（下の「`hw/common/` との違い」） |
| `sim/`（21 個） | `hw/bits/spw8/sim/` | 試験台 12・照合 8・FFT IP の模型 `win_fft_model.v`・PS の DDR の模型 `axi_mem_model.v`。`check_ring.py`・`win_fft_model.v` は SAM45-Fine の同名と違う版（bit ごとのディレクトリなので重ならない） |
| `model/pfb64_fixed.py`・`win64_fixed.py`・`win64_model.py` | `model/` | 名前は今の `model/` と重ならない |
| `runs/m0_coef.json` | **`model/spw8_coef.json`**（名前を替える） | 粗い PFB・light・final の係数の設計（M-0）。模型 2 個と sim の照合 2 個が `../runs/m0_coef.json` で読む。`runs/` は git に入れない置き場なので模型の隣に移す（決めること 1） |
| `model/pfb4_coef.txt` | **既にある** `model/pfb4_coef.txt` | バイト単位で同じ（窓の PFB の係数、SAM45-Fine と同じ） |
| `tools/test_spwplan.py`・`tools/crc128_masks.py` | `hw/bits/spw8/tools/` | spwplan の机の上の試験・ring128 の CRC の係数を作る道具 |
| `b5/pynq/`（6 個） | `hw/bits/spw8/pynq/` | M4 の試行の道具（`spw_b5.py`・`spwfast.c`・`spwplan.py` と、それが import する `plring.py`・`s45core.py`・`extref.py`）。移植元のまま |
| 残り 125 個 | 移さない | b1〜b4・d1・d3・`runs/`（試行の記録）・見積もりの模型 3 個（dump_burst・eng_sched・m2_hist8）・OOC と見積もりの道具 4 個・proj の README・Makefile・`program.tcl` |

### `hw/common/` との違い（2026-11-03）

proj032 の `src/common/` 11 個と `src/board/` 3 個を、YATSUGATAKE の main（54ce5e3、s2 の一本化の後）の `hw/common/`・`hw/board/` と比べた: **7 個がバイト単位で同じ、7 個が違う**。違いはどれも出力を変えない:

| ファイル | 違い |
|---|---|
| `adc_ev.v`・`core_cmn.v`・`tp_core.v`・`gb_adc.v`・`gb_gate.v`・`time_core.v` | proj032 の側に注釈が 1 行多いだけ（「proj032 P-6 / P-7: proj031（12681f1）の src/common から写した。中身は変えていない」）。行を除くとバイト単位で同じ |
| `cmul.v` | `hw/common/` の版は桁送り `SH` を parameter に出した（proj023、SAM45-Wide）。既定 16 で `(1 <<< (SH - 1))`・`>>> SH` が proj032 の `(1 <<< 15)`・`>>> 16` と同じ式 |

**案（決めること 2）: 7 個とも写しを置かず `hw/common/` の版を読む。** 2G-2 の `rec_fr.v` は中身が違ったので写しを置いたが、ここは注釈と定数の書き方だけで、合成の出力は同じになる見込み。M3 の FDRI の比べがそのまま確かめになる。
FDRI が違ったら、M3 の中で直さずに止め、写しを置いて作り直して原因を分ける。

### `sw/pynq/` との違い（2026-11-03）

`b5/pynq/` の 6 個のうち `extref.py` は `sw/pynq/` と同じ、`plring.py` は 1 行（`--bitfile` の既定 proj024.bit ↔ proj021.bit）、`s45core.py` は 29 行違う。`spw_b5.py`・`spwfast.c`・`spwplan.py` は `sw/pynq/` に無い。
M1〜M4 では 6 個とも `hw/bits/spw8/pynq/` に移植元のまま置く（決めること 3）。M5b で specd に入れるのは spwplan と spwfast.c の中身で、そのときに `plring`・`s45core` の違いを `sw/pynq/` の版に寄せる

### M1 で直すパス（予定）

中身は変えない:
- `build.tcl`: `../src/board/` → `../../board/`（3 行: `ps_preset.tcl`・`timing.xdc`・`pps.xdc`）、`$S/common/…` の 11 個 → `../../common/`（`S` は `src` のまま、`$S/spw/…` は直さない）。`build_post.tcl` は道を読まない（`$projdir` の中だけ）。`Makefile` は直す行なし（`BOARD_REPO`・`XILINX_VIVADO` は環境の値）
- sim の照合: `check_pfb64.py`・`check_pfb_chain.py`・`check_front.py`・`check_wsb.py` の模型の道（`"..", "model"` → `"..", "..", "..", "..", "model"` の形）と、`../runs/m0_coef.json` → `model/spw8_coef.json`
- 模型: `pfb64_fixed.py`・`win64_fixed.py` の `"..", "runs", "m0_coef.json"` → `"spw8_coef.json"`（同じディレクトリ）、`pfb64_fixed.py` の `"..", "src", "spw", "pfb64_coef.vh"` → `hw/bits/spw8/src/spw/pfb64_coef.vh`
- `tools/test_spwplan.py`: `"..", "b5", "pynq"` → `"..", "pynq"`、`"..", "model"` → 上と同じ形
- `runs/` は git に入れない（`.gitignore` に `/hw/bits/spw8/runs/`）
- **在ってはいけない側の照合**: SpW8 の Makefile・Tcl・sim・tools・pynq が、`src/common/`（移植元の写し）・`b1/`〜`b4/`・`spw_s45_core_ddr`・ほかの bit のディレクトリ・`runs/m0_coef.json` を指す行が 0

### M1 の結果（2026-11-03、ブランチ `spw8/m1-place`）

- **置く**（527f613）: 付録の置く 58 個を `git show study-rfsoc@proj032-m0:proj032/…` から取り出して置いた。58 個とも移植元と blob が同じ・モードも同じ 100644（`runs/m0_coef.json` は `model/spw8_coef.json` に）
- **パスの直し**: 8 個・23 行（build.tcl 7・sim の照合 4 個で 6・test_spwplan.py 3・模型 2 個で 7）。**違う行はすべてパスの行か係数の名前の行**: 新しい行のパスと名前を元に戻すと 23 行とも古い行と一致（機械で照合。陽性対照: 行に 1 字足すと不一致になる）
  - build.tcl は `$S/common/…` の 11 個を `$C/…` に替え、`S` を定める行に `set C [file normalize ../../common]` を並べた（`S` は `./src` で、`$S/spw/…` と include_dirs は直していない）。`../src/board/` の 3 行は `../../board/`、注釈の 1 行は `hw/board/`
  - 注釈と docstring の中の道も同じ規則で直した（check_front.py・pfb64_fixed.py・test_spwplan.py の 6 行）。**RTL と `.vh` の注釈の `runs/m0_coef.json` は直していない**（係数がどこから来たかの記録。M1 では RTL に触らない）
- **在ってはいけない側**: SpW8 の Makefile・Tcl・sim・tools・pynq と模型 3 個のコードの行が、`../src/`・`src/common`・`src/board`・`runs/m0_coef.json`・`"b5", "pynq"`・`b1/`〜`b4/`・`spw_s45_core_ddr`・ほかの bit のディレクトリ・Fine と 2G の模型の import を指す行は 0（直す前の版 527f613 に当てると 12 行を拾う = 照合が働いている）
- **動かして確かめたこと**（この PC、Vivado は使っていない）: `tools/test_spwplan.py` が「結果: 全部通過」（乱数の組 3000）。`pfb64_fixed.load()` が `spw8_coef.json` と式から作った係数を `hw/bits/spw8/src/spw/pfb64_coef.vh` と照らして一致。
  短い sim 3 本（`tb_spw_regs`・`tb_rmux4`・`tb_hbmc`）を移植先の道（`-I src/spw -I ../../common -y src/spw -y ../../common`）で回して「結果: 全部通過」。Tcl 2 個が `info complete` で完結、Python 18 個（sim 8・tools 2・pynq 5・模型 3）が `py_compile` を通る
- `runs/` と C の読み手の `libspwfast.so` は git に入れない（`.gitignore`）。`hw/bits/spw8/README.md` を足し、`hw/bits/README.md` の行を直した
- **気づいたこと（直していない）**: `model/win64_model.py` の docstring の使い方の行が `python3 win_model.py` のまま（proj021 の名前。移植元の誤り）。M1 は中身を変えないので、M2 の後の別の直しで

### sim の組（M1 の後の `spw8/sim-targets`、M2 の前）

proj032 には sim の Makefile の目標が無く、各 sim は README に書いた手で回した。**M2 の前に、移植先の Makefile に sim の目標を足す**（2G の makefile-trim の代わり。試行の目標を外すのではなく、手で回した形を目標に書き起こす）。組の候補（README の P-1〜P-13 から）:

| sim | 変種 | 照合 | 陽性対照 |
|---|---|---|---|
| `tb_pfb64` | PSPLIT 0・1 × 雑音 ＋ CW・満杯の方形波 | `check_pfb64.py`（整数の模型と bit 単位） | `PFB64_POSCTL_MODEL=1` |
| `tb_head` | — | `check_head.py` | — |
| `tb_hbmc` | 既定・`-DFINAL` | 自己判定（窓ごとの hb2 と bit 単位） | （書き戻しの窓をずらす。README の形を M0 の後に確かめる） |
| `tb_ddcb` | CFG 0〜3 | 自己判定 | — |
| `tb_front` | — | `check_front.py`・`check_pfb_chain.py` | `-DFRONT_POSCTL` |
| `tb_wsb` | c0・c1・c2・c0s6・c2s1 | `check_wsb.py`・`check_ring.py` | `-DENG_CFG_POSCTL`（TB_S 14・6） |
| `tb_core` | 既定・`-DCORE_STOP`・`-DRDMUX` | `check_front.py`・`check_wsb.py`・`check_ring.py` | `-DIPQ_POSCTL`・`-DTPX_POSCTL`・`-DCORE_POSCTL`・`-DDDRR_MUX_POSCTL` |
| `tb_spw_regs` | — | 自己判定（照らし 41 か所） | `-DREGS_POSCTL` |
| `tb_f32cv` | — | `check_f32cv.py` | `-DPOSCTL` |
| `tb_rmux4` | — | 自己判定 | `-DRMUX4_POSCTL` |
| `tb_spwdelay` | — | `check_spwdelay.py`（D(NS) = 86.03・135.07・231.05・411.01・757.03） | `-DDLY_POSCTL=1`・`=64` |
| 模型 | `test_spwplan.py`・`pfb64_fixed.py` の load | 自己判定 | — |

- コマンドの形（`-D`・plusargs・`+FFT_*`）は README に全部は書かれていない。sim-targets の PR で 1 本ずつ書き起こし、**同じ Makefile の目標を `git archive` で取り出した proj032-m0 にも当てて**（パスだけ読み替えて）M2 で比べる
- `tb_spwdelay` は 3 本で各 ≒ 20 分、`tb_core`・`tb_wsb` も長い。`sim-all` は 2G と同じく `SIM_J` 本ずつ並べる

### M2 の結果（2026-11-03、ブランチ `spw8/sim-targets`）

- **sim の目標**: `hw/bits/spw8/Makefile` の後ろに sim の節を足した。模型 3（`model-plan`・`model-pfb64`・`model-win`）と sim 11（`sim-pfb64`・`sim-head`・`sim-hbmc`・`sim-ddcb`・`sim-front`・`sim-wsb`・`sim-core`・`sim-regs`・`sim-f32cv`・`sim-rmux4`・`sim-dly`）。`make sim-all` が 14 本を `SIM_J` 本ずつ並べ、各目標の最後の行「sim-…: 全部通過」で判定する。`sim-dly` の 3 本は `tools/dly_cmp.py` で比べる（そのままの D(NS) が表の値と小数 2 桁まで同じ・入口に 1 段で ＋1 ±0.06・64 段で ＋64 ±0.005）
- 上の「sim の組」の候補から変えたところ（試験台の頭の注で確かめた）:
  - `tb_hbmc` の陽性対照は `-DHBMC_POSCTL`、`tb_ddcb` は `-DCFG=3 -DDDCB_POSCTL`、`tb_wsb` は `-DCFG=0 -DENG_POSCTL`、`tb_spw_regs`・`tb_rmux4` の陽性対照は「結果: 陽性対照は落ちた」の行で読む
  - **`tb_core` の `-DRDMUX`・`-DDDRR_MUX_POSCTL` は `sim-core` から外し、`sim-rdmux` に分けた**（sim-all には入れない）。ddrr_mux3 は b3 rev 6 の試みで、b5 の bit には入っていない。proj032 README の rev 6 に「sim は不合格」（山の帯域が足りず DDR の窓を通る記録が崩れる・前段の記録は既定と bit で同じ・陽性対照も同じ理由で落ちる）と記録がある。`sim-rdmux` はこの記録をそのまま照らす（前段の 4 個 `front_y`・`wsb_in`・`wsb_t`・`tp_x` が `core_n` と同じ、`check_wsb` が 2 本とも不合格）
  - 最初の版は vvp の出力を `tb.log` に書いていて、`check_ring.py` が読む `sim.log` が無く sim-wsb・sim-core が落ちた（見張りが働いた）。`sim.log` に直した
- **両側で全部通過**: 同じ目標（パスだけ読み替えた `Makefile.sim`）を `git archive` で取り出した proj032-m0 に当て、移植先と移植元の両方で 14 本が全部通過・陽性対照はすべて落ちた。`sim-rdmux` も両側で「記録どおり」。D(NS) は両側とも 86.03・135.07・231.05・411.01・757.03
- **出力のバイト比べ**（39 変種の全ファイル）: **出力 298 個がバイト単位で同じ**、片側だけのファイル 0。違ったのはコンパイルした `tb` だけ:
  - `tb` は vvp の番地（`0x…`）がコンパイルのたびに変わるので、番地を出てきた順の番号に置き換え、`src/common` と `../../common` を揃えてから比べた（同じ版を 2 回コンパイルして同じ・CFG を変えると違う、で照らしを確かめた）。20 個が同じ
  - 残る 18 個（粗い PFB を含む pfb64・front・dly・core・rdmux）は、`hw/common/` と違う 7 個（決めること 2: cmul の SH と、コメント 1 行の 6 個）で行番号がずれた分。**移植元をこの 7 個だけ `hw/common/` の版に差し替えてコンパイルし直すと 18 個とも移植先と同じ、元のままでは 18 個とも違う**。決めること 2 の違いはコンパイルの形だけで、sim の出力を変えない
- かかった時間（32 コアの機械、両側を同時に）: 重いのは sim-core ≒ 92 分・sim-front ≒ 88 分・sim-wsb ≒ 38 分・sim-dly ≒ 39〜46 分、sim-rdmux ≒ 80 分。ほかは数分。移植先の `make sim-all`（`SIM_J` 4）は通しで 88 分、「sim-all: 全部通過（14 個）」

### M3 の心配（M3 の前に書く）

- **WNS +0.016 ns は、これまで移した bit で最も小さい**（2G-1-Fast +0.025・2G-4 +0.047・2G-2 +0.074）。ただし SAM45-Fine から 2G-2 まで、ディレクトリだけ違う作り直しで構成データまで同じだった。同じになれば WNS も小数 6 桁まで同じ
- **負に落ちたら RTL も制約も戦略も直さずに止め、決め直す**
- 上の「ビルドは commit の前の作業ツリーから」: FDRI が違ったら、まず P-11 の直しが入っていたかを疑う（e8ff602 の `pfb64_core.v` で proj032 を作り直して FDRI を比べる）。`hw/common/` の 7 個（決めること 2）と切り分けるため、作り直しは 1 つずつ
- `.hwh` は TIMESTAMP と hex・vh の絶対パスが違うはず（2G-2 の M3 と同じ）

### M3 の結果（2026-11-04、ブランチ `spw8/m3-build`）

この PC で、移植先（`hw/bits/spw8/`、717a468 の木 = M2 と同じ RTL・build.tcl）の `make build IMPL=Performance_ExplorePostRoutePhysOpt JOBS=8`（`-1`・PEPRPO、移植元と同じ並列数）を回した（126 分。ほかの Vivado のビルドは無し）。予言（上の「M3 の心配」）どおり、**ディレクトリだけ違う作り直しで構成データまで同じ**:

| | 移植元（proj032 の `b5/build-PEPRPO/`） | 移植先（`build-PEPRPO/`） |
|---|---|---|
| FDRI | 8,608,824 語 / `de7e9d882f560f05b288a591edf8e3a8a7c5e42099e059d69c3b58036a7b3225` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `57bb27ea1efb0b5ae0b7d623733f592f74e6e94935e218e9ff2a92bd9e3a0a97` | **同じ**（.bit のファイルはヘッダの日付だけ違う） |
| TIMING（確定） | WNS 0.015935 ns / WHS 0.009527 ns | **同じ** |
| 報告 7 個（address_map・clock_interaction・clocks・rfdc_params・timing・utilization・utilization_hier） | LUT 265,530（62.44 %）など | 見出しの行（日付など）を除いて **全部同じ** |
| CDC（routed dcp に `report_cdc`） | 要約・詳細 | 見出しを除いて **要約も詳細（3,340 行）も同じ** |
| CRITICAL WARNING・ERROR | 0・0 | 同じ |

- **`.hwh`** は TIMESTAMP の 1 行だけが違う。予言した hex・vh の絶対パスは出なかった（SpW8 は係数を `.vh` で RTL に読み込み、BD の IP の設定に絶対パスを持たないため。外れた予言として残す）
- **P-11 の心配は消えた**: 移植元の .bit は rev 10 の commit（e8ff602）より前の作業ツリーから焼いたが、タグ（proj032-m0）の RTL で作り直した FDRI が同じなので、焼いた木はタグの RTL と同じだった
- **`hw/common/` の 7 個（決めること 2）は構成データを変えない**: cmul の SH（既定 16）とコメント 1 行の 6 個は、合成の結果に効かない（M2 の sim の出力と同じ結論）
- USR_ACCESS は焼いていない（M5c で入れる）。.bit は git に入れない（ADR 0018）

### M4 の結果（2026-11-04、ブランチ `spw8/m4-board`）

M3 で作った bit（FDRI `de7e9d88…3225`）と `hw/bits/spw8/pynq/` の 6 個（ボードの proj032 b5 の写しと sha256 で全部同じ。`libspwfast.so` はボードで `gcc -O3 -march=armv8-a+crc` で作り、前の写しとバイト単位で同じ）を、ボードの新しいディレクトリ（`~/spw8-m4`）に置いた。
配線は N（ノイズソース ON・15.00 V・512 mA、ATT 13 dB を各 run の前後に読んだ）。SG は `--tone` の 3 回だけ（下）。始める前にボードの specd・道具が動いていないこと（載っていたのは proj037.bit）と `/dev/shm` が空なことを見た。
`spw_b5.py --clkin 0 --ref 10` に `--bitfile ~/spw8-m4/proj032b5.bit`:

| run | 引数 | 比べる相手 | 結果 |
|---|---|---|---|
| `m4_b5_ng10` | `--cfg b5 --ng 10 --sec 10` | P-9 `p9b5_b5_ng10`（窓のレコード 16,376・DROP 0） | **全部通過**。窓のレコード **16,376**・DROP 0・照らしの誤り 0・CORE_FLAGS 0・EXT_CNT 0・リングの PEAK 15.4 MB。TP −31.50〜−31.65 dBFS（P-9 −31.35〜−31.50） |
| `m4_fast` | `--cfg b5 --ng 5 --fast --sec 30` | P-13 `p13_fast2`（52.4 MB/s・55.8 %・176 µs・DROP 0） | **全部通過**。52.4 MB/s・輪の中の時間 56.4 %・1 本 178 µs・DROP 0・窓のレコード 95,288・PEAK 40.2 MB |
| `m4_fastpos` | 同上 ＋ `--fast-posctl`、10 s | P-13 の陽性対照 | **落ちた**（窓のレコード 32,782 本が全部 CRC の誤り） |
| `m4_plan` | `--win 3900:128,3890:64,3890:64,3892:16,3891:8,3300:128,3290:32,2650:128 --alt 2,1 --wrst-test --ng 10 --sec 10` | P-10b `p10_plan2` | **全部通過**。WRST の約束 [1]〜[6] で PL の WRST_BAD が check() と 6 つとも同じ・破らない設定は WRST_CNT ＋1。窓のレコード 16,360・DROP 0。双子 0 ↔ 5 の比の中央値 1.00003〜1.00004（4 コア） |

ID（`m4_b5_ng10`）: 4 コアとも IF_ID 0x0207_0A01・PROJ 0x0032_0300・NSTREAM 8・CAPS 3、time_core 0x0207_0A02・リング 0x0207_0A03。

- **双子の比の揺れは P-10b と違う**（今回 0.0016・形の相関 0.99998・最大の ch 1821、P-10b 0.011・0.89〜0.98・486）。合否の線（独立な雑音の 1/4 = 0.016）はどちらも下回る。bit は FDRI で同じなので PL の振る舞いは同じで、違いは入力: P-10b は TP −33.4〜−33.6 dBFS（今回より 2 dB 低い）。proj032 README には、そのころ SG が別作業で掃引中だったとある。今回はノイズだけで 3890 MHz の周りに入力の傾き（平らさ 0.69〜1.59）があり、双子が同じ形を見るので相関が上がる。原因の切り分け（揺れの大きさが何で決まるか）はしていない
- **`--tone`（P-13b の CW の ch の位置）: 32 か所とも予言の ch とずれ 0**（2026-11-04、開発者の了承のうえで SG を使った）。SG E8257D（基準 EXT）＋9 dBm・ノイズ ON・ATT 13 dB（前後で読んだ）。
  窓は `m4_plan` と同じ 8 本に `--fast --ng 10 --sec 10`、CW は P-13b と同じ 3 点（3891.125 MHz: 窓 0〜4 の ch 284・4024・4024・224・4032、3294.8125 MHz: 窓 5・6 の ch 166・3480、2654.8125 MHz: 窓 7 の ch 3942）。
  `m4_cw0`〜`m4_cw2` の 3 回とも「全部通過」（DROP 0）。8 窓 × 4 コア = 32 か所の最大の ch が予言の ch と同じ、ピーク / 中央値 34.6〜54.7 dB（P-13b は 35.5〜54.7 dB）。
  SG は終わった後、元の状態（2000.3 MHz・＋9 dBm・出力 OFF・基準 EXT）に戻した
- 終わった後、ボードには M3 の bit が載ったまま（`~/spw8-m4/proj032b5.bit`）、`/dev/shm` は空。ATT は 13 dB のまま、ノイズソースは ON のまま（触っていない）
- 記録は `hw/bits/spw8/runs/m4/`（git に入れない）

### M5a の結果（2026-11-04、ブランチ `spw8/m5a-delay-table`）

- `sw/pynq/timebase.py`: 全 bit 共通だった `WIN_DELAY_BEATS` を、鍵が (BIT_KIND, BIT_REV) の表 `WIN_DELAY` にした。行は (2, 3) SAM45-Fine（値はそのまま）と (7, 10) SpW8 rev 10（NS 1〜5 = 86.03・135.07・231.05・411.01・757.03、P-12 と `make sim-dly` の値）。`Timebase` は載っている bit の鍵で行を選ぶ（`win_delay`）。表に無い bit・NS は `accuracy()` に `WIN_DELAY[鍵][NS]` を「未較正」と出し、D を引かない。`WIN_DELAY_BEATS` は (2, 3) の行の別名として残す（SAM45-Fine だけを扱う `s45v2c`・`timetest` が使う）
- `s45acq.Clock` は `Timebase` が選んだ行を受け取る（SAM45-Fine では前と同じ値）
- 新しい試験 `sw/pynq/test_win_delay.py`（PL なし）: **全部通過**。(2, 3) が M5a の前の値と同じ・(7, 10) が引ける・`Timebase.__init__` が鍵で選ぶ・SAM45-Fine と SpW8 で NS ごとに引く ns が表どおり・2G-4 (3, 1) と SpW8 の表に無い REV (7, 11) はどの NS も「未較正」で D を引かない。**陽性対照**（`-p`、M5a の前の形 = どの bit にも SAM45-Fine の行を当てる）は 24 項目が落ちた
- SAM45-Fine の値が変わらないこと: `test_cal_b.py` 全部通過（窓 NS 3 を含む）・`test_fake.sh all` 31 試験とも通過・`hw/bits/sam45-fine` の `make sim-regmap`（193 項目と test_regmap）が通過、陽性対照 `sim-regmap-p` は落ちた。`test_tpjump`・`test_timecal`・`test_nch`・`test_s45fast` も通過
- [`spec/timing.md`](spec/timing.md) の持ち越し（窓の D の表）を閉じ、D_eff の表に SpW8 の行を足した

### M5b の結果（2026-11-04、ブランチ `spw8/m5b-specd`、[ADR 0029](decisions/0029-spw-ring-records-f32.md) の PR #106 の上）

作ったもの（`sw/pynq/`）:
- `spwplan.py` を `hw/bits/spw8/pynq/` から移した（中身は同じ）。`hw/bits/spw8/pynq/` の `plring`・`s45core`・`extref` の写し（`sw/pynq/` の版との違いは既定値だけ）は消し、`spw_b5.py` は `sw/pynq/` の版を読む
- `s45acq.py`: `default_settings_spw`（4 ADC とも plan2）・`spw_plan`（SET のたびに 4 ADC とも計画、計画できない組は理由つきで断る）・`spw_cfgs`・`spw_map`、`SpwBackend`（コア 4 × DDC 8、ARM_WRST・ARM_RUN を time_core で、WRST の後に CORE_FLAGS[0]・WRST_CNT ＋1・WCUR・WCUR_DPHI・WCUR2 を読み返す）と `FakeSpwBackend`（流れのレジスタから出した窓の中心の IF を中身に書く）、`Bundler` の f32 の型、`Acq` の窓の数（`nw` 8）・SET のキー（`on`・`coarse`）・`_spec_record_spw`。窓の数に依らない所は SAM45-Fine・2G の道のまま（`test_fake.sh` の前からの 31 試験が通る）
- `s45fast.c`: `s45_spw_acc`（f32 → double の器・CRC・悪い値）・`s45_spw_rec`（器 → IF の昇順の float32・CRC）・**`s45_spw_scan`**（リングの [R, W) を 1 回なめ、magic・尾・CRC・(core, s) → 論理の窓・頭の照らし・SEQ・DUMP_K・束ねの区切り・足し込みを C で。束ができる・捨てる・TP で Python に戻る）
- `specd.py`（`--spw`・bits.json の `"kind": "spw8"`・`--posctl-spw-map`、GET・STATUS）・`specrecv.py`（DDC の L = 256e6 / df）・`s45client.py`（鍵 A0〜D7）・`timebase.TimeCore.IDS`（0x0207_0A02）・`s45core.BIT_REV_MIN_BY_KIND`（7: 10）
- 直したもの: `TpStream._take` は個を 1 つの組で書く（欄ごとに 4 回書くと 1 個 ≒ 20 µs）。`Clock.utc_ns` のスカラーは Python の整数で丸める（`_b2ns` に np.where を通すと 1 回 63 µs。式は同じ・10 万個で一致）。`test_ring_fast`・`test_bund_fast` の偽の Backend に `stall_at`（649f5ee から落ちていた）

**取得の速さ（実機で踏んだ）**: 初めは Python の道（Ring.read → 列 → poll_win → Bundler → C の足し込み）で、PL のレコード 1 本 ≒ 270 µs（ボードの A53）。32 窓 × 10.24 ms = 3,125 本 / s に追いつかず、tint 20.48 ms で 60 s 回すとリングが溢れた（`pl_drop` 47,836）。100 束だけの短い回しでは追いついて見えた（溢れる前に終わる）。
`--fast --fast-ring` を C のなめ（`s45_spw_scan`）にし、記録の道の重い所（時刻の丸め・TP の書き・ctypes の番地の引き）を直した後: なめ 57 µs / 本・束の記録 270 µs / 束・TP のレコード（10 個）≒ 240 µs / 本（実機の 60 s の STATUS の `spw_c_*` から）。tint 20.48 ms の 60 s で **SPEC 93,057・受け側の照合 通過・pl_drop 0・miss 0・1 周の p99 18.3 ms・最長 27 ms・リングの PEAK 2.6 MB**。取得の CPU は ≒ 69 %（なめ 18 %・束の記録 42 %・TP 9 %）。30 分（RATE・V2-b）と 0.3 s の止まり（RING）は M6

PL なしの試験（どこでも回る）:
- `test_spw_fast.py`（`spw_acc`・`SpwAcc`・`spw_rec` を zlib・numpy と bit で照らす）・`test_spw_ring.py`（type 5 のレコードを本物の `plring.Ring.read`・`SpwBackend` に通す。Python の道・C の足し込み・C のなめの 3 つで、32 窓 × 2 束が numpy の float64 の和と bit で同じ・CRC を壊した束を捨てる・頭の NS の違うレコードを捨てる・TP を Python で読む）: 全部通過。陽性対照（`-p`、`--posctl-spw-map`）は落ちる。ボードでも同じ結果
- `test_fake.sh`: **35 試験とも通過**（前からの 31 ＋ `spw`・`spwmap`・`spwp`・`spwcli`、`net`・`netp` に SpW8 を足した）。`spwmap` は論理の窓と s を同じ NS の 2 本で入れ替える陽性対照で、入れ替えた 160 束が IF の照らしで落ちる（NS の違う 2 本を入れ替えると頭の照らし `spw_hdrbad` が先に捨て、受け側に届かない）

実機（配線 N・ATT 13 dB と ノイズ ON を前後に読んだ。M3 の bit `proj032b5.bit`。ボードの `~/spw8-m5b` に `sw/pynq/` を置き `libs45fast.so` をボードで作った。specd `--clkin 0 --ref 10 --bits bits.json --fast --fast-ring --prefault`）:

| 判定 | 結果 |
|---|---|
| ID-1（specd の分） | ID: adc 02070a01・time 02070a02・proj 00320300・kind spw8・tcal board・nw 8。STATUS IDLE・time_ok 1・health 0x0000・flags 0x000 |
| W-1 | **通過**。CW 3 点（SG ＋9 dBm、基準 EXT）で、論理の窓の番号で 32 か所とも予言の ch とずれ 0（3891.125 MHz: A0〜D0 ch 284・窓 1・2 ch 4024・窓 3 ch 224・窓 4 ch 4032 / 3294.8125 MHz: 窓 5 ch 166・窓 6 ch 3480 / 2654.8125 MHz: 窓 7 ch 3942）。ピーク / 中央値 34.7〜54.8 dB（M4 34.6〜54.7 dB）。**陽性対照**（予言 ＋1 ch）は 3 点とも落ちた。SG は元の状態（2000.3 MHz・＋9 dBm・出力 OFF・基準 EXT）に戻した |
| TW | **通過**。`A2.coarse=alt A1.coarse=near`（B〜D も）で 250 束: 4 ADC とも双子の比の中央値 1.00003〜1.00004・比の相対の揺れ 0.0016（線 = 独立な雑音の 1/4 = 0.0112）・形の相関 0.99998。**陽性対照**（spwplan の R0 512 の specd）: 比の中央値 1.34〜1.40・揺れ 0.45・相関 −0.86〜−0.91 で落ちた |
| WRST | **通過**。計画できない組（ADC_B に `alt` の無い 128 MHz・ADC_B の偶奇の組の頭が埋まる組・ADC_A の 128 MHz の `alt`）は ERR で理由つき、直後の GET と `spw_map` は元のまま。次の START の WRST は約束を通り（CORE_FLAGS[0] 0・WRST_CNT ＋1・WCUR の読み返しが合う）、記録は照らしの道具で全部通過 |
| NET | **通過**。32 窓の `SET tint=0.01024` は ERR（「51.2 MB/s」「予算 30 MB/s を越える」「この構成の tint の最小は 0.02048 s」）で GET は 0.04096 のまま、0.02048 は OK、窓 16 本（`C.on=0 D.on=0`）なら 0.01024 が OK。**陽性対照**（`--net-budget-mbs 0`）で 32 窓の 0.01024 が OK |

- 照らしの道具は `hw/bits/spw8/tools/spw_recv_check.py`（specrecv の .s45 を読み、予言は自分の spwplan の計画から出す。CW・双子・記録の頭）
- 記録は `hw/bits/spw8/runs/m5b/`（git に入れない）。終わった後、ボードには M3 の bit が載ったまま、specd は止め、`/dev/shm` は空。ATT 13 dB・ノイズ ON のまま
- `WRST_T` に 1〜7 を書く確かめ（判定 WRST の 3 つ目）は M4 の道具の分で、specd は WRST_T を書かない（interface の WRST_T）

### M5c でしたこと（2026-11-04、ブランチ `spw8/m5c-usr-access`）

- **USR_ACCESS のフック**（Fine の M5b・2G-2 の M5 と同じ）: `hw/bits/spw8/Makefile` に 12 行（git から `USR_ACCESS` を作って build.tcl に渡し、書き出した `proj032b5.bit` を `sw/pynq/bitinfo.py --expect` で読み返す）・`build.tcl` に 22 行（`STEPS.WRITE_BITSTREAM.TCL.PRE` のフック。本体は 2G-2 の行と同じ）。RTL・制約・build_post.tcl は変えない
- PS は変えない: `SpwBackend` の ID は M5b から `usr=self._usr_access()`（載せた .bit を bitinfo で読む）
- 机の上で: `make -n build` で USR_ACCESS が git から作られ（`0x` ＋ commit 7 桁 ＋ 汚れ）、vivado の後に読み返しが走る。M3 の bit を `bitinfo.py --expect none` で読むと通過、`--expect 0x12345670` で失敗。フックの節を tclsh で切り出して回すと、commit の値と `none` の両方で 2G-2 と同じ中身

### M5c の予言（作り直しと回し直しの前に書いた、2026-11-04）

1. **M2 の回し直し**（この commit の木、`make sim-all SIMDIR=build-sim-m5c`）: 14 個とも「全部通過」・陽性対照は落ちる。`build-sim-m5c/` は M2 の `build-sim/` と、iverilog の `tb` の番地（`0x…`）を除いてバイト単位で同じ（RTL も sim も変えていない）
2. **M3 の焼き直し**（この commit の木、`make build IMPL=Performance_ExplorePostRoutePhysOpt JOBS=8 OUTDIR=build-m5c`）: USR_ACCESS が commit（汚れ 0）で、make の読み返しが通る。**FDRI は M3 と同じ**（`de7e9d88…3225`。USR_ACCESS は FDRI の外）、構成の流れ（欄 e）の sha256 は変わる（`57bb27ea…0a97` から）。TIMING（確定）は M3 と小数 6 桁まで同じ（WNS 0.015935 / WHS 0.009527 ns）。報告 7 個と CDC は見出しの行を除いて同じ。CRITICAL WARNING・ERROR 0。`.hwh` は TIMESTAMP の 1 行だけ違う。外れたら作り直しは繰り返さず、何が違ったかを数えてから決め直す
3. **M4 の回し直し**（ボードの新しいディレクトリ、今回の bit、配線 N）: `spw_b5.py` の `m4_b5_ng10`・`m4_fast`・`m4_plan` の 3 つが M4 と同じ結果（窓のレコード 16,376・DROP 0 / 52.4 MB/s・DROP 0 / WRST の約束 6 つ・双子の比の中央値 1.0000x）。specd（M5b の起こし方）の ID に **usr = commit**・ほかは M5b と同じ、短い取得で `spw_recv_check.py` の記録の照らしが通る。ID の陽性対照: M3 の bit で起こすと usr none

## 手順

| 手順 | ブランチ | SpW8 ですること | 合格 |
|---|---|---|---|
| M0 | `spw8/m0-map` | 置き場所の表（この文書と付録）・始める条件・`hw/common/` との違いの数え・判定の書き起こし | 全ファイルに行き先がある・始める条件が全部 [x] |
| S | `spw8/spec` | ADR 0028（決め 1・2）。`interface.md` の WRST_T に「bit ごとに下限があり、短い値は下限に切り上げる（SpW8 は 8 クロック）」、specd の SpW の窓のキーは論理の窓（SET は 1 コアの組をまとめて受け、計画できなければ組ごと断る・STATUS に対応・受け側へのレコードも論理の番号）、`bits.md` の SpW8 の行（b5、ネットワークの tint は 20.48 ms から） | 文書だけ。M1〜M3 と並べて進めてよい |
| M1 | `spw8/m1-place` | 表の行き先に置き、パスと名前（`spw8_coef.json`）だけを直す | 違う行はすべてパスの行か名前の行。在ってはいけない側の照合（**2026-11-03**: 上の「M1 の結果」） |
| — | `spw8/sim-targets` | 上の「sim の組」を Makefile の目標に書き起こす（**2026-11-03**: 上の「M2 の結果」） | — |
| M2 | 同上 | sim を全部回し、proj032-m0 と並べる | 全部通過し、**出力がバイト単位で同じ**。陽性対照が落ちる（**2026-11-03**: 出力 298 個が同じ・tb の違いは決めること 2 の 7 個だけ） |
| M3 | `spw8/m3-build` | ビルド（`-1`、**PEPRPO**） | **FDRI が移植元と同じ**（`de7e9d88…3225`）。WNS / WHS が小数 6 桁まで同じ（+0.015935 / +0.009527）（**2026-11-04**: 上の「M3 の結果」） |
| M4 | `spw8/m4-board` | 実機の短い回帰（`hw/bits/spw8/pynq/spw_b5.py`） | ID・`--cfg b5 --ng 10`（20.48 ms）の全部通過・`--fast --ng 5`（10.24 ms × 32 窓）の DROP 0・`--tone` の CW の ch が P-9・P-13・P-13b と同じ（**2026-11-04**: 上の「M4 の結果」） |
| M5a | `spw8/m5a-delay-table` | **決め 3**: `timebase.WIN_DELAY_BEATS` を (BIT_KIND, BIT_REV) の表にし、SpW8 rev 10 の D(NS) を小数 2 桁で入れる。`timing.md` の残り（91 行目）を同じ PR で閉じる | SAM45-Fine の値が変わらない（test_cal_b・s45v2c）。(7, 10) が引ける。表に無い組は「未較正」（**2026-11-04**: 上の「M5a の結果」） |
| M5b | `spw8/m5b-specd` | **決め 2**: specd に SpW Backend（spwplan で論理の窓 → 流れ s・SET は組ごと・STATUS に対応・レコードを論理の番号に・C の読み手 `--fast-ring` の f32 版・ネットワークの 10.24 ms を断る） | PL なしの試験（`test_fake.sh`。PSPLIT の無い bit では割り当てが恒等で振る舞いが今と同じ）と、実機で W-1・TW・WRST・NET（**2026-11-04**: 上の「M5b の結果」） |
| M5c | `spw8/m5c-usr-access` | USR_ACCESS を焼く（SAM45-Fine の M5b・2G-2 の M5） | M2〜M4 の回し直しが予言どおり（FDRI は変わらず、構成の流れが変わる） |
| M6 | `spw8/m6` | 判定（`test/acceptance/spw8/`）を全部通し、性能評価を書く | `docs/performance/spw8/v1.0.0.md` |
| M7 | `spw8/m7-docs` | spec・design・user の SpW8 の分を書き、リリース | `release.md` |

## 判定（`test/acceptance/spw8/`、2026-11-03 に書き起こした）

SAM45-Fine（窓）と 2G（specd・リング・予算）の判定から SpW8 に当たるものを選んだ。ID は同じ意味のものは同じ ID にする。

| ID | 何を確かめるか | study-rfsoc で |
|---|---|---|
| ID-1 | 自己記述（adc 0x0207_0A01・time 0x0207_0A02・ring 0x0207_0A03・proj 0x0032_0300・kind は M5b で決める名前）・起動の見張り | 通過（P-9 b5 rev 10、試行の道具） |
| H-0 | 立ち上げ（32 窓のレコードの頭の欄・K_F の格子・照合・平らさ・FLAGS 0） | 通過（P-9 `p9b5_b5_ng10`） |
| W-1 | SG の CW の ch（論理の窓の番号で、8 窓 × 4 コア） | 通過（P-13b、`s` の番号で） |
| TW | 2 番目に近い粗い ch・WDPHI ≠ 0 の窓と、近い ch の双子の比の揺れ | 通過（P-10b） |
| WRST | 約束を破る窓の組を SET で断る（PL の WRST_BAD と spwplan の印が同じ） | 通過（P-10b `--wrst-test`、試行の道具） |
| PS-1 | float32・utc_ns の補正（D(NS) の表が SpW8 の値で当たる） | なし（D(NS) は P-12 の sim） |
| RATE | PL と PS の取得 10.24 ms × 32 窓で 30 分 DROP 0 | 通過（P-13、試行の道具の C の読み手） |
| V2-b | ネットワークの tint 20.48 ms で 30 分（取りこぼし・照合・1 周の余裕） | なし |
| V2-L | tint 20.48 ms で 2 時間（電流・温度・落ちない） | なし（P-13 の 30 分で VCCINT 38.5 A・62 ℃） |
| RING | リング 64 MiB が PS の 0.3 s の止まりを吸う | なし |
| NET | 予算を越える tint（10.24 ms）を SET で断る | なし |

- 回さないもの: F-2（ADR 0023）。PL の DDR の窓（b5 に無い）。EQ（2 コアに同じ ADC。SpW8 は 4 コアとも ADC が決まっている）

## 決めること

1. **`runs/m0_coef.json` の置き場所** → **案**: `model/spw8_coef.json` に名前を替え、模型と sim の読む行を直す（M1 で「名前の直し」として数える）。`runs/` は bit ごとに git に入れない置き場なので、移植元の道のままにはできない
2. **`hw/common/` と違う 7 個（注釈 1 行・cmul の SH）の扱い** → **案**: 写しを置かず `hw/common/` の版を読む（上）。M3 の FDRI で確かめる
3. **M4 の試行の道具の置き場所** → **決め**（2026-11-03、開発者）: `hw/bits/spw8/pynq/` に移植元のまま。`sw/pynq/` の同名とは M5b で寄せる
4. **実装の戦略** → **決め**（2026-11-03、開発者）: PEPRPO（P-9 で判定した bit）
5. **仕様の PR の時期** → **決め**（2026-11-03、開発者）: M0 の直後（S）。決め 3 の文書は M5a のコードと同じ PR
