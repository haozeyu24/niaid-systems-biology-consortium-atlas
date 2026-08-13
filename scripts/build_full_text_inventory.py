#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_CORPUS_PATH = PROJECT_ROOT / "papers" / "derived" / "consortium-subset" / "manifest.csv"
FULL_TEXT_DIR = PROJECT_ROOT / "papers" / "fulltext" / "inventory"
OA_DIR = FULL_TEXT_DIR / "oa"
MANUAL_DIR = FULL_TEXT_DIR / "manual"
MANIFEST_PATH = FULL_TEXT_DIR / "manifest.csv"
MANUAL_DOWNLOAD_PATH = FULL_TEXT_DIR / "manual-download-list.csv"
README_PATH = FULL_TEXT_DIR / "README.md"

SOURCE_RECORD_DIRS = {
    "current-program": PROJECT_ROOT / "papers" / "sources" / "current-program" / "records",
    "hpmi": PROJECT_ROOT / "papers" / "sources" / "hpmi" / "records",
    "pi-backlog": PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "records",
}

FIELDNAMES = [
    "source_collection",
    "paper_id",
    "pmid",
    "doi",
    "year",
    "title",
    "center",
    "pi_candidates",
    "cross_virus_relevance",
    "priority",
    "subset_reason",
    "pmcid",
    "pubmed_url",
    "pmc_url",
    "publisher_url",
    "open_access_status",
    "full_text_source",
    "full_text_status",
    "oa_landing_path",
    "oa_pdf_path",
    "manual_download_needed",
    "manual_download_reason",
]


def load_record(source_collection: str, paper_id: str) -> dict:
    record_path = SOURCE_RECORD_DIRS[source_collection] / f"{paper_id}.json"
    return json.loads(record_path.read_text(encoding="utf-8"))


def oa_pdf_path_for_pmcid(pmcid: str) -> str:
    if not pmcid:
        return ""
    return f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"


def local_oa_stub_path(paper_id: str, suffix: str) -> str:
    return f"papers/fulltext/inventory/oa/{paper_id}{suffix}"


def local_oa_file_path(paper_id: str, suffix: str) -> Path:
    return OA_DIR / f"{paper_id}{suffix}"


def write_readme() -> None:
    text = """# Full Text

This folder tracks full-text availability for the `papers/derived/consortium-subset` candidate corpus.

Subfolders:

- `oa/`
  Intended for open-access full-text assets or landing-page captures that can be retrieved automatically or saved locally.
- `manual/`
  Intended for locally added PDFs or text files downloaded manually when automatic OA access is not available.

Key files:

- `manifest.csv`
  Full-text availability and link inventory for every paper in the candidate corpus.
- `manual-download-list.csv`
  Papers that likely require manual PDF download or institutional access.

This layer is about logistics and provenance:

- where full text may be available
- whether a paper appears to be open access
- which papers still need manual collection

It does not yet perform deep full-text parsing.
"""
    README_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    FULL_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    OA_DIR.mkdir(parents=True, exist_ok=True)
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(FINAL_CORPUS_PATH.open(encoding="utf-8")))
    manifest_rows: list[dict[str, str]] = []
    manual_rows: list[dict[str, str]] = []

    for row in rows:
        record = load_record(row["source_collection"], row["paper_id"])
        identifiers = record.get("identifiers", {}) or {}
        links = record.get("links", {}) or {}
        pmcid = str(identifiers.get("pmcid", "") or "")
        pmc_url = str(links.get("pmc", "") or "")
        publisher_url = str(links.get("publisher", "") or "")
        pubmed_url = str(links.get("pubmed", "") or "")

        open_access_status = "unknown"
        full_text_source = "none"
        full_text_status = "not_collected"
        oa_landing_path = ""
        oa_pdf_path = ""
        manual_download_needed = "yes"
        manual_download_reason = "no known open-access full-text link in current metadata"

        if pmcid:
            open_access_status = "pmc_open_access"
            full_text_source = "pmc"
            full_text_status = "oa_available_not_downloaded"
            oa_landing_path = pmc_url
            oa_pdf_path = oa_pdf_path_for_pmcid(pmcid)
            manual_download_needed = "no"
            manual_download_reason = ""
        elif publisher_url:
            open_access_status = "publisher_or_doi_only"
            full_text_source = "publisher"
            full_text_status = "manual_check_needed"
            manual_download_reason = "publisher/DOI link available but OA status not confirmed from current metadata"
        else:
            open_access_status = "no_oa_link_detected"
            full_text_source = "none"
            full_text_status = "manual_check_needed"

        local_pdf = local_oa_file_path(row["paper_id"], ".pdf")
        local_url = local_oa_file_path(row["paper_id"], ".url")
        if local_pdf.exists():
            full_text_status = "oa_pdf_downloaded"
            oa_pdf_path = local_oa_stub_path(row["paper_id"], ".pdf")
        if local_url.exists():
            oa_landing_path = local_oa_stub_path(row["paper_id"], ".url")

        manifest_row = {
            "source_collection": row["source_collection"],
            "paper_id": row["paper_id"],
            "pmid": row["pmid"],
            "doi": row["doi"],
            "year": row["year"],
            "title": row["title"],
            "center": row["center"],
            "pi_candidates": row["pi_candidates"],
            "cross_virus_relevance": row["cross_virus_relevance"],
            "priority": row["priority"],
            "subset_reason": row["subset_reason"],
            "pmcid": pmcid,
            "pubmed_url": pubmed_url,
            "pmc_url": pmc_url,
            "publisher_url": publisher_url,
            "open_access_status": open_access_status,
            "full_text_source": full_text_source,
            "full_text_status": full_text_status,
            "oa_landing_path": oa_landing_path or local_oa_stub_path(row["paper_id"], ".url"),
            "oa_pdf_path": oa_pdf_path or local_oa_stub_path(row["paper_id"], ".pdf"),
            "manual_download_needed": manual_download_needed,
            "manual_download_reason": manual_download_reason,
        }
        manifest_rows.append(manifest_row)
        if manual_download_needed == "yes":
            manual_rows.append(manifest_row)

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(manifest_rows)

    with MANUAL_DOWNLOAD_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_collection",
                "paper_id",
                "pmid",
                "doi",
                "year",
                "title",
                "center",
                "pi_candidates",
                "pubmed_url",
                "publisher_url",
                "manual_download_reason",
            ],
        )
        writer.writeheader()
        for row in manual_rows:
            writer.writerow(
                {
                    "source_collection": row["source_collection"],
                    "paper_id": row["paper_id"],
                    "pmid": row["pmid"],
                    "doi": row["doi"],
                    "year": row["year"],
                    "title": row["title"],
                    "center": row["center"],
                    "pi_candidates": row["pi_candidates"],
                    "pubmed_url": row["pubmed_url"],
                    "publisher_url": row["publisher_url"],
                    "manual_download_reason": row["manual_download_reason"],
                }
            )

    write_readme()
    print(f"Wrote full-text manifest for {len(manifest_rows)} papers to {MANIFEST_PATH}")
    print(f"Wrote manual download list with {len(manual_rows)} rows to {MANUAL_DOWNLOAD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
