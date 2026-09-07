# Limitations

Numbered so they can be cited individually.

1. **No full-corpus run has been performed.** The engine is tested, but every
   number currently in `data/processed/` comes from the small bundled
   fixtures. Fixtures reproduce *real field layouts* from the sources' own
   documentation, which validates parsing — they do not measure real
   coverage. Do not quote a coverage percentage from this repository until
   `scripts/01_fetch.py` has been run against the live bulk downloads.

2. **GNPS MGF records cannot be joined on structure identity.** The format
   has no InChIKey field (see `FORMATS.md`). Auditing GNPS requires the JSON
   or MSP export, or a SMILES/InChI-to-InChIKey conversion step that SPECGAP
   deliberately does not perform, because doing it without a cheminformatics
   toolkit would silently introduce structure-normalization errors. Until
   that step exists, GNPS coverage is under-measured relative to MassBank and
   MoNA, and the two are not directly comparable.

3. **Skeleton-level matching ignores stereochemistry.** Treating two
   structures as matched when only the 14-character InChIKey skeleton agrees
   discards stereochemistry, isotopic labelling and protonation state. It
   will report higher coverage than exact matching. Both are computed; which
   is the headline number is an author decision, not a default.

4. **The fuzzy name threshold is untuned.** `0.92` was chosen a priori, not
   fitted to real name strings. A single-character substitution in a short
   name scores below it and will not match (pinned in
   `tests/test_identity.py`). Real library name fields are messier than the
   fixtures: abbreviations, alternate salt forms, non-English variants and
   typos are all common. Re-tune before trusting name-recoverability figures.

5. **Coverage is computed without regard to spectral quality.** A structure
   counts as covered if any matching spectrum exists, including a single
   low-quality one. GNPS `LIBRARYQUALITY` and MassBank record status are
   parsed and available but not yet used to weight results.

6. **MoNA licences vary per record and are not yet filtered.** Any headline
   number including MoNA must state whether licence-restricted records were
   counted. COCONUT similarly aggregates sources with differing terms even
   though the curated dataset is CC0, so a downstream user needing full
   commercial reuse should filter by originating collection.

7. **Name-recoverability only assesses answerable cases.** Spectra lacking an
   InChIKey, lacking a name, or whose structure is absent from the reference
   set are reported in their own categories, not as failures. This is more
   honest but makes the denominator smaller than the raw record count — the
   stats always state which denominator was used.

8. **Scope is natural products only.** MassBank's `CH$COMPOUND_CLASS` allows
   scoping to natural products; GNPS and MoNA have no equivalent field, so
   their non-natural-product content is not excluded and will depress
   apparent name-recoverability against an NP-only reference set.

9. **No independent verification of upstream assertions.** Where COCONUT
   states that a compound appears in GNPS's collection, SPECGAP does not
   currently check that claim against GNPS itself. The `data/real_pilot/`
   records rely on such self-reported cross-references and are labelled
   accordingly.
