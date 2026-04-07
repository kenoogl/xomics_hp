# Laboratory Website System Specification

## 1. Purpose

本仕様は、研究室Webサイト運用システムの要件・構成・運用フローを定義する。  
対象システムは以下を満たす。

- 静的サイトとして安全かつ軽量に公開できること
- 論文情報を手動/半自動/自動で更新できること
- 継続的品質管理（軽量チェック + 月次監査）を自動実行できること
- 長期保守しやすい構成であること

---

## 2. Scope

対象リポジトリ: `lab-website`

含む範囲:
- Hugoコンテンツとテーマ
- Apache2公開設定
- Reports自動化（BibTeX -> Markdown）
- CI/CD（GitHub Actions）
- QAパイプライン（軽量チェック / 月次監査）

除外範囲:
- 動的バックエンド（DB, APIサーバ, PHP, WordPress）

---

## 3. System Architecture

### 3.1 Stack
- Static site generator: Hugo
- Web server (production): Apache2 on Ubuntu
- Source of truth: GitHub
- CI/CD: GitHub Actions
- Audit engine: Codex (monthly deep audit)
- Optional local runtime: Docker/Nginx

### 3.2 High-level flow
1. 編集者が `site/content` を更新
2. Hugoで `public/` を生成
3. CIで品質チェック
4. `site_checks.yml` 成功後に `develop` は staging、`main` は production へ配信
5. 月次でCodex監査レポートを生成

### 3.3 Directory contract
- `site/` : Hugo source
- `public/` : Hugo build output (generated locally/CI, not version-controlled)
- `data/` : Reports source data (`publications/`)
- `scripts/` : automation/validation scripts
- `.github/workflows/` : CI workflows
- `reports/` : monthly audit reports (generated)
- `apache/` : Apache VirtualHost / deploy-related configs
- `docker/`, `nginx/` : optional local verification configs

---

## 4. Functional Requirements

### 4.1 Site content management
- FR-001: コンテンツは `site/content/*` のMarkdownで管理する。
- FR-002: Hugo buildは `public/` に出力する。
- FR-002a: `public/` は生成物であり、Git 管理対象にしない。
- FR-003: build時は古い生成物を残さない（`--cleanDestinationDir`）。
- FR-004: News は `1ニュース = 1 Markdown` として `site/content/news/` で管理する。
- FR-005: トップページの News セクションは最新5件を `日付 + 本文抜粋` で表示する。
- FR-006: `/news/` は年ごとの時系列アーカイブとし、各ニュースの本文を表示する。
- FR-007: (将来用)
- FR-008: (将来用)
- FR-009: トップページの Latest Reports は最新3件を表示し、各論文タイトルは詳細ページへのリンクを持つ。
- FR-010: トップページのフッターには、ビルド時点の最終更新日時を日本時間で表示する。
- FR-011: トップページの研究室名は、研究室紹介ページ（日本語 `/about/`）へのリンクを持つ。

### 4.2 Report management
- FR-101: Reportsは会計年度（FY）別に管理する（`site/content/reports/FY<year>/`）。
- FR-102: BibTeXソースは `data/publications/` 配下で管理し、`reports-YYYY.bib` を主なデータソースとする。
- FR-103: `scripts/bibtex_to_markdown.py` は BibTeX を Hugo Markdown に変換する。
- FR-103a: report Markdown のファイル名は BibTeX key を元に生成する。
- FR-103b: BibTeX key が重複している場合、変換はエラーで停止する。
- FR-105: 各reportに `pub_type` を保持し、`journal` / `international-conference` / `domestic-conference` / `talk` / `others` を扱えること。表示上の venue として `note` フィールドも活用する。
- FR-108: Reportsトップ（`/reports/`）は会計年度（FY）一覧ページとする。
- FR-109: 各年度別レポート一覧ページ（`/reports/fy2025/` など）は日付降順に一覧を表示する。
- FR-111: report詳細ページでは `doi` / `doi_url`（または `url`）が存在する場合に表示する。

### 4.3 Validation and QA
- FR-201: `scripts/validate_content.py` は命名規約・Front Matter整合を検証する。
- FR-202: `scripts/check_markdown_validity.py` はMarkdown妥当性（UTF-8/Front Matter閉鎖）を検証する。
- FR-203: `scripts/check_internal_links.py` は生成HTML内の内部リンク切れを検出する。
- FR-204: 画像サイズ上限は 500KB とし、超過はCI失敗とする。

### 4.4 Deployment
- FR-301: Apache2は `public/` の静的ファイルのみを配信する。
- FR-302: production の `DocumentRoot` は `/var/www/html` を基準とする。
- FR-303: `develop` は staging、`main` は production へ GitHub Actions から rsync/scp で配信する。
- FR-304: サーバ側反映前に `apache2ctl configtest` を実行し、成功時のみ reload する。
- FR-305: `deploy_staging.yml` と `deploy_production.yml` は `site_checks.yml` 成功後にのみ実行する。

### 4.5 CI/CD workflows
- FR-401: `update_publications.yml` は weekly で publication更新を実行する。
- FR-401a: publication 自動更新 workflow は生成された `public/` を commit しない。
- FR-402: `site_checks.yml` は PR および develop/main push で軽量品質チェックを実行する。
- FR-403: `site_audit.yml` は monthly でフル監査を実行する。
- FR-404: 月次監査レポートは `reports/monthly_site_audit_YYYY-MM-DD.md` を出力する。
- FR-405: deploy workflows は `workflow_run` により `site checks` 完了イベントを受け、成功した branch のみ配信する。

---

## 5. Non-Functional Requirements

### 5.1 Security
- NFR-SEC-001: 動的バックエンドを導入しない。
- NFR-SEC-002: Apache設定は `sites-available` 管理、`apache2ctl configtest` を必須化する。
- NFR-SEC-003: 秘密情報はリポジトリに保存せず GitHub Secrets を使用する。
- NFR-SEC-004: 本番サーバでの直接編集を禁止する。

### 5.2 Maintainability
- NFR-MNT-001: 命名規約を自動検証で強制する。
- NFR-MNT-002: ドキュメントは実装と同期する。
- NFR-MNT-003: 主要運用コマンドをMakefileに集約する。

### 5.3 Performance
- NFR-PERF-001: サイトは軽量静的配信を維持する。
- NFR-PERF-002: 画像サイズ上限 500KB を継続監視する。

### 5.4 Reliability
- NFR-REL-001: CI軽量チェックを通過しない変更は develop/main 品質基準を満たさない。
- NFR-REL-002: 月次監査で中長期的な構造劣化を検知する。

---

## 6. Content Conventions

### 6.1 Naming
- `site/content/*.md`: kebab-case
- `site/content/news/*.md`: kebab-case
- publication の生成ファイル名は BibTeX key ベースの kebab-case とする

### 6.2 (将来用)

### 6.3 Publications metadata
各publicationページは以下を持つこと。
- `title`
- `date`
- `authors`
- `journal`（または同等のvenue）
- `year`
- `pub_type`（`journal` / `international-conference` / `domestic-conference` / `talk` / `others`）
- `peer_reviewed`（任意、会議論文向け。`true` / `false`）
- `annote`（任意、`talk` の補助属性。`invited` など）
- `doi` または `doi_url`（推奨）

### 6.4 Year consistency
- reportの `year`（発行年）は所属ディレクトリ `FY<year>`（会計年度）と概ね一致すること（年度またぎは許容）。
- `date` は YYYY-MM-DD 形式とする。

---

## 7. Operational Workflows

### 7.1 Local development
1. `make build`
2. `make up`
3. `make ps`
4. ブラウザで `http://127.0.0.1` を確認
5. 必要に応じて補助的に `cd site && hugo server` を使う

### 7.2 Manual publication update
1. `site/content/publications/<year>/` にMarkdown追加
2. `make check`
3. PR経由で `develop` へ反映

### 7.3 Semi-automatic publication update
1. `data/publications/` 更新
2. `python scripts/bibtex_to_markdown.py --clean`
3. `python scripts/validate_content.py`
4. `make check`

### 7.4 Fully automatic publication update
1. GitHub Actions (`update_publications.yml`) が定期実行
2. Scholar fetch -> BibTeX convert -> validation -> build
3. 変更があれば自動commit/push
4. `develop` 経由で staging 確認後、`main` で production 反映

### 7.5 Two-level QA pipeline
- Level 1: `site_checks.yml`（PR/develop/main）
- Level 2: `site_audit.yml`（monthly + manual）

---

## 8. CI Workflow Specifications

### 8.1 update_publications.yml
- Trigger: weekly schedule + manual dispatch
- Steps:
  - Python dependencies install
  - Scholar fetch（`SCHOLAR_AUTHOR_ID` 利用）
  - BibTeX->Markdown変換
  - content validation
  - Hugo build
  - commit/push

### 8.2 site_checks.yml
- Trigger: pull_request, push(develop/main)
- Checks:
  - content validation
  - Hugo build
  - markdown validity
  - internal links
  - image size threshold

### 8.3 deploy_staging.yml / deploy_production.yml
- Trigger: `workflow_run` (`site checks` completed)
- Branch gate:
  - `develop` -> staging
  - `main` -> production
- Precondition:
  - `github.event.workflow_run.conclusion == 'success'`
- Steps:
  - checkout target commit (`head_sha`)
  - install Hugo
  - build `public/`
  - deploy over SSH
  - `apache2ctl configtest` + reload

### 8.4 site_audit.yml
- Trigger: monthly schedule + manual dispatch
- Steps:
  - baseline lightweight checks
  - Codex deep audit (`audits/lab_website_quality_audit.md` 指示)
  - report artifact upload
  - report commit/push
- Secret dependency:
  - `OPENAI_API_KEY`（未設定時はスキップ理由つきレポート生成）
- Audit prompts:
  - LLM に渡す監査プロンプトは `audits/` 配下で管理する

---

## 9. Interfaces and Dependencies

### 9.1 Required tools
- Hugo (extended)
- Python 3.x
- rsync or scp (for deployment)
- Apache2 (Ubuntu production)

### 9.2 Python dependencies
- `scholarly`
- `bibtexparser`

### 9.3 GitHub secrets
- `SCHOLAR_AUTHOR_ID`（publication自動取得用）
- `OPENAI_API_KEY`（monthly Codex audit用）
- deployment credentials/secrets（SSH key, host, user）

---

## 10. Acceptance Criteria

- AC-001: `make check` が成功する。
- AC-002: `site_checks.yml` が develop/main/PR で成功する。
- AC-002a: `deploy_staging.yml` / `deploy_production.yml` は `site_checks.yml` 成功時のみ実行される。
- AC-003: `update_publications.yml` が手動実行で成功する。
- AC-004: `site_audit.yml` が月次実行でレポートを生成する。
- AC-005: publicationページが年別/kebab-case規約を満たす。
- AC-006: 内部リンク切れが0件である。
- AC-007: `site/static/images` に 500KB 超過ファイルがない。

---

## 11. Out of Scope / Future Enhancements

- メンバー詳細スキーマ（写真・研究関心の必須化）
- HTML validator追加（QA強化）
- SEO拡張（OGP/Twitter/JSON-LD/canonical）
- Apache TLS/HSTS hardening

---

## 12. Reference Documents

- `README.md`
- `docs/procedures/DEPLOY_CHECKLIST.md`
- `docs/procedures/publications_workflow.md`
- `docs/procedures/scholar_to_website_pipeline.md`
- `docs/operations/lab_site_qa_pipeline.md`
- `audits/lab_website_quality_audit.md`
