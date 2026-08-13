#!/usr/bin/env python3

from __future__ import annotations

import csv
import subprocess
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manifest.csv"
OA_DIR = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "oa"
FAILURES_PATH = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "oa-download-failures.csv"
NCBI_RATE_LIMIT_SECONDS = 0.34


def fetch_file(url: str, output_path: Path) -> None:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, 4):
        try:
            subprocess.run(
                [
                    "curl",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--location",
                    "--max-time",
                    "120",
                    "--user-agent",
                    "niaid-systems-biology-consortium-atlas/0.1 (oa full-text download)",
                    "--output",
                    str(output_path),
                    url,
                ],
                check=True,
                capture_output=True,
            )
            return
        except subprocess.CalledProcessError as error:
            last_error = error
            time.sleep(attempt)
    if last_error is not None:
        raise last_error
    raise RuntimeError("unreachable fetch_file failure")


def write_url_sidecar(path: Path, pmc_url: str, pdf_url: str) -> None:
    content = f"pmc_url: {pmc_url}\npdf_url: {pdf_url}\n"
    path.write_text(content, encoding="utf-8")


def main() -> int:
    OA_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(MANIFEST_PATH.open(encoding="utf-8")))
    target_rows = [row for row in rows if row["open_access_status"] == "pmc_open_access"]

    downloaded = 0
    skipped = 0
    failed = 0
    failed_rows: list[dict[str, str]] = []

    for row in target_rows:
        paper_id = row["paper_id"]
        pdf_path = OA_DIR / f"{paper_id}.pdf"
        url_path = OA_DIR / f"{paper_id}.url"
        pdf_url = row["oa_pdf_path"]
        pmc_url = row["pmc_url"]

        if pdf_path.exists():
            skipped += 1
            if not url_path.exists():
                write_url_sidecar(url_path, pmc_url, pdf_url)
            continue

        print(f"Downloading OA PDF for {paper_id}", flush=True)
        try:
            fetch_file(pdf_url, pdf_path)
            write_url_sidecar(url_path, pmc_url, pdf_url)
            downloaded += 1
        except subprocess.CalledProcessError:
            failed += 1
            if pdf_path.exists():
                pdf_path.unlink()
            failed_rows.append(
                {
                    "paper_id": paper_id,
                    "pmid": row["pmid"],
                    "title": row["title"],
                    "pmc_url": pmc_url,
                    "pdf_url": pdf_url,
                }
            )
        time.sleep(NCBI_RATE_LIMIT_SECONDS)

    with FAILURES_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["paper_id", "pmid", "title", "pmc_url", "pdf_url"],
        )
        writer.writeheader()
        writer.writerows(failed_rows)

    print(f"OA download complete: downloaded={downloaded} skipped={skipped} failed={failed}")
    print(f"Wrote OA download failures to {FAILURES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
