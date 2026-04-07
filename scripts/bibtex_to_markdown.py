#!/usr/bin/env python3
"""Convert BibTeX entries into Hugo publication markdown files.

Default inputs:
  data/publications/reports-*.bib
Output:
  site/content/reports/FY<Year>/<bibtex-key>.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import bibtexparser


MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert BibTeX to Hugo markdown")
    parser.add_argument("bib", nargs="*", help="BibTeX input path(s)")
    parser.add_argument(
        "--output-dir",
        default="site/content/reports",
        help="Hugo reports content root",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove generated publication files before writing new ones",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if not slug:
        return "untitled"
    return slug[:80].strip("-") or "untitled"


def filename_slug_from_bibtex_key(key: str) -> str:
    parts: list[str] = []
    for char in (key or "").strip():
        if char.isalnum():
            parts.append(char.lower())
        elif char == "-":
            parts.append(char)
        else:
            parts.append(f"-x{ord(char):02x}-")

    slug = "".join(parts)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:120].strip("-")


def yaml_quote(value: str) -> str:
    # Use single-quoted YAML scalars and escape embedded single quotes.
    return "'" + value.replace("'", "''") + "'"


def build_doi_url(doi: str, url: str) -> str:
    normalized_url = (url or "").strip()
    if normalized_url:
        return normalized_url

    normalized_doi = (doi or "").strip()
    if not normalized_doi:
        return ""

    normalized_doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", normalized_doi, flags=re.IGNORECASE)
    return f"https://doi.org/{normalized_doi}"


def get_venue(entry: dict) -> str:
    venue = entry.get("journal") or entry.get("booktitle") or entry.get("publisher")
    if not venue and entry.get("ENTRYTYPE", "").lower() == "misc":
        venue = entry.get("note")
    return venue or ""


def extract_fy(bib_path: Path) -> str:
    # reports-2025.bib -> 2025
    m = re.search(r"reports-(\d{4})", bib_path.name)
    if m:
        return m.group(1)
    return ""


def parse_year(entry: dict) -> str:
    # Prefer explicit year-like fields.
    for key in ("year", "pub_year", "date"):
        raw = str(entry.get(key, "")).strip()
        if raw.isdigit() and len(raw) == 4:
            return raw
        m = re.search(r"(19|20)\d{2}", raw)
        if m:
            return m.group(0)

    # Fallback: infer year from venue/note text when possible.
    fallback_blob = " ".join(
        [
            str(entry.get("journal", "")),
            str(entry.get("booktitle", "")),
            str(entry.get("note", "")),
        ]
    )
    m = re.search(r"(19|20)\d{2}", fallback_blob)
    if m:
        return m.group(0)

    return "unknown"


def _extract_month_number(raw: str) -> int | None:
    text = (raw or "").strip().lower()
    if not text:
        return None

    for token, month in MONTH_MAP.items():
        if re.search(rf"\b{re.escape(token)}\.?\b", text):
            return month

    m = re.search(r"\b(1[0-2]|0?[1-9])\b", text)
    if m:
        value = int(m.group(1))
        if 1 <= value <= 12:
            return value

    return None


def _extract_day_number(raw: str) -> int | None:
    text = (raw or "").strip().lower()
    if not text:
        return None

    for value in re.findall(r"\b([0-3]?\d)(?:st|nd|rd|th)?\b", text):
        day = int(value)
        if 1 <= day <= 31:
            return day

    return None


def parse_frontmatter_date(entry: dict) -> str:
    raw_date = str(entry.get("date", "")).strip()
    if raw_date:
        normalized = raw_date.replace("/", "-")
        m = re.match(r"^((?:19|20)\d{2})-(\d{1,2})(?:-(\d{1,2}))?$", normalized)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3) or 1)
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"

        year_match = re.search(r"(19|20)\d{2}", normalized)
        if year_match:
            year = int(year_match.group(0))
            month = _extract_month_number(normalized)
            day = _extract_day_number(normalized)
            if month is not None:
                return f"{year:04d}-{month:02d}-{(day or 1):02d}"
            return f"{year:04d}-01-01"

    year = parse_year(entry)
    if not year.isdigit():
        return "1970-01-01"

    month = _extract_month_number(str(entry.get("month", "")).strip())
    day = _extract_day_number(str(entry.get("month", "")).strip())
    if month is not None:
        return f"{int(year):04d}-{month:02d}-{(day or 1):02d}"

    return f"{int(year):04d}-01-01"


def _is_domestic_conference_venue(venue: str) -> bool:
    v = (venue or "").lower()
    if not v:
        return False

    if "international" in v:
        return False

    domestic_keywords = [
        "情報処理学会",
        "電子情報通信学会",
        "日本機械学会",
        "日本計算工学会",
        "可視化情報学会",
        "日本流体力学会",
        "全国大会",
        "年次大会",
        "講演会",
        "研究会",
        "ipsj",
        "ieice",
    ]
    return any(k in v for k in domestic_keywords)


def _contains_japanese(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", text))


def _normalize_pub_type(value: str) -> str:
    v = (value or "").strip().lower().replace("_", "-")
    allowed = {"journal", "international-conference", "domestic-conference", "others", "talk"}
    return v if v in allowed else ""


def _parse_boolish(value: str) -> bool | None:
    v = (value or "").strip().lower()
    if v in {"true", "yes", "y", "1", "reviewed", "refereed", "peer-reviewed", "査読あり", "査読有"}:
        return True
    if v in {"false", "no", "n", "0", "non-refereed", "nonrefereed", "unreviewed", "査読なし", "査読無"}:
        return False
    return None


def detect_pub_type(entry: dict) -> str:
    manual_type = _normalize_pub_type(str(entry.get("pub_type", "")))
    if manual_type:
        return manual_type

    entry_type = str(entry.get("ENTRYTYPE", "")).strip().lower()
    venue = get_venue(entry)
    authors = str(entry.get("author", "")).strip()

    # if venue (journal/booktitle) or author string contains Japanese,
    # classify as domestic conference.
    if _contains_japanese(venue) or _contains_japanese(authors):
        return "domestic-conference"

    if entry_type == "article":
        return "journal"
    if entry_type in {"inproceedings", "conference", "proceedings"}:
        if _is_domestic_conference_venue(venue):
            return "domestic-conference"
        return "international-conference"
    venue_lower = venue.lower()
    if "conference" in venue_lower or "symposium" in venue_lower or "workshop" in venue_lower:
        if _is_domestic_conference_venue(venue):
            return "domestic-conference"
        return "international-conference"
    return "others"


def detect_peer_reviewed(entry: dict, bib_path: Path, pub_type: str) -> bool | None:
    if pub_type not in {"international-conference", "domestic-conference"}:
        return None

    for key in ("peer_reviewed", "peerreviewed", "refereed", "reviewed"):
        manual = _parse_boolish(str(entry.get(key, "")))
        if manual is not None:
            return manual

    blob = " ".join(
        [
            str(entry.get("note", "")),
            str(entry.get("keywords", "")),
            str(entry.get("booktitle", "")),
            str(entry.get("journal", "")),
            str(entry.get("howpublished", "")),
        ]
    ).lower()
    if any(k in blob for k in ("non-refereed", "non refereed", "査読なし", "without review", "wip")):
        return False
    if any(k in blob for k in ("peer-reviewed", "peer reviewed", "refereed", "査読あり", "査読付")):
        return True

    stem = bib_path.stem.lower()
    if "non_refereed" in stem or "non-refereed" in stem:
        return False
    if "refereed" in stem and "non_refereed" not in stem and "non-refereed" not in stem:
        return True

    return None


def build_markdown(entry: dict, bib_path: Path, fy_name: str = "") -> str:
    title = entry.get("title", "").replace("\n", " ").strip()
    authors = entry.get("author", "").replace("\n", " ").strip()
    venue = get_venue(entry).replace("\n", " ").strip() or "Unknown venue"
    year = parse_year(entry)
    pub_type = detect_pub_type(entry)
    peer_reviewed = detect_peer_reviewed(entry, bib_path, pub_type)
    doi = entry.get("doi", "").strip()
    url = build_doi_url(doi, entry.get("url", "").strip())
    annote = str(entry.get("annote", "") or entry.get("annotation", "")).strip()
    abstract = str(entry.get("abstract", "")).strip()
    if abstract:
        abstract = re.sub(r"\s+", " ", abstract)

    date = parse_frontmatter_date(entry)
    fiscal_year = fy_name if fy_name else f"FY{year}"

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {date}",
        f"authors: {yaml_quote(authors)}",
        f"journal: {yaml_quote(venue)}",
        f"year: {yaml_quote(year)}",
        f"fiscal_year: {yaml_quote(fiscal_year)}",
        f"pub_type: {yaml_quote(pub_type)}",
    ]
    if peer_reviewed is not None:
        lines.append(f"peer_reviewed: {'true' if peer_reviewed else 'false'}")
    if annote:
        lines.append(f"annote: {yaml_quote(annote)}")
    if doi:
        lines.append(f"doi: {yaml_quote(doi)}")
    if url:
        lines.append(f"doi_url: {yaml_quote(url)}")
    if abstract:
        lines.append(f"abstract: {yaml_quote(abstract)}")
    lines.extend(["---", ""])
    return "\n".join(lines) + "\n"


def clean_generated_files(root: Path) -> None:
    if not root.exists():
        return
    for item in root.iterdir():
        if item.is_dir():
            for path in item.glob("*.md"):
                if path.name == "_index.md":
                    continue
                path.unlink()
        elif item.is_file() and item.suffix == ".md" and item.name != "_index.md":
            item.unlink()


def validate_unique_bibtex_keys(entries: list[dict]) -> None:
    seen: dict[str, list[str]] = {}

    for index, entry in enumerate(entries, start=1):
        key = str(entry.get("ID", "")).strip()
        if not key:
            continue
        source = str(entry.get("__source_bib", "")).strip()
        ref = f"{source}:entry#{index}" if source else f"entry#{index}"
        seen.setdefault(key, []).append(ref)

    duplicates = {key: refs for key, refs in seen.items() if len(refs) > 1}
    if duplicates:
        lines = ["Duplicate BibTeX keys found:"]
        for key in sorted(duplicates):
            lines.append(f"- {key}: {', '.join(duplicates[key])}")
        raise SystemExit("\n".join(lines))


def resolve_output_slug(entry: dict, title: str) -> str:
    key = str(entry.get("ID", "")).strip()
    if key:
        key_slug = filename_slug_from_bibtex_key(key)
        if not key_slug:
            raise SystemExit(
                "BibTeX key cannot be converted into a safe filename. "
                f"Use an ASCII key: {key}"
            )
        return key_slug

    title_slug = slugify(title)
    if title_slug == "untitled":
        raise SystemExit(
            "Entry is missing a usable BibTeX key and the title cannot be converted into a safe filename."
        )
    return title_slug


def resolve_bib_inputs(raw_inputs: list[str]) -> list[Path]:
    if raw_inputs:
        return [Path(p) for p in raw_inputs]
    
    # Default to data/publications/reports-*.bib
    paths = sorted(Path("data/publications").glob("reports-*.bib"))
    if not paths:
        fallback = Path("data/publications/reports.bib")
        if fallback.exists():
            return [fallback]
    return paths


def load_entries(bib_paths: list[Path]) -> list[dict]:
    entries: list[dict] = []
    for bib_path in bib_paths:
        with bib_path.open(encoding="utf-8") as bibfile:
            db = bibtexparser.load(bibfile)
        for entry in db.entries:
            copied = dict(entry)
            copied["__source_bib"] = str(bib_path)
            entries.append(copied)
    return entries


def main() -> int:
    args = parse_args()
    out_root = Path(args.output_dir)
    bib_paths = resolve_bib_inputs(args.bib)
    entries = load_entries(bib_paths)

    validate_unique_bibtex_keys(entries)

    if args.clean:
        clean_generated_files(out_root)

    written = 0
    for entry in entries:
        title = entry.get("title", "").strip()
        if not title:
            continue

        source_bib = Path(entry.get("__source_bib", ""))
        fy_year = extract_fy(source_bib)
        fy_name = f"FY{fy_year}" if fy_year else ""
        
        # Use FY folder if available, otherwise fallback to BibTeX year
        folder_name = fy_name if fy_name else parse_year(entry)
        year_dir = out_root / folder_name
        year_dir.mkdir(parents=True, exist_ok=True)

        slug = resolve_output_slug(entry, title)
        md_path = year_dir / f"{slug}.md"
        md_path.write_text(build_markdown(entry, source_bib, fy_name), encoding="utf-8")
        written += 1

    # Ensure each FY directory has an _index.md
    for item in out_root.iterdir():
        if item.is_dir() and not (item / "_index.md").exists():
            fy_title = item.name
            (item / "_index.md").write_text(f"---\ntitle: \"{fy_title}\"\n---\n", encoding="utf-8")

    print(f"Generated {written} publication markdown files under {out_root}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
