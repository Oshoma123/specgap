"""End-to-end pipeline test: fixture -> build -> QA, checking output shape
and invariants rather than specific values (values are seeded-random and
allowed to vary if the fixture generator changes).

Run with: pytest tests/
"""
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
CODE = os.path.join(ROOT, "code")
PROCESSED = os.path.join(ROOT, "data", "processed")


def run(script, *args):
    result = subprocess.run(
        [sys.executable, os.path.join(CODE, script), *args],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, f"{script} failed:\n{result.stdout}\n{result.stderr}"
    return result


def test_pipeline_end_to_end(tmp_path_factory):
    run("00_make_fixture.py")
    run("02_build.py")
    run("03_qa.py")

    coverage_path = os.path.join(PROCESSED, "coverage_audit.csv")
    recov_path = os.path.join(PROCESSED, "name_recoverability.csv")
    stats_path = os.path.join(PROCESSED, "stats.json")
    qa_path = os.path.join(PROCESSED, "qa_report.txt")

    for p in (coverage_path, recov_path, stats_path, qa_path):
        assert os.path.exists(p), f"missing output: {p}"

    with open(coverage_path, newline="") as f:
        coverage_rows = list(csv.DictReader(f))
    assert len(coverage_rows) > 0
    required_cols = {"inchikey", "inchikey_skeleton", "name", "source_db",
                      "matched_exact_inchikey", "matched_skeleton", "matching_spectral_sources"}
    assert required_cols.issubset(coverage_rows[0].keys())

    with open(recov_path, newline="") as f:
        recov_rows = list(csv.DictReader(f))
    assert len(recov_rows) > 0

    with open(stats_path) as f:
        stats = json.load(f)
    assert stats["status"].startswith("SYNTHETIC FIXTURE RUN")
    pct = stats["structural_coverage"]["matched_skeleton_pct"]
    assert 0 <= pct <= 100
    # skeleton coverage can never be lower than exact-InChIKey coverage,
    # since exact match implies skeleton match
    assert stats["structural_coverage"]["matched_skeleton_pct"] >= stats["structural_coverage"]["matched_exact_pct"]

    with open(qa_path) as f:
        qa_text = f.read()
    assert "SYNTHETIC FIXTURE RUN" in qa_text
    assert "Named spot checks" in qa_text
