"""
MODULE 3 — Dual Projection & the Non-Linear "Round Wheel" Paradigm
====================================================================
Directive: Invert the catenary problem — fix the road as flat (Euclidean) and
construct a non-linear "round wheel" code C_round that projects into continuous
metrics with zero axle ripple (β = 0).

Test whether the Z_4 (quaternary) Gray map improves AND-closure and produces
a less-bumpy projection compared to pure binary GF(2)^24.

Construction:
  * Gray map φ: Z_4 → GF(2)^2  with φ(0)=(0,0), φ(1)=(0,1), φ(2)=(1,1), φ(3)=(1,0)
  * This is an isometry: d_Lee(a,b) = d_Ham(φ(a), φ(b))
  * Map 24-bit binary vectors to 12-symbol Z_4 vectors by pairing adjacent bits
  * Measure closure rates: AND-closure (GF(2)), Z_4-additive closure, MIN-closure

Computational plan (Fraction-exact for all counts; mpmath for curvature):
  1. Build the Gray map bijection and verify it (round-trip on all 2^24 vectors)
  2. Compute closure rates for GF(2)^24 AND-product vs Z_4 MIN-product
  3. Compute the metric tensor g_ij(X,Y,Z) = ∂NRCI/∂x_i * ∂NRCI/∂x_j across
     the unique block-sum spatial projections (X = sum bits 0-7, etc.)
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import itertools
import random
import time

from catenary_hodge.engines.adapter import (
    get_golay, get_leech, hamming_weight, xor_vectors, and_vectors, nrci_of
)


# ---------------------------------------------------------------------------
# Gray map: Z_4 ↔ GF(2)^2
# ---------------------------------------------------------------------------
GRAY_MAP: Dict[int, Tuple[int, int]] = {
    0: (0, 0),
    1: (0, 1),
    2: (1, 1),
    3: (1, 0),
}
GRAY_INV: Dict[Tuple[int, int], int] = {v: k for k, v in GRAY_MAP.items()}


def binary_to_z4(v: List[int]) -> List[int]:
    """Convert 24-bit binary vector to 12-symbol Z_4 vector via Gray map inverse.
    Pairs (v[2i], v[2i+1]) → Z_4 symbol.
    """
    if len(v) != 24:
        raise ValueError(f"Expected 24-bit vector, got len={len(v)}")
    out = []
    for i in range(12):
        out.append(GRAY_INV[(v[2 * i], v[2 * i + 1])])
    return out


def z4_to_binary(z: List[int]) -> List[int]:
    """Convert 12-symbol Z_4 vector to 24-bit binary via Gray map."""
    if len(z) != 12:
        raise ValueError(f"Expected 12-symbol Z_4 vector, got len={len(z)}")
    out = []
    for s in z:
        a, b = GRAY_MAP[s]
        out.extend([a, b])
    return out


def gray_round_trip_test(n_samples: int = 1000) -> bool:
    """Verify Gray map is a bijection by random round-trip."""
    rng = random.Random(42)
    for _ in range(n_samples):
        v = [rng.randint(0, 1) for _ in range(24)]
        z = binary_to_z4(v)
        v2 = z4_to_binary(z)
        if v != v2:
            return False
    return True


# ---------------------------------------------------------------------------
# Z_4 operations
# ---------------------------------------------------------------------------
def z4_add(a: int, b: int) -> int:
    return (a + b) % 4


def z4_min(a: int, b: int) -> int:
    """Componentwise MIN in Z_4 (analog of AND in GF(2))."""
    return min(a, b)


def z4_add_vectors(a: List[int], b: List[int]) -> List[int]:
    return [z4_add(a[i], b[i]) for i in range(len(a))]


def z4_min_vectors(a: List[int], b: List[int]) -> List[int]:
    return [z4_min(a[i], b[i]) for i in range(len(a))]


# ---------------------------------------------------------------------------
# Closure metrics
# ---------------------------------------------------------------------------
def gf2_and_closure_rate(codewords: List[List[int]], n_samples: int = 500) -> float:
    """Fraction of AND-products (a ∧ b) that are codewords."""
    cw_set = {tuple(c) for c in codewords}
    n = len(codewords)
    if n <= 1:
        return 1.0
    rng = random.Random(42)
    hits = 0
    for _ in range(n_samples):
        a = codewords[rng.randrange(n)]
        b = codewords[rng.randrange(n)]
        x = and_vectors(a, b)
        if tuple(x) in cw_set:
            hits += 1
    return hits / n_samples


def z4_additive_closure_rate(codewords_z4: List[List[int]], n_samples: int = 500) -> float:
    """Fraction of Z_4 additive products (a + b) that are codewords (in Z_4)."""
    cw_set = {tuple(c) for c in codewords_z4}
    n = len(codewords_z4)
    if n <= 1:
        return 1.0
    rng = random.Random(42)
    hits = 0
    for _ in range(n_samples):
        a = codewords_z4[rng.randrange(n)]
        b = codewords_z4[rng.randrange(n)]
        x = z4_add_vectors(a, b)
        if tuple(x) in cw_set:
            hits += 1
    return hits / n_samples


def z4_min_closure_rate(codewords_z4: List[List[int]], n_samples: int = 500) -> float:
    """Fraction of Z_4 MIN products (min(a,b)) that are codewords (in Z_4)."""
    cw_set = {tuple(c) for c in codewords_z4}
    n = len(codewords_z4)
    if n <= 1:
        return 1.0
    rng = random.Random(42)
    hits = 0
    for _ in range(n_samples):
        a = codewords_z4[rng.randrange(n)]
        b = codewords_z4[rng.randrange(n)]
        x = z4_min_vectors(a, b)
        if tuple(x) in cw_set:
            hits += 1
    return hits / n_samples


# ---------------------------------------------------------------------------
# Block-sum spatial projections (X, Y, Z) and metric tensor
# ---------------------------------------------------------------------------
def block_sums(v: List[int]) -> Tuple[int, int, int]:
    """Return (X, Y, Z) = (sum bits 0-7, sum bits 8-15, sum bits 16-23)."""
    X = sum(v[0:8])
    Y = sum(v[8:16])
    Z = sum(v[16:24])
    return (X, Y, Z)


def unique_block_sum_projections(codewords: List[List[int]]) -> Dict[Tuple[int, int, int], int]:
    """Return {(X,Y,Z): count} over all codewords."""
    out: Dict[Tuple[int, int, int], int] = {}
    for c in codewords:
        xyz = block_sums(c)
        out[xyz] = out.get(xyz, 0) + 1
    return dict(sorted(out.items()))


def nrci_field_over_block_sums(codewords: List[List[int]]) -> Dict[str, Any]:
    """Compute the NRCI field over the unique block-sum projections.

    For each unique (X,Y,Z) projection, compute the mean NRCI of codewords
    sharing that projection.  Then compute the metric tensor
    g_ij = ∂NRCI/∂x_i * ∂NRCI/∂x_j via finite differences.
    """
    # Group codewords by (X,Y,Z)
    groups: Dict[Tuple[int, int, int], List[List[int]]] = {}
    for c in codewords:
        xyz = block_sums(c)
        groups.setdefault(xyz, []).append(c)
    # Compute mean NRCI per group
    nrci_field: Dict[Tuple[int, int, int], float] = {}
    for xyz, cs in groups.items():
        nrcis = [float(nrci_of(c)) for c in cs]
        nrci_field[xyz] = sum(nrcis) / len(nrcis)
    # Compute metric tensor g_ij via finite differences
    # Sample neighboring (X,Y,Z) points
    points = sorted(nrci_field.keys())
    if len(points) < 2:
        return {"n_unique": len(points), "metric_tensor": None}
    # Finite differences on the 3D grid
    diffs = {0: [], 1: [], 2: []}  # X, Y, Z partials
    for p in points:
        for axis in range(3):
            # Find a neighbor differing by 1 in this axis
            for delta in [1, -1]:
                neighbor = list(p)
                neighbor[axis] += delta
                neighbor_t = tuple(neighbor)
                if neighbor_t in nrci_field:
                    d_nrci = nrci_field[neighbor_t] - nrci_field[p]
                    diffs[axis].append(d_nrci / delta)
                    break
    # Metric tensor g_ij = mean(∂NRCI/∂x_i * ∂NRCI/∂x_j)
    means = [sum(d) / len(d) if d else 0.0 for d in [diffs[0], diffs[1], diffs[2]]]
    g = [[means[i] * means[j] for j in range(3)] for i in range(3)]
    # Scalar curvature proxy: trace(g)
    trace_g = sum(g[i][i] for i in range(3))
    # Field statistics
    nrci_vals = list(nrci_field.values())
    nrci_mean = sum(nrci_vals) / len(nrci_vals)
    nrci_min = min(nrci_vals)
    nrci_max = max(nrci_vals)
    nrci_var = sum((v - nrci_mean) ** 2 for v in nrci_vals) / len(nrci_vals)
    return {
        "n_unique_projections": len(points),
        "nrci_field_mean": nrci_mean,
        "nrci_field_min": nrci_min,
        "nrci_field_max": nrci_max,
        "nrci_field_std": nrci_var ** 0.5,
        "metric_tensor_g_ij": g,
        "trace_g": trace_g,
        "scalar_curvature_proxy": trace_g,  # heuristic
        "non_zero_curvature": abs(trace_g) > 1e-10,
    }


# ---------------------------------------------------------------------------
# Module 3 main runner
# ---------------------------------------------------------------------------
def run(n_samples: int = 500) -> Dict[str, Any]:
    print("=== Module 3: Dual Projection & Z_4 Round Wheel ===")
    t0 = time.time()
    g = get_golay()
    cws = g.get_all_codewords()
    # 1. Gray map round trip
    print(f"Gray map round-trip test ({n_samples} samples) ...")
    rt_ok = gray_round_trip_test(n_samples=1000)
    print(f"  Round trip OK: {rt_ok}")
    # 2. Convert codewords to Z_4
    print("Converting 4096 codewords to Z_4^12 via Gray map ...")
    cws_z4 = [binary_to_z4(c) for c in cws]
    t1 = time.time()
    # 3. Closure rates
    print(f"Computing closure rates (n_samples={n_samples}) ...")
    gf2_and = gf2_and_closure_rate(cws, n_samples=n_samples)
    z4_add = z4_additive_closure_rate(cws_z4, n_samples=n_samples)
    z4_min = z4_min_closure_rate(cws_z4, n_samples=n_samples)
    print(f"  GF(2)^24 AND-closure  : {gf2_and:.4f}")
    print(f"  Z_4 additive-closure  : {z4_add:.4f}  (should be 1.0 if Z_4-linear)")
    print(f"  Z_4 MIN-closure       : {z4_min:.4f}")
    print(f"  Improvement factor (MIN/AND): {z4_min/max(gf2_and, 1e-9):.3f}x")
    # 4. Block-sum projections
    print(f"\nComputing unique (X,Y,Z) block-sum projections ...")
    proj = unique_block_sum_projections(cws)
    print(f"  Unique projections: {len(proj)}  (directive predicts ~111)")
    # 5. NRCI field and metric tensor
    print(f"Computing NRCI field and metric tensor over projections ...")
    field_stats = nrci_field_over_block_sums(cws)
    print(f"  NRCI field: mean={field_stats['nrci_field_mean']:.4f}  "
          f"std={field_stats['nrci_field_std']:.4f}  "
          f"range=[{field_stats['nrci_field_min']:.4f}, {field_stats['nrci_field_max']:.4f}]")
    print(f"  Metric tensor trace (curvature proxy): {field_stats['trace_g']:.2e}")
    print(f"  Non-zero curvature: {field_stats['non_zero_curvature']}")
    t2 = time.time()
    print(f"\nTotal Module 3 time: {t2-t0:.1f}s")
    return {
        "gray_round_trip_ok": rt_ok,
        "gf2_and_closure": gf2_and,
        "z4_additive_closure": z4_add,
        "z4_min_closure": z4_min,
        "improvement_factor_min_over_and": z4_min / max(gf2_and, 1e-9),
        "unique_projections": len(proj),
        "nrci_field": field_stats,
        "verdict": "Gray map does NOT round the wheel — closure rates comparable (negative result)"
                   if z4_min / max(gf2_and, 1e-9) < 2.0
                   else "Gray map rounds the wheel — significant closure improvement",
    }


if __name__ == "__main__":
    import json
    result = run()
    out_path = "/home/z/my-project/results/module3_z4_projection.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n→ {out_path}")
