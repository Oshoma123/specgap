"""Unit tests for code/02_build.py's matching logic.

Run with: pytest tests/
"""
import importlib.util
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "code"))

spec = importlib.util.spec_from_file_location("build", os.path.join(ROOT, "code", "02_build.py"))
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def test_normalize_name_strips_salts_and_case():
    assert build.normalize_name("Morphine Hydrochloride") == "morphine"
    assert build.normalize_name("Quercetin Hydrate") == "quercetin"
    assert build.normalize_name("  Caffeine!! ") == "caffeine"


def test_normalize_name_idempotent():
    once = build.normalize_name("Curcumin Sodium Salt")
    twice = build.normalize_name(once)
    assert once == twice


def test_name_recoverable_exact_match():
    ok, method = build.name_recoverable("Curcumin", {"curcumin", "turmeric yellow"})
    assert ok is True
    assert method == "exact"


def test_name_recoverable_fuzzy_match():
    ok, method = build.name_recoverable("Curcumin hydrate", {"curcumin"})
    assert ok is True
    assert method == "exact"  # "hydrate" is stripped, so this becomes exact


def test_name_recoverable_fuzzy_trailing_variant():
    # "curcumins" vs "curcumin": ratio 2*8/17 = 0.941, clears the 0.92 threshold
    ok, method = build.name_recoverable("Curcumins", {"curcumin"})
    assert ok is True
    assert method.startswith("fuzzy:")


def test_name_recoverable_single_char_substitution_not_caught():
    # documents a real limitation (docs/LIMITATIONS.md item 3): a one-letter
    # substitution in an 8-letter word ("kurcumin" vs "curcumin") scores
    # ratio 2*7/16 = 0.875, below the 0.92 threshold, so it is NOT recovered.
    # This is intentional given the current threshold, not a bug — but it
    # means short-name typos are a known blind spot.
    ok, method = build.name_recoverable("Kurcumin", {"curcumin"})
    assert ok is False
    assert method == "none"


def test_name_recoverable_no_match():
    ok, method = build.name_recoverable("Completely Different Compound", {"curcumin"})
    assert ok is False
    assert method == "none"


def test_name_recoverable_empty_candidates():
    ok, method = build.name_recoverable("Anything", set())
    assert ok is False
    assert method == "none"


# --- real-data smoke test, using the verified COCONUT record in
#     docs/REAL_RECORD_EXAMPLE.md (fetched live 2026-09-01) ---

REAL_RECORD = {
    "inchikey": "HZGJWEZZXLGUAU-UHFFFAOYSA-N",
    "inchikey_skeleton": "HZGJWEZZXLGUAU",
    "name": "4-Cyclohexylbutanamide",
}


def test_real_record_skeleton_derivation():
    # the skeleton is always the first 14 characters of the InChIKey
    assert REAL_RECORD["inchikey"][:14] == REAL_RECORD["inchikey_skeleton"]


def test_real_record_name_recoverable_against_itself():
    ok, method = build.name_recoverable(REAL_RECORD["name"], {build.normalize_name(REAL_RECORD["name"])})
    assert ok is True
    assert method == "exact"


def test_real_record_name_not_recoverable_against_unrelated_set():
    ok, method = build.name_recoverable(REAL_RECORD["name"], {"morphine", "caffeine", "quercetin"})
    assert ok is False
