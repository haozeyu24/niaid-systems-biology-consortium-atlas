#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURRENT_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "current-program" / "review-queue.csv"
HPMI_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "review-queue.csv"
PI_BACKLOG_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "review-queue.csv"
OUTPUT_PATH = PROJECT_ROOT / "papers" / "derived" / "consortium-subset" / "manifest.csv"

FIELDNAMES = [
    "source_collection",
    "paper_id",
    "pmid",
    "doi",
    "year",
    "center",
    "title",
    "pi_candidates",
    "subset_reason",
    "virus_or_pathogen",
    "assay_types",
    "cross_virus_relevance",
    "priority",
]


def load_manifest_map(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["paper_id"]: row for row in csv.DictReader(handle)}


def keep_program_or_hpmi(row: dict[str, str]) -> tuple[bool, str]:
    if row.get("cross_virus_relevance") == "high":
        return True, "explicit cross-virus/shared-host signal"
    if row.get("cross_virus_relevance") == "candidate" and (
        row.get("viruses") or row.get("pathogens") or row.get("assay_types")
    ):
        return True, "candidate relevance plus virus/pathogen/assay support"
    if row.get("priority") == "high" and row.get("paper_kind") == "data_or_analysis":
        return True, "high-priority data or analysis paper"
    return False, ""


def keep_pi_backlog(row: dict[str, str]) -> tuple[bool, str]:
    if row.get("final_corpus_decision") == "include":
        return True, row.get("final_corpus_reason", "PI backlog paper selected for final corpus")
    return False, ""


def add_rows(
    rows: list[dict[str, str]],
    source_collection: str,
    queue_path: Path,
    manifest_map: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    if not queue_path.exists():
        return rows

    for row in csv.DictReader(queue_path.open(encoding="utf-8")):
        if source_collection == "pi-backlog":
            keep, reason = keep_pi_backlog(row)
            center = row.get("matched_centers", "")
            pi_candidates = row.get("matched_pis", "")
        else:
            keep, reason = keep_program_or_hpmi(row)
            center = row.get("center", "")
            pi_candidates = row.get("pi_candidates", "")
        if not keep:
            continue

        manifest_row = manifest_map.get(row["paper_id"], {})
        rows.append(
            {
                "source_collection": source_collection,
                "paper_id": row["paper_id"],
                "pmid": row["pmid"],
                "doi": manifest_row.get("doi", ""),
                "year": row.get("year", ""),
                "center": center,
                "title": row.get("title", ""),
                "pi_candidates": pi_candidates,
                "subset_reason": reason,
                "virus_or_pathogen": ";".join(
                    value for value in [row.get("viruses", ""), row.get("pathogens", "")] if value
                ),
                "assay_types": row.get("assay_types", ""),
                "cross_virus_relevance": row.get("cross_virus_relevance", ""),
                "priority": row.get("priority", ""),
            }
        )
    return rows


def main() -> int:
    rows: list[dict[str, str]] = []
    rows = add_rows(
        rows,
        "current-program",
        CURRENT_QUEUE_PATH,
        load_manifest_map(PROJECT_ROOT / "papers" / "sources" / "current-program" / "manifest.csv"),
    )
    rows = add_rows(
        rows,
        "hpmi",
        HPMI_QUEUE_PATH,
        load_manifest_map(PROJECT_ROOT / "papers" / "sources" / "hpmi" / "manifest.csv"),
    )
    rows = add_rows(
        rows,
        "pi-backlog",
        PI_BACKLOG_QUEUE_PATH,
        load_manifest_map(PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "manifest.csv"),
    )
    rows.sort(key=lambda row: (row["year"], row["source_collection"], row["pmid"]), reverse=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} final corpus candidates to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
