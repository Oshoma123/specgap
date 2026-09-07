"""Tests for the coverage engine, focused on the distinctions that make the
reported numbers honest: unjoinable vs uncovered, and assessable vs
unrecoverable.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from specgap.coverage import (  # noqa: E402
    SpectralIndex,
    build_name_lookup,
    name_recoverability,
    structural_coverage,
)
from specgap.parsers.records import SpectralEntry, StructureEntry  # noqa: E402
from specgap.report import coverage_stats, name_stats  # noqa: E402

KEY_A = "NETSQGRTUNRXEO-UHFFFAOYSA-N"      # Dehydrocostus lactone
KEY_A_STEREO = "NETSQGRTUNRXEO-ABCDEFGHIJ-N"  # same skeleton, different stereo
KEY_B = "HZGJWEZZXLGUAU-UHFFFAOYSA-N"      # 4-Cyclohexylbutanamide
KEY_C = "RYYVLZVUVIJVGH-UHFFFAOYSA-N"      # Caffeine (no spectrum in fixtures)


def struct(sid, key, names=(), source="COCONUT"):
    return StructureEntry(structure_id=sid, source=source, inchikey=key,
                          names=list(names))


def spec(sid, key, names=(), source="GNPS"):
    return SpectralEntry(spectrum_id=sid, source=source, inchikey=key,
                         names=list(names))


# ------------------------------------------------------ structural coverage


def test_exact_match_is_covered():
    index = SpectralIndex.build([spec("S1", KEY_A)])
    rows = structural_coverage([struct("C1", KEY_A)], index)
    assert rows[0].status == "covered_exact"
    assert rows[0].matching_sources == "GNPS"


def test_stereo_variant_matches_skeleton_only():
    """The core methodological case: same molecular graph, different
    stereochemistry. Must be skeleton-covered but NOT exact-covered."""
    index = SpectralIndex.build([spec("S1", KEY_A_STEREO)])
    rows = structural_coverage([struct("C1", KEY_A)], index)
    assert rows[0].matched_exact is False
    assert rows[0].matched_skeleton is True
    assert rows[0].status == "covered_skeleton_only"


def test_absent_structure_is_uncovered():
    index = SpectralIndex.build([spec("S1", KEY_A)])
    rows = structural_coverage([struct("C1", KEY_C)], index)
    assert rows[0].status == "uncovered"


def test_structure_without_key_is_unjoinable_not_uncovered():
    """The distinction that keeps the coverage gap honest."""
    index = SpectralIndex.build([spec("S1", KEY_A)])
    rows = structural_coverage([struct("C1", None)], index)
    assert rows[0].status == "unjoinable"
    assert rows[0].matched_exact is False


def test_unjoinable_excluded_from_coverage_denominator():
    index = SpectralIndex.build([spec("S1", KEY_A)])
    rows = structural_coverage(
        [struct("C1", KEY_A), struct("C2", None), struct("C3", "BAD")], index)
    stats = coverage_stats(rows)
    assert stats["n_structures_total"] == 3
    assert stats["n_structures_joinable"] == 1
    # 1 of 1 joinable covered = 100%, NOT 1 of 3 = 33%
    assert stats["exact_inchikey"]["pct_of_joinable"] == 100.0


def test_skeleton_coverage_never_below_exact():
    """Structural invariant: exact match implies skeleton match."""
    index = SpectralIndex.build([spec("S1", KEY_A), spec("S2", KEY_B)])
    rows = structural_coverage(
        [struct("C1", KEY_A), struct("C2", KEY_B), struct("C3", KEY_C)], index)
    stats = coverage_stats(rows)
    assert (stats["skeleton"]["pct_of_joinable"]
            >= stats["exact_inchikey"]["pct_of_joinable"])


def test_multiple_sources_recorded():
    index = SpectralIndex.build([
        spec("S1", KEY_A, source="GNPS"),
        spec("S2", KEY_A, source="MassBank"),
    ])
    rows = structural_coverage([struct("C1", KEY_A)], index)
    assert rows[0].matching_sources == "GNPS;MassBank"


def test_index_counts_unjoinable_spectra_per_source():
    index = SpectralIndex.build([
        spec("S1", KEY_A, source="GNPS"),
        spec("S2", None, source="GNPS"),
        spec("S3", KEY_B, source="MassBank"),
    ])
    assert index.n_total == 3
    assert index.n_joinable == 2
    assert index.n_unjoinable_by_source["GNPS"] == 1
    assert index.n_unjoinable_by_source["MassBank"] == 0


# ----------------------------------------------------- name recoverability


def test_name_recovered_exactly():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([spec("S1", KEY_A, ["Dehydrocostus lactone"])], lookup)
    assert rows[0].status == "recoverable"
    assert rows[0].method == "exact"


def test_name_recovered_via_second_synonym():
    """A library listing a compound under its second name should still
    recover — testing only the primary name would understate recoverability."""
    lookup = build_name_lookup([struct("C1", KEY_A, ["Epiligulyl oxide"])])
    rows = name_recoverability(
        [spec("S1", KEY_A, ["Some obscure trade name", "Epiligulyl oxide"])], lookup)
    assert rows[0].status == "recoverable"


def test_name_recovered_after_adduct_strip():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Desferrioxamine B"])])
    rows = name_recoverability([spec("S1", KEY_A, ["Desferrioxamine B M+H"])], lookup)
    assert rows[0].status == "recoverable"


def test_unrecoverable_name_reported_as_such():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([spec("S1", KEY_A, ["Totally different label"])], lookup)
    assert rows[0].status == "unrecoverable"


def test_spectrum_without_key_is_not_assessed():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([spec("S1", None, ["Dehydrocostus lactone"])], lookup)
    assert rows[0].status == "unjoinable_no_inchikey"
    assert rows[0].method == "not_assessed"


def test_spectrum_without_name_is_not_assessed():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([spec("S1", KEY_A, ["N/A"])], lookup)
    assert rows[0].status == "unjoinable_no_name"


def test_structure_absent_from_reference_set_is_not_a_failure():
    """If the compound isn't in LOTUS/COCONUT at all, its name cannot be
    'unrecoverable' — there is nothing to recover it against."""
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([spec("S1", KEY_C, ["Caffeine"])], lookup)
    assert rows[0].status == "structure_not_in_reference_set"


def test_name_stats_denominator_excludes_unassessable():
    lookup = build_name_lookup([struct("C1", KEY_A, ["Dehydrocostus lactone"])])
    rows = name_recoverability([
        spec("S1", KEY_A, ["Dehydrocostus lactone"]),   # recoverable
        spec("S2", KEY_A, ["Nonsense"]),                # unrecoverable
        spec("S3", None, ["Dehydrocostus lactone"]),    # unjoinable
        spec("S4", KEY_C, ["Caffeine"]),                # not in reference set
    ], lookup)
    stats = name_stats(rows)
    assert stats["n_spectra_total"] == 4
    assert stats["n_assessable"] == 2
    assert stats["pct_of_assessable"] == 50.0   # 1 of 2, not 1 of 4


def test_build_name_lookup_skips_unjoinable_structures():
    lookup = build_name_lookup([
        struct("C1", KEY_A, ["Dehydrocostus lactone"]),
        struct("C2", None, ["Orphan name"]),
    ])
    assert set(lookup) == {KEY_A}
