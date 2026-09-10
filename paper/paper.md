---
title: 'SPECGAP: an open engine for auditing the coverage of public mass spectral libraries'
tags:
  - Python
  - metabolomics
  - natural products
  - mass spectrometry
  - cheminformatics
  - open data
authors:
  - name: Oshoma Erumiseli
    orcid: 0009-0004-3813-4650
    affiliation: 1
affiliations:
  - name: Independent Researcher, Corvallis, Oregon, USA
    index: 1
date: 9 September 2026
bibliography: paper.bib
---

# Summary

Untargeted metabolomics identifies unknown compounds by matching their MS/MS
fragmentation spectra against reference spectral libraries. How well that can
work is bounded by a quantity nobody routinely measures: how much of known
chemical space actually has a reference spectrum. `SPECGAP` measures it.
The engine cross-matches open natural-product structure databases (COCONUT,
LOTUS) against the open spectral-library layer (GNPS, MassBank, MoNA) on
InChIKey identity, and reports two distinct quantities — **structural
coverage**, the share of documented structures with at least one matching
spectrum, and **name-recoverability**, the share of spectral-library entries
whose declared compound name can be reconciled with the structure database.

`SPECGAP` parses each source's native format directly (MassBank records, MGF,
MSP, GNPS JSON, SDF, and LOTUS's CSV export), streams inputs so that
multi-gigabyte libraries run within ordinary laptop memory, and separates
records that are *genuinely uncovered* from those that are *unjoinable* for
want of a structure identifier. Every reported rate names its denominator.
Applied to the complete open layer — 2,745,226 MS2 spectra against 738,823
COCONUT and 227,298 LOTUS structures — it finds roughly 90% of documented
natural-product space has no reference spectrum, that coverage saturates
sharply as libraries are aggregated, and that name-recoverability is a
property of the structure-database/spectral-library *pair* rather than of
either alone.

# Statement of need

Practitioners know that most features in an untargeted metabolomics run go
unannotated, and reviews of the field regularly cite the annotation gap as a
central obstacle. What has been missing is a reproducible measurement: the
gap is asserted, estimated from experience, or inferred from library size,
rather than computed from public data by a script anyone can rerun.

Existing tools address adjacent problems. `matchms` [@Huber2020] provides
spectrum processing and similarity scoring; the GNPS ecosystem
[@Wang2016] supports molecular networking and library search; MassBank
[@Horai2010] and MoNA distribute the libraries themselves. These operate on
spectra. None audits a spectral library *against an external
structure-space reference* to answer how much of known chemistry it covers,
and none does so across libraries in a way that makes the result comparable.

`SPECGAP` fills that gap and is designed to be re-run: a coverage benchmark
refreshed against each new release, rather than a one-off analysis. Its
outputs are a versioned dataset and a QA report, not only a figure.

Three design decisions distinguish it from an ad-hoc script:

**Unjoinable is not uncovered.** A structure with no InChIKey, or a spectrum
whose library recorded none, cannot be assessed at all. Counting such records
as uncovered inflates the gap. This is not a corner case: the GNPS MGF export
defines no InChIKey field, so an audit reading GNPS via MGF would report 100%
of it as missing structure coverage — a property of the export format, not
the library. `SPECGAP` reports the two outcomes separately and states the
denominator for every rate.

**Computationally derived spectra are excluded by default.** MoNA
distributes 3,191,104 in-silico spectra against 1,752,437 experimental ones,
and GNPS marks a large propagated subset. A predicted spectrum is a computed
expectation, not evidence a compound has been measured. Including them
measures how much computation has been applied to a database, not how much
of chemical space has been observed.

**Both matching criteria are always computed.** Exact InChIKey matching is
correct when stereochemistry-specific identification matters; skeleton-level
matching is correct when asking whether any usable reference exists for a
scaffold. The choice moves the answer by a factor of 3.4, so `SPECGAP`
reports both and leaves the scientific judgement to the user.

# Functionality

The library exposes parsers (`specgap.parsers`), identity handling
(`specgap.identity`), the matching engine (`specgap.coverage`) and reporting
(`specgap.report`). A worked example against the bundled fixtures:

```
pip install -e ".[dev,figures]"

python scripts/02_audit.py \
  --structures data/coconut.sdf:COCONUT \
  --spectra-massbank data/MassBank-data/ \
  --spectra-msp data/MoNA-experimental.msp:MoNA \
  --spectra-json data/ALL_GNPS_NO_PROPOGATED.json \
  --ms-level MS2 --out data/processed \
  --provenance "COCONUT 09-2026 x open spectral layer, MS2"
```

This writes per-structure and per-spectrum audit tables, a `stats.json`, and
a human-readable QA report carrying row counts, per-source joinability, named
spot checks and sanity assertions. `scripts/04_inventory.py` profiles a
single library without a structure database. Column definitions are in
`docs/CODEBOOK.md`; format-level decisions in `docs/FORMATS.md`.

MS level, ion mode and compound names are normalised across sources, which
matters more than it sounds: GNPS records MS level as `"2"` while MassBank
and MoNA write `"MS2"`, so a naive level filter silently discards an entire
library. The package has no runtime dependencies beyond the standard library
(`matplotlib` is needed only for figures), runs on Python 3.9+, and ships 80
tests exercised in CI, including parser tests built from field layouts in the
sources' own published specifications.

# Results obtained with the software

Full method and caveats in `docs/FULL_AUDIT.md`; all figures are regenerated
from the released `stats.json` files.

- **~90% of documented natural-product space has no reference spectrum.**
  90.34% of COCONUT and 88.16% of LOTUS structures have no MS2 spectrum in
  GNPS, MassBank or MoNA, even at skeleton level.
- **Coverage saturates.** A 19.7× increase in spectra (139,240 → 2,745,226)
  produced a 2.6× increase in coverage (1.09% → 2.86%). Of 280,024 distinct
  compounds across the whole layer, 7.5% are COCONUT natural products.
- **Composition beats size.** GNPS contributed 7.4× fewer new compounds than
  MoNA but nearly as many newly covered structures: an 18.8% hit rate against
  natural-product space versus MoNA's 3.2%.
- **Name-recoverability is a property of the pair.** The same 2,745,226
  spectra recover 69.54% of their names against COCONUT and 36.17% against
  LOTUS — a 33.4-point difference with the spectral side held identical. Any
  figure of the form "library X has N% name-recoverability" is under-specified
  without naming the reference database.
- **Joinability varies 6.5-fold.** MassBank 0.90%, MoNA 1.35%, GNPS JSON
  5.88% of records unjoinable — and the GNPS MGF export is wholly unjoinable.

# Acknowledgements

This work rests entirely on data made openly available by the COCONUT, LOTUS,
GNPS, MassBank and MoNA teams. Development of the software, including code
scaffolding, documentation drafting and format research, was assisted by
Claude (Anthropic); all analytic decisions, scope judgements, verification
and final text are the author's.

# References
