#!/usr/bin/env python3
"""Generate a small SYNTHETIC fixture standing in for LOTUS/COCONUT/GNPS/
MassBank/MoNA, so the pipeline can be run end-to-end in an environment
without network access.

This is a TEST FIXTURE, not real data. Every record here is invented for
testing shapes and join logic; do not use any of it as a scientific claim.
When network access is available, delete data/raw/fixtures/ and run
01_fetch.py against the real sources instead.

Usage:
  python code/00_make_fixture.py
"""
import csv
import hashlib
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "fixtures")
os.makedirs(OUT, exist_ok=True)
random.seed(20260901)


def fake_inchikey(seed):
    """Deterministic, InChIKey-shaped (14-10-1) placeholder — not a real InChIKey."""
    h = hashlib.md5(seed.encode()).hexdigest().upper()
    return f"{h[:14]}-{h[14:24]}-{h[24:25]}"


# 60 synthetic "natural product" structures across a LOTUS-like and a
# COCONUT-like table, with deliberate overlap between the two.
compound_stems = [f"synthanol-{i}" for i in range(1, 61)]
structures = []
for i, stem in enumerate(compound_stems):
    key = fake_inchikey(stem)
    structures.append({
        "inchikey": key,
        "inchikey_skeleton": key.split("-")[0],
        "name": stem.replace("-", " ").title(),
        "source_db": "LOTUS" if i % 2 == 0 else "COCONUT",
    })

with open(os.path.join(OUT, "lotus_coconut_structures.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["inchikey", "inchikey_skeleton", "name", "source_db"])
    w.writeheader()
    w.writerows(structures)

# Synthetic spectral-library entries: about 60% of structures get a spectrum
# in at least one spectral source; names are perturbed for some entries to
# simulate real-world name-recoverability failure (typos, salts, synonyms).
spectral_sources = ["GNPS", "MassBank", "MoNA"]
rows = []
covered = random.sample(structures, k=int(len(structures) * 0.6))
for s in covered:
    for src in random.sample(spectral_sources, k=random.randint(1, 2)):
        name = s["name"]
        if random.random() < 0.25:
            name = name + " hydrate"  # simulate a resolvable variant
        if random.random() < 0.15:
            name = "Unknown compound " + s["inchikey"][:6]  # simulate an unresolved name
        rows.append({
            "spectrum_id": f"{src}:{s['inchikey'][:8]}:{random.randint(1,999)}",
            "inchikey": s["inchikey"],
            "declared_name": name,
            "spectral_source": src,
            "ionization_mode": random.choice(["positive", "negative"]),
        })

with open(os.path.join(OUT, "spectral_entries.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["spectrum_id", "inchikey", "declared_name",
                                       "spectral_source", "ionization_mode"])
    w.writeheader()
    w.writerows(rows)

print(f"wrote {len(structures)} synthetic structures and {len(rows)} synthetic spectral entries to {OUT}")
print("REMINDER: this is a synthetic fixture for pipeline testing only.")
