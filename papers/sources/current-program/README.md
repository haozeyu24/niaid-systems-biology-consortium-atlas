# Current Program Papers

This folder holds the official current Systems Biology for Infectious Diseases paper corpus derived from the grant-query PubMed search.

## Files

- `manifest.csv`
  Flat overview of the current-program corpus.
- `review-queue.csv`
  Paper-level curation and tagging queue.
- `records/*.json`
  One normalized metadata record per paper.

## Workflow

1. ingest papers from the official PubMed query
2. build or refresh the review queue
3. review and classify papers
4. assign center / PI / pathogen / assay tags
5. mark papers relevant to the cross-virus pathway workflow
6. nominate papers for the curated consortium subset

## Commands

```bash
python3 scripts/preflight.py
python3 scripts/fetch_program_papers.py
python3 scripts/build_review_queue.py
```

This repo currently uses `review-queue.csv` as the main literature curation surface.
