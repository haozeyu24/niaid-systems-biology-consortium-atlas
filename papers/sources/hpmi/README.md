# HPMI Papers

This folder holds the HPMI-specific literature stream.

## Why this exists

HPMI is a current center in the NIAID Systems Biology for Infectious Diseases program, but public grant-query paper collections may not fully capture HPMI output.

So HPMI should be tracked explicitly rather than inferred only from the general current-program corpus.

## Current collection route

The current HPMI collection route is the HPMI grant-number query:

- `AI135990`

This defines the clean HPMI core corpus.

## Later expansion routes

After inspecting the grant-defined core corpus, HPMI can later be expanded through:

1. HPMI PI-name and lab-name searches
2. manual additions for important known papers missed by automated collection

## Files

- `manifest.csv`
  Flat overview of HPMI paper records.
- `review-queue.csv`
  Review and curation surface for HPMI papers.
- `manual-additions.csv`
  Papers added intentionally outside automated collection logic.
- `records/`
  One normalized metadata record per paper.

## Commands

```bash
python3 scripts/preflight.py
python3 scripts/fetch_hpmi_papers.py
python3 scripts/build_hpmi_review_queue.py
python3 scripts/classify_hpmi_review_queue.py
```

## Workflow

1. ingest the HPMI core corpus from the grant query
2. build the HPMI review queue
3. run first-pass HPMI classification
4. review and tag HPMI papers for viral/pathogen relevance, assay types, and downstream usefulness

## Provenance rule

Every HPMI paper should preserve how it entered the collection:

- `hpmi_grant_query`
- `manual_addition`

This keeps the collection auditable.
