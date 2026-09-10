# SPECGAP

**An open engine for assessing the coverage of public mass spectral libraries.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22653061.svg)](https://doi.org/10.5281/zenodo.22653061)

SPECGAP cross-matches natural-product structure sets (**LOTUS**, **COCONUT**)
against the open spectral-library layer (**GNPS**, **MassBank**, **MoNA**) and
reports two things:

- **Structural coverage** — what share of documented natural-product structure
  space has at least one reference spectrum, by exact InChIKey and by
  InChIKey skeleton.
- **Name-recoverability** — what share of spectral-library entries carry a
  compound name that can be reconciled back to a natural-product identity.

Founded September 2026.
Maintainer: Oshoma Erumiseli ([ORCID 0009-0004-3813-4650](https://orcid.org/0009-0004-3813-4650)).
Code: [MIT](LICENSE) · Audit outputs: [CC BY 4.0](LICENSE-DATA).

## Status: complete

Engine finished and tested (80 tests, CI on Python 3.9 and 3.12). **Both
structure databases and all three spectral libraries have been audited at
full scale** — 2,745,226 MS2 spectra against 738,823 COCONUT and 227,298
LOTUS structures.

**Headline result: [`docs/FULL_AUDIT.md`](docs/FULL_AUDIT.md)**

| Reference database | Structures | Exact | Skeleton | Name-recoverability |
|---|---|---|---|---|
| COCONUT | 738,823 | 2.86% | 9.66% | 69.54% |
| LOTUS | 227,298 | 5.08% | 11.84% | 36.17% |

Earlier stages, kept for the trend they show: [MassBank inventory](docs/MASSBANK_INVENTORY.md)
· [COCONUT × MassBank](docs/COVERAGE_AUDIT.md) · [+ MoNA](docs/COVERAGE_AUDIT_2LIB.md)
· [LOTUS](docs/LOTUS_AUDIT.md)

## Findings

**~90% of documented natural-product space has no reference spectrum.**
90.34% of COCONUT and 88.16% of LOTUS have no MS2 spectrum anywhere in the
open spectral layer, even at skeleton level.

**Coverage saturates.** A 19.7× increase in spectra (139,240 → 2,745,226)
produced a 2.6× increase in coverage. Of 280,024 distinct compounds across
the whole layer, 7.5% are COCONUT natural products. Extrapolating gap closure
from library growth is wrong by roughly an order of magnitude.

**Composition beats size.** GNPS contributed 7.4× fewer new compounds than
MoNA but nearly as many newly covered structures — an 18.8% hit rate against
natural-product space versus MoNA's 3.2%.

**Name-recoverability is a property of the pair, not the library.** The same
2,745,226 spectra recover 69.54% of their names against COCONUT and 36.17%
against LOTUS. Any figure of the form "library X has N% name-recoverability"
is under-specified without naming the reference database.

**Curation beats size on the structure side too.** LOTUS is 3.3× smaller than
COCONUT but 1.78× better covered. The gap is narrower over well-referenced
compounds and wider over the long tail.

**Joinability varies 6.5-fold.** MassBank 0.90%, MoNA 1.35%, GNPS JSON 5.88%
unjoinable — and the GNPS MGF export is wholly unjoinable, defining no
InChIKey field at all.

**Skeleton matching multiplies coverage 3.4×**, stably across one, two and
three libraries — so structure databases and spectral libraries disagree
about stereochemical assignment systemically.

## Scope decisions

Three filters, each stated because each *reduces* the reported layer:
in-silico spectra excluded (MoNA ships 3.19M predicted vs 1.75M
experimental); computationally propagated spectra excluded (GNPS
`ALL_GNPS_NO_PROPOGATED`); MS1 and MS3+ excluded, since MS1 records a mass
rather than a fragmentation fingerprint.

## Install and run

```bash
pip install -e ".[dev,figures]"
pytest tests/ -v                      # 69 tests (Python 3.9+)

# Audit the bundled real-format fixtures (works offline):
python scripts/02_audit.py \
  --structures tests/fixtures/coconut_sample.sdf:COCONUT \
  --spectra-msp tests/fixtures/mona_sample.msp:MoNA \
  --spectra-massbank tests/fixtures/massbank_sample.txt \
  --spectra-mgf tests/fixtures/gnps_sample.mgf:GNPS \
  --out data/processed \
  --provenance "bundled documentation fixtures"
```

For a real audit, run `python scripts/01_fetch.py --list`, download the
current bulk files, and point the same `02_audit.py` invocation at them. The
code path is identical; only the input size changes.

## Layout

```
src/specgap/          the library
  identity.py         InChIKey validation, skeletons, adduct stripping, name norming
  coverage.py         the matching engine
  report.py           statistics and the QA report
  parsers/            mgf, msp, gnps_json, massbank, sdf
scripts/              01_fetch, 02_audit, 03_figures,
                      04_inventory (single-library audit),
                      05_inventory_figures, 06_coverage_figures,
                      07_twolib_figures, 08_reference_comparison
tests/                69 tests; fixtures reproduce documented field layouts
docs/                 LOTUS_AUDIT, COVERAGE_AUDIT_2LIB, COVERAGE_AUDIT,
                      MASSBANK_INVENTORY,
                      FORMATS, BUILD_SPEC, CODEBOOK, LIMITATIONS,
                      VERIFY_CHECKLIST
data/real_pilot/      5 hand-verified live COCONUT records
```

## Sources

| Source | Content | License | Checked |
|---|---|---|---|
| [LOTUS](https://lotus.naturalproducts.net) | structure–organism pairs | CC0 | 2026-09-07 |
| [COCONUT 2.0](https://coconut.naturalproducts.net) | ~700k natural products | CC0 | 2026-09-07 |
| [GNPS](https://external.gnps2.org/gnpslibrary) | ~2.9M reference spectra | CC0 (default) | 2026-09-07 |
| [MassBank](https://github.com/MassBank/MassBank-data) | ~120k spectra / ~18.5k compounds | CC BY (per record) | 2026-09-07 |
| [MoNA](https://mona.fiehnlab.ucdavis.edu) | ~3.6M records | varies per record | 2026-09-07 |

## Limitations

Read [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) before citing anything —
particularly on skeleton-level matching, the fuzzy name threshold, and MoNA's
per-record licensing.

## Citation

Erumiseli, O. (2026). *SPECGAP: an open engine for assessing the coverage of
public mass spectral libraries*. Zenodo. <https://doi.org/10.5281/zenodo.22653061>

Machine-readable metadata in [`CITATION.cff`](CITATION.cff). The DOI above is
the concept DOI and always resolves to the latest version; each release also
receives its own version DOI.
