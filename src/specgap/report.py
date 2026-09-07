"""Statistics and QA reporting.

Every rate reported here names its denominator. A coverage number without a
stated denominator is uninterpretable, because the three plausible
denominators (all structures / joinable structures / structures whose
InChIKey appears anywhere in the spectral layer) can differ by a wide margin.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Sequence

from .coverage import CoverageRow, NameRow, SpectralIndex


def _pct(numerator: int, denominator: int) -> float | None:
    return round(100.0 * numerator / denominator, 2) if denominator else None


def coverage_stats(rows: Sequence[CoverageRow]) -> dict:
    total = len(rows)
    joinable = [r for r in rows if r.joinable]
    n_join = len(joinable)
    exact = sum(r.matched_exact for r in joinable)
    skel = sum(r.matched_skeleton for r in joinable)

    by_db: dict[str, dict] = defaultdict(lambda: {"n": 0, "joinable": 0, "exact": 0, "skeleton": 0})
    for r in rows:
        bucket = by_db[r.source_db]
        bucket["n"] += 1
        if r.joinable:
            bucket["joinable"] += 1
            bucket["exact"] += r.matched_exact
            bucket["skeleton"] += r.matched_skeleton

    return {
        "n_structures_total": total,
        "n_structures_joinable": n_join,
        "n_structures_unjoinable": total - n_join,
        "denominator_note": (
            "coverage percentages use JOINABLE structures as the denominator; "
            "structures without a well-formed InChIKey are excluded, not "
            "counted as uncovered"
        ),
        "exact_inchikey": {
            "n_covered": exact,
            "pct_of_joinable": _pct(exact, n_join),
        },
        "skeleton": {
            "n_covered": skel,
            "pct_of_joinable": _pct(skel, n_join),
        },
        "status_counts": dict(Counter(r.status for r in rows)),
        "by_structure_db": {
            db: {
                "n": v["n"],
                "n_joinable": v["joinable"],
                "exact_pct_of_joinable": _pct(v["exact"], v["joinable"]),
                "skeleton_pct_of_joinable": _pct(v["skeleton"], v["joinable"]),
            }
            for db, v in sorted(by_db.items())
        },
    }


def name_stats(rows: Sequence[NameRow]) -> dict:
    total = len(rows)
    assessable = [r for r in rows if r.status in {"recoverable", "unrecoverable"}]
    n_assess = len(assessable)
    recovered = sum(r.recoverable for r in assessable)

    by_source: dict[str, dict] = defaultdict(lambda: {"n": 0, "assessable": 0, "recovered": 0})
    for r in rows:
        bucket = by_source[r.spectral_source]
        bucket["n"] += 1
        if r.status in {"recoverable", "unrecoverable"}:
            bucket["assessable"] += 1
            bucket["recovered"] += r.recoverable

    return {
        "n_spectra_total": total,
        "n_assessable": n_assess,
        "denominator_note": (
            "recoverability uses ASSESSABLE spectra as the denominator: those "
            "with an InChIKey, a declared name, and a structure present in the "
            "reference set. All other outcomes are reported in status_counts"
        ),
        "n_recovered": recovered,
        "pct_of_assessable": _pct(recovered, n_assess),
        "status_counts": dict(Counter(r.status for r in rows)),
        "method_counts": dict(Counter(r.method for r in rows if r.method != "not_assessed")),
        "by_spectral_source": {
            src: {
                "n": v["n"],
                "n_assessable": v["assessable"],
                "recovered_pct_of_assessable": _pct(v["recovered"], v["assessable"]),
            }
            for src, v in sorted(by_source.items())
        },
    }


def index_stats(index: SpectralIndex) -> dict:
    return {
        "n_spectra_total": index.n_total,
        "n_spectra_joinable": index.n_joinable,
        "n_unique_inchikeys": len(index.by_inchikey),
        "n_unique_skeletons": len(index.by_skeleton),
        "by_source": {
            src: {
                "n_total": n,
                "n_unjoinable": index.n_unjoinable_by_source.get(src, 0),
                "pct_unjoinable": _pct(index.n_unjoinable_by_source.get(src, 0), n),
            }
            for src, n in sorted(index.n_total_by_source.items())
        },
    }


def qa_report(
    cov_rows: Sequence[CoverageRow],
    name_rows: Sequence[NameRow],
    index: SpectralIndex,
    provenance_note: str,
    n_spot_checks: int = 5,
) -> str:
    """Human-readable QA report; the first thing a reader should look at."""
    cov = coverage_stats(cov_rows)
    nam = name_stats(name_rows)
    idx = index_stats(index)

    lines = ["SPECGAP QA report", "=" * 60, "", f"PROVENANCE: {provenance_note}", ""]

    lines += ["SPECTRAL INDEX", "-" * 60,
              f"  spectra loaded:      {idx['n_spectra_total']}",
              f"  joinable (InChIKey): {idx['n_spectra_joinable']}",
              f"  unique InChIKeys:    {idx['n_unique_inchikeys']}",
              f"  unique skeletons:    {idx['n_unique_skeletons']}"]
    for src, v in idx["by_source"].items():
        lines.append(f"    {src}: {v['n_total']} spectra, "
                     f"{v['n_unjoinable']} unjoinable ({v['pct_unjoinable']}%)")

    lines += ["", "STRUCTURAL COVERAGE", "-" * 60,
              f"  structures loaded:   {cov['n_structures_total']}",
              f"  joinable:            {cov['n_structures_joinable']}",
              f"  unjoinable:          {cov['n_structures_unjoinable']}",
              f"  exact-InChIKey:      {cov['exact_inchikey']['n_covered']} "
              f"({cov['exact_inchikey']['pct_of_joinable']}% of joinable)",
              f"  skeleton-level:      {cov['skeleton']['n_covered']} "
              f"({cov['skeleton']['pct_of_joinable']}% of joinable)",
              f"  NOTE: {cov['denominator_note']}"]

    lines += ["", "NAME-RECOVERABILITY", "-" * 60,
              f"  spectra:             {nam['n_spectra_total']}",
              f"  assessable:          {nam['n_assessable']}",
              f"  recovered:           {nam['n_recovered']} "
              f"({nam['pct_of_assessable']}% of assessable)",
              f"  NOTE: {nam['denominator_note']}", "",
              "  outcome breakdown:"]
    for status, count in sorted(nam["status_counts"].items()):
        lines.append(f"    {status}: {count}")

    lines += ["", "SPOT CHECKS (verify these by hand against the source)", "-" * 60]
    buckets = defaultdict(list)
    for row in cov_rows:
        buckets[row.status].append(row)
    for status in ("covered_exact", "covered_skeleton_only", "uncovered", "unjoinable"):
        for row in buckets.get(status, [])[:n_spot_checks]:
            lines.append(f"  [{status}] {row.structure_id} ({row.source_db}) "
                         f"key={row.inchikey} sources={row.matching_sources or '-'}")

    lines += ["", "SANITY CHECKS", "-" * 60]
    skel_ge_exact = (
        (cov["skeleton"]["pct_of_joinable"] or 0)
        >= (cov["exact_inchikey"]["pct_of_joinable"] or 0)
    )
    lines.append(f"  skeleton coverage >= exact coverage: "
                 f"{'PASS' if skel_ge_exact else 'FAIL (impossible; join is broken)'}")
    lines.append(f"  joinable <= total (structures): "
                 f"{'PASS' if cov['n_structures_joinable'] <= cov['n_structures_total'] else 'FAIL'}")
    lines.append(f"  assessable <= total (spectra): "
                 f"{'PASS' if nam['n_assessable'] <= nam['n_spectra_total'] else 'FAIL'}")

    return "\n".join(lines) + "\n"
