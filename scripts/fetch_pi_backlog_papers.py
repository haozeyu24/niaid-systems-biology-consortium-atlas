#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import subprocess
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PI_BACKLOG_DIR = PROJECT_ROOT / "papers" / "sources" / "pi-backlog"
RECORDS_DIR = PI_BACKLOG_DIR / "records"
MANIFEST_PATH = PI_BACKLOG_DIR / "manifest.csv"
CURRENT_MANIFEST_PATH = PROJECT_ROOT / "papers" / "sources" / "current-program" / "manifest.csv"
HPMI_MANIFEST_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "manifest.csv"
PIS_PATH = PROJECT_ROOT / "consortium" / "people" / "pis.yaml"
SEARCH_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "literature" / "pi-backlog-search-summary.csv"

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_RATE_LIMIT_SECONDS = 0.34
START_YEAR = 2006
DATE_RANGE_QUERY = f'("{START_YEAR}/01/01"[Date - Publication] : "3000"[Date - Publication])'

PI_QUERY_OVERRIDES = {
    "Melissa Johnson": '("Johnson Melissa"[Author] OR "Melissa Johnson"[Author]) AND (UCLA[Affiliation] OR "University of California Los Angeles"[Affiliation])',
    "Elaine Reed": '("Reed Elaine"[Author] OR "Elaine Reed"[Author]) AND (UCLA[Affiliation] OR "University of California Los Angeles"[Affiliation])',
    "Jeffrey Cox": '("Cox JS"[Author] OR "Cox Jeffrey"[Author] OR "Jeffrey Cox"[Author]) AND (UCSF[Affiliation] OR "University of California San Francisco"[Affiliation])',
    "Michael Yeaman": '("Yeaman MR"[Author] OR "Yeaman Michael"[Author] OR "Michael Yeaman"[Author]) AND (UCLA[Affiliation] OR "University of California Los Angeles"[Affiliation])',
}


def fetch_url(url: str) -> bytes:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                [
                    "curl",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--location",
                    "--max-time",
                    "60",
                    "--user-agent",
                    "niaid-systems-biology-consortium-atlas/0.1 (public metadata ingest)",
                    url,
                ],
                check=True,
                capture_output=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as error:
            last_error = error
            print(f"curl attempt {attempt} failed for {url}", flush=True)
            time.sleep(attempt)
    if last_error is not None:
        raise last_error
    raise RuntimeError("unreachable fetch_url failure")


def text_or_none(value: str | None) -> str:
    return value.strip() if value else ""


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def paper_id_from_pmid(pmid: str) -> str:
    return f"pmid-{pmid}"


def year_from_pubdate(pubdate: str) -> str:
    if not pubdate:
        return ""
    for token in pubdate.replace("/", " ").replace("-", " ").split():
        if token.isdigit() and len(token) == 4:
            return token
    return ""


def load_existing_pmids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["pmid"] for row in csv.DictReader(handle) if row.get("pmid")}


def parse_people() -> list[dict[str, str]]:
    people: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in PIS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- name:"):
            if current:
                people.append(current)
            current = {"name": stripped.split(":", 1)[1].strip(), "center": "", "institution": ""}
        elif current and stripped.startswith("institution:"):
            current["institution"] = stripped.split(":", 1)[1].strip()
        elif current and stripped.startswith("center:"):
            current["center"] = stripped.split(":", 1)[1].strip()
    if current:
        people.append(current)
    return people


def build_author_query(name: str) -> str:
    parts = name.split()
    last = parts[-1]
    initials = "".join(part[0] for part in parts[:-1] if part)
    first = parts[0]
    terms = [f'"{last} {initials}"[Author]', f'"{last} {first}"[Author]', f'"{name}"[Author]']
    return "(" + " OR ".join(dict.fromkeys(terms)) + ")"


def build_pi_query(person: dict[str, str]) -> str:
    base_query = PI_QUERY_OVERRIDES.get(person["name"], build_author_query(person["name"]))
    return f"{base_query} AND {DATE_RANGE_QUERY}"


def pubmed_search(query: str) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": "10000",
        "retmode": "json",
        "sort": "date",
    }
    url = f"{PUBMED_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    payload = json.loads(fetch_url(url).decode("utf-8"))
    return payload["esearchresult"]["idlist"]


def fetch_summaries(pmids: list[str]) -> list[dict]:
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    url = f"{PUBMED_SUMMARY_URL}?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(fetch_url(url))
    records = []
    for docsum in root.findall(".//DocSum"):
        record: dict[str, object] = {
            "authors": [],
            "article_ids": {},
            "full_journal_name": "",
            "pubdate": "",
            "title": "",
        }
        uid = docsum.findtext("Id", default="")
        record["pmid"] = uid
        for item in docsum.findall("Item"):
            name = item.attrib.get("Name")
            if name == "Title":
                record["title"] = text_or_none(item.text)
            elif name == "PubDate":
                record["pubdate"] = text_or_none(item.text)
            elif name == "FullJournalName":
                record["full_journal_name"] = text_or_none(item.text)
            elif name == "AuthorList":
                record["authors"] = [text_or_none(child.text) for child in item.findall("Item") if child.text]
            elif name == "ArticleIds":
                article_ids: dict[str, str] = {}
                for child in item.findall("Item"):
                    id_type = child.attrib.get("Name")
                    if id_type and child.text:
                        article_ids[id_type] = text_or_none(child.text)
                record["article_ids"] = article_ids
        records.append(record)
    return records


def flatten_abstract_text(abstract_node: ET.Element | None) -> str:
    if abstract_node is None:
        return ""
    parts: list[str] = []
    for abstract_text in abstract_node.findall("AbstractText"):
        label = text_or_none(abstract_text.attrib.get("Label"))
        text = "".join(abstract_text.itertext()).strip()
        if not text:
            continue
        if label:
            parts.append(f"{label}: {text}")
        else:
            parts.append(text)
    return "\n\n".join(parts).strip()


def fetch_abstracts(pmids: list[str]) -> dict[str, str]:
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    url = f"{PUBMED_FETCH_URL}?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(fetch_url(url))
    abstracts: dict[str, str] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//MedlineCitation/PMID", default="").strip()
        abstract = flatten_abstract_text(article.find(".//Article/Abstract"))
        if pmid:
            abstracts[pmid] = abstract
    return abstracts


def build_pi_index(existing_pmids: set[str]) -> tuple[dict[str, dict[str, object]], list[dict[str, str]]]:
    index: dict[str, dict[str, object]] = {}
    summary_rows: list[dict[str, str]] = []

    for person in parse_people():
        query = build_pi_query(person)
        print(f"Searching PI backlog for {person['name']} ({person['center']})", flush=True)
        pmids = pubmed_search(query)
        overlap_count = sum(1 for pmid in pmids if pmid in existing_pmids)
        new_count = 0
        for pmid in pmids:
            if pmid in existing_pmids:
                continue
            new_count += 1
            entry = index.setdefault(
                pmid,
                {
                    "matched_pis": [],
                    "matched_centers": [],
                    "route_queries": [],
                },
            )
            if person["name"] not in entry["matched_pis"]:
                entry["matched_pis"].append(person["name"])
            if person["center"] and person["center"] not in entry["matched_centers"]:
                entry["matched_centers"].append(person["center"])
            entry["route_queries"].append(query)

        summary_rows.append(
            {
                "pi_name": person["name"],
                "center": person["center"],
                "institution": person["institution"],
                "query": query,
                "pubmed_hits_last_20_years": str(len(pmids)),
                "overlap_with_program_or_hpmi": str(overlap_count),
                "nonoverlap_hits_added_to_backlog": str(new_count),
            }
        )
        print(
            f"  hits={len(pmids)} overlap={overlap_count} added={new_count}",
            flush=True,
        )
        time.sleep(NCBI_RATE_LIMIT_SECONDS)

    return index, summary_rows


def write_search_summary(rows: list[dict[str, str]]) -> None:
    SEARCH_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SEARCH_SUMMARY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "pi_name",
                "center",
                "institution",
                "query",
                "pubmed_hits_last_20_years",
                "overlap_with_program_or_hpmi",
                "nonoverlap_hits_added_to_backlog",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def reset_records_dir() -> None:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    for path in RECORDS_DIR.glob("*.json"):
        path.unlink()


def write_record(summary: dict, abstract: str, matched_pis: list[str], matched_centers: list[str], route_queries: list[str]) -> dict[str, str]:
    pmid = str(summary["pmid"])
    article_ids = summary.get("article_ids", {})
    if not isinstance(article_ids, dict):
        article_ids = {}
    doi = str(article_ids.get("doi", ""))
    pmcid = str(article_ids.get("pmc", ""))
    title = str(summary.get("title", "")).strip()
    pubdate = str(summary.get("pubdate", "")).strip()
    year = year_from_pubdate(pubdate)
    paper_id = paper_id_from_pmid(pmid)

    record = {
        "paper_id": paper_id,
        "title": title,
        "abstract": abstract,
        "authors": summary.get("authors", []),
        "year": int(year) if year else None,
        "journal": str(summary.get("full_journal_name", "")).strip(),
        "source_collection": "pi-backlog",
        "center": matched_centers[0] if len(matched_centers) == 1 else "",
        "pi_candidates": matched_pis,
        "pathogens": [],
        "viruses": [],
        "assay_types": [],
        "identifiers": {"pmid": pmid, "pmcid": pmcid, "doi": doi},
        "links": {
            "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pmc": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else "",
            "publisher": f"https://doi.org/{doi}" if doi else "",
        },
        "collection_route": ["pi_author_backlog"],
        "extraction_status": {
            "full_text_status": "unknown",
            "dataset_scan_status": "pending",
            "dataset_validation_status": "pending",
            "resource_scan_status": "pending",
        },
        "provenance": {
            "source_query_type": "pi_author_query",
            "route_queries": route_queries,
            "imported_at": time.strftime("%Y-%m-%d"),
        },
    }

    (RECORDS_DIR / f"{paper_id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return {
        "paper_id": paper_id,
        "title": title,
        "pmid": pmid,
        "doi": doi,
        "matched_pis": ";".join(matched_pis),
        "matched_centers": ";".join(matched_centers),
        "collection_route": "pi_author_backlog",
        "year": year,
        "paper_status": "metadata_ingested",
        "abstract_length": str(len(abstract)),
        "dataset_scan_status": "pending",
        "resource_scan_status": "pending",
    }


def write_manifest(rows: list[dict[str, str]]) -> None:
    rows = sorted(rows, key=lambda row: (row["year"], row["pmid"]), reverse=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "title",
                "pmid",
                "doi",
                "matched_pis",
                "matched_centers",
                "collection_route",
                "year",
                "paper_status",
                "abstract_length",
                "dataset_scan_status",
                "resource_scan_status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    existing_pmids = load_existing_pmids(CURRENT_MANIFEST_PATH) | load_existing_pmids(HPMI_MANIFEST_PATH)
    pi_index, summary_rows = build_pi_index(existing_pmids)
    pmids = list(pi_index.keys())
    print(f"Fetching metadata for {len(pmids)} non-overlapping backlog PMIDs", flush=True)

    reset_records_dir()
    manifest_rows: list[dict[str, str]] = []
    for batch in batched(pmids, 200):
        print(f"  fetching batch of {len(batch)} PMIDs", flush=True)
        summaries = fetch_summaries(batch)
        abstracts = fetch_abstracts(batch)
        for summary in summaries:
            pmid = str(summary["pmid"])
            manifest_rows.append(
                write_record(
                    summary,
                    abstracts.get(pmid, ""),
                    list(pi_index[pmid]["matched_pis"]),
                    list(pi_index[pmid]["matched_centers"]),
                    list(pi_index[pmid]["route_queries"]),
                )
            )
        time.sleep(NCBI_RATE_LIMIT_SECONDS)

    write_manifest(manifest_rows)
    write_search_summary(summary_rows)
    print(f"Wrote {len(manifest_rows)} non-overlapping PI backlog papers to {MANIFEST_PATH}")
    print(f"Wrote PI search summary to {SEARCH_SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
