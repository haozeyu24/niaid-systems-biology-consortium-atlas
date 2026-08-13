# Review Strategy

## Purpose

This document explains how literature in this repo is reviewed, prioritized, and curated.

It exists so collaborators can inspect:

- how papers enter the collection
- how first-pass triage is assigned
- what `candidate` means
- what must happen before a paper is treated as important for downstream scientific workflows

## Review Layers

Literature review in this repo happens in layers.

### Layer 1: Collection

Papers first enter the repo through a defined collection source.

Current sources:

- official current-program PubMed grant query
- HPMI grant-query collection
- PI backlog and new-paper scouting workflows

At this layer, inclusion means:

- the paper belongs to the collection source

It does **not** yet mean:

- the paper is central to the scientific question
- the paper is cross-virus relevant
- the paper contains reusable datasets

### Layer 2: Heuristic triage

Each paper receives a first-pass machine-assisted triage in `review-queue.csv`.

This uses title + abstract text to assign:

- `paper_kind`
- `cross_virus_relevance`
- `cross_virus_reason`
- `priority`
- `priority_reason`
- `final_corpus_decision` where applicable
- `final_corpus_reason` where applicable

This is only a sorting aid. It is not a scientific verdict.

### Layer 3: Human or agent curation

The review queue is then curated to assign:

- center
- PI candidates
- pathogen / virus tags
- assay types
- notes on actual usefulness

This is the first level where scientific judgment enters.

### Layer 4: Curated subset selection

Only after review should a paper be moved conceptually into the downstream consortium subset for the cross-virus pathway workflow.

For the PI backlog, the first pass already records an explicit promotion or exclusion reason so collaborators can inspect why a paper was or was not pulled forward.

### Layer 5: Full-text confirmation

For papers already promoted into the `654`-paper candidate corpus, the repo now runs a second-pass full-text review.

This layer uses:

- PMC XML when open access is available
- raglab GROBID normalization for manually downloaded PDFs

It assigns one of:

- `relevant`
- `maybe`
- `not_relevant`

This is still heuristic, but it is materially stricter than title+abstract triage because it can demote papers that only looked promising in metadata.

## Current Heuristic Logic

### `cross_virus_relevance`

This field is intended to support triage, not final interpretation.

Values:

- `high`
- `candidate`
- `unknown`

#### `high`

Assigned when title or abstract contains explicit language suggesting shared or comparative host-pathogen reasoning, such as:

- `shared host`
- `comparative`
- `cross-virus`
- `multi-virus`
- `common host`
- `broad-spectrum`
- `multiple viruses`
- `conserved host`
- `virus-host interaction map`

Interpretation:

- paper is more likely to be directly useful for the target scientific question

#### `candidate`

Assigned when title or abstract contains strong but less specific terms associated with viral host-mechanism work, such as:

- `viral`
- `host-pathogen`
- `interaction`
- `dependency`
- `host factor`
- `proteome`
- `interactome`
- `crispr`
- `pathway`

Interpretation:

- paper may be relevant and deserves inspection
- paper is not yet claimed to support cross-virus pathway reasoning

#### `unknown`

Assigned when no explicit cross-virus/shared-host language or strong viral host-mechanism terms are matched.

Interpretation:

- no strong relevance signal was found from title + abstract
- this does not mean the paper is useless
- it means the paper should not be elevated automatically

### `priority`

This field is intended to determine review order.

Values:

- `high`
- `medium`
- `low`

#### `high`

Generally assigned to recent papers, especially 2026 papers, whose title or abstract includes strong viral/host/pathway keywords.

Interpretation:

- review earlier

#### `medium`

Assigned to:

- recent papers without strong signal
- older papers with relevant mechanistic keywords

Interpretation:

- review after the highest-signal material

#### `low`

Assigned when no strong review-priority keywords are matched.

Interpretation:

- keep in the corpus, but do not prioritize for immediate review

## What The Heuristics Do Not Mean

The heuristics do **not** establish:

- scientific correctness
- pathway-level convergence
- dataset reuse value
- center/PI attribution
- whether the paper should appear in a collaborator-facing shortlist

They only help order review work.

For the PI backlog there is one extra heuristic judgment:

- `include`
- `watch`
- `exclude`

This is still provisional. It keeps the broader PI history searchable while making the final corpus more selective and explainable.

## Review Principles

The review process should follow these rules:

1. Do not confuse corpus membership with scientific importance.
2. Do not confuse keyword matches with mechanistic relevance.
3. Do not infer cross-virus convergence from a title or abstract alone.
4. Preserve papers with weak first-pass signals rather than dropping them silently.
5. Record reasons for promotion into downstream curated subsets.

## Promotion Criteria For Downstream Use

A paper becomes more important for downstream cross-virus work when one or more of the following are true:

- it studies viral host dependency or host-pathogen interaction directly
- it contains comparative or multi-virus framing
- it identifies host pathways rather than only isolated host factors
- it provides evidence that can be connected to other viral systems
- it likely contains reusable data, code, or network resources
- it is useful for framing mechanistic alternatives or contradictions

## Expected Evolution

This strategy should change over time.

Likely improvements:

- more specific viral/pathogen dictionaries
- better assay-type inference
- explicit `likely_dataset_rich` tagging
- center- and PI-aware heuristics
- classifier logic based on reviewed examples instead of keyword rules only

## Current Full-Text Selection Rules

The current full-text selector is deliberately conservative about false positives from the PI backlog.

It gives extra weight to:

- explicit cross-virus or shared-host language in normalized full text
- virus-focused host-factor, pathway, interactome, proteomics, screening, or host-response language in title and abstract

It demotes papers dominated by:

- non-viral pathogens such as tuberculosis or Legionella
- generic method or resource papers without clear virology focus
- off-target disease domains
- corrections and errata
- therapeutic or clinical virology papers that do not clearly advance the host-pathway question

This means a paper can:

- enter the `654` on a relatively loose title+abstract rule
- later be pushed to `maybe` or `not_relevant` once full text is available

That is intentional. The `654` is a broad candidate corpus; the full-text pass is the first real attempt to carve out a more defendable mechanistic subset.

## Current Files

The review workflow currently depends on:

- `papers/sources/current-program/manifest.csv`
- `papers/sources/current-program/review-queue.csv`
- `papers/sources/hpmi/review-queue.csv`
- `papers/sources/pi-backlog/review-queue.csv`
- `papers/fulltext/parsed/manifest.csv`
- `papers/derived/relevance/fulltext-selection.csv`
- `scripts/fetch_program_papers.py`
- `scripts/build_review_queue.py`
- `scripts/fetch_pi_backlog_papers.py`
- `scripts/build_pi_backlog_review_queue.py`
- `scripts/parse_full_text_with_grobid.py`
- `scripts/build_fulltext_relevance_selection.py`
- `docs/literature-workflow.md`

This file is the human-readable inspection layer for that process.
