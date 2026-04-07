# Lab Site QA Pipeline

## Goal

Implement a two-level quality monitoring system for the laboratory website.

Levels:
1. Lightweight automatic checks
2. Periodic full site audit

The system runs automatically using GitHub Actions, with Codex used for monthly deep audits.

---

## System Overview

Developer commit
↓
CI lightweight checks
↓
Site build validation
↓
Branch-based deploy (develop -> staging, main -> production)
↓
Monthly Codex audit
↓
Quality report

---

## Level 1: Lightweight Automatic Checks

Workflow file:
- `.github/workflows/site_checks.yml`

Trigger:
- On every pull request
- On push to `develop`
- On push to `main`

Checks:
- Hugo build success
- Broken internal links (`public/` HTML)
- Image size threshold (`site/static/images`, 500KB max)
- Markdown validity
- Content naming/front matter conventions

Implementation scripts:
- `scripts/check_internal_links.py`
- `scripts/check_markdown_validity.py`
- `scripts/validate_content.py`

---

## Deploy Hooks (Environment Mapping)

- `develop` push:
  - Run lightweight checks
  - `site checks` 成功後に deploy workflow が起動
  - Deploy generated `public/` to staging (`/var/www/mercury-staging`)
- `main` push:
  - Run lightweight checks
  - `site checks` 成功後に deploy workflow が起動
  - Deploy generated `public/` to production (`/var/www/html`)

Deploy transport:
- `rsync` or `scp` over SSH from GitHub Actions
- `public/` is built inside GitHub Actions and is not committed to Git.

---

## Level 2: Monthly Full Audit

Workflow file:
- `.github/workflows/site_audit.yml`

Trigger:
- Monthly schedule (`0 3 1 * *`, UTC)
- Manual dispatch

Flow:
1. Run baseline lightweight checks
2. Execute Codex audit prompt based on `audits/lab_website_quality_audit.md`
3. Save report to `reports/monthly_site_audit_YYYY-MM-DD.md`
4. Upload report artifact
5. Commit report back to repository

Codex prompt:
- "Read the repository and execute the instructions in `audits/lab_website_quality_audit.md`. Output a full audit report in markdown."

Requirements:
- GitHub secret `OPENAI_API_KEY` must be configured for Codex execution.
- If secret or CLI is unavailable, workflow writes a fallback report explaining the skip reason.

---

## Priority Levels for Findings

- critical
- recommended
- optional

---

## Typical Lab Maintenance Flow

paper accepted
↓
Google Scholar update
↓
publication automation
↓
site update (develop)
↓
CI checks pass
↓
staging check
↓
main merge
↓
production deploy
↓
monthly full audit

---

## Benefits

- Site reliability
- Consistent structure
- Automatic error detection
- Safe release path via staging
- Long-term maintainability
