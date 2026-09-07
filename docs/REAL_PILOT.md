# Real pilot dataset (n=5) — what it is and isn't

`data/raw/real_pilot/coconut_real_pilot.csv` contains **five real records**,
individually fetched live from COCONUT's public compound pages on
2026-09-01 (URLs in the `source_url` column — every row is independently
checkable by opening that URL). This is genuinely real data, unlike
`data/raw/fixtures/`, which is synthetic.

## What was measured

Each COCONUT compound page lists which external "collections" that
compound has been curated into — one of which is sometimes **GNPS**.
`in_gnps_collection` records whether COCONUT's own curators have tagged
that compound as present in GNPS.

## What this is NOT

This is **not** the InChIKey-join structural-coverage measurement that
`code/02_build.py` performs, and it is **not** a name-recoverability
measurement at all. Specifically:

- It relies on COCONUT's own asserted cross-reference, not an independent
  SPECGAP join against a real GNPS spectral record. No actual GNPS spectrum
  was fetched or matched against these InChIKeys.
- n=5 is a hand-picked, search-discovered convenience sample (compounds
  that happened to surface in web searches), not a random or representative
  sample of either LOTUS/COCONUT or GNPS. No coverage percentage computed
  from it should be read as an estimate of true corpus-wide coverage.
- Two of the five records don't expose an InChIKey in the fetched page
  content at all (only SMILES) — real-world data completeness varies even
  in a live, curated database.

## Why it's still worth having

It's a real, independently verifiable existence proof that the pipeline's
join logic operates on genuine identifiers from genuine sources, and it
gives one concrete real number (`3/5 = 60% of this hand-picked sample are
COCONUT-tagged as GNPS-cross-referenced`) to sit alongside the synthetic
fixture's numbers, clearly labeled as what it is: a 5-record convenience
sample, not an audit.

## How to extend this properly

A real, citable audit needs the actual bulk downloads (`code/01_fetch.py`)
and an independent InChIKey join against real GNPS/MassBank/MoNA spectral
records — not COCONUT's self-reported collection tags. This pilot is a
stepping stone toward that, not a substitute for it.
