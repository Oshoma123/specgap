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

## Status: two-sided coverage audit complete

Engine finished and tested (69 tests), parsing the sources' **native formats**
— GNPS MGF, GNPS JSON, MoNA/GNPS MSP, MassBank records, COCONUT and LOTUS SDF.

**Full real runs completed against both sides:**
- MassBank release 2026.03 — 139,240 records ([`docs/MASSBANK_INVENTORY.md`](docs/MASSBANK_INVENTORY.md))
- COCONUT September 2026 × MassBank 2026.03 — 738,823 structures ([`docs/COVERAGE_AUDIT.md`](docs/COVERAGE_AUDIT.md))

Still outstanding: GNPS and MoNA on the spectral side. Current coverage
figures are **coverage by MassBank alone**, not by the whole open spectral
layer.

## Selected findings

**96% of natural-product structure space has no MassBank spectrum.** Of
738,823 COCONUT structures, 8,025 (1.09%) have an exact-InChIKey match in
MassBank; 27,068 (3.66%) match at skeleton level. Even if every one of
MassBank's 20,335 distinct compounds were a COCONUT natural product, exact
coverage could not exceed 2.75%.

**Skeleton matching triples coverage (3.37×).** Relaxing from exact InChIKey
to molecular skeleton adds 19,043 structures — far more than either source's
internal stereochemistry redundancy explains. The two databases frequently
annotate the same molecular graph with different stereochemistry.

**Naming is not the bottleneck; acquisition is.** 89.87% of assessable
spectra recover their compound name, against ~4% structural coverage. The
two layers are decoupled.

**MassBank's natural-product content is ~4× what its own field reports.**
39.5% of its distinct compounds appear in COCONUT, versus the 9.45% its
`CH$COMPOUND_CLASS` field claims — that field is unpopulated for 53.4% of
records. Do not filter MassBank for natural products with it.

**Joinability spans the full range.** COCONUT 100%, MassBank 98.58%, GNPS
`.mgf` 0% — the MGF format defines no InChIKey field, so no coverage number
computed over it is meaningful.

**Record counts overstate chemical coverage ~7×.** MassBank's 139,240
spectra represent 20,335 distinct compounds.

**MassBank is not uniformly CC BY.** 30.2% of records carry a non-commercial
restriction; 149 are no-derivatives.

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
                      05_inventory_figures, 06_coverage_figures
tests/                69 tests; fixtures reproduce documented field layouts
docs/                 COVERAGE_AUDIT (headline result), MASSBANK_INVENTORY,
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

Machine-readable metadata in [`CITATION.cff`](CITATION.cff). The DOI above
resolves to the archived release.
