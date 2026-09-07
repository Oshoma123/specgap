# Verification checklist (author completes before any release)

Initial and date each line in your own copy. `scripts` here refers to
`code/`. This checklist assumes you have already replaced the synthetic
fixture with real data — do that first.

## Reproduce
- [ ] Fresh fetch via `code/01_fetch.py --all` on a machine with network access; each source's file logged in `data/raw/PROVENANCE.txt`
- [ ] `data/raw/fixtures/` deleted so `code/02_build.py` reads only real data
- [ ] Full pipeline re-run (`02_build.py` → `03_qa.py` → `04_figures.py --final`); outputs diff clean against any previously committed version
- [ ] Every number in `README.md`, `paper/paper.md`, and `docs/AUDIT_REPORT.md` re-derived from `data/processed/stats.json` after the re-run

## Source-level checks
- [ ] Five structures checked by hand: look each up directly on lotus.naturalproducts.net or coconut.naturalproducts.net and confirm the InChIKey and name match
- [ ] Five spectral entries checked by hand against GNPS/MassBank/MoNA directly
- [ ] Source vintages confirmed current (bulk-download pages checked for a newer release than the one fetched)
- [ ] MassBank's CC BY 4.0 attribution requirement satisfied in README/paper; MoNA per-record licenses spot-checked before inclusion in the headline coverage number

## Row-level spot checks (minimum 15 units)
- [ ] Five natural products you recognize by name, checked against both a structure database and a spectral source
- [ ] Five "unmatched" structures — confirm by manual search that they are genuinely absent from GNPS/MassBank/MoNA, not a join bug
- [ ] Five random spectral entries flagged `name_recoverable=False` — confirm by eye whether the name really doesn't resolve, or whether the normalization rules (docs/CODEBOOK.md) are too strict

## Judgment calls to own
- [ ] Headline coverage number: exact-InChIKey or skeleton-level (docs/BUILD_SPEC.md verify points)
- [ ] Name-fuzzy-match threshold (`NAME_FUZZY_THRESHOLD` in `code/02_build.py`) — re-tune against real name strings before trusting name-recoverability figures
- [ ] MoNA license filtering: include all records, or only records with a clear open license?

## Before it goes public
- [ ] README, limitations, and manuscript text rewritten in your own voice; nothing you cannot defend remains
- [ ] Draft stamps removed by regenerating with `--final`; `code/publish_gate.py`-equivalent check passes (see below)
- [ ] LICENSE, LICENSE-DATA, AUTHORS.json, CITATION.cff all in place and consistent
- [ ] Evidence log row written the day of release
