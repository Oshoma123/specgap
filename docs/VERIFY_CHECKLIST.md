# Verification checklist

Complete before any release that reports real coverage numbers.

## Before the run
- [ ] `pytest tests/ -v` passes on your machine (66 tests)
- [ ] `scripts/01_fetch.py --list` endpoints all still resolve
- [ ] Downloaded the GNPS **JSON or MSP** export, not the MGF (see docs/FORMATS.md)
- [ ] Every download logged in `data/raw/PROVENANCE.txt` with SHA-256

## After the run
- [ ] `qa_report.txt` sanity checks all PASS
- [ ] `unjoinable` counts per source are plausible, not silently huge
- [ ] Five covered structures checked by hand on GNPS/MassBank/MoNA directly
- [ ] Five `uncovered` structures manually searched to confirm genuine absence
- [ ] Five `unrecoverable` names eyeballed — too-strict normalization, or real?
- [ ] Denominators in any quoted number stated explicitly

## Judgment calls to own
- [ ] Headline coverage: exact-InChIKey or skeleton
- [ ] Fuzzy threshold, re-tuned against real name strings
- [ ] MoNA licence filtering: in or out of the headline number
- [ ] Whether to add SMILES-to-InChIKey conversion for GNPS, and with what toolkit

## Before publishing
- [ ] README status section rewritten to describe the real run
- [ ] LIMITATIONS.md item 1 updated or removed as appropriate
- [ ] CITATION.cff version and date bumped
- [ ] Zenodo DOI minted and recorded in README and CITATION.cff
