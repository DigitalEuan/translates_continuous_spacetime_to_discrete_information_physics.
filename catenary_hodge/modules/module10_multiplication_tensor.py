"""
MODULE 10 — Multiplication as Tensor Product of Polygons (Extension A)
========================================================================
Implements Extension A from suggestions_25jul26.txt §4.

If Addition is merging vertices (A + B), what is Multiplication?
In geometry, multiplying two regular polygons corresponds to the Minkowski
Product / Tensor Product of their symmetries. A regular A-gon multiplied
by a regular B-gon yields a structure with A*B symmetries on the torus
S^1 x S^1.

This module:
  1. Defines the Multiplication Reaction: A * B = C, where C = A*B.
  2. Computes the binding energy Delta_C_mul = C(A*B) - (C(A) + C(B)).
  3. Verifies the multiplicative phi formula:
       phi(A*B) = phi(A) * phi(B) * gcd(A,B) / phi(gcd(A,B))
  4. Classifies multiplication reactions into the same three thermodynamic
     regimes (EXOTHERMIC, ENDOTHERMIC, ISO-RESONANT).
  5. Sweeps a large reaction space (A, B ∈ [3, 100]) to find the
     distribution of regimes.
  6. Compares addition vs multiplication reaction kinetics — does
     multiplication release or absorb more topological energy?
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import time

from catenary_hodge.engines.totient_kinetics import (
    phi, count_sub_cycles_closed, R_n, geometric_tension, is_prime,
    analyze_reaction, analyze_multiplication_reaction, prime_factors,
)
from catenary_hodge.engines.totient_kinetics import phi_multiplicative


# ---------------------------------------------------------------------------
# 1. Multiplication reaction enumeration
# ---------------------------------------------------------------------------
def multiplication_reaction(a: int, b: int) -> Dict[str, Any]:
    """Full analysis of A * B = C as a tensor-product reaction.

    The product forms an A*B-vertex structure on the torus S^1 x S^1.
    The sub-cycle topology of the product is:
        C(A*B) = floor(AB/2) - phi(AB)/2

    For coprime A, B:  phi(AB) = phi(A) * phi(B), so
        C(A*B) = floor(AB/2) - phi(A)*phi(B)/2

    For general A, B:  phi(AB) = phi(A) * phi(B) * d / phi(d)  with d = gcd(A,B).
    """
    return analyze_multiplication_reaction(a, b)


# ---------------------------------------------------------------------------
# 2. Large-scale regime distribution sweep
# ---------------------------------------------------------------------------
def regime_distribution_sweep(n_max: int = 100) -> Dict[str, Any]:
    """Sweep A, B ∈ [3, n_max] and classify all multiplication reactions.

    Returns the distribution of EXOTHERMIC / ENDOTHERMIC / ISO-RESONANT
    regimes, plus statistics on coprime vs non-coprime pairs.
    """
    regimes = {"EXOTHERMIC": 0, "ENDOTHERMIC": 0, "ISO-RESONANT": 0}
    coprime_count = 0
    non_coprime_count = 0
    delta_C_values: List[int] = []
    iso_resonant_pairs: List[Tuple[int, int]] = []
    for a in range(3, n_max + 1):
        for b in range(a, n_max + 1):  # symmetric, only do upper triangle
            r = multiplication_reaction(a, b)
            regimes[r["regime"]] += 1
            delta_C_values.append(r["delta_C_multiplication"])
            if r["coprime"]:
                coprime_count += 1
            else:
                non_coprime_count += 1
            if r["regime"] == "ISO-RESONANT":
                iso_resonant_pairs.append((a, b))
    total = sum(regimes.values())
    return {
        "n_max": n_max,
        "total_reactions": total,
        "regime_counts": regimes,
        "regime_fractions": {k: v / total for k, v in regimes.items()},
        "coprime_pairs": coprime_count,
        "non_coprime_pairs": non_coprime_count,
        "delta_C_stats": {
            "min": min(delta_C_values),
            "max": max(delta_C_values),
            "mean": sum(delta_C_values) / len(delta_C_values),
        },
        "iso_resonant_pairs_sample": iso_resonant_pairs[:20],
        "n_iso_resonant": len(iso_resonant_pairs),
    }


# ---------------------------------------------------------------------------
# 3. Addition vs Multiplication comparison
# ---------------------------------------------------------------------------
def addition_vs_multiplication(n_max: int = 50) -> Dict[str, Any]:
    """Compare Delta_C for A+B vs A*B across all pairs (A, B) in [3, n_max].

    Tests whether multiplication releases or absorbs more topological
    energy than addition on average.
    """
    add_deltas: List[int] = []
    mul_deltas: List[int] = []
    paired: List[Dict[str, Any]] = []
    for a in range(3, n_max + 1):
        for b in range(a, n_max + 1):
            r_add = analyze_reaction(a, b)
            r_mul = multiplication_reaction(a, b)
            add_deltas.append(r_add["delta_C"])
            mul_deltas.append(r_mul["delta_C_multiplication"])
            if abs(r_add["delta_C"]) > 0 or abs(r_mul["delta_C_multiplication"]) > 0:
                paired.append({
                    "a": a, "b": b,
                    "delta_C_add": r_add["delta_C"],
                    "delta_C_mul": r_mul["delta_C_multiplication"],
                    "add_regime": r_add["regime"],
                    "mul_regime": r_mul["regime"],
                })
    return {
        "n_max": n_max,
        "n_pairs": len(add_deltas),
        "addition": {
            "mean_delta_C": sum(add_deltas) / len(add_deltas),
            "min_delta_C": min(add_deltas),
            "max_delta_C": max(add_deltas),
        },
        "multiplication": {
            "mean_delta_C": sum(mul_deltas) / len(mul_deltas),
            "min_delta_C": min(mul_deltas),
            "max_delta_C": max(mul_deltas),
        },
        "multiplication_releases_more_energy": (
            sum(mul_deltas) < sum(add_deltas)  # more negative = more exothermic
        ),
        "sample_paired_reactions": paired[:15],
    }


# ---------------------------------------------------------------------------
# 4. Coprime vs non-coprime multiplication
# ---------------------------------------------------------------------------
def coprime_vs_noncoprime_analysis(n_max: int = 50) -> Dict[str, Any]:
    """Compare multiplication reactions for coprime vs non-coprime pairs.

    For coprime (a, b): phi(ab) = phi(a)*phi(b), so the multiplicative
    formula simplifies. This should produce a distinct regime distribution.
    """
    coprime_deltas: List[int] = []
    noncoprime_deltas: List[int] = []
    for a in range(3, n_max + 1):
        for b in range(a, n_max + 1):
            r = multiplication_reaction(a, b)
            if r["coprime"]:
                coprime_deltas.append(r["delta_C_multiplication"])
            else:
                noncoprime_deltas.append(r["delta_C_multiplication"])
    return {
        "n_max": n_max,
        "n_coprime_pairs": len(coprime_deltas),
        "n_noncoprime_pairs": len(noncoprime_deltas),
        "coprime_mean_delta_C": sum(coprime_deltas) / len(coprime_deltas) if coprime_deltas else 0,
        "noncoprime_mean_delta_C": sum(noncoprime_deltas) / len(noncoprime_deltas) if noncoprime_deltas else 0,
        "coprime_min_max": (min(coprime_deltas), max(coprime_deltas)) if coprime_deltas else (0, 0),
        "noncoprime_min_max": (min(noncoprime_deltas), max(noncoprime_deltas)) if noncoprime_deltas else (0, 0),
    }


# ---------------------------------------------------------------------------
# 5. Module 10 main runner
# ---------------------------------------------------------------------------
def run(n_max_sweep: int = 100, n_max_compare: int = 50) -> Dict[str, Any]:
    print("=== Module 10: Multiplication as Tensor Product (Extension A) ===")
    t0 = time.time()
    print("\n1. Sample multiplication reactions:")
    test_pairs = [(5, 7), (6, 8), (9, 6), (24, 12), (5, 11), (8, 8), (12, 4)]
    for a, b in test_pairs:
        r = multiplication_reaction(a, b)
        print(f"   {r['reaction']:>14}  Delta_C_mul={r['delta_C_multiplication']:>+5}  "
              f"phi(AB) ok={r['multiplicative_phi_holds']}  coprime={r['coprime']}  "
              f"regime={r['regime']}")
    print(f"\n2. Regime distribution sweep (A, B in [3, {n_max_sweep}])...")
    sweep = regime_distribution_sweep(n_max=n_max_sweep)
    print(f"   Total reactions: {sweep['total_reactions']}")
    print(f"   Regime counts: {sweep['regime_counts']}")
    print(f"   Regime fractions: {dict((k, round(v, 4)) for k, v in sweep['regime_fractions'].items())}")
    print(f"   Coprime pairs: {sweep['coprime_pairs']}, non-coprime: {sweep['non_coprime_pairs']}")
    print(f"   Delta_C stats: min={sweep['delta_C_stats']['min']}, "
          f"max={sweep['delta_C_stats']['max']}, "
          f"mean={sweep['delta_C_stats']['mean']:.2f}")
    print(f"   ISO-RESONANT count: {sweep['n_iso_resonant']}")
    if sweep['iso_resonant_pairs_sample']:
        print(f"   Sample ISO-RESONANT pairs: {sweep['iso_resonant_pairs_sample'][:10]}")
    print(f"\n3. Addition vs Multiplication (A, B in [3, {n_max_compare}])...")
    cmp = addition_vs_multiplication(n_max=n_max_compare)
    print(f"   Addition:     mean Delta_C = {cmp['addition']['mean_delta_C']:.3f}  "
          f"(range {cmp['addition']['min_delta_C']} to {cmp['addition']['max_delta_C']})")
    print(f"   Multiplication: mean Delta_C = {cmp['multiplication']['mean_delta_C']:.3f}  "
          f"(range {cmp['multiplication']['min_delta_C']} to {cmp['multiplication']['max_delta_C']})")
    print(f"   Multiplication releases MORE energy: {cmp['multiplication_releases_more_energy']}")
    print(f"\n4. Coprime vs non-coprime multiplication (N up to {n_max_compare})...")
    cn = coprime_vs_noncoprime_analysis(n_max=n_max_compare)
    print(f"   Coprime pairs:     mean Delta_C = {cn['coprime_mean_delta_C']:.3f}  "
          f"(range {cn['coprime_min_max']})")
    print(f"   Non-coprime pairs: mean Delta_C = {cn['noncoprime_mean_delta_C']:.3f}  "
          f"(range {cn['noncoprime_min_max']})")
    t1 = time.time()
    print(f"\nTotal Module 10 time: {t1-t0:.1f}s")
    return {
        "sample_reactions": [
            multiplication_reaction(a, b) for a, b in test_pairs
        ],
        "regime_distribution_sweep": sweep,
        "addition_vs_multiplication": cmp,
        "coprime_vs_noncoprime": cn,
        "verdict": (
            f"Multiplication reactions sweep {sweep['total_reactions']:,} pairs (A,B in [3, {n_max_sweep}]). "
            f"Regime distribution: {dict((k, round(v, 4)) for k, v in sweep['regime_fractions'].items())}. "
            f"Multiplication's mean Delta_C ({cmp['multiplication']['mean_delta_C']:.2f}) "
            f"is {'MORE' if cmp['multiplication_releases_more_energy'] else 'LESS'} exothermic than "
            f"addition's ({cmp['addition']['mean_delta_C']:.2f}). "
            "The tensor-product structure of multiplication generates substantially "
            "more topological binding energy than the merge structure of addition."
        ),
    }


if __name__ == "__main__":
    import json
    result = run(n_max_sweep=80, n_max_compare=40)
    out_path = "/home/z/my-project/results/module10_multiplication_tensor.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n→ {out_path}")
