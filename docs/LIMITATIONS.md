# Limitations

1. **No real data has been run yet.** Everything currently in
   `data/processed/`, `paper/figures/`, and the manuscript drafts comes from
   a synthetic fixture built to test the pipeline's shape and logic, not
   from LOTUS/COCONUT/GNPS/MassBank/MoNA. This is the single most important
   limitation and it is not a caveat to bury — no number here should be
   cited until `code/01_fetch.py` has been run against live data and the
   fixture files have been deleted.

2. **InChIKey-skeleton matching is a real methodological choice, not a
   formality.** Treating two structures as "matched" when only the first 14
   characters of their InChIKeys agree ignores stereochemistry, isotope
   labeling, and protonation state. This inflates apparent coverage relative
   to exact-InChIKey matching. Both are reported; which one is the
   headline number is a verify point for the author (`docs/BUILD_SPEC.md`).

3. **Name-recoverability depends heavily on the normalization and
   fuzzy-matching rules**, which are currently simple (salt/hydrate
   stripping, a fixed Levenshtein threshold). Real spectral-library name
   fields are messier than this: abbreviations, alternate salt forms,
   language variants, and outright typos are common. The threshold
   (`NAME_FUZZY_THRESHOLD = 0.92`) was chosen for the fixture, not tuned
   against real data, and should be re-evaluated once real MoNA/GNPS/MassBank
   name strings are in hand. Concretely: a single-character substitution in
   a short name (e.g. an 8-letter word) scores below 0.92 and is *not*
   recovered — `tests/test_build.py::test_name_recoverable_single_char_substitution_not_caught`
   documents this as a known blind spot, confirmed by the test suite rather
   than just asserted here.

4. **License heterogeneity within MoNA is not yet handled per-record.**
   MoNA aggregates records with mixed licensing; this build's `01_fetch.py`
   flags this as something to check but does not yet parse and filter by
   per-record license. Any headline coverage number that includes MoNA
   should state whether license-restricted MoNA records were included.

5. **COCONUT itself aggregates sources with mixed licenses** (e.g., NPAtlas,
   KNApSAcK carry more restrictive terms even though the curated COCONUT
   dataset is CC0). A downstream user filtering for full commercial
   reuse should filter COCONUT by originating source, not assume CC0
   propagates to every record.

6. **Coverage and name-recoverability are computed independently of spectral
   quality.** A "matched" structure may have only a single low-quality or
   in-silico-predicted spectrum; this pipeline does not currently weight
   matches by spectral library quality flags (e.g., GNPS `LIBRARYQUALITY`).

7. **Small-molecule scope only.** LOTUS and COCONUT are natural-product
   structure databases; SPECGAP does not attempt to characterize coverage
   gaps for non-natural-product chemical space.
