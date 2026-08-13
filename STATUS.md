# Project Status

This file is the fastest way to understand what this repo is, what has already been built, and what comes next.

## What This Repo Is

`niaid-systems-biology-consortium-atlas` is a public-facing research operations repo for the NIAID Systems Biology for Infectious Diseases consortium.

Its immediate scientific purpose is to support the search for host-pathogen mechanisms shared across multiple viruses, especially pathway-level convergence that would be missed by looking only for overlap at the single host-protein level.

Its practical purpose is to turn a diffuse literature and consortium landscape into something inspectable, reproducible, and later usable by agentic workflows such as Symposium.

## What Has Been Built

The repo currently has five working layers.

### 1. Consortium Atlas

- consortium center metadata
- PI and lab-head metadata
- source links for the current program and related literature

### 2. Literature Collection

- official current-program paper collection from the PubMed grant query
- HPMI literature collection
- 20-year PI-backlog scouting layer
- merged non-redundant full collection

Current collection counts:

- `576` current-program papers
- `135` HPMI papers
- `4,159` non-overlapping PI-backlog papers
- `4,870` papers in the merged full collection

### 3. Candidate-Corpus Curation

The full collection was reduced into a candidate corpus using explicit title+abstract heuristics and documented promotion reasons.

Current candidate-corpus count:

- `654` papers in `papers/derived/consortium-subset/manifest.csv`

### 4. Full-Text Normalization And Relevance Review

The `654` candidate papers were then pushed into a full-text layer:

- PMC-open-access papers were fetched and normalized from XML
- manually downloaded PDFs were normalized through the raglab GROBID path
- a stricter second-pass relevance review assigned `relevant`, `maybe`, or `not_relevant`

Current full-text counts:

- `587` PMC-open-access papers downloaded and parsed
- `50` manually downloaded PDFs imported and parsed
- `17` papers still unmatched for manual PDF collection
- `215` papers marked `relevant`
- `174` papers marked `maybe`
- `265` papers marked `not_relevant`

### 5. Relevant-Core Extraction

The `215 relevant` papers were converted into a structured literature core:

- virus labels
- host-system signals
- assay-type signals
- dataset accession matches
- resource-link matches
- a practical `tier_1` / `tier_2` / `tier_3` priority bucket

Current extraction counts:

- `26` papers with explicit dataset accessions
- `26` papers with reusable resource links
- `43` first-pass dataset rows
- `48` first-pass resource rows
- `39` `tier_1` papers for immediate follow-up

## Most Important Files

If you only open a few files, start here:

- `README.md`
- `papers/derived/relevance/relevant-paper-core.csv`
- `outputs/reports/core/relevant-core-summary.md`
- `outputs/reports/core/relevant-dataset-resource-priority.csv`
- `datasets/manifest.csv`
- `resources/manifest.csv`

## What Has Not Been Finished Yet

- the dataset/resource layer is still first-pass extraction, not yet manual normalization
- the `17` unmatched candidate papers still need PDF resolution if they matter
- no vector database or retrieval layer has been built yet
- no final Symposium-facing evidence workflow has been built yet

## What We Are About To Do

The next work phase should focus on the `215 relevant` papers, especially the `39 tier_1` papers and the `42` papers that already expose a dataset accession or reusable resource link.

Immediate next tasks:

1. manually validate the first-pass dataset and resource extraction
2. normalize dataset records into a more reliable curated manifest
3. build a lightweight vector layer over the `215 relevant` normalized papers
4. use that retrieval layer to support Symposium-style hypothesis generation around shared host-pathway mechanisms across viruses

## Why This Matters

This repo is already past the “paper collection” stage.

It now acts as:

- a consortium map
- a reproducible literature atlas
- a defendable narrowed corpus
- a structured bridge into dataset curation
- a realistic starting point for the agentic workflow
