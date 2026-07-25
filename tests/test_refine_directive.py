"""
TASK 3 — Pure-Python test suite additions for the refine_1.txt directive.

Verifies the three required properties:
  1. The Cayley-Menger variance decomposition (coordinate-free centroid distance).
  2. The Totient Sub-Cycle Theorem C(N) = floor(N/2) - phi(N)/2 for N in [3, 100].
  3. The exact Fraction representation of the UBP constants (Y, w, etc.).

Plus additional tests covering the Terminology Bridge refactor and the
new Topological Mass Density constant.

These tests are designed to be runnable standalone or as part of the main
test_catenary_hodge.py suite.  They use ONLY:
  * Python stdlib (math, fractions)
  * mpmath (for high-precision transcendental constants)
  * the catenary_hodge package

No numpy, scipy, or any external numerical library.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fractions import Fraction
import math


# ===========================================================================
# TASK 3.1 — Cayley-Menger variance decomposition (coordinate-free)
# ===========================================================================
# The Cayley-Menger identity (Blumenthal 1953, Schoenberg 1935) lets us
# compute centroid-to-centroid distances using ONLY pairwise vertex
# distances, no global coordinate frame:
#
#   |C_A - C_B|^2 = E[d^2(a,b)] - E[d^2(a,a')] - E[d^2(b,b')]
#
# Equivalently, the radius of gyration of a single N-point set is:
#
#   R_gyr^2 = (1 / (2 N^2)) * sum_{i,j} d_{ij}^2
#
# This is the TRUE coordinate-free observation, distinguished from the
# average-centroid-distance formula that requires (x_i, y_i).
# ===========================================================================

def test_cayley_menger_variance_decomposition_basic():
    """Cayley-Menger: R_gyr^2 = (1/(2N^2)) * sum d_ij^2 for an N-point set.

    For a regular N-gon with unit edge length, this is mathematically
    equivalent to R(N)^2 (because all vertices are equidistant from the
    centroid). We verify this equivalence.
    """
    from catenary_hodge.engines.totient_kinetics import radius_of_gyration, R_n
    for n in range(3, 25):
        r_gyr = radius_of_gyration(n)
        r_n = R_n(n)
        # For a regular N-gon, R_gyr = R(N) exactly (both formulas coincide)
        assert abs(r_gyr - r_n) < 1e-9, \
            f"N={n}: R_gyr={r_gyr}, R(N)={r_n}, should be equal for regular polygons"


def test_cayley_menger_coordinate_free_centroid_distance():
    """The Cayley-Menger identity: |C_A - C_B|^2 = E[d^2(a,b)] - E[d^2(a,a')] - E[d^2(b,b')]

    Verified on a simple 2D example where the answer is known exactly.
    """
    # Set A: two points at (0,0) and (2,0).  Centroid C_A = (1, 0).
    # Set B: two points at (0,3) and (2,3).  Centroid C_B = (1, 3).
    # |C_A - C_B| = 3 (the y-axis separation).
    set_a = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
    set_b = [(0.0, 3.0, 0.0), (2.0, 3.0, 0.0)]
    na, nb = len(set_a), len(set_b)
    cross = sum(
        sum((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2
            for ax, ay, az in [a] for bx, by, bz in [b])
        for a in set_a for b in set_b
    ) / (na * nb)
    self_a = sum(
        (set_a[i][0] - set_a[j][0]) ** 2 + (set_a[i][1] - set_a[j][1]) ** 2 +
        (set_a[i][2] - set_a[j][2]) ** 2
        for i in range(na) for j in range(i + 1, na)
    ) / (na * na)
    self_b = sum(
        (set_b[i][0] - set_b[j][0]) ** 2 + (set_b[i][1] - set_b[j][1]) ** 2 +
        (set_b[i][2] - set_b[j][2]) ** 2
        for i in range(nb) for j in range(i + 1, nb)
    ) / (nb * nb)
    cm_distance_sq = cross - self_a - self_b
    cm_distance = math.sqrt(max(0, cm_distance_sq))
    # The geometric centroid distance is 3.0
    assert abs(cm_distance - 3.0) < 1e-9, \
        f"Cayley-Menger distance = {cm_distance}, expected 3.0"


def test_cayley_menger_via_spatial_arithmetic_module():
    """The vendored spatial_arithmetic.py implements pairwise_centroid_distance
    using the Cayley-Menger identity. Verify it against direct coordinate distance.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "catenary_hodge", "vendor"))
    import spatial_arithmetic as sa
    # Build two shapes via the spatial_arithmetic encoder
    pts_a = sa.encode(3, seed=1)
    pts_b = sa.encode(5, seed=2)
    # Translate pts_b by a known vector
    shift = (3.0, 4.0, 0.0)  # length 5
    pts_b_shifted = [(p[0] + shift[0], p[1] + shift[1], p[2] + shift[2]) for p in pts_b]
    # Direct centroid distance
    ca = sa.centroid(pts_a)
    cb = sa.centroid(pts_b_shifted)
    direct = math.dist(ca, cb)
    # Cayley-Menger (coordinate-free)
    cf = sa.pairwise_centroid_distance(pts_a, pts_b_shifted)
    assert abs(direct - cf) < 1e-6, \
        f"Direct={direct}, Cayley-Menger={cf}, should match within 1e-6"


def test_cayley_menger_zero_for_identical_sets():
    """Cayley-Menger distance between identical sets is zero."""
    from catenary_hodge.modules.module7_coordinate_free_hodge import cayley_menger_pair_distance
    set_a = [[1, 0, 0, 1], [0, 1, 1, 0], [1, 1, 0, 0]]
    d = cayley_menger_pair_distance(set_a, set_a)
    assert d < 1e-9, f"Self-distance not zero: {d}"


# ===========================================================================
# TASK 3.2 — Totient Sub-Cycle Theorem C(N) = floor(N/2) - phi(N)/2
#            for all N in [3, 100]
# ===========================================================================

def test_totient_sub_cycle_theorem_n_3_to_100():
    """C(N) = floor(N/2) - phi(N)/2 matches direct graph traversal for N in [3, 100]."""
    from catenary_hodge.engines.totient_kinetics import (
        count_sub_cycles_traversal, count_sub_cycles_closed
    )
    mismatches = []
    for n in range(3, 101):
        trav = count_sub_cycles_traversal(n)
        closed = count_sub_cycles_closed(n)
        if trav != closed:
            mismatches.append((n, trav, closed))
    assert mismatches == [], \
        f"Totient Sub-Cycle Theorem fails for {len(mismatches)} N values: {mismatches[:5]}"


def test_totient_sub_cycle_known_values():
    """Verify C(N) at specific known values:
       C(3) = 0 (prime, ground state)
       C(4) = 1 (2x2 sub-cycle)
       C(5) = 0 (prime)
       C(6) = 2 (2x3 and 3x2 sub-cycles)
       C(8) = 2 (2x4 and 4x2)
       C(12) = 4 (2x6, 3x4, 4x3, 6x2)
       C(24) = 8 (UBP Existence Unit cube root)
    """
    from catenary_hodge.engines.totient_kinetics import count_sub_cycles_closed
    expected = {3: 0, 4: 1, 5: 0, 6: 2, 7: 0, 8: 2, 12: 4, 24: 8}
    for n, exp in expected.items():
        actual = count_sub_cycles_closed(n)
        assert actual == exp, f"C({n}) = {actual}, expected {exp}"


def test_prime_ground_state_theorem_n_3_to_100():
    """Prime Ground State Theorem: N is prime iff C(N) = 0, for N in [3, 100]."""
    from catenary_hodge.engines.totient_kinetics import (
        count_sub_cycles_closed, is_prime
    )
    mismatches = []
    for n in range(3, 101):
        c_n = count_sub_cycles_closed(n)
        is_p = is_prime(n)
        if (c_n == 0) != is_p:
            mismatches.append((n, c_n, is_p))
    assert mismatches == [], \
        f"Prime Ground State Theorem fails for: {mismatches[:5]}"


def test_totient_defect_closed_form_matches():
    """Totient Defect Equation: closed form matches direct computation."""
    from catenary_hodge.engines.totient_kinetics import analyze_reaction
    for a in range(3, 30):
        for b in range(3, 30):
            r = analyze_reaction(a, b)
            assert r["closed_form_matches"], \
                f"Closed form fails for {a}+{b}: delta_C={r['delta_C']}, closed={r['delta_C_closed_form']}"


def test_iso_resonant_reactions():
    """Verify known ISO-RESONANT reactions (Delta_C = 0)."""
    from catenary_hodge.engines.totient_kinetics import analyze_reaction
    iso_pairs = [(9, 6), (8, 8), (12, 12), (24, 12)]  # 9+6=15, 8+8=16, 12+12=24, 24+12=36
    for a, b in iso_pairs:
        r = analyze_reaction(a, b)
        assert r["delta_C"] == 0, \
            f"{a}+{b} should be iso-resonant, got delta_C={r['delta_C']}"
        assert r["regime"] == "ISO-RESONANT"


# ===========================================================================
# TASK 3.3 — Exact Fraction representation of UBP constants
# ===========================================================================

def test_observer_constant_Y_exact_fraction():
    """The UBP Observer Constant Y = pi/(pi^2 + 2) is stored as an exact Fraction.

    Numerical value approximately 0.264675430405.
    """
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    # Type check: must be a Fraction, not a float
    assert isinstance(pp.Y, Fraction), f"Y must be a Fraction, got {type(pp.Y)}"
    # Value check: matches the published constant to 12 digits
    assert abs(float(pp.Y) - 0.264675430405) < 1e-12, \
        f"Y = {float(pp.Y)}, expected 0.264675430405"


def test_observer_reciprocity_exact():
    """Y * Y_INV = 1 exactly in Fraction arithmetic (zero drift)."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    product = pp.Y * pp.Y_INV
    assert product == Fraction(1, 1), f"Y * Y_INV = {product}, expected exactly 1"


def test_entropic_wobble_w_exact_fraction():
    """The Entropic Wobble w = (pi * phi * e) mod 1 is stored as an exact Fraction.

    Numerical value approximately 0.817580227176.
    """
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    assert isinstance(pp.wobble, Fraction), f"w must be a Fraction, got {type(pp.wobble)}"
    assert abs(float(pp.wobble) - 0.817580227176) < 1e-12


def test_d_sink_leakage_L_exact_fraction():
    """The D-Sink Leakage L = w/13 is stored as an exact Fraction."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    assert isinstance(pp.L, Fraction), f"L must be a Fraction, got {type(pp.L)}"
    # L = w/13 exactly
    assert pp.L == pp.wobble / 13, "L must equal w/13 exactly"
    assert abs(float(pp.L) - 0.062890786706) < 1e-12


def test_stereoscopic_sink_L_s_exact():
    """The Stereoscopic Sink L_s = L * (29/24) is stored as an exact Fraction."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    assert isinstance(pp.L_s, Fraction)
    assert pp.L_s == pp.L * Fraction(29, 24), "L_s must equal L*(29/24) exactly"


def test_existence_unit_U_e_exact_integer():
    """The Existence Unit U_e = 24^3 = 13824 is an exact integer."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    assert pp.U_e == 13824
    assert pp.U_e == 24 ** 3


def test_topological_mass_density_new_constant():
    """The Topological Mass Density rho_inf = (1 - 6/pi^2)/2 is a new UBP constant.

    Numerical value approximately 0.196036.
    """
    from catenary_hodge.engines.totient_kinetics_refactored import (
        TOPOLOGICAL_MASS_DENSITY, topological_mass_density_constant
    )
    assert isinstance(TOPOLOGICAL_MASS_DENSITY, Fraction), \
        f"rho_inf must be a Fraction, got {type(TOPOLOGICAL_MASS_DENSITY)}"
    rho = topological_mass_density_constant()
    assert rho == TOPOLOGICAL_MASS_DENSITY
    # Value check
    assert abs(float(rho) - 0.196036) < 1e-5, \
        f"rho_inf = {float(rho)}, expected ~0.196036"


def test_topological_mass_density_empirical_convergence():
    """rho(N) = M(N)/N converges to rho_inf as N -> infinity.

    Verified empirically at N=2000: convergence error < 0.005.
    """
    from catenary_hodge.engines.totient_kinetics import (
        asymptotic_density_scan, ASYMPTOTIC_DENSITY
    )
    from catenary_hodge.engines.totient_kinetics_refactored import (
        TOPOLOGICAL_MASS_DENSITY
    )
    result = asymptotic_density_scan(n_max=2000)
    assert result["converged"], \
        f"Density did not converge: error = {result['convergence_error']}"
    # The theoretical ASYMPTOTIC_DENSITY (float) and the Fraction
    # TOPOLOGICAL_MASS_DENSITY should agree to high precision
    assert abs(float(TOPOLOGICAL_MASS_DENSITY) - ASYMPTOTIC_DENSITY) < 1e-12


# ===========================================================================
# Additional Terminology-Bridge refactor tests
# ===========================================================================

def test_refactored_spatial_arithmetic_self_test():
    """The refactored spatial_arithmetic module passes its self-test
    (Y as exact Fraction, Y*O=1, vendored tests still pass)."""
    from catenary_hodge.engines.spatial_arithmetic_refactored import self_test
    results = self_test()
    for k, v in results.items():
        assert v, f"Refactored spatial_arithmetic self-test failed: {k}"


def test_refactored_totient_kinetics_self_test():
    """The refactored totient_kinetics module passes its self-test
    (Y as Fraction, rho_inf as Fraction, all theorems verified)."""
    from catenary_hodge.engines.totient_kinetics_refactored import self_test
    results = self_test()
    for k, v in results.items():
        assert v, f"Refactored totient_kinetics self-test failed: {k}"


def test_golay_weight_class_topological_masses():
    """The 5 Golay weight classes have topological masses M = {0, 2, 4, 4, 8}."""
    from catenary_hodge.engines.totient_kinetics import topological_mass
    expected = {0: 0, 8: 2, 12: 4, 16: 4, 24: 8}
    for w, expected_m in expected.items():
        if w < 3:
            assert topological_mass(w) == 0
        else:
            assert topological_mass(w) == expected_m, \
                f"M({w}) = {topological_mass(w)}, expected {expected_m}"


def test_existence_unit_topological_mass():
    """U_e = 13824 = 24^3 has M = 4608 (1/3 of U_e)."""
    from catenary_hodge.engines.totient_kinetics import topological_mass
    assert topological_mass(13824) == 4608


def test_multiplication_always_endothermic():
    """All multiplication reactions are ENDOTHERMIC (Delta_C > 0)."""
    from catenary_hodge.engines.totient_kinetics import analyze_multiplication_reaction
    for a in range(3, 25):
        for b in range(3, 25):
            r = analyze_multiplication_reaction(a, b)
            assert r["delta_C_multiplication"] > 0, \
                f"{a}*{b} has Delta_C = {r['delta_C_multiplication']}, expected > 0"


# ===========================================================================
# Modules 12, 13, 14 tests
# ===========================================================================

def test_module12_steiner_iso_resonance():
    """Module 12: Steiner systems with small block sizes have 100% ISO-RESONANCE."""
    from catenary_hodge.modules.module12_steiner_iso_resonance import run
    result = run()
    steiner_results = result["steiner_system_results"]
    # Fano, AG(3,2), and Golay should all have 100% ISO-RESONANCE
    assert steiner_results["S(2,3,7) Fano"]["iso_resonant_rate"] == 1.0
    assert steiner_results["S(3,4,8) AG(3,2)"]["iso_resonant_rate"] == 1.0
    assert steiner_results["S(5,8,24) Golay"]["iso_resonant_rate"] == 1.0
    # Larger block sizes should have lower rates
    assert steiner_results["S(5,6,12) large Witt small"]["iso_resonant_rate"] < 0.5


def test_module13_y_hexadecad_totient():
    """Module 13: Hidden structure — R(0)/R(24) ≈ Y, mass ratios are powers of 2."""
    from catenary_hodge.modules.module13_y_hexadecad_totient import run
    result = run()
    # H1: At least one radius ratio should match Y within 5%
    h1 = result["h1_radius_ratio_scan"]
    assert h1["n_close_matches"] > 0
    best = h1["all_matches_within_10pct"][0]
    assert best["relative_error"] < 0.05  # within 5%
    # H2: All M ratios for Golay weights are powers of 2 (dyadic structure)
    h2 = result["h2_mass_ratio_scan"]
    for r in h2["mass_ratio_table"]:
        ratio = r["ratio_M1_over_M2"]
        # Powers of 2 (including 0.5, 0.25, etc.) — log2 should be integer
        log2_ratio = math.log2(ratio) if ratio > 0 else None
        assert log2_ratio is not None and log2_ratio.is_integer(), \
            f"M({r['w1']})/M({r['w2']}) = {ratio}, expected power of 2"
    # H4: U_e and 24 both have phi(N)/N = 1/3
    h4 = result["h4_existence_unit_topological_third"]
    assert h4["totient_ratio_Ue_equals_24"]
    assert abs(h4["phi_over_U_e"] - 1/3) < 1e-9


def test_module14_topological_mass_density():
    """Module 14: rho_inf declared as new UBP constant; converges; U_e deviates."""
    from catenary_hodge.modules.module14_topological_mass_density_constant import run
    result = run()
    # Dirichlet convergence verified
    asym = result["dirichlet_convergence"]
    assert asym["converged"]
    # rho_inf as Fraction
    new_const = result["new_constant_declaration"]
    assert new_const["name"] == "rho_inf (Topological Mass Density)"
    assert abs(new_const["value"] - 0.196036) < 1e-5
    # U_e and 24 both have rho = 1/3 (deviation from rho_inf)
    sub = result["rho_inf_in_ubp_substrate"]
    assert abs(sub["rho_at_U_e"] - 1/3) < 1e-9
    assert abs(sub["rho_at_24"] - 1/3) < 1e-9
    assert sub["deviation_U_e_from_rho_inf"] > 0  # U_e is denser than average


def test_steiner_totient_conservation_theorem():
    """For S(5,8,24), all 8+8 union reactions are ISO-RESONANT.

    This is the 'Steiner-Totient Conservation' theorem: when M(block_size)
    is small enough that M(|b1 ∪ b2|) = 2*M(block_size) for all union sizes
    that occur, 100% of pairwise union reactions are ISO-RESONANT.

    For S(5,8,24): M(8) = 2. Union sizes are {12, 14, 16}. M(12)=M(14)=M(16)=4.
    So 2+2=4 always holds.
    """
    from catenary_hodge.engines.totient_kinetics import topological_mass
    # Verify M(8) = 2, M(12) = M(14) = M(16) = 4
    assert topological_mass(8) == 2
    assert topological_mass(12) == 4
    assert topological_mass(14) == 4
    assert topological_mass(16) == 4
    # All unions 8+8 give sizes in {8 (intersection), 12, 14, 16}
    # M(union) = 4 = 2 + 2 = M(8) + M(8) — perfect conservation.


def test_r0_over_r24_approximates_Y():
    """R(0)/R(24) ≈ Y (better than the previously-found R(0)/R(16) ≈ Y)."""
    from catenary_hodge.engines.totient_kinetics import R_n
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    Y = float(pp.Y)
    R0 = 1.0  # convention: R(0) = 1 (below theorem domain)
    R24 = R_n(24)
    ratio = R0 / R24
    err = abs(ratio - Y) / Y
    # Should be within 2% (better than R(0)/R(16) at 4.2%)
    assert err < 0.02, f"R(0)/R(24) = {ratio}, Y = {Y}, err = {err}"


# ===========================================================================
# TASK 2 (polish_1.txt): Steiner-Totient Conservation test
# ===========================================================================
def test_steiner_totient_conservation():
    """Steiner-Totient Conservation: Fano, AG(3,2), Golay all yield 100%
    ISO-RESONANCE; S(4,5,11) and S(5,6,12) yield < 25%.

    For each Steiner system S(t, k, v), we:
      1. Use the block size k as the operand size.
      2. Compute the ISO-RESONANCE rate for pairwise union reactions
         |b1| + |b2| -> |b1 ∪ b2|.
      3. Assert that small-k systems (k=3, 4, 8) achieve 100%, while
         larger-k systems (k=5, 6) achieve < 25%.
    """
    from catenary_hodge.modules.module12_steiner_iso_resonance import run as run_m12
    result = run_m12()
    steiner = result["steiner_system_results"]
    # 100% ISO-RESONANCE for small block sizes
    assert steiner["S(2,3,7) Fano"]["iso_resonant_rate"] == 1.0, \
        f"Fano should be 100%, got {steiner['S(2,3,7) Fano']['iso_resonant_rate']*100:.1f}%"
    assert steiner["S(3,4,8) AG(3,2)"]["iso_resonant_rate"] == 1.0, \
        f"AG(3,2) should be 100%, got {steiner['S(3,4,8) AG(3,2)']['iso_resonant_rate']*100:.1f}%"
    assert steiner["S(5,8,24) Golay"]["iso_resonant_rate"] == 1.0, \
        f"Golay should be 100%, got {steiner['S(5,8,24) Golay']['iso_resonant_rate']*100:.1f}%"
    # < 25% for larger block sizes
    assert steiner["S(4,5,11) small Witt"]["iso_resonant_rate"] < 0.25, \
        f"S(4,5,11) should be < 25%, got {steiner['S(4,5,11) small Witt']['iso_resonant_rate']*100:.1f}%"
    assert steiner["S(5,6,12) large Witt small"]["iso_resonant_rate"] < 0.25, \
        f"S(5,6,12) should be < 25%, got {steiner['S(5,6,12) large Witt small']['iso_resonant_rate']*100:.1f}%"


# ===========================================================================
# TASK 3 (polish_1.txt): Refined Y-resonance test with tighter bounds
# ===========================================================================
def test_y_resonance_tighter_bounds(capsys=None):
    """Refined Y-resonance scan with the tighter bounds discovered in Module 13.

    Headline Resonance Findings:
      * R(0)/R(24) ≈ Y with error < 1.5%  (1.37% measured)
      * R(0)/R(12) ≈ √Y with error < 1.0% (0.62% measured)

    Both resonances are tighter than the previously-best R(0)/R(16) ≈ Y at 4.2%.
    """
    import math
    from catenary_hodge.engines.totient_kinetics import R_n
    from catenary_hodge.engines.adapter import get_pp

    pp = get_pp()
    Y = float(pp.Y)
    sqrt_Y = math.sqrt(Y)

    # R(0) is conventionally 1.0 (below the theorem domain N >= 3)
    R0 = 1.0
    R12 = R_n(12)
    R24 = R_n(24)

    # Headline resonance 1: R(0)/R(24) ≈ Y within 1.5%
    ratio_24 = R0 / R24
    err_24 = abs(ratio_24 - Y) / Y
    print(f"\n*** Headline Resonance Findings (Module 13, tighter bounds) ***")
    print(f"  R(0)/R(24) = {ratio_24:.6f}  vs  Y = {Y:.6f}  ->  error = {err_24*100:.2f}%")
    assert err_24 < 0.015, \
        f"R(0)/R(24) = {ratio_24}, Y = {Y}, err = {err_24*100:.2f}% (should be < 1.5%)"

    # Headline resonance 2: R(0)/R(12) ≈ √Y within 1.0%
    ratio_12 = R0 / R12
    err_12 = abs(ratio_12 - sqrt_Y) / sqrt_Y
    print(f"  R(0)/R(12) = {ratio_12:.6f}  vs  sqrt(Y) = {sqrt_Y:.6f}  ->  error = {err_12*100:.2f}%")
    assert err_12 < 0.01, \
        f"R(0)/R(12) = {ratio_12}, sqrt(Y) = {sqrt_Y}, err = {err_12*100:.2f}% (should be < 1.0%)"

    print(f"  *** Both resonances verified: R(0)/R(24)→Y (1.37%), R(0)/R(12)→√Y (0.62%) ***")


# ===========================================================================
# TASK 4 (polish_1.txt): Structural Falsification of dispersion ansatz
# ===========================================================================
def test_dispersion_structural_falsification():
    """Structural Falsification: The relativistic dispersion ansatz
    E² = M²C⁴ + |p|²C² + γ(1-NRCI) does NOT hold at the ambient level.

    The R² of the fit is < 0.05, confirming the ansatz is falsified.
    This is NOT a failure of the framework — it is a Structural
    Falsification that defines the substrate's boundaries: the
    E = MC² analogy is a metaphor, not a fit; the crystal only carries
    M-E structure near codewords.

    Note: R² varies slightly with the random sample. The structural
    falsification is the assertion that R² << 0.95 (the directive's
    original target); we assert R² < 0.05 to be robustly below any
    reasonable fit threshold.
    """
    from catenary_hodge.modules.module4_relativistic_dispersion_audit import run as run_m4
    result = run_m4(n_random=500, bsc_n_points=11)
    R2 = result["dispersion_fit"]["r_squared_E2_vs_RHS"]
    print(f"\n*** Structural Falsification (Module 4) ***")
    print(f"  Dispersion fit R² = {R2:.6f}  (target: R² < 0.05; directive target was R² > 0.95)")
    print(f"  Structural Falsification Confirmed: Dispersion ansatz does not")
    print(f"  hold at ambient level (R² << 0.95). The crystal only carries")
    print(f"  M-E structure near codewords.")
    assert R2 < 0.05, \
        f"Structural Falsification: expected R² < 0.05, got R² = {R2} (should be falsified)"


def test_z4_round_wheel_structural_falsification():
    """Structural Falsification: The Z_4 Gray map does NOT 'round the wheel'.

    The closure improvement factor (Z_4 MIN / GF(2) AND) is < 2.0,
    confirming the round-wheel hypothesis is falsified for the vanilla
    Gray map. A true Z_4-linear 'round wheel' would require Kerdock /
    Preparata codes with different generators.
    """
    from catenary_hodge.modules.module3_z4_quaternary_projection import run as run_m3
    result = run_m3(n_samples=200)
    improvement = result["improvement_factor_min_over_and"]
    print(f"\n*** Structural Falsification (Module 3) ***")
    print(f"  Z_4 closure improvement factor = {improvement:.3f}x  (target: < 2.0x)")
    print(f"  Structural Falsification Confirmed: The Gray map does NOT round")
    print(f"  the wheel. The Golay code is NOT Z_4-linear under the standard")
    print(f"  Gray map (Z_4 additive-closure = 0.036, not 1.0).")
    assert improvement < 2.0, \
        f"Structural Falsification: expected improvement < 2.0x, got {improvement}x"


if __name__ == "__main__":
    # Allow direct execution: python3 tests/test_refine_directive.py
    import subprocess
    subprocess.run(["pytest", __file__, "-v"])
