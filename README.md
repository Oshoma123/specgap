# SPECGAP

**An open engine for assessing the coverage of public mass spectral libraries.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22653062.svg)](https://doi.org/10.5281/zenodo.22653062)

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

**Full real runs completed:**
- MassBank 2026.03 inventory — 139,240 records ([`docs/MASSBANK_INVENTORY.md`](docs/MASSBANK_INVENTORY.md))
- COCONUT × MassBank — 738,823 structures ([`docs/COVERAGE_AUDIT.md`](docs/COVERAGE_AUDIT.md))
- COCONUT × (MassBank + MoNA), MS2 only — 1.79M spectra ([`docs/COVERAGE_AUDIT_2LIB.md`](docs/COVERAGE_AUDIT_2LIB.md))
- LOTUS × (MassBank + MoNA), identical spectra — ([`docs/LOTUS_AUDIT.md`](docs/LOTUS_AUDIT.md))

Both structure databases done. Two of three spectral libraries. **GNPS
remains outstanding** — use its `ALL_GNPS_NO_PROPAGATED` JSON export, which
does carry InChIKeys (the MGF export does not).

## Selected findings

**92% of natural-product structure space has no MS2 spectrum** in either
MassBank or MoNA. Of 738,823 COCONUT structures, 15,338 (2.08%) match by
exact InChIKey and 58,225 (7.88%) at skeleton level, against 1.79M spectra.

**The spectral layer is not scaling toward natural products.** Adding MoNA
brought 12.3× more distinct compounds but only 1.9× the coverage. 39.5% of
MassBank's compounds are COCONUT natural products; across the combined
249,218 compounds, just 6.2% are. MoNA's 228,883 additional compounds
yielded 7,313 newly covered structures — a 3.2% hit rate.

**Name-recoverability is a property of the pair, not the library.** The same
1.79M spectra recover 83.15% of their names against COCONUT and 43.12%
against LOTUS — a 40-point swing with the spectral side held identical. Any
figure of the form "library X has N% name-recoverability" is meaningless
without naming the reference database.

**The gap is not uniform across natural-product space.** LOTUS is 3.3×
smaller than COCONUT but twice as well covered (4.07% vs 2.08% exact). The
better-referenced, more tightly curated database is the better-measured one;
coverage over the long tail is worse than a single headline figure suggests.

**Skeleton matching quadruples coverage (3.80×).** Relaxing exact InChIKey
to molecular skeleton adds 42,887 structures. The multiplier *rose* when a
second independently-curated library was added, arguing the
stereochemistry mismatch between spectral libraries and structure databases
is systemic rather than one library's quirk.

**Naming is not the bottleneck; acquisition is.** 83.15% of assessable
spectra recover their compound name, against ~8% structural coverage. MoNA's
naming is measurably worse than MassBank's (which alone scored 89.87%), but
both remain an order of magnitude above coverage.

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
public mass spectral libraries*. Zenodo. <https://doi.org/10.5281/zenodo.22653062>

Machine-readable metadata in [`CITATION.cff`](CITATION.cff). The DOI above is
the concept DOI and always resolves to the latest version; each release also
receives its own version DOI.
