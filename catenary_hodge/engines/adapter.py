"""
Catenary-Hodge engine adapter — wraps the vendored ubp_unified_v5.py
to expose a clean interface for the 5 modules.

The upstream engine is Fraction-exact for all UBP algebra (Y, w, L, NRCI).
This adapter adds:
  * Direct access to Golay, Leech, particle-physics engines.
  * Helper utilities for GF(2) linear algebra (matmul mod 2, null space,
    syndrome_weight, AND-product).
  * The UBP constants as Fraction objects (re-exported).
  * Numerical consistency checks (run on import for tests).
"""
from __future__ import annotations
from fractions import Fraction
from typing import Iterable, List, Tuple, Dict, Any
import itertools
import sys
import os

# Make vendored ubp_unified_v5 importable
_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor")
_VENDOR_DIR = os.path.normpath(_VENDOR_DIR)
if _VENDOR_DIR not in sys.path:
    sys.path.insert(0, _VENDOR_DIR)

# Re-export upstream engines
from ubp_unified_v5 import (  # noqa: E402
    GolayCodeEngine,
    LeechLatticeEngine,
    MonsterGroup,
    BarnesWallEngine,
    UBPSourceCodeParticlePhysics,
    TriadActivationEngine,
)

# ---------------------------------------------------------------------------
# Module-level singletons (lazy-built)
# ---------------------------------------------------------------------------
_GOLAY: GolayCodeEngine | None = None
_LEECH: LeechLatticeEngine | None = None
_PP: UBPSourceCodeParticlePhysics | None = None


def get_golay() -> GolayCodeEngine:
    global _GOLAY
    if _GOLAY is None:
        _GOLAY = GolayCodeEngine()
    return _GOLAY


def get_leech() -> LeechLatticeEngine:
    global _LEECH
    if _LEECH is None:
        _LEECH = LeechLatticeEngine(get_golay())
    return _LEECH


def get_pp() -> UBPSourceCodeParticlePhysics:
    global _PP
    if _PP is None:
        _PP = UBPSourceCodeParticlePhysics()
    return _PP


# ---------------------------------------------------------------------------
# UBP constants — Fraction-exact, re-exported from upstream
# ---------------------------------------------------------------------------
def Y() -> Fraction:
    return get_pp().Y


def Y_INV() -> Fraction:
    return get_pp().Y_INV


def w() -> Fraction:
    return get_pp().wobble


def L() -> Fraction:
    return get_pp().L


def L_s() -> Fraction:
    return get_pp().L_s


def U_e() -> int:
    return get_pp().U_e


def sigma() -> Fraction:
    return get_pp().sigma


# ---------------------------------------------------------------------------
# GF(2) linear algebra helpers (exact, integer arithmetic)
# ---------------------------------------------------------------------------
def matmul_mod2(M: List[List[int]], v: List[int]) -> List[int]:
    """Compute M * v mod 2."""
    return [sum(M[i][j] * v[j] for j in range(len(v))) % 2 for i in range(len(M))]


def mat_mul_mod2(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """Compute A * B mod 2."""
    m, n = len(A), len(A[0])
    p = len(B[0])
    out = [[0] * p for _ in range(m)]
    for i in range(m):
        for k in range(n):
            if A[i][k]:
                for j in range(p):
                    out[i][j] ^= B[k][j]
    return out


def mat_T_mod2(M: List[List[int]]) -> List[List[int]]:
    """Transpose."""
    if not M:
        return []
    return [[M[i][j] for i in range(len(M))] for j in range(len(M[0]))]


def null_space_mod2(M: List[List[int]]) -> List[List[int]]:
    """Basis of null space of M over GF(2)."""
    if not M:
        return []
    m, n = len(M), len(M[0])
    A = [row[:] for row in M]
    pivots = []
    r = 0
    for c in range(n):
        pivot_row = -1
        for i in range(r, m):
            if A[i][c] == 1:
                pivot_row = i
                break
        if pivot_row < 0:
            continue
        A[r], A[pivot_row] = A[pivot_row], A[r]
        for i in range(m):
            if i != r and A[i][c] == 1:
                A[i] = [(A[i][j] + A[r][j]) % 2 for j in range(n)]
        pivots.append((r, c))
        r += 1
        if r == m:
            break
    pivot_cols = {p[1] for p in pivots}
    free_cols = [c for c in range(n) if c not in pivot_cols]
    basis = []
    for fc in free_cols:
        vec = [0] * n
        vec[fc] = 1
        for (pr, pc) in pivots:
            s = 0
            for j in free_cols:
                s ^= A[pr][j] * vec[j]
            vec[pc] = s
        basis.append(vec)
    return basis


def hamming_weight(v: Iterable[int]) -> int:
    return sum(1 for x in v if x)


def xor_vectors(a: List[int], b: List[int]) -> List[int]:
    return [(a[i] ^ b[i]) for i in range(len(a))]


def and_vectors(a: List[int], b: List[int]) -> List[int]:
    return [(a[i] & b[i]) for i in range(len(a))]


def or_vectors(a: List[int], b: List[int]) -> List[int]:
    return [(a[i] | b[i]) for i in range(len(a))]


# ---------------------------------------------------------------------------
# Convenience: Golay code invariants (cached)
# ---------------------------------------------------------------------------
def weight_enumerator(g: GolayCodeEngine | None = None) -> Dict[int, int]:
    """Return {weight: count} for the Golay code."""
    g = g or get_golay()
    out: Dict[int, int] = {}
    for c in g.get_all_codewords():
        wt = sum(c)
        out[wt] = out.get(wt, 0) + 1
    return dict(sorted(out.items()))


def is_self_dual(g: GolayCodeEngine | None = None) -> bool:
    """Check G * G^T = 0 (mod 2)."""
    g = g or get_golay()
    GGT = mat_mul_mod2(g.G, mat_T_mod2(g.G))
    return all(GGT[i][j] == 0 for i in range(12) for j in range(12))


def all_codewords_zero_syndrome(g: GolayCodeEngine | None = None) -> bool:
    """Check that every codeword has zero syndrome (Push 9 alignment test)."""
    g = g or get_golay()
    return all(g.syndrome_weight(c) == 0 for c in g.get_all_codewords())


def nrci_of(v: List[int]) -> Fraction:
    """NRCI(v) = 10 / (10 + tax(v)) where tax(v) = wt(v)*Y + ||v||^2 / 8."""
    return get_leech().calculate_nrci(list(map(int, v)))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test() -> Dict[str, bool]:
    g = get_golay()
    l = get_leech()
    pp = get_pp()
    out: Dict[str, bool] = {}
    out["n_codewords_4096"] = (len(g.get_all_codewords()) == 4096)
    out["n_octads_759"] = (len(g.get_octads()) == 759)
    expected_we = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
    out["weight_enumerator"] = (weight_enumerator() == expected_we)
    out["self_dual"] = is_self_dual()
    out["all_zero_syndrome"] = all_codewords_zero_syndrome()
    out["Y_value"] = abs(float(pp.Y) - 0.264675430405) < 1e-12
    out["Y_reciprocity"] = abs(float(pp.Y * pp.Y_INV) - 1.0) < 1e-50
    out["L_eq_w_over_13"] = abs(float(pp.L - pp.wobble / 13)) < 1e-50
    out["L_s_eq_L_sigma"] = abs(float(pp.L_s - pp.L * Fraction(29, 24))) < 1e-50
    out["U_e_13824"] = (pp.U_e == 13824)
    # NRCI of canonical octad
    oc = g.get_octads()[0]
    nrci_val = float(l.calculate_nrci(list(map(int, oc))))
    out["nrci_octad_0p7623"] = abs(nrci_val - 0.762346) < 1e-5
    return out


if __name__ == "__main__":
    results = self_test()
    for k, v in results.items():
        print(f"  {k:30s}: {'PASS' if v else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit("FAIL: engine adapter self-test failed.")
    print("\nALL ENGINE ADAPTER SELF-TESTS PASS.")
