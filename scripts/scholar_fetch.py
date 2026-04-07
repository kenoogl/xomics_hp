#!/usr/bin/env python3
"""Fetch publications from Google Scholar and export a BibTeX file.

Usage:
  python scripts/scholar_fetch.py --author-id <SCHOLAR_ID>

The author id can also be provided via SCHOLAR_AUTHOR_ID environment variable.
"""

from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path

from scholarly import scholarly


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Google Scholar publications to BibTeX")
    parser.add_argument("--author-id", default=os.getenv("SCHOLAR_AUTHOR_ID"), help="Google Scholar author id")
    parser.add_argument(
        "--author-name",
        default=os.getenv("SCHOLAR_AUTHOR_NAME"),
        help="Author name query if author-id is unavailable",
    )
    parser.add_argument("--output", default="data/publications/generated.bib", help="Output BibTeX file path")
    parser.add_argument("--max-pubs", type=int, default=0, help="Maximum number of publications to fetch (0: no limit)")
    parser.add_argument("--min-year", type=int, default=0, help="Skip publications older than this year (0: disabled)")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay seconds between publication fetches")
    parser.add_argument("--retries", type=int, default=3, help="Retry count for Scholar API calls")
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="Continue when a single publication fetch fails",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow writing an empty BibTeX output when no publication is fetched",
    )
    parser.add_argument("--verbose", action="store_true", help="Print progress logs")
    return parser.parse_args()


def _make_key(title: str, year: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "_" for ch in title).strip("_")
    compact = "_".join(part for part in base.split("_") if part)
    short = compact[:60] if compact else "untitled"
    return f"{short}_{year}" if year else short


def _sanitize_bib_value(text: str) -> str:
    return text.replace("\n", " ").replace("{", "").replace("}", "").strip()


def _extract_doi(text: str) -> str:
    m = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", text or "")
    return m.group(1) if m else ""


def _retry_call(fn, retries: int):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < retries:
                time.sleep(min(2.0, 0.4 * attempt))
    raise RuntimeError(f"Scholar API call failed after {retries} attempts: {last_err}") from last_err


def _resolve_author(args: argparse.Namespace) -> dict:
    if args.author_id:
        return _retry_call(lambda: scholarly.search_author_id(args.author_id), args.retries)

    if args.author_name:
        iterator = scholarly.search_author(args.author_name)
        try:
            return next(iterator)
        except StopIteration as exc:
            raise RuntimeError(f"Author not found by name: {args.author_name}") from exc

    raise RuntimeError("Missing author identity. Use --author-id or --author-name (or env vars).")


def _parse_year(value: str) -> int:
    s = str(value or "").strip()
    return int(s) if s.isdigit() else 0


def _to_bibtex_entry(pub: dict) -> str:
    bib = pub.get("bib", {})
    title = _sanitize_bib_value(bib.get("title", ""))
    authors = _sanitize_bib_value(bib.get("author", ""))
    year = str(_parse_year(bib.get("pub_year", "")) or "").strip()
    venue = _sanitize_bib_value(bib.get("venue", ""))
    pub_url = str(pub.get("pub_url", "")).strip()
    doi = _extract_doi(bib.get("doi", "")) or _extract_doi(pub_url)

    key = _make_key(title, year)
    entry_type = "inproceedings" if "conference" in venue.lower() or "workshop" in venue.lower() else "article"

    fields = [
        f"@{entry_type}{{{key},",
        f"  title={{{title}}},",
        f"  author={{{authors}}},",
    ]
    if venue:
        if entry_type == "inproceedings":
            fields.append(f"  booktitle={{{venue}}},")
        else:
            fields.append(f"  journal={{{venue}}},")
    if year:
        fields.append(f"  year={{{year}}},")
    if doi:
        fields.append(f"  doi={{{doi}}},")
        fields.append(f"  url={{https://doi.org/{doi}}},")
    elif pub_url:
        fields.append(f"  url={{{pub_url}}},")
    fields.append("}")
    return "\n".join(fields)


def main() -> int:
    args = parse_args()
    author = _resolve_author(args)
    author = _retry_call(lambda: scholarly.fill(author), args.retries)

    pubs = author.get("publications", [])
    if args.verbose:
        print(f"Found {len(pubs)} publications in Scholar profile.")

    entries: list[str] = []
    used_keys: set[str] = set()
    for i, pub in enumerate(pubs, start=1):
        try:
            filled = _retry_call(lambda: scholarly.fill(pub), args.retries)
            year = _parse_year(filled.get("bib", {}).get("pub_year", ""))
            if args.min_year and year and year < args.min_year:
                continue

            entry = _to_bibtex_entry(filled)
            key_line = entry.splitlines()[0]
            key = key_line.split("{", 1)[1].rstrip(",")
            if key in used_keys:
                continue
            used_keys.add(key)
            entries.append(entry)

            if args.verbose:
                title = filled.get("bib", {}).get("title", "").strip()
                print(f"[{i}/{len(pubs)}] fetched: {title}")
        except Exception as exc:  # noqa: BLE001
            if not args.skip_errors:
                raise SystemExit(f"Failed to fetch publication #{i}: {exc}") from exc
            if args.verbose:
                print(f"[{i}/{len(pubs)}] skipped due to error: {exc}")

        if args.max_pubs > 0 and len(entries) >= args.max_pubs:
            break
        if args.delay > 0:
            time.sleep(args.delay)

    if not entries and not args.allow_empty:
        raise SystemExit(
            "No publications were fetched. Use --allow-empty to write an empty file, "
            "or check --author-id/--author-name."
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
