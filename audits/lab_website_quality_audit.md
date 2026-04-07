# Lab Website Quality Audit Prompt

## Task

Perform a full quality audit of the laboratory website repository.

The goal is to evaluate the site against best practices for academic research group websites.
Analyze repository structure, site content, navigation, CI, and production deployment configuration.
Produce a detailed report.

---

## Scope of Review

Evaluate the following aspects:

1. Architecture
2. Information structure
3. Navigation
4. Content quality
5. Publication system
6. Automation
7. Performance
8. Security
9. SEO
10. Accessibility
11. Maintainability

---

## 1. Architecture Check

Verify static-site architecture.

Expected stack:
- Hugo
- GitHub Actions
- Ubuntu + Apache2 (production)
- Optional: Docker/Nginx for local verification

Check:
- Hugo configuration
- Static content structure
- CI build/deploy flow
- Absence of dynamic backend

Flag if:
- PHP present
- database dependency exists
- WordPress detected

---

## 2. Repository Structure

Expected directories:
- `site/`
- `scripts/`
- `data/`
- `.github/workflows/`
- `apache/` (if production config is versioned)

Optional local directories:
- `docker/`
- `nginx/`
- `public/` (generated build output; may be absent in a clean checkout)

Check for missing directories and document impact.

---

## 3. Content Structure

Expected content sections:
- `research/`
- `publications/`
- `members/`
- `news/`
- `projects/`
- `join/`
- `contact/`

Check:
- missing sections
- inconsistent naming
- orphan pages

---

## 4. Navigation Audit

Recommended primary navigation:
- Home
- Research
- Publications
- Members
- News
- Join

Rules:
- max 6 main menu items
- users should reach information in <= 3 clicks

Detect:
- deep navigation trees
- duplicate navigation paths

---

## 5. Publications Page Quality

Required fields:
- title
- authors
- venue/journal
- year
- pub_type (`journal` / `international-conference` / `domestic-conference` / `talk` / `others`)
- DOI or PDF

Optional (for conference papers):
- peer_reviewed (`true` / `false`)
- annote (`invited` etc. for talks)

Verify consistency and visibility.
Also verify publications can be grouped into:
- Journal
- International Conference
  - Refereed
  - Non-Refereed
  - Unspecified
- Domestic Conference
  - Refereed
  - Non-Refereed
  - Unspecified
- Others
  - `talk` は Others に集約されること
  - `pub_type=talk` かつ `annote=invited` で `Invited talk` が表示されること

Check automation assets:
- `data/publications/`
- `scripts/bibtex_to_markdown.py`
- `scripts/scholar_fetch.py`

---

## 6. Deployment Configuration Quality

Production assumptions:
- Apache2 serves generated static files from `/var/www/...`
- no direct editing on server
- deploy via CI (`rsync/scp`)

Check for:
- branch-to-environment mapping (`develop` -> staging, `main` -> production)
- Apache config validation step (`apache2ctl configtest`) in process docs/automation
- rollback readiness

---

## 7. Automation and QA

Check if repository includes:
- lightweight checks workflow
- monthly audit workflow
- publication update workflow

Expected checks:
- Hugo build
- markdown validity
- internal links
- image size threshold

---

## 8. Report Format

Output sections:
1. Site architecture summary
2. Strengths
3. Weaknesses
4. Missing features
5. Recommended improvements
6. Priority fixes

Priority levels:
- critical
- recommended
- optional

---

## Final Goal

Upgrade and maintain the website as a production-quality academic laboratory site with:
- strong research communication
- stable GitHub-centered operations
- safe Ubuntu+Apache2 production delivery
