"""
Figures for the totient-kinetics modules (9, 10, 11).
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
# Figure 10: Totient kinetics table + reaction regimes (Module 9)
# ---------------------------------------------------------------------------
def fig10_totient_table_and_reactions():
    data = _load("module9_intrinsic_extrinsic_duality.json")
    golay = data["golay_weight_totient_analysis"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), constrained_layout=True)
    # Left: M(N) for Golay weight classes
    weights = [r["weight"] for r in golay["weight_class_rows"]]
    masses = [r["topological_mass"] for r in golay["weight_class_rows"]]
    codewords = [r["codeword_count"] for r in golay["weight_class_rows"]]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    bars = ax1.bar(range(len(weights)), masses, color=colors, edgecolor='black')
    for i, (w, m, c) in enumerate(zip(weights, masses, codewords)):
        ax1.text(i, m + 0.1, f'M={m}\n({c} cws)', ha='center', va='bottom', fontsize=9)
    ax1.set_xticks(range(len(weights)))
    ax1.set_xticklabels([f'wt={w}' for w in weights])
    ax1.set_ylabel('Topological Mass M(N) = C(N)')
    ax1.set_title('Module 9: Golay Weight Class Topological Mass\n'
                  'M = {0, 2, 4, 4, 8} for weights {0, 8, 12, 16, 24}')
    ax1.grid(True, alpha=0.3, axis='y')
    # Right: Reaction regime distribution for Golay weight-class additions
    reactions = golay["weight_class_reactions"]
    labels = [r["label"][:30] for r in reactions]
    deltas = [r["delta_C"] for r in reactions]
    regimes = [r["regime"] for r in reactions]
    regime_colors = {"EXOTHERMIC": "#d62728", "ENDOTHERMIC": "#1f77b4", "ISO-RESONANT": "#2ca02c"}
    bar_colors = [regime_colors[r] for r in regimes]
    x = range(len(labels))
    bars2 = ax2.bar(x, deltas, color=bar_colors, edgecolor='black')
    for i, (d, r) in enumerate(zip(deltas, regimes)):
        ax2.text(i, d + (0.1 if d >= 0 else -0.3), f'{d:+d}\n{r[:4]}',
                ha='center', va='bottom' if d >= 0 else 'top', fontsize=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
    ax2.set_ylabel('Delta_C (binding energy)')
    ax2.set_title('Module 9: Cross-Reactions Between Weight Classes\n'
                  '8+8=16 and 12+12=24 are ISO-RESONANT (perfect conservation)')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(0, color='black', linewidth=0.5)
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=regime_colors[k], label=k) for k in regime_colors]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=9)
    out = os.path.join(FIGURE_DIR, "fig10_totient_table_and_reactions.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 11: Multiplication tensor product + addition comparison (Module 10)
# ---------------------------------------------------------------------------
def fig11_multiplication_tensor():
    data = _load("module10_multiplication_tensor.json")
    sweep = data["regime_distribution_sweep"]
    cmp = data["addition_vs_multiplication"]
    cn = data["coprime_vs_noncoprime"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    ax1, ax2, ax3 = axes
    # Left: regime distribution pie
    regimes = sweep["regime_counts"]
    labels = list(regimes.keys())
    sizes = list(regimes.values())
    colors = ['#d62728', '#1f77b4', '#2ca02c']
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 10})
    ax1.set_title(f'Module 10: Multiplication Regime Distribution\n'
                  f'({sweep["total_reactions"]} reactions; ALL endothermic)')
    # Middle: addition vs multiplication Delta_C
    cats = ['Addition', 'Multiplication']
    means = [cmp["addition"]["mean_delta_C"], cmp["multiplication"]["mean_delta_C"]]
    mins = [cmp["addition"]["min_delta_C"], cmp["multiplication"]["min_delta_C"]]
    maxs = [cmp["addition"]["max_delta_C"], cmp["multiplication"]["max_delta_C"]]
    x = range(len(cats))
    ax2.bar(x, means, color=['#1f77b4', '#ff7f0e'], edgecolor='black')
    for i, (m, mn, mx) in enumerate(zip(means, mins, maxs)):
        ax2.text(i, m + 5, f'mean={m:.1f}\nrange=[{mn}, {mx}]',
                ha='center', va='bottom', fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(cats)
    ax2.set_ylabel('Mean Delta_C')
    ax2.set_title('Addition vs Multiplication\n(Multiplication is ~1000x more endothermic)')
    ax2.grid(True, alpha=0.3, axis='y')
    # Right: coprime vs non-coprime
    cats3 = ['Coprime pairs', 'Non-coprime pairs']
    means3 = [cn["coprime_mean_delta_C"], cn["noncoprime_mean_delta_C"]]
    counts3 = [cn["n_coprime_pairs"], cn["n_noncoprime_pairs"]]
    x3 = range(len(cats3))
    bars3 = ax3.bar(x3, means3, color=['#2ca02c', '#9467bd'], edgecolor='black')
    for i, (m, c) in enumerate(zip(means3, counts3)):
        ax3.text(i, m + 2, f'mean={m:.1f}\nn={c}', ha='center', va='bottom', fontsize=9)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(cats3)
    ax3.set_ylabel('Mean Delta_C (multiplication)')
    ax3.set_title('Coprime vs Non-Coprime Multiplication\n(Non-coprime slightly more endothermic)')
    ax3.grid(True, alpha=0.3, axis='y')
    out = os.path.join(FIGURE_DIR, "fig11_multiplication_tensor.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


# ---------------------------------------------------------------------------
# Figure 12: Topological mass + asymptotic density (Module 11)
# ---------------------------------------------------------------------------
def fig12_topological_mass():
    data = _load("module11_topological_mass.json")
    asym = data["asymptotic_density_verification"]
    heavy = data["topologically_heavy_numbers"]
    ubp = data["ubp_base_topological_mass"]
    golay = data["golay_weight_topological_mass"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax1, ax2, ax3, ax4 = axes.flat
    # Top-left: rho(N) cumulative average approaching asymptote
    samples = asym["sample_densities"]
    ns = [s["n"] for s in samples]
    cum_avg = [s["cum_avg"] for s in samples]
    rho_n = [s["rho"] for s in samples]
    ax1.plot(ns, cum_avg, 'o-', color='#1f77b4', linewidth=2, markersize=5,
             label='Cumulative avg rho(N)')
    ax1.axhline(asym["asymptotic_density_theoretical"], color='red', linestyle='--',
                label=f'Asymptote = (1-6/π²)/2 = {asym["asymptotic_density_theoretical"]:.6f}')
    ax1.set_xlabel('N')
    ax1.set_ylabel('rho(N) = M(N)/N')
    ax1.set_title(f'Module 11: Asymptotic Density Convergence\n'
                  f'(error at N={asym["n_max"]}: {asym["convergence_error"]:.6f})')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9)
    # Top-right: Topologically heaviest numbers
    heaviest = heavy["heaviest_numbers"][:10]
    h_ns = [r["n"] for r in heaviest]
    h_ms = [r["M_N"] for r in heaviest]
    h_facs = [r["prime_factorization"] for r in heaviest]
    bars = ax2.barh(range(len(h_ns)), h_ms, color='#d62728', edgecolor='black')
    for i, (n, m, f) in enumerate(zip(h_ns, h_ms, h_facs)):
        ax2.text(m + 1, i, f'N={n} ({f})', va='center', fontsize=8)
    ax2.set_yticks(range(len(h_ns)))
    ax2.set_yticklabels([f'N={n}' for n in h_ns], fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlabel('Topological Mass M(N)')
    ax2.set_title(f'Module 11: Topologically Heaviest Numbers (N in [3, {heavy["n_max"]}])')
    ax2.grid(True, alpha=0.3, axis='x')
    # Bottom-left: UBP base numbers topological mass
    ubp_ns = [r["n"] for r in ubp["rows"]]
    ubp_ms = [r["M_N"] for r in ubp["rows"]]
    ubp_labels = [f'N={n}\n{r["prime_factorization"][:15]}' for n, r in zip(ubp_ns, ubp["rows"])]
    bars3 = ax3.bar(range(len(ubp_ns)), ubp_ms, color='#9467bd', edgecolor='black')
    for i, (n, m) in enumerate(zip(ubp_ns, ubp_ms)):
        ax3.text(i, m + 50, f'M={m}', ha='center', va='bottom', fontsize=9)
    ax3.set_xticks(range(len(ubp_ns)))
    ax3.set_xticklabels(ubp_labels, fontsize=8)
    ax3.set_ylabel('Topological Mass M(N)')
    ax3.set_title('Module 11: UBP Substrate Base Numbers\n(U_e = 13824 has M = 4608)')
    ax3.grid(True, alpha=0.3, axis='y')
    # Bottom-right: Golay weight class topological mass vs codeword count
    g_weights = [r["weight"] for r in golay["weight_class_rows"]]
    g_masses = [r["M_N"] for r in golay["weight_class_rows"]]
    g_cws = [r["codeword_count"] for r in golay["weight_class_rows"]]
    x = range(len(g_weights))
    ax4b = ax4.twinx()
    bars4 = ax4.bar(x, g_masses, width=0.4, color='#ff7f0e', edgecolor='black',
                    label='Topological Mass M(N)')
    ax4b.plot(x, g_cws, 's-', color='#1f77b4', linewidth=2, markersize=10,
              label='Codeword count')
    for i, (m, c) in enumerate(zip(g_masses, g_cws)):
        ax4.text(i, m + 0.1, f'M={m}', ha='center', va='bottom', fontsize=9, color='#ff7f0e')
        ax4b.text(i, c * 1.05, f'{c}', ha='center', va='bottom', fontsize=8, color='#1f77b4')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f'wt={w}' for w in g_weights])
    ax4.set_ylabel('Topological Mass M(N)', color='#ff7f0e')
    ax4b.set_ylabel('Codeword count', color='#1f77b4')
    ax4.set_title('Module 11: Golay Weight Class — Mass vs Codeword Count\n'
                  'Dodecad (wt=12) has highest count, all-ones (wt=24) has highest mass')
    ax4.grid(True, alpha=0.3, axis='y')
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4b.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    out = os.path.join(FIGURE_DIR, "fig12_topological_mass.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def generate_totient_figures():
    print("Generating totient-kinetics figures (Modules 9-11) ...")
    fig10_totient_table_and_reactions()
    fig11_multiplication_tensor()
    fig12_topological_mass()
    print("All totient-kinetics figures generated.")


if __name__ == "__main__":
    generate_totient_figures()
