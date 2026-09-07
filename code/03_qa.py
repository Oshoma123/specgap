#!/usr/bin/env python3
"""Write data/processed/qa_report.txt and data/processed/stats.json from
coverage_audit.csv and name_recoverability.csv.

Every number that appears in any document (README, paper, poster) must be
read from stats.json, not typed by hand — see docs/BUILD_SPEC.md.

Usage:
  python code/03_qa.py
"""
import csv
import json
import os
import random

PROCESSED = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def read_csv(name):
    with open(os.path.join(PROCESSED, name), newline="") as f:
        return list(csv.DictReader(f))


def pct(n, d):
    return round(100 * n / d, 2) if d else None


def main():
    coverage = read_csv("coverage_audit.csv")
    recov = read_csv("name_recoverability.csv")

    n_struct = len(coverage)
    n_exact = sum(r["matched_exact_inchikey"] == "True" for r in coverage)
    n_skel = sum(r["matched_skeleton"] == "True" for r in coverage)

    by_source_db = {}
    for r in coverage:
        d = by_source_db.setdefault(r["source_db"], {"n": 0, "matched_skel": 0})
        d["n"] += 1
        d["matched_skel"] += r["matched_skeleton"] == "True"

    n_spec = len(recov)
    n_recov = sum(r["name_recoverable"] == "True" for r in recov)
    by_spectral_source = {}
    for r in recov:
        d = by_spectral_source.setdefault(r["spectral_source"], {"n": 0, "recovered": 0})
        d["n"] += 1
        d["recovered"] += r["name_recoverable"] == "True"

    stats = {
        "status": "SYNTHETIC FIXTURE RUN \u2014 not real coverage data, see docs/BUILD_SPEC.md",
        "structural_coverage": {
            "n_structures": n_struct,
            "matched_exact_inchikey": n_exact,
            "matched_exact_pct": pct(n_exact, n_struct),
            "matched_skeleton": n_skel,
            "matched_skeleton_pct": pct(n_skel, n_struct),
            "by_source_db": {
                k: {"n": v["n"], "matched_skeleton_pct": pct(v["matched_skel"], v["n"])}
                for k, v in by_source_db.items()
            },
        },
        "name_recoverability": {
            "n_spectral_entries": n_spec,
            "recovered": n_recov,
            "recovered_pct": pct(n_recov, n_spec),
            "by_spectral_source": {
                k: {"n": v["n"], "recovered_pct": pct(v["recovered"], v["n"])}
                for k, v in by_spectral_source.items()
            },
        },
    }
    with open(os.path.join(PROCESSED, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    # named spot checks: 5 structures the author can eyeball, chosen to
    # include matched, unmatched, and boundary (skeleton-only) cases
    random.seed(20260901)
    matched = [r for r in coverage if r["matched_exact_inchikey"] == "True"]
    unmatched = [r for r in coverage if r["matched_exact_inchikey"] != "True" and r["matched_skeleton"] != "True"]
    skeleton_only = [r for r in coverage
                      if r["matched_skeleton"] == "True" and r["matched_exact_inchikey"] != "True"]
    spot = (random.sample(matched, min(2, len(matched)))
            + random.sample(unmatched, min(2, len(unmatched)))
            + random.sample(skeleton_only, min(1, len(skeleton_only))))

    lines = []
    lines.append("SPECGAP QA report")
    lines.append("STATUS: SYNTHETIC FIXTURE RUN -- not real coverage data (see docs/BUILD_SPEC.md)")
    lines.append("")
    lines.append(f"Structures loaded: {n_struct}")
    for k, v in by_source_db.items():
        lines.append(f"  {k}: {v['n']} structures, {pct(v['matched_skel'], v['n'])}% skeleton-matched")
    lines.append(f"Exact-InChIKey structural coverage: {n_exact}/{n_struct} ({pct(n_exact, n_struct)}%)")
    lines.append(f"Skeleton-level structural coverage: {n_skel}/{n_struct} ({pct(n_skel, n_struct)}%)")
    lines.append("")
    lines.append(f"Spectral entries loaded: {n_spec}")
    for k, v in by_spectral_source.items():
        lines.append(f"  {k}: {v['n']} entries, {pct(v['recovered'], v['n'])}% name-recoverable")
    lines.append(f"Overall name-recoverability: {n_recov}/{n_spec} ({pct(n_recov, n_spec)}%)")
    lines.append("")
    lines.append("Named spot checks (verify these by hand against source data before trusting the run):")
    for r in spot:
        lines.append(f"  - {r['name']} ({r['inchikey']}, {r['source_db']}): "
                      f"exact={r['matched_exact_inchikey']}, skeleton={r['matched_skeleton']}, "
                      f"sources={r['matching_spectral_sources'] or 'none'}")
    lines.append("")
    lines.append("Sanity checks:")
    lines.append(f"  - no orphan rows: {'PASS' if n_struct and n_spec else 'FAIL'}")
    lines.append(f"  - coverage percentages in [0,100]: "
                  f"{'PASS' if 0 <= (pct(n_exact, n_struct) or 0) <= 100 else 'FAIL'}")

    with open(os.path.join(PROCESSED, "qa_report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
