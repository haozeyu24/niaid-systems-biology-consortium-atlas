#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "manifest.csv"
REVIEW_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "review-queue.csv"
RECORDS_DIR = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "records"

FIELDNAMES = [
    "paper_id",
    "pmid",
    "year",
    "title",
    "abstract_excerpt",
    "matched_pis",
    "matched_centers",
    "viruses",
    "pathogens",
    "assay_types",
    "paper_kind",
    "cross_virus_relevance",
    "cross_virus_reason",
    "priority",
    "priority_reason",
    "final_corpus_decision",
    "final_corpus_reason",
    "review_status",
    "notes",
]


def combined_text(title: str, abstract: str) -> str:
    return f"{title}\n{abstract}".lower()


def has_term(text: str, term: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", text) is not None


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
            "network",
        ]
    ):
        return "data_or_analysis"
    return "primary_research"


def infer_cross_virus_relevance(title: str, abstract: str) -> tuple[str, str]:
    lowered = combined_text(title, abstract)
    high_matched = [
        token
        for token in [
            "shared host",
            "comparative",
            "cross-virus",
            "cross virus",
            "multi-virus",
            "multiple viruses",
            "common host",
            "broad-spectrum",
            "pan-viral",
            "conserved host",
            "virus-host interaction map",
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
            "infection",
        ]
        if has_term(lowered, token)
    ]
    if candidate_matched:
        return "candidate", f"relevant viral/host/pathway terms matched: {', '.join(candidate_matched[:5])}"
    return "unknown", "no explicit cross-virus or strong viral host-mechanism terms matched"


def infer_priority(title: str, abstract: str, year: str) -> tuple[str, str]:
    lowered = combined_text(title, abstract)
    recent_matched = [
        token
        for token in [
            "virus",
            "viral",
            "host",
            "pathway",
            "screen",
            "interactome",
            "proteomics",
            "crispr",
        ]
        if has_term(lowered, token)
    ]
    if year in {"2026", "2025", "2024"} and recent_matched:
        return "high", f"recent paper with relevant terms: {', '.join(recent_matched[:5])}"
    if recent_matched:
        return "medium", f"relevant mechanistic terms: {', '.join(recent_matched[:5])}"
    return "low", "no strong backlog-priority keywords matched"


def decide_final_corpus(title: str, abstract: str, paper_kind: str, cross_virus_relevance: str) -> tuple[str, str]:
    lowered = combined_text(title, abstract)
    virus_terms = [
        token
        for token in [
            "virus",
            "viral",
            "influenza",
            "coronavirus",
            "sars",
            "hiv",
            "dengue",
            "zika",
            "rsv",
        ]
        if has_term(lowered, token)
    ]
    mechanism_terms = [
        token
        for token in [
            "pathway",
            "host factor",
            "dependency",
            "interactome",
            "interaction",
            "network",
            "proteomics",
            "screen",
            "transcriptome",
            "host response",
        ]
        if has_term(lowered, token)
    ]

    if cross_virus_relevance == "high":
        return "include", "explicit cross-virus or shared-host framing in title/abstract"
    if virus_terms and mechanism_terms:
        return "include", f"viral context plus mechanism/resource terms: {', '.join((virus_terms + mechanism_terms)[:6])}"
    if paper_kind == "review" and virus_terms and mechanism_terms:
        return "include", "review with viral and host-mechanism framing that can help the final corpus"
    if virus_terms:
        return "watch", f"infectious-disease paper but mechanism signal is still weak: {', '.join(virus_terms[:4])}"
    return "exclude", "no clear viral host-mechanism or cross-virus signal in title/abstract"


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
        title = str(record.get("title", "") or row["title"])
        abstract = str(record.get("abstract", "") or "")
        year = row.get("year", "")

        paper_kind = infer_paper_kind(title, abstract)
        cross_virus_relevance, cross_virus_reason = infer_cross_virus_relevance(title, abstract)
        priority, priority_reason = infer_priority(title, abstract, year)
        final_corpus_decision, final_corpus_reason = decide_final_corpus(
            title,
            abstract,
            paper_kind,
            cross_virus_relevance,
        )

        review_rows.append(
            {
                "paper_id": paper_id,
                "pmid": row["pmid"],
                "year": year,
                "title": title,
                "abstract_excerpt": abstract_excerpt(abstract),
                "matched_pis": row.get("matched_pis", ""),
                "matched_centers": row.get("matched_centers", ""),
                "viruses": "",
                "pathogens": "",
                "assay_types": "",
                "paper_kind": paper_kind,
                "cross_virus_relevance": cross_virus_relevance,
                "cross_virus_reason": cross_virus_reason,
                "priority": priority,
                "priority_reason": priority_reason,
                "final_corpus_decision": final_corpus_decision,
                "final_corpus_reason": final_corpus_reason,
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
    print(f"Wrote {len(rows)} PI backlog review rows to {REVIEW_QUEUE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
