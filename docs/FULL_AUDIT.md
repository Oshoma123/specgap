# The complete audit: two structure databases × the whole open spectral layer

**SPECGAP's headline result.** Every open natural-product structure database
cross-matched against every major open MS/MS spectral library.

| | |
|---|---|
| Structure side | COCONUT SDF 2D 09-2026 (738,823) · LOTUS frozen 260413 (227,298) |
| Spectral side | MassBank 2026.03 · MoNA experimental · GNPS `ALL_GNPS_NO_PROPOGATED` |
| Spectra analysed | **2,745,226 MS2** (2,848,089 parsed, non-MS2 excluded) |
| Filters | MS2 only · in-silico excluded · computationally propagated excluded |
| Run | 2026-09-09, SPECGAP v0.8, Python 3.9 |

Data: `data/processed/coconut_all3_audit_2026.09.json`,
`data/processed/lotus_all3_audit_2026.09.json`.

```
python scripts/02_audit.py \
  --structures <coconut_sdf_2d-09-2026.sdf>:COCONUT \
  --spectra-massbank <MassBank-data-2026.03> \
  --spectra-msp <MoNA-export-Experimental_Spectra.msp>:MoNA \
  --spectra-json <ALL_GNPS_NO_PROPOGATED.json> \
  --ms-level MS2 --out data/processed
```

---

## Results

| Reference database | Structures | Exact match | Skeleton match | Name-recoverability |
|---|---|---|---|---|
| COCONUT | 738,823 | 21,130 (**2.86%**) | 71,380 (**9.66%**) | **69.54%** |
| LOTUS | 227,298 | 11,554 (**5.08%**) | 26,910 (**11.84%**) | **36.17%** |

Both 100% joinable. The spectral side is byte-identical between the two runs,
so every difference is attributable to the reference database alone.

---

## 1. Roughly 90% of documented natural-product space has no reference spectrum

**90.34% of COCONUT and 88.16% of LOTUS have no MS2 spectrum anywhere in the
open spectral layer**, even under the permissive skeleton criterion that
ignores stereochemistry.

This is the whole layer: 2.75M MS2 spectra from all three major libraries,
280,024 distinct compounds. It is not a shortfall of one resource but the
aggregate state of open natural-product mass spectrometry.

## 2. Coverage saturates: 20× the spectra bought 2.6× the coverage

Measured against COCONUT, holding everything else fixed:

| Libraries | Spectra | Distinct compounds | Covered (exact) |
|---|---|---|---|
| MassBank | 139,240 | 20,335 | 8,025 (1.09%) |
| + MoNA | 1,788,666 | 249,218 | 15,338 (2.08%) |
| + GNPS | 2,745,226 | 280,024 | 21,130 (2.86%) |

A **19.7× increase in spectra produced a 2.6× increase in coverage.** The
compound-level view explains why: 280,024 distinct compounds are represented
across the whole layer, of which **7.5% are COCONUT natural products.** The
spectral layer is growing in pharmaceutical, environmental and metabolomic
chemical space that barely intersects natural-product diversity.

**Extrapolating gap closure from raw library growth is wrong by roughly an
order of magnitude.**

## 3. Composition beats size: GNPS is 6× more natural-product-relevant than MoNA

| Library added | New distinct compounds | Newly covered structures | Hit rate |
|---|---|---|---|
| MoNA | 228,883 | 7,313 | **3.2%** |
| GNPS | 30,806 | 5,792 | **18.8%** |

GNPS contributed **7.4× fewer** new compounds than MoNA yet nearly as many
newly covered structures. This is consistent with GNPS hosting dedicated
natural-product collections (NIH-NATURALPRODUCTSLIBRARY,
TUEBINGEN-NATURAL-PRODUCT-COLLECTION, XANTHONES-DB, LEAFBOT and others).

For anyone allocating effort toward closing the gap, this is the actionable
finding: **what a library contains matters far more than how much it
contains.**

## 4. Name-recoverability is a property of the pair, not the library

**The same 2,745,226 spectra recover 69.54% of their names against COCONUT
and 36.17% against LOTUS — a 33.4-point gap.**

Nothing about the spectra changed. MassBank, MoNA and GNPS declared exactly
the same compound names in both runs. The difference is entirely in what the
reference database calls those compounds: COCONUT aggregates synonyms from
many contributing collections, while LOTUS derives from Wikidata with
typically one traditional name plus an IUPAC name per structure.

A statement of the form *"library X has N% name-recoverability"* is not well
formed. It is meaningful only as *"N% against reference database Y"*, and the
choice of Y moves the figure by more than thirty points. SPECGAP reports the
pair in every result for this reason.

The effect was 40 points against two libraries and 33.4 against three, so it
narrows as the spectral layer broadens but does not disappear.

## 5. Metadata quality dilutes as libraries are aggregated

| Spectral layer | vs COCONUT | vs LOTUS |
|---|---|---|
| MassBank | 89.87% | — |
| + MoNA | 83.15% | 43.12% |
| + GNPS | **69.54%** | **36.17%** |

Name-recoverability declines monotonically with each library added, against
both reference databases. Aggregate metadata-quality figures are weighted
averages over sources of very different quality, and they fall as the
aggregate grows. MassBank alone reaches 89.87%; the whole layer manages
69.54%.

## 6. Curation beats size on the structure side too

LOTUS holds 227,298 structures to COCONUT's 738,823 — **3.3× smaller** — yet
is **1.78× better covered** (5.08% vs 2.86% exact; 11.84% vs 9.66%
skeleton).

LOTUS requires a referenced, validated structure-organism pair for inclusion.
COCONUT aggregates broadly, including entries from collections with weaker
provenance. The compounds that clear LOTUS's bar are disproportionately the
ones somebody has also measured.

**The coverage gap is therefore not uniform across natural-product space.**
It is narrower over well-documented, literature-anchored compounds and wider
over the long tail — by roughly a factor of two. A single headline coverage
figure for "natural products" conceals this.

Note the direction: LOTUS is *better covered* but has *worse
name-recoverability*. The two measures are not proxies for one another.

## 7. Joinability varies 6.5-fold across libraries

Measured in a single run, so the comparison is exact:

| Library | Spectra | Unjoinable | Rate |
|---|---|---|---|
| MassBank | 117,211 | 1,053 | **0.90%** |
| MoNA | 1,671,603 | 22,532 | **1.35%** |
| GNPS (JSON) | 956,412 | 56,276 | **5.88%** |

Unjoinable records carry no usable structure identifier and cannot be
assessed for coverage at all — they are reported separately, never as
uncovered.

This extends the format finding in `FORMATS.md`. The GNPS **MGF** export is
0% joinable because it defines no InChIKey field; its **JSON** export does
carry `InChIKey_smiles` and `InChIKey_inchi`, but is still 6.5× worse than
MassBank. Format choice determines whether an audit is possible at all;
curation determines how well it works.

## 8. Skeleton matching multiplies coverage 3.4×

Relaxing exact InChIKey to the 14-character skeleton takes COCONUT coverage
from 21,130 to 71,380 structures — **3.38×**, adding 50,250 structures whose
only spectral match differs in stereochemistry, isotopic labelling or
protonation state.

The multiplier was 3.37× with one library and 3.80× with two, so it is stable
across very different spectral layers. Structure databases and spectral
libraries disagree about stereochemical assignment systemically, not as an
artefact of any one source.

Which criterion to report is a scientific judgement SPECGAP does not make for
the user:

- **Exact InChIKey** is correct when stereochemistry-specific identification
  matters; diastereomers can differ in fragmentation and bioactivity.
- **Skeleton** is correct when the question is whether any usable reference
  exists for a scaffold, given that MS/MS often cannot resolve
  stereochemistry anyway.

Both are computed in every run.

---

## Scope decisions

Three filters were applied. Each **reduces** the reported spectral layer, and
each is stated rather than buried.

**In-silico spectra excluded.** MoNA offers 3,191,104 predicted spectra
against 1,752,437 experimental. Only the experimental export was used.

**Computationally propagated spectra excluded.** GNPS marks these
`GNPS_PROPOGATED`; the `ALL_GNPS_NO_PROPOGATED` aggregate was used.

**MS1 and MS3+ excluded.** MS1 records a mass, not a fragmentation
fingerprint. Verified level distribution for MassBank: MS2 117,211 · MS
21,011 · MS3 929 · MS4 70 · MSn 19 — sums exactly to 139,240, confirming no
spelling variants were silently dropped.

A predicted or propagated spectrum is a computed expectation, not evidence
that a compound has been measured. Counting them would report how much
computation has been applied to a database rather than how much of chemical
space has been observed.

## Limitations

1. **The spectral libraries overlap.** GNPS imports MASSBANK, MASSBANKEU and
   MONA as constituent libraries, so the three are not independent. Coverage
   is computed over distinct structures, which absorbs most double counting,
   but per-source spectrum counts are not additive and the marginal
   contributions in §3 are upper bounds.
2. **LOTUS and COCONUT overlap**, unquantified here. The two covered sets are
   not independent, so §6 compares coverage rates rather than union coverage.
3. **No spectral-quality weighting.** Any matching MS2 spectrum counts,
   regardless of instrument, quality flag, or whether it would support
   identification in practice.
4. **Fuzzy name threshold fixed at 0.92**, chosen a priori and untuned
   (`LIMITATIONS.md` item 4). The 33.4-point reference gap is far too large
   to be a threshold artefact, but absolute recoverability figures would
   shift.
5. **Deprecated MassBank records are included**; the format permits a
   `DEPRECATED` marker the parser does not currently exclude.
6. **Neither structure database is ground truth.** LOTUS is narrower and
   better referenced, COCONUT broader and more inclusive. They encode
   different decisions about what counts as a documented natural product.
7. **Snapshot, not trend.** One time point per source. Re-running against
   future releases would measure whether the gap is closing, which this
   cannot.

## Reproducing

All inputs are public and openly licensed. The full pipeline runs in about an
hour on a laptop; peak memory is bounded by the structure side (~1 GB), since
spectra are streamed. `docs/VERIFY_CHECKLIST.md` lists the checks to complete
before citing any figure here.
