#!/usr/bin/env python3
"""Lightweight Markdown validity checks.

Checks:
- File is valid UTF-8
- If file starts with YAML front matter (---), it must be closed
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check markdown validity")
    parser.add_argument("--root", default=".", help="Repository root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    md_files = sorted(root.rglob("*.md"))
    errors: list[str] = []

    for path in md_files:
        rel = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: invalid UTF-8 ({exc})")
            continue

        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            closed = any(line.strip() == "---" for line in lines[1:])
            if not closed:
                errors.append(f"{rel}: front matter is not closed")

    if errors:
        print("Markdown validity check failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Markdown validity check passed ({len(md_files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
