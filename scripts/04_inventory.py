#!/usr/bin/env python3
"""Inventory a spectral library on its own — no structure database required.

Answers the questions that must be settled *before* any coverage number
means anything:

  - How many records does the library actually contain?
  - What fraction carry a usable structure identifier (InChIKey)? Records
    without one can never be assessed for structural coverage, so this is the
    ceiling on what any coverage audit can measure.
  - How many distinct compounds does that represent (unique InChIKeys, and
    unique skeletons ignoring stereochemistry)? Spectral libraries hold many
    spectra per compound — different adducts, collision energies, instruments
    — so record count badly overstates compound coverage.
  - For MassBank, what fraction is classed as natural product? That is the
    subset relevant to a LOTUS/COCONUT comparison.
  - What licences apply, per record?

Usage:
  python scripts/04_inventory.py --massbank <dir-or-file> --out data/processed
  python scripts/04_inventory.py --msp <file>:MoNA --out data/processed
  python scripts/04_inventory.py --mgf <file>:GNPS --json <file>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from specgap.identity import is_standard_inchikey, is_wellformed_inchikey, skeleton  # noqa: E402
from specgap.parsers import (  # noqa: E402
    is_natural_product, parse_gnps_json, parse_massbank_dir,
    parse_massbank_stream, parse_mgf, parse_msp,
)


def split_spec(value, default_label):
    """Split 'path:LABEL'. Windows-safe (see scripts/02_audit.py)."""
    head, sep, tail = value.rpartition(":")
    if not sep:
        return value, default_label
    if tail and not any(c in tail for c in "\\/") and head and not (
            len(head) == 1 and head.isalpha()):
        return head, tail
    return value, default_label


def load(args):
    entries = []
    if args.massbank:
        path = args.massbank
        print(f"reading MassBank from {path} ...", flush=True)
        if os.path.isdir(path):
            n_seen = 0
            for entry in parse_massbank_dir(path):
                entries.append(entry)
                n_seen += 1
                if n_seen % 5000 == 0:
                    print(f"  ... {n_seen:,} records parsed", flush=True)
            print(f"  done: {n_seen:,} MassBank records", flush=True)
        else:
            with open(path, encoding="utf-8", errors="replace") as fh:
                entries += list(parse_massbank_stream(fh))
    for item in args.msp or []:
        path, label = split_spec(item, "MoNA")
        print(f"reading MSP from {path} ({label}) ...")
        with open(path, encoding="utf-8", errors="replace") as fh:
            entries += list(parse_msp(fh, source=label))
    for item in args.mgf or []:
        path, label = split_spec(item, "GNPS")
        print(f"reading MGF from {path} ({label}) ...")
        with open(path, encoding="utf-8", errors="replace") as fh:
            entries += list(parse_mgf(fh, source=label))
    for item in args.json or []:
        path, _ = split_spec(item, "GNPS")
        print(f"reading GNPS JSON from {path} ...")
        with open(path, encoding="utf-8", errors="replace") as fh:
            entries += list(parse_gnps_json(fh))
    return entries


def pct(n, d):
    return round(100.0 * n / d, 2) if d else None


def inventory(entries):
    total = len(entries)
    keys, skels = set(), set()
    joinable = named = np_class = nonstandard = 0
    licenses, modes, sources, classes = Counter(), Counter(), Counter(), Counter()
    np_keys = set()

    for e in entries:
        sources[e.source] += 1
        key = (e.inchikey or "").strip().upper()
        if is_wellformed_inchikey(key):
            joinable += 1
            keys.add(key)
            skels.add(skeleton(key))
            if not is_standard_inchikey(key):
                nonstandard += 1
        if e.primary_name:
            named += 1
        if e.license:
            licenses[e.license] += 1
        if e.ion_mode:
            modes[e.ion_mode] += 1
        if e.compound_class:
            classes[e.compound_class.split(";")[0].strip()] += 1
        if is_natural_product(e):
            np_class += 1
            if is_wellformed_inchikey(key):
                np_keys.add(key)

    return {
        "n_records": total,
        "n_by_source": dict(sources),
        "joinability": {
            "n_joinable": joinable,
            "pct_joinable": pct(joinable, total),
            "note": ("records without a well-formed InChIKey cannot be assessed "
                     "for structural coverage; this is the ceiling on any "
                     "coverage measurement over this library"),
        },
        "distinct_compounds": {
            "n_unique_inchikeys": len(keys),
            "n_unique_skeletons": len(skels),
            "spectra_per_unique_compound": (
                round(joinable / len(keys), 2) if keys else None),
            "note": ("libraries hold many spectra per compound (adducts, "
                     "collision energies, instruments), so record count "
                     "overstates compound coverage"),
        },
        "nonstandard_inchikeys": nonstandard,
        "naming": {
            "n_with_name": named,
            "pct_with_name": pct(named, total),
        },
        "natural_products": {
            "n_records_classed_np": np_class,
            "pct_of_records": pct(np_class, total),
            "n_unique_np_inchikeys": len(np_keys),
            "note": ("MassBank CH$COMPOUND_CLASS only; GNPS and MoNA have no "
                     "equivalent field, so this is absent for those sources"),
        },
        "licenses": dict(licenses.most_common()),
        "ion_modes": dict(modes.most_common()),
        "top_compound_classes": dict(classes.most_common(10)),
    }


def render(inv, provenance):
    L = []
    L.append("SPECGAP spectral-library inventory")
    L.append("=" * 62)
    L.append(f"PROVENANCE: {provenance}")
    L.append("")
    L.append(f"Records:                 {inv['n_records']:,}")
    for src, n in inv["n_by_source"].items():
        L.append(f"  {src}: {n:,}")
    L.append("")
    j = inv["joinability"]
    L.append("JOINABILITY (ceiling on any coverage measurement)")
    L.append("-" * 62)
    L.append(f"  with usable InChIKey:  {j['n_joinable']:,} ({j['pct_joinable']}%)")
    L.append(f"  without:               {inv['n_records'] - j['n_joinable']:,}")
    L.append("")
    d = inv["distinct_compounds"]
    L.append("DISTINCT COMPOUNDS")
    L.append("-" * 62)
    L.append(f"  unique InChIKeys:      {d['n_unique_inchikeys']:,}")
    L.append(f"  unique skeletons:      {d['n_unique_skeletons']:,}  (stereochemistry ignored)")
    L.append(f"  spectra per compound:  {d['spectra_per_unique_compound']}")
    L.append(f"  non-standard InChIKeys: {inv['nonstandard_inchikeys']:,}")
    L.append("")
    n = inv["natural_products"]
    if n["n_records_classed_np"]:
        L.append("NATURAL PRODUCTS (the LOTUS/COCONUT-comparable subset)")
        L.append("-" * 62)
        L.append(f"  records classed NP:    {n['n_records_classed_np']:,} ({n['pct_of_records']}%)")
        L.append(f"  unique NP InChIKeys:   {n['n_unique_np_inchikeys']:,}")
        L.append("")
    L.append("NAMING")
    L.append("-" * 62)
    L.append(f"  with a compound name:  {inv['naming']['n_with_name']:,} "
             f"({inv['naming']['pct_with_name']}%)")
    if inv["licenses"]:
        L.append("")
        L.append("LICENCES (per record)")
        L.append("-" * 62)
        for lic, cnt in inv["licenses"].items():
            L.append(f"  {lic}: {cnt:,}")
    if inv["ion_modes"]:
        L.append("")
        L.append("ION MODES")
        L.append("-" * 62)
        for mode, cnt in inv["ion_modes"].items():
            L.append(f"  {mode}: {cnt:,}")
    if inv["top_compound_classes"]:
        L.append("")
        L.append("TOP COMPOUND CLASSES")
        L.append("-" * 62)
        for cls, cnt in inv["top_compound_classes"].items():
            L.append(f"  {cls}: {cnt:,}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--massbank", help="MassBank-data directory or concatenated file")
    ap.add_argument("--msp", nargs="*", help="MSP path[:LABEL]")
    ap.add_argument("--mgf", nargs="*", help="MGF path[:LABEL]")
    ap.add_argument("--json", nargs="*", help="GNPS JSON path")
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--provenance", default="")
    args = ap.parse_args()

    entries = load(args)
    if not entries:
        sys.exit("no records parsed — check the path and that it contains .txt records")

    provenance = args.provenance or f"massbank={args.massbank} msp={args.msp} mgf={args.mgf}"
    inv = inventory(entries)
    report = render(inv, provenance)
    print()
    print(report)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "inventory.json"), "w", encoding="utf-8") as fh:
        json.dump({"provenance": provenance, **inv}, fh, indent=2)
    with open(os.path.join(args.out, "inventory_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"wrote {args.out}/inventory.json and inventory_report.txt")


if __name__ == "__main__":
    main()
