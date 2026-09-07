#!/usr/bin/env python3
"""Build paper/figures/coverage_by_source.png from data/processed/stats.json.

Carries a visible DRAFT watermark until run with --final (see
docs/BUILD_SPEC.md on draft stamping). Uses a perceptually-uniform colormap
per the dataviz convention referenced in build-standards.md.

Usage:
  python code/04_figures.py [--final]
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
STATS = os.path.join(ROOT, "data", "processed", "stats.json")
OUT = os.path.join(ROOT, "paper", "figures")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true", help="remove the DRAFT watermark")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    with open(STATS) as f:
        stats = json.load(f)

    by_source = stats["name_recoverability"]["by_spectral_source"]
    sources = sorted(by_source)
    values = [by_source[s]["recovered_pct"] for s in sources]

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = plt.cm.viridis([0.25, 0.55, 0.85][:len(sources)])
    ax.bar(sources, values, color=colors)
    ax.set_ylabel("Name-recoverability (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Name-recoverability by spectral source")
    for i, v in enumerate(values):
        ax.text(i, v + 2, f"{v}%", ha="center")

    if not a.final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=60, color="gray", alpha=0.25,
                  ha="center", va="center", rotation=30)
        fig.text(0.5, 0.02, "Synthetic fixture run \u2014 not real coverage data",
                  fontsize=8, color="firebrick", ha="center")

    fig.tight_layout()
    path = os.path.join(OUT, "coverage_by_source.png")
    fig.savefig(path, dpi=150)
    print(f"wrote {path} (draft={not a.final})")


if __name__ == "__main__":
    main()
