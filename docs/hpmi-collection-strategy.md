# HPMI Collection Strategy

## Role of HPMI in this repo

HPMI is a first-class center in the consortium metadata and should be a first-class literature stream in the repo.

It should not depend only on:

- the general current-program grant query
- PI-name matching alone

## Collection strategy

Use three routes, but not at the same priority:

1. `hpmi_grant_query`
   This is the current primary route and defines the clean HPMI core corpus.
2. `pi_name_search`
   Use later as an expansion layer, not as the first definition of HPMI.
3. `manual_addition`
   Add known important HPMI papers that automated collection misses.

## Current implementation choice

The repo should currently use `hpmi_grant_query` as the active HPMI ingest path.

Why:

- lower noise
- cleaner provenance
- easier inspection
- avoids sweeping in unrelated PI papers from broad author searches

## Why not rely on PI names alone

PI-name search can:

- miss relevant consortium papers where the PI is not listed as an author
- pull in papers that are correct for the PI but not useful for the target workflow
- blur HPMI-specific work with broader lab output

## Why not rely on manual curation alone

Manual-only collection:

- does not scale
- is hard to reproduce
- makes update logic opaque

## Recommended HPMI scope

Start with papers associated with:

- Nevan Krogan
- Jeffrey Cox
- Michael Glickman
- Melanie Ott
- Andrej Sali
- Danielle Swaney
- Jennifer Doudna
- Trey Ideker

Then widen as needed for:

- project-level collaborators
- viral host dependency work
- computational/modeling outputs tied to HPMI

That widening should happen only after the grant-defined core has been inspected.

## Provenance

Each HPMI paper record should capture:

- `collection_route`
- `source_query` or `source_search`
- `source_url`
- `imported_at`

This is important because the repo will later need to explain why a paper is considered part of HPMI collection logic.
