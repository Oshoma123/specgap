#!/usr/bin/env python3
"""SPECGAP core: cross-match natural-product structures against spectral
library entries and compute structural coverage + name-recoverability.

Input (either the real fetched data, or the synthetic fixture from
code/00_make_fixture.py):
  data/raw/**/lotus_coconut_structures.csv   columns: inchikey, inchikey_skeleton, name, source_db
  data/raw/**/spectral_entries.csv           columns: spectrum_id, inchikey, declared_name, spectral_source, ionization_mode

Output:
  data/processed/coverage_audit.csv       one row per structure, matched or not
  data/processed/name_recoverability.csv  one row per spectral entry, recovered or not

Usage:
  python code/02_build.py [--fixture]
"""
import argparse
import csv
import difflib
import glob
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw")
PROCESSED = os.path.join(ROOT, "data", "processed")

NAME_FUZZY_THRESHOLD = 0.92  # verify point — see docs/BUILD_SPEC.md


def normalize_name(name):
    name = name.lower().strip()
    name = re.sub(r"\b(hydrate|hydrochloride|hcl|sodium|potassium|salt)\b", "", name)
    name = re.sub(r"[^a-z0-9]+", " ", name).strip()
    return name


def find_input(filename):
    matches = glob.glob(os.path.join(RAW, "**", filename), recursive=True)
    if not matches:
        raise SystemExit(
            f"missing {filename} under data/raw/ — run code/00_make_fixture.py "
            f"for a test run, or code/01_fetch.py for real data")
    return matches[0]


def load_structures():
    path = find_input("lotus_coconut_structures.csv")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    by_key, by_skel, names_by_key = {}, {}, {}
    for r in rows:
        by_key.setdefault(r["inchikey"], []).append(r)
        by_skel.setdefault(r["inchikey_skeleton"], []).append(r)
        names_by_key.setdefault(r["inchikey"], set()).add(normalize_name(r["name"]))
    return rows, by_key, by_skel, names_by_key


def load_spectra():
    path = find_input("spectral_entries.csv")
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def name_recoverable(declared_name, candidate_names):
    norm = normalize_name(declared_name)
    if norm in candidate_names:
        return True, "exact"
    for cand in candidate_names:
        ratio = difflib.SequenceMatcher(None, norm, cand).ratio()
        if ratio >= NAME_FUZZY_THRESHOLD:
            return True, f"fuzzy:{ratio:.2f}"
    return False, "none"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    os.makedirs(PROCESSED, exist_ok=True)

    structures, by_key, by_skel, names_by_key = load_structures()
    spectra = load_spectra()

    keys_with_spectrum = {s["inchikey"] for s in spectra}
    skels_with_spectrum = {s["inchikey"][:14] for s in spectra}
    sources_by_key = {}
    for s in spectra:
        sources_by_key.setdefault(s["inchikey"], set()).add(s["spectral_source"])

    # --- structural coverage: one row per structure-database entry ---
    coverage_rows = []
    for r in structures:
        key, skel = r["inchikey"], r["inchikey_skeleton"]
        matched_exact = key in keys_with_spectrum
        matched_skel = skel in skels_with_spectrum
        coverage_rows.append({
            "inchikey": key,
            "inchikey_skeleton": skel,
            "name": r["name"],
            "source_db": r["source_db"],
            "matched_exact_inchikey": matched_exact,
            "matched_skeleton": matched_skel,
            "matching_spectral_sources": ";".join(sorted(sources_by_key.get(key, []))),
        })
    with open(os.path.join(PROCESSED, "coverage_audit.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(coverage_rows[0].keys()))
        w.writeheader()
        w.writerows(coverage_rows)

    # --- name recoverability: one row per spectral entry ---
    recov_rows = []
    for s in spectra:
        candidates = names_by_key.get(s["inchikey"], set())
        recoverable, method = name_recoverable(s["declared_name"], candidates)
        recov_rows.append({
            "spectrum_id": s["spectrum_id"],
            "inchikey": s["inchikey"],
            "declared_name": s["declared_name"],
            "spectral_source": s["spectral_source"],
            "ionization_mode": s["ionization_mode"],
            "name_recoverable": recoverable,
            "match_method": method,
        })
    with open(os.path.join(PROCESSED, "name_recoverability.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recov_rows[0].keys()))
        w.writeheader()
        w.writerows(recov_rows)

    print(f"wrote {len(coverage_rows)} coverage rows and {len(recov_rows)} name-recoverability rows to {PROCESSED}")


if __name__ == "__main__":
    main()
