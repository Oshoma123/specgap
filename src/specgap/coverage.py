"""The SPECGAP coverage engine.

Two measures, deliberately kept separate because they answer different
questions and fail in different ways:

STRUCTURAL COVERAGE
    Of the natural-product structures documented in LOTUS/COCONUT, how many
    have at least one reference spectrum in GNPS/MassBank/MoNA?

NAME-RECOVERABILITY
    Of the entries in those spectral libraries, how many carry a compound
    name that can be reconciled with a name recorded for the same structure
    in LOTUS/COCONUT?

The distinction that most affects honesty of the result:

    UNCOVERED  = the structure is joinable (has a well-formed InChIKey) and
                 no spectral library has a matching key.
    UNJOINABLE = the structure or the spectrum lacks a usable InChIKey, so
                 the question cannot be answered for that record at all.

Reporting unjoinable records as "uncovered" would silently inflate the
coverage gap, and since GNPS's MGF and JSON exports carry no InChIKey field,
that inflation would be large and systematic. Every count below therefore
carries an explicit denominator.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from .identity import is_wellformed_inchikey, name_matches, normalize_name, skeleton
from .parsers.records import SpectralEntry, StructureEntry


@dataclass
class SpectralIndex:
    """Lookup structure built from spectral-library entries."""

    by_inchikey: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_skeleton: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    n_total: int = 0
    n_joinable: int = 0
    n_unjoinable_by_source: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    n_total_by_source: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def add(self, entry: SpectralEntry) -> None:
        self.n_total += 1
        self.n_total_by_source[entry.source] += 1
        key = (entry.inchikey or "").strip().upper()
        if is_wellformed_inchikey(key):
            self.n_joinable += 1
            self.by_inchikey[key].add(entry.source)
            self.by_skeleton[skeleton(key)].add(entry.source)
        else:
            self.n_unjoinable_by_source[entry.source] += 1

    @classmethod
    def build(cls, entries: Iterable[SpectralEntry]) -> "SpectralIndex":
        index = cls()
        for entry in entries:
            index.add(entry)
        return index


@dataclass
class CoverageRow:
    structure_id: str
    source_db: str
    inchikey: str | None
    joinable: bool
    matched_exact: bool
    matched_skeleton: bool
    matching_sources: str      # ';'-joined, exact-key matches only

    @property
    def status(self) -> str:
        if not self.joinable:
            return "unjoinable"
        if self.matched_exact:
            return "covered_exact"
        if self.matched_skeleton:
            return "covered_skeleton_only"
        return "uncovered"


def structural_coverage(
    structures: Iterable[StructureEntry],
    index: SpectralIndex,
) -> list[CoverageRow]:
    """One CoverageRow per structure-database entry."""
    rows: list[CoverageRow] = []
    for structure in structures:
        key = (structure.inchikey or "").strip().upper()
        joinable = is_wellformed_inchikey(key)
        if not joinable:
            rows.append(CoverageRow(
                structure_id=structure.structure_id,
                source_db=structure.source,
                inchikey=structure.inchikey,
                joinable=False,
                matched_exact=False,
                matched_skeleton=False,
                matching_sources="",
            ))
            continue
        sources = index.by_inchikey.get(key, set())
        rows.append(CoverageRow(
            structure_id=structure.structure_id,
            source_db=structure.source,
            inchikey=key,
            joinable=True,
            matched_exact=bool(sources),
            matched_skeleton=skeleton(key) in index.by_skeleton,
            matching_sources=";".join(sorted(sources)),
        ))
    return rows


@dataclass
class NameRow:
    spectrum_id: str
    spectral_source: str
    declared_name: str | None
    inchikey: str | None
    joinable: bool
    has_declared_name: bool
    structure_known: bool       # the InChIKey exists in the structure set
    recoverable: bool
    method: str

    @property
    def status(self) -> str:
        if not self.joinable:
            return "unjoinable_no_inchikey"
        if not self.has_declared_name:
            return "unjoinable_no_name"
        if not self.structure_known:
            return "structure_not_in_reference_set"
        return "recoverable" if self.recoverable else "unrecoverable"


def build_name_lookup(
    structures: Iterable[StructureEntry],
) -> dict[str, set[str]]:
    """InChIKey -> set of normalized names known for that structure."""
    lookup: dict[str, set[str]] = defaultdict(set)
    for structure in structures:
        key = (structure.inchikey or "").strip().upper()
        if not is_wellformed_inchikey(key):
            continue
        for name in structure.names:
            norm = normalize_name(name)
            if norm:
                lookup[key].add(norm)
    return lookup


def name_recoverability(
    spectra: Iterable[SpectralEntry],
    name_lookup: dict[str, set[str]],
    fuzzy_threshold: float = 0.92,
) -> list[NameRow]:
    """One NameRow per spectral-library entry.

    A spectrum is only judged recoverable-or-not when the question is
    answerable: it must have an InChIKey, a declared name, and its structure
    must be present in the reference set. Everything else is reported as its
    own category rather than as a failure.
    """
    rows: list[NameRow] = []
    for entry in spectra:
        key = (entry.inchikey or "").strip().upper()
        joinable = is_wellformed_inchikey(key)
        declared = entry.primary_name
        has_name = bool(normalize_name(declared))
        candidates = name_lookup.get(key, set()) if joinable else set()
        structure_known = bool(candidates)

        if joinable and has_name and structure_known:
            # test every name the spectral library gave us, not only the first
            recoverable, method = False, "none"
            for candidate_name in entry.names or []:
                recoverable, method = name_matches(
                    candidate_name, candidates, fuzzy_threshold)
                if recoverable:
                    break
        else:
            recoverable, method = False, "not_assessed"

        rows.append(NameRow(
            spectrum_id=entry.spectrum_id,
            spectral_source=entry.source,
            declared_name=declared,
            inchikey=key or None,
            joinable=joinable,
            has_declared_name=has_name,
            structure_known=structure_known,
            recoverable=recoverable,
            method=method,
        ))
    return rows
