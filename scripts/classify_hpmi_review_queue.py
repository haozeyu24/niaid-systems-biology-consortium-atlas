#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "review-queue.csv"
RECORDS_DIR = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "records"

VIRUS_KEYWORDS = {
    "sars-cov-2": ["sars-cov-2", "covid-19", "covid 19", "omicron"],
    "sars-cov": ["sars-cov"],
    "coronavirus": ["coronavirus", "coronaviruses"],
    "influenza": ["influenza", "flu"],
    "dengue": ["dengue", "denv"],
    "zika": ["zika", "zikv"],
    "hiv": ["hiv", "human immunodeficiency virus"],
    "enterovirus": ["enterovirus"],
    "lassa": ["lassa virus", "lasv"],
}

PATHOGEN_KEYWORDS = {
    "mycobacterium_tuberculosis": ["mycobacterium tuberculosis", "m. tuberculosis", "tuberculosis", "mtb"],
    "mycobacterium_marinum": ["mycobacterium marinum"],
    "legionella_pneumophila": ["legionella pneumophila"],
    "arenaviridae": ["arenaviridae", "arenavirus", "arenaviruses"],
}

ASSAY_KEYWORDS = {
    "crispr_screen": ["crispr screening", "genome-wide crispr", "crispr screen"],
    "protein_interaction_mapping": ["protein interaction mapping", "interactome", "protein-protein interaction", "affinity purification mass spectrometry"],
    "proteomics": ["proteomic", "proteomics", "mass spectrometry", "phosphorylation"],
    "transcriptomics": ["rna-seq", "transcriptional", "single-cell rna", "transcriptom"],
    "structural_biology": ["structure", "structural", "cryo-em", "integrative structure"],
    "genome_editing": ["genome editing", "cas9", "cas12a", "tnpb"],
}


def keyword_matches(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    matches: list[str] = []
    for label, terms in keyword_map.items():
        if any(term in lowered for term in terms):
            matches.append(label)
    return matches


def main() -> int:
    rows = list(csv.DictReader(REVIEW_QUEUE_PATH.open(encoding="utf-8")))
    fieldnames = rows[0].keys() if rows else []
    enriched_rows: list[dict[str, str]] = []

    for row in rows:
        record_path = RECORDS_DIR / f"{row['paper_id']}.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
        title = str(record.get("title", "") or row.get("title", ""))
        abstract = str(record.get("abstract", "") or "")
        text = f"{title}\n{abstract}"

        row["viruses"] = ";".join(keyword_matches(text, VIRUS_KEYWORDS))
        row["pathogens"] = ";".join(keyword_matches(text, PATHOGEN_KEYWORDS))
        row["assay_types"] = ";".join(keyword_matches(text, ASSAY_KEYWORDS))
        enriched_rows.append(row)

    with REVIEW_QUEUE_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"Classified {len(enriched_rows)} HPMI review queue rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
