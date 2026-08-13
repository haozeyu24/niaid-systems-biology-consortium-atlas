#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "papers" / "derived" / "full-collection"
OUTPUT_PATH = OUTPUT_DIR / "manifest.csv"

SOURCES = [
    {
        "name": "current-program",
        "manifest": PROJECT_ROOT / "papers" / "sources" / "current-program" / "manifest.csv",
        "records_dir": PROJECT_ROOT / "papers" / "sources" / "current-program" / "records",
    },
    {
        "name": "hpmi",
        "manifest": PROJECT_ROOT / "papers" / "sources" / "hpmi" / "manifest.csv",
        "records_dir": PROJECT_ROOT / "papers" / "sources" / "hpmi" / "records",
    },
    {
        "name": "pi-backlog",
        "manifest": PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "manifest.csv",
        "records_dir": PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "records",
    },
]

FIELDNAMES = [
    "paper_id",
    "title",
    "pmid",
    "doi",
    "year",
    "journal",
    "source_collections",
    "in_current_program",
    "in_hpmi",
    "in_pi_backlog",
    "center",
    "pi_candidates",
    "paper_status",
]


def load_record(records_dir: Path, paper_id: str) -> dict:
    path = records_dir / f"{paper_id}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def merge_nonempty(existing: str, incoming: str) -> str:
    return existing if existing else incoming


def merge_list_text(existing: str, incoming_values: list[str]) -> str:
    items = [value for value in existing.split(";") if value] if existing else []
    for value in incoming_values:
        if value and value not in items:
            items.append(value)
    return ";".join(items)


def main() -> int:
    merged: dict[str, dict[str, str]] = {}

    for source in SOURCES:
        rows = list(csv.DictReader(source["manifest"].open(encoding="utf-8")))
        for row in rows:
            paper_id = row["paper_id"]
            record = load_record(source["records_dir"], paper_id)
            pmid = row.get("pmid", "")
            entry = merged.setdefault(
                pmid,
                {
                    "paper_id": paper_id,
                    "title": row.get("title", ""),
                    "pmid": pmid,
                    "doi": row.get("doi", ""),
                    "year": row.get("year", ""),
                    "journal": str(record.get("journal", "") or ""),
                    "source_collections": "",
                    "in_current_program": "no",
                    "in_hpmi": "no",
                    "in_pi_backlog": "no",
                    "center": str(record.get("center", "") or ""),
                    "pi_candidates": "",
                    "paper_status": row.get("paper_status", ""),
                },
            )

            entry["title"] = merge_nonempty(entry["title"], row.get("title", ""))
            entry["doi"] = merge_nonempty(entry["doi"], row.get("doi", ""))
            entry["year"] = merge_nonempty(entry["year"], row.get("year", ""))
            entry["journal"] = merge_nonempty(entry["journal"], str(record.get("journal", "") or ""))
            entry["paper_status"] = merge_nonempty(entry["paper_status"], row.get("paper_status", ""))
            entry["center"] = merge_nonempty(entry["center"], str(record.get("center", "") or ""))
            entry["source_collections"] = merge_list_text(entry["source_collections"], [source["name"]])
            entry["pi_candidates"] = merge_list_text(
                entry["pi_candidates"],
                [str(value) for value in (record.get("pi_candidates", []) or [])],
            )

            if source["name"] == "current-program":
                entry["in_current_program"] = "yes"
            elif source["name"] == "hpmi":
                entry["in_hpmi"] = "yes"
            elif source["name"] == "pi-backlog":
                entry["in_pi_backlog"] = "yes"

    rows = sorted(
        merged.values(),
        key=lambda row: (row.get("year", ""), row.get("pmid", "")),
        reverse=True,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
