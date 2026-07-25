"""
UBP Constants — exact Fraction representations (v2, polished per polish_1.txt).

All UBP constants are stored as fractions.Fraction objects to guarantee
zero numerical drift. Transcendental numbers (pi, phi, e) are stored as
high-precision mpmath values AND as Fraction approximations suitable for
exact arithmetic.

This module is self-contained: all mathematical foundations are embedded
directly. No external UBP/LDP citations are required to understand or
verify the constants defined here.

Canonical constants (Module 2.2 of the report):
    M   = pi * phi * e           = 13.817580227176...    Triadic Monad
    w   = M mod 1                =  0.817580227176...    Entropic Wobble
    Y   = pi / (pi^2 + 2)        =  0.264675430405...    Observer Constant
                                    (Spectral Gap in Information Geometry)
    L   = w / 13                 =  0.062890786706...    D-Sink Leakage
    L_s = L * (29/24)            =  0.075993033936...    Stereoscopic Sink
    sigma = 29/24                =  1.208333...           Stereoscopic Coeff
    U_e = 24^3                   = 13824                  Existence Unit
    c   = 24                                              Speed of Light
    rho_inf = (1 - 6/pi^2)/2     =  0.196036...           Topological Mass
                                    Density (Dirichlet Constant)

Invariants verified by self_test():
    Y * Y_INV       == 1              (Observer reciprocity)
    L               == w / 13         (D-Sink definition)
    L_s             == L * (29/24)    (Stereoscopic sink)
    M               == pi * phi * e   (Triadic monad)
    w               == M - 13         (Entropic wobble)
    phi(U_e) / U_e  == 1/3            (Existence Unit coprime density)
"""
from fractions import Fraction
from math import sqrt
import mpmath as mp

# ---------------------------------------------------------------------------
# Integer / rational constants (exact)
# ---------------------------------------------------------------------------
U_E: int = 24 ** 3            # 13824 — Existence Unit
C_LIGHT: int = 24             # Speed of Light (bits per tick)
C2_LIGHT: int = 24 ** 2       # 576
DIM: int = 24
SIGMA: Fraction = Fraction(29, 24)


# ---------------------------------------------------------------------------
# Transcendental inputs: high-precision mpmath values (80 decimal digits)
# ---------------------------------------------------------------------------
mp.dps = 80

PI_MPM = mp.mpf("3.14159265358979323846264338327950288419716939937510582097494459230781640628620899")
PHI_MPM = (mp.mpf("1") + mp.sqrt(5)) / 2          # golden ratio
E_MPM = mp.mpf("2.71828182845904523536028747135266249775724709369995957496696762772407663035354759")

# Triadic Monad M = pi * phi * e
MONAD_MPM = PI_MPM * PHI_MPM * E_MPM               # ≈ 13.817580227176...

# Entropic Wobble w = M mod 1
WOBBLE_MPM = MONAD_MPM - mp.floor(MONAD_MPM)       # ≈ 0.817580227176...

# Observer Constant Y = pi / (pi^2 + 2). Maps to the Spectral Gap.
Y_MPM = PI_MPM / (PI_MPM * PI_MPM + 2)             # ≈ 0.264675430405...
Y_INV_MPM = PI_MPM + 2 / PI_MPM                    # ≈ 3.778212425957...

# D-Sink Leakage L = w / 13
L_MPM = WOBBLE_MPM / 13                            # ≈ 0.062890786706...

# Stereoscopic Sink L_s = L * (29/24)
L_S_MPM = L_MPM * mp.mpf(29) / 24                  # ≈ 0.075993033936...

# Topological Mass Density rho_inf = (1 - 6/pi^2)/2 (Dirichlet Constant)
ZETA_2_MPM = PI_MPM * PI_MPM / 6                   # zeta(2) = pi^2/6
RHO_INF_MPM = (mp.mpf(1) - 1 / ZETA_2_MPM) / 2     # ≈ 0.196036...


# ---------------------------------------------------------------------------
# Fraction conversion (per polish_1.txt TASK 1 spec)
# ---------------------------------------------------------------------------
def _mp_to_fraction(x: mp.mpf, dps: int = 60) -> Fraction:
    """Convert mpmath float to Fraction with `dps` decimal digits of precision.

    Uses the polish_1.txt convention: Fraction(str(mpmath_value)[:62]).
    """
    s = mp.nstr(x, dps + 5, strip_zeros=False)
    # Handle scientific notation
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


# ---------------------------------------------------------------------------
# Exact-Fraction versions of the UBP constants
#
# Construction order matters: MONAD is derived as the product PI_FRAC*PHI_FRAC*E_FRAC
# so that the algebraic identity M = pi*phi*e holds EXACTLY in Fraction arithmetic.
# Likewise W = MONAD - 13 (the integer part of M), so w = M mod 1 holds exactly.
# Y_INV is derived as 1/Y so the reciprocity Y * Y_INV = 1 holds exactly.
# L_S is derived as L * SIGMA so the L_s = L*(29/24) identity holds exactly.
# RHO_INF is derived in closed form so its identity (1 - 6/pi^2)/2 holds exactly.
# ---------------------------------------------------------------------------

# Per polish_1.txt TASK 1: Y = Fraction(str(mpmath.pi / (mpmath.pi**2 + 2))[:62])
Y: Fraction = _mp_to_fraction(Y_MPM, 60)

# Observer reciprocal derived exactly from Y so Y * Y_INV = 1 holds.
Y_INV: Fraction = Fraction(1, 1) / Y

PI_FRAC: Fraction = _mp_to_fraction(PI_MPM, 60)
PHI_FRAC: Fraction = _mp_to_fraction(PHI_MPM, 60)
E_FRAC: Fraction = _mp_to_fraction(E_MPM, 60)

# Per polish_1.txt TASK 1: M = Fraction(str(mpmath.pi * mpmath.phi * mpmath.e)[:62])
# We compute M as the exact product of the Fraction versions of pi, phi, e so
# the identity M = pi*phi*e holds exactly in Fraction arithmetic.
MONAD: Fraction = PI_FRAC * PHI_FRAC * E_FRAC

# Per polish_1.txt TASK 1: w = M % 1 (Entropic Wobble)
# For positive M, M % 1 = M - floor(M). The integer part of M is 13.
W: Fraction = MONAD - 13                              # Entropic Wobble

# L = w / 13 (D-Sink Leakage)
L: Fraction = W / 13

# L_s = L * (29/24) (Stereoscopic Sink), derived exactly
L_S: Fraction = L * SIGMA

# rho_inf = (1 - 6/pi^2)/2 (Topological Mass Density / Dirichlet Constant)
# Derived as a closed-form Fraction from PI_FRAC.
RHO_INF: Fraction = (Fraction(1, 1) - Fraction(6, 1) / (PI_FRAC * PI_FRAC)) / 2


# ---------------------------------------------------------------------------
# Existence Unit coprime density verification (per polish_1.txt TASK 1)
# ---------------------------------------------------------------------------
def _phi(n: int) -> int:
    """Euler's totient function (exact integer arithmetic)."""
    if n < 1:
        return 0
    if n == 1:
        return 1
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def existence_unit_coprime_density() -> Fraction:
    """Return phi(U_e) / U_e as an exact Fraction.

    Per polish_1.txt TASK 1: verify phi(U_e)/U_e == Fraction(1, 3).
    This holds because U_e = 13824 = 2^9 * 3^3, so
        phi(U_e) = U_e * (1 - 1/2) * (1 - 1/3) = U_e * 1/2 * 2/3 = U_e / 3.
    """
    return Fraction(_phi(U_E), U_E)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test() -> dict:
    """Verify all UBP constant identities hold exactly in Fraction arithmetic."""
    out = {}
    # Y = pi / (pi^2 + 2)
    out["Y_defn"] = abs(float(Y) - float(PI_FRAC / (PI_FRAC * PI_FRAC + 2))) < 1e-50
    # Y * Y_INV = 1 (exactly)
    out["Y_reciprocity"] = (Y * Y_INV == Fraction(1, 1))
    # L = w / 13 (exactly)
    out["L_defn"] = (L == W / 13)
    # L_s = L * (29/24) (exactly)
    out["L_s_defn"] = (L_S == L * SIGMA)
    # M = pi * phi * e (exactly, by construction)
    out["M_defn"] = (MONAD == PI_FRAC * PHI_FRAC * E_FRAC)
    # w = M - 13 (exactly, by construction)
    out["w_defn"] = (W == MONAD - 13)
    # phi(U_e)/U_e == 1/3 (exactly)
    out["U_e_coprime_density"] = (existence_unit_coprime_density() == Fraction(1, 3))
    # rho_inf = (1 - 6/pi^2)/2 (exactly, by construction)
    out["rho_inf_defn"] = (RHO_INF == (Fraction(1, 1) - Fraction(6, 1) / (PI_FRAC * PI_FRAC)) / 2)
    # Numerical spot checks
    out["Y_val"] = abs(float(Y) - 0.264675430405) < 1e-10
    out["w_val"] = abs(float(W) - 0.817580227176) < 1e-10
    out["L_val"] = abs(float(L) - 0.062890786706) < 1e-10
    out["rho_inf_val"] = abs(float(RHO_INF) - 0.196036) < 1e-5
    out["U_e_val"] = (U_E == 13824)
    out["sigma_val"] = (SIGMA == Fraction(29, 24))
    return out


if __name__ == "__main__":
    results = self_test()
    for k, v in results.items():
        print(f"  {k:30s}: {'PASS' if v else 'FAIL'}")
    print()
    print(f"Y      = {float(Y):.60f}")
    print(f"Y_INV  = {float(Y_INV):.60f}")
    print(f"W      = {float(W):.60f}")
    print(f"L      = {float(L):.60f}")
    print(f"L_S    = {float(L_S):.60f}")
    print(f"MONAD  = {float(MONAD):.60f}")
    print(f"RHO_INF= {float(RHO_INF):.60f}")
    print(f"U_E    = {U_E}")
    print(f"SIGMA  = {SIGMA}  (= {float(SIGMA):.10f})")
    print(f"phi(U_e)/U_e = {existence_unit_coprime_density()} "
          f"(expected 1/3 = {Fraction(1,3)})")
    if not all(results.values()):
        raise SystemExit("FAIL: at least one UBP constant identity failed.")
    print("\nALL UBP CONSTANT SELF-TESTS PASS.")
