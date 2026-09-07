#!/usr/bin/env python3
"""Build figures from data/processed/stats.json.

Every number is read from the stats file — nothing is typed into the plotting
code — so figures cannot drift from the data they claim to show.

The default figure is the joinability breakdown rather than a single coverage
bar, because 'what fraction of each library can even be assessed' is the
first thing a reader needs in order to interpret any coverage number.

Usage:
  python scripts/03_figures.py [--stats data/processed/stats.json]
                               [--out paper/figures] [--final]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def joinability_figure(stats: dict, out_dir: str, final: bool) -> str:
    by_source = stats["spectral_index"]["by_source"]
    sources = sorted(by_source)
    totals = [by_source[s]["n_total"] for s in sources]
    unjoinable = [by_source[s]["n_unjoinable"] for s in sources]
    joinable = [t - u for t, u in zip(totals, unjoinable)]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    colors = plt.cm.viridis([0.7, 0.25])
    ax.bar(sources, joinable, label="joinable (has InChIKey)", color=colors[0])
    ax.bar(sources, unjoinable, bottom=joinable,
           label="unjoinable (no usable structure key)", color=colors[1])

    for i, (j, u, t) in enumerate(zip(joinable, unjoinable, totals)):
        if t:
            ax.text(i, t, f"{100 * u / t:.0f}% unjoinable",
                    ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("Spectra")
    ax.set_title("Spectral records assessable for structure-based coverage")
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    provenance = stats.get("provenance", "unspecified provenance")
    fig.text(0.5, 0.005, f"Source: {provenance}", ha="center", fontsize=7,
             color="dimgray")

    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=70, color="gray", alpha=0.18,
                 ha="center", va="center", rotation=28)

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(out_dir, "joinability_by_source.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def coverage_figure(stats: dict, out_dir: str, final: bool) -> str:
    cov = stats["structural_coverage"]
    labels = ["exact InChIKey", "skeleton"]
    values = [cov["exact_inchikey"]["pct_of_joinable"] or 0,
              cov["skeleton"]["pct_of_joinable"] or 0]

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.bar(labels, values, color=plt.cm.viridis([0.35, 0.65]))
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of joinable structures covered")
    ax.set_title("Structural coverage")
    for i, v in enumerate(values):
        ax.text(i, v + 1.5, f"{v}%", ha="center")
    ax.spines[["top", "right"]].set_visible(False)

    fig.text(0.5, 0.005,
             f"Denominator: {cov['n_structures_joinable']} joinable of "
             f"{cov['n_structures_total']} structures. "
             f"{stats.get('provenance', '')}",
             ha="center", fontsize=7, color="dimgray", wrap=True)

    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=64, color="gray", alpha=0.18,
                 ha="center", va="center", rotation=28)

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = os.path.join(out_dir, "structural_coverage.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stats", default="data/processed/stats.json")
    ap.add_argument("--out", default="paper/figures")
    ap.add_argument("--final", action="store_true", help="remove the DRAFT watermark")
    args = ap.parse_args()

    with open(args.stats, encoding="utf-8") as fh:
        stats = json.load(fh)
    os.makedirs(args.out, exist_ok=True)

    for path in (joinability_figure(stats, args.out, args.final),
                 coverage_figure(stats, args.out, args.final)):
        print(f"wrote {path} (draft={not args.final})")


if __name__ == "__main__":
    main()
