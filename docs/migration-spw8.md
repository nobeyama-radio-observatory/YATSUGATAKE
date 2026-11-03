# study-rfsoc からの移植計画（SpW8）

- 状態: **M0**（2026-11-03、ブランチ `spw8/m0-map`）。置き場所の表・`hw/common/` との違い・移植元の bit を数え、判定を `test/acceptance/spw8/` に書き起こした
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

### M3 の心配（M3 の前に書く）

- **WNS +0.016 ns は、これまで移した bit で最も小さい**（2G-1-Fast +0.025・2G-4 +0.047・2G-2 +0.074）。ただし SAM45-Fine から 2G-2 まで、ディレクトリだけ違う作り直しで構成データまで同じだった。同じになれば WNS も小数 6 桁まで同じ
- **負に落ちたら RTL も制約も戦略も直さずに止め、決め直す**
- 上の「ビルドは commit の前の作業ツリーから」: FDRI が違ったら、まず P-11 の直しが入っていたかを疑う（e8ff602 の `pfb64_core.v` で proj032 を作り直して FDRI を比べる）。`hw/common/` の 7 個（決めること 2）と切り分けるため、作り直しは 1 つずつ
- `.hwh` は TIMESTAMP と hex・vh の絶対パスが違うはず（2G-2 の M3 と同じ）

## 手順

| 手順 | ブランチ | SpW8 ですること | 合格 |
|---|---|---|---|
| M0 | `spw8/m0-map` | 置き場所の表（この文書と付録）・始める条件・`hw/common/` との違いの数え・判定の書き起こし | 全ファイルに行き先がある・始める条件が全部 [x] |
| S | `spw8/spec` | ADR 0028（決め 1・2）。`interface.md` の WRST_T に「bit ごとに下限があり、短い値は下限に切り上げる（SpW8 は 8 クロック）」、specd の SpW の窓のキーは論理の窓（SET は 1 コアの組をまとめて受け、計画できなければ組ごと断る・STATUS に対応・受け側へのレコードも論理の番号）、`bits.md` の SpW8 の行（b5、ネットワークの tint は 20.48 ms から） | 文書だけ。M1〜M3 と並べて進めてよい |
| M1 | `spw8/m1-place` | 表の行き先に置き、パスと名前（`spw8_coef.json`）だけを直す | 違う行はすべてパスの行か名前の行。在ってはいけない側の照合 |
| — | `spw8/sim-targets` | 上の「sim の組」を Makefile の目標に書き起こす | — |
| M2 | 同上 | sim を全部回し、proj032-m0 と並べる | 全部通過し、**出力がバイト単位で同じ**。陽性対照が落ちる |
| M3 | `spw8/m3-build` | ビルド（`-1`、**PEPRPO**） | **FDRI が移植元と同じ**（`de7e9d88…3225`）。WNS / WHS が小数 6 桁まで同じ（+0.015935 / +0.009527） |
| M4 | `spw8/m4-board` | 実機の短い回帰（`hw/bits/spw8/pynq/spw_b5.py`） | ID・`--cfg b5 --ng 10`（20.48 ms）の全部通過・`--fast --ng 5`（10.24 ms × 32 窓）の DROP 0・`--tone` の CW の ch が P-9・P-13・P-13b と同じ |
| M5a | `spw8/m5a-delay-table` | **決め 3**: `timebase.WIN_DELAY_BEATS` を (BIT_KIND, BIT_REV) の表にし、SpW8 rev 10 の D(NS) を小数 2 桁で入れる。`timing.md` の残り（91 行目）を同じ PR で閉じる | SAM45-Fine の値が変わらない（test_cal_b・s45v2c）。(7, 10) が引ける。表に無い組は「未較正」 |
| M5b | `spw8/m5b-specd` | **決め 2**: specd に SpW Backend（spwplan で論理の窓 → 流れ s・SET は組ごと・STATUS に対応・レコードを論理の番号に・C の読み手 `--fast-ring` の f32 版・ネットワークの 10.24 ms を断る） | PL なしの試験（`test_fake.sh`。PSPLIT の無い bit では割り当てが恒等で振る舞いが今と同じ）と、実機で W-1・TW・WRST・NET |
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
