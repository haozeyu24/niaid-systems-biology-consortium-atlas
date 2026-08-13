#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURRENT_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "current-program" / "review-queue.csv"
HPMI_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "review-queue.csv"
PI_BACKLOG_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "review-queue.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "reports" / "literature" / "initial-literature-shortlist.csv"

FIELDNAMES = [
    "source_collection",
    "paper_id",
    "pmid",
    "year",
    "center",
    "title",
    "pi_candidates",
    "viruses",
    "pathogens",
    "assay_types",
    "paper_kind",
    "cross_virus_relevance",
    "cross_virus_reason",
    "priority",
    "priority_reason",
    "abstract_excerpt",
]


def load_rows(path: Path, source_collection: str) -> list[dict[str, str]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for row in rows:
        row["source_collection"] = source_collection
    return rows


def shortlist_score(row: dict[str, str]) -> int:
    score = 0
    if row.get("source_collection") == "hpmi":
        score += 3
    elif row.get("source_collection") == "pi-backlog":
        score += 1
    if row.get("cross_virus_relevance") == "high":
        score += 4
    elif row.get("cross_virus_relevance") == "candidate":
        score += 2
    if row.get("priority") == "high":
        score += 3
    elif row.get("priority") == "medium":
        score += 1
    if row.get("viruses"):
        score += 2
    if row.get("pathogens"):
        score += 1
    if row.get("assay_types"):
        score += 1
    if row.get("paper_kind") == "data_or_analysis":
        score += 1
    return score


def keep_row(row: dict[str, str]) -> bool:
    if row.get("source_collection") == "pi-backlog":
        return row.get("final_corpus_decision") in {"include", "watch"}
    if row.get("cross_virus_relevance") in {"high", "candidate"}:
        return True
    if row.get("priority") == "high" and (row.get("viruses") or row.get("pathogens")):
        return True
    if row.get("source_collection") == "hpmi" and row.get("priority") in {"high", "medium"}:
        return True
    return False


def main() -> int:
    rows = (
        load_rows(CURRENT_QUEUE_PATH, "current-program")
        + load_rows(HPMI_QUEUE_PATH, "hpmi")
        + load_rows(PI_BACKLOG_QUEUE_PATH, "pi-backlog")
    )
    shortlist = [row for row in rows if keep_row(row)]
    shortlist.sort(
        key=lambda row: (
            shortlist_score(row),
            row.get("year", ""),
            row.get("pmid", ""),
        ),
        reverse=True,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(
            {field: row.get(field, "") for field in FIELDNAMES}
            for row in shortlist
        )

    print(f"Wrote {len(shortlist)} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
