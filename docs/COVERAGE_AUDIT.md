# COCONUT × MassBank structural coverage audit

**The two-sided measurement SPECGAP was built for.** How much of documented
natural-product structure space has a reference MS/MS spectrum?

Sources: [COCONUT](https://coconut.naturalproducts.net) SDF 2D, September 2026
release (CC0) × [MassBank-data](https://github.com/MassBank/MassBank-data)
release 2026.03. Both corpora complete, no sampling.
Run 2026-09-07, SPECGAP v0.3, Python 3.9. Reproduce with:

```
python scripts/02_audit.py \
  --structures <coconut_sdf_2d-09-2026.sdf>:COCONUT \
  --spectra-massbank <MassBank-data-2026.03> \
  --out data/processed \
  --provenance "COCONUT SDF 2D 09-2026 (CC0) vs MassBank-data 2026.03"
```

Figures: `data/processed/coconut_massbank_audit_2026.09.json`.

---

## Headline

| Measure | Value |
|---|---|
| COCONUT structures | **738,823** (100% joinable) |
| MassBank spectra | 139,240 (98.58% joinable, 20,335 distinct compounds) |
| **Covered, exact InChIKey** | **8,025 — 1.09%** |
| **Covered, skeleton level** | **27,068 — 3.66%** |
| Uncovered even at skeleton level | 711,755 — **96.34%** |
| Name-recoverability | **89.87%** of assessable spectra |

**Scope.** This measures COCONUT's coverage by **MassBank alone**, not by the
whole open spectral layer. GNPS and MoNA are not included; adding them will
raise coverage. Read every number below as *coverage by one library*.

## 1. The coverage gap is ~96%, and it is structural not incidental

Fewer than four in a hundred documented natural-product structures have a
MassBank spectrum sharing even their molecular skeleton. At exact-InChIKey
identity it is one in a hundred.

The arithmetic ceiling makes the shape of this clear: MassBank holds 20,335
distinct compounds against COCONUT's 738,823 structures, so **even if every
MassBank compound were a COCONUT natural product, exact coverage could not
exceed 2.75%**. The measured 1.09% is 40% of that theoretical maximum. The
gap is not a MassBank curation failure; it is a scale mismatch between what
has been chemically documented and what has been spectrally measured.

## 2. Stereochemistry matters more than expected: skeleton matching triples coverage

Relaxing from exact InChIKey to 14-character skeleton takes coverage from
8,025 to 27,068 structures — a **3.37× increase, 19,043 additional
structures**.

This is the most consequential methodological finding in the run. MassBank's
own internal stereochemistry redundancy is only 11.4% (20,335 InChIKeys
collapsing to 18,026 skeletons, see `MASSBANK_INVENTORY.md`), so a 3.37×
cross-database effect cannot be explained by redundancy within either
source. It means **MassBank and COCONUT frequently describe the same
molecular graph with different stereochemical annotation** — differing
assignments, unspecified centres on one side, or genuinely different
stereoisomers of the same scaffold.

Practically: ~19,000 COCONUT structures have a MassBank spectrum of a
stereochemically-related compound that exact-key matching discards. Whether
those count as "covered" is a scientific judgement, not a default:

- **Exact InChIKey** is correct if stereochemistry-specific identification is
  the goal. Diastereomers can differ in fragmentation and in bioactivity.
- **Skeleton** is correct if the question is whether *any* usable reference
  spectrum exists for that scaffold, given that libraries often cannot
  resolve stereochemistry from MS/MS anyway.

SPECGAP reports both and takes no position. Spot checks confirm the skeleton
matches are genuine stereoisomer near-misses, not parser artefacts — e.g.
`SLYDIPAXCVVRNY-UOWMTANKSA-N` (COCONUT, skeleton-only) against exact matches
such as `GAPDDBFHNYHZIS-LXFDRBQGSA-N`, differing in the second block.

## 3. Naming is in far better shape than coverage

**89.87% of assessable spectra (65,588 of 72,981) recover their compound
name** against COCONUT. Only 7,393 (10.13%) are unrecoverable.

The two layers are decoupled. Chemical space coverage is ~4%; naming
integrity within what *is* covered is ~90%. Improving one would not have
improved the other. For anyone prioritising work on public spectral
infrastructure, this argues that acquisition of new reference spectra — not
metadata cleanup — is the binding constraint.

Full outcome accounting (sums exactly to 139,240):

| Outcome | Records | Share |
|---|---|---|
| Recoverable | 65,588 | 47.1% |
| Structure not in COCONUT | 64,252 | 46.1% |
| Unrecoverable | 7,393 | 5.3% |
| No InChIKey | 1,976 | 1.4% |
| No declared name | 31 | 0.02% |

## 4. MassBank's natural-product content is ~4× what its own field reports

46.1% of MassBank spectra describe compounds absent from COCONUT entirely —
expected, since MassBank is an environmental, exposomics and pharmaceutical
library, not an NP library.

More interesting: **8,025 of MassBank's 20,335 distinct compounds (39.5%) are
present in COCONUT**, i.e. are documented natural products. MassBank's own
`CH$COMPOUND_CLASS` field classes only 9.45% of records as natural products.

This independently confirms the caveat raised in `MASSBANK_INVENTORY.md`:
that 9.45% is a floor produced by an unpopulated field (53.4% of records
leave it `N/A`), not a measurement. Cross-referencing against a structure
database recovers roughly four times as much natural-product content as
trusting the annotation. **Do not filter MassBank for natural products using
`CH$COMPOUND_CLASS`** — it discards about three quarters of them.

## 5. Both corpora are fully joinable

COCONUT: 738,823 of 738,823 structures carry a well-formed InChIKey — 100%.
MassBank: 98.58%. Against the GNPS MGF export's 0% (`FORMATS.md`), the three
sources span the entire range of what is measurable:

| Source | Joinable | Consequence |
|---|---|---|
| COCONUT SDF | 100% | fully auditable |
| MassBank records | 98.58% | fully auditable |
| GNPS `.mgf` | 0% | not auditable in this format at all |

No coverage number over GNPS-via-MGF is meaningful; the format carries no
structure key.

## Limitations specific to this audit

1. **One spectral library.** Coverage by MassBank alone. GNPS and MoNA would
   raise it, by an unknown amount. The 96.34% uncovered figure is an upper
   bound on the true gap across the whole open spectral layer.
2. **No spectral-quality weighting.** A structure counts as covered if any
   matching spectrum exists, regardless of quality, instrument, or whether
   the spectrum would actually support identification.
3. **COCONUT is not ground truth for "all natural products."** It aggregates
   ~750k structures from many collections with varying curation; some entries
   are predicted rather than isolated. Coverage of COCONUT is not identical
   to coverage of nature.
4. **Deprecated MassBank records are included.** The format permits a
   `DEPRECATED` marker that `parse_massbank_record` does not currently
   exclude; a small number of the 139,240 may be withdrawn records.
5. **Name-recoverability uses a fixed 0.92 fuzzy threshold**, chosen a priori
   and not tuned against these name strings (`LIMITATIONS.md` item 4). The
   89.87% figure would shift somewhat under a different threshold.

## What comes next

Adding GNPS (via `.json`/`.msp`, never `.mgf`) and MoNA would convert this
from "coverage by MassBank" into coverage by the open spectral layer, which
is the project's stated goal. LOTUS on the structure side would test whether
the gap looks different against a differently-curated NP reference.
