# 0019. ライセンスは BSD-3-Clause、著作権者は国立天文台

- 状態: 採用
- 決定日: 2026-10-08
- 根拠: study-rfsoc の LICENSE・README（ライセンス）

## 決定

- **BSD 3-Clause License**。著作権者は National Astronomical Observatory of Japan
- 各ソースファイルに `SPDX-License-Identifier: BSD-3-Clause` を書き、著作権者の表記は `LICENSE` の 1 か所にだけ持つ

## 理由

- study-rfsoc と同じにして、移植するコードの由来とライセンスを一致させる
- 土台の PYNQ が BSD-3-Clause で、条件が揃う

## 影響

- 第 3 条により、書面の許可なく著作権者・貢献者の名前を派生物の推奨や販促に使えない
