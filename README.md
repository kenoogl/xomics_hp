# Pan-Omics Data-Driven Innovation Center Website

Hugo で構築した研究室向け静的Webサイトです。  
本番公開は **Ubuntu + Apache2**、GitHub を唯一の正本として運用します。

## 運用方針

- GitHub を唯一の正本にする
- 本番サーバ（Ubuntu）で直接編集しない
- 変更は必ず PR / merge 経由で反映する
- 本番前にローカルまたは staging で確認する

## 構成

- `site/`: Hugo ソース（テーマ、レイアウト、コンテンツ、静的アセット）
- `public/`: Hugo のビルド出力（ローカル/CI生成物。Git 管理しない）
- `scripts/`: 自動化/検証スクリプト
- `data/`: BibTeX などのデータソース
- `.github/workflows/`: CI/CD
- `apache/`: Apache 本番設定（VirtualHost など）
- `docker/`, `nginx/`: ローカル検証向け（任意）

## ローカル確認（推奨）

```bash
cd /Users/Daily/Development/Xomics
make build
make up
make ps
```

確認URL: [http://localhost:8080](http://localhost:8080)

停止:

```bash
cd /Users/Daily/Development/Xomics
make down
```

## デプロイ方針（本番）

- `develop` への push: `site_checks.yml` 実行後、成功時のみ staging 配信
- `main` への push: `site_checks.yml` 実行後、成功時のみ production 配信
- 配信先は Ubuntu + Apache2（`/var/www/...`）
- 配信方式は `rsync`/`scp`（GitHub Actions 実行）
- `public/` は GitHub Actions 上でビルドし、配信用 artifact として扱う

## コンテンツ更新フロー

1. `site/content/` の Markdown を編集
2. `make build && make up && make ps` で確認
3. `feature/*` で commit / push
4. PR を `develop` へマージ
5. staging 確認後、`main` へマージ
6. production 反映

## 日英運用方針

- `About`、および主要な固定ページは日英対応を基本とする
- `News`、`Reports` は日本語のみで運用する
- 国際向けに告知したい重要ニュースのみ、必要に応じて個別に英語化する

## News 運用

- FR-007: （欠番）
- FR-008: （欠番）
- `/news/` では年ごとの時系列アーカイブとして本文を表示する
- `title` は管理用メタデータとして保持し、トップページでは本文中心に見せる
- `date` はイベント開催日ではなく、ニュースを公開した日を入れる
- 未来日付を入れると Hugo の通常ビルドでは除外され、トップページや `/news/` に表示されない

詳細: [docs/specifications/spec.md](./docs/specifications/spec.md)

## Reports メンテナンス

標準の更新方法は BibTeX ベースです。会計年度（FY）ごとに分類して管理します。

```bash
cd /Users/Daily/Development/Xomics
./scripts/update_publications.sh  # reports を更新してページ反映
```

- reports Markdown のファイル名は BibTeX key を元に生成されます
- BibTeX key が重複している場合、変換はエラーで停止します
- BibTeX key は ASCII ベースで一意に管理してください
- BibTeX ソースは `data/publications/` 配下の `reports-YYYY.bib` で管理します
  - `YYYY` は会計年度（例: 2025）を指します
  - 実行すると `site/content/reports/FY2025/` のように出力されます

- 手動更新・分類ルール・表示ルール: [reports_workflow.md](./docs/procedures/reports_workflow.md)
- 仕様上の要件: [spec.md](./docs/specifications/spec.md)

### 更新フロー

```bash
python scripts/bibtex_to_markdown.py --clean
python scripts/validate_content.py
make build
make up
```

## QA パイプライン

- 軽量チェック: `.github/workflows/site_checks.yml`
  - Hugo build
  - Markdown validity
  - 内部リンク
  - 画像サイズ上限（500KB）
- 月次監査: `.github/workflows/site_audit.yml`
  - `reports/monthly_site_audit_YYYY-MM-DD.md` を生成
- 半年ごと監査（手動）
  - `audits/research_visibility_audit.md`
  - `audits/research_impact_audit.md`

監査用の LLM プロンプトは `docs/` ではなく `audits/` に分離して管理します。

詳細:
- [lab_site_qa_pipeline.md](/Users/Daily/Development/Xomics/docs/operations/lab_site_qa_pipeline.md)
- [docs/README.md](/Users/Daily/Development/Xomics/docs/README.md)

## 補足

リポジトリには `docker/` と `nginx/` がありますが、これは主にローカル検証用途です。  
本番配信は Ubuntu + Apache2 を基準に運用します。

## トラブルシュート（ローカル確認）

`make up` 実行時に以下のようなエラーが出る場合:

`failed to connect to the docker API at unix:///Users/.../.colima/default/docker.sock`

Colima（Dockerデーモン）が停止しています。以下で復旧します。

```bash
colima start
make up
make ps
```

`make ps` で `lab_web` が `Up` になっていれば、`http://localhost:8080` で確認できます。
