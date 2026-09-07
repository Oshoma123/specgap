# Build spec — SPECGAP v0.2

PROJECT
  SPECGAP. Archetypes stacked: pipeline/tool (primary), open dataset (the
  audits), analysis paper (the findings).

QUESTION
  Of the natural-product structures documented in LOTUS and COCONUT, what
  fraction have at least one matching MS/MS spectrum in GNPS, MassBank or
  MoNA (structural coverage)? Of the entries in those libraries, what
  fraction carry a name reconcilable with those structure databases
  (name-recoverability)?

SOURCES
  See README.md source table and scripts/01_fetch.py, which carries the
  verified entry point and a format caveat for each.

UNIT OF ANALYSIS
  One chemical structure, keyed on InChIKey; also reported at the
  14-character skeleton level.

MEASURES
  structural_coverage      per structure; exact and skeleton; per source
  name_recoverability      per spectrum; exact and fuzzy; per source
  Both report unjoinable/unassessable records as their own category, never
  as failures, and always state the denominator used.

OUTPUTS
  data/processed/coverage_audit.csv
  data/processed/name_recoverability.csv
  data/processed/stats.json
  data/processed/qa_report.txt
  paper/figures/*.png

VENUES
  1. GitHub + Zenodo DOI (engine and, later, the audit dataset)
  2. JOSS (the engine; it now has tests, docs and packaging)
  3. ChemRxiv or a data-journal descriptor (the audit findings, once real)

VERIFY POINTS (author must rule on these personally)
  - exact-InChIKey vs skeleton as the headline coverage number
  - the fuzzy name threshold, re-tuned against real name strings
  - whether licence-restricted MoNA records enter the headline number
  - whether to add SMILES-to-InChIKey conversion so GNPS becomes joinable,
    and if so with which toolkit and which normalization settings

LICENSE
  Code MIT; audit outputs CC BY 4.0.

CONSTRAINT ON THIS BUILD
  Assembled in an environment without outbound network access. All parsing is
  validated against fixtures reproducing documented field layouts; no
  full-corpus download was performed. This is stated in the README status
  section rather than buried here.
