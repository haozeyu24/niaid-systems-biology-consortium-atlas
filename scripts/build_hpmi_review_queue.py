#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "manifest.csv"
REVIEW_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "review-queue.csv"
RECORDS_DIR = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "records"

FIELDNAMES = [
    "paper_id",
    "pmid",
    "year",
    "title",
    "abstract_excerpt",
    "collection_route",
    "center",
    "pi_candidates",
    "pathogens",
    "viruses",
    "assay_types",
    "paper_kind",
    "cross_virus_relevance",
    "cross_virus_reason",
    "priority",
    "priority_reason",
    "review_status",
    "notes",
]


def combined_text(title: str, abstract: str) -> str:
    return f"{title}\n{abstract}".lower()


def has_term(text: str, term: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", text) is not None


def infer_priority(title: str, abstract: str, year: str) -> tuple[str, str]:
    lowered = combined_text(title, abstract)
    matched = [
        token
        for token in [
            "virus",
            "viral",
            "sars",
            "cov",
            "influenza",
            "dengue",
            "zika",
            "rsv",
            "host-pathogen",
            "host pathogen",
            "respiratory infection",
            "dependency network",
            "interaction map",
            "crispr screen",
            "tuberculosis",
            "mycobacterium",
        ]
        if has_term(lowered, token)
    ]
    if year in {"2026", "2025"}:
        if matched:
            return "high", f"recent HPMI paper with relevant terms: {', '.join(matched[:5])}"
        return "medium", "recent HPMI paper but no strong viral/pathogen keywords matched"
    if matched:
        return "medium", f"older HPMI paper with relevant terms: {', '.join(matched[:5])}"
    return "low", "no strong HPMI literature-priority keywords matched"


def infer_cross_virus_relevance(title: str, abstract: str) -> tuple[str, str]:
    lowered = combined_text(title, abstract)
    high_matched = [
        token
        for token in [
            "shared host",
            "comparative",
            "cross-virus",
            "multi-virus",
            "common host",
            "broad-spectrum",
            "multiple viruses",
            "conserved host",
            "pan-viral",
            "across variants",
        ]
        if has_term(lowered, token)
    ]
    if high_matched:
        return "high", f"explicit cross-virus/shared-host language: {', '.join(high_matched[:5])}"

    candidate_matched = [
        token
        for token in [
            "virus",
            "viral",
            "host-pathogen",
            "host pathogen",
            "interaction",
            "dependency",
            "host factor",
            "proteome",
            "interactome",
            "crispr",
            "pathway",
            "tuberculosis",
            "mycobacterium",
        ]
        if has_term(lowered, token)
    ]
    if candidate_matched:
        return "candidate", f"relevant host-pathogen/pathway terms matched: {', '.join(candidate_matched[:5])}"
    return "unknown", "no explicit cross-virus or strong host-mechanism terms matched"


def infer_paper_kind(title: str, abstract: str) -> str:
    lowered = combined_text(title, abstract)
    if any(has_term(lowered, token) for token in ["review", "perspective", "commentary"]):
        return "review"
    if any(has_term(lowered, token) for token in ["protocol", "workflow", "method", "pipeline"]):
        return "methods"
    if any(
        has_term(lowered, token)
        for token in [
            "atlas",
            "map",
            "screen",
            "proteom",
            "interact",
            "transcript",
            "phospho",
            "multi-omic",
            "multiomic",
            "sequencing",
            "profiling",
        ]
    ):
        return "data_or_analysis"
    return "primary_research"


def abstract_excerpt(text: str, limit: int = 280) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def build_rows() -> list[dict[str, str]]:
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        manifest_rows = list(csv.DictReader(handle))

    review_rows: list[dict[str, str]] = []
    for row in manifest_rows:
        paper_id = row["paper_id"]
        record_path = RECORDS_DIR / f"{paper_id}.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
        title = str(record.get("title", "") or row.get("title", ""))
        abstract = str(record.get("abstract", "") or "")
        cross_virus_relevance, cross_virus_reason = infer_cross_virus_relevance(title, abstract)
        priority, priority_reason = infer_priority(title, abstract, row["year"])

        review_rows.append(
            {
                "paper_id": paper_id,
                "pmid": row["pmid"],
                "year": row["year"],
                "title": title,
                "abstract_excerpt": abstract_excerpt(abstract),
                "collection_route": row["collection_route"],
                "center": "HPMI",
                "pi_candidates": "",
                "pathogens": "",
                "viruses": "",
                "assay_types": "",
                "paper_kind": infer_paper_kind(title, abstract),
                "cross_virus_relevance": cross_virus_relevance,
                "cross_virus_reason": cross_virus_reason,
                "priority": priority,
                "priority_reason": priority_reason,
                "review_status": "pending",
                "notes": "",
            }
        )
    return review_rows


def write_rows(rows: list[dict[str, str]]) -> None:
    with REVIEW_QUEUE_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = build_rows()
    write_rows(rows)
    print(f"Wrote {len(rows)} HPMI review queue rows to {REVIEW_QUEUE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
