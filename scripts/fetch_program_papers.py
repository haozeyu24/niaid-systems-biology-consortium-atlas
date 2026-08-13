#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURRENT_PROGRAM_DIR = PROJECT_ROOT / "papers" / "sources" / "current-program"
RECORDS_DIR = CURRENT_PROGRAM_DIR / "records"
MANIFEST_PATH = CURRENT_PROGRAM_DIR / "manifest.csv"

PUBMED_QUERY = "(AI135964[Grant Number]) OR (AI135995[Grant Number])"
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_RATE_LIMIT_SECONDS = 0.34


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


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def text_or_none(value: str | None) -> str:
    return value.strip() if value else ""


def paper_id_from_pmid(pmid: str) -> str:
    return f"pmid-{pmid}"


def fetch_summaries(pmids: list[str]) -> list[dict]:
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    url = f"{PUBMED_SUMMARY_URL}?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(fetch_url(url))
    records = []
    for docsum in root.findall(".//DocSum"):
        record: dict[str, object] = {
            "authors": [],
            "article_ids": {},
            "full_journal_name": "",
            "pubdate": "",
            "source": "",
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
            elif name == "Source":
                record["source"] = text_or_none(item.text)
            elif name == "AuthorList":
                authors = [text_or_none(child.text) for child in item.findall("Item") if child.text]
                record["authors"] = authors
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
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
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


def write_record(summary: dict, abstract: str) -> dict[str, str]:
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
        "source_collection": "current-program",
        "center": "",
        "pi_candidates": [],
        "pathogens": [],
        "viruses": [],
        "assay_types": [],
        "identifiers": {
            "pmid": pmid,
            "pmcid": pmcid,
            "doi": doi,
        },
        "links": {
            "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pmc": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else "",
            "publisher": f"https://doi.org/{doi}" if doi else "",
        },
        "extraction_status": {
            "full_text_status": "unknown",
            "dataset_scan_status": "pending",
            "dataset_validation_status": "pending",
            "resource_scan_status": "pending",
        },
        "provenance": {
            "source_query": PUBMED_QUERY,
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/?term=%28AI135964%5BGrant+Number%5D%29+OR+%28AI135995%29&sort=date",
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
        "center": "",
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
                "center",
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
    pmids = pubmed_search(PUBMED_QUERY)
    if not pmids:
        print("No PubMed records found for current program query.", file=sys.stderr)
        return 1

    manifest_rows: list[dict[str, str]] = []
    for batch in batched(pmids, 200):
        summaries = fetch_summaries(batch)
        abstracts = fetch_abstracts(batch)
        for summary in summaries:
            pmid = str(summary["pmid"])
            manifest_rows.append(write_record(summary, abstracts.get(pmid, "")))
        time.sleep(NCBI_RATE_LIMIT_SECONDS)

    write_manifest(manifest_rows)
    print(f"Ingested {len(manifest_rows)} papers into {CURRENT_PROGRAM_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
