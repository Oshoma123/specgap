"""MSP (NIST-style) parser, used by MoNA and GNPS's .msp export.

MSP is a loose, widely-varying format: 'Key: value' header lines, then peak
lines, with records separated by blank lines. Different producers spell the
same field differently, which is the main parsing hazard. MoNA in particular
emits both 'InChIKey:' and 'InChIKey=' inside a 'Comments:' blob depending on
the export.

Unlike GNPS's MGF, MSP exports usually DO carry an InChIKey field, which is
why SPECGAP prefers .msp/.json over .mgf for GNPS where both are available.

Synonym lines ('Synon:' in NIST convention) are captured as additional names,
because name-recoverability should not fail merely because a library listed a
compound under its second-most-common name.
"""
from __future__ import annotations

import re
from typing import Iterator, TextIO

from .records import SpectralEntry

_NULLS = {"N/A", "NA", "", "NONE", "NULL"}

# Field aliases seen across MoNA / GNPS / NIST-style exports.
_NAME_KEYS = {"name", "compound_name", "title"}
_SYNONYM_KEYS = {"synon", "synonym", "synonyms"}
_INCHIKEY_KEYS = {"inchikey", "inchi_key", "inchikey_id"}
_SMILES_KEYS = {"smiles", "canonical_smiles"}
_INCHI_KEYS = {"inchi", "inchi_code"}
_IONMODE_KEYS = {"ion_mode", "ionmode", "polarity"}
_ID_KEYS = {"db#", "id", "spectrum_id", "spectrumid", "accession"}
_NPEAKS_KEYS = {"num peaks", "num_peaks", "numpeaks"}

# MoNA embeds key=value pairs inside a free-text Comments field.
_COMMENT_KV = re.compile(r'"?([A-Za-z_ ]+)=([^"]+)"?')


def _clean(value: str) -> str | None:
    value = value.strip().strip('"')
    return None if value.upper() in _NULLS else value


def parse_msp(handle: TextIO, source: str = "MoNA") -> Iterator[SpectralEntry]:
    """Stream SpectralEntry records from an MSP file handle."""
    fields: dict[str, str] = {}
    synonyms: list[str] = []
    n_peaks = 0
    seen_any = False

    def flush():
        nonlocal fields, synonyms, n_peaks, seen_any
        if seen_any and fields:
            entry = _build(fields, synonyms, n_peaks, source)
            fields, synonyms, n_peaks, seen_any = {}, [], 0, False
            return entry
        fields, synonyms, n_peaks, seen_any = {}, [], 0, False
        return None

    for raw in handle:
        line = raw.rstrip("\n").strip()
        if not line:
            entry = flush()
            if entry:
                yield entry
            continue

        if ":" in line:
            key, _, value = line.partition(":")
            k = key.strip().lower()
            if k in _SYNONYM_KEYS:
                cleaned = _clean(value)
                if cleaned:
                    synonyms.append(cleaned)
            else:
                fields[k] = value.strip()
            seen_any = True
            # 'Num Peaks:' marks the end of the header; peaks follow
            continue

        # peak line
        if line and line[0].isdigit():
            n_peaks += 1
            seen_any = True

    entry = flush()
    if entry:
        yield entry


def _from_comments(fields: dict[str, str], wanted: set[str]) -> str | None:
    """Pull a key out of MoNA's embedded 'Comments:' key=value blob."""
    blob = fields.get("comments")
    if not blob:
        return None
    for key, value in _COMMENT_KV.findall(blob):
        if key.strip().lower().replace(" ", "_") in wanted:
            return _clean(value)
    return None


def _pick(fields: dict[str, str], keys: set[str]) -> str | None:
    for k in keys:
        if k in fields:
            cleaned = _clean(fields[k])
            if cleaned:
                return cleaned
    return _from_comments(fields, keys)


def _build(fields, synonyms, n_peaks, source) -> SpectralEntry:
    primary = _pick(fields, _NAME_KEYS)
    names = ([primary] if primary else []) + [s for s in synonyms if s != primary]
    npeaks_field = _pick(fields, _NPEAKS_KEYS)
    try:
        declared_peaks = int(npeaks_field) if npeaks_field else None
    except ValueError:
        declared_peaks = None

    return SpectralEntry(
        spectrum_id=_pick(fields, _ID_KEYS) or f"{source}:unidentified",
        source=source,
        inchikey=_pick(fields, _INCHIKEY_KEYS),
        smiles=_pick(fields, _SMILES_KEYS),
        inchi=_pick(fields, _INCHI_KEYS),
        names=names,
        ion_mode=(lambda m: m.lower() if m else None)(_pick(fields, _IONMODE_KEYS)),
        n_peaks=declared_peaks if declared_peaks is not None else n_peaks,
    )
