"""CSV structure parser, for LOTUS frozen metadata exports.

LOTUS's maintained distribution is a Zenodo-deposited CSV of Wikidata-derived
structure-organism pairs (the `lotus.naturalproducts.net` SDF site is
explicitly unmaintained and being phased out, so the CSV is the correct
source despite requiring a different parser).

The frozen metadata table carries one row per (structure, organism,
reference) triple, enriched with InChI, SMILES, molecular formula,
NPClassifier and ClassyFire classifications, and Open Tree of Life taxonomy.

Two consequences for SPECGAP:

  1. **Rows are not compounds.** A structure found in fifty organisms appears
     in fifty rows. Emitting one StructureEntry per row would count that
     compound fifty times and distort every coverage denominator. This parser
     therefore aggregates by InChIKey, merging names and organisms, and emits
     one entry per distinct structure. That requires holding a dict of
     structures in memory, which is acceptable: LOTUS is ~250k compounds.

  2. **Column names vary between releases.** Lookup is case-insensitive over
     an alias list, and a header scan reports what was actually matched so a
     silent all-None parse is impossible to miss.

Gzipped input is handled transparently, since the Zenodo files ship as .gz.
"""
from __future__ import annotations

import csv
import gzip
import io
import os
from typing import Iterator

from .records import StructureEntry

_NULLS = {"", "NA", "N/A", "NONE", "NULL", "NAN"}

_INCHIKEY_COLS = ("structure_inchikey", "inchikey", "inchi_key",
                  "structure_inchikey_2d", "standard_inchikey")
_INCHI_COLS = ("structure_inchi", "inchi", "standard_inchi")
_SMILES_COLS = ("structure_smiles", "smiles", "structure_smiles_2d",
                "canonical_smiles")
_NAME_COLS = ("structure_nameTraditional", "structure_nametraditional",
              "structure_name", "traditional_name", "name",
              "structure_nameIupac", "structure_nameiupac", "iupac_name")
_ORGANISM_COLS = ("organism_name", "organism_taxonomy_09species",
                  "organism_taxonomy_08genus", "organism", "taxon_name")
_ID_COLS = ("structure_wikidata", "wikidata_id", "structure_id", "lotus_id")


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip()
    return None if v.upper() in _NULLS else v


def _resolve(fieldnames, aliases):
    """Return the first present column name, matched case-insensitively."""
    lowered = {f.lower().strip(): f for f in (fieldnames or [])}
    for alias in aliases:
        if alias.lower() in lowered:
            return lowered[alias.lower()]
    return None


def _open(path: str):
    if path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8",
                                errors="replace")
    return open(path, encoding="utf-8", errors="replace")


def parse_lotus_csv(path: str, source: str = "LOTUS",
                    verbose: bool = True) -> Iterator[StructureEntry]:
    """Yield one StructureEntry per distinct InChIKey in a LOTUS CSV export."""
    with _open(path) as fh:
        reader = csv.DictReader(fh)
        cols = {
            "inchikey": _resolve(reader.fieldnames, _INCHIKEY_COLS),
            "inchi": _resolve(reader.fieldnames, _INCHI_COLS),
            "smiles": _resolve(reader.fieldnames, _SMILES_COLS),
            "name": _resolve(reader.fieldnames, _NAME_COLS),
            "organism": _resolve(reader.fieldnames, _ORGANISM_COLS),
            "id": _resolve(reader.fieldnames, _ID_COLS),
        }
        if verbose:
            print("  LOTUS column mapping:", flush=True)
            for want, got in cols.items():
                print(f"    {want:<9} -> {got or '(not found)'}", flush=True)
        if not cols["inchikey"]:
            raise SystemExit(
                "no InChIKey column found in " + os.path.basename(path)
                + "; columns present: " + ", ".join(reader.fieldnames or []))

        merged: dict[str, StructureEntry] = {}
        for row in reader:
            key = _clean(row.get(cols["inchikey"]))
            if not key:
                continue
            key = key.upper()
            entry = merged.get(key)
            if entry is None:
                entry = StructureEntry(
                    structure_id=_clean(row.get(cols["id"])) if cols["id"] else key,
                    source=source,
                    inchikey=key,
                    smiles=_clean(row.get(cols["smiles"])) if cols["smiles"] else None,
                    inchi=_clean(row.get(cols["inchi"])) if cols["inchi"] else None,
                )
                merged[key] = entry
            if cols["name"]:
                name = _clean(row.get(cols["name"]))
                if name and name not in entry.names:
                    entry.names.append(name)
            if cols["organism"]:
                org = _clean(row.get(cols["organism"]))
                if org and org not in entry.organisms:
                    entry.organisms.append(org)

    if verbose:
        print(f"  LOTUS: {len(merged):,} distinct structures", flush=True)
    for entry in merged.values():
        yield entry
