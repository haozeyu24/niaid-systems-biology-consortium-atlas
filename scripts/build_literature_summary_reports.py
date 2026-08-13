#!/usr/bin/env python3

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FULL_COLLECTION_PATH = PROJECT_ROOT / "papers" / "derived" / "full-collection" / "manifest.csv"
FINAL_CORPUS_PATH = PROJECT_ROOT / "papers" / "derived" / "consortium-subset" / "manifest.csv"
PI_BACKLOG_SEARCH_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "literature" / "pi-backlog-search-summary.csv"
CURRENT_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "current-program" / "review-queue.csv"
HPMI_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "review-queue.csv"
PI_BACKLOG_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "review-queue.csv"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "literature"
SUMMARY_MD_PATH = REPORTS_DIR / "literature-summary.md"
SOURCE_COUNTS_PATH = REPORTS_DIR / "literature-source-counts.csv"
CENTER_COUNTS_PATH = REPORTS_DIR / "literature-center-counts.csv"
PI_COUNTS_PATH = REPORTS_DIR / "literature-pi-counts.csv"


def load_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []


def write_counter_csv(path: Path, header_a: str, header_b: str, counter: Counter[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([header_a, header_b])
        for key, value in counter.most_common():
            writer.writerow([key, value])


def split_values(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def build_summary_markdown(
    full_rows: list[dict[str, str]],
    final_rows: list[dict[str, str]],
    backlog_rows: list[dict[str, str]],
    source_counts: Counter[str],
    center_counts: Counter[str],
    pi_counts: Counter[str],
    pi_search_rows: list[dict[str, str]],
) -> str:
    backlog_decisions = Counter(row["final_corpus_decision"] for row in backlog_rows)
    backlog_relevance = Counter(row["cross_virus_relevance"] for row in backlog_rows)

    top_search_rows = sorted(
        pi_search_rows,
        key=lambda row: int(row["nonoverlap_hits_added_to_backlog"]),
        reverse=True,
    )[:10]

    lines = [
        "# Literature Summary",
        "",
        "## Current State",
        "",
        f"- Full collection papers: {len(full_rows)}",
        f"- Final corpus candidates: {len(final_rows)}",
        f"- PI backlog papers: {len(backlog_rows)}",
        "",
        "## Source Counts",
        "",
    ]
    for key, value in source_counts.most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Largest Centers In Full Collection",
            "",
        ]
    )
    for key, value in center_counts.most_common(10):
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Largest PI Candidate Counts",
            "",
        ]
    )
    for key, value in pi_counts.most_common(10):
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## PI Backlog Triage",
            "",
            f"- include: {backlog_decisions.get('include', 0)}",
            f"- watch: {backlog_decisions.get('watch', 0)}",
            f"- exclude: {backlog_decisions.get('exclude', 0)}",
            f"- cross-virus high: {backlog_relevance.get('high', 0)}",
            f"- cross-virus candidate: {backlog_relevance.get('candidate', 0)}",
            f"- cross-virus unknown: {backlog_relevance.get('unknown', 0)}",
            "",
            "## Largest PI Backlog Search Buckets",
            "",
        ]
    )
    for row in top_search_rows:
        lines.append(
            f"- {row['pi_name']} ({row['center']}): {row['nonoverlap_hits_added_to_backlog']} non-overlap papers"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    full_rows = load_rows(FULL_COLLECTION_PATH)
    final_rows = load_rows(FINAL_CORPUS_PATH)
    current_rows = load_rows(CURRENT_QUEUE_PATH)
    hpmi_rows = load_rows(HPMI_QUEUE_PATH)
    backlog_rows = load_rows(PI_BACKLOG_QUEUE_PATH)
    pi_search_rows = load_rows(PI_BACKLOG_SEARCH_SUMMARY_PATH)

    source_counts: Counter[str] = Counter()
    center_counts: Counter[str] = Counter()
    pi_counts: Counter[str] = Counter()

    for row in full_rows:
        for source in split_values(row.get("source_collections", "")):
            source_counts[source] += 1
        center_counts[row.get("center", "") or "unassigned"] += 1
        for pi in split_values(row.get("pi_candidates", "")):
            pi_counts[pi] += 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    write_counter_csv(SOURCE_COUNTS_PATH, "source_collection", "paper_count", source_counts)
    write_counter_csv(CENTER_COUNTS_PATH, "center", "paper_count", center_counts)
    write_counter_csv(PI_COUNTS_PATH, "pi_candidate", "paper_count", pi_counts)

    summary_markdown = build_summary_markdown(
        full_rows,
        final_rows,
        backlog_rows,
        source_counts,
        center_counts,
        pi_counts,
        pi_search_rows,
    )
    SUMMARY_MD_PATH.write_text(summary_markdown, encoding="utf-8")

    print(f"Wrote summary markdown to {SUMMARY_MD_PATH}")
    print(f"Wrote source counts to {SOURCE_COUNTS_PATH}")
    print(f"Wrote center counts to {CENTER_COUNTS_PATH}")
    print(f"Wrote PI counts to {PI_COUNTS_PATH}")
    print(
        f"Reviewed queues: current={len(current_rows)} hpmi={len(hpmi_rows)} pi_backlog={len(backlog_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
