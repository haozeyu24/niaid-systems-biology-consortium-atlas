#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FULL_TEXT_MANIFEST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manifest.csv"
NORMALIZED_DIR = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "normalized"
PMC_XML_DIR = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "pmc_xml"
PARSE_MANIFEST_PATH = PROJECT_ROOT / "papers" / "fulltext" / "parsed" / "manifest.csv"

def resolve_raglab_src() -> Path:
    candidates: list[Path] = []
    env_value = os.environ.get("RAGLAB_SRC")
    if env_value:
        candidates.append(Path(env_value).expanduser())
    candidates.extend(
        [
            PROJECT_ROOT.parents[1] / "raglab" / "PI3K_RAG" / "src",
            Path.home() / ".openclaw" / "workspaces" / "raglab" / "PI3K_RAG" / "src",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate raglab source. Set RAGLAB_SRC or place raglab/PI3K_RAG/src alongside this workspace."
    )


RAGLAB_SRC = resolve_raglab_src()
if str(RAGLAB_SRC) not in sys.path:
    sys.path.insert(0, str(RAGLAB_SRC))

from pi3k_rag.ingestion import body_word_count, normalize_document_from_source_path, write_normalized_document  # type: ignore
from pi3k_rag.pmc import PMCClient  # type: ignore


SOURCE_RECORD_DIRS = {
    "current-program": PROJECT_ROOT / "papers" / "sources" / "current-program" / "records",
    "hpmi": PROJECT_ROOT / "papers" / "sources" / "hpmi" / "records",
    "pi-backlog": PROJECT_ROOT / "papers" / "sources" / "pi-backlog" / "records",
}


def load_record(source_collection: str, paper_id: str) -> dict:
    path = SOURCE_RECORD_DIRS[source_collection] / f"{paper_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def local_pdf_path_for_row(row: dict[str, str]) -> Path | None:
    manual_pdf = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "manual" / f"{row['paper_id']}.pdf"
    if manual_pdf.exists():
        return manual_pdf
    oa_pdf = PROJECT_ROOT / "papers" / "fulltext" / "inventory" / "oa" / f"{row['paper_id']}.pdf"
    if oa_pdf.exists():
        return oa_pdf
    return None


def parser_cache_path(pdf_path: Path) -> Path:
    return pdf_path.parent.parent / "parser_cache" / "grobid" / f"{pdf_path.stem}.tei.xml"


def repo_relative(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except Exception:
        return str(path)


def sanitize_normalized_payload(normalized_path: Path) -> dict:
    payload = json.loads(normalized_path.read_text(encoding="utf-8"))
    source_path = payload.get("source_path")
    if source_path:
        try:
            payload["source_path"] = repo_relative(Path(source_path))
        except Exception:
            pass
    normalized_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    PMC_XML_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(FULL_TEXT_MANIFEST_PATH.open(encoding="utf-8")))
    manifest_rows: list[dict[str, str]] = []
    pmc_client = PMCClient(tool="niaid-systems-biology-consortium-atlas", insecure=True)

    for row in rows:
        use_pmc_xml = bool(row["pmcid"])
        pdf_path = local_pdf_path_for_row(row)
        normalized_target = NORMALIZED_DIR / f"{row['pmid']}.json"
        cached_xml_target = PMC_XML_DIR / f"{row['pmcid']}.xml" if row["pmcid"] else None
        if not use_pmc_xml and pdf_path is None:
            manifest_rows.append(
                {
                    "paper_id": row["paper_id"],
                    "pmid": row["pmid"],
                    "source_collection": row["source_collection"],
                    "parse_source_type": "",
                    "pdf_path": "",
                    "xml_path": "",
                    "normalized_json_path": "",
                    "parse_status": "missing_local_pdf",
                    "section_count": "0",
                    "body_word_count": "0",
                    "parser_warnings": "local PDF missing",
                }
            )
            continue

        record = load_record(row["source_collection"], row["paper_id"])
        paper_row = {
            "pmid": row["pmid"],
            "doi": row["doi"],
            "pmcid": row["pmcid"],
            "title": row["title"],
            "abstract": record.get("abstract", "") or "",
            "journal": record.get("journal", "") or "",
            "pub_year": int(row["year"]) if row["year"] else None,
        }
        parse_source_type = "pmc_xml" if use_pmc_xml else "pdf_grobid"
        xml_path = ""
        document = None

        if normalized_target.exists():
            payload = sanitize_normalized_payload(normalized_target)
            manifest_rows.append(
                {
                    "paper_id": row["paper_id"],
                    "pmid": row["pmid"],
                    "source_collection": row["source_collection"],
                    "parse_source_type": parse_source_type,
                    "pdf_path": repo_relative(pdf_path),
                    "xml_path": repo_relative(cached_xml_target) if cached_xml_target and cached_xml_target.exists() else "",
                    "normalized_json_path": repo_relative(normalized_target),
                    "parse_status": "cached_normalized",
                    "section_count": str(len(payload.get("sections", []))),
                    "body_word_count": str(
                        len(
                            " ".join(section.get("text", "") for section in payload.get("sections", [])).split()
                        )
                    ),
                    "parser_warnings": "; ".join(payload.get("parser_warnings", [])),
                }
            )
            continue

        try:
            if use_pmc_xml:
                xml_target = PMC_XML_DIR / f"{row['pmcid']}.xml"
                if not xml_target.exists():
                    print(f"Fetching PMC XML for {row['paper_id']}", flush=True)
                    raw_xml = pmc_client.fetch_article_xml(row["pmcid"])
                    xml_target.write_text(raw_xml, encoding="utf-8")
                else:
                    print(f"Using cached PMC XML for {row['paper_id']}", flush=True)
                xml_path = repo_relative(xml_target)
                document = normalize_document_from_source_path(
                    row=paper_row,
                    source_type="pmc_xml",
                    source_path=str(xml_target),
                )
            else:
                print(f"Parsing {row['paper_id']} with Grobid", flush=True)
                document = normalize_document_from_source_path(
                    row=paper_row,
                    source_type="pdf",
                    source_path=str(pdf_path),
                    pdf_parser="grobid",
                )
                xml_path = repo_relative(parser_cache_path(pdf_path))
        except Exception as exc:
            manifest_rows.append(
                {
                    "paper_id": row["paper_id"],
                    "pmid": row["pmid"],
                    "source_collection": row["source_collection"],
                    "parse_source_type": parse_source_type,
                    "pdf_path": repo_relative(pdf_path),
                    "xml_path": xml_path,
                    "normalized_json_path": "",
                    "parse_status": "parse_error",
                    "section_count": "0",
                    "body_word_count": "0",
                    "parser_warnings": str(exc),
                }
            )
            continue

        normalized_path = ""
        parse_status = "normalized"
        if document is not None:
            normalized_target_path = write_normalized_document(document, NORMALIZED_DIR)
            sanitize_normalized_payload(normalized_target_path)
            normalized_path = repo_relative(normalized_target_path)
            if not document.sections:
                parse_status = "normalized_empty_sections"
        else:
            parse_status = "normalization_failed"

        warnings = "; ".join(document.parser_warnings) if document else "normalization returned None"
        manifest_rows.append(
            {
                "paper_id": row["paper_id"],
                "pmid": row["pmid"],
                "source_collection": row["source_collection"],
                "parse_source_type": parse_source_type,
                "pdf_path": repo_relative(pdf_path),
                "xml_path": xml_path,
                "normalized_json_path": normalized_path,
                "parse_status": parse_status,
                "section_count": str(len(document.sections) if document else 0),
                "body_word_count": str(body_word_count(document) if document else 0),
                "parser_warnings": warnings,
            }
        )

    with PARSE_MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "paper_id",
                "pmid",
                "source_collection",
                "parse_source_type",
                "pdf_path",
                "xml_path",
                "normalized_json_path",
                "parse_status",
                "section_count",
                "body_word_count",
                "parser_warnings",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Wrote parse manifest to {PARSE_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
