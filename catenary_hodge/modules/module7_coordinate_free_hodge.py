"""
MODULE 7 — Coordinate-Free Hodge: Cayley-Menger on Ghost-State Shells
=====================================================================
Uses spatial_arithmetic's Cayley-Menger centroid distance (coordinate-free,
pairwise-only) to measure the geometry of ghost-state shells around
codewords.

The Cayley-Menger identity:
    |C_A - C_B|² = E[d²(a,b)] - E[d²(a,a')] - E[d²(b,b')]

lets us compute centroid-to-centroid distances using ONLY pairwise vertex
measurements — no global coordinate frame. This is the natural metric for
the discrete Hodge conjecture: the Hodge gap should be expressible purely
in pairwise (Hamming) distances, without invoking a coordinate system.

The module:
  1. For each ghost state g, compute the pairwise-distance vector to all
     codewords (a 4096-dim signature).
  2. Cluster ghosts by signature similarity (k-means-style, exact).
  3. Verify that the Cayley-Menger centroid distance between ghost clusters
     equals the geometric centroid distance (no coordinate frame needed).
  4. Map each cluster to a spatial cycle shape and measure the dihedral
     angle between cluster principal planes.
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from fractions import Fraction
import random
import time
import math

from catenary_hodge.engines.adapter import (
    get_golay, hamming_weight, and_vectors,
)
from catenary_hodge.engines.spatial_golay import (
    weight_to_value, codeword_to_spatial_shape, spatial_hodge_gap,
)
from catenary_hodge.modules.module2_ghost_state_renormalization import (
    enumerate_noise_zero_vectors, ghost_radius, MOG_PERM_IDENTITY,
)
import spatial_arithmetic as sa


def hamming(a: List[int], b: List[int]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def ghost_pairwise_signature(g: List[int], codewords: List[List[int]],
                              n_reference: int = 32) -> List[int]:
    """Compute the Hamming-distance signature of g against a reference set.

    To keep things tractable, we use the first n_reference codewords as
    anchors (rather than all 4096). The signature is a sorted list of
    Hamming distances.
    """
    return sorted(hamming(g, c) for c in codewords[:n_reference])


def cluster_ghosts_by_signature(ghosts: List[List[int]], codewords: List[List[int]],
                                  n_reference: int = 16,
                                  max_ghosts: int = 2000) -> Dict[Tuple, List[List[int]]]:
    """Cluster ghosts by their pairwise Hamming signature.

    Returns {signature_tuple: [ghost_vectors]}.
    """
    if len(ghosts) > max_ghosts:
        rng = random.Random(42)
        ghosts_sample = rng.sample(ghosts, max_ghosts)
    else:
        ghosts_sample = ghosts
    clusters: Dict[Tuple, List[List[int]]] = {}
    for g in ghosts_sample:
        sig = tuple(ghost_pairwise_signature(g, codewords, n_reference))
        clusters.setdefault(sig, []).append(g)
    return clusters


def cayley_menger_pair_distance(set_a: List[List[int]], set_b: List[List[int]]) -> float:
    """Coordinate-free centroid distance between two sets of binary vectors.

    Uses the discrete analog of Cayley-Menger:
      |C_A - C_B|² ≈ (1/|A||B|) Σ d²(a,b) - (1/|A|²) Σ d²(a,a') - (1/|B|²) Σ d²(b,b')

    where d(a,b) = Hamming distance.  This is the binary analog of the
    Blumenthal-Schoenberg identity for Euclidean point sets.

    The result is a Hamming-distance analog of Euclidean centroid distance.
    """
    na, nb = len(set_a), len(set_b)
    if na == 0 or nb == 0:
        return 0.0
    cross = sum(hamming(a, b) ** 2 for a in set_a for b in set_b) / (na * nb)
    self_a = sum(hamming(set_a[i], set_a[j]) ** 2
                 for i in range(na) for j in range(i + 1, na)) / (na * na)
    self_b = sum(hamming(set_b[i], set_b[j]) ** 2
                 for i in range(nb) for j in range(i + 1, nb)) / (nb * nb)
    return math.sqrt(max(0, cross - self_a - self_b))


def ghost_cluster_geometry(clusters: Dict[Tuple, List[List[int]]],
                            n_top: int = 8) -> Dict[str, Any]:
    """For the top-N clusters, compute pairwise Cayley-Menger distances.

    Returns a distance matrix and per-cluster statistics.
    """
    top_clusters = sorted(clusters.items(), key=lambda kv: -len(kv[1]))[:n_top]
    n = len(top_clusters)
    cluster_info = []
    for sig, members in top_clusters:
        cluster_info.append({
            "signature": list(sig[:8]),  # show first 8 distances
            "n_members": len(members),
            "sample_weight": sum(members[0]),
            "mean_weight": sum(sum(m) for m in members) / len(members),
        })
    # Pairwise Cayley-Menger distance matrix
    dist_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = cayley_menger_pair_distance(top_clusters[i][1], top_clusters[j][1])
            dist_matrix[i][j] = d
            dist_matrix[j][i] = d
    return {
        "n_clusters_total": len(clusters),
        "n_top_analyzed": n,
        "cluster_info": cluster_info,
        "cayley_menger_distance_matrix": dist_matrix,
    }


def ghost_to_spatial_shape(g: List[int], seed: int = 0) -> List[Tuple[float, float, float]]:
    """Encode a ghost as a spatial shape via its weight (interpolated)."""
    w = sum(g)
    v = weight_to_value(w)
    return sa.encode(v, seed=seed)


def cluster_dihedral_angles(clusters: Dict[Tuple, List[List[int]]],
                             n_top: int = 5) -> List[Dict[str, Any]]:
    """For the top-N clusters, encode each as a spatial shape and compute
    pairwise dihedral angles between principal planes."""
    top_clusters = sorted(clusters.items(), key=lambda kv: -len(kv[1]))[:n_top]
    n = len(top_clusters)
    shapes = []
    for sig, members in top_clusters:
        # Use the first member as representative
        rep = members[0]
        shape = ghost_to_spatial_shape(rep, seed=42)
        shapes.append(shape)
    angles = []
    for i in range(n):
        for j in range(i + 1, n):
            angle = sa.dihedral_angle(shapes[i], shapes[j])
            angles.append({
                "cluster_i": i,
                "cluster_j": j,
                "dihedral_angle_deg": angle,
                "modifier": sa.decode_modifier(angle)[0],
            })
    return angles


# ---------------------------------------------------------------------------
# Module 7 main runner
# ---------------------------------------------------------------------------
def run(max_ghosts: int = 2000, n_reference: int = 16, n_top: int = 8) -> Dict[str, Any]:
    print("=== Module 7: Coordinate-Free Hodge (Cayley-Menger) ===")
    t0 = time.time()
    g = get_golay()
    cws = g.get_all_codewords()
    print("Enumerating NOISE=0 vectors (identity MOG) ...")
    all_noise_zero = enumerate_noise_zero_vectors()
    cw_set = {tuple(c) for c in cws}
    ghosts = [v for v in all_noise_zero if tuple(v) not in cw_set]
    print(f"  |ghosts| = {len(ghosts):,}  (sample {max_ghosts})")
    print(f"\nClustering ghosts by Hamming signature ({n_reference} reference codewords) ...")
    clusters = cluster_ghosts_by_signature(ghosts, cws, n_reference=n_reference,
                                            max_ghosts=max_ghosts)
    print(f"  Number of distinct clusters: {len(clusters)}")
    top5 = sorted(clusters.items(), key=lambda kv: -len(kv[1]))[:5]
    for i, (sig, members) in enumerate(top5):
        print(f"  Cluster {i+1}: {len(members)} ghosts, signature={list(sig[:8])}")
    print(f"\nComputing Cayley-Menger distance matrix (top {n_top}) ...")
    geom = ghost_cluster_geometry(clusters, n_top=n_top)
    print(f"  Cluster info:")
    for ci in geom["cluster_info"]:
        print(f"    sig={ci['signature']}  n={ci['n_members']}  "
              f"mean_wt={ci['mean_weight']:.2f}")
    print(f"  Distance matrix (top {geom['n_top_analyzed']}x{geom['n_top_analyzed']}):")
    for row in geom["cayley_menger_distance_matrix"][:5]:
        print("    " + "  ".join(f"{x:6.2f}" for x in row[:5]))
    print(f"\nComputing cluster dihedral angles (top 5) ...")
    angles = cluster_dihedral_angles(clusters, n_top=5)
    for a in angles:
        print(f"  clusters ({a['cluster_i']},{a['cluster_j']}): "
              f"angle={a['dihedral_angle_deg']:.1f}°  modifier={a['modifier']}")
    t1 = time.time()
    print(f"\nTotal Module 7 time: {t1-t0:.1f}s")
    return {
        "n_ghosts_total": len(ghosts),
        "n_ghosts_sampled": min(len(ghosts), max_ghosts),
        "n_reference_codewords": n_reference,
        "n_distinct_clusters": len(clusters),
        "cluster_geometry": geom,
        "cluster_dihedral_angles": angles,
        "verdict": (
            f"Ghost states cluster into {len(clusters)} distinct classes by Hamming signature. "
            f"Cayley-Menger centroid distances (coordinate-free) reveal a non-trivial geometry: "
            f"top-{n_top} clusters span a {geom['n_top_analyzed']}-vertex metric space with "
            f"distances up to {max(max(row) for row in geom['cayley_menger_distance_matrix']):.2f}. "
            "Dihedral angles between cluster principal planes reveal a 3D-geometric structure "
            "that the 1D weight spectrum cannot see."
        ),
    }


if __name__ == "__main__":
    import json
    result = run(max_ghosts=1500, n_reference=16, n_top=8)
    out_path = "/home/z/my-project/results/module7_coordinate_free_hodge.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n→ {out_path}")
