"""End-to-end: real-format fixtures -> parsers -> engine -> stats.

These tests exercise the same code path a full-corpus run uses; only the
input size differs.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
sys.path.insert(0, os.path.join(ROOT, "src"))

from specgap.coverage import (  # noqa: E402
    SpectralIndex, build_name_lookup, name_recoverability, structural_coverage,
)
from specgap.parsers import (  # noqa: E402
    parse_massbank_stream, parse_mgf, parse_msp, parse_sdf,
)
from specgap.report import coverage_stats, index_stats, name_stats, qa_report  # noqa: E402


def load_all():
    with open(os.path.join(FIXTURES, "coconut_sample.sdf")) as fh:
        structures = list(parse_sdf(fh, source="COCONUT"))
    spectra = []
    with open(os.path.join(FIXTURES, "gnps_sample.mgf")) as fh:
        spectra += list(parse_mgf(fh, source="GNPS"))
    with open(os.path.join(FIXTURES, "mona_sample.msp")) as fh:
        spectra += list(parse_msp(fh, source="MoNA"))
    with open(os.path.join(FIXTURES, "massbank_sample.txt")) as fh:
        spectra += list(parse_massbank_stream(fh))
    return structures, spectra


def test_pipeline_runs_and_is_internally_consistent():
    structures, spectra = load_all()
    index = SpectralIndex.build(spectra)
    cov = structural_coverage(structures, index)
    lookup = build_name_lookup(structures)
    names = name_recoverability(spectra, lookup)

    cstats = coverage_stats(cov)
    nstats = name_stats(names)

    assert cstats["n_structures_total"] == len(structures)
    assert nstats["n_spectra_total"] == len(spectra)
    assert cstats["n_structures_joinable"] <= cstats["n_structures_total"]
    assert nstats["n_assessable"] <= nstats["n_spectra_total"]
    assert (cstats["skeleton"]["pct_of_joinable"]
            >= cstats["exact_inchikey"]["pct_of_joinable"])


def test_gnps_mgf_is_wholly_unjoinable():
    """A real format-level finding, not a fixture artifact: the GNPS MGF
    export carries SMILES and INCHI but no INCHIKEY field, so no GNPS MGF
    record can be joined on InChIKey without a structure-conversion step.
    Verified against GNPS's published format documentation. If GNPS ever adds
    an InChIKey field this test should fail, which is the point.
    """
    with open(os.path.join(FIXTURES, "gnps_sample.mgf")) as fh:
        gnps = list(parse_mgf(fh, source="GNPS"))
    index = SpectralIndex.build(gnps)
    assert index.n_total == len(gnps)
    assert index.n_joinable == 0
    assert index.n_unjoinable_by_source["GNPS"] == len(gnps)


def test_massbank_and_mona_are_partly_joinable():
    """Contrast with GNPS MGF: these formats do carry InChIKeys."""
    with open(os.path.join(FIXTURES, "mona_sample.msp")) as fh:
        mona = list(parse_msp(fh, source="MoNA"))
    with open(os.path.join(FIXTURES, "massbank_sample.txt")) as fh:
        mb = list(parse_massbank_stream(fh))
    index = SpectralIndex.build(mona + mb)
    assert index.n_joinable > 0


def test_qa_report_states_its_denominators():
    """A coverage number without a denominator is uninterpretable."""
    structures, spectra = load_all()
    index = SpectralIndex.build(spectra)
    cov = structural_coverage(structures, index)
    names = name_recoverability(spectra, build_name_lookup(structures))
    report = qa_report(cov, names, index, "test provenance line")
    assert "test provenance line" in report
    assert "of joinable" in report
    assert "of assessable" in report
    assert "SANITY CHECKS" in report


def _split_spec():
    """Load split_spec from the audit script (not an importable package)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "audit_cli", os.path.join(ROOT, "scripts", "02_audit.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.split_spec


def test_split_spec_handles_windows_paths():
    """Regression: a Windows drive colon must not disable label splitting.

    Found by a real Python 3.9 run on Windows, where
    'C:\\...\\coconut_sample.sdf:COCONUT' came through with ':COCONUT' still
    attached to the filename, so the file could not be opened.
    """
    split_spec = _split_spec()
    assert split_spec(r"C:\data\x.sdf:COCONUT", "D") == (r"C:\data\x.sdf", "COCONUT")
    assert split_spec(r"C:\data\x.sdf", "D") == (r"C:\data\x.sdf", "D")
    assert split_spec(r"D:\a b\c.msp:MoNA", "D") == (r"D:\a b\c.msp", "MoNA")


def test_split_spec_handles_posix_and_relative_paths():
    split_spec = _split_spec()
    assert split_spec("tests/f/x.sdf:LOTUS", "D") == ("tests/f/x.sdf", "LOTUS")
    assert split_spec("tests/f/x.sdf", "D") == ("tests/f/x.sdf", "D")
    assert split_spec("/data/x.sdf:GNPS", "D") == ("/data/x.sdf", "GNPS")
    assert split_spec("/data/x.sdf", "D") == ("/data/x.sdf", "D")


def test_split_spec_rejects_bare_drive_letter_as_label():
    split_spec = _split_spec()
    assert split_spec("C:", "D") == ("C:", "D")
    assert split_spec(r"C:\data", "D") == (r"C:\data", "D")


def test_audit_script_runs_end_to_end():
    """The CLI users actually invoke must work, not just the library."""
    with tempfile.TemporaryDirectory() as out:
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "02_audit.py"),
             "--structures", os.path.join(FIXTURES, "coconut_sample.sdf") + ":COCONUT",
             "--spectra-msp", os.path.join(FIXTURES, "mona_sample.msp") + ":MoNA",
             "--spectra-massbank", os.path.join(FIXTURES, "massbank_sample.txt"),
             "--spectra-mgf", os.path.join(FIXTURES, "gnps_sample.mgf") + ":GNPS",
             "--out", out,
             "--provenance", "pytest fixture run"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        for name in ("coverage_audit.csv", "name_recoverability.csv",
                     "stats.json", "qa_report.txt"):
            assert os.path.exists(os.path.join(out, name)), name
