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
HPMI_DIR = PROJECT_ROOT / "papers" / "sources" / "hpmi"
RECORDS_DIR = HPMI_DIR / "records"
MANIFEST_PATH = HPMI_DIR / "manifest.csv"

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_RATE_LIMIT_SECONDS = 0.34

HPMI_GRANT_QUERY = "(AI135990[Grant Number])"
HPMI_GRANT_URL = "https://pubmed.ncbi.nlm.nih.gov/?term=%28AI135990%5BGrant+Number%5D%29&sort=date"


def fetch_url(url: str) -> bytes:
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


def text_or_none(value: str | None) -> str:
    return value.strip() if value else ""


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


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


def year_from_pubdate(pubdate: str) -> str:
    if not pubdate:
        return ""
    for token in pubdate.replace("/", " ").replace("-", " ").split():
        if token.isdigit() and len(token) == 4:
            return token
    return ""


def paper_id_from_pmid(pmid: str) -> str:
    return f"pmid-{pmid}"


def write_record(summary: dict, abstract: str, routes: list[str], route_notes: list[str]) -> dict[str, str]:
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
        "source_collection": "hpmi",
        "center": "HPMI",
        "pi_candidates": [],
        "pathogens": [],
        "viruses": [],
        "assay_types": [],
        "identifiers": {"pmid": pmid, "pmcid": pmcid, "doi": doi},
        "links": {
            "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pmc": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else "",
            "publisher": f"https://doi.org/{doi}" if doi else "",
        },
        "collection_route": routes,
        "extraction_status": {
            "full_text_status": "unknown",
            "dataset_scan_status": "pending",
            "dataset_validation_status": "pending",
            "resource_scan_status": "pending",
        },
        "provenance": {
            "source_query": HPMI_GRANT_QUERY,
            "source_url": HPMI_GRANT_URL,
            "route_notes": route_notes,
            "imported_at": time.strftime("%Y-%m-%d"),
        },
    }

    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    (RECORDS_DIR / f"{paper_id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    return {
        "paper_id": paper_id,
        "title": title,
        "pmid": pmid,
        "doi": doi,
        "collection_route": ";".join(routes),
        "year": year,
        "paper_status": "metadata_ingested",
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
                "collection_route",
                "year",
                "paper_status",
                "dataset_scan_status",
                "resource_scan_status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_hpmi_search_index() -> dict[str, dict[str, list[str]]]:
    index: dict[str, dict[str, list[str]]] = {}

    grant_pmids = pubmed_search(HPMI_GRANT_QUERY)
    for pmid in grant_pmids:
        index.setdefault(pmid, {"routes": [], "route_notes": []})
        index[pmid]["routes"].append("hpmi_grant_query")
        index[pmid]["route_notes"].append(HPMI_GRANT_QUERY)

    return index


def reset_records_dir() -> None:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    for path in RECORDS_DIR.glob("*.json"):
        path.unlink()


def main() -> int:
    hpmi_index = build_hpmi_search_index()
    pmids = list(hpmi_index.keys())
    reset_records_dir()
    manifest_rows: list[dict[str, str]] = []

    for batch in batched(pmids, 200):
        summaries = fetch_summaries(batch)
        abstracts = fetch_abstracts(batch)
        for summary in summaries:
            pmid = str(summary["pmid"])
            routes = list(hpmi_index[pmid]["routes"])
            route_notes = list(hpmi_index[pmid]["route_notes"])
            manifest_rows.append(write_record(summary, abstracts.get(pmid, ""), routes, route_notes))
        time.sleep(NCBI_RATE_LIMIT_SECONDS)

    write_manifest(manifest_rows)
    print(f"Ingested {len(manifest_rows)} HPMI papers into {HPMI_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
