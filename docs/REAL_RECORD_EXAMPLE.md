# A real, verified COCONUT record

Unlike everything under `data/raw/fixtures/`, this one record is real,
fetched live from the COCONUT API on 2026-09-01. It exists to (a) confirm
the API endpoint pattern `01_fetch.py` should use and (b) give the repo one
genuine, citable worked example instead of only synthetic data.

**Endpoint confirmed live:** `https://coconut.naturalproducts.net/api/schemas/bioschemas/<CNP_ID>`
(Bioschemas/JSON-LD format; one record per request — useful for spot-checks
and single-compound lookups, not bulk export. Bulk export is still the CSV/
SDF/Postgres-dump route documented in `01_fetch.py`.)

## Record: CNP0606256.0

| Field | Value |
|---|---|
| Name | 4-Cyclohexylbutanamide |
| InChIKey | `HZGJWEZZXLGUAU-UHFFFAOYSA-N` |
| SMILES | `NC(=O)CCCC1CCCCC1` |
| Molecular formula | C10H19NO |
| Chemical class | Fatty Acyls / Fatty amides / Lipids and lipid-like molecules |
| Source organism | *Crassocephalum crepidioides* |
| Source collection | "Australian natural products" (Phytochemistry of Australian Plants) |
| Citation | Owokotomo et al., "Analysis of the Essential Oils of Leaves and Stems of *Crassocephalum crepidioides* Growing in South Western Nigeria," doi:[10.5539/ijc.v4n2p34](https://doi.org/10.5539/ijc.v4n2p34) |
| License | CC BY 4.0 (per record) |
| Live URL | <https://coconut.naturalproducts.net/compound/CNP0606256.0> |

This single record does not constitute a coverage audit (n=1 proves
nothing about coverage) — it is a fetch-integration check only. `tests/`
uses this record's InChIKey and name as a real-data smoke test alongside
the synthetic fixture tests.
