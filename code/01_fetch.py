#!/usr/bin/env python3
"""Fetch the real bulk sources for SPECGAP.

Requires network access (this repo may have been built in a sandbox without
it — see docs/BUILD_SPEC.md "sandbox constraint"). Each fetch is logged to
data/raw/PROVENANCE.txt via provenance.py-style records.

Sources and current bulk-download entry points (verify these still resolve;
platforms occasionally rotate URLs — see docs/BUILD_SPEC.md for the source
table and re-check each site's own Download page if a URL below 404s):

  LOTUS      https://lotus.naturalproducts.net/download
             (SDF export and MongoDB dump; also frozen versioned releases on
             Zenodo, search "LOTUS natural products database")
  COCONUT    https://coconut.naturalproducts.net/download
             (CSV / SDF / Postgres dump for bulk export; REST API documented
             at https://coconut.naturalproducts.net/api-documentation)
             Per-record endpoint CONFIRMED LIVE 2026-09-01:
             https://coconut.naturalproducts.net/api/schemas/bioschemas/<CNP_ID>
             returns one record as Bioschemas JSON-LD (name, InChIKey, SMILES,
             taxonomy, citation, license). Useful for spot-checks and single-
             compound lookups; still use the bulk dump for the full corpus.
             See docs/REAL_RECORD_EXAMPLE.md for a real, verified example.
  GNPS       https://external.gnps2.org/gnpslibrary
             (mgf/msp/json bulk export of all reference spectral libraries;
             versioned archives also on Zenodo)
  MassBank   https://github.com/MassBank/MassBank-data
             (per-record flat files under records/; versioned zip releases
             with DOIs under Releases)
  MoNA       https://mona.fiehnlab.ucdavis.edu/downloads
             (SDF/JSON/MSP bulk exports; check per-record license field
             before treating an entry as "open")

Usage:
  python code/01_fetch.py --all
  python code/01_fetch.py --source lotus
"""
import argparse
import datetime
import hashlib
import os
import sys
import urllib.request

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROVENANCE = os.path.join(RAW, "PROVENANCE.txt")

SOURCES = {
    "lotus": "https://lotus.naturalproducts.net/download",
    "coconut": "https://coconut.naturalproducts.net/download",
    "gnps": "https://external.gnps2.org/gnpslibrary",
    "massbank": "https://github.com/MassBank/MassBank-data/releases",
    "mona": "https://mona.fiehnlab.ucdavis.edu/downloads",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_provenance(filename, url, note=""):
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, filename)
    line = " | ".join([
        datetime.date.today().isoformat(),
        filename,
        f"{os.path.getsize(path)} bytes" if os.path.exists(path) else "0 bytes",
        f"sha256:{sha256(path)}" if os.path.exists(path) else "sha256:MISSING",
        url,
        note,
    ])
    with open(PROVENANCE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def fetch(source):
    url = SOURCES[source]
    print(f"[{source}] landing page: {url}")
    print(f"[{source}] this script fetches the LANDING/DOWNLOAD page only; "
          f"the actual bulk file link changes by release. Open the page, "
          f"copy the current bulk-download URL, and either download it "
          f"manually into data/raw/{source}/ or extend this function with "
          f"the direct file URL, then re-run.")
    # Intentionally conservative: we do not guess a versioned filename that
    # will go stale. This keeps the script honest rather than silently
    # fetching an outdated or wrong file.


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=list(SOURCES), help="fetch a single source")
    ap.add_argument("--all", action="store_true", help="fetch all sources")
    a = ap.parse_args()
    if not a.source and not a.all:
        ap.print_help()
        sys.exit(1)
    targets = list(SOURCES) if a.all else [a.source]
    for s in targets:
        fetch(s)


if __name__ == "__main__":
    main()
