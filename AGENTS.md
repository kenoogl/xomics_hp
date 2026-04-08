# AGENTS.md

## Purpose

This repository is a Hugo-based laboratory website.

- Production: Ubuntu + Apache2
- Source of truth: GitHub
- Local verification: `docker/` + `nginx/` and `make` commands

Agents working in this repository should preserve the current operating model and avoid unnecessary structural churn.

## Repository Contract

- `site/`: Hugo source
- `site/content/`: Markdown content
- `site/content/research/`: Japanese research pages
- `site/content/research-en/`: English research pages
- `site/content/news/`: news items
- `site/content/publications/`: generated publication pages
- `site/static/`: images, PDFs, and other static assets
- `scripts/`: generation and validation scripts
- `docs/`: human-facing documentation
- `audits/`: LLM/Codex audit prompts
- `public/`: Hugo build output (generated locally/CI, not version-controlled)

Do not repurpose `docs/` for audit prompts. Keep audit prompts under `audits/`.

## Operating Rules

- GitHub is the only source of truth.
- Do not assume direct edits on the production server.
- Do not redesign the site structure unless the user explicitly asks for it.
- Prefer incremental changes over broad rewrites.
- Treat deployment as gated: `deploy_staging.yml` / `deploy_production.yml` are expected to run only after successful `site_checks.yml`.
- If a change affects behavior, navigation, workflows, or repository structure, update the relevant documentation in the same turn.

## Content Rules

### General

- Use kebab-case for Markdown filenames.
- Use ASCII/kebab-case for static asset filenames when possible.
- Do not manually edit files under `site/content/publications/` unless the user explicitly asks for it.
- Prefer editing source data or generator scripts over editing generated outputs.

### Japanese and English

- Japanese content is primary.
- Research pages should be maintained in Japanese and English pairs when applicable.
- English research page titles must not append `(EN)`.
- Japanese research pages should link to the English version.
- English research pages should link back to the Japanese version.
- News is operated in Japanese only unless the user explicitly wants a specific item translated.

### Writing Style

- Japanese explanatory pages should use polite `です・ます` style unless the user requests otherwise.
- Keep technical language precise and concise.
- Avoid decorative or marketing-heavy wording.
- Audit reports, review reports, and repository assessment summaries should be written in Japanese unless the user explicitly requests another language.

## Research Page Rules

- Research content lives in `site/content/research/` and `site/content/research-en/`.
- Pages intended for the homepage highlight section must include `top_highlight: true`.
- Homepage research highlights are capped at 5 items.
- Research pages should include:
  - `title`
  - `date`
  - `summary`
  - `thumbnail` when used on listing/highlight pages
- Figures should be placed under `site/static/images/`.
- If adding a new Japanese research page that corresponds to an existing English workflow pattern, create the English counterpart in the same turn unless the user says otherwise.

## News Rules

- One news item equals one Markdown file.
- News files live in `site/content/news/`.
- `date` means publication date, not event date.
- Future dates will be excluded from normal Hugo builds.
- Homepage news shows the latest 5 items as `date + excerpt`.
- `/news/` is a yearly archive and should show the body content in chronological groupings.
- PDF links in news should point to files under `site/static/`, using root-relative paths such as `/pdfs/file-name.pdf`.

## Publication Rules

- The authoritative publication BibTeX sources live under `data/publications/`.
- Managed source files are:
  - `journal.bib`
  - `intl_conf.bib`
  - `domestic_conf.bib`
  - `others.bib`
  - `generated.bib`
- Main update entrypoint: `scripts/update_publications.sh`
- Main generator: `scripts/bibtex_to_markdown.py`
- Main validation: `scripts/validate_content.py`
- Publication filenames are generated from BibTeX keys.
- BibTeX keys must be unique and ASCII-safe before regeneration.

### Publication Categories

- Supported `pub_type` values:
  - `journal`
  - `international-conference`
  - `domestic-conference`
  - `talk`
  - `others`

- `pub_type` explicitly written in BibTeX takes precedence over automatic inference.
- `talk` is displayed under `Others`.
- `annote=invited` with `pub_type=talk` should display `Invited talk`.
- `peer_reviewed` is used for conference categories.
- If `abstract`, `doi`, or `url` exists, the detail page should display them.

### Publication Editing Policy

- Prefer changing BibTeX and regenerating pages rather than editing generated Markdown by hand.
- `generated.bib` is the default output target for `scholar_fetch.py`; review and reclassify entries into the managed category files as needed.
- If generation rules are wrong, fix `scripts/bibtex_to_markdown.py`.
- After publication regeneration, run validation and build checks before considering the work complete.

## Validation Checklist

After content or layout changes, run the minimum necessary checks.

### Required for most content/layout changes

```bash
cd /Users/Daily/Development/Xomics
python scripts/validate_content.py
make build
```

### Required for publication update workflow

```bash
cd /Users/Daily/Development/Xomics
./scripts/update_publications.sh
```

### Local verification when appearance or asset delivery changed

```bash
cd /Users/Daily/Development/Xomics
make up
make ps
```

  `make ps` で `lab_web` が `Up` になっていれば、`http://localhost:8080` で確認できます。

## Documentation Update Rules

Update documentation in the same turn when changing any of the following:

- repository structure
- workflow commands
- deployment assumptions
- audit prompt locations
- content conventions
- publication pipeline behavior
- homepage selection rules

Primary documents:

- `README.md`
- `docs/specifications/spec.md`
- `docs/README.md`
- workflow-specific docs under `docs/`

Audit prompts are not documentation pages. They live under `audits/`.

## Navigation and Layout Rules

- Preserve the current top-page structure unless the user requests otherwise.
- When changing homepage sections, keep the intent clear:
  - Research: selected highlights
  - Latest Publications: links to detail pages
  - News: latest 5 excerpts
- For list pages with short items, prefer information-dense layouts over decorative cards.

## Safety Rules

- Do not edit `public/` by hand unless debugging generated output.
- Do not commit `public/`; it is a build artifact.
- Do not commit unrelated generated noise.
- Do not remove existing bilingual links without replacing them appropriately.
- Do not change URL structure casually; if a filename changes, preserve routing with `slug` when needed.

## Commit Rules

- If the user asks for commit/push, include all relevant changes for the requested task and avoid unrelated files.
- Use direct, factual commit messages.
- Do not amend prior commits unless explicitly requested.

### Shorthand

- `git-cp` means: commit the current relevant source/documentation changes and push them to `origin/main`.
- When this shorthand is used, treat it as an explicit request to perform both `git commit` and `git push`.
- Execute `git-cp` sequentially for safety:
  1. `git add`
  2. `git commit`
  3. `git push`
  Do not run commit and push in parallel.

## Audit Rules

- `audits/` contains prompts intended for LLM/Codex execution.
- Monthly full audit prompt:
  - `audits/lab_website_quality_audit.md`
- Periodic visibility audit prompt:
  - `audits/research_visibility_audit.md`
- Periodic impact audit prompt:
  - `audits/research_impact_audit.md`

When moving or renaming audit prompts, update:

- `README.md`
- `docs/README.md`
- `docs/specifications/spec.md`
- any GitHub Actions workflows that reference them
