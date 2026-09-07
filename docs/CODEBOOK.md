# Codebook

## Input tables (`data/raw/**/`)

### `lotus_coconut_structures.csv`
One row per structure-database entry (LOTUS or COCONUT contribute separate
rows even for the same compound; deduplication happens implicitly via
InChIKey grouping in `code/02_build.py`).

| Column | Type | Definition |
|---|---|---|
| `inchikey` | string | Full 27-character InChIKey of the structure. |
| `inchikey_skeleton` | string | First block of the InChIKey (14 chars), ignoring stereochemistry/isotope/protonation layers. |
| `name` | string | A preferred or common name for the structure, as recorded by the source database. |
| `source_db` | string | `LOTUS` or `COCONUT`. |

### `spectral_entries.csv`
One row per spectral-library record.

| Column | Type | Definition |
|---|---|---|
| `spectrum_id` | string | Source-native spectrum identifier. |
| `inchikey` | string | InChIKey the spectral library associates with this spectrum. |
| `declared_name` | string | Compound name as recorded by the spectral library (unnormalized). |
| `spectral_source` | string | `GNPS`, `MassBank`, or `MoNA`. |
| `ionization_mode` | string | `positive` or `negative`. |

## Output tables (`data/processed/`)

### `coverage_audit.csv`
| Column | Definition |
|---|---|
| `matched_exact_inchikey` | `True` if any spectral entry shares this exact 27-char InChIKey. |
| `matched_skeleton` | `True` if any spectral entry shares this InChIKey's 14-char skeleton (looser — ignores stereochemistry). |
| `matching_spectral_sources` | `;`-joined list of spectral sources with an exact-InChIKey match. |

### `name_recoverability.csv`
| Column | Definition |
|---|---|
| `name_recoverable` | `True` if `declared_name`, after normalization, exact- or fuzzy-matches (Levenshtein ratio ≥ 0.92, see `code/02_build.py:NAME_FUZZY_THRESHOLD`) any name recorded for the same InChIKey in the structure tables. |
| `match_method` | `exact`, `fuzzy:<ratio>`, or `none`. |

## Name normalization (`code/02_build.py:normalize_name`)
Lowercased; common salt/hydrate suffixes (`hydrate`, `hydrochloride`, `hcl`,
`sodium`, `potassium`, `salt`) stripped as whole words; punctuation collapsed
to single spaces. This is a deliberately simple rule set — see
`docs/LIMITATIONS.md` and the verify points in `docs/BUILD_SPEC.md`.
