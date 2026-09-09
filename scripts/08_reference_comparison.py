#!/usr/bin/env python3
"""Figure: the same spectra audited against two reference databases.

All values read from the two audit JSONs. The point of the figure is that
the spectral side is identical between them, so every difference shown is
attributable to the reference database alone.

Usage: python scripts/08_reference_comparison.py [--out paper/figures] [--final]
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
    ap.add_argument("--coconut", default="data/processed/coconut_massbank_mona_audit_2026.09.json")
    ap.add_argument("--lotus", default="data/processed/lotus_massbank_mona_audit_2026.09.json")
    ap.add_argument("--out", default="paper/figures")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    C = json.load(open(a.coconut, encoding="utf-8"))
    L = json.load(open(a.lotus, encoding="utf-8"))
    assert (C["spectral_index"]["n_spectra_total"]
            == L["spectral_index"]["n_spectra_total"]), \
        "runs must share the same spectral side for this comparison to hold"
    n_spectra = C["spectral_index"]["n_spectra_total"]

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 4.0))
    blue, green = "#2a5f8f", "#3b8a6e"

    def panel(ax, title, cval, lval, fmt="{:.2f}%", ylim=None):
        bars = ax.bar(["COCONUT", "LOTUS"], [cval, lval], color=[blue, green],
                      width=0.55)
        for b, v in zip(bars, [cval, lval]):
            ax.text(b.get_x() + b.get_width() / 2, v + (ylim or max(cval, lval)) * 0.03,
                    fmt.format(v), ha="center", fontsize=11, fontweight="bold")
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, (ylim or max(cval, lval) * 1.28))
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)

    panel(axes[0], "Structural coverage\n(exact InChIKey)",
          C["structural_coverage"]["exact_inchikey"]["pct_of_joinable"],
          L["structural_coverage"]["exact_inchikey"]["pct_of_joinable"])
    panel(axes[1], "Structural coverage\n(skeleton)",
          C["structural_coverage"]["skeleton"]["pct_of_joinable"],
          L["structural_coverage"]["skeleton"]["pct_of_joinable"])
    panel(axes[2], "Name-recoverability\n(of assessable)",
          C["name_recoverability"]["pct_of_assessable"],
          L["name_recoverability"]["pct_of_assessable"], ylim=100)

    # arrow offset to the right of the bars so it cannot overlap the labels
    lo = L["name_recoverability"]["pct_of_assessable"]
    hi = C["name_recoverability"]["pct_of_assessable"]
    axes[2].annotate("", xy=(1.42, lo), xytext=(1.42, hi),
                     arrowprops=dict(arrowstyle="<->", color="firebrick", lw=1.6))
    axes[2].text(1.50, (hi + lo) / 2, f"{hi - lo:.0f}\npts", color="firebrick",
                 fontsize=10, fontweight="bold", va="center", ha="left")
    axes[2].set_xlim(-0.6, 1.9)

    fig.suptitle(f"Identical spectra (n = {n_spectra:,} MS2), two reference databases",
                 fontsize=12, y=0.98)
    fig.text(0.5, 0.015,
             "MassBank 2026.03 + MoNA experimental, MS2 only. "
             "Every difference shown is attributable to the reference database.",
             ha="center", fontsize=7, color="dimgray")
    if not a.final:
        fig.text(0.5, 0.5, "DRAFT", fontsize=62, color="gray", alpha=0.14,
                 ha="center", va="center", rotation=28)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    path = os.path.join(a.out, "reference_database_dependence.png")
    fig.savefig(path, dpi=150); plt.close(fig)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
