# Scholar 連携パイプライン

## 目的

Google Scholar 由来の論文情報を使って、研究室サイトの Publications を自動更新する。

パイプライン:

Google Scholar -> BibTeX -> Markdown -> Hugo -> Website

---

## システム構成

構成要素:

1. Google Scholar（論文情報ソース）
2. BibTeX データベース
3. Python スクリプト
4. Hugo 静的サイト
5. GitHub Actions（Ubuntu + Apache2 への配信）

全体フロー:

```text
Scholar
  ↓
BibTeX
  ↓
Python 変換
  ↓
Markdown（site/content/publications）
  ↓
Hugo build（public/ を生成）
  ↓
Ubuntu + Apache2 へ配信
  ↓
公開サイト
```

---

## リポジトリ構成

```text
lab-website/

site/
  content/publications/

data/
  publications/
    journal.bib
    intl_conf.bib
    domestic_conf.bib
    others.bib
    generated.bib

scripts/
  scholar_fetch.py
  bibtex_to_markdown.py
  validate_content.py

.github/workflows/
  update_publications.yml
```

---

## Step 1: Google Scholar から取得

使用ライブラリ:

- `scholarly`

インストール:

```bash
pip install scholarly
```

実行例:

```bash
python scripts/scholar_fetch.py --author-id "<YOUR_SCHOLAR_ID>" --output data/publications/generated.bib
```

出力:

- `data/publications/generated.bib`

---

## Step 2: BibTeX を Hugo Markdown に変換

実行:

```bash
pip install bibtexparser
python scripts/bibtex_to_markdown.py --clean
python scripts/validate_content.py
```

この変換で publication の `pub_type` も自動付与される。

- BibTeX に `pub_type` が明示されている場合は、その値を最優先で採用する。
- `journal`
- `international-conference`
- `domestic-conference`
- `talk`
- `others`

`talk` は公開ページでは `Others` に集約表示される。
`pub_type=talk` で `annote=invited` の場合は、一覧と詳細で `Invited talk` を表示する。

`international-conference` / `domestic-conference` の場合は `peer_reviewed` も自動判定される（`true` / `false` / 未設定）。

- 明示値: `peer_reviewed`, `peerreviewed`, `refereed`, `reviewed`
- キーワード推定: `note`, `keywords`（例: `non-refereed`, `査読なし`）
- Bibファイル名推定: `*_refereed.bib`, `*_non_refereed.bib`

国内会議判定では、`journal` / `booktitle` / `author` に日本語が含まれる場合を `domestic-conference` とする。

出力例:

- `site/content/publications/2026/wake-modeling.md`

---

## Step 3: Hugo ビルド

実行:

```bash
cd site
hugo --destination ../public --cleanDestinationDir
```

出力:

- `public/`（build artifact。Git 管理しない）

---

## Step 4: Ubuntu + Apache2 へデプロイ

生成済み静的ファイルをサーバに反映する。

```text
GitHub Actions -> rsync/scp -> /var/www/mercury-staging（develop）
GitHub Actions -> rsync/scp -> /var/www/html（main）
```

公開先:

- Staging: `http://staging.mercury.cc.kyushu-u.ac.jp`
- Production: `http://mercury.cc.kyushu-u.ac.jp`

---

## Step 5: GitHub Actions 自動化

対象 workflow:

- `.github/workflows/update_publications.yml`

主要処理:

1. Python 依存をインストール（`scholarly`, `bibtexparser`）
2. Scholar データ取得（`SCHOLAR_AUTHOR_ID`）
3. BibTeX -> Markdown 変換
4. content validation
5. Hugo build
6. `data/publications/` と `site/content/publications/` を commit/push

---

## Step 6: 品質ゲート

publication 同期後に、以下の品質チェックを実行する。

- `.github/workflows/site_checks.yml`
  - Hugo build
  - content validation
  - markdown validity
  - internal link checks
  - image size threshold（500KB）
- `.github/workflows/site_audit.yml`
  - 月次フル監査
  - `audits/lab_website_quality_audit.md` ベースの深掘り監査

---

## 運用サマリ

週次運用:

1. Scholar から論文情報を取得
2. BibTeX を更新
3. Markdown を再生成
4. content 検証と Hugo build
5. 変更を commit/push
6. ブランチ方針に従って配信（develop/main）

---

## メリット

```text
Scholar が更新される
  ↓
サイトの Publications も更新される
```

- 手動更新コストの削減
- 更新漏れの低減
- staging を経由した安全な反映

---

## 拡張案

- DOI 抽出ロジックの強化
- PDF リンク自動付与
- 引用数（citation）連携
- 研究トピック自動タグ付け
