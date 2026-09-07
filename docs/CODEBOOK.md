# Codebook

## `coverage_audit.csv` — one row per structure-database entry

| Column | Definition |
|---|---|
| `structure_id` | Source-native identifier (e.g. `CNP0138595.0`). |
| `source_db` | `LOTUS` or `COCONUT`. |
| `inchikey` | Full 27-character InChIKey, uppercased; empty if absent. |
| `joinable` | `True` if the InChIKey is well-formed and usable for matching. |
| `matched_exact` | `True` if a spectrum shares this exact InChIKey. |
| `matched_skeleton` | `True` if a spectrum shares the 14-char skeleton (ignores stereochemistry). |
| `matching_sources` | `;`-joined spectral sources with an exact-key match. |
| `status` | `covered_exact` / `covered_skeleton_only` / `uncovered` / `unjoinable`. |

`unjoinable` is **not** a subset of `uncovered`. A structure with no InChIKey
cannot be assessed; counting it as uncovered would inflate the coverage gap.

## `name_recoverability.csv` — one row per spectral-library entry

| Column | Definition |
|---|---|
| `spectrum_id` | Source-native identifier (e.g. `MSBNK-AAFC-AC000101`). |
| `spectral_source` | `GNPS`, `MassBank`, or `MoNA`. |
| `declared_name` | Primary compound name as the library recorded it. |
| `inchikey` | InChIKey the library associates with the spectrum. |
| `joinable` | `True` if that InChIKey is well-formed. |
| `has_declared_name` | `False` for empty or placeholder names (`N/A` etc.). |
| `structure_known` | `True` if the InChIKey appears in the structure reference set. |
| `recoverable` | `True` if any of the library's names for this spectrum matches a name recorded for the same structure. |
| `method` | `exact`, `fuzzy:<ratio>`, `none`, or `not_assessed`. |
| `status` | `recoverable` / `unrecoverable` / `structure_not_in_reference_set` / `unjoinable_no_inchikey` / `unjoinable_no_name`. |

## Name normalization (`specgap.identity.normalize_name`)

Applied in order: strip trailing adduct notation (`[M+Na]`, `M+H`);
lowercase; remove whole-word salt and hydrate terms (hydrate, hydrochloride,
sodium, sulfate, …); collapse non-alphanumerics to single spaces. Placeholder
strings (`N/A`, `NONE`, `UNKNOWN`, `-`) normalize to the empty string and
never match anything.

## `stats.json`

Nested under `spectral_index`, `structural_coverage`, `name_recoverability`.
Each block carries a `denominator_note` stating exactly which population its
percentages are computed over, plus `status_counts` giving the full breakdown.
