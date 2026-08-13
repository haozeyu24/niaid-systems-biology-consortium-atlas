# Parsed Full Text

This folder holds normalized full-text artifacts derived from the candidate corpus.

Sources:

- PMC XML for open-access papers
- local PDFs for manually collected papers

Key files:

- `manifest.csv`
  Parse status, source type, and normalized-output tracking for each paper.
- `normalized/*.json`
  Structured text used for downstream full-text relevance review and later retrieval workflows.
- `pmc_xml/`
  Cached PMC XML files used during normalization.

This is the bridge between paper metadata and agent-usable text.
