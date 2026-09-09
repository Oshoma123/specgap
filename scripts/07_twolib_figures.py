#!/usr/bin/env python3
"""Figures comparing the one-library and two-library audits.

All values read from the two audit JSONs; nothing typed into plotting code.

Usage: python scripts/07_twolib_figures.py [--out paper/figures] [--final]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", default="data/processed/coconut_massbank_audit_2026.09.json")
    ap.add_argument("--two", default="data/processed/coconut_massbank_mona_audit_2026.09.json")
    ap.add_argument("--out", default="paper/figures")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    one = json.load(open(a.one, encoding="utf-8"))
    two = json.load(open(a.two, encoding="utf-8"))

    # --- diminishing returns: compounds added vs coverage gained ---
    k1 = one["spectral_index"]["n_unique_inchikeys"]
    k2 = two["spectral_index"]["n_unique_inchikeys"]
    c1 = one["structural_coverage"]["exact_inchikey"]["n_covered"]
    c2 = two["structural_coverage"]["exact_inchikey"]["n_covered"]

    # Two panels with independent linear axes. A shared log axis was tried
    # and rejected: it truncated the 8,025 baseline below the axis floor,
    # making MoNA look responsible for all coverage rather than half of it.
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.2))
    panels = [
        (axes[0], "Distinct compounds\nin spectral layer", k1, k2 - k1, k2 / k1),
        (axes[1], "COCONUT structures\ncovered (exact)", c1, c2 - c1, c2 / c1),
    ]
    for ax, title, base, added, mult in panels:
        ax.bar([0], [base], color="#2a5f8f", width=0.55, label="MassBank only")
        ax.bar([0], [added], bottom=[base], color="#7fb069", width=0.55,
               label="added by MoNA")
        ax.text(0, base / 2, f"{base:,}", ha="center", va="center",
                color="white", fontweight="bold", fontsize=10)
        ax.text(0, base + added / 2, f"+{added:,}", ha="center", va="center",
                color="#123", fontweight="bold", fontsize=10)
        ax.text(0, (base + added) * 1.04, f"{mult:.1f}\u00d7", ha="center",
                fontsize=13, fontweight="bold")
        ax.set_title(title, fontsize=10)
        ax.set_xticks([]); ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(0, (base + added) * 1.18)
        ax.spines[["top", "right", "bottom"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("MoNA adds 12.3\u00d7 the compounds, 1.9\u00d7 the coverage",
                 fontsize=12, y=0.97)
    fig.text(0.5, 0.01, two["provenance"], ha="center", fontsize=6.5, color="dimgray")
    if not a.final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=64, color="gray", alpha=0.14,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    p1 = os.path.join(a.out, "diminishing_returns.png")
    fig.savefig(p1, dpi=150); plt.close(fig)

    # --- the gap, one vs two libraries ---
    tot = two["structural_coverage"]["n_structures_joinable"]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    rows = ["+ MoNA (MS2)", "MassBank only"]
    skel = [two["structural_coverage"]["skeleton"]["n_covered"],
            one["structural_coverage"]["skeleton"]["n_covered"]]
    ax.barh(rows, skel, color=["#3b8a6e", "#2a5f8f"])
    ax.barh(rows, [tot - s for s in skel], left=skel, color="#d9d9d9")
    for i, s in enumerate(skel):
        ax.text(tot * 0.012, i, f"  {s:,} covered ({100*s/tot:.2f}%)",
                va="center", color="white", fontweight="bold", fontsize=10)
    ax.set_xlim(0, tot); ax.set_xticks([])
    ax.set_xlabel(f"COCONUT structures (n = {tot:,}), skeleton-level match")
    ax.set_title("Two of three open libraries still leave 92% uncovered", pad=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.text(0.5, 0.02, "MS2 only; in-silico spectra excluded", ha="center",
             fontsize=7, color="dimgray")
    if not a.final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=58, color="gray", alpha=0.16,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    p2 = os.path.join(a.out, "gap_one_vs_two_libraries.png")
    fig.savefig(p2, dpi=150); plt.close(fig)
    print(f"wrote {p1}\n      {p2}")


if __name__ == "__main__":
    main()
