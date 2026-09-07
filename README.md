# SPECGAP

**An open engine for assessing the coverage of public mass spectral libraries.**

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

## Status: engine complete, full-corpus audit not yet run

The engine is finished and tested (69 tests). It parses the sources' **native
formats** — GNPS MGF, GNPS JSON, MoNA/GNPS MSP, MassBank records, COCONUT and
LOTUS SDF — and the test fixtures reproduce field layouts taken from those
projects' own published specifications.

What has **not** happened yet is a run against the full multi-million-record
downloads. No corpus-wide coverage percentage is published here, and none
should be quoted from this repository. `scripts/01_fetch.py` points at the
real bulk endpoints; running it is the next step and requires only bandwidth
and disk.

## First finding: the GNPS MGF export cannot be joined at all

The GNPS MGF format defines `SMILES`, `INCHI` and `INCHIAUX` but **no
`INCHIKEY` field**, and both structure fields are frequently the literal
string `N/A`. Every GNPS MGF record is therefore *unjoinable* for
InChIKey-based coverage analysis.

This matters beyond SPECGAP: an audit that reads GNPS via MGF and reports the
result as *uncovered* structure space is measuring the export format rather
than the library's content, and will overstate the coverage gap
systematically. Use the `.json` or `.msp` exports instead.

SPECGAP therefore separates two outcomes that are easy to conflate:

| Outcome | Meaning |
|---|---|
| `uncovered` | joinable, and genuinely absent from every spectral library |
| `unjoinable` | no usable structure identifier — the question cannot be answered |

Every reported rate names its denominator for the same reason. Details in
[`docs/FORMATS.md`](docs/FORMATS.md); pinned by
`tests/test_e2e.py::test_gnps_mgf_is_wholly_unjoinable`.

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
scripts/              01_fetch, 02_audit, 03_figures
tests/                69 tests; fixtures reproduce documented field layouts
docs/                 FORMATS, BUILD_SPEC, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST
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

See [`CITATION.cff`](CITATION.cff). A DOI will be minted on the first
real-data release.
