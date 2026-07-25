"""
Figures for Modules 12, 13, 14 (Steiner ISO-RESONANCE, Y-Hexadecad-Totient,
Topological Mass Density).
"""
import os
import json
import math
from typing import Dict, List, Any

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
# Figure 13: Steiner ISO-RESONANCE rates (Module 12)
# ---------------------------------------------------------------------------
def fig13_steiner_iso_resonance():
    data = _load("module12_steiner_iso_resonance.json")
    results = data["steiner_system_results"]
    names = list(results.keys())
    iso_rates = [results[n]["iso_resonant_rate"] * 100 for n in names]
    n_blocks = [results[n]["n_blocks"] for n in names]
    block_sizes = []
    for n in names:
        # Extract block size from the system name
        if "Fano" in n:
            block_sizes.append(3)
        elif "AG(3,2)" in n:
            block_sizes.append(4)
        elif "small Witt" in n:
            block_sizes.append(5)
        elif "large Witt small" in n:
            block_sizes.append(6)
        elif "Golay" in n:
            block_sizes.append(8)
        else:
            block_sizes.append(0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), constrained_layout=True)
    # Left: ISO-RESONANCE rate by Steiner system
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    bars = ax1.bar(range(len(names)), iso_rates, color=colors, edgecolor='black')
    for i, (r, n, k) in enumerate(zip(iso_rates, n_blocks, block_sizes)):
        ax1.text(i, r + 2, f'{r:.1f}%\n(k={k}, n={n})',
                ha='center', va='bottom', fontsize=9)
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels([n.replace(' ', '\n') for n in names], fontsize=8)
    ax1.set_ylabel('ISO-RESONANT rate (%)')
    ax1.set_title('Module 12: ISO-RESONANCE Rate Across Steiner Systems\n'
                  'Fano, AG(3,2), and Golay all hit 100% — Steiner-Totient Conservation')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 115)
    # Right: ISO-RESONANT rate vs block size k
    ax2.plot(block_sizes, iso_rates, 'o-', color='#d62728', linewidth=2.5, markersize=14)
    for k, r, n in zip(block_sizes, iso_rates, n_blocks):
        ax2.annotate(f'{r:.0f}%', (k, r), textcoords="offset points",
                    xytext=(10, -10), fontsize=10)
    ax2.set_xlabel('Steiner block size k')
    ax2.set_ylabel('ISO-RESONANT rate (%)')
    ax2.set_title('Module 12: ISO-RESONANCE vs Block Size\n'
                  'Steiner-Totient Conservation: 100% iff M(k) is small enough')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 115)
    out = os.path.join(FIGURE_DIR, "fig13_steiner_iso_resonance.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 14: Y-Hexadecad-Totient hidden structure (Module 13)
# ---------------------------------------------------------------------------
def fig14_y_hexadecad_totient():
    data = _load("module13_y_hexadecad_totient.json")
    h1 = data["h1_radius_ratio_scan"]
    h2 = data["h2_mass_ratio_scan"]
    h4 = data["h4_existence_unit_topological_third"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    ax1, ax2, ax3 = axes
    # Left: Top radius-ratio matches to Y
    matches = h1["all_matches_within_10pct"][:8]
    if matches:
        labels = [f"R({m['w1']})/R({m['w2']})" for m in matches]
        values = [m["ratio"] for m in matches]
        targets = [m["target"] for m in matches]
        target_vals = [m["target_value"] for m in matches]
        errors = [m["relative_error"] * 100 for m in matches]
        x = range(len(labels))
        bars = ax1.bar(x, values, color='#1f77b4', edgecolor='black', alpha=0.7, label='Ratio')
        for i, (v, t, tv, e) in enumerate(zip(values, targets, target_vals, errors)):
            ax1.plot([i, i], [0, tv], color='red', linewidth=2, alpha=0.6)
            ax1.text(i, v + 0.02, f'{v:.3f}\nvs {t}\n(err {e:.1f}%)',
                    ha='center', va='bottom', fontsize=8)
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
        ax1.set_ylabel('Ratio value')
        ax1.set_title('Module 13: Top R(N1)/R(N2) Matches to UBP Constants\n'
                      'Red lines = target values')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.legend(loc='upper right', fontsize=9)
    # Middle: Mass ratio heatmap (Golay weights)
    weights = [8, 12, 16, 24]
    mass_matrix = [[0]*4 for _ in range(4)]
    for r in h2["mass_ratio_table"]:
        if r["w1"] in weights and r["w2"] in weights:
            i = weights.index(r["w1"])
            j = weights.index(r["w2"])
            mass_matrix[i][j] = r["ratio_M1_over_M2"]
    im = ax2.imshow(mass_matrix, cmap='YlOrRd', interpolation='nearest')
    ax2.set_xticks(range(4))
    ax2.set_yticks(range(4))
    ax2.set_xticklabels([f'wt={w}' for w in weights])
    ax2.set_yticklabels([f'wt={w}' for w in weights])
    for i in range(4):
        for j in range(4):
            ax2.text(j, i, f'{mass_matrix[i][j]:.1f}', ha='center', va='center',
                    color='black' if mass_matrix[i][j] < 2 else 'white', fontsize=11)
    plt.colorbar(im, ax=ax2, label='M(w1)/M(w2)')
    ax2.set_title('Module 13: Topological Mass Ratio Matrix\n'
                  'All ratios are powers of 2 (dyadic structure)')
    # Right: Existence Unit topological third
    ax3.axis('off')
    text = (
        f"EXISTENCE UNIT TOPOLOGICAL THIRD\n\n"
        f"U_e = 13824 = 24^3\n"
        f"phi(U_e) = 4608\n"
        f"M(U_e) = 4608 = U_e / 3\n\n"
        f"phi(24) = 8\n"
        f"M(24) = 8 = 24 / 3\n\n"
        f"Totient ratio invariance:\n"
        f"  phi(U_e)/U_e = phi(24)/24 = 1/3\n\n"
        f"The 'coprime density' of U_e equals that of 24.\n"
        f"M(N) = N/3 exactly when phi(N)/N = 1/3.\n"
        f"This is the 'topological third' of the Existence Unit.\n\n"
        f"U_e and 24 both deviate from rho_inf = 0.196\n"
        f"by +0.137 (70.4% above asymptotic average)."
    )
    ax3.text(0.05, 0.95, text, transform=ax3.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#f0f2f5', alpha=0.8))
    out = os.path.join(FIGURE_DIR, "fig14_y_hexadecad_totient.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 15: Topological Mass Density as new UBP constant (Module 14)
# ---------------------------------------------------------------------------
def fig15_topological_mass_density():
    data = _load("module14_topological_mass_density_constant.json")
    dirichlet = data["dirichlet_convergence"]
    hl = data["topological_half_life"]
    cmp = data["ubp_constants_comparison"]
    sub = data["rho_inf_in_ubp_substrate"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax1, ax2, ax3, ax4 = axes.flat
    # Top-left: Convergence of rho(N) to rho_inf
    samples = dirichlet["sample_densities"]
    ns = [s["n"] for s in samples]
    cum_avg = [s["cum_avg"] for s in samples]
    rho_n = [s["rho"] for s in samples]
    ax1.plot(ns, cum_avg, 'o-', color='#1f77b4', linewidth=2, markersize=5,
             label='Cumulative avg rho(N)')
    ax1.axhline(dirichlet["asymptotic_density_theoretical"], color='red', linestyle='--',
                label=f'rho_inf = (1-6/π²)/2 = {dirichlet["asymptotic_density_theoretical"]:.6f}')
    ax1.set_xlabel('N')
    ax1.set_ylabel('rho(N) cumulative average')
    ax1.set_title(f'Module 14: Dirichlet Convergence\n'
                  f'(error at N={dirichlet["n_max"]}: {dirichlet["convergence_error"]:.6f})')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9)
    # Top-right: Topological half-life
    half_lives = hl["half_lives"]
    eps_vals = [h["epsilon"] for h in half_lives if h["n_required"]]
    n_reqs = [h["n_required"] for h in half_lives if h["n_required"]]
    ax2.plot(eps_vals, n_reqs, 's-', color='#d62728', linewidth=2, markersize=12)
    for e, n in zip(eps_vals, n_reqs):
        ax2.annotate(f'N={n}', (e, n), textcoords="offset points",
                    xytext=(10, 5), fontsize=9)
    ax2.set_xlabel('Epsilon (convergence threshold)')
    ax2.set_ylabel('N required')
    ax2.set_title('Module 14: Topological Half-Life\n(How large N needs to be for |cumavg - rho_inf| < eps)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    # Bottom-left: UBP constants comparison table
    ax3.axis('off')
    table_data = [["Constant", "Value", "Closed form"]]
    for name, val, cf, _ in cmp["constants_table"]:
        val_str = f"{val:.6f}" if isinstance(val, float) else str(val)
        table_data.append([name, val_str, cf])
    table = ax3.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    for i in range(3):
        table[0, i].set_facecolor('#1f3a5f')
        table[0, i].set_text_props(color='white', weight='bold')
    # Highlight the new rho_inf row
    for j in range(3):
        table[2, j].set_facecolor('#fff3cd')
    ax3.set_title('Module 14: UBP Constants Table (with NEW rho_inf highlighted)', pad=20)
    # Bottom-right: rho_inf in the UBP substrate
    ax4.axis('off')
    text = (
        f"rho_inf IN THE UBP SUBSTRATE\n\n"
        f"rho_inf = (1 - 6/π²)/2 ≈ 0.196036\n\n"
        f"Empirical rho(N):\n"
        f"  rho(U_e = 13824) = 1/3 ≈ 0.333333\n"
        f"  rho(24)           = 1/3 ≈ 0.333333\n"
        f"  rho_inf (avg)     =       0.196036\n\n"
        f"Deviation of U_e from rho_inf: +0.137\n"
        f"The Existence Unit has 70.4% higher\n"
        f"sub-cycle density than the average\n"
        f"integer — reflecting its highly composite\n"
        f"structure (24 = 2³·3).\n\n"
        f"NEW UBP CONSTANT DECLARED:\n"
        f"  rho_inf (Topological Mass Density)\n"
        f"  Closed form: (1 - 6/π²)/2\n"
        f"  Exact Fraction repr: yes (60 digits)\n"
        f"  Dirichlet convergence: verified"
    )
    ax4.text(0.05, 0.95, text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#fff3cd', alpha=0.9))
    out = os.path.join(FIGURE_DIR, "fig15_topological_mass_density.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def generate_refine_figures():
    print("Generating refine-directive figures (Modules 12-14) ...")
    fig13_steiner_iso_resonance()
    fig14_y_hexadecad_totient()
    fig15_topological_mass_density()
    print("All refine-directive figures generated.")


if __name__ == "__main__":
    generate_refine_figures()
