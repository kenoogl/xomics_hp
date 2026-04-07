# Reports 運用ワークフロー

## 目的

研究室サイトの Reports ページを継続的に更新・運用するための手順を定義する。
本サイトでは「論文（Publications）」を「報告（Reports）」として扱い、会計年度（FY）単位で管理する。

対応する更新方式:

1. 手動更新
2. BibTeX を使った半自動更新

---

## 前提

本リポジトリは以下を前提とする。

- 静的サイト生成: Hugo
- コンテンツ管理: Markdown
- 報告データソース: BibTeX (`data/publications/reports-YYYY.bib`)
- 品質チェック: `scripts/validate_content.py` など

---

## ディレクトリ構成

Hugo ソースルートは `site/`。出力先は `site/content/reports/`。

```text
site/content/reports/
  FY2025/
  FY2024/
```

各レポートは1ファイル（Markdown）で管理する。

---

## 方法1: 手動更新

### Step 1: Markdown ファイルを追加

```text
site/content/reports/FY2025/wake-modeling.md
```

### Step 2: Front Matter を記述

```yaml
---
title: "Data-driven Wake Modeling using AI"
date: 2026-01-01
authors: "Kenji Ono, John Smith"
journal: "Journal of Wind Engineering"
year: "2026"
fiscal_year: "FY2025"
pub_type: "journal"
doi: "10.xxxx/xxxxx"
---

論文概要をここに記載。
```

### Step 3: ビルドと検証

```bash
make build
make up
```

---

## 方法2: BibTeX 半自動更新

ソースは `data/publications/` 配下の `reports-YYYY.bib` （YYYYは会計年度）で管理する。

### Step 1: BibTeX を更新

```text
data/publications/reports-2025.bib
```

### Step 2: 変換スクリプトを実行

```bash
python scripts/bibtex_to_markdown.py --clean
python scripts/validate_content.py
```

`bibtex_to_markdown.py` は既定で `reports-*.bib` を読み込み、ファイル名から会計年度（FY）を抽出して出力先ディレクトリを決定する。

### Step 3: サイトの更新と確認

```bash
make build
make up
```

---

## 運用上の注意

- `reports-YYYY.bib` の `YYYY` を正しく設定する（これが FY ディレクトリ名になる）。
- `pub_type` は `journal` / `international-conference` / `domestic-conference` / `talk` / `others` を使用する。
- `misc` エントリの場合、`note` フィールドの内容が掲載元として表示される。
- 会計年度（FY）ディレクトリにはビルド時に `_index.md` が自動生成される。
