#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEVANT_PAPERS_PATH = PROJECT_ROOT / "outputs" / "reports" / "fulltext" / "fulltext-relevant-papers.csv"
PARSE_MANIFEST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "manifest.csv"
NORMALIZED_DIR = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "normalized"
CORE_OUTPUT_PATH = PROJECT_ROOT / "papers" / "derived" / "relevance" / "relevant-paper-core.csv"
DATASET_OUTPUT_PATH = PROJECT_ROOT / "datasets" / "manifest.csv"
RESOURCE_OUTPUT_PATH = PROJECT_ROOT / "resources" / "manifest.csv"
SUMMARY_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "reports" / "core" / "relevant-core-summary.md"
PRIORITY_EXPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "core" / "relevant-dataset-resource-priority.csv"


VIRUS_PATTERNS = {
    "influenza_a": [r"\binfluenza a\b", r"\biav\b", r"\bh1n1\b", r"\bh3n2\b", r"\bh5n1\b"],
    "sars_cov_2": [r"\bsars-cov-2\b", r"\bcovid-19\b", r"\bcovid 19\b"],
    "sars_cov_1": [
        r"\bsars-cov-1\b",
        r"\bsars-cov\b(?!-2)",
        r"\bsars cov\b(?! 2)",
        r"severe acute respiratory syndrome coronavirus(?! 2)",
    ],
    "mers_cov": [r"\bmers-cov\b", r"\bmers\b"],
    "hiv": [r"\bhiv-1\b", r"\bhiv\b", r"\bhuman immunodeficiency virus\b"],
    "dengue": [r"\bdengue\b", r"\bdenv\b"],
    "zika": [r"\bzika\b", r"\bzika virus\b"],
    "rsv": [r"\brsv\b", r"\brespiratory syncytial virus\b"],
    "ebola": [r"\bebola\b", r"\bebov\b"],
    "hbv": [r"\bhepatitis b virus\b", r"\bhbv\b"],
    "hcv": [r"\bhepatitis c virus\b", r"\bhcv\b"],
    "coronavirus_general": [r"\bcoronavirus\b", r"\bcoronaviruses\b"],
    "mpox": [r"\bmpox\b", r"\bmonkeypox\b"],
    "yellow_fever": [r"\byellow fever virus\b"],
    "flavivirus_general": [r"\bflavivirus\b", r"\bflaviviruses\b"],
    "hepatitis_a": [r"\bhepatitis a virus\b", r"\bhav\b"],
}

HOST_SYSTEM_PATTERNS = {
    "A549_cells": [r"\ba549\b"],
    "Calu-3_cells": [r"\bcalu-?3\b"],
    "HEK293T_cells": [r"\b293t\b", r"\bhek293t\b"],
    "Huh7_cells": [r"\bhuh-?7\b"],
    "Vero_E6_cells": [r"\bvero e6\b", r"\bvero\b"],
    "NHBE_cells": [r"\bnhbe\b", r"\bnormal human bronchial epithelial\b"],
    "primary_CD4_T_cells": [r"\bprimary human cd4\+? t cells?\b", r"\bcd4\+? t cells?\b"],
    "PBMCs": [r"\bpbmcs?\b", r"\bperipheral blood mononuclear cells?\b"],
    "macrophages": [r"\bmacrophages?\b", r"\bmonocyte-derived macrophages?\b", r"\balveolar macrophages?\b"],
    "human_lung_tissue": [r"\bhuman lung\b", r"\blung tissue\b"],
    "airway_epithelium": [r"\bairway epithelium\b", r"\bairway epithelial\b"],
    "organoids": [r"\borganoid\b", r"\borganoids\b"],
    "mice": [r"\bmice\b", r"\bmouse\b", r"\bmurine\b"],
    "ferrets": [r"\bferrets?\b"],
    "hamsters": [r"\bhamsters?\b"],
    "rhesus_macaques": [r"\brhesus macaques?\b", r"\bmacaques?\b"],
    "bat_cells_or_hosts": [r"\bbat\b", r"\bbats\b"],
    "human_patients": [r"\bpatients?\b", r"\bclinical\b", r"\bcohort\b"],
}

ASSAY_PATTERNS = {
    "AP-MS_interactome": [r"affinity purification[- ]mass spectrometry", r"\bap-ms\b"],
    "proximity_labeling": [r"\bbioid\b", r"proximity interactome", r"proximity labeling"],
    "proteomics": [r"\bproteomics?\b", r"mass spectrometry"],
    "phosphoproteomics": [r"\bphosphoproteomics?\b", r"phosphorylation landscape"],
    "transcriptomics": [r"\btranscriptomics?\b", r"\brna-seq\b", r"\brna seq\b"],
    "single_cell": [r"\bsingle-cell\b", r"\bsingle cell\b", r"\bscRNA-seq\b"],
    "CRISPR_screen": [r"\bcrispr\b", r"\bgenome-wide crispr screen\b", r"\bgenetic screens?\b"],
    "protein_interaction_mapping": [r"protein interaction map", r"protein interaction network", r"interactome"],
    "network_analysis": [r"\bnetwork\b", r"\bnetworks\b", r"\bnetwork rewiring\b"],
    "imaging": [r"\bimaging\b", r"\bimmunopet\b", r"\blive imaging\b", r"\bmicroscopy\b"],
    "genetic_perturbation": [r"\bsiRNA\b", r"\bknockdown\b", r"\bperturbation\b"],
    "proteogenomics": [r"\bproteogenomic\b", r"\bproteogenomics\b"],
}

DATASET_PATTERNS = {
    "GEO": re.compile(r"\bGSE\d{3,}\b"),
    "SRA": re.compile(r"\bSRP\d{3,}\b"),
    "BioProject": re.compile(r"\bPRJNA\d{3,}\b"),
    "PRIDE": re.compile(r"\bPXD\d{3,}\b"),
    "ArrayExpress": re.compile(r"\bE-MTAB-\d+\b"),
    "MassIVE": re.compile(r"\bMSV\d{6,}\b"),
    "Single_Cell_Portal": re.compile(r"\bSCP\d+\b"),
}

RESOURCE_PATTERNS = {
    "GitHub": re.compile(r"github\.com/[^\s\)\]>]+", re.I),
    "NDEx": re.compile(r"ndexbio\.org/[^\s\)\]>]+", re.I),
    "Zenodo": re.compile(r"zenodo\.org/[^\s\)\]>]+", re.I),
    "Figshare": re.compile(r"figshare\.com/[^\s\)\]>]+", re.I),
    "Synapse": re.compile(r"synapse\.org/[^\s\)\]>]+", re.I),
}

PRIORITY_ORDER = {
    "tier_1": 3,
    "tier_2": 2,
    "tier_3": 1,
}


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8")))


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def find_labels(text: str, pattern_map: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    labels: list[str] = []
    for label, patterns in pattern_map.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                labels.append(label)
                break
    return labels


def find_accessions(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for repository, pattern in DATASET_PATTERNS.items():
        for accession in sorted(set(pattern.findall(text))):
            found.append((repository, accession))
    return found


def find_resources(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for resource_type, pattern in RESOURCE_PATTERNS.items():
        for url in sorted(set(pattern.findall(text))):
            found.append((resource_type, url.rstrip(".,);]")))
    return found


def infer_reuse_value(accession_count: int, assay_count: int, virus_count: int, resource_count: int) -> str:
    if accession_count >= 2 or (accession_count >= 1 and assay_count >= 2):
        return "high"
    if accession_count >= 1 or assay_count >= 2 or resource_count >= 1:
        return "medium"
    if virus_count >= 1:
        return "low"
    return "unknown"


def infer_pathway_relevance(title: str, abstract: str, body: str) -> str:
    text = f"{title}\n{abstract}\n{body}".lower()
    strong_terms = [
        "pan-viral",
        "shared host",
        "cross-virus",
        "cross virus",
        "network rewiring",
        "host response",
        "host factors",
        "host factor",
        "pathway",
        "pathways",
        "interactome",
        "protein interaction",
    ]
    hit_count = sum(1 for term in strong_terms if term in text)
    if hit_count >= 5:
        return "high"
    if hit_count >= 2:
        return "medium"
    return "low"


def infer_access_friction(parse_source_type: str, accession_count: int, resource_count: int) -> str:
    if accession_count >= 1 and parse_source_type == "pmc_xml":
        return "low"
    if accession_count >= 1 or resource_count >= 1:
        return "medium"
    return "high"


def infer_priority_bucket(
    accession_count: int,
    resource_count: int,
    reuse_value: str,
    pathway_relevance: str,
) -> str:
    if accession_count >= 1 and pathway_relevance in {"high", "medium"}:
        return "tier_1"
    if resource_count >= 1 and reuse_value in {"high", "medium"}:
        return "tier_1"
    if reuse_value == "high" or pathway_relevance == "high":
        return "tier_2"
    if accession_count >= 1 or resource_count >= 1 or reuse_value == "medium":
        return "tier_2"
    return "tier_3"


def build_dataset_title(paper_title: str, repository: str, accession: str, assays: list[str]) -> str:
    assay_text = assays[0] if assays else "dataset"
    return f"{paper_title} [{repository} {accession}; {assay_text}]"


def build_resource_name(title: str, resource_type: str, url: str) -> str:
    if resource_type == "GitHub":
        return url.split("/")[-1]
    if resource_type == "NDEx":
        return f"NDEx resource for {title[:80]}"
    return f"{resource_type} resource for {title[:80]}"


def main() -> int:
    relevant_rows = load_csv_rows(RELEVANT_PAPERS_PATH)
    parse_manifest = {row["paper_id"]: row for row in load_csv_rows(PARSE_MANIFEST_PATH)}

    timestamp = datetime.now(timezone.utc).isoformat()
    core_rows: list[dict[str, str]] = []
    dataset_rows: list[dict[str, str]] = []
    resource_rows: list[dict[str, str]] = []

    counters = Counter()

    for row in relevant_rows:
        paper_id = row["paper_id"]
        pmid = row["pmid"]
        normalized_path = NORMALIZED_DIR / f"{pmid}.json"
        if not normalized_path.exists():
            counters["missing_normalized"] += 1
            continue

        payload = json.loads(normalized_path.read_text(encoding="utf-8"))
        title = payload.get("title", "") or row.get("title", "")
        abstract = payload.get("abstract", "")
        body = " ".join(section.get("text", "") for section in payload.get("sections", []))
        raw_text = payload.get("raw_text", "")
        title_abstract_text = normalize_whitespace("\n".join([title, abstract]))
        full_text = normalize_whitespace("\n".join([title, abstract, body, raw_text]))

        viruses = find_labels(title_abstract_text, VIRUS_PATTERNS)
        host_systems = find_labels(full_text, HOST_SYSTEM_PATTERNS)
        assays = find_labels(full_text, ASSAY_PATTERNS)
        datasets = find_accessions(full_text)
        resources = find_resources(full_text)

        counters["papers_processed"] += 1
        counters["papers_with_dataset_accessions"] += int(bool(datasets))
        counters["papers_with_resource_links"] += int(bool(resources))
        counters["papers_with_assay_hits"] += int(bool(assays))
        counters["papers_with_host_system_hits"] += int(bool(host_systems))

        parse_row = parse_manifest.get(paper_id, {})
        code_available = any(resource_type == "GitHub" for resource_type, _ in resources)
        reuse_value = infer_reuse_value(len(datasets), len(assays), len(viruses), len(resources))
        pathway_relevance = infer_pathway_relevance(title, abstract, body)
        access_friction = infer_access_friction(parse_row.get("parse_source_type", ""), len(datasets), len(resources))
        priority_bucket = infer_priority_bucket(len(datasets), len(resources), reuse_value, pathway_relevance)

        core_rows.append(
            {
                "paper_id": paper_id,
                "pmid": pmid,
                "year": row.get("year", ""),
                "source_collection": row.get("source_collection", ""),
                "center": row.get("center", ""),
                "pi_candidates": row.get("pi_candidates", ""),
                "title": row.get("title", title),
                "decision_reason": row.get("decision_reason", ""),
                "parse_status": parse_row.get("parse_status", ""),
                "parse_source_type": parse_row.get("parse_source_type", ""),
                "viruses": ";".join(viruses),
                "host_systems": ";".join(host_systems),
                "assay_types": ";".join(assays),
                "dataset_repositories": ";".join(sorted({repository for repository, _ in datasets})),
                "dataset_accessions": ";".join(f"{repository}:{accession}" for repository, accession in datasets),
                "resource_types": ";".join(sorted({resource_type for resource_type, _ in resources})),
                "resource_links": ";".join(url for _, url in resources),
                "raw_data_available": "true" if datasets else "false",
                "processed_data_available": "true" if datasets else "false",
                "code_available": "true" if code_available else "false",
                "reuse_value": reuse_value,
                "pathway_relevance": pathway_relevance,
                "access_friction": access_friction,
                "priority_bucket": priority_bucket,
            }
        )

        for repository, accession in datasets:
            dataset_id = f"{paper_id}-{repository.lower()}-{accession.lower()}"
            dataset_rows.append(
                {
                    "dataset_id": dataset_id,
                    "source_paper_id": paper_id,
                    "repository": repository,
                    "accession": accession,
                    "title": build_dataset_title(row.get("title", title), repository, accession, assays),
                    "assay_type": assays[0] if assays else "",
                    "host_system": ";".join(host_systems[:3]),
                    "pathogen": ";".join(viruses[:3]),
                    "reuse_value": reuse_value,
                    "status": "candidate",
                }
            )

        for resource_type, url in resources:
            resource_digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
            resource_id = f"{paper_id}-{resource_type.lower()}-{resource_digest}"
            resource_rows.append(
                {
                    "resource_id": resource_id,
                    "source_paper_id": paper_id,
                    "resource_type": resource_type,
                    "name": build_resource_name(row.get("title", title), resource_type, url),
                    "url": url,
                    "notes": f"Auto-extracted from normalized full text on {timestamp}",
                    "status": "candidate",
                }
            )

    core_rows.sort(
        key=lambda record: (
            PRIORITY_ORDER.get(record["priority_bucket"], 0),
            record["reuse_value"],
            record["pathway_relevance"],
            record["year"],
            record["paper_id"],
        ),
        reverse=True,
    )
    dataset_rows.sort(key=lambda record: (record["repository"], record["accession"], record["source_paper_id"]))
    resource_rows.sort(key=lambda record: (record["resource_type"], record["source_paper_id"], record["url"]))

    CORE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATASET_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESOURCE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRIORITY_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with CORE_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "pmid",
                "year",
                "source_collection",
                "center",
                "pi_candidates",
                "title",
                "decision_reason",
                "parse_status",
                "parse_source_type",
                "viruses",
                "host_systems",
                "assay_types",
                "dataset_repositories",
                "dataset_accessions",
                "resource_types",
                "resource_links",
                "raw_data_available",
                "processed_data_available",
                "code_available",
                "reuse_value",
                "pathway_relevance",
                "access_friction",
                "priority_bucket",
            ],
        )
        writer.writeheader()
        writer.writerows(core_rows)

    with DATASET_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset_id",
                "source_paper_id",
                "repository",
                "accession",
                "title",
                "assay_type",
                "host_system",
                "pathogen",
                "reuse_value",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(dataset_rows)

    with RESOURCE_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "resource_id",
                "source_paper_id",
                "resource_type",
                "name",
                "url",
                "notes",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(resource_rows)

    with PRIORITY_EXPORT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "pmid",
                "priority_bucket",
                "reuse_value",
                "pathway_relevance",
                "source_collection",
                "center",
                "pi_candidates",
                "title",
                "viruses",
                "host_systems",
                "assay_types",
                "dataset_accessions",
                "resource_types",
                "resource_links",
            ],
        )
        writer.writeheader()
        for record in core_rows:
            if not record["dataset_accessions"] and not record["resource_links"]:
                continue
            writer.writerow({field: record.get(field, "") for field in writer.fieldnames})

    virus_counter = Counter()
    assay_counter = Counter()
    host_counter = Counter()
    repo_counter = Counter()
    resource_counter = Counter()
    priority_counter = Counter()
    for record in core_rows:
        for value in filter(None, record["viruses"].split(";")):
            virus_counter[value] += 1
        for value in filter(None, record["assay_types"].split(";")):
            assay_counter[value] += 1
        for value in filter(None, record["host_systems"].split(";")):
            host_counter[value] += 1
        for value in filter(None, record["dataset_repositories"].split(";")):
            repo_counter[value] += 1
        for value in filter(None, record["resource_types"].split(";")):
            resource_counter[value] += 1
        priority_counter[record["priority_bucket"]] += 1

    with SUMMARY_OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        handle.write("# Relevant Paper Core Summary\n\n")
        handle.write("This report summarizes the structured extraction pass over the 215 full-text-relevant papers.\n\n")
        handle.write("## Counts\n\n")
        handle.write(f"- papers processed: `{counters['papers_processed']}`\n")
        handle.write(f"- papers with dataset accessions: `{counters['papers_with_dataset_accessions']}`\n")
        handle.write(f"- papers with resource links: `{counters['papers_with_resource_links']}`\n")
        handle.write(f"- papers with assay hits: `{counters['papers_with_assay_hits']}`\n")
        handle.write(f"- papers with host-system hits: `{counters['papers_with_host_system_hits']}`\n")
        handle.write(f"- dataset rows written: `{len(dataset_rows)}`\n")
        handle.write(f"- resource rows written: `{len(resource_rows)}`\n\n")

        handle.write("## Priority Buckets\n\n")
        for label in ["tier_1", "tier_2", "tier_3"]:
            count = priority_counter.get(label, 0)
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("## Top Viruses\n\n")
        for label, count in virus_counter.most_common(12):
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("\n## Top Assay Signals\n\n")
        for label, count in assay_counter.most_common(12):
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("\n## Top Host-System Signals\n\n")
        for label, count in host_counter.most_common(12):
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("\n## Dataset Repositories\n\n")
        for label, count in repo_counter.most_common():
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("\n## Resource Types\n\n")
        for label, count in resource_counter.most_common():
            handle.write(f"- `{label}`: `{count}`\n")

        handle.write("\n## Tier 1 Starting Papers\n\n")
        for record in core_rows:
            if record["priority_bucket"] != "tier_1":
                continue
            handle.write(
                f"- `{record['paper_id']}` {record['title']}\n"
                f"  reuse={record['reuse_value']}; pathway={record['pathway_relevance']}; "
                f"datasets={record['dataset_accessions'] or 'none'}; resources={record['resource_types'] or 'none'}\n"
            )
            if handle.tell() > 12000:
                break

    print(f"Wrote relevant paper core table to {CORE_OUTPUT_PATH}")
    print(f"Wrote dataset candidates to {DATASET_OUTPUT_PATH}")
    print(f"Wrote resource candidates to {RESOURCE_OUTPUT_PATH}")
    print(f"Wrote summary report to {SUMMARY_OUTPUT_PATH}")
    print(f"Wrote dataset/resource priority export to {PRIORITY_EXPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
