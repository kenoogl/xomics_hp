#!/usr/bin/env python3
"""Check broken internal links in generated Hugo HTML output.

Scans `public/**/*.html` and validates local href/src targets.
Only checks local links (absolute-path and relative-path).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

LINK_RE = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']")
IGNORE_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check broken internal links in public HTML")
    parser.add_argument("--public-dir", default="public", help="Path to generated public directory")
    return parser.parse_args()


def iter_html_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.html"))


def normalize_target(raw: str) -> str:
    target = raw.split("#", 1)[0].split("?", 1)[0].strip()
    return target


def resolve_target(public_dir: Path, current_file: Path, target: str) -> list[Path]:
    if target.startswith("/"):
        base = public_dir / target.lstrip("/")
    else:
        base = current_file.parent / target

    candidates: list[Path] = []
    if base.suffix:
        candidates.append(base)
    else:
        candidates.append(base)
        candidates.append(base / "index.html")
        candidates.append(base.with_suffix(".html"))
    return candidates


def main() -> int:
    args = parse_args()
    public_dir = Path(args.public_dir).resolve()

    if not public_dir.exists():
        raise SystemExit(f"Public directory not found: {public_dir}")

    html_files = iter_html_files(public_dir)
    broken: list[str] = []

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        for raw_link in LINK_RE.findall(text):
            if raw_link.startswith(IGNORE_PREFIXES):
                continue
            target = normalize_target(raw_link)
            if not target:
                continue

            candidates = resolve_target(public_dir, html_file, target)
            if any(path.exists() for path in candidates):
                continue

            rel = html_file.relative_to(public_dir)
            broken.append(f"{rel}: {raw_link}")

    if broken:
        print("Broken internal links found:")
        for item in broken:
            print(f"- {item}")
        return 1

    print(f"Internal link check passed ({len(html_files)} HTML files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
