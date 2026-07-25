"""
Additional figures for the spatial-arithmetic-fusion modules (6, 7, 8).

All plots use Noto Sans SC + DejaVu Sans for font fallback, constrained_layout=True,
no numpy/scipy.
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
# Figure 7: Spatial weight spectrum (Module 6)
# ---------------------------------------------------------------------------
def fig7_spatial_spectrum():
    data = _load("module6_spatial_catenary.json")
    spec = data["spatial_weight_spectrum"]
    rows = spec["weight_classes"]
    weights = [r["weight"] for r in rows]
    radii = [r["theoretical_radius"] for r in rows]
    counts = [r["codeword_count"] for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    # Left: radius vs weight
    ax1.plot(weights, radii, 'o-', color='#1f77b4', linewidth=2.5, markersize=12)
    for w, r, c in zip(weights, radii, counts):
        ax1.annotate(f'R={r:.3f}\n({c} cws)', (w, r), textcoords="offset points",
                    xytext=(15, -10), fontsize=9)
    ax1.set_xlabel('Golay codeword weight')
    ax1.set_ylabel('Spatial radius R(n) = 1/(2·sin(π/n))')
    ax1.set_title('Module 6: Spatial Weight Spectrum\n(Golay weights → 3D cycle radii)')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(weights)
    # Right: AND-closure rate by stratum
    strata = data["stratified_hodge_gap"]
    names = [s["stratum"] for s in strata]
    rates = [s["and_closure_rate"] for s in strata]
    angles = [s["mean_dihedral_angle_deg"] for s in strata]
    x = list(range(len(names)))
    bars = ax2.bar(x, rates, color=['#d62728', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b'],
                   edgecolor='black')
    for i, (r, a) in enumerate(zip(rates, angles)):
        ax2.text(i, r + 0.02, f'{r:.3f}\n({a:.0f}°)', ha='center', va='bottom', fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels([n.replace(' × ', '\n× ') for n in names], fontsize=8)
    ax2.set_ylabel('AND-closure rate')
    ax2.set_title('Module 6: Stratified Hodge Gap\n(color = dihedral angle °)')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 1.15)
    out = os.path.join(FIGURE_DIR, "fig7_spatial_spectrum.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 8: Cayley-Menger distance matrix (Module 7)
# ---------------------------------------------------------------------------
def fig8_cayley_menger():
    data = _load("module7_coordinate_free_hodge.json")
    geom = data["cluster_geometry"]
    matrix = geom["cayley_menger_distance_matrix"]
    info = geom["cluster_info"]
    n = len(matrix)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), constrained_layout=True)
    # Left: heatmap of distance matrix
    im = ax1.imshow(matrix, cmap='viridis', interpolation='nearest')
    ax1.set_xticks(range(n))
    ax1.set_yticks(range(n))
    ax1.set_xticklabels([f'C{i+1}\n(n={info[i]["n_members"]})' for i in range(n)], fontsize=8)
    ax1.set_yticklabels([f'C{i+1}' for i in range(n)], fontsize=9)
    for i in range(n):
        for j in range(n):
            ax1.text(j, i, f'{matrix[i][j]:.2f}', ha='center', va='center',
                     color='white' if matrix[i][j] > max(max(row) for row in matrix) / 2 else 'black',
                     fontsize=8)
    plt.colorbar(im, ax=ax1, label='Cayley-Menger distance')
    ax1.set_title(f'Module 7: Ghost-Cluster Distance Matrix\n'
                  f'({data["n_distinct_clusters"]} total clusters; top {n} shown)')
    # Right: cluster sizes
    sizes = [info[i]["n_members"] for i in range(n)]
    mean_wts = [info[i]["mean_weight"] for i in range(n)]
    ax2.bar(range(n), sizes, color='#5b7a99', edgecolor='black')
    for i, (s, mw) in enumerate(zip(sizes, mean_wts)):
        ax2.text(i, s + 1, f'{s}\nwt={mw:.1f}', ha='center', va='bottom', fontsize=9)
    ax2.set_xticks(range(n))
    ax2.set_xticklabels([f'C{i+1}' for i in range(n)], fontsize=9)
    ax2.set_ylabel('Number of ghosts in cluster')
    ax2.set_title('Module 7: Ghost-Cluster Sizes\n(with mean Hamming weight)')
    ax2.grid(True, alpha=0.3, axis='y')
    out = os.path.join(FIGURE_DIR, "fig8_cayley_menger.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 9: Spatial Y-constant resonance (Module 8)
# ---------------------------------------------------------------------------
def fig9_y_resonance():
    data = _load("module8_spatial_y_constant.json")
    # Left: R(n) scan vs Y, 1/Y
    scan = data["r_scan"]
    # Right: catenary curvature per weight class
    curv = data["catenary_curvature"]
    # Bottom: R(n) ratios vs constants
    ratios = data["r_ratios"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax1, ax2, ax3, ax4 = axes.flat

    # Top-left: R(n) for n in [4, 60], with Y and 1/Y horizontal lines
    pp_y = scan["Y_value"]
    pp_yinv = scan["Y_INV_value"]
    ns = list(range(4, 61))
    Rs = [1.0 / (2 * math.sin(math.pi / n)) for n in ns]
    ax1.plot(ns, Rs, 'o-', color='#1f77b4', linewidth=2, markersize=5, label='R(n) = 1/(2·sin(π/n))')
    ax1.axhline(pp_y, color='red', linestyle='--', alpha=0.7, label=f'Y = {pp_y:.4f}')
    ax1.axhline(pp_yinv, color='green', linestyle='--', alpha=0.7, label=f'1/Y = {pp_yinv:.4f}')
    ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.5, label='1.0')
    ax1.set_xlabel('n (node count)')
    ax1.set_ylabel('R(n)')
    ax1.set_title('Module 8: Spatial Primitive R(n) vs Observer Constant Y')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=9)

    # Top-right: R(n) ratios for Golay weight class pairs
    radii = ratios["radii_by_weight"]
    weights = sorted(int(w) for w in radii.keys())
    # Build ratio matrix
    mat = [[radii[str(w1)] / radii[str(w2)] if w2 != 0 else 0 for w2 in weights] for w1 in weights]
    im = ax2.imshow(mat, cmap='coolwarm', interpolation='nearest', vmin=0, vmax=4)
    ax2.set_xticks(range(len(weights)))
    ax2.set_yticks(range(len(weights)))
    ax2.set_xticklabels([f'wt={w}' for w in weights], fontsize=9)
    ax2.set_yticklabels([f'wt={w}' for w in weights], fontsize=9)
    for i in range(len(weights)):
        for j in range(len(weights)):
            ax2.text(j, i, f'{mat[i][j]:.2f}', ha='center', va='center',
                     color='white' if abs(mat[i][j] - 2) > 1 else 'black', fontsize=9)
    plt.colorbar(im, ax=ax2, label='R(w1)/R(w2)')
    ax2.set_title('Module 8: Spatial Radius Ratios\n(R(0)/R(16) ≈ Y; R(12)/R(0) ≈ e)')

    # Bottom-left: catenary curvature per weight class
    rows = curv["weight_class_curvatures"]
    wts = [r["weight"] for r in rows]
    int_kappas = [r["integrated_curvature"] for r in rows]
    bumps = [r["bumpiness_R_times_kappa"] for r in rows]
    x = list(range(len(wts)))
    ax3.bar([xi - 0.2 for xi in x], int_kappas, width=0.4, color='#d62728',
            label='∫κ = 2nY/π', edgecolor='black')
    ax3.bar([xi + 0.2 for xi in x], bumps, width=0.4, color='#1f77b4',
            label='R · ∫κ (bumpiness)', edgecolor='black')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f'wt={w}' for w in wts])
    ax3.set_ylabel('Curvature')
    ax3.set_title(f"Module 8: Catenary Curvature\nFormula: ∫₀ⁿ κ dh = 2nY/π = 2n/(π²+2)")
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.legend(fontsize=9)

    # Bottom-right: continued fraction of Y
    cf = data["continued_fractions"]
    Y_cf = cf["Y_continued_fraction"]
    R8_cf = cf["R8_over_pi_cf"]
    R24_cf = cf["R24_over_pi_cf"]
    ax4.axis('off')
    text = (
        f"CONTINUED FRACTIONS\n\n"
        f"Y = π/(π²+2):\n  [{', '.join(str(c) for c in Y_cf)}]\n\n"
        f"R(8)/π  (octad radius / π):\n  [{', '.join(str(c) for c in R8_cf)}]\n\n"
        f"R(24)/π (all-ones / π):\n  [{', '.join(str(c) for c in R24_cf)}]\n\n"
        f"R(8)/R(24):\n  [{', '.join(str(c) for c in cf['R8_over_R24_cf'])}]\n\n"
        f"Y's CF has a '27' (large term at index 6) —\n"
        f"this is a convergent indicating a near-rational\n"
        f"approximation at the 7th term.\n"
        f"\nNumerical values:\n"
        f"  Y              = {cf['Y_value']:.10f}\n"
        f"  R(8)/R(0)      = {radii['8']/radii['0']:.6f}\n"
        f"  R(12)/R(0) ≈ e = {radii['12']/radii['0']:.6f} (e=2.718282)\n"
        f"  R(0)/R(16) ≈ Y = {radii['0']/radii['16']:.6f} (Y=0.264675)"
    )
    ax4.text(0.05, 0.95, text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#f0f2f5', alpha=0.8))
    out = os.path.join(FIGURE_DIR, "fig9_y_resonance.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def generate_spatial_figures():
    print("Generating spatial figures (Modules 6-8) ...")
    fig7_spatial_spectrum()
    fig8_cayley_menger()
    fig9_y_resonance()
    print("All spatial figures generated.")


if __name__ == "__main__":
    generate_spatial_figures()
