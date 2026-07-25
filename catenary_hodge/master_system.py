"""
CAPSTONE — The 3-Axis Emergent Master System
=============================================
Directive (from map_dimension_projection_1.txt):
  Every system can be uniquely placed using a 3-Axis Coordinate System:
    Axis 1: Topological Simplex / Form Degree (k-Forms) → Determines the Field Operator
    Axis 2: Preserved Invariant / Projection Kernel → Determines the Projection Style
    Axis 3: Discrete Substrate Dimension (n-D Topology) → Determines the Code/Polytope Geometry

This module constructs the 3-axis master system as a Python data structure,
validates d²=0 (the unifying axiom of discrete exterior calculus), and
maps every system element to its (k-form, projection-kernel, substrate-dim) coordinate.

The de Rham complex in the UBP substrate:
  k=0 (vertex)  : Code Weight W(v) / Energy Potential E(v)         ↔ Gradient ∇f
  k=1 (edge)    : XOR Parity Loop / Parity Check Syndrome          ↔ Curl ∇×A
  k=2 (face)    : AND Mass Defect / Flux Deficit                   ↔ Divergence ∇·A
  k=3 (cell)    : Substrate Density / MOG Octad Density            ↔ Volume Integral

The d²=0 axiom in UBP:
  H · G^T = 0 (mod 2)  — the parity check matrix annihilates the generator.
  This is the discrete analog of "the boundary of a boundary is zero".
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import itertools

from catenary_hodge.engines.adapter import (
    get_golay, get_leech, get_pp, hamming_weight, xor_vectors, and_vectors,
    mat_mul_mod2, mat_T_mod2,
)


# ---------------------------------------------------------------------------
# Axis 1: de Rham chain (k-forms and their UBP discrete equivalents)
# ---------------------------------------------------------------------------
DERHAM_CHAIN = [
    {
        "k": 0,
        "geometric_entity": "Vertex / Point",
        "field_question": "Where does scalar value increase fastest?",
        "vector_calculus": "Gradient ∇f",
        "ubp_equivalent": "Code Weight W(v) / Energy Potential E(v)",
        "operator_symbol": "∇",
    },
    {
        "k": 1,
        "geometric_entity": "Edge / Line",
        "field_question": "Is the field rotating around this loop?",
        "vector_calculus": "Curl ∇×A",
        "ubp_equivalent": "XOR Parity Loop / Parity Check Syndrome s(v)=H·v",
        "operator_symbol": "∇×",
    },
    {
        "k": 2,
        "geometric_entity": "Face / Surface",
        "field_question": "Is field flowing out of or into this boundary?",
        "vector_calculus": "Divergence ∇·A",
        "ubp_equivalent": "AND Mass Defect / Flux Deficit Δm(a,b)",
        "operator_symbol": "∇·",
    },
    {
        "k": 3,
        "geometric_entity": "Cell / Volume",
        "field_question": "What is the enclosed density charge?",
        "vector_calculus": "Volume integral ∭ρ dV",
        "ubp_equivalent": "Substrate Density / MOG Octad Density (759 octads)",
        "operator_symbol": "∭",
    },
]


# ---------------------------------------------------------------------------
# Axis 2: Projection kernels (preserved invariant → projection style)
# ---------------------------------------------------------------------------
PROJECTION_KERNELS = [
    {
        "kernel": "Linear",
        "name": "Orthographic",
        "preserves": "Linear subspaces / Hamming weights",
        "math_definition": "P projects along parallel lines perpendicular to plane; ker(P) = V⊥",
        "use_case": "Linear binary codes (G_24 generator matrix projections, parity checks)",
        "ubp_application": "Codeword enumeration, syndrome calculation, AND/XOR closure tests",
    },
    {
        "kernel": "Conformal",
        "name": "Stereographic",
        "preserves": "Angles, circles, conformal metrics (NRCI)",
        "math_definition": "P projects from pole N ∈ S^n onto tangential hyperplane",
        "use_case": "Spherical polytopes, Leech lattice kissing points (196,560 vectors)",
        "ubp_application": "NRCI field analysis, Module 5 Leech harmonic projection",
    },
    {
        "kernel": "Topological",
        "name": "Schlegel Diagram",
        "preserves": "Face-adjacency, cell connectivity, boundary intersections",
        "math_definition": "Perspective projection from point just outside one top-dimensional cell",
        "use_case": "4D configuration spaces (8-cell, 24-cell, 120-cell), robotics path planning",
        "ubp_application": "MOG column adjacency, Module 2 ghost-state shell topology",
    },
    {
        "kernel": "Symmetry",
        "name": "Petrie Polygon",
        "preserves": "Maximum finite rotational symmetry groups (W(F_4), W(H_4), M_24)",
        "math_definition": "Projection onto 2D plane defined by the Coxeter element",
        "use_case": "Hunting for core resonances, rotational invariants, harmonic symmetries",
        "ubp_application": "Y-constant harmonic peaks, Module 5 angular power spectrum",
    },
]


# ---------------------------------------------------------------------------
# Axis 3: Substrate hierarchy (4D polytopes → 24D LDP)
# ---------------------------------------------------------------------------
SUBSTRATE_HIERARCHY = [
    {
        "dimension": 4,
        "discrete_code": "[4,2,2] trivial",
        "polytope": "5-cell / 8-cell (tesseract)",
        "field_operator": "Scalar (Gradient)",
        "ubp_constants": "Y^0 = 1 (Identity)",
        "and_closure": 1.0,
        "xor_closure": 1.0,
        "dnc_ratio": 0.50,
    },
    {
        "dimension": 8,
        "discrete_code": "[8,4,4] extended Hamming",
        "polytope": "16-cell / 24-cell",
        "field_operator": "Vector field (Curl)",
        "ubp_constants": "Y^1 = 0.2647",
        "and_closure": 0.344,
        "xor_closure": 1.0,
        "dnc_ratio": 0.50,
    },
    {
        "dimension": 12,
        "discrete_code": "[12,6,6] ternary Golay",
        "polytope": "120-cell",
        "field_operator": "Flux / Surface (Divergence)",
        "ubp_constants": "Y^2 = 0.0701",
        "and_closure": 0.054,
        "xor_closure": 0.004,  # not 1.0 because ternary, XOR isn't the right op
        "dnc_ratio": 0.50,
    },
    {
        "dimension": 14,
        "discrete_code": "[14,7,2] truncated Golay (naive truncation)",
        "polytope": "(none standard — transition zone)",
        "field_operator": "Mixed (Phase transition)",
        "ubp_constants": "Y^3 = 0.0186",
        "and_closure": 0.336,
        "xor_closure": 1.0,
        "dnc_ratio": 0.143,
        "note": "Phase transition zone; naive truncation breaks Steiner structure",
    },
    {
        "dimension": 24,
        "discrete_code": "[24,12,8] extended binary Golay",
        "polytope": "600-cell / Leech Lattice Λ_24",
        "field_operator": "Full Hodge Diamond",
        "ubp_constants": "Y^6 = 0.000342 (Information layer)",
        "and_closure": 0.010,
        "xor_closure": 1.0,
        "dnc_ratio": 0.333,
    },
]


# ---------------------------------------------------------------------------
# The Rosetta Stone: projection decision matrix
# ---------------------------------------------------------------------------
ROSETTA_STONE = [
    {
        "input_goal": "Track rate of code energy change",
        "form_degree": 0,
        "operator_required": "Gradient (∇E)",
        "optimal_projection": "Orthographic",
        "structural_example": "Hamming weight / energy gradient across code states",
    },
    {
        "input_goal": "Detect parity loops / phase rotations",
        "form_degree": 1,
        "operator_required": "Curl (∇×A)",
        "optimal_projection": "Petrie Polygon",
        "structural_example": "Syndrome check loops / automorphism subgroup cycles",
    },
    {
        "input_goal": "Measure information flow / leakage",
        "form_degree": 2,
        "operator_required": "Divergence (∇·A)",
        "optimal_projection": "Stereographic",
        "structural_example": "AND mass defect flux across MOG quadrants",
    },
    {
        "input_goal": "Map robot configuration space paths",
        "form_degree": 3,
        "operator_required": "Volume integration",
        "optimal_projection": "Schlegel Diagram",
        "structural_example": "4D tesseract / 24-cell collision-free path mapping",
    },
    {
        "input_goal": "Analyze coherence / NRCI fields",
        "form_degree": "Metric field",
        "operator_required": "Conformal Laplacian Δ_g",
        "optimal_projection": "Hyperspherical Stereographic",
        "structural_example": "S³ → R³ projection of Leech lattice kissing points",
    },
]


# ---------------------------------------------------------------------------
# d²=0 axiom verification (the unifying axiom)
# ---------------------------------------------------------------------------
def verify_d_squared_zero() -> Dict[str, Any]:
    """Verify d²=0 in the UBP substrate: H · G^T = 0 (mod 2).

    This is the discrete analog of "the boundary of a boundary is zero":
      * curl(grad(f)) = 0  ↔  H annihilates the row-space of G
      * div(curl(A)) = 0   ↔  Every codeword's syndrome is zero
    """
    g = get_golay()
    HGT = mat_mul_mod2(g.H, mat_T_mod2(g.G))
    hgt_zero = all(HGT[i][j] == 0 for i in range(12) for j in range(12))
    # Also verify: every codeword's syndrome is zero (the operational d²=0)
    cws = g.get_all_codewords()
    all_zero_syn = all(g.syndrome_weight(c) == 0 for c in cws)
    # The boundary-of-boundary check on the cellular level:
    # For each octad, count its 8-element support; for each pair of octads,
    # check that their AND-product (intersection) is itself in the Steiner system
    # at weights {0, 2, 4, 8}.  This is the "boundary of a 2-boundary is zero".
    octads = g.get_octads()[:50]  # sample
    intersection_weights = set()
    for a in octads[:20]:
        for b in octads[:20]:
            x = and_vectors(a, b)
            intersection_weights.add(sum(x))
    steiner_ok = intersection_weights.issubset({0, 2, 4, 8})
    return {
        "H_GT_zero_mod2": hgt_zero,
        "all_codewords_zero_syndrome": all_zero_syn,
        "n_codewords_tested": len(cws),
        "octad_intersection_weights": sorted(intersection_weights),
        "steiner_intersection_subset_of_0248": steiner_ok,
        "d_squared_zero_axiom_holds": hgt_zero and all_zero_syn and steiner_ok,
        "interpretation": (
            "H · G^T = 0 (mod 2) is the discrete analog of d²=0 in differential geometry. "
            "It means: every codeword's syndrome is zero (the parity-check operator annihilates "
            "the generator's row-space).  This is the unifying axiom that connects UBP's linear "
            "algebra to discrete exterior calculus."
        ),
    }


# ---------------------------------------------------------------------------
# Build the 3-axis coordinate system as a dict
# ---------------------------------------------------------------------------
def build_master_system() -> Dict[str, Any]:
    """Return the complete 3-axis master system."""
    d2_check = verify_d_squared_zero()
    return {
        "axis_1_form_degree": DERHAM_CHAIN,
        "axis_2_projection_kernels": PROJECTION_KERNELS,
        "axis_3_substrate_hierarchy": SUBSTRATE_HIERARCHY,
        "rosetta_stone": ROSETTA_STONE,
        "d_squared_zero_axiom": d2_check,
        "summary_directives": [
            "Treat d²=0 as the unifying axiom: align all LDP linear algebra (H·G^T=0) with discrete exterior derivatives.",
            "Never force rendering styles: Schlegel for topology/adjacency, Stereographic for metric fields/NRCI, Petrie for symmetry/harmonics, Orthographic for linear parity/weights.",
            "Map operators to form dimensions: Gradient → vertices, Curl → edges, Divergence → faces. The equations cease to be arbitrary — they become inevitable consequences of discrete geometry.",
        ],
        "mapping_count": {
            "form_degrees": len(DERHAM_CHAIN),
            "projection_kernels": len(PROJECTION_KERNELS),
            "substrate_dimensions": len(SUBSTRATE_HIERARCHY),
            "rosetta_entries": len(ROSETTA_STONE),
            "total_3axis_cells": len(DERHAM_CHAIN) * len(PROJECTION_KERNELS) * len(SUBSTRATE_HIERARCHY),
        },
    }


# ---------------------------------------------------------------------------
# Place any system element on the 3-axis grid
# ---------------------------------------------------------------------------
def place_on_grid(form_degree: int, projection_kernel: str, substrate_dim: int) -> Dict[str, Any]:
    """Place a system element at (form_degree, projection_kernel, substrate_dim)."""
    k_match = next((d for d in DERHAM_CHAIN if d["k"] == form_degree), None)
    p_match = next((p for p in PROJECTION_KERNELS if p["name"].lower() == projection_kernel.lower()), None)
    s_match = next((s for s in SUBSTRATE_HIERARCHY if s["dimension"] == substrate_dim), None)
    return {
        "coordinate": (form_degree, projection_kernel, substrate_dim),
        "form_degree_info": k_match,
        "projection_kernel_info": p_match,
        "substrate_info": s_match,
        "valid": all([k_match, p_match, s_match]),
    }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------
def run() -> Dict[str, Any]:
    print("=== Capstone: 3-Axis Emergent Master System ===")
    system = build_master_system()
    print(f"\nAxis 1 — Form Degree (de Rham chain):")
    for entry in system["axis_1_form_degree"]:
        print(f"  k={entry['k']} ({entry['geometric_entity']:20s}) "
              f"→ {entry['vector_calculus']:12s} ↔ {entry['ubp_equivalent']}")
    print(f"\nAxis 2 — Projection Kernels:")
    for entry in system["axis_2_projection_kernels"]:
        print(f"  {entry['name']:18s} ({entry['kernel']:12s}) "
              f"preserves: {entry['preserves']}")
    print(f"\nAxis 3 — Substrate Hierarchy:")
    for entry in system["axis_3_substrate_hierarchy"]:
        print(f"  {entry['dimension']:>2}D  {entry['discrete_code']:35s}  "
              f"d/n={entry['dnc_ratio']:.3f}  AND-cl={entry['and_closure']:.3f}  "
              f"polytope: {entry['polytope']}")
    print(f"\nRosetta Stone — Projection Decision Matrix:")
    for entry in system["rosetta_stone"]:
        print(f"  {entry['input_goal']:40s}  →  {entry['operator_required']:18s} "
              f"via {entry['optimal_projection']}")
    print(f"\nVerifying d²=0 axiom (H·G^T = 0 mod 2):")
    d2 = system["d_squared_zero_axiom"]
    print(f"  H·G^T = 0 (mod 2)             : {d2['H_GT_zero_mod2']}")
    print(f"  All codewords zero syndrome   : {d2['all_codewords_zero_syndrome']}")
    print(f"  Octad intersection weights    : {d2['octad_intersection_weights']}")
    print(f"  Subset of {{0,2,4,8}} (Steiner) : {d2['steiner_intersection_subset_of_0248']}")
    print(f"  d²=0 AXIOM HOLDS              : {d2['d_squared_zero_axiom_holds']}")
    print(f"\nMapping count:")
    for k, v in system["mapping_count"].items():
        print(f"  {k:30s}: {v}")
    return system


if __name__ == "__main__":
    import json
    result = run()
    out_path = "/home/z/my-project/results/capstone_master_system.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n→ {out_path}")
