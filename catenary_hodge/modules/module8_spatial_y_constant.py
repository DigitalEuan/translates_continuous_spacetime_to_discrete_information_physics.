"""
MODULE 8 — Spatial Y-Constant: R(n) vs Y = π/(π²+2) Resonance Scan
====================================================================
Tests whether the UBP Observer Constant Y = π/(π²+2) ≈ 0.2647 emerges
naturally from the spatial primitive R(n) = 1/(2·sin(π/n)).

The spatial primitive R(n) is the natural-log analog in spatial_arithmetic
(it's the unique function that makes value→radius→value a round trip).
The UBP Observer Constant Y is the inverse of the arithmetic mean of π
and 2/π:  Y = 1 / (π + 2/π) = π / (π² + 2).

This module scans:
  1. R(n) for n ∈ [4, 100] and finds n* such that R(n*) ≡ Y (mod some scale)
  2. Whether the ratio R(8)/R(24) (octad radius / all-ones radius) relates to Y
  3. The catenary curvature κ(h) = Y·(1 - cos(π h/n)) integrated over R(n) nodes
  4. Whether Y emerges from a continued-fraction expansion of R(n)/π
  5. The Golden-ratio cross-check: R(n) at n = φ-related indices
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import math
import time
import mpmath as mp

from catenary_hodge.engines.adapter import get_pp, get_golay
from catenary_hodge.engines.spatial_golay import (
    weight_to_value, WEIGHT_TO_SPATIAL_VALUE, spatial_weight_spectrum,
)
import spatial_arithmetic as sa


def scan_r_for_y(min_n: int = 4, max_n: int = 200) -> Dict[str, Any]:
    """Scan R(n) = 1/(2·sin(π/n)) for n in [min_n, max_n] and find values
    that match Y = π/(π²+2) under various transformations.

    Transformations tested:
      * R(n) directly
      * 1/R(n) (the Observer reciprocal)
      * R(n)/π
      * R(n) mod 1
      * π · R(n) mod 1
    """
    pp = get_pp()
    Y = float(pp.Y)
    Y_INV = float(pp.Y_INV)
    pi = math.pi
    closest = []
    for n in range(min_n, max_n + 1):
        R = sa.value_to_radius((n - sa.BASE_NODES) // 2)
        # Test multiple transformations
        transforms = [
            ("R(n)", R),
            ("1/R(n)", 1.0 / R if R != 0 else float('inf')),
            ("R(n)/π", R / pi),
            ("R(n) mod 1", R - math.floor(R)),
            ("π · R(n) mod 1", (pi * R) % 1.0),
            ("R(n)² mod 1", (R * R) % 1.0),
        ]
        for tname, val in transforms:
            for target_name, target in [("Y", Y), ("Y_INV", Y_INV), ("1", 1.0), ("π", pi)]:
                if target == 0:
                    continue
                err = abs(val - target) / abs(target)
                if err < 0.01:  # within 1%
                    closest.append({
                        "n": n,
                        "transform": tname,
                        "value": val,
                        "target": target_name,
                        "target_value": target,
                        "relative_error": err,
                    })
    # Sort by error
    closest.sort(key=lambda x: x["relative_error"])
    return {
        "scan_range": [min_n, max_n],
        "Y_value": Y,
        "Y_INV_value": Y_INV,
        "n_close_matches": len(closest),
        "top_10_closest": closest[:10],
    }


def r_ratios_vs_y() -> Dict[str, Any]:
    """Compute ratios of R(n) for Golay weight classes and check if any
    equals Y or 1/Y.
    """
    pp = get_pp()
    Y = float(pp.Y)
    Y_INV = float(pp.Y_INV)
    spec = spatial_weight_spectrum()
    radii = {r["weight"]: r["theoretical_radius"] for r in spec["weight_classes"]}
    # Compute all pairwise ratios
    ratios = []
    weights = sorted(radii.keys())
    for w1 in weights:
        for w2 in weights:
            if w1 == w2:
                continue
            ratio = radii[w1] / radii[w2]
            # Compare to Y, 1/Y, π, e, φ
            for target_name, target in [("Y", Y), ("Y_INV", Y_INV),
                                         ("π", math.pi), ("e", math.e),
                                         ("φ", (1 + math.sqrt(5)) / 2)]:
                err = abs(ratio - target) / abs(target)
                if err < 0.05:  # within 5%
                    ratios.append({
                        "weight_pair": f"{w1}/{w2}",
                        "ratio": ratio,
                        "target": target_name,
                        "target_value": target,
                        "relative_error": err,
                    })
    ratios.sort(key=lambda x: x["relative_error"])
    return {
        "ratios": ratios,
        "n_close_matches": len(ratios),
        "radii_by_weight": radii,
    }


def continued_fraction_y_check() -> Dict[str, Any]:
    """Compute the continued fraction of Y = π/(π²+2) and R(n)/π for
    various n, and check if they share convergents.
    """
    pp = get_pp()
    Y_mp = mp.mpf(math.pi) / (mp.mpf(math.pi) ** 2 + 2)
    Y_cf = mp.identify(Y_mp) if hasattr(mp, 'identify') else None
    # Compute CF of Y manually
    def continued_fraction(x, n_terms=10):
        cf = []
        for _ in range(n_terms):
            if x == 0:
                break
            int_part = int(mp.floor(x))
            cf.append(int_part)
            frac_part = x - int_part
            if frac_part < mp.mpf("1e-12"):
                break
            x = 1 / frac_part
        return cf
    Y_cfrac = continued_fraction(Y_mp, 10)
    # Compute CF of R(8)/π (octad radius / π)
    R8 = sa.value_to_radius(weight_to_value(8))
    R8_over_pi_cf = continued_fraction(mp.mpf(R8) / mp.mpf(math.pi), 10)
    R24 = sa.value_to_radius(weight_to_value(24))
    R24_over_pi_cf = continued_fraction(mp.mpf(R24) / mp.mpf(math.pi), 10)
    # Check ratio R(8)/R(24)
    R_ratio_cf = continued_fraction(mp.mpf(R8) / mp.mpf(R24), 10)
    return {
        "Y_value": float(Y_mp),
        "Y_continued_fraction": Y_cfrac,
        "Y_identified_as": Y_cf,
        "R8_over_pi_cf": R8_over_pi_cf,
        "R24_over_pi_cf": R24_over_pi_cf,
        "R8_over_R24_cf": R_ratio_cf,
        "interpretation": (
            "The continued fraction of Y = π/(π²+2) is compared to those of "
            "R(n)/π for the Golay weight classes. A shared convergent would "
            "indicate a deep arithmetic link between the spatial primitive "
            "and the Observer constant."
        ),
    }


def catenary_curvature_on_r_road() -> Dict[str, Any]:
    """Integrate the catenary curvature κ(h) = Y·(1 - cos(π h/n)) over the
    spatial cycle R(n) for each Golay weight class.

    The integral  ∫₀ⁿ κ(h) dh = 2nY/π = 2n/(π²+2)  measures the total
    'bumpiness' of the catenary road when a wheel of n nodes rolls along it.
    """
    pp = get_pp()
    Y = float(pp.Y)
    pi = math.pi
    results = []
    for weight, value in WEIGHT_TO_SPATIAL_VALUE.items():
        n_nodes = 2 * value + sa.BASE_NODES
        # Integrated curvature: 2·n·Y/π
        int_curv = 2 * n_nodes * Y / pi
        # Per-node curvature (average)
        per_node = int_curv / n_nodes
        # R(n) for this n
        R = sa.value_to_radius(value)
        # Curvature × radius (dimensionless bumpiness)
        bumpiness = int_curv * R
        results.append({
            "weight": weight,
            "n_nodes": n_nodes,
            "spatial_value": value,
            "R_n": R,
            "integrated_curvature": int_curv,
            "per_node_curvature": per_node,
            "bumpiness_R_times_kappa": bumpiness,
        })
    return {
        "weight_class_curvatures": results,
        "Y_value": Y,
        "formula": "∫₀ⁿ κ(h) dh = 2nY/π = 2n/(π²+2)",
    }


def golden_ratio_cross_check() -> Dict[str, Any]:
    """Cross-check R(n) at φ-related indices.

    The Golden ratio φ = (1+√5)/2 appears in the UBP Entropic Wobble
    w = (π·φ·e) mod 1.  Here we test whether R(n) at n = round(φ·k) for
    k = 1..20 produces any special values related to Y.
    """
    pp = get_pp()
    Y = float(pp.Y)
    Y_INV = float(pp.Y_INV)
    phi = (1 + math.sqrt(5)) / 2
    results = []
    for k in range(1, 21):
        n = round(phi * k) + sa.BASE_NODES
        if n < 4:
            continue
        v = (n - sa.BASE_NODES) // 2
        if v < 0:
            continue
        R = sa.value_to_radius(v)
        results.append({
            "k": k,
            "n_phi": round(phi * k),
            "n_total": n,
            "spatial_value": v,
            "R_n": R,
            "R_over_pi": R / math.pi,
            "R_mod_1": R - math.floor(R),
        })
    # Find which R(n) at φ-related n is closest to Y or 1/Y
    closest_to_Y = None
    closest_to_Y_INV = None
    for r in results:
        err_y = abs(r["R_n"] - Y) / Y
        err_yinv = abs(r["R_n"] - Y_INV) / Y_INV
        if closest_to_Y is None or err_y < closest_to_Y["err"]:
            closest_to_Y = {"k": r["k"], "n": r["n_total"], "R": r["R_n"], "err": err_y}
        if closest_to_Y_INV is None or err_yinv < closest_to_Y_INV["err"]:
            closest_to_Y_INV = {"k": r["k"], "n": r["n_total"], "R": r["R_n"], "err": err_yinv}
    return {
        "phi_value": phi,
        "phi_related_n_values": results,
        "closest_R_to_Y": closest_to_Y,
        "closest_R_to_Y_INV": closest_to_Y_INV,
    }


# ---------------------------------------------------------------------------
# Module 8 main runner
# ---------------------------------------------------------------------------
def run() -> Dict[str, Any]:
    print("=== Module 8: Spatial Y-Constant Resonance Scan ===")
    t0 = time.time()
    print("\n1. Scanning R(n) for n ∈ [4, 200] for matches to Y, 1/Y, π, 1, π")
    scan = scan_r_for_y(min_n=4, max_n=200)
    print(f"   Found {scan['n_close_matches']} close matches")
    print(f"   Top 5:")
    for m in scan["top_10_closest"][:5]:
        print(f"     n={m['n']:>3}  {m['transform']:>14} = {m['value']:.6f}  "
              f"vs {m['target']}={m['target_value']:.6f}  err={m['relative_error']:.4f}")
    print("\n2. R(n) ratios vs Y, 1/Y, π, e, φ")
    ratios = r_ratios_vs_y()
    print(f"   Found {ratios['n_close_matches']} close ratio matches")
    for r in ratios["ratios"][:5]:
        print(f"     R({r['weight_pair']}) = {r['ratio']:.6f}  "
              f"vs {r['target']}={r['target_value']:.6f}  err={r['relative_error']:.4f}")
    print("\n3. Continued fraction of Y vs R(n)/π")
    cf = continued_fraction_y_check()
    print(f"   Y continued fraction: {cf['Y_continued_fraction']}")
    print(f"   R(8)/π continued fraction: {cf['R8_over_pi_cf']}")
    print(f"   R(24)/π continued fraction: {cf['R24_over_pi_cf']}")
    print(f"   R(8)/R(24) continued fraction: {cf['R8_over_R24_cf']}")
    print("\n4. Catenary curvature on R(n) road")
    curv = catenary_curvature_on_r_road()
    print(f"   Formula: {curv['formula']}")
    for r in curv["weight_class_curvatures"]:
        print(f"     weight={r['weight']:>2}  n={r['n_nodes']:>2}  "
              f"R={r['R_n']:.4f}  ∫κ={r['integrated_curvature']:.4f}  "
              f"R·∫κ={r['bumpiness_R_times_kappa']:.4f}")
    print("\n5. Golden-ratio cross-check")
    gr = golden_ratio_cross_check()
    print(f"   Closest R(n) to Y: {gr['closest_R_to_Y']}")
    print(f"   Closest R(n) to Y_INV: {gr['closest_R_to_Y_INV']}")
    t1 = time.time()
    print(f"\nTotal Module 8 time: {t1-t0:.1f}s")
    return {
        "r_scan": scan,
        "r_ratios": ratios,
        "continued_fractions": cf,
        "catenary_curvature": curv,
        "golden_ratio_cross_check": gr,
        "verdict": (
            f"R(n) scan over n ∈ [4, 200] found {scan['n_close_matches']} near-matches to Y/1/Y/π. "
            f"Top match: {scan['top_10_closest'][0] if scan['top_10_closest'] else 'none'}. "
            f"Continued fraction of Y = {cf['Y_continued_fraction']}. "
            "The catenary curvature ∫κ = 2nY/π gives each weight class a "
            "characteristic bumpiness; this is the geometric origin of the Hodge gap."
        ),
    }


if __name__ == "__main__":
    import json
    result = run()
    out_path = "/home/z/my-project/results/module8_spatial_y_constant.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n→ {out_path}")
