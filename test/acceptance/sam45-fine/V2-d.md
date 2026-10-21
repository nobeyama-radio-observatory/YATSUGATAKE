# V2-d — LOAD で bit を往復し、取得の起こし直しと ID・usr が切り替わる

- **前提**: 共通の前提。specd（ボードで `python3 specd.py --clkin 0 --ref 10 --bits bits.json`、制御 PC から）。配線 N。`bits.json` に 2 件以上: 既定の bit（`sam45-fine`、判定する bit）と、往復の相手（`m4`: YATSUGATAKE の M4 の bit `../sam45-fine-m4/proj021.bit`、USR_ACCESS を焼いていない、道具は同じ `pydir`）。どちらも `sha256` を書く
- **手順**:

```bash
python3 specrecv.py --host $B --out v2d.s45 --seconds 300 --json v2d.json &
python3 specctl.py --host $B BITS ID "SEND ON"
python3 specctl.py --host $B "LOAD bit=m4" ID STATUS "START n=50"
sleep 5
python3 specctl.py --host $B "LOAD bit=sam45-fine" ID STATUS "START n=50"
wait
```

- **合格**（測る前に決めた条件。YATSUGATAKE M6、2026-10-17）:
  - LOAD 1 回 ≦ 30 s。EVENT LOAD 2 個で、sha256 が相手の bit・判定する bit の値（bits.json と同じ）
  - 相手（`m4`）のとき: ID が adc_id 02020301・time_id 02020302、**usr `none`**、time_ok=1
  - 戻ったとき: ID が同じ adc_id・time_id、**usr が判定する bit の USR_ACCESS**（M5b の bit では `8eba3480`）、time_ok=1、STATUS に pl_*（pl_drop・pl_crc 0）、START の EVENT に proto 2・fmt f32・read ring・`ids.usr`
  - どの START も STOP は「n に達した」・8 窓 × 50・miss 0、TP の anch_dev 0・gap 0
  - 受け側: SPEC 800（2 回 × 8 窓 × 50）・**版 2 だけ**、CRC・欠け・説明のない欠け・dup・kgap・tdev・tp_gap 0、照合 通過
  - **見ないこと**: 版をまたぐ往復（s45proto 版 1 ↔ 2）。製品に版 1 の bit が無いため。版 1 ↔ 2 は proj021 で通過した記録（下）に頼る。2 本目の製品の bit ができたら、それを相手にして ID の切り替えも見る
- **陽性対照**: usr が `none` ↔ USR_ACCESS と切り替わること自体（同じ ID の 2 本の bit を、specd が本当に載せ替えた証拠）。`bits.json` の `sha256` を 1 文字変えた LOAD が `ERR LOAD … sha256 が bits.json と違う` で止まり、元の bit のまま動くこと
- **記録**: **YATSUGATAKE M6 で通過（2026-10-17、M5b の bit `ed6bcf78…`・usr 8eba3480、`~/m2/m6/v2d.txt`・`v2d.json`、相手 `m4`）**: LOAD 20.6・21.3 s、usr none → 8eba3480、ID は同じ、2 回の START とも 8 窓 × 50・miss 0、START の中の SPEC 400 ＋ 400・版 2 だけ・欠け 0・照合 通過。**測った後の注**: 受けた全体は SPEC 832。頭の 32 個は直前の運転（PS-2）の受けが閉じてから STOP までに溜まった記録で、次につないだ受け手に送られた（seq は受け手をまたいで欠けずに続く）。前に運転があった specd で回すときは、START ごとに数える。陽性対照（`v2d_posctl.txt`）: sha256 を変えた bits.json で `ERR LOAD m4 の sha256 が bits.json と違う`、ID は usr 8eba3480 のまま。 proj021（study-rfsoc）の判定では相手を proj020（版 1）にしていた: **最終の bit で通過（2026-10-14、2 回目、`v2d`、86fe33b の specd）**: SPEC 800・版 {1: 570, 2: 608}・欠け 0・照合 通過、proj020 の STATUS が `tp_jump=-` で答えた、LOAD 20.3・20.4 s。1 回目 NG: 何も受けていない specrecv が LOAD の間に 10 s で切られ、proj020 のときの STATUS が KeyError（どちらも specd の不具合、86fe33b で直した）。ID の切り替え・START n=50 × 2（8 窓 × 50・miss 0）・版 1 の記録は出た。2-3d の bit で通過（2026-10-13、LOAD 17.4〜20.8 s）
