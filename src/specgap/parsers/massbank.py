"""MassBank record parser (MassBank Record Format 2.6.0).

Real record structure (abridged, per the official format specification):

    ACCESSION: MSBNK-AAFC-AC000101
    RECORD_TITLE: (-)-Nicotine; ESI-QQ; MS2; CE 40 V; [M+H]+
    DATE: 2011.02.21 (Created 2007.07.07)
    AUTHORS: ...
    LICENSE: CC BY
    CH$NAME: D-Tartaric acid
    CH$NAME: (2S,3S)-Tartaric acid
    CH$COMPOUND_CLASS: Natural Product; Carotenoid; Terpenoid; Lipid
    CH$FORMULA: C9H10ClNO3
    CH$EXACT_MASS: 430.38108
    CH$SMILES: NCC(O)=O
    CH$IUPAC: InChI=1S/C2H5NO2/c3-1-2(4)5/h1,3H2,(H,4,5)
    CH$LINK: INCHIKEY UFFBMTHBGFGIHF-UHFFFAOYSA-N
    AC$MASS_SPECTROMETRY: MS_TYPE MS2
    AC$MASS_SPECTROMETRY: ION_MODE POSITIVE
    PK$NUM_PEAK: 86
    PK$PEAK: m/z int. rel.int.
      326.65 5.3 5
    //

Three details that materially affect SPECGAP's results:

  1. CH$NAME is MANDATORY and ITERATIVE. A record may carry several synonyms.
     Name-recoverability must test the declared name against the structure
     database, but coverage of MassBank's own naming is better measured using
     ALL its names, so every CH$NAME is captured in order.
  2. CH$LINK: INCHIKEY is OPTIONAL. Records without it cannot be joined on
     InChIKey and must be counted as unjoinable rather than as uncovered.
  3. CH$COMPOUND_CLASS begins with either 'Natural Product' or
     'Non-Natural Product'. This lets SPECGAP scope MassBank to the natural
     products actually in LOTUS/COCONUT's universe instead of penalising
     MassBank for its (large) environmental and pharmaceutical content.

Records are separated by a line containing only '//'.
"""
from __future__ import annotations

import os
from typing import Iterator, TextIO

from .records import SpectralEntry


def _split_tag(line: str) -> tuple[str, str] | None:
    """Split 'TAG: value' into (TAG, value). Returns None for continuations."""
    if line.startswith(" ") or ":" not in line:
        return None
    tag, _, value = line.partition(":")
    return tag.strip(), value.strip()


def parse_massbank_record(text: str) -> SpectralEntry | None:
    """Parse one MassBank record (the text between record boundaries)."""
    accession = None
    names: list[str] = []
    inchikey = smiles = inchi = None
    ion_mode = ms_type = compound_class = license_ = None

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.strip() == "//":
            break
        parsed = _split_tag(line)
        if not parsed:
            continue
        tag, value = parsed

        if tag == "ACCESSION":
            accession = value
        elif tag == "CH$NAME":
            if value:
                names.append(value)
        elif tag == "CH$SMILES":
            smiles = value or None
        elif tag == "CH$IUPAC":
            inchi = value or None
        elif tag == "CH$COMPOUND_CLASS":
            compound_class = value or None
        elif tag == "LICENSE":
            license_ = value or None
        elif tag == "CH$LINK":
            # subtag syntax: 'CH$LINK: INCHIKEY UFFBMTHBGFGIHF-UHFFFAOYSA-N'
            subtag, _, rest = value.partition(" ")
            if subtag.upper() == "INCHIKEY" and rest.strip():
                inchikey = rest.strip()
        elif tag == "AC$MASS_SPECTROMETRY":
            subtag, _, rest = value.partition(" ")
            sub = subtag.upper()
            if sub == "ION_MODE":
                ion_mode = rest.strip().lower() or None
            elif sub == "MS_TYPE":
                ms_type = rest.strip() or None

    if accession is None:
        return None

    return SpectralEntry(
        spectrum_id=accession,
        source="MassBank",
        inchikey=inchikey,
        smiles=smiles,
        inchi=inchi,
        names=names,
        ion_mode=ion_mode,
        ms_level=ms_type,
        compound_class=compound_class,
        license=license_,
    )


def parse_massbank_stream(handle: TextIO) -> Iterator[SpectralEntry]:
    """Parse a concatenated stream of MassBank records separated by '//'."""
    buffer: list[str] = []
    for raw in handle:
        if raw.strip() == "//":
            entry = parse_massbank_record("\n".join(buffer))
            if entry:
                yield entry
            buffer = []
        else:
            buffer.append(raw.rstrip("\n"))
    if buffer:
        entry = parse_massbank_record("\n".join(buffer))
        if entry:
            yield entry


def parse_massbank_dir(root: str) -> Iterator[SpectralEntry]:
    """Walk a MassBank-data checkout, parsing every .txt record file.

    MassBank-data stores one record per .txt file under per-contributor
    directories, so this is the shape the GitHub/Zenodo release arrives in.
    """
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.endswith(".txt"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    entry = parse_massbank_record(fh.read())
            except OSError:
                continue
            if entry:
                yield entry


def is_natural_product(entry: SpectralEntry) -> bool:
    """True if MassBank classes this record as a natural product.

    Per the format spec, CH$COMPOUND_CLASS must begin with either
    'Natural Product' or 'Non-Natural Product' — so the check must be
    anchored, otherwise 'Non-Natural Product' matches a naive substring test.
    """
    if not entry.compound_class:
        return False
    return entry.compound_class.strip().lower().startswith("natural product")
