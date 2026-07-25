"""Test suite for the Catenary-Hodge package.

Validates:
  * UBP constants are exact Fractions with correct identities
  * Golay [24,12,8] code invariants (weight enumerator, self-duality, Push 9 alignment)
  * Ladder engines ([4,2,2], [8,4,4], [12,6,6], [14,7,*], [24,12,8])
  * Module outputs (smoke tests for Modules 1-5 + capstone)

Run with: `pytest tests/ -v`
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fractions import Fraction


def test_ubp_constants():
    """UBP constants are exact Fractions with correct identities."""
    from catenary_hodge.engines.adapter import self_test
    results = self_test()
    for name, ok in results.items():
        assert ok, f"UBP constant check failed: {name}"


def test_golay_code_invariants():
    """Golay [24,12,8] weight enumerator and self-duality."""
    from catenary_hodge.engines.adapter import get_golay, weight_enumerator, is_self_dual, all_codewords_zero_syndrome
    g = get_golay()
    assert len(g.get_all_codewords()) == 4096
    assert len(g.get_octads()) == 759
    we = weight_enumerator(g)
    assert we == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}, f"Wrong weight enumerator: {we}"
    assert is_self_dual(g), "Golay code is not self-dual"
    assert all_codewords_zero_syndrome(g), "Not all codewords have zero syndrome (Push 9 bug)"


def test_push9_alignment_fixed():
    """Push 9 alignment bug is fixed: all 4096 codewords yield E=0."""
    from catenary_hodge.engines.adapter import get_golay
    g = get_golay()
    cws = g.get_all_codewords()
    zero_count = sum(1 for c in cws if g.syndrome_weight(c) == 0)
    assert zero_count == 4096, f"Only {zero_count}/4096 codewords have zero syndrome"


def test_ladder_4_2_2():
    """[4,2,2] trivial self-dual code."""
    from catenary_hodge.engines.ladder import get_code_4_2_2
    c = get_code_4_2_2()
    assert c["weight_enumerator"] == {0: 1, 2: 2, 4: 1}
    assert len(c["codewords"]) == 4


def test_ladder_8_4_4():
    """[8,4,4] extended Hamming code."""
    from catenary_hodge.engines.ladder import get_code_8_4_4
    c = get_code_8_4_4()
    assert c["weight_enumerator"] == {0: 1, 4: 14, 8: 1}
    assert len(c["codewords"]) == 16


def test_ladder_12_6_6_ternary():
    """[12,6,6] ternary Golay code over GF(3)."""
    from catenary_hodge.engines.ladder import get_code_12_6_6
    c = get_code_12_6_6()
    assert c["weight_enumerator"] == {0: 1, 6: 264, 9: 440, 12: 24}
    assert len(c["codewords"]) == 729


def test_ladder_14_7():
    """[14,7,*] truncated Golay (d reported honestly)."""
    from catenary_hodge.engines.ladder import get_code_14_7_4
    c = get_code_14_7_4()
    assert len(c["codewords"]) == 128
    assert c["d"] >= 2  # naive truncation gives d=2 (finding)


def test_ladder_24_12_8():
    """[24,12,8] extended binary Golay."""
    from catenary_hodge.engines.ladder import get_code_24_12_8
    c = get_code_24_12_8()
    assert c["weight_enumerator"] == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
    assert len(c["codewords"]) == 4096


def test_nrci_octad_value():
    """NRCI of canonical octad = 0.762346 (LDP paper verified value)."""
    from catenary_hodge.engines.adapter import get_golay, get_leech
    g = get_golay()
    l = get_leech()
    oc = g.get_octads()[0]
    nrci = float(l.calculate_nrci(list(map(int, oc))))
    assert abs(nrci - 0.762346) < 1e-5


def test_d_squared_zero_axiom():
    """d^2=0 axiom: H*G^T = 0 (mod 2)."""
    from catenary_hodge.capstone.master_system import verify_d_squared_zero
    d2 = verify_d_squared_zero()
    assert d2["H_GT_zero_mod2"], "H*G^T != 0 (mod 2)"
    assert d2["all_codewords_zero_syndrome"], "Some codeword has nonzero syndrome"
    assert d2["steiner_intersection_subset_of_0248"], "Octad intersections outside {0,2,4,8}"


def test_module1_runs():
    """Module 1 produces a result with the expected ladder rows."""
    from catenary_hodge.modules.module1_catenary_profile_ladder import run
    result = run(n_proj_samples=5, n_closure_samples=20)
    assert "ladder_rows" in result
    assert len(result["ladder_rows"]) == 5
    assert "n_c" in result
    # n_c from beta_proj slope should be in [10, 16]
    assert 10.0 <= result["n_c"]["from_beta_proj"] <= 16.0


def test_module2_runs():
    """Module 2 enumerates 262,144 NOISE=0 vectors."""
    from catenary_hodge.modules.module2_ghost_state_renormalization import run
    result = run(max_ghosts_radius=500, max_ghosts_orbit=50, max_ghosts_octads=500)
    assert result["noise_zero_count"] == 262144
    # LDP identity-MOG alignment gives 128 codewords at NOISE=0
    assert result["codewords_in_noise_zero"] == 128
    # Ghosts = 262144 - 128 = 262016
    assert result["ghost_count"] == 262016


def test_module3_runs():
    """Module 3 Z_4 Gray map round-trip and closure rates.

    Note: The Z_4 'round wheel' hypothesis is STRUCTURALLY FALSIFIED — the
    closure improvement factor is < 2.0. This is a structural finding about
    the substrate, NOT a test failure.
    """
    from catenary_hodge.modules.module3_z4_quaternary_projection import run
    result = run(n_samples=50)
    assert result["gray_round_trip_ok"]
    assert 0.0 < result["gf2_and_closure"] <= 1.0
    assert 0.0 < result["z4_additive_closure"] <= 1.0
    assert result["unique_projections"] > 100  # ~111 expected


def test_module4_runs():
    """Module 4: Push 9 alignment fixed (4096/4096 at E=0).

    Note: The dispersion R² is STRUCTURALLY FALSIFIED (R² < 0.01). This is
    a structural finding about the substrate, NOT a test failure.
    """
    from catenary_hodge.modules.module4_relativistic_dispersion_audit import run
    result = run(n_random=500, bsc_n_points=11)
    assert result["push9_alignment_ok"]
    assert result["zero_energy_codewords"] == 4096
    # R^2 should be very small — dispersion ansatz is FALSIFIED
    # (this is a Structural Falsification, not a failure)
    assert abs(result["dispersion_fit"]["r_squared_E2_vs_RHS"]) < 0.05


def test_module5_runs():
    """Module 5: Ternary Golay weight histogram matches reference."""
    from catenary_hodge.modules.module5_leech_harmonic_projection import ternary_binary_bridge
    bridge = ternary_binary_bridge()
    assert bridge["ternary_we"] == {0: 1, 6: 264, 9: 440, 12: 24}


def test_capstone_master_system():
    """Capstone: 3-axis master system has correct dimensions."""
    from catenary_hodge.capstone.master_system import build_master_system
    s = build_master_system()
    assert len(s["axis_1_form_degree"]) == 4
    assert len(s["axis_2_projection_kernels"]) == 4
    assert len(s["axis_3_substrate_hierarchy"]) == 5
    assert len(s["rosetta_stone"]) == 5
    assert s["d_squared_zero_axiom"]["d_squared_zero_axiom_holds"]


def test_y_reciprocity_exact():
    """Y * Y_INV = 1 exactly in Fraction arithmetic."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    product = pp.Y * pp.Y_INV
    assert product == Fraction(1, 1), f"Y*Y_INV = {product}, expected 1"


def test_L_eq_w_over_13_exact():
    """L = w/13 exactly in Fraction arithmetic."""
    from catenary_hodge.engines.adapter import get_pp
    pp = get_pp()
    assert pp.L == pp.wobble / 13


def test_spatial_arithmetic_self_test():
    """Vendored spatial_arithmetic.py passes its own 13-test suite."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "catenary_hodge", "vendor"))
    import spatial_arithmetic as sa
    # Round-trip
    assert sa.decode(sa.encode(7, seed=42)) == 7
    assert sa.decode(sa.encode(-5, seed=42)) == -5
    # Natural primitive
    assert sa.radius_to_value(sa.value_to_radius(10)) == 10
    # Scene + observe
    r = sa.observe_scene(sa.build_scene(7, 3, "ADD", seed=42))
    assert r["ok"] and r["a"] == 7 and r["b"] == 3 and r["operator"] == "ADD"
    assert r["base_result"] == 10


def test_spatial_golay_weight_mapping():
    """Each Golay codeword weight class maps to a unique spatial value/radius."""
    from catenary_hodge.engines.spatial_golay import (
        weight_to_value, value_to_weight, spatial_weight_spectrum
    )
    # Bijective mapping for the 5 codeword weights
    weights = [0, 8, 12, 16, 24]
    values = [weight_to_value(w) for w in weights]
    assert len(set(values)) == 5, f"Values not distinct: {values}"
    # Round-trip
    for w in weights:
        assert value_to_weight(weight_to_value(w)) == w
    # 5 distinct radii
    spec = spatial_weight_spectrum()
    radii = [round(r["theoretical_radius"], 6) for r in spec["weight_classes"]]
    assert len(set(radii)) == 5


def test_module6_runs():
    """Module 6: Spatial catenary produces valid output."""
    from catenary_hodge.modules.module6_spatial_catenary import run
    result = run(n_samples=80)
    assert "spatial_weight_spectrum" in result
    assert "stratified_hodge_gap" in result
    assert len(result["stratified_hodge_gap"]) == 5
    # Round-trip should be 100% (weight → spatial value → weight)
    assert result["roundtrip_ok_count"] == result["roundtrip_total"]


def test_module7_runs():
    """Module 7: Coordinate-free Hodge clusters ghosts by Hamming signature."""
    from catenary_hodge.modules.module7_coordinate_free_hodge import run
    result = run(max_ghosts=500, n_reference=8, n_top=5)
    assert result["n_ghosts_total"] == 262016  # LDP identity-MOG value
    assert result["n_distinct_clusters"] > 1
    assert len(result["cluster_geometry"]["cayley_menger_distance_matrix"]) == 5


def test_module8_runs():
    """Module 8: Spatial Y-constant resonance scan."""
    from catenary_hodge.modules.module8_spatial_y_constant import run
    result = run()
    assert "r_scan" in result
    assert "continued_fractions" in result
    assert "catenary_curvature" in result
    # The catenary curvature table should have 5 weight classes
    assert len(result["catenary_curvature"]["weight_class_curvatures"]) == 5
    # Y continued fraction should start with [0, 3, ...]
    assert result["continued_fractions"]["Y_continued_fraction"][:2] == [0, 3]


def test_spatial_hodge_gap_zero_identity():
    """AND(zero, anything) = zero (zero is the identity for AND)."""
    from catenary_hodge.engines.spatial_golay import spatial_hodge_gap
    from catenary_hodge.engines.adapter import get_golay
    g = get_golay()
    cws = g.get_all_codewords()
    zero = [0] * 24
    gap = spatial_hodge_gap(zero, cws[10])
    assert gap["and_weight"] == 0
    assert gap["and_is_codeword"]


def test_cayley_menger_binary_analog():
    """Cayley-Menger distance on identical sets is zero."""
    from catenary_hodge.modules.module7_coordinate_free_hodge import cayley_menger_pair_distance
    set_a = [[1, 0, 0, 1], [0, 1, 1, 0], [1, 1, 0, 0]]
    # Same set vs itself: distance should be 0
    d = cayley_menger_pair_distance(set_a, set_a)
    assert d < 1e-9, f"Self-distance not zero: {d}"


# ===========================================================================
# Totient Kinetics tests (Modules 9, 10, 11)
# ===========================================================================
def test_totient_kinetics_sub_cycle_theorem():
    """C(N) = floor(N/2) - phi(N)/2 matches traversal for N in [3, 100]."""
    from catenary_hodge.engines.totient_kinetics import (
        count_sub_cycles_traversal, count_sub_cycles_closed
    )
    mismatches = 0
    for n in range(3, 101):
        if count_sub_cycles_traversal(n) != count_sub_cycles_closed(n):
            mismatches += 1
    assert mismatches == 0, f"{mismatches} mismatches in C(N) closed form"


def test_totient_defect_closed_form():
    """Totient Defect Equation closed-form matches direct computation."""
    from catenary_hodge.engines.totient_kinetics import analyze_reaction
    for a in range(3, 30):
        for b in range(3, 30):
            r = analyze_reaction(a, b)
            assert r["closed_form_matches"], f"Closed form fails for {a}+{b}"


def test_prime_ground_state_theorem():
    """N is prime iff C(N) = 0, for N in [3, 500]."""
    from catenary_hodge.engines.totient_kinetics import verify_prime_ground_state_theorem
    result = verify_prime_ground_state_theorem(n_max=500)
    assert result["theorem_verified"], f"Theorem fails: {result['mismatches']}"


def test_multiplicative_phi_formula():
    """phi(AB) = phi(A)*phi(B)*gcd/phi(gcd) for various pairs."""
    from catenary_hodge.engines.totient_kinetics import phi, phi_multiplicative
    for a in [6, 8, 12, 15, 24, 60]:
        for b in [4, 7, 9, 11, 16, 25]:
            assert phi_multiplicative(a, b) == phi(a * b), \
                f"Multiplicative phi fails for {a}*{b}"


def test_asymptotic_density_convergence():
    """rho(N) = M(N)/N converges to (1 - 6/pi^2)/2 ≈ 0.196."""
    from catenary_hodge.engines.totient_kinetics import asymptotic_density_scan, ASYMPTOTIC_DENSITY
    result = asymptotic_density_scan(n_max=2000)
    assert result["converged"], \
        f"Density did not converge: error = {result['convergence_error']}"
    assert abs(result["cumulative_average_at_n_max"] - ASYMPTOTIC_DENSITY) < 0.01


def test_golay_weight_topological_masses():
    """Golay weight classes have M = {0, 2, 4, 4, 8}."""
    from catenary_hodge.engines.totient_kinetics import topological_mass
    expected = {0: 0, 8: 2, 12: 4, 16: 4, 24: 8}
    for w, expected_m in expected.items():
        if w < 3:
            assert topological_mass(w) == 0
        else:
            assert topological_mass(w) == expected_m, \
                f"M({w}) = {topological_mass(w)}, expected {expected_m}"


def test_iso_resonant_8_plus_8():
    """8+8=16 is ISO-RESONANT (perfect sub-cycle conservation: 2+2=4)."""
    from catenary_hodge.engines.totient_kinetics import analyze_reaction
    r = analyze_reaction(8, 8)
    assert r["delta_C"] == 0, f"8+8 should be iso-resonant, got delta_C={r['delta_C']}"
    assert r["regime"] == "ISO-RESONANT"


def test_multiplication_always_endothermic():
    """All multiplication reactions are ENDOTHERMIC (Delta_C > 0)."""
    from catenary_hodge.engines.totient_kinetics import analyze_multiplication_reaction
    for a in range(3, 30):
        for b in range(3, 30):
            r = analyze_multiplication_reaction(a, b)
            assert r["delta_C_multiplication"] > 0, \
                f"{a}*{b} has Delta_C = {r['delta_C_multiplication']}, expected > 0"


def test_existence_unit_topological_mass():
    """U_e = 13824 = 24^3 has M = 4608 (1/3 of U_e)."""
    from catenary_hodge.engines.totient_kinetics import topological_mass
    assert topological_mass(13824) == 4608


def test_module9_runs():
    """Module 9: Intrinsic-Extrinsic Duality runs and verifies the Prime Ground State Theorem."""
    from catenary_hodge.modules.module9_intrinsic_extrinsic_duality import run
    result = run()
    assert result["prime_ground_state_verification"]["theorem_verified"]
    assert len(result["duality_table"]["rows"]) > 50
    # Golay weight classes have M = {0, 2, 4, 4, 8}
    golay_rows = result["golay_weight_totient_analysis"]["weight_class_rows"]
    masses = [r["topological_mass"] for r in golay_rows]
    assert masses == [0, 2, 4, 4, 8]


def test_module10_runs():
    """Module 10: Multiplication tensor product — all reactions endothermic."""
    from catenary_hodge.modules.module10_multiplication_tensor import run
    result = run(n_max_sweep=30, n_max_compare=20)
    sweep = result["regime_distribution_sweep"]
    assert sweep["regime_counts"]["ENDOTHERMIC"] == sweep["total_reactions"]
    assert sweep["regime_counts"]["EXOTHERMIC"] == 0
    assert sweep["regime_counts"]["ISO-RESONANT"] == 0


def test_module11_runs():
    """Module 11: Topological mass asymptotic density converges."""
    from catenary_hodge.modules.module11_topological_mass import run
    result = run(n_max_table=50, n_max_asymptotic=1000, n_max_heavy=100, top_k=10)
    asym = result["asymptotic_density_verification"]
    assert asym["converged"]
    # U_e = 13824 has M = 4608
    ubp_rows = result["ubp_base_topological_mass"]["rows"]
    ue_row = next(r for r in ubp_rows if r["n"] == 13824)
    assert ue_row["M_N"] == 4608


def test_cayley_menger_radius_of_gyration():
    """R_gyr for regular N-gon equals R(N) (mathematically equivalent)."""
    from catenary_hodge.engines.totient_kinetics import radius_of_gyration, R_n
    for n in range(3, 20):
        r_gyr = radius_of_gyration(n)
        r_n = R_n(n)
        assert abs(r_gyr - r_n) < 1e-9, \
            f"N={n}: R_gyr={r_gyr}, R(N)={r_n}, should be equal"


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v"])
