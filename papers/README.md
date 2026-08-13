# Papers

This folder holds the literature atlas for the repo.

It is organized as a sequence of layers rather than one undifferentiated paper dump.

## Top-Level Groups

- `sources/`
  Literature grouped by collection route.
- `derived/`
  Union views, narrowed corpora, and relevance outputs derived from the sources.
- `fulltext/`
  Full-text inventory and parsing outputs.

## Source Layers

- `sources/current-program/`
  Official current Systems Biology for Infectious Diseases grant-query corpus.
- `sources/hpmi/`
  Explicit HPMI literature layer.
- `sources/pi-backlog/`
  Broader 20-year PI-name-based scouting layer.

## Derived Layers

- `derived/full-collection/`
  PMID-level union of the major collection routes.
- `derived/consortium-subset/`
  Heuristic candidate corpus promoted from the broader collection.
- `derived/relevance/`
  Second-pass full-text relevance review and structured paper-core extraction.

## Full-Text Layers

- `fulltext/inventory/`
  Full-text availability, OA route, and manual-download tracking.
- `fulltext/parsed/`
  Normalized full-text outputs derived from PMC XML and local PDFs.

## Reading Order

If you are new to the repo, the most useful order is:

1. `sources/`
2. `derived/full-collection/`
3. `derived/consortium-subset/`
4. `fulltext/inventory/`
5. `derived/relevance/`

That path moves from broad collection to the current mechanistic literature core.
