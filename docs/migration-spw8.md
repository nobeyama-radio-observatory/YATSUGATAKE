# study-rfsoc からの移植計画（SpW8）

- 状態: **M0**（2026-11-03、ブランチ `spw8/m0-map`）。置き場所の表・`hw/common/` との違い・移植元の bit を数え、判定を `test/acceptance/spw8/` に書き起こした（PR #98）。仕様の S は PR #99（ADR 0028）。**M1 済み**（2026-11-03、ブランチ `spw8/m1-place`。表の行き先に置き、パスと係数の名前だけを直した。下の「M1 の結果」）。**M2 済み**（2026-11-03、ブランチ `spw8/sim-targets`。sim を Makefile の目標に書き起こし、同じ目標を proj032-m0 に当てて出力がバイト単位で同じ。下の「M2 の結果」）。**M3 済み**（2026-11-04、ブランチ `spw8/m3-build`。PEPRPO の作り直しで FDRI・構成の流れ・WNS / WHS まで移植元と同じ。下の「M3 の結果」）。**M4 済み**（2026-11-04、ブランチ `spw8/m4-board`。ID・NG 10・`--fast` の NG 5・計画の窓と WRST の約束・SG の CW の ch の位置が P-9・P-13・P-10b・P-13b と同じ。下の「M4 の結果」）。**M5a 済み**（2026-11-04、ブランチ `spw8/m5a-delay-table`。D(NS) を (BIT_KIND, BIT_REV) の表 `timebase.WIN_DELAY` にし、(7, 10) を足した。下の「M5a の結果」）。**M5b 済み**（2026-11-04、ブランチ `spw8/m5b-specd`。specd の SpW Backend（論理の窓・計画・C のリングの道）で、実機の W-1・TW・WRST・NET が通った。下の「M5b の結果」）。**M5c 済み**（2026-11-04、ブランチ `spw8/m5c-usr-access`。USR_ACCESS を焼いた bit で M2〜M4 の回し直しが予言どおり（FDRI・TIMING・報告・CDC が M3 と同じ）、specd の ID に `usr`。下の「M5c の結果」）。**M6 済み**（2026-11-04、ブランチ `spw8/m6`。1 回目は判定 11 のうち 9 が通過し、V2-b・V2-L が loop_slow で、RING が 3 回のうち 1 回で落ちた。specd の束の記録を C に移し（取得の CPU 69 % → 34 %）、落ちた 3 つと関わる判定を回し直して 11 がすべて通過。下の「M6 の結果」、性能評価 [`performance/spw8/v1.0.0.md`](performance/spw8/v1.0.0.md)）。**M7**（2026-11-05、ブランチ `spw8/m7-docs`）: 仕様・設計（`docs/design/spw8/`）・使い方の SpW8 の分、CHANGELOG の v1.5.0。次はリリースのビルド（タグの commit で作り直し、FDRI が判定した bit と同じことを確かめる）
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

### M5c の結果（2026-11-04）: 予言 1・2 は当たり、3 は数の書き方の 1 か所だけ外れた

**予言 1（M2 の回し直し、6ed5843 の木、`make sim-all SIMDIR=build-sim-m5c`）: 当たり**。14 個とも「全部通過」・陽性対照はすべて落ちた（88 分、ビルドと並べて回した）。`build-sim-m5c/` と M2 の `build-sim/` の両方にある 296 個のうち 260 個がバイト単位で同じ、残る 36 個は iverilog の `tb` で、番地（`0x…`）を出てきた順の番号に読み替えると 36 個とも同じ（読み替えの陽性対照: CFG の違う `ddcb_0` と `ddcb_3` の `tb` は読み替えても違う）。M2 にだけある 40 個は `sim-rdmux` の分（`core_muxpos`・`core_rdmux`、sim-all の外）

**予言 2（M3 の焼き直し、6ed5843、`make build IMPL=Performance_ExplorePostRoutePhysOpt JOBS=8 OUTDIR=build-m5c`、`-1`・PEPRPO、2 時間 13 分）: 当たり**

| | M3（移植元と同じ） | M5c |
|---|---|---|
| USR_ACCESS（bitinfo） | なし | **6ed58430 = commit 6ed5843（汚れなし）**（書き込み 1 回）。make の読み返しの照合 通過、vivado.log と impl_1 の runme.log にも `USR_ACCESS: 0x6ed58430` |
| **FDRI** | 8,608,824 語 / `de7e9d882f560f05b288a591edf8e3a8a7c5e42099e059d69c3b58036a7b3225` | **同じ** |
| 構成の流れ（欄 e）の sha256 | `57bb27ea…0a97` | `04f6269c6c7631b6d5644b262f8cef94342e647dadf5a58c18f240b0226d6fbb`（USR_ACCESS の書き込みの分。.bit の長さは同じ 34,437,476 B） |
| TIMING（確定） | WNS 0.015935 / WHS 0.009527 ns | **同じ（小数 6 桁まで）** |
| 報告 7 個（見出しの日付・命令の行を除く） | | **7 個とも同じ** |
| CDC（routed dcp に `report_cdc`、見出しを除く） | 要約・詳細 | **要約も詳細（3,373 行）も同じ** |
| ERROR・CRITICAL WARNING | 0・0 | 同じ |
| `.hwh` | | TIMESTAMP の 1 行だけが違う |
| `.bit` / `.hwh` の sha256 | `fb7eb37d…e787` / — | `6b38f91882167825cc1a143d08af2649982b57e29996ecfa436d4f73608a0d2b` / `482409158986e699120eb4dcad69bdfaf328c80b0deebb364b145098e1f537e2` |

**予言 3（M4 の回し直し）: 結果は M4 と同じ。ただし予言に書いたレコードの数（16,376）は外れた**。ボードの `~/spw8-m5c`（今回の bit・hwh、6ed5843 の `sw/pynq/`、`spw_b5.py`・`spwfast.c`、bits.json は `"kind": "spw8"`・sha256 付き。`libs45fast.so` は `build_fast.sh` で「CRC: 命令」、`libspwfast.so` は M4 とバイト単位で同じ）。始める前にボードの specd・道具が動いていないこと（載っていたのは M3 の bit）と `/dev/shm` が空なこと、機器（ATT 13 dB・ノイズ ON 15.00 V・511 mA・SG 出力 OFF、配線 N）を読んだ。SG は使っていない

| run | M5c | M4 |
|---|---|---|
| `m5c_b5_ng10`（`--cfg b5 --ng 10 --sec 10`） | **全部通過**。窓のレコード 16,360・DROP 0・照らしの誤り 0・CORE_FLAGS 0・4 コアとも WRST_CNT 0 → 1・WRST_BAD 0。27.0 MB/s・465 µs / 本。TP −31.61〜−31.77 dBFS | 全部通過。16,376・DROP 0。27.0 MB/s・465 µs。TP −31.50〜−31.65 |
| `m5c_fast`（`--cfg b5 --ng 5 --fast --sec 30`） | **全部通過**。52.4 MB/s・輪の中の時間 56.1 %・1 本 177 µs・DROP 0・窓のレコード 95,279・C の CRC を zlib と照らした 50 本 | 全部通過。52.4 MB/s・56.4 %・178 µs・DROP 0・95,288 |
| `m5c_plan`（`--win … --alt 2,1 --wrst-test --ng 10 --sec 10`） | **全部通過**。WRST の約束 [0]〜[6] で PL の WRST_BAD が check() と 7 つとも同じ。窓のレコード 16,350・DROP 0。双子 0 ↔ 5 の比の中央値 1.00002〜1.00004・揺れ 0.0016・形の相関 0.99998 | 全部通過。16,360。1.00003〜1.00004・0.0016 |

- **外れ**: 窓のレコードの数は M4 と同じにならない（16,360 / 16,376、95,279 / 95,288）。`spw_b5.py` は `time.time() + sec` で読みを打ち切るので、数は壁の時計で決まり、回すたびに数束ぶん動く。M4 の中でも同じ NG 10 の `m4_b5_ng10` と `m4_plan` で 16,376 と 16,360 だった。DROP 0・照らしの誤り 0・CORE_FLAGS 0 は同じなので、PL の違いではない。予言の「16,376」は書き方が細かすぎた（次からは DROP と誤りで書く）
- **specd**（`~/spw8-m5c`、M5b の起こし方 `--clkin 0 --ref 10 --bits bits.json --fast --fast-ring --prefault`）: ID は adc_id 02070a01・time_id 02070a02・**usr 6ed58430**・tcal board・lmx_pwr 3・adcs 4・nw 8。STATUS は IDLE・time_ok 1・health 0x0000・flags 0x000・`spw_map` は M5b と同じ（plan2）。TW の形（`A2.coarse=alt A1.coarse=near`、B〜D も、250 束）を specrecv で受けて照合 通過（SPEC 8,000・CRC の誤り 0・説明できない欠け 0）、STATUS の miss 0・pl_drop 0・`spw_hdrbad`・`spw_seqgap`・`spw_stray`・`spw_valbad` 0。`spw_recv_check.py --twin 2,1` は全部通過（4 ADC とも比の中央値 1.00003〜1.00004・揺れ 0.0016・相関 0.99998〜0.99999、M5b と同じ）
- **ID の陽性対照**: M3 の bit（`~/spw8-m5b`、USR_ACCESS なし）で specd を起こすと ID が **usr none**（ほかは同じ）
- 終わった後: specd は `SHUTDOWN confirm=1` で止め、`/dev/shm` は空。ボードには M3 の bit が載ったまま（陽性対照の分）。ATT 13 dB・ノイズ ON（15.00 V・511 mA）・SG（2000.3 MHz・＋9 dBm・出力 OFF・基準 EXT）は前と同じ
- 記録は `hw/bits/spw8/runs/m5c/`（git に入れない）

### M6 の決め（2026-11-04、測る前に書いた。ブランチ `spw8/m6`）

対象の bit は M5c の bit（`6b38f918…0a2b`・USR_ACCESS 6ed58430）と、それに載せる `sw/pynq/`。配線は N（ATT 13 dB・ノイズ ON）、W-1 だけ N/S（SG ＋9 dBm、使う前の状態を記録して戻す）。判定の合格は `test/acceptance/spw8/` のまま変えない。specd の形で書き方が決まっていなかった所だけ、ここで決める:

1. **RATE の specd の形**: 受けは V2-b と同じ 30 分（PL 10.24 ms・ネットワークの tint 20.48 ms・32 窓）で、V2-b と 1 回の運転で兼ねる。「輪の中の時間の割合」は、STOP の直前の STATUS の `spw_c_scan_s ＋ spw_c_ev_s ＋ spw_c_one_s`（C のなめ・束の記録・Python で読んだ TP）÷ RUN の秒とする（試行の道具の「輪の中の時間」と同じく、リングを読んで記録にするまでの時間）。線は 70 % のまま。M5b の 60 s では ≒ 69 % だったので、**落ちうる**。試行の道具の形（`spw_b5.py --fast --ng 5 --sec 1800`）も同じ日に回す
2. **H-0 の specd の形**: b5 の組を IF:幅で SET する（`3584:128,3584:64,3328:64,3072:16,3520:128,2752:64,2496:32,3008:8`。spwplan はこれを b5 と同じ流れ s・粗い ch・NS・d 0 に計画する）。tint 0.02048 で 10 s 受け、`spw_recv_check.py --ref`（同じ日の試行の道具の `--cfg b5 --ng 10` の .json）で、32 窓とも**中央値の比 1 ± 0.05・16 区間の形の差 ≦ 0.05**。頭の欄・照合は受け側の照合と `spw_recv_check.py`、K_F・DUMP_K は試行の道具の形で見る（specd は DUMP_K の飛びを miss に数える）
3. **PS-1**: SpW8 の記録は PL が丸めた f32 で、Fine の `s45v2c.py` の u64 と f32 の組は無い（ADR 0029）。「float32 が PL の記録とバイト単位で同じ」は、**n_sum 1（tint 0.01024・窓 16 本 = ADC 2 つずつ 2 回）の SPEC の本体と、同じ運転で PL のリングから写し取った type 5 の本体を IF の昇順に並べたもの**を比べる。写し取りはボードの試験用ディレクトリの `plring.py` に `hw/bits/spw8/tools/spw_ps1.py patch` で包みを足す（製品には入れない。写し取りは Python の道なので specd は `--fast`・`--fast-ring` なし）。e の照らしは H-0 の運転（32 窓・NS 1〜5）の記録で、`spw_ps1.py check`。表を引いたかは `GET CAL` に足した `wdly`・`wdly_ns`（この PR で足した）で見る。陽性対照は `spw_ps1.py patch-nodly` で (7, 10) の行を外した specd（`wdly_ns=none`、e が NS で D の差だけずれる）
4. **順**: 試行の道具（H-0・RATE 30 分・陽性対照）→ specd 1（ID-1・GET CAL・H-0・W-1・TW・WRST・NET → V2-b ＝ RATE の specd の形 30 分）→ 写し取りの specd（PS-1）と陽性対照の specd → RING（0.3 s）と陽性対照（8 s）→ 起こし直した specd で V2-L 2 時間。AMS は RATE・V2-b・V2-L の間 10 s ごと（`amslog.py`）

### M6 の結果（2026-11-04）: 1 回目は判定 11 のうち 9 が通過、束の記録を C に移した回し直しで **11 がすべて通過**

対象は M5c の bit（`6b38f918…0a2b`・usr 6ed58430）と、ボードの `~/spw8-m6`（main の `sw/pynq/`、sha256 で同じ）。始める前と終わった後にボードの specd・道具が動いていないこと・`/dev/shm` が空なこと、ATT 13 dB・ノイズ ON（15.00 V・511 mA）・SG（2000.3 MHz・＋9 dBm・出力 OFF・基準 EXT）を読んだ。W-1 の後に SG を前の状態に戻した。記録は `hw/bits/spw8/runs/m6/`（git に入れない）。数字の全部は各判定の「記録（M6）」

| ID | 結果 | 要点 |
|---|---|---|
| ID-1 | 通過 | usr 6ed58430・tcal board・`GET CAL` に `wdly=7.10` |
| H-0 | 通過 | 試行の道具で全部通過。specd で 32 窓とも道具の記録との中央値の比 0.981〜1.001・形の差 ≦ 0.006。陽性対照は落ちた |
| W-1 | 通過 | 32 か所とも ch のずれ 0。陽性対照（予言 ＋1）は落ちた |
| TW | 通過 | 比の揺れ 0.0016。陽性対照（R0 512）は揺れ 0.45 で落ちた |
| WRST | 通過 | 約束を破る組は ERR・GET と対応は元のまま |
| NET | 通過 | 32 窓の 10.24 ms は ERR・16 窓は OK。陽性対照で通る |
| PS-1 | 通過 | e の窓どうしの差 −1.0〜0.0 ns。n_sum 1 の SPEC が PL のレコード（IF の昇順）と 512 本ともバイト単位で同じ。陽性対照（表を外す・並べ替えない）は落ちた |
| RATE | 通過 | 試行の道具 51.6 MB/s・55.0 %・DROP 0。specd の取得の CPU 69.5 %（線 70 %）、回し直しで 34.3 %。温度の「±1 ℃」は均し方を決めていなかったので P-13 と同じく均した値で読んだ |
| V2-b | 1 回目は不合格、**回し直しで通過** | 1 回目: 受け・miss・pl_drop は 0、**loop_slow 133（線 ≦ 5）**、109 は最初の 1 分（周の最長 348 ms）。回し直し: loop_slow 2（最初の 1 分）・p99 7.5 ms・取得の CPU 34.3 %・1 周の計 7.0 ms / 束。陽性対照で pl_drop 25,142・kgap 32 |
| V2-L | 1 回目は不合格、**回し直しで通過** | 1 回目: 受け 2 時間・miss・pl_drop は 0、VCCINT 最大 39.46 A。**loop_slow 50**（2 時間にばらけ、周の最長 28 ms）。temp20 は均すと線の内、生の読みは 70.11 ℃ が 2 回。回し直し: loop_slow 1（最初の 1 分）・p99 6.8 ms・CPU 34.1 %・VCCINT 最大 39.39 A・temp20 最大 69.12 ℃（生の読み）、後半 1 時間の 5 分平均の偏差 ≦ 0.34 ℃ |
| RING | 1 回目は 3 回のうち 1 回が不合格、**回し直しで 3 回とも通過** | 1 回目: 0.3 s の止まりの後に原因の分からない ≒ 0.5 s の止まりが重なり pl_drop 334、残る 2 回は PEAK 27.5・28.1 MB で通過。回し直し: 3 回とも pl_drop 0・PEAK 21.2 MB（線 33.6 MB） |

- **道具の誤り 2 つ**（測った後に見つけ、同じ記録で照らし直した。合格の線は変えていない）: `spw_recv_check.py --ref` が積分の長さ（道具 20.48 ms・specd の PL のダンプ 10.24 ms）を揃えていなかった（比が 0.5 に出た）。`spw_ps1.py` が utc_ns を float64 で引いて桁落ちしていた（NS 3・4 の窓だけ ±256 ns）
- **見えたこと 1（取得の CPU）**: 不合格の 3 つは、どれも取得の CPU が ≒ 70 % で余裕が無いことの現れと見ている。束の記録（`spw_c_ev_s`）が 6 割を占める。0.3 s 止まったリングを追いつく速さが ≒ 0.3 倍しかないので、PEAK が 28 MB まで上がり、ほかの止まりが重なると溢れる。tint を 1 回越える周が 2 時間で 50 回出る。V2-b の最初の 1 分の 109 回と 348 ms は、起動の後の何か（GC は RUN の中では見えなかった）。原因は確かめていない。→ 回し直しで、CPU を 34 % に下げると 3 つとも通り、RING の PEAK も 28 → 21 MB に下がった（余裕の無さという見立てと合う）。ただし最初の 1 分の 109 回・348 ms が 2 回・48 ms に減った仕組みと、1 回目の RING の 0.5 s の止まりの原因は確かめていない
- **見えたこと 2（TP のくぼみ）**: TP_JUMP が 4 ADC とも ≒ 35,000 回 / 30 分（≒ 19.5 / s）。4 ADC 共通に −0.05〜−0.17 dB・2〜8 ms のくぼみが、間隔の中央値 28.7 ms（≒ 35 Hz）で出る。判定の外。原因は調べていない
- **見えたこと 3（温度）**: RATE・V2-L の temp20 は 68 ℃ 前後で、P-13（62 ℃）より ≒ 6 ℃ 高い。VCCINT は同じ。部屋かファンの違いと見るが確かめていない
- **ディスク**: V2-L の 2 時間（≒ 178 GB）は PC の空き（85 GB）に入らないので、受けは書かずに照合だけにした
- **回し直し**（11:42〜14:20 UTC、M5c の bit のまま、ソフトは commit 808f398 の `sw/pynq/` をボードの `~/spw8-m6b` に写し sha256 で同じ、記録は `hw/bits/spw8/runs/m6b/`）:
  - **直したこと**: 1 回目の束の記録は、できた束ごとに Python が SPEC の記録を組んでリングへ入れていて、ボードで 1 本 ≒ 250 µs（リングへの書き 53 µs・C の記録の組み 50〜60 µs・残りは Python の呼び出しの重さ）。32 窓 × 毎秒 ≒ 49 束で取得の CPU の 6 割を占めていた。束ができたら C のなめ（`s45_spw_scan`）がそのまま出口の溜まりへ SPEC の記録を書き、Python は scan のたびに書いた位置をロックの中で公開するだけにした（`s45fast.c` の `sw_out`）。窓ごとの 88 B の頭の型と utc_ns の基準は Python が前もって作る。落ちの印・溜まりの端の折り返し・空きが無い・陽性対照の形・捨てる形のときは今までの Python の道に戻る。`test_spw_ring.py` の 6 で、直に書く道と Python の道が同じ (seq, バイト) と数えを出すことを、溜まりの小さい形（折り返し・空きなしで Python の道に戻る）と大きい形で確かめた（陽性対照: 頭の時刻を 1 ずらすと落ちる）。STATUS に `spw_c_out`（C が直に書いた本数）を足した
  - **ボードの 60 s**: 取得の CPU 69 → 34 %・周の p99 19 → 8 ms・SPEC 93,275 本がすべて直に書かれた
  - **回し直したもの**: ID-1・H-0（specd の形）・PS-1 の e・V2-b（＝ RATE の specd の側）とその陽性対照・RING 3 回・V2-L。H-0 の SPEC 15,680 本は、時刻と番号の外の欄の組が 1 回目と全部同じ。W-1・TW・WRST・NET・PS-1 の float32 は記録の道に関わらない（PS-1 の float32 は Python の道で測る）ので回し直していない
  - **結果**: 上の表のとおり全部通過。loop_slow は V2-b 2・V2-L 1・RING 3〜4 で、どれも最初の 1 分（≒ 48 ms の周。RING は 0.3 s の止まりの周を含む）。1 回目の RING の 0.5 s の止まりの重なりは出なかった（原因は分からないまま）
  - **温度の読み**: V2-L の後半 1 時間の平らさは RATE と同じく均した値で読んだ（5 分平均の偏差 0.34 ℃）。1 分の移動平均では 1.02 ℃ で ±1 ℃ をわずかに越える（1 分ごとに区切った平均では 0.63 ℃）。均し方を測る前に決めていなかった件は RATE の記録のとおり
- **性能評価**: [`performance/spw8/v1.0.0.md`](performance/spw8/v1.0.0.md)（回し直した結果で書いた）

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
| M5c | `spw8/m5c-usr-access` | USR_ACCESS を焼く（SAM45-Fine の M5b・2G-2 の M5） | M2〜M4 の回し直しが予言どおり（FDRI は変わらず、構成の流れが変わる）（**2026-11-04**: 上の「M5c の結果」） |
| M6 | `spw8/m6` | 判定（`test/acceptance/spw8/`）を全部通し、性能評価を書く | `docs/performance/spw8/v1.0.0.md`（**2026-11-04**: 上の「M6 の結果」） |
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
