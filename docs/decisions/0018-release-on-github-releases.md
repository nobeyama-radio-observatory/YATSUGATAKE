# 0018. .bit は git に入れず GitHub Releases に。版は 2 段

- 状態: 提案（リリースの手順と、版を .bit に焼き込む方法は proj021 と最初のリリースで決める）
- 決定日: 2026-10-08
- 根拠: study-rfsoc proj021 の README（検討事項 1）

## 背景

製品版の .bit を利用者に配る。どの .bit がどのソースから作られたかを、ファイルからも実機からも辿れる必要がある。

## 決定（案）

- **.bit・.hwh は git に入れず、GitHub Releases に添付する**。添付するもの: .bit・.hwh・ビルドログ・タイミングの要約・sha256
- **版は 2 段**
  - リポジトリ全体の版: インターフェース（IF_VER）と specd の互換性
  - bit ごとの版: bit は仕上がる時期がそれぞれ違う
- **.bit に commit を焼き込む**。候補は USR_ACCESSE2（`BITSTREAM.CONFIG.USR_ACCESS` で 32 bit。配置・配線の後に入るので配置を変えない）
- 性能評価（`docs/performance/`）はリリースのタグと 1 対 1 で結ぶ

## 理由

- .bit は大きく、ソースから再生成できる。git に入れると履歴が膨らむ
- **RTL の定数に commit を入れると、commit ごとに配置が組み替わり「同じ RTL の作り直しは WNS まで再現する」が崩れる**。USR_ACCESS なら配置に触れない
- bit ごとに版を持てば、1 本だけ直したときに他の bit の版を上げずに済む

## 見送った案

- **.bit を git LFS に入れる**: 公開リポジトリで LFS の帯域を使う。Releases で足りる
- **BUILD_TAG のような RTL の generic に commit を入れる**: 上のとおり配置が変わる

## 影響

- 決めること: USR_ACCESS の 32 bit に何を入れるか（commit の短いハッシュ ＋ 汚れの bit など）、`bits.json` の sha256 との役割分担、IF_ID の BIT_REV との関係
- 確かめること: 同じ RTL で USR_ACCESS だけ違う 2 本の WNS が一致すること
- 手順は [`../release.md`](../release.md)
