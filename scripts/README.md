# Scripts

Current naming pattern:

- `fetch_*_papers.py` for metadata ingest
- `build_*_review_queue.py` for title/abstract triage
- `classify_*_review_queue.py` for virus/pathogen/assay tagging
- `build_*_candidates.py` for downstream curated subsets
- `run_literature_refresh.py` for the end-to-end literature refresh

Current implemented literature entry points:

- `fetch_program_papers.py`
- `build_review_queue.py`
- `classify_current_program_review_queue.py`
- `fetch_hpmi_papers.py`
- `build_hpmi_review_queue.py`
- `classify_hpmi_review_queue.py`
- `fetch_pi_backlog_papers.py`
- `build_pi_backlog_review_queue.py`
- `classify_pi_backlog_review_queue.py`
- `build_initial_literature_shortlist.py`
- `build_full_collection_manifest.py`
- `build_literature_summary_reports.py`
- `build_final_corpus_candidates.py`
- `build_full_text_inventory.py`
- `download_pmc_oa_full_texts.py`
- `import_downloaded_manual_pdfs.py`
- `parse_full_text_with_grobid.py`
- `build_fulltext_relevance_selection.py`
- `extract_relevant_paper_core_entities.py`
- `run_literature_refresh.py`

Full-text stage notes:

- `download_pmc_oa_full_texts.py`
  Downloads PMC-open-access full texts for the current candidate corpus.
- `import_downloaded_manual_pdfs.py`
  Matches PDFs from `~/Downloads` into `papers/fulltext/inventory/manual/` and records import provenance.
- `parse_full_text_with_grobid.py`
  Uses PMC XML when available and the raglab GROBID normalization path for local PDFs.
- `build_fulltext_relevance_selection.py`
  Builds `papers/derived/relevance/fulltext-selection.csv` with `relevant` / `maybe` / `not_relevant` calls and explicit reasons.
- `extract_relevant_paper_core_entities.py`
  Extracts structured virus, host-system, assay, dataset, and resource signals from the `215 relevant` papers into `papers/derived/relevance/relevant-paper-core.csv`, `datasets/manifest.csv`, and `resources/manifest.csv`.
