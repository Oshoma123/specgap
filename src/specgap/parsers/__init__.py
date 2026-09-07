"""Parsers for the real file formats the source libraries actually publish.

Each parser yields `SpectralEntry` or `StructureEntry` records with a uniform
shape, so `specgap.coverage` never needs to know which library a record came
from. Parsers are streaming (generators) because the real files are large:
the GNPS full export is ~2.9M spectra and MoNA ~3.6M records, which must not
be held in memory at once.

Format references (verified against official documentation, 2026-09):
  MGF / GNPS   https://ccms-ucsd.github.io/GNPSDocumentation/downloadlibraries/
  GNPS JSON    https://ccms-ucsd.github.io/GNPSDocumentation/api/
  MassBank     https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md
  SDF          MDL/CTfile spec; COCONUT and LOTUS both publish SDF exports
See docs/FORMATS.md for the field-level mapping decisions.
"""
from .records import SpectralEntry, StructureEntry
from .mgf import parse_mgf
from .msp import parse_msp
from .gnps_json import parse_gnps_json
from .massbank import parse_massbank_record, parse_massbank_dir, parse_massbank_stream, is_natural_product
from .sdf import parse_sdf

__all__ = [
    "SpectralEntry",
    "StructureEntry",
    "parse_mgf",
    "parse_msp",
    "parse_gnps_json",
    "parse_massbank_record",
    "parse_massbank_dir",
    "parse_massbank_stream",
    "is_natural_product",
    "parse_sdf",
]
