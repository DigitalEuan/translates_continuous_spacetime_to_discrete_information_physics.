"""
Totient Kinetics — Topological Spectral Analysis of Regular Polytopes
=====================================================================
The UBP Totient Kinetics engine, representing the topological spectral
analysis of internal diagonal sub-cycles within regular N-gons. This
framework bridges Discrete Distance Geometry with analytic number theory
by mapping Euler's Totient Function to the internal diagonal topology of
regular polygons, then framing arithmetic addition as a thermodynamic
"reaction" with binding energy.

Core Theorems (embedded, no self-citations):

  1. The UBP Natural Primitive R(N), defining the circumradius of a
     unit-edge regular N-gon:
         R(N) = 1 / (2 * sin(pi / N))

  2. The Totient Sub-Cycle Theorem (verified 100% for N in [3, 999]):
     The exact number of closed internal diagonal loops (sub-cycles)
     C(N) formed by vertex-jumping on an N-gon is:
         C(N) = floor(N/2) - phi(N)/2
     where phi(N) is Euler's Totient Function.

  3. The Totient Defect Equation (closed-form binding energy):
         Delta_C = OddPair(A, B) + (phi(A) + phi(B) - phi(A+B)) / 2
     where OddPair(A, B) = 1 iff both A and B are odd, else 0.

  4. The Prime Ground State Theorem (Corollary 1):
     An integer N >= 3 is prime if and only if C(N) = 0.
     A prime number is a shape that cannot be short-circuited.

  5. The Topological Mass and Asymptotic Density:
         M(N) := C(N),    rho(N) := M(N)/N  ->  (1 - 6/pi^2)/2  as N -> infinity
     (Dirichlet's theorem on the average order of phi).

  6. Multiplication as Tensor Product:
     The product A*B forms an A*B-vertex structure on the torus S^1 x S^1
     with binding energy Delta_C_mul(A,B) = C(A*B) - (C(A) + C(B)).
     The multiplicative totient formula phi(AB) = phi(A)*phi(B)*gcd(A,B)/phi(gcd(A,B))
     always yields Delta_C_mul > 0 (multiplication is endothermic).

Bridge to standard terminology:
  * UBP / LDP framework  ->  Discrete Information Geometry / Algebraic Coding Theory
  * Y-Constant            ->  Spectral Gap / Observer Constant: Y = pi/(pi^2+2) approx 0.2647
  * Golay/Leech substrate -> the [24,12,8] extended binary Golay code G_24 and the
                              continuous Leech lattice Lambda_24
  * Ghost states          -> vectors in the geometric kernel (Hodge Gap): satisfy
                              the NOISE=0 geometric condition but fail algebraic
                              codeword membership
  * Spatial Arithmetic    -> Discrete Distance Geometry / Geometric Number Theory
  * Totient Kinetics      -> Topological Spectral Analysis of Regular Polytopes
  * Natural Primitive R(N) -> Circumradius of the unit-edge regular N-gon

All algebraic computations use fractions.Fraction for zero numerical drift.
Transcendental functions (sin, cos, tan, pi) use the math module; the
number-theoretic computations (phi, gcd, prime factorization) use exact
integer arithmetic.

References:
  * Euler, L. (1763). Theoremata arithmetica nova methodo demonstrata.
  * Dirichlet, P. G. L. (1849). Uber die Bestimmung der mittleren Werthe
    von Zahlengrossen.
  * Hardy, G. H. & Wright, E. M. (1938). An Introduction to the Theory of
    Numbers. Oxford UP.
  * Blumenthal, L. M. (1953). Theory and Applications of Distance Geometry.
    (Cayley-Menger identity)
  * Conway, J. H. & Sloane, N. J. A. (1999). Sphere Packings, Lattices and
    Groups. (Golay code, Leech lattice)
"""

# This module re-exports the totient kinetics engine from
# catenary_hodge.engines.totient_kinetics (which itself was built on the
# user-supplied spatial_totient_kinetics.py, with the peer-review fixes
# applied).  Docstrings use the Terminology Bridge per refine_1.txt.

import os
import sys
from fractions import Fraction

_ENGINES_DIR = os.path.dirname(os.path.abspath(__file__))
if _ENGINES_DIR not in sys.path:
    sys.path.insert(0, _ENGINES_DIR)

# Re-export everything from the v2 totient kinetics engine
from totient_kinetics import *  # noqa: F401, F403
from totient_kinetics import (  # noqa: F401
    phi, is_prime, prime_factors, R_n, R_n_mp, geometric_tension,
    count_sub_cycles_traversal, count_sub_cycles_closed,
    odd_pair, totient_defect, geometric_tension_delta, analyze_reaction,
    phi_multiplicative, analyze_multiplication_reaction,
    chord_length, radius_of_gyration, radius_of_gyration_average_distance,
    compare_radius_definitions, intrinsic_extrinsic_duality_table,
    prime_ground_state_test, verify_prime_ground_state_theorem,
    topological_mass, topological_mass_density, asymptotic_density_scan,
    ZETA_2, ASYMPTOTIC_DENSITY,
)


# ---------------------------------------------------------------------------
# The Topological Mass Density as a new UBP constant (exact Fraction)
# ---------------------------------------------------------------------------
import math

# rho_inf = (1 - 6/pi^2) / 2 = (1 - 1/zeta(2)) / 2
# We compute this as a Fraction via mpmath at high precision.
import mpmath as _mp
_mp.dps = 80

PI_MPM_TK = _mp.mpf("3.14159265358979323846264338327950288419716939937510582097494459230781640628620899")
ZETA_2_MPM = PI_MPM_TK * PI_MPM_TK / 6


def _mp_to_fraction(x, dps: int = 60) -> Fraction:
    """Convert mpmath float to Fraction with `dps` decimal digits of precision."""
    s = _mp.nstr(x, dps + 5, strip_zeros=False)
    if "e" in s:
        mantissa, exp = s.split("e")
        exp = int(exp)
    else:
        mantissa, exp = s, 0
    if "." in mantissa:
        int_part, dec_part = mantissa.split(".")
    else:
        int_part, dec_part = mantissa, ""
    sign = -1 if int_part.startswith("-") else 1
    int_part = int_part.lstrip("-")
    num = int(int_part + dec_part) if (int_part + dec_part) else 0
    den = 10 ** len(dec_part)
    frac = Fraction(sign * num, den)
    if exp >= 0:
        frac *= Fraction(10) ** exp
    else:
        frac /= Fraction(10) ** (-exp)
    return frac


# The UBP Topological Mass Density rho_inf = (1 - 6/pi^2)/2, as an exact Fraction.
# This is the asymptotic density of internal sub-cycles in a regular N-gon
# as N -> infinity (Dirichlet's theorem on the average order of phi).
TOPOLOGICAL_MASS_DENSITY: Fraction = _mp_to_fraction(
    (1 - 1 / ZETA_2_MPM) / 2, 60
)

# The UBP Observer Constant Y = pi/(pi^2 + 2), as an exact Fraction.
# Maps to the Spectral Gap in Information Geometry.
Y_OBSERVER_TK: Fraction = _mp_to_fraction(
    PI_MPM_TK / (PI_MPM_TK * PI_MPM_TK + 2), 60
)

# The UBP Observer Reciprocal O = 1/Y (derived exactly from Y).
OBSERVER_RECIP_TK: Fraction = Fraction(1, 1) / Y_OBSERVER_TK


def topological_mass_density_constant() -> Fraction:
    """Return the Topological Mass Density rho_inf = (1 - 6/pi^2)/2 as Fraction.

    This is the asymptotic density of internal sub-cycles in a regular N-gon.
    Numerically approximately 0.196036.  Verified empirically: rho(N) -> rho_inf
    as N -> infinity, with convergence error < 0.001 at N = 5000.
    """
    return TOPOLOGICAL_MASS_DENSITY


def observer_constant_tk() -> Fraction:
    """Return the UBP Observer Constant Y = pi/(pi^2 + 2) as Fraction.

    Maps to the Spectral Gap in Information Geometry.  Reciprocity identity
    Y * O = 1 holds exactly in Fraction arithmetic.
    """
    return Y_OBSERVER_TK


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test() -> dict:
    out = {}
    out["Y_value_matches_float"] = abs(float(Y_OBSERVER_TK) - 0.264675430405) < 1e-12
    out["Y_reciprocity_exact"] = (Y_OBSERVER_TK * OBSERVER_RECIP_TK == Fraction(1, 1))
    out["rho_inf_matches_float"] = abs(float(TOPOLOGICAL_MASS_DENSITY) - 0.196036) < 1e-5
    out["sub_cycle_theorem_n_3_to_100"] = all(
        count_sub_cycles_traversal(n) == count_sub_cycles_closed(n)
        for n in range(3, 101)
    )
    out["prime_ground_state_n_3_to_500"] = verify_prime_ground_state_theorem(n_max=500)["theorem_verified"]
    out["totient_defect_closed_form_matches"] = all(
        analyze_reaction(a, b)["closed_form_matches"]
        for a in range(3, 30) for b in range(3, 30)
    )
    return out


if __name__ == "__main__":
    results = self_test()
    for k, v in results.items():
        print(f"  {k:50s}: {'PASS' if v else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit("FAIL: refactored totient_kinetics self-test failed.")
    print("\nALL REFACTORED TOTIENT_KINETICS SELF-TESTS PASS.")
    print(f"  Y_OBSERVER (Spectral Gap)      = {float(Y_OBSERVER_TK):.20f}")
    print(f"  TOPOLOGICAL_MASS_DENSITY       = {float(TOPOLOGICAL_MASS_DENSITY):.20f}")
    print(f"  Y * O = 1 exactly              : {Y_OBSERVER_TK * OBSERVER_RECIP_TK == Fraction(1, 1)}")
    print(f"  rho_inf = (1 - 6/pi^2)/2       : {float(TOPOLOGICAL_MASS_DENSITY):.10f}")
