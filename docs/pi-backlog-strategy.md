# PI Backlog Strategy

## Purpose

The PI backlog is the broad scouting layer for papers that are not already captured by:

- the current Systems Biology for Infectious Diseases grant-query corpus
- the HPMI grant-query corpus

It exists because important mechanistic or resource-rich papers by consortium PIs may matter for the final scientific workflow even when they are outside the current grant-number slices.

## Collection Rule

The first pass uses PubMed author queries over the last 20 years for the current program PIs.

Current implementation:

- search each PI separately
- limit to 2006-present
- merge results across PIs
- exclude PMIDs already present in `papers/sources/current-program` or `papers/sources/hpmi`
- keep per-PI search summaries so the retrieval logic is inspectable

Outputs:

- `papers/sources/pi-backlog/manifest.csv`
- `papers/sources/pi-backlog/review-queue.csv`
- `outputs/reports/literature/pi-backlog-search-summary.csv`

## Inclusion Logic For Final Corpus

A PI-backlog paper is promoted into the final corpus when the title and abstract indicate at least one of the following:

- explicit cross-virus or shared-host framing
- viral or host-pathogen context plus mechanism or pathway language
- likely reusable systems-biology resource generation
- strong review or synthesis value for the host-pathogen mechanism question

Papers are left out when title and abstract do not show clear relevance to viral host-mechanism work.

The reason is written explicitly in `final_corpus_reason`.

## Known Limitations

- PubMed author queries can include some homonym noise
- author-only searches may miss older papers with unusual author indexing
- title and abstract review cannot confirm full dataset usefulness

Those limitations are acceptable for the first loose pass because overlap is removed, inclusion logic is explicit, and the per-PI search summary makes suspicious hit patterns easy to inspect.
