"""GNPS JSON export parser (ALL_GNPS.json).

Real record shape, per GNPS API documentation:

    {
      "spectrum_id": "CCMSLIB00000579358",
      "source_file": "Training_001.mgf",
      "scan": "1",
      "ms_level": "2",
      "library_membership": "CASMI",
      "spectrum_status": "1",
      "peaks_json": "[[164.033997,32294.5],[179.057495,129907.1]]",
      "splash": "null-null-null-null",
      "Compound_Name": "Theophyllin",
      "Ion_Source": "LC-ESI",
      "Compound_Source": "Commercial",
      "Instrument": "Orbitrap",
      "Adduct": "M-H",
      "Precursor_MZ": "179.057",
      "Smiles": "CN1C2=C(NC=N2)C(=O)N(C)C1=O",
      "INCHI": "\"InChI=1S/C7H8N4O2/...\"",
      "INCHI_AUX": "N/A",
      "Library_Class": "1",
      "SpectrumID": "CCMSLIB00000579358",
      "Ion_Mode": " Negative",
      ...
    }

Parsing hazards handled here:
  - Field names are inconsistently cased ('Compound_Name', 'INCHI',
    'spectrum_id' vs 'SpectrumID'), so lookup is case-insensitive.
  - 'Ion_Mode' values carry leading whitespace (' Negative' in GNPS's own
    documented example), so values are stripped before use.
  - INCHI values are sometimes wrapped in escaped double quotes.
  - Like the MGF export, GNPS JSON carries no InChIKey field; SMILES/InChI
    are present instead. See docs/LIMITATIONS.md.

The top level may be a JSON array or newline-delimited JSON; both are handled
because GNPS has published both shapes.
"""
from __future__ import annotations

import json
from typing import Any, Iterator, TextIO

from .records import SpectralEntry

_NULLS = {"N/A", "NA", "", "NONE", "NULL"}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().strip('"').strip()
    return None if text.upper() in _NULLS else text


def _get(record: dict, *keys: str) -> str | None:
    lowered = {k.lower(): v for k, v in record.items()}
    for key in keys:
        if key.lower() in lowered:
            cleaned = _clean(lowered[key.lower()])
            if cleaned:
                return cleaned
    return None


def _count_peaks(record: dict) -> int | None:
    blob = record.get("peaks_json")
    if not blob:
        return None
    try:
        return len(json.loads(blob) if isinstance(blob, str) else blob)
    except (ValueError, TypeError):
        return None


def record_to_entry(record: dict) -> SpectralEntry:
    name = _get(record, "Compound_Name", "compound_name", "name")
    return SpectralEntry(
        spectrum_id=_get(record, "spectrum_id", "SpectrumID") or "GNPS:unidentified",
        source="GNPS",
        inchikey=_get(record, "InChIKey", "InChIKey_smiles", "inchikey"),
        smiles=_get(record, "Smiles", "SMILES"),
        inchi=_get(record, "INCHI", "InChI"),
        names=[name] if name else [],
        ion_mode=(lambda m: m.lower() if m else None)(_get(record, "Ion_Mode", "ionmode")),
        ms_level=_get(record, "ms_level", "MSLEVEL"),
        library_quality=_get(record, "Library_Class", "LIBRARYQUALITY"),
        n_peaks=_count_peaks(record),
    )


def parse_gnps_json(handle: TextIO) -> Iterator[SpectralEntry]:
    """Stream entries from a GNPS JSON export (array or newline-delimited)."""
    first = handle.read(1)
    while first and first.isspace():
        first = handle.read(1)
    if not first:
        return
    handle.seek(0)

    if first == "[":
        # Whole-array form. This does load the file into memory; for the full
        # 2.9M-spectrum export prefer the newline-delimited or MSP form.
        for record in json.load(handle):
            if isinstance(record, dict):
                yield record_to_entry(record)
    else:
        for line in handle:
            line = line.strip().rstrip(",")
            if not line or line in "[]":
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                yield record_to_entry(record)
