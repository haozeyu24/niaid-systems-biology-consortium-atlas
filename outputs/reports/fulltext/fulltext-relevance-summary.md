# Full-Text Relevance Summary

This report summarizes the full-text selection pass over the 654-paper candidate corpus.

## Counts

- `relevant`: `215`
- `maybe`: `174`
- `not_relevant`: `265`

## Counts By Source

### relevant

- `pi-backlog`: `145`
- `hpmi`: `36`
- `current-program`: `34`

### maybe

- `current-program`: `93`
- `pi-backlog`: `64`
- `hpmi`: `17`

### not_relevant

- `pi-backlog`: `155`
- `hpmi`: `55`
- `current-program`: `55`

## Heuristic Meaning

- `relevant`: title+abstract and full text support virus-focused host-mechanism or explicit cross-virus/shared-host relevance.
- `maybe`: virus-relevant, but likely narrower, more clinical/therapeutic, or worth later inspection before promotion.
- `not_relevant`: dominated by non-viral pathogens, generic methods/resources, off-target disease areas, or weak host-mechanism relevance for this project.

## Example Relevant Papers

- `pmid-37758692` Proteomic and genetic analyses of influenza A viruses identify pan-viral host targets.
  Reason: explicit cross-virus/shared-host full-text language: pan-viral
- `pmid-33060197` Comparative host-coronavirus protein interaction networks reveal pan-viral disease mechanisms.
  Reason: explicit cross-virus/shared-host full-text language: pan-viral
- `pmid-42013838` Systematic discovery of pro- and anti-HIV host factors in primary human CD4+ T cells.
  Reason: viral context plus mechanism-rich title/abstract: hiv, virus, viral, hiv, host factor, host factors
- `pmid-37738970` SARS-CoV-2 variants evolve convergent strategies to remodel the host response.
  Reason: explicit cross-virus/shared-host full-text language: cross virus, conserved host
- `pmid-42134328` Coronavirus protein interaction mapping in bat and human cells reveals network rewiring governing immune evasion and zoonotic potential.
  Reason: explicit cross-virus/shared-host full-text language: cross virus, shared host, conserved host
- `pmid-42182519` Pathogen-specific host responses define distinct pneumonia endotypes in the human lung.
  Reason: virus-focused title/abstract plus weaker cross-virus framing in body: broad-spectrum, covid-19, host response, interaction, interactions, alveolar
- `pmid-34171302` An ancient viral epidemic involving host coronavirus interacting genes more than 20,000 years ago in East Asia.
  Reason: explicit cross-virus/shared-host full-text language: multiple viruses
- `pmid-32645325` The Global Phosphorylation Landscape of SARS-CoV-2 Infection.
  Reason: virus-focused title/abstract plus weaker cross-virus framing in body: broad-spectrum, coronavirus, sars-cov-2, sars, covid-19, pathway

## Example Maybe Papers

- `pmid-27120583` Synthesis and Anti-Influenza Activity of Pyridine, Pyridazine, and Pyrimidine C-Nucleosides as Favipiravir (T-705) Analogues.
  Reason: virus-focused paper with broad-spectrum or cross-virus language, but mainly therapeutic/clinical framing: broad-spectrum, anti-influenza activity, inhibitor, influenza
- `pmid-35150638` Mutations in SARS-CoV-2 variants of concern link to increased spike cleavage and virus transmission.
  Reason: virus-focused title/abstract with some host-mechanism signal: sars-cov-2, sars, replication
- `pmid-35411346` An immunoPET probe to SARS-CoV-2 reveals early infection of the male genital tract in rhesus macaques.
  Reason: virus-focused title/abstract with some host-mechanism signal: sars-cov-2, sars, replication
- `pmid-35262081` An immunoPET probe to SARS-CoV-2 reveals early infection of the male genital tract in rhesus macaques.
  Reason: virus-focused title/abstract with some host-mechanism signal: sars-cov-2, sars, replication
- `pmid-39488529` Live imaging of airway epithelium reveals that mucociliary clearance modulates SARS-CoV-2 spread.
  Reason: virus context appears stronger in body than title/abstract; possible mechanistic paper to inspect: virus, viral, sars-cov-2, sars, pathway, pathways
- `pmid-39303692` Genetic tracing of market wildlife and viruses at the epicenter of the COVID-19 pandemic.
  Reason: virus context appears stronger in body than title/abstract; possible mechanistic paper to inspect: virus, viral, sars-cov-2, sars, covid-19, screen
- `pmid-33930332` Functional landscape of SARS-CoV-2 cellular restriction.
  Reason: virus-focused title/abstract with some host-mechanism signal: coronavirus, sars-cov-2, sars, covid-19, replication
- `pmid-35012962` Preclinical and randomized phase I studies of plitidepsin in adults hospitalized with COVID-19.
  Reason: virus-focused title/abstract with some host-mechanism signal: sars-cov-2, sars, covid-19, replication

## Example Not-Relevant Papers

- `pmid-37857833` A Legionella toxin exhibits tRNA mimicry and glycosyl transferase activity to target the translation machinery and trigger a ribotoxic stress response.
  Reason: title is dominated by a non-viral pathogen context: legionella
- `pmid-38117589` Cross-family small GTPase ubiquitination by the intracellular pathogen Legionella pneumophila.
  Reason: title is dominated by a non-viral pathogen context: legionella, pneumophila
- `pmid-37577546` Cross-family small GTPase ubiquitination by the intracellular pathogen Legionella pneumophila.
  Reason: title is dominated by a non-viral pathogen context: legionella, pneumophila
- `pmid-33303586` Genetic interaction mapping informs integrative structure determination of protein complexes.
  Reason: non-viral pathogen focus dominates title/abstract/full text: bacterial
- `pmid-41688792` Membrane-associated effluxosomes coordinate multi-metal resistance in Mycobacterium tuberculosis.
  Reason: title is dominated by a non-viral pathogen context: mycobacter, tuberculosis, bacterium
- `pmid-27322406` Comparative Protein Structure Modeling Using MODELLER.
  Reason: non-viral pathogen focus dominates title/abstract/full text: candida
- `pmid-41171885` Mycobacterium tuberculosis triggers reduced inflammatory cytokine responses and virulence in mice lacking Tax1bp1.
  Reason: title is dominated by a non-viral pathogen context: mycobacter, tuberculosis, bacterium
- `pmid-41256720` Genome-wide screen in Mycobacterium tuberculosis infected macrophages reveals innate regulation of antibacterial mediators by IRF2.
  Reason: title is dominated by a non-viral pathogen context: mycobacter, tuberculosis, bacterial, bacterium
