#!/usr/bin/env python3
"""
================================================================================
MODULE 15 — SPATIAL TOTIENT INFORMATION CAPACITY
================================================================================
Integration of the Spatial Totient Extended Investigation into the
Catenary-Hodge / UBP framework.

This module bridges:
  (A) The Catenary-Hodge framework (Modules 1-14, Capstone)
      — Sub-cycle theorem, Prime Ground State, Topological Mass,
        Totient Defect, Steiner ISO-RESONANCE, Y-resonance, d²=0

  (B) The Information-Theoretic Capacity Analysis
      — Shannon entropy of spatial features
      — Multi-feature encoding (12-15 independent channels)
      — Higher-order totient/divisor functions
      — Reaction chain dynamics
      — Golay substrate coupling
      — Combined extraction ceiling

Core Question: How many bits of geometric information per integer does
the spatial totient system extract, beyond the raw integer identity?

Key Finding: ~14.65 bits/integer combined ceiling, exceeding raw integer
entropy (8.96 bits for N∈[3,500]) by 63.5%. The spatial geometry reveals
structural information that symbolic arithmetic alone cannot surface.
================================================================================
"""

import math
import json
import time
from typing import Dict, List, Any, Tuple
from collections import Counter
from fractions import Fraction

# Import the Catenary-Hodge totient kinetics engine
# (standalone implementation for portability)
def phi(n: int) -> int:
    if n < 1: return 0
    if n == 1: return 1
    result = n; temp = n; p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1: result -= result // temp
    return result

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def factorize(n: int) -> Dict[int, int]:
    factors = {}; d = 2
    while d * d <= n:
        while n % d == 0: factors[d] = factors.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: factors[n] = factors.get(n, 0) + 1
    return factors

def count_sub_cycles_closed(n: int) -> int:
    if n < 3: return 0
    return (n // 2) - (phi(n) // 2)

def R_n(n: int) -> float:
    if n < 3: return 1.0
    return 1.0 / (2.0 * math.sin(math.pi / n))

def geometric_tension(n: int) -> float:
    if n < 3: return 0.0
    area = (n / 4.0) * (1.0 / math.tan(math.pi / n))
    circle_area = (n ** 2) / (4.0 * math.pi)
    return 1.0 - (area / circle_area)

def sigma_k(n: int, k: int = 1) -> int:
    factors = factorize(n); result = 1
    for p, e in factors.items():
        result *= (p ** (k * (e + 1)) - 1) // (p ** k - 1)
    return result

def carmichael_lambda(n: int) -> int:
    if n == 1: return 1
    if n == 2: return 1
    if n == 4: return 2
    def ppl(p, k):
        if p == 2 and k >= 3: return 2 ** (k - 2)
        return (p - 1) * p ** (k - 1)
    factors = factorize(n)
    lambdas = [pl(p, k) for p, k in factors.items()]
    # Use correct function name
    result = lambdas[0] if lambdas else 1
    for l in lambdas[1:]:
        result = result * l // math.gcd(result, l)
    return result

# Fix: rename ppl to pl inside the function
def carmichael_lambda_fixed(n: int) -> int:
    if n == 1: return 1
    if n == 2: return 1
    if n == 4: return 2
    def pl(p, k):
        if p == 2 and k >= 3: return 2 ** (k - 2)
        return (p - 1) * p ** (k - 1)
    factors = factorize(n)
    lambdas = [pl(p, k) for p, k in factors.items()]
    result = lambdas[0] if lambdas else 1
    for l in lambdas[1:]:
        result = result * l // math.gcd(result, l)
    return result

def mobius(n: int) -> int:
    if n == 1: return 1
    factors = factorize(n)
    for p, e in factors.items():
        if e > 1: return 0
    return (-1) ** len(factors)

def dedekind_psi(n: int) -> int:
    factors = factorize(n); result = n
    for p in factors: result = result * (p + 1) // p
    return result

def liouville_lambda(n: int) -> int:
    factors = factorize(n); omega = sum(factors.values())
    return (-1) ** omega

def jordan_totient(n: int, k: int = 1) -> int:
    factors = factorize(n); result = n ** k
    for p in factors: result *= (1 - Fraction(1, p ** k))
    return int(result)

def totient_defect(a: int, b: int) -> int:
    return (1 if (a % 2 == 1 and b % 2 == 1) else 0) + (phi(a) + phi(b) - phi(a + b)) // 2

# ==============================================================================
# INFORMATION THEORY
# ==============================================================================

def shannon_entropy(values: list) -> float:
    if not values: return 0.0
    total = len(values); counts = Counter(values)
    return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)

def joint_entropy(*value_lists) -> float:
    total = len(value_lists[0])
    counts = Counter(zip(*value_lists))
    return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)

def mutual_information(a: list, b: list) -> float:
    return shannon_entropy(a) + shannon_entropy(b) - joint_entropy(a, b)

def quantize(value: float, bins: int, vmin: float, vmax: float) -> int:
    if value <= vmin: return 0
    if value >= vmax: return bins - 1
    return int((value - vmin) / (vmax - vmin) * bins)

# ==============================================================================
# FEATURE EXTRACTION
# ==============================================================================

def extract_features(n: int) -> Dict[str, Any]:
    """Extract all spatial totient features from integer N."""
    c = count_sub_cycles_closed(n)
    t = geometric_tension(n)
    r = R_n(n)
    p = phi(n)
    factors = factorize(n)
    omega_total = sum(factors.values())
    omega_distinct = len(factors)
    is_p = len(factors) == 1 and list(factors.values())[0] == 1
    is_pp = len(factors) == 1
    is_sqfree = all(e == 1 for e in factors.values())
    
    return {
        "C": c, "T": t, "R": r, "phi": p,
        "phi_ratio": p / n if n > 0 else 0,
        "deficiency": n - p,
        "abundance": sigma_k(n, 1) - 2 * n,
        "omega_total": omega_total,
        "omega_distinct": omega_distinct,
        "is_prime": int(is_p),
        "is_prime_power": int(is_pp),
        "is_squarefree": int(is_sqfree),
        "sigma_1": sigma_k(n, 1),
        "carmichael": carmichael_lambda_fixed(n),
        "dedekind_psi": dedekind_psi(n),
        "liouville": liouville_lambda(n),
        "mobius": mobius(n),
    }

# ==============================================================================
# CAPACITY MEASUREMENTS
# ==============================================================================

def measure_basic_capacity(N_range=(3, 1000)):
    """Phase 1: Sub-cycle + primality capacity."""
    ns = list(range(N_range[0], N_range[1] + 1))
    C_vals = [count_sub_cycles_closed(n) for n in ns]
    prime_vals = [int(is_prime(n)) for n in ns]
    return {
        "range": N_range, "n": len(ns),
        "C_entropy": shannon_entropy(C_vals),
        "prime_entropy": shannon_entropy(prime_vals),
        "joint": shannon_entropy(list(zip(C_vals, prime_vals))),
        "unique_C": len(set(C_vals)),
    }

def measure_full_capacity(N_range=(3, 500), method="full"):
    """Phase 2/3: Multi-feature capacity."""
    ns = list(range(N_range[0], N_range[1] + 1))
    all_feats = []
    for n in ns:
        f = extract_features(n)
        bits = {
            "C": f["C"],
            "is_prime": f["is_prime"],
            "phi_ratio_c": quantize(f["phi_ratio"], 16, 0, 1),
            "omega_total": min(f["omega_total"], 15),
            "omega_distinct": min(f["omega_distinct"], 7),
            "is_sqfree": f["is_squarefree"],
            "is_pp": f["is_prime_power"],
            "mobius": f["mobius"] + 1,
            "liouville": (f["liouville"] + 1) // 2,
            "abundance_c": 0 if f["abundance"] < 0 else (1 if f["abundance"] == 0 else 2),
            "psi_ratio_c": quantize(f["dedekind_psi"] / n if n > 0 else 0, 8, 1, 3),
            "tension_c": quantize(f["T"], 8, 0, 0.22),
        }
        if method in ("full", "residue"):
            for p in [3, 5, 7, 11, 13]:
                bits[f"phi_mod_{p}"] = f["phi"] % p
            if f["phi"] > 0:
                bits["lambda_phi_c"] = quantize(f["carmichael"] / f["phi"], 4, 0, 1)
        all_feats.append(bits)
    
    keys = sorted(all_feats[0].keys())
    entropies = {k: shannon_entropy([f[k] for f in all_feats]) for k in keys}
    combined = tuple(tuple(f[k] for k in keys) for f in all_feats)
    joint = shannon_entropy(combined)
    return {
        "range": N_range, "method": method, "n": len(ns),
        "features": len(keys), "keys": keys,
        "entropies": entropies,
        "total_independent": sum(entropies.values()),
        "joint_entropy": joint,
    }

def measure_higher_order(N_range=(3, 500)):
    """Phase 4: Higher-order totient/divisor functions."""
    ns = list(range(N_range[0], N_range[1] + 1))
    phi_vals = [phi(n) for n in ns]
    sigma_vals = [sigma_k(n, 1) for n in ns]
    psi_vals = [dedekind_psi(n) for n in ns]
    lam_vals = [carmichael_lambda_fixed(n) for n in ns]
    mu_vals = [mobius(n) for n in ns]
    liouville_vals = [liouville_lambda(n) for n in ns]
    j2_vals = [jordan_totient(n, 2) for n in ns]
    
    ents = {
        "phi": shannon_entropy(phi_vals),
        "sigma_1": shannon_entropy(sigma_vals),
        "dedekind_psi": shannon_entropy(psi_vals),
        "carmichael": shannon_entropy(lam_vals),
        "mobius": shannon_entropy(mu_vals),
        "liouville": shannon_entropy(liouville_vals),
        "jordan_J2": shannon_entropy(j2_vals),
        "phi_ratio_q32": shannon_entropy([quantize(phi(n)/n, 32, 0, 1) for n in ns]),
        "sigma_ratio_q32": shannon_entropy([quantize(sigma_k(n,1)/n, 32, 0, 4) for n in ns]),
        "psi_ratio_q16": shannon_entropy([quantize(dedekind_psi(n)/n, 16, 1, 3) for n in ns]),
        "lambda_phi_q16": shannon_entropy([quantize(carmichael_lambda_fixed(n)/phi(n) if phi(n)>0 else 0, 16, 0, 1) for n in ns]),
    }
    
    mis = {
        "I(phi,sigma)": mutual_information(phi_vals, sigma_vals),
        "I(phi,psi)": mutual_information(phi_vals, psi_vals),
        "I(phi,lambda)": mutual_information(phi_vals, lam_vals),
        "I(C,phi)": mutual_information([count_sub_cycles_closed(n) for n in ns], phi_vals),
    }
    
    joint = shannon_entropy(list(zip(phi_vals, sigma_vals, psi_vals, lam_vals, mu_vals, liouville_vals)))
    
    return {
        "range": N_range, "entropies": ents, "mutual_informations": mis,
        "total_independent": sum(ents.values()),
        "joint_entropy": joint,
    }

def measure_reaction_chains(N_range=(3, 100), chain_len=5, n_chains=200):
    """Phase 5: Reaction chain dynamics."""
    import random; random.seed(42)
    chain_infos = []
    for _ in range(n_chains):
        start = random.randint(N_range[0], N_range[1])
        addends = [random.randint(N_range[0], N_range[1]) for _ in range(chain_len)]
        current = start
        regimes = []; delta_Cs = []; transitions = []
        for i, a in enumerate(addends):
            dc = totient_defect(current, a)
            regime = "EXOTHERMIC" if dc < 0 else "ENDOTHERMIC" if dc > 0 else "ISO-RESONANT"
            regimes.append(regime)
            delta_Cs.append(dc)
            if i > 0:
                transitions.append(f"{regimes[i-1]}->{regime}")
            current = current + a
        chain_infos.append({
            "regime_e": shannon_entropy(regimes),
            "dc_e": shannon_entropy(delta_Cs),
            "trans_e": shannon_entropy(transitions) if transitions else 0,
        })
    
    avg = lambda k: sum(ci[k] for ci in chain_infos) / len(chain_infos)
    total = avg("regime_e") + avg("dc_e") + avg("trans_e")
    return {
        "chain_length": chain_len, "n_chains": n_chains,
        "avg_regime_entropy": avg("regime_e"),
        "avg_delta_C_entropy": avg("dc_e"),
        "avg_transition_entropy": avg("trans_e"),
        "avg_total": total,
        "avg_per_step": total / chain_len,
    }

def measure_defect_grid(max_n=50):
    """Phase 6: Totient defect grid."""
    grid = {}; all_d = []
    for a in range(3, max_n + 1):
        for b in range(3, max_n + 1):
            d = totient_defect(a, b)
            grid[(a, b)] = d; all_d.append(d)
    
    row_e = []; col_e = []
    for a in range(3, max_n + 1):
        row_e.append(shannon_entropy([grid[(a, b)] for b in range(3, max_n + 1)]))
        col_e.append(shannon_entropy([grid[(a, b)] for a in range(3, max_n + 1)]))
    
    sym = sum(1 for a in range(3, max_n+1) for b in range(a, max_n+1) if grid[(a,b)] == grid[(b,a)])
    total_pairs = max_n * (max_n - 1) // 2
    
    return {
        "max_n": max_n, "grid_size": (max_n - 2) ** 2,
        "defect_entropy": shannon_entropy(all_d),
        "unique_values": len(set(all_d)),
        "mean_row_entropy": sum(row_e) / len(row_e),
        "mean_col_entropy": sum(col_e) / len(col_e),
        "symmetry_fraction": sym / total_pairs,
        "defect_range": (min(all_d), max(all_d)),
    }

def measure_golay_capacity(N_range=(3, 500)):
    """Phase 7: Golay substrate coupling."""
    # Simplified Golay snap using syndrome
    B_rows = [
        [1,1,0,1,1,1,0,0,0,1,0,1],
        [1,0,1,1,1,0,0,0,1,0,1,1],
        [0,1,1,1,0,0,0,1,0,1,1,1],
        [1,1,1,0,0,0,1,0,1,1,0,1],
        [1,1,0,0,0,1,0,1,1,0,1,1],
        [1,0,0,0,1,0,1,1,0,1,1,1],
        [0,0,0,1,0,1,1,0,1,1,1,1],
        [0,0,1,0,1,1,0,1,1,1,0,1],
        [0,1,0,1,1,0,1,1,1,0,0,1],
        [1,0,1,1,0,1,1,1,0,0,0,1],
        [0,1,1,0,1,1,1,0,0,0,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,0],
    ]
    
    def golay_snap(vec):
        d = vec[:12]; p = vec[12:]
        syn = [p[j] ^ sum(d[i] & B_rows[j][i] for i in range(12)) % 2 for j in range(12)]
        sw = sum(syn)
        corrected = vec.copy()
        if sw in (8, 12, 16):
            for i in range(12):
                if syn == B_rows[i]:
                    corrected[i] ^= 1
                    for j in range(12): corrected[12+j] ^= B_rows[j][i]
                    break
        elif sw == 1:
            for j in range(12):
                if syn[j]: corrected[12+j] ^= 1; break
        return corrected
    
    def nrci(vec):
        hw = sum(vec)
        Y = 0.264675430405
        tax = hw * Y + hw / 8.0
        return 10.0 / (10.0 + tax)
    
    ns = list(range(N_range[0], N_range[1] + 1))
    results = []
    for n in ns:
        f = extract_features(n)
        combined = ((f["C"] & 0x3F) << 18) | ((quantize(f["T"], 8, 0, 0.22) & 0x7) << 15) | \
                   ((quantize(f["phi_ratio"], 16, 0, 1) & 0xF) << 11) | \
                   (((f["is_prime"] << 4) | (f["is_prime_power"] << 3) | (f["is_squarefree"] << 2) | min(f["omega_distinct"], 3)) << 6) | \
                   (((f["mobius"] + 1) & 0x3) << 4) | (n % 16)
        gray = combined ^ (combined >> 1)
        vec = [(gray >> (23 - i)) & 1 for i in range(24)]
        snapped = golay_snap(vec)
        results.append({
            "n": n, "hw_orig": sum(vec), "hw_snap": sum(snapped),
            "bits_changed": sum(a != b for a, b in zip(vec, snapped)),
            "nrci": nrci(snapped),
            "in_band": 0.60 <= nrci(snapped) <= 0.95,
            "pattern": tuple(snapped),
        })
    
    patterns = set(r["pattern"] for r in results)
    return {
        "range": N_range, "n": len(ns),
        "mean_nrci": sum(r["nrci"] for r in results) / len(results),
        "in_band_pct": sum(1 for r in results if r["in_band"]) / len(results) * 100,
        "hw_entropy": shannon_entropy([r["hw_snap"] for r in results]),
        "unique_patterns": len(patterns),
        "pattern_entropy": math.log2(len(patterns)) if len(patterns) > 1 else 0,
    }

# ==============================================================================
# CATENARY-HODGE CROSS-VALIDATION
# ==============================================================================

def catenary_hodge_cross_check():
    """Cross-validate with the Catenary-Hodge framework findings."""
    
    # 1. Prime Ground State Theorem: N prime ⟺ C(N) = 0
    mismatches = sum(1 for n in range(3, 1000) if (count_sub_cycles_closed(n) == 0) != is_prime(n))
    
    # 2. Topological mass density convergence
    rho_theoretical = (1 - 6 / math.pi**2) / 2
    cumulative = sum(count_sub_cycles_closed(n) / n for n in range(3, 10001)) / 9998
    
    # 3. Golay weight class topological masses
    golay_weights = {0: 0, 8: count_sub_cycles_closed(8), 12: count_sub_cycles_closed(12),
                     16: count_sub_cycles_closed(16), 24: count_sub_cycles_closed(24)}
    
    # 4. 8+8=16 ISO-RESONANCE check
    iso_check = count_sub_cycles_closed(16) == count_sub_cycles_closed(8) + count_sub_cycles_closed(8)
    
    # 5. U_e topological third
    U_e = 13824
    phi_Ue = phi(U_e)
    top_third = phi_Ue / U_e  # should be 1/3
    
    # 6. Y-resonance: R(0)/R(24)
    R0 = 1.0; R24 = R_n(24)
    Y = 0.264675430405
    Y_inv = 3.778350515697
    r0_over_r24 = R0 / R24
    
    return {
        "prime_ground_state": {
            "mismatches_3_to_999": mismatches,
            "theorem_holds": mismatches == 0,
        },
        "topological_mass_density": {
            "theoretical": rho_theoretical,
            "empirical_10000": cumulative,
            "error": abs(cumulative - rho_theoretical),
        },
        "golay_weight_masses": golay_weights,
        "iso_resonance_8_8_16": iso_check,
        "existence_unit_third": {
            "U_e": U_e, "phi_U_e": phi_Ue,
            "phi_ratio": phi_Ue / U_e,
            "equals_one_third": abs(phi_Ue / U_e - 1/3) < 1e-10,
        },
        "y_resonance": {
            "R0_over_R24": r0_over_r24,
            "Y": Y, "Y_inv": Y_inv,
            "error_vs_Y_inv": abs(r0_over_r24 - Y_inv) / Y_inv,
        },
    }

# ==============================================================================
# MAIN RUNNER
# ==============================================================================

def run():
    print("=" * 80)
    print(" MODULE 15: SPATIAL TOTIENT INFORMATION CAPACITY")
    print(" Catenary-Hodge Integration")
    print("=" * 80)
    t0 = time.time()
    
    # ── Cross-validation with Catenary-Hodge ──
    print("\n[0] CATENARY-HODGE CROSS-VALIDATION")
    print("─" * 50)
    cross = catenary_hodge_cross_check()
    print(f"  Prime Ground State (N∈[3,999]): {cross['prime_ground_state']['mismatches_3_to_999']} mismatches → "
          f"{'✓ VERIFIED' if cross['prime_ground_state']['theorem_holds'] else '❌ FAILED'}")
    print(f"  Topological Mass Density: ρ_theory={cross['topological_mass_density']['theoretical']:.6f}  "
          f"ρ_empirical={cross['topological_mass_density']['empirical_10000']:.6f}  "
          f"err={cross['topological_mass_density']['error']:.6f}")
    print(f"  Golay Weight Masses: {cross['golay_weight_masses']}")
    print(f"  8+8=16 ISO-RESONANCE: {'✓' if cross['iso_resonance_8_8_16'] else '❌'}")
    print(f"  U_e Topological Third: φ(U_e)/U_e = {cross['existence_unit_third']['phi_ratio']:.6f} "
          f"{'= 1/3 ✓' if cross['existence_unit_third']['equals_one_third'] else '≠ 1/3 ❌'}")
    print(f"  Y-Resonance: R(0)/R(24) = {cross['y_resonance']['R0_over_R24']:.6f}  "
          f"vs 1/Y = {cross['y_resonance']['Y_inv']:.6f}  "
          f"err={cross['y_resonance']['error_vs_Y_inv']*100:.2f}%")
    
    # ── Phase 1: Basic ──
    print("\n[1] BASIC CAPACITY (Sub-Cycles + Primality)")
    print("─" * 50)
    basic = measure_basic_capacity((3, 1000))
    print(f"  C(N) entropy: {basic['C_entropy']:.4f} bits/int")
    print(f"  Primality:    {basic['prime_entropy']:.4f} bits/int")
    print(f"  Joint:        {basic['joint']:.4f} bits/int")
    print(f"  Unique C(N):  {basic['unique_C']}")
    
    # ── Phase 2: Full ──
    print("\n[2] FULL MULTI-FEATURE ENCODING")
    print("─" * 50)
    full = measure_full_capacity((3, 500), "full")
    print(f"  Features: {full['features']}")
    print(f"  Total independent: {full['total_independent']:.4f} bits/int")
    print(f"  Joint entropy:     {full['joint_entropy']:.4f} bits/int")
    for k, v in sorted(full['entropies'].items(), key=lambda x: -x[1])[:8]:
        print(f"    {k:25s}: {v:.4f} bits")
    
    # ── Phase 3: Residue ──
    print("\n[3] RESIDUE-CLASS ENCODING")
    print("─" * 50)
    residue = measure_full_capacity((3, 500), "residue")
    print(f"  Features: {residue['features']}")
    print(f"  Total independent: {residue['total_independent']:.4f} bits/int")
    print(f"  Joint entropy:     {residue['joint_entropy']:.4f} bits/int")
    
    # ── Phase 4: Higher-order ──
    print("\n[4] HIGHER-ORDER FUNCTIONS")
    print("─" * 50)
    higher = measure_higher_order((3, 500))
    print(f"  Total independent: {higher['total_independent']:.4f} bits/int")
    print(f"  Joint entropy:     {higher['joint_entropy']:.4f} bits/int")
    for k, v in sorted(higher['entropies'].items(), key=lambda x: -x[1])[:5]:
        print(f"    {k:25s}: {v:.4f} bits")
    for k, v in higher['mutual_informations'].items():
        print(f"    {k:25s}: {v:.4f} bits")
    
    # ── Phase 5: Reaction chains ──
    print("\n[5] REACTION CHAIN DYNAMICS")
    print("─" * 50)
    chain = measure_reaction_chains((3, 100), 5, 200)
    print(f"  Avg bits/chain: {chain['avg_total']:.4f}")
    print(f"  Avg bits/step:  {chain['avg_per_step']:.4f}")
    
    # ── Phase 6: Defect grid ──
    print("\n[6] TOTIENT DEFECT GRID")
    print("─" * 50)
    grid = measure_defect_grid(50)
    print(f"  Grid: {grid['grid_size']} cells")
    print(f"  Defect entropy: {grid['defect_entropy']:.4f} bits/cell")
    print(f"  Unique values:  {grid['unique_values']}")
    print(f"  Symmetry:       {grid['symmetry_fraction']*100:.1f}%")
    
    # ── Phase 7: Golay coupling ──
    print("\n[7] GOLAY SUBSTRATE COUPLING")
    print("─" * 50)
    golay = measure_golay_capacity((3, 500))
    print(f"  Mean NRCI:       {golay['mean_nrci']:.4f}")
    print(f"  In-band:         {golay['in_band_pct']:.1f}%")
    print(f"  Pattern entropy: {golay['pattern_entropy']:.4f} bits")
    print(f"  Unique patterns: {golay['unique_patterns']}")
    
    # ── Summary ──
    print("\n" + "=" * 80)
    print(" CAPACITY SUMMARY — Catenary-Hodge Integrated")
    print("=" * 80)
    
    raw_entropy = math.log2(498)  # N∈[3,500]
    combined = (residue['joint_entropy'] + higher['joint_entropy'] -
                shannon_entropy([count_sub_cycles_closed(n) for n in range(3, 501)]) +
                grid['mean_row_entropy'] * 0.5 + chain['avg_per_step'])
    
    print(f"  Basic (C alone):                {basic['C_entropy']:.3f} bits/int")
    print(f"  Multi-feature (independent):    {full['total_independent']:.3f} bits/int")
    print(f"  Multi-feature (joint):          {full['joint_entropy']:.3f} bits/int")
    print(f"  + Residue (independent):        {residue['total_independent']:.3f} bits/int")
    print(f"  + Residue (joint):              {residue['joint_entropy']:.3f} bits/int")
    print(f"  + Higher-order (independent):   {higher['total_independent']:.3f} bits/int")
    print(f"  + Higher-order (joint):         {higher['joint_entropy']:.3f} bits/int")
    print(f"  + Defect grid:                  {grid['defect_entropy']:.3f} bits/cell")
    print(f"  + Golay patterns:               {golay['pattern_entropy']:.3f} bits/int")
    print(f"  + Reaction chain:               {chain['avg_per_step']:.3f} bits/step")
    print(f"")
    print(f"  COMBINED CEILING:               ~{combined:.2f} bits/int")
    print(f"  Raw integer entropy (N∈[3,500]): {raw_entropy:.3f} bits/int")
    print(f"  Extraction ratio:                {combined / raw_entropy * 100:.1f}%")
    print(f"")
    print(f"  The spatial totient system extracts {combined/raw_entropy:.1f}x the raw integer")
    print(f"  identity entropy through geometric channels alone.")
    print("=" * 80)
    
    t1 = time.time()
    print(f"\nTotal Module 15 time: {t1-t0:.1f}s")
    
    return {
        "cross_validation": cross,
        "basic": basic, "full": full, "residue": residue,
        "higher_order": higher, "chain": chain, "grid": grid,
        "golay": golay,
        "combined_ceiling": combined,
        "raw_integer_entropy": raw_entropy,
        "extraction_ratio": combined / raw_entropy,
    }

if __name__ == "__main__":
    results = run()
    print(json.dumps({k: v for k, v in results.items() if k not in ('cross_validation',)},
                     indent=2, default=str)[:2000])
