# COCONUT × (MassBank + MoNA) coverage audit

Adding a second spectral library to
[`COVERAGE_AUDIT.md`](COVERAGE_AUDIT.md). Two of three libraries now
included; GNPS remains outstanding.

Sources: [COCONUT](https://coconut.naturalproducts.net) SDF 2D, September
2026 (CC0) × [MassBank-data](https://github.com/MassBank/MassBank-data)
2026.03 + [MoNA](https://mona.fiehnlab.ucdavis.edu) experimental export.
**MS2 only.** Run 2026-09-07, SPECGAP v0.5. Figures:
`data/processed/coconut_massbank_mona_audit_2026.09.json`.

```
python scripts/02_audit.py \
  --structures <coconut_sdf_2d-09-2026.sdf>:COCONUT \
  --spectra-massbank <MassBank-data-2026.03> \
  --spectra-msp <MoNA-export-Experimental_Spectra.msp>:MoNA \
  --ms-level MS2 --out data/processed \
  --provenance "COCONUT 09-2026 x (MassBank 2026.03 + MoNA experimental MS2)"
```

---

## Headline

| Measure | MassBank only | **+ MoNA (MS2)** |
|---|---|---|
| Spectra | 139,240 | **1,788,666** |
| Distinct compounds | 20,335 | **249,218** |
| Covered, exact InChIKey | 8,025 (1.09%) | **15,338 (2.08%)** |
| Covered, skeleton | 27,068 (3.66%) | **58,225 (7.88%)** |
| Uncovered at skeleton | 96.34% | **92.12%** |
| Name-recoverability | 89.87% | **83.15%** |

COCONUT side unchanged: 738,823 structures, 100% joinable.

## 1. Twelve times the compounds, twice the coverage

MoNA contributed **12.3× more distinct compounds** (20,335 → 249,218) but
raised exact coverage only **1.91×** and skeleton coverage **2.15×**.

The efficiency figure states it plainly. Of MassBank's 20,335 distinct
compounds, **39.5% are COCONUT natural products**. Across the combined
249,218, only **6.2%** are. MoNA's 228,883 additional compounds yielded
7,313 newly covered structures — a **3.2% hit rate** against natural-product
space.

This is the central result of adding a second library: **the open spectral
layer is not scaling toward natural products.** MoNA is a large, valuable
resource, but its growth is concentrated in pharmaceutical, environmental
and metabolomic chemical space that barely intersects documented
natural-product diversity. Extrapolating the gap's closure from raw library
growth is therefore wrong by roughly an order of magnitude.

## 2. The gap is still ~92%

680,598 of 738,823 COCONUT structures have no MS2 spectrum in either
library, even at skeleton level. Two of the three major open libraries,
1.79M spectra, and more than nine in ten documented natural products remain
spectrally unmeasured.

## 3. Stereochemistry mismatch grew: skeleton matching now 3.80×

Relaxing exact InChIKey to skeleton adds 42,887 structures — a **3.80×
multiplier**, up from 3.37× with MassBank alone.

That it *rose* with a second, independently-curated library argues the
effect is systemic rather than a MassBank quirk: spectral libraries and
structure databases disagree about stereochemical assignment generally.
Roughly three quarters of all structures with any spectral match have it
only at skeleton level.

## 4. MoNA's naming is measurably worse than MassBank's

Name-recoverability fell from **89.87% to 83.15%** while the assessable
population grew from 72,981 to 245,992 spectra. Since MassBank's own figure
is unchanged, MoNA's naming must be materially messier — its share of the
combined pool recovers at a lower rate.

Both remain far above the ~8% structural coverage. The conclusion from
`COVERAGE_AUDIT.md` holds and strengthens: **naming is not the binding
constraint; acquisition is.**

Full accounting (sums exactly to 1,788,666):

| Outcome | Records | Share |
|---|---|---|
| Structure not in COCONUT | 1,518,798 | 84.9% |
| Recoverable | 204,543 | 11.4% |
| Unrecoverable | 41,449 | 2.3% |
| No InChIKey | 23,585 | 1.3% |
| No declared name | 291 | 0.02% |

**84.9% of MS2 spectra in both libraries describe compounds absent from
COCONUT entirely.** The open spectral layer is overwhelmingly not about
natural products.

## 5. Scope decisions, and why they matter

Two filters were applied. Both change the result substantially and are
stated rather than buried.

**In-silico spectra excluded.** MoNA offers 3,191,104 predicted spectra
against 1,752,437 experimental. Predicted spectra are computed expectations,
not measurements, and cannot support identification of an unknown. Including
them would have inflated apparent coverage with computation rather than
observation. Only the experimental export was used.

**MS1 and MS3+ excluded.** MS1 records a mass, not a fragmentation
fingerprint. Verified level distributions:

- MassBank: MS2 117,211 · MS 21,011 · MS3 929 · MS4 70 · MSn 19 (sums to
  139,240)
- MoNA experimental: 1,671,455 of 1,752,437 are MS2

The 22,029 excluded MassBank records are genuinely non-MS2, not a parsing
failure — no spelling variants appear in the distribution.

Both filters *reduce* the reported spectral layer. The 92.12% gap is
therefore measured against the defensible comparator, not the largest
available number.

## Limitations

1. **GNPS is still missing** (~2.9M spectra). Its MGF export carries no
   InChIKey (`FORMATS.md`), so inclusion needs the JSON/MSP export and
   possibly structure conversion. Coverage will rise; on the MoNA evidence,
   probably by less than raw spectrum count suggests.
2. **MoNA licences are unfiltered.** Licences vary per record (the sampled
   record carries `CC BY-NC`). No redistribution claim should be made over
   MoNA-derived results without filtering.
3. **No spectral-quality weighting.** Any matching MS2 spectrum counts,
   regardless of instrument, quality or whether it would support
   identification in practice.
4. **Fuzzy name threshold (0.92) still untuned** against real name strings
   (`LIMITATIONS.md` item 4). The 83.15% figure is threshold-dependent.
5. **COCONUT is not ground truth for all natural products** — it aggregates
   collections of varying curation, some entries predicted rather than
   isolated.

## Open question worth resolving

MoNA's download page reports 3,596,790 total spectra, yet lists 3,191,104
in-silico and 1,752,437 experimental, which sum to 4,943,541. The categories
must overlap, or the counts were computed at different times. This does not
affect the results above — the experimental export was parsed directly and
its own record count used — but anyone citing MoNA's size should resolve it
first.
