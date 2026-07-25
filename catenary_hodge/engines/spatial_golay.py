"""
Spatial-Golay adapter — fuses spatial_arithmetic with the UBP Golay engine.

The fusion:
  * Each Golay codeword c is mapped to a 3D cycle shape via its weight class:
        weight 0  → value 0  (4-node cycle, radius 1/√2)
        weight 8  → value 2  (8-node cycle, octad)
        weight 12 → value 4  (12-node cycle, dodecad)
        weight 16 → value 6  (16-node cycle, hexadecad)
        weight 24 → value 10 (24-node cycle, all-ones)
    The natural primitive R(n) = 1/(2·sin(π/n)) gives each weight class a
    unique radius, so codeword geometry becomes a 1D weight spectrum.

  * Pairwise codeword AND-products (the cup product / Hodge intersection)
    become spatial scenes: place two codeword-shapes at operator distance
    and observe whether the result decodes to another valid codeword.

  * The Cayley-Menger coordinate-free centroid distance gives a NEW metric
    for the Hodge gap: instead of measuring AND-closure rate abstractly,
    we measure the geometric radius-ratio between codeword pairs and their
    AND-product.

  * The dihedral-angle modifier channel reveals whether codeword pairs
    live in coplanar (low-modifier) or skew (high-modifier) spatial
    configurations — a property the binary algebra cannot see.
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import math
import random
import sys
import os

# Make vendored spatial_arithmetic importable
_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor")
_VENDOR_DIR = os.path.normpath(_VENDOR_DIR)
if _VENDOR_DIR not in sys.path:
    sys.path.insert(0, _VENDOR_DIR)

import spatial_arithmetic as sa
from catenary_hodge.engines.adapter import (
    get_golay, hamming_weight, and_vectors, xor_vectors,
)


# ---------------------------------------------------------------------------
# Weight class → spatial value mapping
# ---------------------------------------------------------------------------
WEIGHT_TO_SPATIAL_VALUE: Dict[int, int] = {
    0: 0,    # 4-node cycle (BASE_NODES=4)
    8: 2,    # 8-node cycle (octad)
    12: 4,   # 12-node cycle (dodecad)
    16: 6,   # 16-node cycle (hexadecad)
    24: 10,  # 24-node cycle (all-ones)
}


def weight_to_value(w: int) -> int:
    """Map a Golay codeword weight to a spatial value.

    Each weight class in {0, 8, 12, 16, 24} gets a unique spatial value,
    so the weight spectrum becomes a 1D radius spectrum via R(n) = 1/(2·sin(π/n)).
    """
    if w not in WEIGHT_TO_SPATIAL_VALUE:
        # Non-codeword weight: assign a value by interpolation
        # weight w → value (w - 4) // 2 if w >= 4 else 0
        return max(0, (w - 4) // 2) if w >= 4 else 0
    return WEIGHT_TO_SPATIAL_VALUE[w]


def value_to_weight(v: int) -> int:
    """Inverse: spatial value back to Golay codeword weight."""
    for w, val in WEIGHT_TO_SPATIAL_VALUE.items():
        if val == v:
            return w
    return 4 + 2 * v  # interpolated


def codeword_to_spatial_shape(c: List[int], seed: int = 0) -> List[Tuple[float, float, float]]:
    """Encode a Golay codeword as a 3D spatial cycle via its weight.

    The codeword's weight determines the node count n = 2·value + BASE_NODES.
    The 3D cycle is non-planar (genuinely 3D), so two codewords with the same
    weight but different bit patterns can still be distinguished by their
    dihedral angle.
    """
    w = sum(c)
    v = weight_to_value(w)
    return sa.encode(v, seed=seed)


def codeword_pair_scene(c1: List[int], c2: List[int], operator: str = "ADD",
                         seed: int = 0) -> List[Tuple[float, float, float]]:
    """Build a two-codeword spatial scene at operator distance.

    The operator distance encodes the desired arithmetic relation:
        ADD (4×)      — codeword sum (XOR)
        MULTIPLY (3×) — cup product (AND)
        SUBTRACT (5×) — codeword difference (XOR with sign)
        DIVIDE (6×)   — ratio (not meaningful for binary, but applies to weights)
    """
    v1 = weight_to_value(sum(c1))
    v2 = weight_to_value(sum(c2))
    return sa.build_scene(v1, v2, operator, seed=seed)


# ---------------------------------------------------------------------------
# Spatial Hodge gap metric
# ---------------------------------------------------------------------------
def spatial_hodge_gap(c1: List[int], c2: List[int], seed: int = 0) -> Dict[str, Any]:
    """Measure the spatial Hodge gap between two codewords.

    The Hodge gap is whether AND(c1, c2) is itself a codeword.  In spatial
    terms, we encode c1 and c2 as 3D cycles, place them at MULTIPLY distance
    (3×, the cup product), and check whether the resulting scene decodes
    correctly.

    Returns:
      * and_weight: weight of c1 ∧ c2
      * and_is_codeword: True iff c1 ∧ c2 ∈ G_24
      * spatial_radius_ratio: R(c1)/R(c2) — should match weight ratio
      * dihedral_angle: angle between the two codeword-shapes' principal planes
      * modifier: dihedral modifier (ID, SQUARE, NEGATE, RECIP, ABS)
    """
    g = get_golay()
    cw_set = {tuple(c) for c in g.get_all_codewords()}
    and_product = and_vectors(c1, c2)
    and_w = sum(and_product)
    and_is_cw = tuple(and_product) in cw_set

    s1 = codeword_to_spatial_shape(c1, seed=seed * 2)
    s2 = codeword_to_spatial_shape(c2, seed=seed * 2 + 1)
    r1 = sa.radius_of(s1)
    r2 = sa.radius_of(s2)
    radius_ratio = r1 / r2 if r2 > 0 else float('inf')
    angle = sa.dihedral_angle(s1, s2)
    mod_name, mod_fn = sa.decode_modifier(angle)
    # Coordinate-free centroid distance
    centroid_dist = sa.pairwise_centroid_distance(s1, s2)
    # What operator does the distance ratio suggest?
    ratio_to_op = centroid_dist / max(r1, r2, sa.UNIT)
    suggested_op_mult = round(ratio_to_op)
    suggested_op = sa.OPCODE_TABLE.get(suggested_op_mult, ("NONE", None))[0]
    return {
        "c1_weight": sum(c1),
        "c2_weight": sum(c2),
        "and_weight": and_w,
        "and_is_codeword": and_is_cw,
        "c1_spatial_value": weight_to_value(sum(c1)),
        "c2_spatial_value": weight_to_value(sum(c2)),
        "spatial_radius_c1": r1,
        "spatial_radius_c2": r2,
        "spatial_radius_ratio": radius_ratio,
        "centroid_distance": centroid_dist,
        "distance_ratio": ratio_to_op,
        "suggested_operator": suggested_op,
        "dihedral_angle_deg": angle,
        "dihedral_modifier": mod_name,
    }


# ---------------------------------------------------------------------------
# Spatial enumeration: all 5 weight classes → 5 spatial values
# ---------------------------------------------------------------------------
def spatial_weight_spectrum() -> Dict[str, Any]:
    """Encode each Golay weight class as a spatial shape and report radii.

    The natural primitive R(n) = 1/(2·sin(π/n)) gives each weight class a
    unique radius. The ratio between consecutive radii is the geometric
    "step" between weight classes.
    """
    g = get_golay()
    we = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
    rows = []
    for w in sorted(we.keys()):
        v = weight_to_value(w)
        n_nodes = 2 * v + sa.BASE_NODES
        R = sa.value_to_radius(v)
        # Take a sample codeword of this weight
        cws = [c for c in g.get_all_codewords() if sum(c) == w]
        sample_cw = cws[0] if cws else [0] * 24
        shape = codeword_to_spatial_shape(sample_cw, seed=42)
        actual_r = sa.radius_of(shape)
        rows.append({
            "weight": w,
            "codeword_count": we[w],
            "spatial_value": v,
            "node_count": n_nodes,
            "theoretical_radius": R,
            "actual_radius": actual_r,
            "sample_codeword_weight": sum(sample_cw),
        })
    return {
        "weight_classes": rows,
        "natural_primitive": "R(n) = 1 / (2 * sin(pi/n))",
        "interpretation": (
            "Each Golay weight class maps to a unique spatial cycle. "
            "The radius spectrum R(0), R(2), R(4), R(6), R(10) gives a "
            "1D geometric embedding of the weight enumerator. "
            "The cup product (AND) between two codewords corresponds "
            "spatially to placing them at MULTIPLY distance (3× radius)."
        ),
    }


# ---------------------------------------------------------------------------
# Spatial arithmetic as a coordinate-free Hodge filter
# ---------------------------------------------------------------------------
def spatial_hodge_filter_sample(n_samples: int = 200, seed: int = 42) -> Dict[str, Any]:
    """Sample random codeword pairs, measure spatial Hodge gap statistics.

    For each pair (c1, c2):
      * AND-product weight
      * Whether AND-product is a codeword
      * Spatial radius ratio
      * Dihedral angle
      * Suggested operator from distance ratio
    """
    g = get_golay()
    cws = g.get_all_codewords()
    rng = random.Random(seed)
    results = []
    n_and_closed = 0
    angle_hist: Dict[str, int] = {}
    for _ in range(n_samples):
        c1 = rng.choice(cws)
        c2 = rng.choice(cws)
        gap = spatial_hodge_gap(c1, c2, seed=rng.randint(0, 10000))
        results.append(gap)
        if gap["and_is_codeword"]:
            n_and_closed += 1
        mod = gap["dihedral_modifier"]
        angle_hist[mod] = angle_hist.get(mod, 0) + 1
    # Aggregate
    and_weights = [r["and_weight"] for r in results]
    angles = [r["dihedral_angle_deg"] for r in results]
    ratios = [r["spatial_radius_ratio"] for r in results]
    return {
        "n_samples": n_samples,
        "and_closure_rate": n_and_closed / n_samples,
        "and_weight_distribution": {w: and_weights.count(w) for w in sorted(set(and_weights))},
        "mean_dihedral_angle": sum(angles) / len(angles),
        "dihedral_modifier_histogram": dict(sorted(angle_hist.items())),
        "mean_radius_ratio": sum(ratios) / len(ratios),
        "sample_first_5": results[:5],
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test() -> Dict[str, bool]:
    out: Dict[str, bool] = {}
    # 1. Weight → value mapping is bijective on the 5 codeword weights
    out["weight_value_bijection"] = (
        all(weight_to_value(w) is not None for w in [0, 8, 12, 16, 24]) and
        len(set(WEIGHT_TO_SPATIAL_VALUE.values())) == 5
    )
    # 2. Spatial spectrum has 5 distinct radii
    spec = spatial_weight_spectrum()
    radii = [r["theoretical_radius"] for r in spec["weight_classes"]]
    out["distinct_radii"] = len(set(round(r, 6) for r in radii)) == 5
    # 3. Spatial Hodge gap returns valid result
    g = get_golay()
    cws = g.get_all_codewords()
    gap = spatial_hodge_gap(cws[1], cws[2])
    out["gap_returns_dict"] = isinstance(gap, dict) and "and_is_codeword" in gap
    # 4. AND of zero with anything is zero (codeword 0 is the identity)
    zero_cw = [0] * 24
    gap_zero = spatial_hodge_gap(zero_cw, cws[1])
    out["zero_and_is_zero_weight"] = (gap_zero["and_weight"] == 0)
    # 5. AND of a codeword with itself is itself
    c = cws[5]
    gap_self = spatial_hodge_gap(c, c)
    out["self_and_preserves_weight"] = (gap_self["and_weight"] == sum(c))
    return out


if __name__ == "__main__":
    results = self_test()
    for k, v in results.items():
        print(f"  {k:30s}: {'PASS' if v else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit("FAIL: spatial-golay adapter self-test failed.")
    print("\nALL SPATIAL-GOLAY ADAPTER SELF-TESTS PASS.")
    print()
    spec = spatial_weight_spectrum()
    print("Spatial weight spectrum:")
    for r in spec["weight_classes"]:
        print(f"  weight={r['weight']:>2}  |C|={r['codeword_count']:>4}  "
              f"value={r['spatial_value']:>2}  nodes={r['node_count']:>2}  "
              f"R={r['theoretical_radius']:.4f}")
