#!/usr/bin/env python3
"""Fetch the real bulk sources. Requires network access.

This script does NOT guess versioned filenames, because those rotate and a
silently-stale download is worse than an error. It prints the current
download entry point for each source, fetches what it can resolve, and logs
provenance (SHA-256, size, URL, date) for every file that lands on disk.

Source entry points, each verified reachable 2026-09-07:

  LOTUS      https://lotus.naturalproducts.net/download
             Structure-organism pairs, Wikidata-backed. SDF and database
             dumps; frozen versioned releases also on Zenodo.

  COCONUT    https://coconut.naturalproducts.net/download
             Bulk CSV / SDF / PostgreSQL dump. REST API documented at
             https://coconut.naturalproducts.net/api-documentation
             Per-record JSON-LD (useful for spot-checks, one record per call):
             https://coconut.naturalproducts.net/api/schemas/bioschemas/<CNP_ID>

  GNPS       https://external.gnps2.org/gnpslibrary
             All reference libraries. IMPORTANT: prefer ALL_GNPS.json or the
             .msp export over the .mgf export — the MGF format carries no
             InChIKey field, so MGF records cannot be joined on structure
             identity (see docs/FORMATS.md and docs/LIMITATIONS.md).

  MassBank   https://github.com/MassBank/MassBank-data/releases
             Versioned release archives with DOIs; one .txt record per
             spectrum under per-contributor directories. CC BY.

  MoNA       https://mona.fiehnlab.ucdavis.edu/downloads
             SDF / JSON / MSP bulk exports. Licenses vary PER RECORD; check
             before treating a MoNA record as open.

Usage:
  python scripts/01_fetch.py --list
  python scripts/01_fetch.py --url <direct-file-url> --dest data/raw/gnps/
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw")
PROVENANCE = os.path.join(RAW, "PROVENANCE.txt")

SOURCES = {
    "lotus": ("LOTUS", "https://lotus.naturalproducts.net/download",
              "SDF / DB dump; also frozen releases on Zenodo"),
    "coconut": ("COCONUT", "https://coconut.naturalproducts.net/download",
                "CSV / SDF / Postgres dump; REST API available"),
    "gnps": ("GNPS", "https://external.gnps2.org/gnpslibrary",
             "prefer ALL_GNPS.json or .msp; .mgf has NO InChIKey field"),
    "massbank": ("MassBank", "https://github.com/MassBank/MassBank-data/releases",
                 "versioned archives with DOIs; one .txt per record"),
    "mona": ("MoNA", "https://mona.fiehnlab.ucdavis.edu/downloads",
             "SDF / JSON / MSP; per-record licences vary"),
}


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def log_provenance(path: str, url: str, note: str = "") -> None:
    os.makedirs(os.path.dirname(PROVENANCE) or ".", exist_ok=True)
    line = " | ".join([
        datetime.date.today().isoformat(),
        os.path.relpath(path, ROOT),
        f"{os.path.getsize(path)} bytes",
        f"sha256:{sha256(path)}",
        url,
        note,
    ]).rstrip(" |")
    with open(PROVENANCE, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line)


def list_sources() -> None:
    print("SPECGAP source entry points (open each, copy the current bulk-file URL):\n")
    for key, (label, url, note) in SOURCES.items():
        print(f"  {key:<10} {label}")
        print(f"  {'':<10} {url}")
        print(f"  {'':<10} note: {note}\n")
    print("Then: python scripts/01_fetch.py --url <direct-file-url> --dest data/raw/<source>/")


def fetch(url: str, dest_dir: str, note: str) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    filename = os.path.basename(url.split("?")[0]) or "download.bin"
    dest = os.path.join(dest_dir, filename)
    print(f"fetching {url}\n      -> {dest}")
    urllib.request.urlretrieve(url, dest)  # noqa: S310 (user-supplied URL by design)
    log_provenance(dest, url, note)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print source entry points")
    ap.add_argument("--url", help="direct URL of a bulk file to download")
    ap.add_argument("--dest", default=os.path.join(RAW, "misc"))
    ap.add_argument("--note", default="", help="how this URL was discovered")
    args = ap.parse_args()

    if args.list or not args.url:
        list_sources()
        if not args.url:
            sys.exit(0)
    fetch(args.url, args.dest, args.note)


if __name__ == "__main__":
    main()
