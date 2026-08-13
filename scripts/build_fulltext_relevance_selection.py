#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_CORPUS_PATH = PROJECT_ROOT / "papers" / "derived" / "consortium-subset" / "manifest.csv"
PARSE_MANIFEST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "manifest.csv"
OUTPUT_DIR = PROJECT_ROOT / "papers" / "derived" / "relevance"
OUTPUT_PATH = OUTPUT_DIR / "fulltext-selection.csv"

VIRUS_TERMS = [
    "virus",
    "viral",
    "influenza",
    "coronavirus",
    "sars-cov-2",
    "sars cov 2",
    "sars",
    "covid-19",
    "hiv",
    "dengue",
    "zika",
    "rsv",
    "ebola",
    "hepatitis b virus",
    "hbv",
    "mpox",
    "yellow fever virus",
]

SPECIFIC_VIRUS_TERMS = [
    "influenza",
    "coronavirus",
    "sars-cov-2",
    "sars cov 2",
    "sars",
    "covid-19",
    "hiv",
    "dengue",
    "zika",
    "rsv",
    "ebola",
    "hepatitis b virus",
    "hbv",
    "hcv",
    "hepatitis c virus",
    "mpox",
    "yellow fever virus",
    "flavivirus",
    "h1n1",
    "h3n2",
    "h5n1",
]

MECHANISM_TERMS = [
    "host factor",
    "host factors",
    "host response",
    "pathway",
    "pathways",
    "interaction",
    "interactions",
    "interactome",
    "protein interaction",
    "proteomics",
    "transcriptomics",
    "screen",
    "crispr",
    "dependency",
    "restriction factor",
    "immune evasion",
    "replication",
    "macrophage",
    "alveolar",
    "epithelial",
    "network",
]

STRONG_CROSS_VIRUS_TERMS = [
    "cross-virus",
    "cross virus",
    "multi-virus",
    "multiple viruses",
    "shared host",
    "pan-viral",
    "conserved host",
]

WEAK_CROSS_VIRUS_TERMS = [
    "broad-spectrum",
    "host adaptation",
    "species barriers",
]

OFF_TOPIC_TERMS = [
    "cancer",
    "tumor",
    "tumour",
    "leukemia",
    "ovarian",
    "prostate",
    "fracture",
    "endometriosis",
    "hemodialysis",
    "kidney",
    "retinal",
    "uveitis",
    "spinal",
    "gynecologic",
    "diabetes",
    "breast cancer",
    "acute myeloid leukemia",
]

NON_VIRAL_PATHOGEN_TERMS = [
    "mycobacter",
    "tuberculosis",
    "legionella",
    "bacterial",
    "bacterium",
    "fungal",
    "fungus",
    "parasite",
    "plasmodium",
    "salmonella",
    "listeria",
    "staphylococcus",
    "streptococcus",
    "pneumophila",
    "t gondii",
    "toxoplasma",
    "candida",
]

METHOD_RESOURCE_TERMS = [
    "modeller",
    "modbase",
    "protein structure modeling",
    "comparative protein structure",
    "molecular modeling",
    "ligand docking",
    "database of annotated comparative protein structure models",
    "cryoem map",
]

THERAPEUTIC_CLINICAL_TERMS = [
    "anti-influenza activity",
    "inhibitor",
    "inhibits viral replication",
    "drug discovery",
    "repurposing screen",
    "transplantation",
    "transplant survival",
    "preclinical",
]

LOW_PRIORITY_VIROLOGY_TERMS = [
    "oncolytic virus",
    "cancer therapy",
    "favipiravir",
    "anti-influenza activity",
]

REVIEW_ARTICLE_TERMS = [
    "review",
    "perspective",
    "commentary",
]


def matched_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term in lowered]


def build_body_excerpt(text: str, terms: list[str]) -> str:
    lowered = text.lower()
    for term in terms:
        idx = lowered.find(term)
        if idx != -1:
            start = max(0, idx - 180)
            end = min(len(text), idx + 320)
            return " ".join(text[start:end].split())
    return " ".join(text[:500].split())


def any_title_startswith(title: str, prefixes: list[str]) -> bool:
    lowered = title.lower().strip()
    return any(lowered.startswith(prefix) for prefix in prefixes)


def count_unique_hits(*groups: list[str]) -> int:
    merged: set[str] = set()
    for group in groups:
        merged.update(group)
    return len(merged)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final_rows = {row["paper_id"]: row for row in csv.DictReader(FINAL_CORPUS_PATH.open(encoding="utf-8"))}
    parse_rows = list(csv.DictReader(PARSE_MANIFEST_PATH.open(encoding="utf-8")))

    output_rows: list[dict[str, str]] = []
    for parse_row in parse_rows:
        paper_id = parse_row["paper_id"]
        final_row = final_rows.get(paper_id)
        if final_row is None:
            continue

        body_text = ""
        abstract_text = ""
        if parse_row["normalized_json_path"]:
            payload = json.loads(Path(parse_row["normalized_json_path"]).read_text(encoding="utf-8"))
            abstract_text = payload.get("abstract", "")
            body_text = " ".join(section.get("text", "") for section in payload.get("sections", []))

        title_text = final_row.get("title", "")
        title_abstract_text = "\n".join(
            [
                title_text,
                abstract_text,
            ]
        )
        full_text = "\n".join(
            [
                title_text,
                abstract_text,
                body_text,
            ]
        )

        title_virus_hits = matched_terms(title_text, VIRUS_TERMS)
        title_non_viral_hits = matched_terms(title_text, NON_VIRAL_PATHOGEN_TERMS)
        title_abstract_virus_hits = matched_terms(title_abstract_text, VIRUS_TERMS)
        title_abstract_specific_virus_hits = matched_terms(title_abstract_text, SPECIFIC_VIRUS_TERMS)
        title_abstract_mechanism_hits = matched_terms(title_abstract_text, MECHANISM_TERMS)
        virus_hits = matched_terms(full_text, VIRUS_TERMS)
        mechanism_hits = matched_terms(full_text, MECHANISM_TERMS)
        strong_cross_hits = matched_terms(full_text, STRONG_CROSS_VIRUS_TERMS)
        weak_cross_hits = matched_terms(full_text, WEAK_CROSS_VIRUS_TERMS)
        off_topic_hits = matched_terms(full_text, OFF_TOPIC_TERMS)
        non_viral_hits = matched_terms(full_text, NON_VIRAL_PATHOGEN_TERMS)
        method_hits = matched_terms(title_abstract_text, METHOD_RESOURCE_TERMS)
        therapeutic_hits = matched_terms(title_abstract_text, THERAPEUTIC_CLINICAL_TERMS)
        low_priority_virology_hits = matched_terms(title_abstract_text, LOW_PRIORITY_VIROLOGY_TERMS)
        review_hits = matched_terms(title_abstract_text, REVIEW_ARTICLE_TERMS)

        decision = "not_relevant"
        reason = "full text did not support viral host-mechanism relevance"
        if any_title_startswith(title_text, ["correction:", "erratum:", "retraction:"]):
            reason = "publication type is a correction/erratum rather than a primary paper"
        elif matched_terms(title_text, OFF_TOPIC_TERMS) and not title_virus_hits and not title_abstract_specific_virus_hits:
            reason = f"title is dominated by an off-target disease area: {', '.join(matched_terms(title_text, OFF_TOPIC_TERMS)[:5])}"
        elif title_non_viral_hits:
            reason = f"title is dominated by a non-viral pathogen context: {', '.join(title_non_viral_hits[:5])}"
        elif non_viral_hits and not title_abstract_specific_virus_hits:
            reason = f"non-viral pathogen focus dominates title/abstract/full text: {', '.join(non_viral_hits[:5])}"
        elif method_hits and not title_abstract_virus_hits:
            reason = f"generic method/resource paper without clear virus focus in title/abstract: {', '.join(method_hits[:5])}"
        elif off_topic_hits and not title_abstract_virus_hits:
            reason = f"title/abstract/full text looks off-target for the virus question: {', '.join(off_topic_hits[:5])}"
        elif low_priority_virology_hits and not title_abstract_mechanism_hits:
            reason = f"virus-related but low-priority for host-pathway discovery: {', '.join(low_priority_virology_hits[:5])}"
        elif therapeutic_hits and not title_abstract_mechanism_hits and not strong_cross_hits:
            decision = "maybe"
            reason = f"virus-relevant but primarily therapeutic/clinical rather than host-mechanism focused: {', '.join(therapeutic_hits[:5])}"
        elif strong_cross_hits and (title_abstract_virus_hits or title_abstract_specific_virus_hits):
            decision = "relevant"
            reason = f"explicit cross-virus/shared-host full-text language: {', '.join(strong_cross_hits[:5])}"
        elif weak_cross_hits and title_abstract_specific_virus_hits and title_abstract_mechanism_hits and not therapeutic_hits:
            decision = "relevant"
            reason = (
                "virus-focused title/abstract plus weaker cross-virus framing in body: "
                f"{', '.join((weak_cross_hits + title_abstract_specific_virus_hits + title_abstract_mechanism_hits)[:6])}"
            )
        elif weak_cross_hits and title_abstract_specific_virus_hits and therapeutic_hits:
            decision = "maybe"
            reason = (
                "virus-focused paper with broad-spectrum or cross-virus language, but mainly therapeutic/clinical framing: "
                f"{', '.join((weak_cross_hits + therapeutic_hits + title_abstract_specific_virus_hits)[:6])}"
            )
        elif (
            count_unique_hits(title_abstract_specific_virus_hits, title_abstract_virus_hits) >= 1
            and count_unique_hits(title_abstract_mechanism_hits) >= 2
        ):
            decision = "relevant"
            reason = (
                "viral context plus mechanism-rich title/abstract: "
                f"{', '.join((title_abstract_specific_virus_hits + title_abstract_virus_hits + title_abstract_mechanism_hits)[:6])}"
            )
        elif title_abstract_specific_virus_hits and title_abstract_mechanism_hits:
            decision = "maybe"
            reason = (
                "virus-focused title/abstract with some host-mechanism signal: "
                f"{', '.join((title_abstract_specific_virus_hits + title_abstract_mechanism_hits)[:6])}"
            )
        elif title_abstract_virus_hits and len(mechanism_hits) >= 2 and not review_hits:
            decision = "maybe"
            reason = (
                "virus context appears stronger in body than title/abstract; possible mechanistic paper to inspect: "
                f"{', '.join((title_abstract_virus_hits + mechanism_hits)[:6])}"
            )
        elif title_abstract_virus_hits and review_hits:
            decision = "maybe"
            reason = f"virus-focused review/perspective that may help background framing: {', '.join(review_hits[:5])}"

        output_rows.append(
            {
                "paper_id": paper_id,
                "pmid": final_row["pmid"],
                "source_collection": final_row["source_collection"],
                "year": final_row["year"],
                "title": final_row["title"],
                "center": final_row["center"],
                "pi_candidates": final_row["pi_candidates"],
                "previous_subset_reason": final_row["subset_reason"],
                "parse_status": parse_row["parse_status"],
                "body_word_count": parse_row["body_word_count"],
                "decision": decision,
                "decision_reason": reason,
                "title_abstract_virus_hits": ";".join(title_abstract_virus_hits),
                "title_abstract_specific_virus_hits": ";".join(title_abstract_specific_virus_hits),
                "title_abstract_mechanism_hits": ";".join(title_abstract_mechanism_hits),
                "virus_hits": ";".join(virus_hits),
                "mechanism_hits": ";".join(mechanism_hits),
                "cross_virus_hits": ";".join(strong_cross_hits + weak_cross_hits),
                "off_topic_hits": ";".join(off_topic_hits),
                "non_viral_pathogen_hits": ";".join(non_viral_hits),
                "method_resource_hits": ";".join(method_hits),
                "therapeutic_clinical_hits": ";".join(therapeutic_hits),
                "body_excerpt": build_body_excerpt(
                    body_text,
                    strong_cross_hits or weak_cross_hits or mechanism_hits or virus_hits or off_topic_hits,
                ),
            }
        )

    output_rows.sort(key=lambda row: (row["decision"], int(row["body_word_count"] or "0")), reverse=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "pmid",
                "source_collection",
                "year",
                "title",
                "center",
                "pi_candidates",
                "previous_subset_reason",
                "parse_status",
                "body_word_count",
                "decision",
                "decision_reason",
                "title_abstract_virus_hits",
                "title_abstract_specific_virus_hits",
                "title_abstract_mechanism_hits",
                "virus_hits",
                "mechanism_hits",
                "cross_virus_hits",
                "off_topic_hits",
                "non_viral_pathogen_hits",
                "method_resource_hits",
                "therapeutic_clinical_hits",
                "body_excerpt",
            ],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote full-text relevance selection to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
