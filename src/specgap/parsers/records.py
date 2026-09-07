"""Uniform record shapes emitted by every parser."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SpectralEntry:
    """One reference spectrum from a spectral library."""

    spectrum_id: str
    source: str                      # GNPS | MassBank | MoNA
    inchikey: str | None = None
    smiles: str | None = None
    inchi: str | None = None
    names: list[str] = field(default_factory=list)   # all synonyms, in order
    ion_mode: str | None = None      # positive | negative | None
    ms_level: str | None = None
    library_quality: str | None = None   # GNPS LIBRARYQUALITY, 1 is best
    compound_class: str | None = None    # MassBank CH$COMPOUND_CLASS
    license: str | None = None           # per-record, matters for MoNA/MassBank
    n_peaks: int | None = None

    @property
    def primary_name(self) -> str | None:
        return self.names[0] if self.names else None


@dataclass
class StructureEntry:
    """One compound from a natural-product structure database."""

    structure_id: str
    source: str                      # LOTUS | COCONUT
    inchikey: str | None = None
    smiles: str | None = None
    inchi: str | None = None
    names: list[str] = field(default_factory=list)
    organisms: list[str] = field(default_factory=list)

    @property
    def primary_name(self) -> str | None:
        return self.names[0] if self.names else None
