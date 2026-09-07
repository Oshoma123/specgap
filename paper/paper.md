---
title: 'SPECGAP: an open Python engine for assessing the coverage of public mass spectral libraries'
tags:
  - Python
  - metabolomics
  - natural products
  - mass spectrometry
  - cheminformatics
authors:
  - name: Oshoma Erumiseli
    orcid: 0009-0004-3813-4650
    affiliation: 1
affiliations:
  - name: Independent Researcher, Corvallis, Oregon, USA
    index: 1
date: [DRAFT — set on first real-data release]
bibliography: paper.bib
---

<!-- STATUS: DRAFT. Written against a synthetic fixture run; see docs/BUILD_SPEC.md.
     Every number below is a placeholder from the fixture and MUST be replaced
     after a real run of code/01_fetch.py through code/04_figures.py --final. -->

# Summary

Untargeted metabolomics identifies unknown compounds in a sample by matching
their MS/MS fragmentation spectra against reference spectral libraries. Two
questions determine how useful this process can ever be: how much of the
known chemical space of natural products has a reference spectrum *anywhere*
in the public spectral-library ecosystem (structural coverage), and, when a
spectrum does have a name attached, how often can that name actually be
reconciled with an authoritative structure database (name-recoverability).
SPECGAP is a small, dependency-light Python engine that answers both
questions by cross-matching two open natural-product structure databases
(LOTUS, COCONUT) against three open spectral-library platforms (GNPS,
MassBank, MoNA), on InChIKey identity and on a looser InChIKey-skeleton
basis, and produces a reproducible, versioned audit as a byproduct of every
run.

# Statement of need

Researchers routinely observe that a large share of MS/MS features in an
untargeted metabolomics dataset go unannotated, but the scale and shape of
the underlying coverage gap — which parts of known natural-product chemical
space are simply absent from public spectral libraries, versus present but
under a name that doesn't resolve back to a structure — is not tracked as a
standing, reproducible measurement. Existing spectral-library quality tools
(e.g. `matchms`) focus on cleaning and searching individual libraries, not on
auditing coverage against an external structure-space ground truth across
multiple libraries at once. SPECGAP fills that specific gap: a small,
auditable tool whose entire output is reproducible from public data and a
public script, intended to be re-run periodically as a coverage benchmark
rather than as a one-off analysis.

# Functionality

SPECGAP's core operations are `code/02_build.py` (join structures against
spectra on InChIKey and InChIKey-skeleton; join spectral names against
structure names with configurable normalization and fuzzy matching) and
`code/03_qa.py` (compute per-source and overall coverage and
name-recoverability statistics with named spot checks). A worked example on
the bundled synthetic fixture:

```
python code/00_make_fixture.py
python code/02_build.py
python code/03_qa.py
```

produces `data/processed/coverage_audit.csv`, `name_recoverability.csv`,
`qa_report.txt`, and `stats.json`. Point the same two scripts at real data
fetched via `code/01_fetch.py` to get a real audit. Full column definitions
are in `docs/CODEBOOK.md`.

# Acknowledgements

This tool builds entirely on data made public by the LOTUS, COCONUT, GNPS,
MassBank, and MoNA teams; SPECGAP would not exist without their choice to
make natural-product and spectral data openly downloadable. Development of
this repository, including code scaffolding and documentation drafting, was
assisted by Claude (Anthropic); all analytic decisions, verification, and
final text are the author's.

# References
