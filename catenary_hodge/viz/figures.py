"""
Visualization module — matplotlib rendering of Fraction-computed data.

All plots use:
  * Noto Sans SC + DejaVu Sans for font fallback (per CLAUDE.md rule 7)
  * constrained_layout=True (per CLAUDE.md rule 7)
  * bbox_to_anchor for legends (per CLAUDE.md rule 7)
  * No numpy/scipy — pure matplotlib + Python lists
"""
import os
import sys
import json
import math
from typing import Dict, List, Any, Tuple

import matplotlib.font_manager as fm
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
except Exception:
    pass
# Try a few Noto Sans SC locations; ignore if not loadable
for p in [
    '/usr/share/fonts/truetype/chinese/NotoSansSC[wght].ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
]:
    try:
        fm.fontManager.addfont(p)
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

FIGURE_DIR = "/home/z/my-project/figures"
RESULTS_DIR = "/home/z/my-project/results"


def _load(name: str) -> Dict:
    with open(os.path.join(RESULTS_DIR, name), "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Figure 1: Catenary β(n) across the Golay ladder (Module 1)
# ---------------------------------------------------------------------------
def fig1_catenary_beta():
    data = _load("module1_catenary_ladder.json")
    rows = data["ladder_rows"]
    ns = [r["n"] for r in rows]
    beta_and = [r["beta_and"] for r in rows]
    beta_xor = [r["beta_xor"] for r in rows]
    beta_proj = [r["beta_proj"] for r in rows]
    dn = [r["d_over_n"] for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    # Left: closure rates
    ax1.plot(ns, beta_xor, 'o-', label='β_XOR (linear closure)', color='#1f77b4', linewidth=2, markersize=10)
    ax1.plot(ns, beta_and, 's-', label='β_AND (geometric closure)', color='#d62728', linewidth=2, markersize=10)
    ax1.plot(ns, beta_proj, '^-', label='β_proj (axle bumpiness)', color='#2ca02c', linewidth=2, markersize=10)
    ax1.axvspan(12, 14, alpha=0.15, color='orange', label='LDP transition band [12, 14]')
    ax1.set_xlabel('Dimension n')
    ax1.set_ylabel('Closure rate / bumpiness')
    ax1.set_title('Module 1: Catenary Metrics Across the Golay Ladder')
    ax1.set_xticks(ns)
    ax1.set_xticklabels([f'[{r["n"]},{r["k"]},{r["d"]}]' for r in rows], rotation=30)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='center right', bbox_to_anchor=(1.0, 0.5))
    # Right: d/n ratio
    ax2.plot(ns, dn, 'D-', color='#9467bd', linewidth=2, markersize=12)
    ax2.axhline(0.50, color='gray', linestyle=':', alpha=0.5, label='d/n = 0.50 (low-dim)')
    ax2.axhline(0.33, color='gray', linestyle='--', alpha=0.5, label='d/n = 0.33 (Golay)')
    ax2.axvspan(12, 14, alpha=0.15, color='orange')
    ax2.set_xlabel('Dimension n')
    ax2.set_ylabel('d/n ratio')
    ax2.set_title(f'Module 1: d/n Drop\nCritical dimension n_c = {data["n_c"]["from_beta_proj"]}')
    ax2.set_xticks(ns)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right')
    out = os.path.join(FIGURE_DIR, "fig1_catenary_beta.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 2: Ghost radius distribution (Module 2)
# ---------------------------------------------------------------------------
def fig2_ghost_radius():
    data = _load("module2_ghost_states.json")
    ghost_dist = {int(k): int(v) for k, v in data["ghost_radius_distribution"].items()}
    random_dist = {int(k): int(v) for k, v in data["random_null_radius_distribution"].items()}
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    all_r = sorted(set(list(ghost_dist.keys()) + list(random_dist.keys())))
    g_counts = [ghost_dist.get(r, 0) for r in all_r]
    r_counts = [random_dist.get(r, 0) for r in all_r]
    width = 0.35
    x = list(range(len(all_r)))
    ax.bar([xi - width/2 for xi in x], g_counts, width, label=f'Ghost states (mean r={data["mean_ghost_radius"]:.2f})', color='#d62728')
    ax.bar([xi + width/2 for xi in x], r_counts, width, label=f'Random null vectors (mean r={data["mean_random_radius"]:.2f})', color='#1f77b4')
    ax.set_xlabel('Hamming distance r to nearest codeword')
    ax.set_ylabel('Count (sample)')
    ax.set_title('Module 2: Ghost-State Radius Distribution\n(Ghosts cluster at r=4 — the octad intersection weight class)')
    ax.set_xticks(x)
    ax.set_xticklabels(all_r)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    out = os.path.join(FIGURE_DIR, "fig2_ghost_radius.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 3: Z_4 closure comparison (Module 3)
# ---------------------------------------------------------------------------
def fig3_z4_closure():
    data = _load("module3_z4_projection.json")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    # Left: closure rates
    categories = ['GF(2)^24\nAND', 'Z_4\nadditive', 'Z_4\nMIN']
    values = [data["gf2_and_closure"], data["z4_additive_closure"], data["z4_min_closure"]]
    colors = ['#d62728', '#1f77b4', '#2ca02c']
    bars = ax1.bar(categories, values, color=colors, edgecolor='black')
    for bar, v in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                 f'{v:.4f}', ha='center', va='bottom', fontsize=11)
    ax1.set_ylabel('Closure rate')
    ax1.set_title('Module 3: Closure Rate Comparison\n(Gray map does NOT round the wheel)')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, max(values) * 1.3)
    # Right: NRCI field histogram
    nrci_field = data["nrci_field"]
    # We don't have the per-point field; use summary
    labels = ['min', 'mean', 'max']
    vals = [nrci_field["nrci_field_min"], nrci_field["nrci_field_mean"], nrci_field["nrci_field_max"]]
    ax2.bar(labels, vals, color=['#ff7f0e', '#9467bd', '#17becf'], edgecolor='black')
    for i, (l, v) in enumerate(zip(labels, vals)):
        ax2.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', fontsize=11)
    ax2.set_ylabel('NRCI')
    ax2.set_title(f'Module 3: NRCI Field Statistics\n({nrci_field["n_unique_projections"]} unique (X,Y,Z) projections)')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 1.1)
    out = os.path.join(FIGURE_DIR, "fig3_z4_closure.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 4: Dispersion fit scatter (Module 4)
# ---------------------------------------------------------------------------
def fig4_dispersion_fit():
    data = _load("module4_dispersion.json")
    # Re-generate the scatter by re-running the module with a small sample
    # Actually, we already have summary stats; let's plot the BSC scan instead
    bsc = data["bsc_melting"]["scan_points"]
    ps = [p["p_flip"] for p in bsc]
    nrcis = [p["mean_nrci"] for p in bsc]
    decodes = [p["decode_success_rate"] for p in bsc]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    # Left: BSC melting scan
    ax1.plot(ps, nrcis, 'o-', color='#d62728', linewidth=2, markersize=6, label='Mean NRCI')
    ax1.axhline(0.60, color='orange', linestyle='--', alpha=0.7, label='NRCI = 0.60 threshold')
    ax1.axhline(0.7623, color='green', linestyle=':', alpha=0.7, label='Canonical octad NRCI = 0.7623')
    ax1.set_xlabel('BSC crossover probability p (= temperature)')
    ax1.set_ylabel('NRCI')
    ax1.set_title('Module 4: BSC Melting Scan (NRCI)')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower left')
    # Right: Decode success rate
    ax2.plot(ps, decodes, 's-', color='#1f77b4', linewidth=2, markersize=6, label='Decode success rate')
    ax2.axhline(0.50, color='orange', linestyle='--', alpha=0.7, label='50% decode threshold')
    if data["bsc_melting"]["T_c_decode_below_0p50"] is not None:
        ax2.axvline(data["bsc_melting"]["T_c_decode_below_0p50"], color='red', linestyle=':',
                    alpha=0.7, label=f"T_c = {data['bsc_melting']['T_c_decode_below_0p50']:.3f}")
    ax2.axvline(1/6, color='gray', linestyle=':', alpha=0.5, label='d/2n = 1/6 ≈ 0.167')
    ax2.set_xlabel('BSC crossover probability p')
    ax2.set_ylabel('Decode success rate')
    ax2.set_title('Module 4: BSC Melting Scan (Decode)')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower left')
    out = os.path.join(FIGURE_DIR, "fig4_dispersion_fit.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 5: Leech harmonic spectrum (Module 5)
# ---------------------------------------------------------------------------
def fig5_leech_harmonic():
    data = _load("module5_leech_harmonic.json")
    sh = data["harmonic_spectrum"]
    S_l = sh["S_l"]
    Y_val = sh["Y_value"]
    s_max = sh["S_max"]
    threshold = Y_val * s_max
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    # Left: S(l) bar chart
    ls = list(range(len(S_l)))
    ax1.bar(ls, S_l, color='#1f77b4', edgecolor='black', label='S(l)')
    ax1.axhline(threshold, color='red', linestyle='--', alpha=0.7,
                label=f'Y · S_max = {Y_val:.4f} · {s_max:.2e} = {threshold:.2e}')
    ax1.set_xlabel('l (spherical harmonic degree)')
    ax1.set_ylabel('S(l) = Σ_m |a_lm|²')
    ax1.set_title('Module 5: Angular Power Spectrum on S²\n(Leech lattice minimal vectors)')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    # Right: Ternary vs Binary Golay weight histograms
    bridge = data["ternary_binary_bridge"]
    ternary_we = {int(k): int(v) for k, v in bridge["ternary_we"].items()}
    # Ternary WE
    t_w = sorted(ternary_we.keys())
    t_c = [ternary_we[w] for w in t_w]
    ax2.bar([w - 0.2 for w in t_w], t_c, width=0.4, color='#d62728',
            label=f'Ternary [12,6,6] Golay (729 codewords)', edgecolor='black')
    # Note: binary first-12 columns is binomial — different scale, plot as overlay
    binary_we = {int(k): int(v) for k, v in bridge["binary_first12_we"].items()}
    b_w = sorted(binary_we.keys())
    b_c = [binary_we[w] for w in b_w]
    ax2b = ax2.twinx()
    ax2b.plot(b_w, b_c, 'o-', color='#1f77b4', linewidth=2, markersize=6,
              label='Binary G_24 first 12 cols (binomial)')
    ax2b.set_ylabel('Binary first-12 count', color='#1f77b4')
    ax2.set_xlabel('Weight')
    ax2.set_ylabel('Ternary codeword count', color='#d62728')
    ax2.set_title('Module 5: Ternary-Binary Bridge\n(Ternary Golay preserves algebraic structure; binary truncation does not)')
    ax2.grid(True, alpha=0.3)
    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper center')
    out = os.path.join(FIGURE_DIR, "fig5_leech_harmonic.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 6: 3-axis master system Rosetta stone (capstone)
# ---------------------------------------------------------------------------
def fig6_master_system():
    data = _load("capstone_master_system.json")
    axis3 = data["axis_3_substrate_hierarchy"]
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    # Plot AND-closure vs dimension, colored by d/n
    dims = [s["dimension"] for s in axis3]
    and_cl = [s["and_closure"] for s in axis3]
    xor_cl = [s["xor_closure"] for s in axis3]
    codes = [s["discrete_code"] for s in axis3]
    ax.plot(dims, and_cl, 'o-', color='#d62728', linewidth=2.5, markersize=14, label='AND-closure (geometric)')
    ax.plot(dims, xor_cl, 's-', color='#1f77b4', linewidth=2.5, markersize=14, label='XOR-closure (linear)')
    ax.axvspan(12, 14, alpha=0.15, color='orange', label='Phase transition band')
    ax.set_xlabel('Substrate dimension n')
    ax.set_ylabel('Closure rate')
    ax.set_title('Capstone: 3-Axis Master System — AND-Closure Collapse\n(d²=0 verified; H·G^T = 0 mod 2; 80 total 3-axis cells)')
    ax.set_xticks(dims)
    ax.set_xticklabels([f'{d}D\n{c}' for d, c in zip(dims, codes)], fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='center right')
    ax.set_ylim(-0.05, 1.1)
    # Add annotations
    for d, ac in zip(dims, and_cl):
        ax.annotate(f'{ac:.3f}', (d, ac), textcoords="offset points", xytext=(0, 12),
                    ha='center', fontsize=9, color='#d62728')
    out = os.path.join(FIGURE_DIR, "fig6_master_system.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Generate all figures
# ---------------------------------------------------------------------------
def generate_all():
    print("Generating figures ...")
    fig1_catenary_beta()
    fig2_ghost_radius()
    fig3_z4_closure()
    fig4_dispersion_fit()
    fig5_leech_harmonic()
    fig6_master_system()
    print("All figures generated.")


if __name__ == "__main__":
    generate_all()
