"""SPECGAP: assessing the coverage of public mass spectral libraries.

Cross-matches natural-product structure sets (LOTUS, COCONUT) against the
open spectral-library layer (GNPS, MassBank, MoNA), reporting structural
coverage and name-recoverability.
"""
__version__ = "0.7.0"

from .identity import (
    is_wellformed_inchikey,
    is_standard_inchikey,
    name_matches,
    normalize_name,
    skeleton,
    strip_adduct,
)
from .coverage import (
    CoverageRow,
    NameRow,
    SpectralIndex,
    build_name_lookup,
    name_recoverability,
    structural_coverage,
)
from .report import coverage_stats, index_stats, name_stats, qa_report

__all__ = [
    "__version__",
    "is_wellformed_inchikey", "is_standard_inchikey", "name_matches",
    "normalize_name", "skeleton", "strip_adduct",
    "CoverageRow", "NameRow", "SpectralIndex", "build_name_lookup",
    "name_recoverability", "structural_coverage",
    "coverage_stats", "index_stats", "name_stats", "qa_report",
]
