# SPECGAP coverage audit — data descriptor (DRAFT)

**Status: DRAFT, synthetic fixture run. Not for citation.** See
`docs/BUILD_SPEC.md` and `README.md`. Replace this entire status block once
`code/01_fetch.py` has pulled real data and the pipeline has been re-run
with `--final`.

## What this dataset is

`data/processed/coverage_audit.csv` and `data/processed/name_recoverability.csv`
are a snapshot audit of how much of the documented natural-product structure
space (LOTUS + COCONUT) has a corresponding reference spectrum in the major
open MS/MS spectral libraries (GNPS + MassBank + MoNA), and how often
spectral-library compound names can be reconciled back to those structures.

## Methods

Structures are keyed on InChIKey; a match requires either an identical
27-character InChIKey (exact) or an identical first-14-character skeleton
(looser, ignores stereochemistry — see `docs/LIMITATIONS.md`, item 2).
Name-recoverability normalizes declared spectral-library names (casefold,
strip common salt/hydrate suffixes) and accepts an exact or ≥0.92
Levenshtein-ratio fuzzy match against any name recorded for that InChIKey in
the structure tables. Full logic: `code/02_build.py`; full column
definitions: `docs/CODEBOOK.md`.

## Validation

`code/03_qa.py` writes `qa_report.txt` with row counts at each stage, match
rates by source, and five hand-checkable spot-check records per run. See
`docs/VERIFY_CHECKLIST.md` for the author's pre-release verification steps,
none of which have been completed yet for this draft.

## Current (fixture) snapshot

See `data/processed/stats.json`, generated 2026-09-01 from the synthetic
fixture in `data/raw/fixtures/`. These numbers describe the pipeline test
run, not real coverage.

## Usage notes

Once real data has been substituted, this file's headline numbers should be
read alongside `docs/LIMITATIONS.md` in full — in particular, the choice
between exact-InChIKey and skeleton-level coverage as the reported figure,
and whether license-restricted MoNA records are included.
