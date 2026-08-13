#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "review-queue.csv"
RECORDS_DIR = PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "records"


VIRUS_KEYWORDS = {
    "sars-cov-2": ["sars-cov-2", "covid-19", "covid 19", "coronavirus disease 2019"],
    "sars-cov": ["sars-cov"],
    "mers-cov": ["mers-cov"],
    "coronavirus": ["coronavirus", "coronaviruses"],
    "influenza": ["influenza", "flu"],
    "rsv": ["respiratory syncytial virus", "rsv"],
    "dengue": ["dengue", "denv"],
    "zika": ["zika", "zikv"],
    "hiv": ["hiv", "human immunodeficiency virus"],
    "ebv": ["epstein-barr", "ebv"],
    "cmv": ["cytomegalovirus", "cmv"],
    "hcv": ["hepatitis c virus", "hcv"],
    "poxvirus": ["poxvirus", "vaccinia"],
}

PATHOGEN_KEYWORDS = {
    "pseudomonas_aeruginosa": ["pseudomonas aeruginosa"],
    "mycobacterium_tuberculosis": ["mycobacterium tuberculosis", "tuberculosis", "mtb"],
    "staphylococcus_aureus": ["staphylococcus aureus"],
    "chlamydia_trachomatis": ["chlamydia trachomatis"],
    "clostridioides_difficile": ["clostridioides difficile", "c. difficile"],
    "klebsiella_pneumoniae": ["klebsiella pneumoniae"],
    "candida_albicans": ["candida albicans"],
    "legionella_pneumophila": ["legionella pneumophila"],
}

ASSAY_KEYWORDS = {
    "crispr_screen": ["crispr", "genome-wide screen", "genetic screen"],
    "proteomics": ["proteomics", "proteomic", "mass spectrometry", "phosphoprote", "interactome"],
    "transcriptomics": ["rna-seq", "transcriptom", "single-cell rna", "scrna-seq"],
    "metabolomics": ["metabolomics", "metabolomic"],
    "epigenomics": ["epigenom", "methylation", "chromatin"],
    "network_modeling": ["network", "systems biology", "modeling", "graph"],
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

    print(f"Classified {len(enriched_rows)} PI backlog review queue rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
