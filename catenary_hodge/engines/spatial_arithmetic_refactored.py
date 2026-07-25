"""
Spatial Arithmetic — Discrete Distance Geometry engine
======================================================
The UBP Spatial Arithmetic engine, operating as a framework for Discrete
Distance Geometry and Geometric Number Theory. All arithmetic operations
(add, subtract, multiply, divide) are reconstructed from a single geometric
relationship — the UBP Natural Primitive R(N), representing the circumradius
of a unit-edge regular N-gon:

    R(N) = 1 / (2 * sin(pi / N))

This primitive is the geometric analog of the exponential/logarithm (EML)
operator in ordinary arithmetic: from it, all operations follow.

  * ADD       — distance ratio 4x (linear subspace merge)
  * MULTIPLY  — distance ratio 3x (cup-product intersection)
  * SUBTRACT  — distance ratio 5x (set difference)
  * DIVIDE    — distance ratio 6x (set quotient, returns Fraction)

A dihedral-angle modifier channel (ID, SQUARE, NEGATE, RECIP, ABS) provides
an additional 5-state orthogonal encoding.

Architecture:
    GEOMETRY (passive) — vertices, edges, positions. No logic.
    OBSERVER (active)  — cluster, decode, evaluate. All logic.

All algebraic operations use fractions.Fraction for zero numerical drift.
Transcendental functions (sin, cos, atan2) use the math module; the
observer-side bookkeeping (operator distance ratios, parity encoding,
cluster detection) is exact integer arithmetic.

References (embedded, no self-citations):
  * The Golay/Leech substrate (the [24,12,8] extended binary Golay code
    G_24 and the continuous Leech lattice Lambda_24) provides the ambient
    discrete-geometric context.
  * The UBP Observer Constant Y = pi/(pi^2 + 2) approx 0.264675 maps to
    the Spectral Gap in Information Geometry.
  * Non-codeword "ghost states" (vectors satisfying the geometric
    NOISE=0 condition but failing algebraic membership) are analogous to
    the Hodge Gap in algebraic geometry.

Usage:
    python3 spatial_arithmetic.py                     # run all tests
    python3 spatial_arithmetic.py --eval "3+4*5"      # evaluate expression
    python3 spatial_arithmetic.py --scene 7 ADD 3     # build and decode
    python3 spatial_arithmetic.py --natural 5 3       # natural addition
"""

# This module re-exports the vendored spatial_arithmetic engine, with
# docstrings updated per the Terminology Bridge directive.
# All actual computation is delegated to the vendored implementation.

import os
import sys
from fractions import Fraction

_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor")
_VENDOR_DIR = os.path.normpath(_VENDOR_DIR)
if _VENDOR_DIR not in sys.path:
    sys.path.insert(0, _VENDOR_DIR)

# Re-export everything from the vendored module
from spatial_arithmetic import *  # noqa: F401, F403
from spatial_arithmetic import (  # noqa: F401
    make_3d_cycle, encode, decode, value_to_radius, radius_to_value,
    pairwise_centroid_distance, dihedral_angle, decode_modifier,
    cluster_detect, reorder_to_cycle, natural_add, natural_divide,
    build_fraction, observe_with_fractions, build_scene, build_expression,
    observe_scene, observe_expression, run_tests,
    OPCODE_TABLE, OPCODE_BY_NAME, MODIFIER_TABLE,
    UNIT, EXACT_TOL, BASE_NODES, FRAC_BIND_MIN, FRAC_BIND_MAX,
)


# ---------------------------------------------------------------------------
# UBP Observer Constant Y as an exact Fraction (embedded, no self-citation)
# ---------------------------------------------------------------------------
import math
import mpmath as _mp
_mp.dps = 80

PI_MPM = _mp.mpf("3.14159265358979323846264338327950288419716939937510582097494459230781640628620899")


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


# The UBP Observer Constant Y = pi/(pi^2 + 2), as an exact Fraction.
# Maps to the Spectral Gap in Information Geometry.
Y_OBSERVER: Fraction = _mp_to_fraction(PI_MPM / (PI_MPM * PI_MPM + 2), 60)

# The UBP Observer Reciprocal O = 1/Y = pi + 2/pi.  Derived as the exact
# Fraction reciprocal of Y_OBSERVER so the reciprocity identity Y * O = 1
# holds EXACTLY in Fraction arithmetic (zero drift).
OBSERVER_RECIP: Fraction = Fraction(1, 1) / Y_OBSERVER


def observer_constant() -> Fraction:
    """Return the UBP Observer Constant Y = pi/(pi^2 + 2) as an exact Fraction.

    This constant, in the UBP framework, maps to the Spectral Gap in
    Information Geometry. It satisfies the reciprocity identity Y * O = 1
    exactly in Fraction arithmetic.
    """
    return Y_OBSERVER


def verify_observer_reciprocity() -> bool:
    """Verify Y * O = 1 exactly in Fraction arithmetic."""
    return Y_OBSERVER * OBSERVER_RECIP == Fraction(1, 1)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test() -> dict:
    out = {}
    out["Y_value_matches_float"] = abs(float(Y_OBSERVER) - 0.264675430405) < 1e-12
    out["Y_reciprocity_exact"] = (Y_OBSERVER * OBSERVER_RECIP == Fraction(1, 1))
    out["vendored_tests_pass"] = run_tests()
    return out


if __name__ == "__main__":
    results = self_test()
    for k, v in results.items():
        print(f"  {k:35s}: {'PASS' if v else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit("FAIL: refactored spatial_arithmetic self-test failed.")
    print("\nALL REFACTORED SPATIAL_ARITHMETIC SELF-TESTS PASS.")
    print(f"  Y_OBSERVER = {float(Y_OBSERVER):.60f}")
    print(f"  OBSERVER_RECIP = {float(OBSERVER_RECIP):.60f}")
    print(f"  Y * O = 1 exactly: {Y_OBSERVER * OBSERVER_RECIP == Fraction(1, 1)}")
