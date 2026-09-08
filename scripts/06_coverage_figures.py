import json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

s = json.load(open('data/processed/coconut_massbank_audit_2026.09.json'))
c = s['structural_coverage']; n = s['name_recoverability']
tot = c['n_structures_joinable']
os.makedirs('paper/figures', exist_ok=True)

# Fig 1: the gap, exact vs skeleton
fig, ax = plt.subplots(figsize=(7.5, 3.4))
exact = c['exact_inchikey']['n_covered']; skel = c['skeleton']['n_covered']
ax.barh(['Skeleton\nmatch', 'Exact\nInChIKey'], [skel, exact],
        color=['#3b8a6e', '#2a5f8f'])
ax.barh(['Skeleton\nmatch', 'Exact\nInChIKey'], [tot-skel, tot-exact],
        left=[skel, exact], color='#d9d9d9')
for i, v in enumerate([skel, exact]):
    ax.text(tot*0.012, i, f"  {v:,} covered ({100*v/tot:.2f}%)",
            va='center', fontsize=10, color='white', fontweight='bold')
ax.text(tot*0.55, 0.5, f"{tot-skel:,}–{tot-exact:,} uncovered",
        va='center', ha='center', fontsize=10, color='#555')
ax.set_xlim(0, tot); ax.set_xlabel('COCONUT structures (n = %s)' % f"{tot:,}")
ax.set_title('Natural-product structure space with a MassBank spectrum', pad=10)
ax.spines[['top','right','left']].set_visible(False); ax.set_xticks([])
fig.text(0.5, 0.02, s['provenance'], ha='center', fontsize=7, color='dimgray')
fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig('paper/figures/coverage_gap.png', dpi=150); plt.close(fig)

# Fig 2: the two layers side by side
fig, ax = plt.subplots(figsize=(6.2, 4.2))
vals = [c['skeleton']['pct_of_joinable'], n['pct_of_assessable']]
bars = ax.bar(['Structural coverage\n(skeleton level)', 'Name-recoverability\n(of assessable)'],
              vals, color=['#a33d3d', '#2a6f4e'], width=0.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+2, f"{v}%", ha='center', fontsize=13, fontweight='bold')
ax.set_ylim(0, 100); ax.set_ylabel('%')
ax.set_title('Coverage is the constraint, not naming', pad=10)
ax.spines[['top','right']].set_visible(False)
fig.text(0.5, 0.02, 'COCONUT 09-2026 × MassBank 2026.03. Denominators differ; see docs/COVERAGE_AUDIT.md',
         ha='center', fontsize=7, color='dimgray')
fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig('paper/figures/coverage_vs_naming.png', dpi=150); plt.close(fig)
print("wrote paper/figures/coverage_gap.png and coverage_vs_naming.png")
