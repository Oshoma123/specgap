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
  - Unlike the MGF export, GNPS JSON DOES carry InChIKeys, as
    'InChIKey_smiles' and 'InChIKey_inchi' (hashes GNPS computes from the
    deposited SMILES and InChI). This is why SPECGAP can audit GNPS via JSON
    but not via MGF.
  - 'library_membership' values containing GNPS_PROPOGATED mark
    computationally propagated spectra, not measurements. Filter them out
    before reporting coverage.

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
        # GNPS derives InChIKeys from the deposited structure and exposes
        # both: InChIKey_smiles (hashed from SMILES) and InChIKey_inchi
        # (hashed from InChI). They usually agree; where they disagree the
        # deposited SMILES and InChI disagree, which is a data-quality
        # signal in itself. Preference order is explicit rather than
        # incidental: a plain InChIKey field if present, then the
        # SMILES-derived key, then the InChI-derived one.
        inchikey=_get(record, "InChIKey", "inchikey", "InChIKey_smiles",
                      "InChIKey_inchi"),
        smiles=_get(record, "Smiles", "SMILES"),
        inchi=_get(record, "INCHI", "InChI"),
        names=[name] if name else [],
        ion_mode=(lambda m: m.lower() if m else None)(_get(record, "Ion_Mode", "ionmode")),
        ms_level=_get(record, "ms_level", "MSLEVEL"),
        library_quality=_get(record, "Library_Class", "LIBRARYQUALITY"),
        # library_membership names the contributing library. Values containing
        # GNPS_PROPOGATED mark spectra propagated COMPUTATIONALLY from
        # reference spectra rather than measured — the GNPS analogue of MoNA's
        # in-silico set. They must not be counted as reference coverage.
        compound_class=_get(record, "library_membership"),
        n_peaks=_count_peaks(record),
    )


def _iter_json_objects(handle: TextIO, chunk_size: int = 1 << 20):
    """Yield top-level JSON objects from an array, without loading the file.

    ALL_GNPS_NO_PROPOGATED.json is a *pretty-printed* array of ~4.7 GB: each
    record spans many lines, so neither json.load() (which would need tens of
    GB of memory) nor a line-by-line reader (each line is a fragment) works.

    This scans for balanced braces at depth 1, tracking string literals and
    backslash escapes so that braces inside values -- SMILES, InChI strings,
    free-text names -- do not corrupt the depth count.
    """
    depth = 0
    in_string = False
    escaped = False
    buf = []
    while True:
        chunk = handle.read(chunk_size)
        if not chunk:
            break
        for ch in chunk:
            if depth > 0:
                buf.append(ch)
            if escaped:
                escaped = False
                continue
            if ch == "\\" and in_string:
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                if depth == 0:
                    buf = ["{"]
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    text = "".join(buf)
                    buf = []
                    try:
                        obj = json.loads(text)
                    except ValueError:
                        continue
                    if isinstance(obj, dict):
                        yield obj


def parse_gnps_json(handle: TextIO) -> Iterator[SpectralEntry]:
    """Stream entries from a GNPS JSON export.

    Handles the pretty-printed array form (the shape GNPS actually ships) and
    newline-delimited JSON, without ever holding the whole file in memory.
    """
    for record in _iter_json_objects(handle):
        yield record_to_entry(record)
