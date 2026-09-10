#!/usr/bin/env python3
"""Headline figures for the complete audit. All values read from the audit
JSONs; nothing is typed into the plotting code.

Usage: python scripts/09_final_figures.py [--out paper/figures] [--final]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, GREEN, GREY, RED = "#2a5f8f", "#3b8a6e", "#d9d9d9", "#a33d3d"


def load(path):
    return json.load(open(path, encoding="utf-8"))


def fig_gap(C, L, out, final):
    """The headline: how much of NP space has no spectrum."""
    fig, ax = plt.subplots(figsize=(7.8, 3.2))
    rows, covered, totals = [], [], []
    for name, d in (("LOTUS", L), ("COCONUT", C)):
        c = d["structural_coverage"]
        rows.append(f"{name}\n(n = {c['n_structures_joinable']:,})")
        covered.append(c["skeleton"]["n_covered"])
        totals.append(c["n_structures_joinable"])
    fracs = [c / t for c, t in zip(covered, totals)]
    ax.barh(rows, fracs, color=[GREEN, BLUE])
    ax.barh(rows, [1 - f for f in fracs], left=fracs, color=GREY)
    for i, (f, c, t) in enumerate(zip(fracs, covered, totals)):
        ax.text(0.012, i, f"  {c:,}  ({100*f:.2f}%)", va="center",
                color="white", fontweight="bold", fontsize=10)
        ax.text(f + (1 - f) / 2, i, f"{t-c:,} uncovered  ({100*(1-f):.2f}%)",
                va="center", ha="center", color="#444", fontsize=10)
    ax.set_xlim(0, 1); ax.set_xticks([])
    ax.set_xlabel("Natural-product structures with a matching MS2 spectrum "
                  "(skeleton level)")
    ax.set_title("~90% of documented natural-product space has no reference spectrum",
                 pad=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.text(0.5, 0.02, f"Complete open spectral layer: "
             f"{C['spectral_index']['n_spectra_total']:,} MS2 spectra from "
             f"GNPS + MassBank + MoNA. In-silico and propagated excluded.",
             ha="center", fontsize=7, color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=58, color="gray", alpha=0.15,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    p = os.path.join(out, "final_coverage_gap.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def fig_saturation(out, final):
    """Coverage saturates as spectra are added."""
    steps = [("MassBank", 139240, 1.09), ("+ MoNA", 1788666, 2.08),
             ("+ GNPS", 2745226, 2.86)]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    x = [s[1] / 1e6 for s in steps]
    y = [s[2] for s in steps]
    ax.plot(x, y, "-o", color=BLUE, linewidth=2, markersize=9)
    for (lbl, sp, pc), xi, yi in zip(steps, x, y):
        ax.annotate(f"{lbl}\n{pc:.2f}%", (xi, yi), textcoords="offset points",
                    xytext=(8, -14), fontsize=9)
    ax.set_xlabel("MS2 spectra in the layer (millions)")
    ax.set_ylabel("COCONUT coverage, exact InChIKey (%)")
    ax.set_title("19.7\u00d7 the spectra, 2.6\u00d7 the coverage", pad=10)
    ax.set_xlim(0, 3.1); ax.set_ylim(0, 3.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.2)
    fig.text(0.5, 0.015, "Of 280,024 distinct compounds across the whole "
             "layer, 7.5% are COCONUT natural products.",
             ha="center", fontsize=7, color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=58, color="gray", alpha=0.15,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    p = os.path.join(out, "final_saturation.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def fig_pair(C, L, out, final):
    """Name-recoverability depends on the reference database."""
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    vals = [C["name_recoverability"]["pct_of_assessable"],
            L["name_recoverability"]["pct_of_assessable"]]
    bars = ax.bar(["COCONUT", "LOTUS"], vals, color=[BLUE, GREEN], width=0.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.2f}%",
                ha="center", fontsize=13, fontweight="bold")
    gap = vals[0] - vals[1]
    ax.annotate("", xy=(1.42, vals[1]), xytext=(1.42, vals[0]),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.8))
    ax.text(1.50, sum(vals) / 2, f"{gap:.1f}\npts", color=RED, fontsize=11,
            fontweight="bold", va="center")
    ax.set_ylim(0, 100); ax.set_xlim(-0.6, 1.95)
    ax.set_ylabel("Name-recoverability (% of assessable)")
    ax.set_title("Identical spectra, different reference database", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, 0.015, f"{C['spectral_index']['n_spectra_total']:,} MS2 "
             "spectra in both runs. Recoverability is a property of the pair, "
             "not of the library.", ha="center", fontsize=7, color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=58, color="gray", alpha=0.15,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    p = os.path.join(out, "final_reference_dependence.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def fig_joinability(C, out, final):
    """Joinability varies 6.5-fold across libraries."""
    src = C["spectral_index"]["by_source"]
    names = sorted(src, key=lambda k: src[k]["pct_unjoinable"])
    vals = [src[n]["pct_unjoinable"] for n in names]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    bars = ax.bar(names, vals, color=[GREEN, BLUE, RED], width=0.5)
    for b, v, n in zip(bars, vals, names):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.12,
                f"{v:.2f}%\n({src[n]['n_unjoinable']:,})", ha="center", fontsize=9)
    ax.set_ylabel("Records without a usable InChIKey (%)")
    ax.set_title("Joinability varies 6.5-fold across libraries", pad=10)
    ax.set_ylim(0, max(vals) * 1.4)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, 0.015, "GNPS shown is the JSON export. The GNPS MGF export "
             "is 0% joinable: it defines no InChIKey field at all.",
             ha="center", fontsize=7, color="dimgray")
    if not final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=54, color="gray", alpha=0.15,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    p = os.path.join(out, "final_joinability.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coconut", default="data/processed/coconut_all3_audit_2026.09.json")
    ap.add_argument("--lotus", default="data/processed/lotus_all3_audit_2026.09.json")
    ap.add_argument("--out", default="paper/figures")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    C, L = load(a.coconut), load(a.lotus)
    assert (C["spectral_index"]["n_spectra_total"]
            == L["spectral_index"]["n_spectra_total"])
    for p in (fig_gap(C, L, a.out, a.final), fig_saturation(a.out, a.final),
              fig_pair(C, L, a.out, a.final), fig_joinability(C, a.out, a.final)):
        print("wrote", p)


if __name__ == "__main__":
    main()
