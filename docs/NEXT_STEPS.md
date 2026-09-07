# Next steps

## v0.2 (first real-data release)
- Run `code/01_fetch.py` against live LOTUS, COCONUT, GNPS, MassBank, MoNA bulk downloads.
- Re-tune `NAME_FUZZY_THRESHOLD` against real declared_name strings.
- Add per-record MoNA license parsing and an "open-license-only" coverage variant.
- Weight matches by GNPS `LIBRARYQUALITY` and MassBank record-validation status.

## v0.3
- Break coverage down by chemical class/superclass (NPClassifier or ClassyFire annotations from COCONUT).
- Track coverage over time using LOTUS/COCONUT/GNPS versioned releases, to report a coverage *trend*, not just a snapshot.
- Publish the audit as a living, periodically-refreshed dataset (archetype 5) on top of the current one-shot dataset (archetype 1).

## Longer term
- JOSS submission for the matching engine once it has a test suite and has been used on a full real run.
- A short methods paper (ChemRxiv) once the headline numbers are real and the verify-point decisions above are settled.
