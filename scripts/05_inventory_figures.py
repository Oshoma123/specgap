#!/usr/bin/env python3
"""Figures for a spectral-library inventory, built from inventory JSON.

Every value is read from the stats file; nothing is typed into the plotting
code, so figures cannot drift from the data they claim to show.

Usage:
  python scripts/05_inventory_figures.py \
      --inventory data/processed/massbank_inventory_2026.03.json \
      --out paper/figures [--final]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Licences that permit commercial reuse. dl-de/by-2-0 is the German
# open-government data licence: attribution-style, commercially permissive.
COMMERCIAL_OK = {"CC BY", "CC BY-SA", "CC0", "dl-de/by-2-0"}


def licence_figure(inv: dict, out_dir: str, final: bool) -> str:
    lic = inv["licenses"]
    names = list(lic)
    values = [lic[k] for k in names]
    total = sum(values)
    colors = ["#2a6f4e" if n in COMMERCIAL_OK else "#a33d3d" for n in names]

    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.barh(names[::-1], values[::-1], color=colors[::-1])
    ax.invert_yaxis()
    ax.set_xlabel("Records")
    ax.set_title("MassBank licences are not uniform (release 2026.03)", pad=26)

    for bar, value in zip(bars, values[::-1]):
        ax.text(value + total * 0.006, bar.get_y() + bar.get_height() / 2,
                f"{value:,} ({100 * value / total:.1f}%)",
                va="center", fontsize=8)

    restricted = sum(v for k, v in lic.items() if k not in COMMERCIAL_OK)
    ax.set_xlim(0, max(values) * 1.28)
    ax.spines[["top", "right"]].set_visible(False)

    handles = [plt.Rectangle((0, 0), 1, 1, color="#2a6f4e"),
               plt.Rectangle((0, 0), 1, 1, color="#a33d3d")]
    ax.legend(handles,
              [f"commercial reuse permitted ({100 * (total - restricted) / total:.1f}%)",
               f"non-commercial restricted ({100 * restricted / total:.1f}%)"],
              loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2,
              fontsize=8, frameon=False)

    fig.text(0.5, 0.01, f"n = {total:,} records. {inv.get('provenance','')}",
             ha="center", fontsize=7, color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=66, color="gray", alpha=0.16,
                 ha="center", va="center", rotation=28)

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    path = os.path.join(out_dir, "massbank_licences.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def scale_figure(inv: dict, out_dir: str, final: bool) -> str:
    """Records vs distinct compounds vs distinct skeletons."""
    d = inv["distinct_compounds"]
    labels = ["Records\n(spectra)", "Distinct compounds\n(InChIKey)",
              "Distinct skeletons\n(no stereochemistry)"]
    values = [inv["n_records"], d["n_unique_inchikeys"], d["n_unique_skeletons"]]

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    bars = ax.bar(labels, values, color=plt.cm.viridis([0.2, 0.5, 0.75]))
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.02,
                f"{value:,}", ha="center", fontsize=10)
    ax.set_ylabel("Count")
    ax.set_title(f"Record count overstates chemical coverage "
                 f"{d['spectra_per_unique_compound']}\u00d7")
    ax.set_ylim(0, max(values) * 1.15)
    ax.spines[["top", "right"]].set_visible(False)

    fig.text(0.5, 0.01, inv.get("provenance", ""), ha="center", fontsize=7,
             color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=62, color="gray", alpha=0.16,
                 ha="center", va="center", rotation=28)

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    path = os.path.join(out_dir, "massbank_scale.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", default="data/processed/massbank_inventory_2026.03.json")
    ap.add_argument("--out", default="paper/figures")
    ap.add_argument("--final", action="store_true")
    args = ap.parse_args()

    with open(args.inventory, encoding="utf-8") as fh:
        inv = json.load(fh)
    os.makedirs(args.out, exist_ok=True)

    for path in (licence_figure(inv, args.out, args.final),
                 scale_figure(inv, args.out, args.final)):
        print(f"wrote {path} (draft={not args.final})")


if __name__ == "__main__":
    main()
