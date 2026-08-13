# Literature Workflow

## Current Priority

Finish the literature side before moving into dataset extraction.

That means the next work should focus on:

1. paper collection integrity
2. paper classification and tagging
3. center / PI attribution
4. relevance filtering for the cross-virus scientific question
5. construction of a curated literature subset for downstream reasoning

Dataset extraction comes after the literature corpus is stable enough to support it.

## Collection Model

The literature side should not rely on one grant-query link alone.

Use three distinct layers:

1. `current-program`
   Papers returned by the official public grant-query corpus.
2. `hpmi`
   HPMI-specific literature stream, currently defined first by the HPMI grant-number query and only later expanded by PI/lab searches and manual backfill.
3. `pi-backlog`
   Papers discovered by PI-name and lab-based searches, including historical and newly published work.
4. `full-collection`
   The union of the official query-based corpus, HPMI-specific collection, and PI-name-based tracking.

This matters because the official current-program query may be incomplete with respect to current centers such as HPMI.

## Literature Phases

### Phase L1: Current-program corpus

Goal:

- maintain the official current-program paper collection from the PubMed grant query

Outputs:

- normalized paper records
- manifest of all current-program papers

Status:

- initial ingest complete

### Phase L2: Paper classification

Goal:

- classify current-program papers by center, PI, pathogen/virus, assay type, and scientific relevance

Minimum tags:

- `center`
- `pi_candidates`
- `pathogens`
- `viruses`
- `assay_types`
- `paper_kind`
- `cross_virus_relevance`

### Phase L3: PI paper tracking

Goal:

- collect broader PI historical and newly published papers outside the strict grant-query corpus

This remains separate from the current-program corpus.

Current first-pass rule:

- search all current program PIs over the last 20 years
- remove overlaps with `current-program` and `hpmi`
- retain explicit per-PI search-summary outputs so the backlog is auditable

It also serves as a correction layer when the official query under-represents a current center.

### Phase L3b: HPMI-specific collection

Goal:

- maintain an explicit HPMI literature stream using HPMI-aware collection logic

This is separate because HPMI is strategically central to the target scientific workflow and may be incompletely represented by the general query.

### Phase L4: Curated consortium subset

Goal:

- build a smaller literature subset that is most relevant to:
  - host-pathogen interactions
  - host dependency
  - comparative virology
  - pathway-level convergence
  - reusable evidence for Symposium-style reasoning

This subset should feed the first scientific workflows.

### Phase L5: Continuous publication tracking

Goal:

- keep all three literature layers updated without manual reruns

Current implementation path:

- local orchestrator script: `scripts/run_literature_refresh.py`
- scheduled repo workflow: `.github/workflows/pubmed-refresh.yml`

## Literature-First Rules

- do not start dataset extraction until paper-level classification is good enough
- do not mix official program papers with broader PI backlog papers
- do not optimize for exhaustive reading before basic tagging exists
- do not try to infer pathway convergence from raw titles alone

## Review Order

Recommended order:

1. current-program papers published most recently
2. viral papers most relevant to host dependency and host-pathway questions
3. historically important PI papers that define major assay or interaction-map resources
4. broader backlog papers

## Required Outcomes Before Dataset Phase

Before moving heavily into datasets, the literature side should produce:

- a trustworthy current-program paper list
- a trustworthy HPMI paper list
- a broader PI-name-based literature collection
- an inspectable PI-backlog search summary by PI
- a defensible union view of the full collection
- an attributed center / PI view of the corpus
- a tagged viral subset
- a shortlist of papers most likely to contain reusable datasets/resources
- a curated literature subset for the cross-virus pathway question
