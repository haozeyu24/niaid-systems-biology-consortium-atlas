# NIAID Systems Biology Consortium Atlas

Public research operations repo for the NIAID Systems Biology for Infectious Diseases consortium.

It is meant to stay useful even before the downstream agentic workflow is complete.

For a fast collaborator-facing overview, start with `STATUS.md`.

## Purpose

This repo is being built to support:

- consortium mapping
- PI and lab tracking
- current-program paper collection
- HPMI paper collection
- PI-backlog scouting over the last 20 years
- curated final corpus selection with explicit promotion reasons
- dataset and resource extraction from papers
- cross-virus pathway convergence analysis
- future Symposium-style agentic workflows

The immediate scientific goal is to help find host-pathogen mechanisms shared across multiple viruses, especially pathway-level convergence where viruses do not target the same human protein directly.

## Scope

This repo is not a full-text paper archive.

It is a structured atlas of:

- consortium structure
- paper metadata
- dataset and resource metadata
- derived pathway/evidence tables
- reproducible collection and normalization workflows

## Layout

```text
niaid-systems-biology-consortium-atlas/
  consortium/
    centers/
    people/
  papers/
    sources/
      current-program/
      hpmi/
      pi-backlog/
    derived/
      full-collection/
      consortium-subset/
      relevance/
    fulltext/
      inventory/
      parsed/
  datasets/
  resources/
  pathways/
  schemas/
  scripts/
  workflows/
  docs/
  outputs/
```

## Current Sources

- NIAID Systems Biology Consortium page
- official PubMed grant-query corpus for the current program
- HPMI-specific literature collection
- PI-name-based literature expansion for centers and labs in the consortium
- public center and lab pages

## Current Status

The literature-side scaffold is already in place.

What is currently built:

- consortium center, PI, and lab metadata in `consortium/`
- official current-program PubMed ingest in `papers/sources/current-program/`
- explicit HPMI literature collection in `papers/sources/hpmi/`
- 20-year non-overlapping PI backlog in `papers/sources/pi-backlog/`
- merged PMID-level union view in `papers/derived/full-collection/`
- first-pass title+abstract review queues for all three literature layers
- curated final-corpus candidate manifest in `papers/derived/consortium-subset/manifest.csv`
- full-text availability and manual-download tracking in `papers/fulltext/inventory/`
- parsed PMC XML / PDF normalization outputs in `papers/fulltext/parsed/`
- second-pass full-text relevance selection outputs in `papers/derived/relevance/`
- scouting and summary reports in `outputs/reports/`
- preflight and refresh scripts in `scripts/`
- scheduled publication-tracking workflow in `.github/workflows/pubmed-refresh.yml`

Current literature counts from the latest run:

- `576` current-program papers
- `135` HPMI papers
- `4,159` non-overlapping PI-backlog papers
- `4,870` papers in the merged full collection
- `654` final corpus candidates
- `1,696` rows in the broader literature shortlist
- `587` PMC open-access full-text papers downloaded
- `50` manually downloaded PDFs imported from `~/Downloads`
- `17` candidate papers still unmatched for manual PDF collection
- `215` papers currently marked `relevant` after full-text review
- `174` papers currently marked `maybe` after full-text review
- `265` papers currently marked `not_relevant` after full-text review
- `43` first-pass dataset candidate rows extracted from the `215 relevant` papers
- `48` first-pass resource candidate rows extracted from the `215 relevant` papers

Key outputs to inspect first:

- `papers/sources/current-program/manifest.csv`
- `papers/sources/hpmi/manifest.csv`
- `papers/sources/pi-backlog/manifest.csv`
- `papers/derived/full-collection/manifest.csv`
- `papers/sources/pi-backlog/review-queue.csv`
- `papers/derived/consortium-subset/manifest.csv`
- `papers/fulltext/inventory/manifest.csv`
- `papers/fulltext/inventory/manual-download-list.csv`
- `papers/fulltext/parsed/manifest.csv`
- `papers/derived/relevance/fulltext-selection.csv`
- `papers/derived/relevance/relevant-paper-core.csv`
- `outputs/reports/literature/pi-backlog-search-summary.csv`
- `outputs/reports/literature/initial-literature-shortlist.csv`
- `outputs/reports/literature/literature-summary.md`
- `outputs/reports/fulltext/fulltext-relevance-summary.md`
- `outputs/reports/fulltext/fulltext-relevant-papers.csv`
- `outputs/reports/core/relevant-core-summary.md`
- `outputs/reports/core/relevant-dataset-resource-priority.csv`
- `datasets/manifest.csv`
- `resources/manifest.csv`

Current limits:

- this repo stores structured metadata and review outputs, not full-text papers
- PI-backlog author queries are a first pass and may still need manual tightening for some names
- dataset extraction is not yet the main completed layer; literature curation comes first
- local PDF and parser-cache assets are reproducible working files and should stay out of public git history
- raw fetched `records/*.json` files and normalized full-text JSON are treated as reproducible working artifacts for a lean public repo

## Full-Text Layer

The repo now includes a dedicated `papers/fulltext/inventory/` layer for the current `654`-paper candidate corpus.

Its purpose is to separate:

- papers with a known PMC-based open-access route
- papers with only a publisher or DOI link
- papers that likely require manual download

Current files:

- `papers/fulltext/inventory/manifest.csv`
  One row per paper in the `654`, with PubMed, PMC, publisher, OA status, and collection status fields.
- `papers/fulltext/inventory/manual-download-list.csv`
  A practical list of papers that still need manual PDF collection or institutional-access checking.
- `papers/fulltext/inventory/oa/`
  Reserved for open-access assets or saved OA landing references.
- `papers/fulltext/inventory/manual/`
  Reserved for manually downloaded PDFs or text files.

This layer is logistical rather than interpretive.

It answers:

- do we have a known PMC route?
- do we only have a publisher link?
- which papers still need manual downloading?

## Full-Text Parsing And Relevance Layer

The repo now also has a structured full-text parsing and second-pass relevance layer.

What this layer does:

- fetch PMC-open-access papers as XML
- normalize manually downloaded PDFs with the raglab GROBID path
- store normalized JSON for downstream use
- assign a more defendable `relevant` / `maybe` / `not_relevant` decision for each paper in the `654`

Current files:

- `papers/fulltext/parsed/manifest.csv`
  Parse status for every paper in the `654`, including whether it came from PMC XML or a local PDF.
- `papers/fulltext/parsed/normalized/*.json`
  Structured normalized documents used for downstream review and later dataset extraction.
- `papers/derived/relevance/fulltext-selection.csv`
  Full-text review sheet with explicit reasons for every decision.
- `outputs/reports/fulltext/fulltext-relevance-summary.md`
  Human-readable summary of the latest full-text selection pass.
- `outputs/reports/fulltext/fulltext-relevant-papers.csv`
  Export of papers currently marked `relevant`.

Current parsing status:

- `587` papers parsed from PMC XML
- `50` papers parsed from manually downloaded PDFs via raglab GROBID
- `17` papers still missing a matched local PDF

Current full-text decision counts:

- `215` `relevant`
- `174` `maybe`
- `265` `not_relevant`

### What The Full-Text Decisions Mean

- `relevant`
  Title, abstract, and normalized full text support virus-focused host-mechanism or explicit cross-virus/shared-host relevance.
- `maybe`
  The paper is still virology-relevant, but looks narrower, more clinical/therapeutic, or needs later inspection before promotion.
- `not_relevant`
  The paper is dominated by non-viral pathogens, generic methods/resources, off-target disease areas, corrections, or otherwise low-priority contexts for this project.

## Relevant-Core Extraction Layer

The repo now includes a first-pass structured extraction over the `215 relevant` papers.

Its job is to convert the literature core into reusable metadata for the next stage of work.

What this layer currently extracts:

- virus labels
- host-system signals
- assay-type signals
- dataset repository and accession matches
- code/network/resource links
- a practical `tier_1` / `tier_2` / `tier_3` priority bucket

Current outputs:

- `papers/derived/relevance/relevant-paper-core.csv`
  Paper-level structured summary for the `215 relevant` papers.
- `datasets/manifest.csv`
  First-pass dataset candidate table extracted from the literature core.
- `resources/manifest.csv`
  First-pass resource table for GitHub, NDEx, and similar links mentioned in the papers.
- `outputs/reports/core/relevant-core-summary.md`
  Summary of the extraction pass, including priority buckets and a starting shortlist.
- `outputs/reports/core/relevant-dataset-resource-priority.csv`
  Compact export of papers with at least one dataset accession or reusable resource link.

Current extraction counts:

- `26` papers with dataset accessions
- `26` papers with resource links
- `43` dataset rows written
- `48` resource rows written
- `39` `tier_1` papers for immediate manual follow-up

## How The Corpus Shrinks From 4,870 To 654

The repo currently uses a transparent heuristic filter, not hidden judgment.

The reduction works in stages:

1. `full-collection`
   This is the union of all distinct PMIDs gathered from:
   - `current-program`
   - `hpmi`
   - `pi-backlog`

2. `review queues`
   Each paper is scored from title and abstract text into fields such as:
   - `paper_kind`
   - `cross_virus_relevance`
   - `priority`
   - `viruses`
   - `pathogens`
   - `assay_types`

3. `consortium-subset`
   A paper is promoted into the current `654`-paper candidate corpus only if it passes one of the documented inclusion rules below.

### Inclusion Rules

For `current-program` and `hpmi` papers, a paper is included if at least one of these is true:

- `cross_virus_relevance = high`
  Meaning the title or abstract contains explicit comparative or shared-host language such as `cross-virus`, `multi-virus`, `shared host`, or `broad-spectrum`.

- `cross_virus_relevance = candidate` and at least one of these is non-empty:
  - `viruses`
  - `pathogens`
  - `assay_types`

  Meaning the paper has viral or host-mechanism language plus some additional signal that it is biologically relevant or resource-like.

- `priority = high` and `paper_kind = data_or_analysis`
  Meaning it looks like a recent, likely resource-rich paper even if the cross-virus language is not explicit.

For `pi-backlog` papers, a paper is included only if:

- `final_corpus_decision = include`

That decision is assigned from title and abstract using these rules:

- include if the paper has explicit cross-virus or shared-host framing
- include if the paper has viral context plus mechanism or resource language such as `pathway`, `interaction`, `interactome`, `network`, `proteomics`, `screen`, or `host response`
- include if it is a review with both viral framing and host-mechanism framing

If a PI-backlog paper only has infectious-disease language without enough host-mechanism signal, it is marked `watch` instead of being promoted into the `654`.

### What The 654 Means

The `654` papers are best understood as:

- a heuristic candidate corpus
- enriched for viral host-mechanism and cross-virus relevance
- stricter than the full collection
- still broad enough to support later dataset and evidence extraction

They are not claimed to be:

- a final biological truth set
- a manually curated gold-standard set
- an exhaustive set of all useful papers

### Where To Inspect The Logic

- inclusion build logic: `scripts/build_final_corpus_candidates.py`
- PI-backlog include/watch/exclude logic: `scripts/build_pi_backlog_review_queue.py`
- review strategy explanation: `docs/review-strategy.md`
- resulting candidate corpus: `papers/derived/consortium-subset/manifest.csv`

## Key docs

- `docs/scope.md`
- `docs/roadmap.md`
- `docs/literature-workflow.md`
- `docs/review-strategy.md`
- `docs/pi-backlog-strategy.md`
- `docs/portability.md`

## Preflight

Run preflight before using pipeline scripts on a new machine:

```bash
python3 scripts/preflight.py
```

The preflight currently checks:

- Python version
- `curl` availability
- expected repo layout
- write access to the repo
- HTTPS reachability to NCBI/PubMed

Preflight should report problems clearly. It is expected to evolve as the repo grows.

## Current pipeline entry point

To ingest the official current-program PubMed corpus:

```bash
python3 scripts/fetch_program_papers.py
```

This populates:

- `papers/sources/current-program/manifest.csv`
- `papers/sources/current-program/records/*.json`

To ingest the HPMI literature stream:

```bash
python3 scripts/fetch_hpmi_papers.py
```

This populates:

- `papers/sources/hpmi/manifest.csv`
- `papers/sources/hpmi/records/*.json`

To ingest the non-overlapping 20-year PI backlog:

```bash
python3 scripts/fetch_pi_backlog_papers.py
python3 scripts/build_pi_backlog_review_queue.py
python3 scripts/classify_pi_backlog_review_queue.py
```

To refresh the full literature layer end-to-end:

```bash
python3 scripts/run_literature_refresh.py
```

This also rebuilds:

- `outputs/reports/literature/pi-backlog-search-summary.csv`
- `outputs/reports/literature/initial-literature-shortlist.csv`
- `outputs/reports/literature/literature-summary.md`
- `papers/derived/consortium-subset/manifest.csv`
- `papers/derived/full-collection/manifest.csv`
- `papers/fulltext/inventory/manifest.csv`
- `papers/fulltext/inventory/manual-download-list.csv`

To extend into full-text parsing and second-pass selection:

```bash
python3 scripts/download_pmc_oa_full_texts.py
python3 scripts/import_downloaded_manual_pdfs.py
python3 scripts/parse_full_text_with_grobid.py
python3 scripts/build_fulltext_relevance_selection.py
python3 scripts/extract_relevant_paper_core_entities.py
```

This populates:

- `papers/fulltext/inventory/oa/`
- `papers/fulltext/inventory/manual/`
- `papers/fulltext/parsed/manifest.csv`
- `papers/fulltext/parsed/normalized/*.json`
- `papers/derived/relevance/fulltext-selection.csv`
- `papers/derived/relevance/relevant-paper-core.csv`
- `datasets/manifest.csv`
- `resources/manifest.csv`
- `outputs/reports/fulltext/fulltext-relevance-summary.md`
- `outputs/reports/fulltext/fulltext-relevant-papers.csv`
- `outputs/reports/core/relevant-core-summary.md`

## Automated Tracking

The repo now includes a scheduled GitHub Actions workflow at `.github/workflows/pubmed-refresh.yml`.

Its job is to:

- refresh current-program papers
- refresh HPMI papers
- refresh the PI backlog
- rebuild review queues and final corpus candidates
- commit metadata changes back to the repo

This gives you a publication-tracking system without requiring a machine-specific local cron setup.

## Principles

- separate official current-program papers from broader PI paper histories
- treat the full literature collection as the union of official query-based papers plus PI-name-based tracking
- treat datasets/resources as first-class records, not notes buried in paper summaries
- preserve provenance for every derived record
- keep the repo useful before any agentic workflow is complete
- optimize for scientific reuse, not just collection completeness
- treat preflight as a maintained contract for portability, not a one-time script
