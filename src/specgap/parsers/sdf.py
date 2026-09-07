"""SDF (MDL SDfile) parser for COCONUT and LOTUS structure exports.

An SDF record is a molfile block followed by data fields, then '$$$$':

    <molfile connection table lines>
    M  END
    > <identifier>
    CNP0138595.0

    > <inchikey>
    NETSQGRTUNRXEO-UHFFFAOYSA-N

    > <name>
    Dehydrocostus lactone

    > <synonyms>
    Epiligulyl oxide
    Dehydro-alpha-curcumene

    $$$$

SPECGAP only needs the data fields, not the connection table, so the molfile
block is skipped rather than parsed — this keeps the parser dependency-free
(no RDKit) and fast enough for COCONUT's ~700k records.

Field naming differs between COCONUT and LOTUS exports and has changed across
releases, so tag lookup is case-insensitive and alias-tolerant. If a needed
field is missing entirely the record is still emitted, with None, so it can be
counted as unjoinable rather than silently dropped.
"""
from __future__ import annotations

import re
from typing import Iterator, TextIO

from .records import StructureEntry

_TAG_RE = re.compile(r"^>\s*<([^>]+)>")
_NULLS = {"N/A", "NA", "", "NONE", "NULL"}

_ID_TAGS = ("identifier", "coconut_id", "coconut-id", "lotus_id",
            "wikidata_id", "id", "database_id")
_INCHIKEY_TAGS = ("inchikey", "inchi_key", "standard_inchi_key", "inchikey3d")
_SMILES_TAGS = ("smiles", "canonical_smiles", "absolute_smiles", "isomeric_smiles")
_INCHI_TAGS = ("inchi", "standard_inchi")
_NAME_TAGS = ("name", "preferred_name", "traditional_name", "iupac_name",
              "molecule_name")
_SYNONYM_TAGS = ("synonyms", "synonym", "alternate_names", "all_names")
_ORGANISM_TAGS = ("organisms", "taxonomy", "found_in_organisms",
                  "organism", "taxonomicrange")


def _clean(value: str) -> str | None:
    value = value.strip()
    return None if value.upper() in _NULLS else value


def _lookup(data: dict[str, list[str]], tags: tuple[str, ...]) -> str | None:
    for tag in tags:
        if tag in data and data[tag]:
            cleaned = _clean(data[tag][0])
            if cleaned:
                return cleaned
    return None


def _lookup_multi(data: dict[str, list[str]], tags: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for tag in tags:
        for line in data.get(tag, []):
            # multi-valued fields are variously newline-, semicolon- or
            # pipe-separated depending on the exporter
            for part in re.split(r"[;|]", line):
                cleaned = _clean(part)
                if cleaned and cleaned not in out:
                    out.append(cleaned)
    return out


def parse_sdf(handle: TextIO, source: str = "COCONUT") -> Iterator[StructureEntry]:
    """Stream StructureEntry records from an SDF file handle."""
    data: dict[str, list[str]] = {}
    current_tag: str | None = None

    for raw in handle:
        line = raw.rstrip("\n")

        if line.strip() == "$$$$":
            entry = _build(data, source)
            if entry:
                yield entry
            data, current_tag = {}, None
            continue

        match = _TAG_RE.match(line)
        if match:
            current_tag = match.group(1).strip().lower()
            data.setdefault(current_tag, [])
            continue

        if current_tag is not None:
            if line.strip() == "":
                current_tag = None      # blank line ends a data field
            else:
                data[current_tag].append(line.strip())

    entry = _build(data, source)
    if entry:
        yield entry


def _build(data: dict[str, list[str]], source: str) -> StructureEntry | None:
    if not data:
        return None
    primary = _lookup(data, _NAME_TAGS)
    synonyms = _lookup_multi(data, _SYNONYM_TAGS)
    names = ([primary] if primary else []) + [s for s in synonyms if s != primary]
    return StructureEntry(
        structure_id=_lookup(data, _ID_TAGS) or f"{source}:unidentified",
        source=source,
        inchikey=_lookup(data, _INCHIKEY_TAGS),
        smiles=_lookup(data, _SMILES_TAGS),
        inchi=_lookup(data, _INCHI_TAGS),
        names=names,
        organisms=_lookup_multi(data, _ORGANISM_TAGS),
    )
