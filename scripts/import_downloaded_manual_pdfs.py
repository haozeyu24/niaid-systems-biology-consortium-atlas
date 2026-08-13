#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
import shutil
from difflib import SequenceMatcher
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUAL_LIST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manual-download-list.csv"
MANUAL_DIR = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manual"
REPORT_PATH = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manual-import-report.csv"
DOWNLOADS_DIR = Path.home() / "Downloads"

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


def normalize_doi(value: str) -> str:
    return value.strip().lower()


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def extract_pdf_clues(path: Path) -> dict[str, str]:
    text_parts: list[str] = [path.stem]
    try:
        reader = PdfReader(str(path))
        metadata = reader.metadata or {}
        for key in ("/Title", "/Subject"):
            if metadata.get(key):
                text_parts.append(str(metadata[key]))
        page_text = ""
        for page in reader.pages[:2]:
            extracted = page.extract_text() or ""
            if extracted:
                page_text += "\n" + extracted[:4000]
        if page_text:
            text_parts.append(page_text)
    except Exception:
        pass

    combined = "\n".join(text_parts)
    doi_match = DOI_RE.search(combined)
    return {
        "text": combined,
        "doi": normalize_doi(doi_match.group(0)) if doi_match else "",
        "normalized_text": normalize_text(combined),
    }


def title_similarity(title: str, clue_text: str) -> float:
    normalized_title = normalize_text(title)
    if not normalized_title:
        return 0.0
    ratio = SequenceMatcher(None, normalized_title, clue_text).ratio()
    title_tokens = set(normalized_title.split())
    clue_tokens = set(clue_text.split())
    overlap = len(title_tokens & clue_tokens) / max(len(title_tokens), 1)
    return max(ratio, overlap)


def write_sidecar(path: Path, source_path: Path) -> None:
    path.write_text(f"downloads_source_file: {source_path.name}\n", encoding="utf-8")


def main() -> int:
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)

    targets = list(csv.DictReader(MANUAL_LIST_PATH.open(encoding="utf-8")))
    pdf_paths = sorted(DOWNLOADS_DIR.glob("*.pdf"))
    clues_by_path = {path: extract_pdf_clues(path) for path in pdf_paths}

    used_paths: set[Path] = set()
    report_rows: list[dict[str, str]] = []

    for row in targets:
        target_doi = normalize_doi(row["doi"])
        matched_path: Path | None = None
        match_method = ""
        best_score = 0.0

        if target_doi:
            for path, clues in clues_by_path.items():
                if path in used_paths:
                    continue
                if clues["doi"] and clues["doi"] == target_doi:
                    matched_path = path
                    match_method = "doi"
                    best_score = 1.0
                    break

        if matched_path is None:
            scored: list[tuple[float, Path]] = []
            for path, clues in clues_by_path.items():
                if path in used_paths:
                    continue
                score = title_similarity(row["title"], clues["normalized_text"])
                if score >= 0.55:
                    scored.append((score, path))
            scored.sort(key=lambda item: item[0], reverse=True)
            if scored:
                best_score, matched_path = scored[0]
                match_method = "title_similarity"

        dest_pdf = MANUAL_DIR / f"{row['paper_id']}.pdf"
        dest_sidecar = MANUAL_DIR / f"{row['paper_id']}.source.txt"
        status = "unmatched"

        if matched_path is not None:
            shutil.copy2(matched_path, dest_pdf)
            write_sidecar(dest_sidecar, matched_path)
            used_paths.add(matched_path)
            status = "imported"

        report_rows.append(
            {
                "paper_id": row["paper_id"],
                "pmid": row["pmid"],
                "doi": row["doi"],
                "title": row["title"],
                "status": status,
                "match_method": match_method,
                "match_score": f"{best_score:.3f}" if best_score else "",
                "downloads_source_file": matched_path.name if matched_path else "",
            }
        )

    with REPORT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "pmid",
                "doi",
                "title",
                "status",
                "match_method",
                "match_score",
                "downloads_source_file",
            ],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    imported = sum(1 for row in report_rows if row["status"] == "imported")
    unmatched = len(report_rows) - imported
    print(f"Imported {imported} manual PDFs into {MANUAL_DIR}")
    print(f"Unmatched manual targets: {unmatched}")
    print(f"Wrote import report to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
