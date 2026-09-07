# Source formats and how SPECGAP reads them

Field mappings were taken from each project's own published specification,
verified 2026-09-07. Where a format is ambiguous or varies between exporters,
the decision SPECGAP makes is stated here rather than left implicit in code.

## The headline format-layer finding

**The GNPS MGF export cannot be joined on structure identity at all.**

GNPS's MGF format defines `SMILES`, `INCHI` and `INCHIAUX` fields but **no
`INCHIKEY` field**. Both `SMILES` and `INCHI` are frequently the literal
string `N/A` even for named compounds. Consequently, every GNPS MGF record is
"unjoinable" for InChIKey-based coverage analysis, and any audit that reads
GNPS via MGF and reports the result as *uncovered* structure space is
measuring the export format, not the library's actual content.

Practical consequence for anyone auditing spectral coverage:

| GNPS export | Joinable on InChIKey? | Use for coverage work? |
|---|---|---|
| `.mgf` | No — field does not exist | No |
| `.json` (`ALL_GNPS.json`) | Only if InChIKey present; SMILES/InChI otherwise | Preferred, with conversion |
| `.msp` | Usually yes | Preferred |

SPECGAP reports these records as `unjoinable`, never as `uncovered`. See
`tests/test_e2e.py::test_gnps_mgf_is_wholly_unjoinable`, which pins this
behaviour and will fail if GNPS ever adds the field.

## MGF (GNPS)

Reference: <https://ccms-ucsd.github.io/GNPSDocumentation/downloadlibraries/>

Records run `BEGIN IONS` … `END IONS`; header lines are `KEY=value`; peak
lines are whitespace-separated `mz intensity` pairs with no `=`.

| MGF field | SPECGAP field | Notes |
|---|---|---|
| `SPECTRUMID` | `spectrum_id` | falls back to `TITLE` |
| `NAME` | `names[0]` | carries adduct notation — stripped before matching |
| `SMILES`, `INCHI` | `smiles`, `inchi` | literal `N/A` mapped to `None` |
| `IONMODE` | `ion_mode` | lowercased |
| `LIBRARYQUALITY` | `library_quality` | 1 is best |
| — | `inchikey` | **always None; no such field** |

`NAME` values such as `Bortezomib (Velcade) [M+Na]` and
`Desferrioxamine B M+H` embed the measured adduct. The adduct describes the
ion, not the compound, and never appears in a structure database's name
field, so `identity.strip_adduct` removes both the bracketed and bare
trailing forms before any name comparison.

## GNPS JSON

Reference: <https://ccms-ucsd.github.io/GNPSDocumentation/api/>

Field names are inconsistently cased across the export (`Compound_Name`,
`INCHI`, `spectrum_id` alongside `SpectrumID`), so lookup is
case-insensitive. `Ion_Mode` values carry leading whitespace in GNPS's own
documented example (`" Negative"`) and are stripped. `INCHI` values may be
wrapped in escaped double quotes. Peak count is derived from `peaks_json`.

Both a JSON array and newline-delimited JSON are accepted, since GNPS has
published both shapes. The array form is loaded whole; for the full ~2.9M
spectrum export, prefer the newline-delimited or MSP form.

## MassBank record format 2.6.0

Reference: <https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md>

Records are `TAG: value` or `TAG: SUBTAG value`, continuation lines are
indented, and each record ends with `//`.

Three details materially affect results:

1. **`CH$NAME` is mandatory and iterative.** A record may list several
   synonyms. SPECGAP captures all of them in order and tests every one during
   name-recoverability, because a library listing a compound under its second
   name is not a naming failure.
2. **`CH$LINK: INCHIKEY` is optional.** Records without it are `unjoinable`,
   not `uncovered`. Note the subtag syntax: the InChIKey follows the literal
   word `INCHIKEY` on the same line as other `CH$LINK` entries such as `CAS`
   and `PUBCHEM`, so the subtag must be matched, not the tag.
3. **`CH$COMPOUND_CLASS` starts with `Natural Product` or
   `Non-Natural Product`.** This lets an audit scope MassBank to natural
   products rather than penalising it for its large environmental and
   pharmaceutical content. The check is *anchored* — a naive substring test
   for "Natural Product" also matches "Non-Natural Product", which would
   invert the classification. `tests/test_parsers.py` pins this.

`LICENSE` is per-record (`CC BY`, `CC BY-NC`, `CC0` …), which matters for any
downstream redistribution claim.

## MSP (MoNA, and GNPS's `.msp` export)

MSP is loosely specified and varies by producer. SPECGAP accepts aliases for
each field (`InChIKey` / `inchi_key`, `Ion_mode` / `ionmode` / `polarity`,
`DB#` / `id` / `accession`) and additionally scans MoNA's free-text
`Comments:` blob for embedded `key=value` pairs. `Synon:` lines become
additional names. Blank lines separate records.

## SDF (COCONUT, LOTUS)

The molfile connection table is skipped entirely — SPECGAP needs only the
data fields, so no cheminformatics toolkit is required and parsing stays fast
enough for COCONUT's scale. Data tags (`> <inchikey>`) are matched
case-insensitively against a list of known aliases, since tag names differ
between COCONUT and LOTUS and have changed across releases. Multi-valued
fields are split on `;` and `|`. Records missing an InChIKey are still
emitted, so they can be counted as unjoinable rather than silently dropped.
