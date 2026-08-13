#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_QUEUE_PATH = PROJECT_ROOT / "papers" / "sources" / "current-program" / "review-queue.csv"
RECORDS_DIR = PROJECT_ROOT / "papers" / "sources" / "current-program" / "records"
PIS_PATH = PROJECT_ROOT / "consortium" / "people" / "pis.yaml"


VIRUS_KEYWORDS = {
    "sars-cov-2": ["sars-cov-2", "covid-19", "covid 19", "coronavirus disease 2019"],
    "sars-cov": ["sars-cov"],
    "mers-cov": ["mers-cov"],
    "influenza": ["influenza", "flu"],
    "rsv": ["respiratory syncytial virus", "rsv"],
    "dengue": ["dengue", "denv"],
    "zika": ["zika", "zikv"],
    "hiv": ["hiv", "human immunodeficiency virus"],
    "ebv": ["epstein-barr", "ebv"],
    "cmv": ["cytomegalovirus", "cmv"],
    "hcv": ["hepatitis c virus", "hcv"],
}

PATHOGEN_KEYWORDS = {
    "pseudomonas_aeruginosa": ["pseudomonas aeruginosa"],
    "mycobacterium_tuberculosis": ["mycobacterium tuberculosis", "tuberculosis", "mtb"],
    "staphylococcus_aureus": ["staphylococcus aureus"],
    "chlamydia_trachomatis": ["chlamydia trachomatis"],
    "clostridioides_difficile": ["clostridioides difficile", "c. difficile"],
    "klebsiella_pneumoniae": ["klebsiella pneumoniae"],
}

ASSAY_KEYWORDS = {
    "crispr_screen": ["crispr", "genome-wide screen", "genetic screen"],
    "proteomics": ["proteomics", "proteomic", "mass spectrometry", "phosphoprote", "interactome"],
    "transcriptomics": ["rna-seq", "transcriptom", "single-cell rna", "scrna-seq"],
    "metabolomics": ["metabolomics", "metabolomic"],
    "epigenomics": ["epigenom", "methylation", "chromatin"],
    "clinical_modeling": ["population pharmacokinetic", "machine learning model", "predictive accuracy"],
}


def load_pi_last_names() -> dict[str, str]:
    # Minimal YAML parsing for the current simple structure.
    mapping: dict[str, str] = {}
    current_name = None
    for line in PIS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:"):
            current_name = stripped.split(":", 1)[1].strip()
            last = current_name.split()[-1].lower()
            mapping[last] = current_name
    return mapping


def keyword_matches(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    matches: list[str] = []
    for label, terms in keyword_map.items():
        if any(term in lowered for term in terms):
            matches.append(label)
    return matches


def infer_pi_candidates(authors: list[str], pi_last_names: dict[str, str]) -> list[str]:
    matches: list[str] = []
    for author in authors:
        parts = author.replace(",", " ").split()
        if not parts:
            continue
        if len(parts) == 2 and parts[1].isupper():
            last = parts[0].lower()
        elif len(parts) == 2 and "." in parts[1]:
            last = parts[0].lower()
        else:
            last = parts[-1].lower()
        if last in pi_last_names and pi_last_names[last] not in matches:
            matches.append(pi_last_names[last])
    return matches


def infer_center(pi_candidates: list[str]) -> str:
    joined = " | ".join(pi_candidates)
    if any(name in joined for name in ["Krogan", "Cox", "Glickman", "Ott", "Sali", "Swaney", "Doudna", "Ideker"]):
        return "HPMI"
    if any(name in joined for name in ["Garcia-Sastre", "Chanda", "Schotsaert", "Medina"]):
        return "SYBIL"
    if any(name in joined for name in ["Andersen", "Garry", "McNamara", "Grant"]):
        return "CViSB"
    if any(name in joined for name in ["Wunderink", "Hauser"]):
        return "SCRIPT"
    if any(name in joined for name in ["Yeaman", "Filler", "Reed", "Johnson"]):
        return "UCLA-Persistent-BSI"
    return ""


def main() -> int:
    pi_last_names = load_pi_last_names()
    rows = list(csv.DictReader(REVIEW_QUEUE_PATH.open(encoding="utf-8")))
    fieldnames = rows[0].keys() if rows else []

    enriched_rows: list[dict[str, str]] = []
    for row in rows:
        record_path = RECORDS_DIR / f"{row['paper_id']}.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
        title = str(record.get("title", "") or row.get("title", ""))
        abstract = str(record.get("abstract", "") or "")
        text = f"{title}\n{abstract}"
        authors = record.get("authors", []) or []
        pi_candidates = infer_pi_candidates(authors, pi_last_names)
        viruses = keyword_matches(text, VIRUS_KEYWORDS)
        pathogens = keyword_matches(text, PATHOGEN_KEYWORDS)
        assays = keyword_matches(text, ASSAY_KEYWORDS)
        center = infer_center(pi_candidates)

        row["pi_candidates"] = ";".join(pi_candidates)
        row["viruses"] = ";".join(viruses)
        row["pathogens"] = ";".join(pathogens)
        row["assay_types"] = ";".join(assays)
        if not row.get("center"):
            row["center"] = center
        enriched_rows.append(row)

    with REVIEW_QUEUE_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"Classified {len(enriched_rows)} review queue rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
