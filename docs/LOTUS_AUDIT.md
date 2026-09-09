# LOTUS × (MassBank + MoNA): reference-database dependence

The same 1,788,666 MS2 spectra audited against a **second, independently
curated** natural-product structure database. Comparing this to
[`COVERAGE_AUDIT_2LIB.md`](COVERAGE_AUDIT_2LIB.md) isolates the effect of the
reference database, because the spectral side is byte-identical between the
two runs.

Sources: [LOTUS](https://lotus.nprod.net) frozen metadata export 260413
(Wikidata-derived, CC0) × MassBank 2026.03 + MoNA experimental. MS2 only.
Run 2026-09-09, SPECGAP v0.6. Figures:
`data/processed/lotus_massbank_mona_audit_2026.09.json`.

```
python scripts/02_audit.py \
  --structures-csv <260413_frozen_metadata.csv.gz>:LOTUS \
  --spectra-massbank <MassBank-data-2026.03> \
  --spectra-msp <MoNA-export-Experimental_Spectra.msp>:MoNA \
  --ms-level MS2 --out data/processed
```

---

## The result: identical spectra, opposite conclusions

| Measure | vs COCONUT | vs LOTUS |
|---|---|---|
| Reference structures | 738,823 | 227,298 |
| Covered, exact InChIKey | 15,338 (**2.08%**) | 9,251 (**4.07%**) |
| Covered, skeleton | 58,225 (**7.88%**) | 22,726 (**10.00%**) |
| Assessable spectra | 245,992 | 282,961 |
| **Name-recoverability** | **83.15%** | **43.12%** |
| Unrecoverable | 41,449 | 160,935 |

Spectral side identical in both runs: 1,788,666 spectra, 249,218 distinct
compounds, 1.79M records parsed from the same two files.

## 1. Name-recoverability is a property of the pair, not of the library

**The same spectra recover 83.15% of their names against COCONUT and 43.12%
against LOTUS — a 40-point difference.**

Nothing about the spectral libraries changed. MassBank and MoNA declared
exactly the same compound names in both runs. The entire difference comes
from what the reference database calls those compounds.

The mechanism is visible in the curation model. COCONUT aggregates synonyms
from many contributing collections, so a spectral library's chosen name is
likely to appear somewhere in its name set. LOTUS derives from Wikidata,
where a structure typically carries one traditional name plus an IUPAC name.
A spectrum labelled with a trade name, an abbreviation, or a
collection-specific synonym reconciles against COCONUT and fails against
LOTUS — not because the annotation is wrong, but because the reference is
narrower.

**Consequence for anyone measuring metadata quality:** a statement of the
form *"library X has N% name-recoverability"* is not well formed. It is
meaningful only as *"N% against reference database Y"*, and the choice of Y
can move the figure by 40 points. SPECGAP reports the pair in every result
for this reason.

## 2. Smaller and better curated beats larger: LOTUS is 3.3× smaller and 2× better covered

LOTUS holds 227,298 structures to COCONUT's 738,823, yet **4.07% of LOTUS is
spectrally covered against 2.08% of COCONUT** — and 10.00% versus 7.88% at
skeleton level.

This is consistent with the diminishing-returns result on the spectral side
(`COVERAGE_AUDIT_2LIB.md`), now appearing on the structure side. LOTUS
requires a referenced, validated structure-organism pair for inclusion;
COCONUT aggregates broadly, including entries from collections with weaker
provenance. The compounds that clear LOTUS's bar are disproportionately the
ones somebody has also measured.

So the coverage gap is not uniform across natural-product space. It is
narrower over well-documented, literature-anchored compounds and wider over
the long tail. **Reporting one coverage percentage for "natural products"
obscures this**; the figure depends on which definition of the space is used,
by roughly a factor of two.

In absolute terms COCONUT still has more covered compounds (15,338 vs 9,251)
— it is simply a larger and more heterogeneous target.

## 3. Both remain overwhelmingly uncovered

90.00% of LOTUS and 92.12% of COCONUT have no MS2 spectrum in MassBank or
MoNA even at skeleton level. Choosing the more favourable reference database
and the looser matching criterion still leaves nine in ten documented
natural products spectrally unmeasured.

Full LOTUS outcome accounting (sums exactly to 1,788,666):

| Outcome | Records | Share |
|---|---|---|
| Structure not in LOTUS | 1,481,829 | 82.8% |
| Unrecoverable | 160,935 | 9.0% |
| Recoverable | 122,026 | 6.8% |
| No InChIKey | 23,585 | 1.3% |
| No declared name | 291 | 0.02% |

## 4. LOTUS is 100% joinable

227,298 of 227,298 structures carry a well-formed InChIKey, matching
COCONUT's 100%. Both major open natural-product structure databases are
fully auditable; the joinability problem is confined to the spectral side,
and specifically to the GNPS MGF export (`FORMATS.md`).

## A parsing decision that materially affects the count

LOTUS's frozen export has **one row per (structure, organism, reference)
triple**, not per compound. A structure recorded from fifty organisms
appears in fifty rows. Counting rows as structures would have inflated the
denominator several-fold and driven the reported coverage percentage down
correspondingly.

`parsers/lotus_csv.py` aggregates by InChIKey, merging names and organisms,
and emits one entry per distinct structure — pinned by
`tests/test_parsers.py::test_lotus_csv_aggregates_rows_into_distinct_structures`.
Anyone reproducing this work from the raw CSV should confirm they have done
the same before comparing numbers.

## Limitations

1. **GNPS still absent** (~2.9M spectra). Coverage will rise for both
   reference databases; whether the LOTUS/COCONUT ordering survives is an
   open question this run cannot answer.
2. **The LOTUS/COCONUT overlap is unmeasured.** The two share many
   structures, so the covered sets are not independent. Quantifying the
   intersection would sharpen point 2 and is a natural next analysis.
3. **Name-recoverability remains threshold-dependent** (0.92, untuned —
   `LIMITATIONS.md` item 4). The 40-point gap is far too large to be a
   threshold artifact, but both absolute figures would shift.
4. **Neither database is ground truth for natural products.** LOTUS is
   narrower and better referenced; COCONUT is broader and more inclusive.
   Neither is "correct"; they encode different decisions about what counts.
