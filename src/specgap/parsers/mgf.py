"""MGF parser for GNPS reference spectral libraries.

Real GNPS MGF block (from GNPS documentation):

    BEGIN IONS
    PEPMASS=407.186
    CHARGE=1
    MSLEVEL=2
    SOURCE_INSTRUMENT=LC-ESI-qTof
    FILENAME=Plate1_1_20_GG1_01_16488.mzXML
    SEQ=*..*
    IONMODE=Positive
    ORGANISM=GNPS-SELLECKCHEM-FDA-PART2
    NAME=Bortezomib (Velcade) [M+Na]
    PI=Dorrestein
    DATACOLLECTOR=Garg_Neha
    SMILES=C1=CN=CC(=N1)C(N[C@H](...)=O
    INCHI=N/A
    INCHIAUX=N/A
    PUBMED=N/A
    SUBMITUSER=negarg
    LIBRARYQUALITY=1
    SPECTRUMID=CCMSLIB00000077995
    SCANS=1211
    95.886879 236.0
    ...
    END IONS

Notes that matter for parsing correctness:
  - GNPS MGF has NO INCHIKEY field. Only SMILES and INCHI, and both are
    frequently the literal string 'N/A'. SPECGAP therefore cannot key GNPS
    MGF records on InChIKey without an external structure conversion step
    (see docs/LIMITATIONS.md). The JSON export is preferable where possible.
  - NAME carries adduct notation ('[M+Na]', 'M+H') that must be stripped
    before name matching; specgap.identity.strip_adduct does this.
  - Peak lines are 'mz intensity' pairs with no key; anything without '=' and
    after the header block is a peak.
"""
from __future__ import annotations

from typing import Iterator, TextIO

from .records import SpectralEntry

_NULLS = {"N/A", "NA", "", "NONE", "NULL"}


def _clean(value: str) -> str | None:
    value = value.strip()
    return None if value.upper() in _NULLS else value


def parse_mgf(handle: TextIO, source: str = "GNPS") -> Iterator[SpectralEntry]:
    """Stream SpectralEntry records from an MGF file handle."""
    fields: dict[str, str] = {}
    n_peaks = 0
    in_block = False

    for raw in handle:
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()

        if upper == "BEGIN IONS":
            fields, n_peaks, in_block = {}, 0, True
            continue

        if upper == "END IONS":
            if in_block:
                yield _build(fields, n_peaks, source)
            fields, n_peaks, in_block = {}, 0, False
            continue

        if not in_block:
            continue

        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip().upper()] = value.strip()
        else:
            # peak line: 'mz intensity'
            n_peaks += 1


def _build(fields: dict[str, str], n_peaks: int, source: str) -> SpectralEntry:
    name = _clean(fields.get("NAME", ""))
    return SpectralEntry(
        spectrum_id=(
            _clean(fields.get("SPECTRUMID", ""))
            or _clean(fields.get("TITLE", ""))
            or f"{source}:unidentified"
        ),
        source=source,
        inchikey=None,          # not present in GNPS MGF; see module docstring
        smiles=_clean(fields.get("SMILES", "")),
        inchi=_clean(fields.get("INCHI", "")),
        names=[name] if name else [],
        ion_mode=(fields.get("IONMODE", "").strip().lower() or None),
        ms_level=_clean(fields.get("MSLEVEL", "")),
        library_quality=_clean(fields.get("LIBRARYQUALITY", "")),
        n_peaks=n_peaks,
    )
