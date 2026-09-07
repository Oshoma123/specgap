# MassBank inventory, release 2026.03

**First SPECGAP run on a real, complete spectral library.**

Source: [MassBank-data](https://github.com/MassBank/MassBank-data) release
2026.03, full corpus, every record file parsed.
Run 2026-09-07 with `scripts/04_inventory.py` (SPECGAP v0.2, Python 3.9).
Reproduce with:

```
python scripts/04_inventory.py --massbank <MassBank-data-2026.03> \
  --out data/processed --provenance "MassBank-data release 2026.03"
```

Machine-readable figures: `data/processed/massbank_inventory_2026.03.json`.

---

## Headline numbers

| Measure | Value |
|---|---|
| Records parsed | **139,240** |
| Records with a usable InChIKey | **137,264 (98.58%)** |
| Distinct compounds (unique InChIKey) | **20,335** |
| Distinct skeletons (stereochemistry ignored) | **18,026** |
| Spectra per distinct compound | **6.75** |
| Records classed as natural product | 13,159 (9.45%) — **a floor, see below** |
| Distinct natural-product compounds | 2,550 |
| Positive / negative ion mode | 97,803 / 41,437 (2.36 : 1) |

---

## 1. MassBank is 98.6% joinable — and that is not the norm

Only 1,976 of 139,240 records lack a well-formed InChIKey. Structural
coverage is therefore measurable across essentially the whole library.

The contrast with GNPS is the point. The **GNPS MGF export defines no
`INCHIKEY` field at all** (`docs/FORMATS.md`), so 100% of GNPS MGF records
are unjoinable — not uncovered, but unmeasurable. Whether spectral coverage
can be assessed *even in principle* depends on which library and which export
format an analyst happens to download:

| Source / format | Joinable on InChIKey |
|---|---|
| MassBank records | 98.58% (measured, this run) |
| GNPS `.mgf` | 0% — field does not exist (structural, verified from spec) |
| GNPS `.json` / `.msp` | partial — carries SMILES/InChI, InChIKey inconsistently |

An audit that reads GNPS via MGF and reports the shortfall as *uncovered
natural-product space* is measuring the export format, not the library.

## 2. 139,240 spectra is 20,335 compounds

The single most-misquoted figure about spectral libraries. At **6.75 spectra
per distinct compound** — different adducts, collision energies, instruments
and contributors for the same molecule — record counts overstate chemical
coverage by nearly sevenfold. Any statement of the form "library X contains
N spectra, so N compounds are identifiable" is wrong by that factor.

## 3. Stereochemistry accounts for 11.4% of apparent distinct compounds

20,335 unique InChIKeys collapse to 18,026 unique skeletons: **2,309 keys
(11.4%) differ from another key only in stereochemistry, isotopic labelling
or protonation state.**

This makes SPECGAP's exact-vs-skeleton matching decision concrete rather than
theoretical. Choosing skeleton-level matching enlarges the matchable
denominator by over a tenth before a single structure database is joined.
Since spectral libraries frequently cannot resolve stereochemistry, the
looser criterion is often the honest one — but it must be stated, not
assumed. (`docs/LIMITATIONS.md` item 3.)

All 137,264 keys are standard InChIKeys; none are non-standard.

## 4. Licensing: MassBank is not uniformly CC BY

MassBank's default licence is CC BY, and the project is usually described
that way. Per record, the actual distribution is more varied — the counts sum
exactly to 139,240, so this is the complete picture:

| Licence | Records | Share |
|---|---|---|
| CC BY | 48,404 | 34.8% |
| CC BY-NC-SA | 33,478 | 24.0% |
| CC BY-SA | 21,086 | 15.1% |
| `dl-de/by-2-0` | 20,658 | 14.8% |
| CC BY-NC | 8,434 | 6.1% |
| CC0 | 7,031 | 5.0% |
| CC BY-NC-ND | 149 | 0.1% |

**42,061 records (30.2%) carry a non-commercial restriction**, and 149 are
no-derivatives. Redistributing a derived dataset built on "MassBank, CC BY"
without filtering would misstate the terms for nearly a third of it.
`dl-de/by-2-0` is the German open-government data licence, attribution-style
and commercially permissive, so **69.8% is commercially reusable** — a
majority, but not the whole.

## 5. The natural-product figure is a floor, not an estimate

9.45% of records are classed as natural products. That number should not be
quoted as MassBank's natural-product content, because
**`CH$COMPOUND_CLASS` is unpopulated for 74,331 records (53.4%)** — `N/A`
(69,656) plus `NA` (4,675). Natural-product status is simply unknown for over
half the corpus. The true share lies somewhere between 9.45% and roughly 63%,
and this inventory cannot narrow it.

The field is also inconsistently curated where it *is* populated:
`Natural Product` (11,788) and `Natural product` (1,334) appear as distinct
strings. SPECGAP's check is case-insensitive and **anchored to the start of
the field**, which matters: the spec allows `Non-natural product` (2,172
records), and a naive substring test for "natural product" would silently
classify those as natural products, inverting them.

## Open question before citing any of this

MassBank's own published figures for the January 2026 release were
approximately **119,845 spectra across 18,529 compounds**. This run of the
2026.03 release finds **139,240 records and 20,335 compounds**. Growth over
two months is plausible, and the compound counts are close (18,529 published
vs 18,026 skeletons / 20,335 exact keys here — the published figure may count
skeletons). The record-count gap is larger and worth resolving: it may
reflect genuine growth, deprecated records that this parser includes, or a
different counting convention.

**Confirm MassBank's counting method before citing either figure**, and note
that `parse_massbank_record` currently does not exclude records marked
`DEPRECATED`, which the format specification permits.

## What this does and does not establish

**Does:** MassBank's joinability, distinct-compound count, stereochemistry
overlap, licence distribution and ion-mode balance, measured directly from
the complete corpus.

**Does not:** any statement about *structural coverage* of natural-product
chemical space. That requires the structure side — LOTUS or COCONUT — which
has not been downloaded or run. Coverage is a two-sided measurement and only
one side exists so far.
