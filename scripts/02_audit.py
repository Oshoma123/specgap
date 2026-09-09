#!/usr/bin/env python3
"""Run a SPECGAP audit over whatever real source files are present.

Works identically on the tiny bundled fixtures and on the full multi-million
record downloads; only the input paths change. Nothing here is hard-coded to
fixture data.

Usage:
  python scripts/02_audit.py \
      --structures tests/fixtures/coconut_sample.sdf:COCONUT \
      --spectra-msp tests/fixtures/mona_sample.msp:MoNA \
      --spectra-massbank tests/fixtures/massbank_sample.txt \
      --spectra-mgf tests/fixtures/gnps_sample.mgf:GNPS \
      --out data/processed \
      --provenance "bundled documentation fixtures, not real corpus"

Each --structures / --spectra-* argument takes PATH[:SOURCE_LABEL].
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from specgap.coverage import (  # noqa: E402
    SpectralIndex, build_name_lookup, name_recoverability, structural_coverage,
)
from specgap.parsers import (  # noqa: E402
    parse_gnps_json, parse_massbank_dir, parse_massbank_stream, parse_mgf,
    parse_msp, parse_sdf,
)
from specgap.report import (  # noqa: E402
    coverage_stats, index_stats, name_stats, qa_report,
)


def split_spec(value: str, default_label: str) -> tuple[str, str]:
    """Split 'path:LABEL' into (path, LABEL).

    Windows-safe. Windows paths contain a drive colon ('C:\\data\\x.sdf'), so
    a naive split on the first colon, or a guard that merely checks for a
    drive letter anywhere, breaks: it either truncates the path or silently
    leaves ':LABEL' glued to the filename.

    Rules: split on the LAST colon, and accept the suffix as a label only if
    it looks like one — non-empty, containing no path separator, and with a
    non-empty head that is not a bare drive letter. Anything else is treated
    as a plain path with the default label.

    Examples:
      'C:\\data\\x.sdf:COCONUT'  -> ('C:\\data\\x.sdf', 'COCONUT')
      'C:\\data\\x.sdf'          -> ('C:\\data\\x.sdf', default)
      'tests/x.sdf:LOTUS'        -> ('tests/x.sdf', 'LOTUS')
      '/data/x.sdf'              -> ('/data/x.sdf', default)
    """
    head, sep, tail = value.rpartition(":")
    if not sep:
        return value, default_label
    looks_like_label = bool(tail) and not any(c in tail for c in "\\/")
    head_is_drive_letter = len(head) == 1 and head.isalpha()
    if looks_like_label and head and not head_is_drive_letter:
        return head, tail
    return value, default_label


def load_structures(args):
    entries = []
    for item in args.structures or []:
        path, label = split_spec(item, "COCONUT")
        with open(path, encoding="utf-8", errors="replace") as fh:
            entries.extend(parse_sdf(fh, source=label))
        print(f"  structures: {len(entries):>8} after {path} ({label})")
    return entries


def load_spectra(args):
    """Yield spectral entries lazily; never materialise the full library.

    The spectral side can be far larger than the structure side (the MoNA
    experimental export is ~11 GB / 1.75M records; GNPS ~2.9M), so this is a
    generator and the caller streams it. Progress is reported by count since
    a silent multi-minute parse is indistinguishable from a hang.
    """
    n = 0

    def tick(label):
        nonlocal n
        n += 1
        if n % 100000 == 0:
            print(f"  ... {n:,} spectra parsed ({label})", flush=True)

    for item in args.spectra_mgf or []:
        path, label = split_spec(item, "GNPS")
        print(f"  reading {path} (mgf/{label})", flush=True)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for e in parse_mgf(fh, source=label):
                tick(label); yield e
    for item in args.spectra_msp or []:
        path, label = split_spec(item, "MoNA")
        print(f"  reading {path} (msp/{label})", flush=True)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for e in parse_msp(fh, source=label):
                tick(label); yield e
    for item in args.spectra_json or []:
        path, _label = split_spec(item, "GNPS")
        print(f"  reading {path} (gnps-json)", flush=True)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for e in parse_gnps_json(fh):
                tick("GNPS"); yield e
    for path in args.spectra_massbank or []:
        print(f"  reading {path} (massbank)", flush=True)
        if os.path.isdir(path):
            for e in parse_massbank_dir(path):
                tick("MassBank"); yield e
        else:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for e in parse_massbank_stream(fh):
                    tick("MassBank"); yield e
    print(f"  done: {n:,} spectra", flush=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--structures", nargs="*", help="SDF path[:LABEL]")
    ap.add_argument("--spectra-mgf", nargs="*", help="MGF path[:LABEL]")
    ap.add_argument("--spectra-msp", nargs="*", help="MSP path[:LABEL]")
    ap.add_argument("--spectra-json", nargs="*", help="GNPS JSON path")
    ap.add_argument("--spectra-massbank", nargs="*", help="MassBank file or directory")
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--fuzzy-threshold", type=float, default=0.92)
    ap.add_argument("--ms-level", default=None,
                    help="keep only spectra whose recorded level matches this "
                         "(e.g. MS2). MS1 spectra give a mass, not a "
                         "fragmentation fingerprint, and are not usable as "
                         "identification references")
    ap.add_argument("--provenance", required=True,
                    help="one line describing exactly what data this run used")
    args = ap.parse_args()

    print("Loading structures...")
    structures = load_structures(args)
    if not structures:
        sys.exit("need at least one structure file")

    # Spectra are streamed twice rather than held in memory: the spectral side
    # can be far larger than the structure side (MoNA experimental export is
    # ~11 GB / 1.75M records, GNPS ~2.9M), and materialising it would dominate
    # memory for no benefit. Re-reading from disk is cheaper than paging.
    def spectra_stream():
        for entry in load_spectra(args):
            if args.ms_level and (entry.ms_level or "").upper() != args.ms_level.upper():
                continue
            yield entry

    print("Pass 1/2: indexing spectra...")
    index = SpectralIndex.build(spectra_stream())
    if index.n_total == 0:
        sys.exit("no spectra parsed (check paths, and --ms-level if set)")

    print("Matching structures...")
    cov_rows = structural_coverage(structures, index)
    lookup = build_name_lookup(structures)

    print("Pass 2/2: name-recoverability...")
    name_rows = name_recoverability(spectra_stream(), lookup, args.fuzzy_threshold)

    os.makedirs(args.out, exist_ok=True)

    cov_path = os.path.join(args.out, "coverage_audit.csv")
    with open(cov_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(asdict(cov_rows[0])) + ["status"])
        writer.writeheader()
        for row in cov_rows:
            writer.writerow({**asdict(row), "status": row.status})

    name_path = os.path.join(args.out, "name_recoverability.csv")
    with open(name_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(asdict(name_rows[0])) + ["status"])
        writer.writeheader()
        for row in name_rows:
            writer.writerow({**asdict(row), "status": row.status})

    stats = {
        "provenance": args.provenance,
        "ms_level_filter": args.ms_level,
        "fuzzy_threshold": args.fuzzy_threshold,
        "spectral_index": index_stats(index),
        "structural_coverage": coverage_stats(cov_rows),
        "name_recoverability": name_stats(name_rows),
    }
    stats_path = os.path.join(args.out, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)

    report = qa_report(cov_rows, name_rows, index, args.provenance)
    qa_path = os.path.join(args.out, "qa_report.txt")
    with open(qa_path, "w", encoding="utf-8") as fh:
        fh.write(report)

    print()
    print(report)
    print(f"wrote {cov_path}\n      {name_path}\n      {stats_path}\n      {qa_path}")


if __name__ == "__main__":
    main()
