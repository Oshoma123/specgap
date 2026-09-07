"""Tests for chemical-identity handling."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from specgap.identity import (  # noqa: E402
    is_standard_inchikey,
    is_wellformed_inchikey,
    name_matches,
    normalize_name,
    skeleton,
    strip_adduct,
)

REAL_KEY = "NETSQGRTUNRXEO-UHFFFAOYSA-N"     # Dehydrocostus lactone (COCONUT)


def test_wellformed_accepts_real_key():
    assert is_wellformed_inchikey(REAL_KEY)


def test_wellformed_rejects_malformed():
    for bad in ["", None, "NOTAKEY", "NETSQGRTUNRXEO", "netsqgrtunrxeo-UHFFFAOYSA-N".upper()[:20],
                "NETSQGRTUNRXEO-UHFFFAOYSA", "NETSQGRTUNRXEO-UHFFFAOYSA-NN",
                "NETSQGRTUNRXE0-UHFFFAOYSA-N"]:  # digit zero, not letter O
        assert not is_wellformed_inchikey(bad), bad


def test_skeleton_is_first_block():
    assert skeleton(REAL_KEY) == "NETSQGRTUNRXEO"
    assert len(skeleton(REAL_KEY)) == 14


def test_standard_inchikey_flag():
    assert is_standard_inchikey(REAL_KEY)                      # ...YSA-N -> S at pos 8
    assert not is_standard_inchikey("NETSQGRTUNRXEO-UHFFFAOYNA-N")


# ------------------------------------------------------------- adducts


def test_strip_bracketed_adduct():
    assert strip_adduct("Bortezomib (Velcade) [M+Na]") == "Bortezomib (Velcade)"


def test_strip_bare_trailing_adduct():
    assert strip_adduct("Desferrioxamine B M+H") == "Desferrioxamine B"


def test_strip_adduct_leaves_plain_names_alone():
    assert strip_adduct("Dehydrocostus lactone") == "Dehydrocostus lactone"
    assert strip_adduct("Caffeine") == "Caffeine"


# --------------------------------------------------------- name norming


def test_normalize_handles_case_and_punctuation():
    assert normalize_name("  Dehydrocostus   Lactone!! ") == "dehydrocostus lactone"


def test_normalize_strips_salt_words():
    assert normalize_name("Morphine Hydrochloride") == "morphine"
    assert normalize_name("4-Cyclohexylbutanamide hydrate") == "4 cyclohexylbutanamide"


def test_normalize_treats_na_as_empty():
    """Critical: if 'N/A' normalized to a real value, every N/A record would
    spuriously match every other N/A record."""
    for null in ["N/A", "n/a", "NONE", "null", "-", "", None, "Unknown"]:
        assert normalize_name(null) == "", null


def test_normalize_is_idempotent():
    once = normalize_name("Curcumin Sodium Salt [M+H]")
    assert normalize_name(once) == once


def test_normalize_strips_adduct_before_matching():
    assert normalize_name("Desferrioxamine B M+H") == "desferrioxamine b"


# ------------------------------------------------------------ matching


def test_exact_match():
    ok, method = name_matches("Dehydrocostus lactone", {"dehydrocostus lactone"})
    assert ok and method == "exact"


def test_salt_variant_becomes_exact_after_normalization():
    ok, method = name_matches("Curcumin Hydrate", {"curcumin"})
    assert ok and method == "exact"


def test_fuzzy_match_on_plural_variant():
    ok, method = name_matches("Curcumins", {"curcumin"})
    assert ok and method.startswith("fuzzy:")


def test_no_match_on_unrelated_name():
    ok, method = name_matches("Caffeine", {"dehydrocostus lactone"})
    assert not ok and method == "none"


def test_empty_candidates_never_match():
    ok, method = name_matches("Anything", set())
    assert not ok and method == "none"


def test_empty_declared_name_never_matches():
    """Absence of a name is not evidence of a match."""
    for null in ["N/A", "", None]:
        ok, method = name_matches(null, {"curcumin"})
        assert not ok and method == "none"


def test_short_name_typo_below_threshold_is_documented():
    """A one-character substitution in an 8-letter word scores 0.875, under
    the 0.92 default. This is a known blind spot, not a bug — see
    docs/LIMITATIONS.md. Pinned here so a threshold change is deliberate."""
    ok, _ = name_matches("Kurcumin", {"curcumin"})
    assert not ok


def test_threshold_is_configurable():
    ok, method = name_matches("Kurcumin", {"curcumin"}, fuzzy_threshold=0.80)
    assert ok and method.startswith("fuzzy:")
