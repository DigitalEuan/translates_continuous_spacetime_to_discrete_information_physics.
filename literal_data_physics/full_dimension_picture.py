#!/usr/bin/env python3
"""
================================================================================
LITERAL DATA PHYSICS — Full Dimension Picture
================================================================================
The Catenary Hodge framework defines 4 form degrees (k=0,1,2,3).
We built everything at k=1 (pairwise). Now we build the full picture.

k=0 (Vertex):  Single integer — mass, radius, charge, zone
k=1 (Edge):    Pairwise — Totient Defect ΔC(A,B) — how A and B react
k=2 (Face):    Three-body — Face Defect — how A,B,C share common structure
k=3 (Cell):    Four-body — Cell Density — how A,B,C,D occupy the substrate

Each level reveals structure invisible to the levels below it.
================================================================================
"""

import math
import random
import time
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
from fractions import Fraction

# ==============================================================================
# CORE
# ==============================================================================

def phi(n):
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

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def factorize(n):
    f = {}; d = 2
    while d * d <= n:
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def C(n):
    if n < 3: return 0
    return (n // 2) - (phi(n) // 2)

def R_n(n):
    if n < 3: return 1.0
    return 1.0 / (2.0 * math.sin(math.pi / n))

def sigma_k(n, k=1):
    result = 1
    for p, e in factorize(n).items():
        result *= (p ** (k * (e + 1)) - 1) // (p ** k - 1)
    return result

def geometric_tension(n):
    if n < 3: return 0.0
    area = (n / 4.0) * (1.0 / math.tan(math.pi / n))
    circle_area = (n ** 2) / (4.0 * math.pi)
    return 1.0 - (area / circle_area)

# ==============================================================================
# k=0: VERTEX — Single Integer Properties
# ==============================================================================

class Vertex:
    """
    k=0: The properties of a single integer.
    Like a particle at rest — mass, charge, radius, spin.
    """
    def __init__(self, n):
        self.n = n
        self.mass = C(n)
        self.charge = n % 2
        self.radius = R_n(n)
        self.tension = geometric_tension(n)
        self.factors = factorize(n)
        self.omega = sum(self.factors.values())
        self.omega_d = len(self.factors)
        self.is_prime = is_prime(n)
        self.phi_ratio = phi(n) / n if n > 0 else 0
        self.sigma_ratio = sigma_k(n, 1) / n if n > 0 else 0
    
    def describe(self):
        f_str = "×".join(f"{p}^{e}" if e > 1 else str(p) for p, e in self.factors.items())
        return (f"Vertex({self.n}: M={self.mass}, R={self.radius:.3f}, "
                f"q={self.charge}, ω={self.omega}, factors={f_str})")

# ==============================================================================
# k=1: EDGE — Pairwise Interaction (Totient Defect)
# ==============================================================================

def edge_defect(a, b):
    """
    k=1: The Totient Defect — pairwise interaction between two integers.
    Like a bond between two atoms.
    
    ΔC(A,B) = OddPair(A,B) + (φ(A) + φ(B) − φ(A+B)) / 2
    """
    return (1 if (a % 2 == 1 and b % 2 == 1) else 0) + \
           (phi(a) + phi(b) - phi(a + b)) // 2

def edge_regime(dc):
    if dc < 0: return "EXOTHERMIC"
    if dc > 0: return "ENDOTHERMIC"
    return "ISO-RESONANT"

# ==============================================================================
# k=2: FACE — Three-Body Interaction (Triple GCD Structure)
# ==============================================================================

def face_defect(a, b, c):
    """
    k=2: The Face Defect — three-body interaction.
    Measures how the triple intersection (gcd(a,b,c)) differs from
    the pairwise intersections (gcd(a,b), gcd(b,c), gcd(a,c)).
    
    In the Golay code: this is the AND-product of three codewords.
    For integers: this is the triple GCD structure.
    
    The face defect captures REDUNDANCY — when pairwise interactions
    over-predict the triple interaction.
    """
    gcd_ab = math.gcd(a, b)
    gcd_bc = math.gcd(b, c)
    gcd_ac = math.gcd(a, c)
    gcd_abc = math.gcd(a, math.gcd(b, c))
    
    c_ab = C(gcd_ab) if gcd_ab >= 3 else 0
    c_bc = C(gcd_bc) if gcd_bc >= 3 else 0
    c_ac = C(gcd_ac) if gcd_ac >= 3 else 0
    c_abc = C(gcd_abc) if gcd_abc >= 3 else 0
    
    pairwise_avg = (c_ab + c_bc + c_ac) / 3
    face_excess = c_abc - pairwise_avg
    
    return {
        "gcd_ab": gcd_ab, "gcd_bc": gcd_bc, "gcd_ac": gcd_ac,
        "gcd_abc": gcd_abc,
        "C_ab": c_ab, "C_bc": c_bc, "C_ac": c_ac, "C_abc": c_abc,
        "pairwise_avg": pairwise_avg,
        "face_excess": face_excess,
        "is_three_body": abs(face_excess) > 0.5,
        "redundancy": pairwise_avg - c_abc,  # how much pairwise over-predicts
    }

# ==============================================================================
# k=3: CELL — Four-Body Interaction (Substrate Density)
# ==============================================================================

def cell_defect(a, b, c, d):
    """
    k=3: The Cell Defect — four-body interaction.
    Measures how the quadruple structure relates to triple and pairwise.
    
    In the Golay code: this is the MOG octad density (759 octads in 24D).
    For integers: this is the quadruple GCD structure and the density
    of common factors across four integers.
    
    The cell defect captures DENSITY — how packed the common structure is.
    """
    gcd_abcd = math.gcd(a, math.gcd(b, math.gcd(c, d)))
    
    # Triple GCDs
    gcds_triple = [
        math.gcd(a, math.gcd(b, c)),
        math.gcd(a, math.gcd(b, d)),
        math.gcd(a, math.gcd(c, d)),
        math.gcd(b, math.gcd(c, d)),
    ]
    
    # Pairwise GCDs
    gcds_pair = [
        math.gcd(a, b), math.gcd(a, c), math.gcd(a, d),
        math.gcd(b, c), math.gcd(b, d), math.gcd(c, d),
    ]
    
    c_quad = C(gcd_abcd) if gcd_abcd >= 3 else 0
    c_triples = [C(g) if g >= 3 else 0 for g in gcds_triple]
    c_pairs = [C(g) if g >= 3 else 0 for g in gcds_pair]
    
    triple_avg = sum(c_triples) / len(c_triples)
    pair_avg = sum(c_pairs) / len(c_pairs)
    
    # Cell defect: how the quad relates to triples and pairs
    cell_excess = c_quad - triple_avg
    density = c_quad / pair_avg if pair_avg > 0 else 0
    
    return {
        "gcd_abcd": gcd_abcd,
        "C_quad": c_quad,
        "triple_avg": triple_avg,
        "pair_avg": pair_avg,
        "cell_excess": cell_excess,
        "density": density,
        "is_four_body": abs(cell_excess) > 0.5,
    }

# ==============================================================================
# FULL DIMENSION PICTURE — Unified Analysis
# ==============================================================================

def full_dimension_analysis(N_range=(3, 100)):
    """
    Analyze all four form degrees simultaneously.
    How much information does each k-level add?
    """
    ns = list(range(N_range[0], N_range[1] + 1))
    
    # k=0: Vertex properties
    vertices = {n: Vertex(n) for n in ns}
    
    # k=1: Edge defects (sample pairs)
    random.seed(42)
    edge_samples = random.sample([(a, b) for a in ns for b in ns if a < b], 
                                  min(500, len(ns) * (len(ns) - 1) // 2))
    edge_data = []
    for a, b in edge_samples:
        dc = edge_defect(a, b)
        edge_data.append({"a": a, "b": b, "defect": dc, "regime": edge_regime(dc)})
    
    # k=2: Face defects (sample triples)
    face_samples = random.sample(
        [(a, b, c) for a in range(N_range[0], min(50, N_range[1] + 1))
         for b in range(a, min(50, N_range[1] + 1))
         for c in range(b, min(50, N_range[1] + 1))],
        min(500, 20000)
    )
    face_data = []
    for a, b, c in face_samples:
        fd = face_defect(a, b, c)
        face_data.append({"a": a, "b": b, "c": c, **fd})
    
    # k=3: Cell defects (sample quads)
    cell_samples = random.sample(
        [(a, b, c, d) for a in range(N_range[0], min(30, N_range[1] + 1))
         for b in range(a, min(30, N_range[1] + 1))
         for c in range(b, min(30, N_range[1] + 1))
         for d in range(c, min(30, N_range[1] + 1))],
        min(500, 10000)
    )
    cell_data = []
    for a, b, c, d in cell_samples:
        cd = cell_defect(a, b, c, d)
        cell_data.append({"a": a, "b": b, "c": c, "d": d, **cd})
    
    return {
        "vertices": vertices,
        "edge_data": edge_data,
        "face_data": face_data,
        "cell_data": cell_data,
    }

# ==============================================================================
# INFORMATION CONTENT AT EACH k-LEVEL
# ==============================================================================

def information_per_level(N_range=(3, 200)):
    """
    How much information does each form degree carry?
    """
    ns = list(range(N_range[0], N_range[1] + 1))
    
    def entropy(values):
        if not values: return 0.0
        total = len(values); counts = Counter(values)
        return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
    
    # k=0: Vertex entropy
    k0_mass = [C(n) for n in ns]
    k0_charge = [n % 2 for n in ns]
    k0_zone = [0 if is_prime(n) else (1 if C(n) <= 4 else (2 if C(n) <= 15 else 3)) for n in ns]
    
    # k=1: Edge entropy (pairwise)
    random.seed(42)
    pairs = random.sample([(a, b) for a in ns for b in ns if a < b], min(1000, len(ns)*(len(ns)-1)//2))
    k1_defects = [edge_defect(a, b) for a, b in pairs]
    k1_regimes = [edge_regime(d) for d in k1_defects]
    
    # k=2: Face entropy (three-body)
    triples = random.sample(
        [(a, b, c) for a in range(3, min(50, N_range[1]+1))
         for b in range(a, min(50, N_range[1]+1))
         for c in range(b, min(50, N_range[1]+1))],
        min(1000, 20000)
    )
    k2_excess = [face_defect(a, b, c)["face_excess"] for a, b, c in triples]
    k2_three_body = [int(face_defect(a, b, c)["is_three_body"]) for a, b, c in triples]
    
    # k=3: Cell entropy (four-body)
    quads = random.sample(
        [(a, b, c, d) for a in range(3, min(30, N_range[1]+1))
         for b in range(a, min(30, N_range[1]+1))
         for c in range(b, min(30, N_range[1]+1))
         for d in range(c, min(30, N_range[1]+1))],
        min(500, 10000)
    )
    k3_excess = [cell_defect(a, b, c, d)["cell_excess"] for a, b, c, d in quads]
    k3_four_body = [int(cell_defect(a, b, c, d)["is_four_body"]) for a, b, c, d in quads]
    
    # Quantize continuous values
    def quantize_list(vals, bins, lo, hi):
        return [min(max(int((v - lo) / (hi - lo) * bins), 0), bins - 1) for v in vals]
    
    return {
        "k0": {
            "mass_entropy": entropy(k0_mass),
            "charge_entropy": entropy(k0_charge),
            "zone_entropy": entropy(k0_zone),
            "total": entropy(k0_mass) + entropy(k0_charge) + entropy(k0_zone),
        },
        "k1": {
            "defect_entropy": entropy(quantize_list(k1_defects, 32, -50, 50)),
            "regime_entropy": entropy(k1_regimes),
            "total": entropy(quantize_list(k1_defects, 32, -50, 50)) + entropy(k1_regimes),
        },
        "k2": {
            "excess_entropy": entropy(quantize_list(k2_excess, 16, -20, 20)),
            "three_body_entropy": entropy(k2_three_body),
            "total": entropy(quantize_list(k2_excess, 16, -20, 20)) + entropy(k2_three_body),
        },
        "k3": {
            "excess_entropy": entropy(quantize_list(k3_excess, 16, -20, 20)),
            "four_body_entropy": entropy(k3_four_body),
            "total": entropy(quantize_list(k3_excess, 16, -20, 20)) + entropy(k3_four_body),
        },
    }

# ==============================================================================
# CROSS-LEVEL INTERACTIONS
# ==============================================================================

def cross_level_analysis(N_range=(3, 100)):
    """
    How do the k-levels interact?
    Does k=2 add information beyond k=1?
    Does k=3 add information beyond k=2?
    """
    ns = list(range(N_range[0], N_range[1] + 1))
    
    def entropy(values):
        if not values: return 0.0
        total = len(values); counts = Counter(values)
        return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
    
    def joint_entropy(*lists):
        total = len(lists[0])
        counts = Counter(zip(*lists))
        return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
    
    # Sample triples with all k-levels
    random.seed(42)
    triples = random.sample(
        [(a, b, c) for a in range(3, min(40, N_range[1]+1))
         for b in range(a, min(40, N_range[1]+1))
         for c in range(b, min(40, N_range[1]+1))],
        min(500, 10000)
    )
    
    # k=0: mass of each
    k0_a = [C(a) for a, b, c in triples]
    k0_b = [C(b) for a, b, c in triples]
    k0_c = [C(c) for a, b, c in triples]
    
    # k=1: pairwise defects
    k1_ab = [edge_defect(a, b) for a, b, c in triples]
    k1_bc = [edge_defect(b, c) for a, b, c in triples]
    k1_ac = [edge_defect(a, c) for a, b, c in triples]
    
    # k=2: face defect
    k2 = [face_defect(a, b, c)["face_excess"] for a, b, c in triples]
    k2_flag = [int(face_defect(a, b, c)["is_three_body"]) for a, b, c in triples]
    
    # Quantize
    def q(vals, bins, lo, hi):
        return [min(max(int((v - lo) / (hi - lo) * bins), 0), bins - 1) for v in vals]
    
    k1_ab_q = q(k1_ab, 16, -30, 30)
    k1_bc_q = q(k1_bc, 16, -30, 30)
    k2_q = q(k2, 16, -20, 20)
    
    # Information at each level
    h_k0 = joint_entropy(k0_a, k0_b, k0_c)
    h_k1 = joint_entropy(k1_ab_q, k1_bc_q)
    h_k2 = entropy(k2_flag)
    
    # Does k=2 add beyond k=1?
    h_k1_joint_k2 = joint_entropy(k1_ab_q, k1_bc_q, k2_flag)
    marginal_k2 = h_k1_joint_k2 - h_k1
    
    # Does k=1 add beyond k=0?
    h_k0_joint_k1 = joint_entropy(k0_a, k0_b, k0_c, k1_ab_q)
    marginal_k1 = h_k0_joint_k1 - h_k0
    
    return {
        "n_triples": len(triples),
        "k0_entropy": h_k0,
        "k1_entropy": h_k1,
        "k2_entropy": h_k2,
        "k0_k1_joint": h_k0_joint_k1,
        "k1_k2_joint": h_k1_joint_k2,
        "marginal_k1_over_k0": marginal_k1,
        "marginal_k2_over_k1": marginal_k2,
        "total_joint": h_k1_joint_k2,
        "three_body_rate": sum(k2_flag) / len(k2_flag) * 100,
    }

# ==============================================================================
# THE FULL PICTURE — demonstration
# ==============================================================================

def full_picture_demo():
    """
    Show the full dimension picture for a specific example.
    """
    # Pick a triple with interesting structure
    a, b, c = 60, 84, 105
    
    print(f"  EXAMPLE: ({a}, {b}, {c})")
    print(f"  ─────────────────────────────────────────")
    
    # k=0: Vertex
    va, vb, vc = Vertex(a), Vertex(b), Vertex(c)
    print(f"\n  k=0 (Vertex):")
    print(f"    {va.describe()}")
    print(f"    {vb.describe()}")
    print(f"    {vc.describe()}")
    
    # k=1: Edge
    dc_ab = edge_defect(a, b)
    dc_bc = edge_defect(b, c)
    dc_ac = edge_defect(a, c)
    print(f"\n  k=1 (Edge — pairwise Totient Defect):")
    print(f"    ΔC({a},{b}) = {dc_ab:+d} ({edge_regime(dc_ab)})")
    print(f"    ΔC({b},{c}) = {dc_bc:+d} ({edge_regime(dc_bc)})")
    print(f"    ΔC({a},{c}) = {dc_ac:+d} ({edge_regime(dc_ac)})")
    print(f"    Sum: {dc_ab + dc_bc + dc_ac:+d}")
    
    # k=2: Face
    fd = face_defect(a, b, c)
    print(f"\n  k=2 (Face — three-body GCD structure):")
    print(f"    gcd({a},{b}) = {fd['gcd_ab']}, C = {fd['C_ab']}")
    print(f"    gcd({b},{c}) = {fd['gcd_bc']}, C = {fd['C_bc']}")
    print(f"    gcd({a},{c}) = {fd['gcd_ac']}, C = {fd['C_ac']}")
    print(f"    gcd({a},{b},{c}) = {fd['gcd_abc']}, C = {fd['C_abc']}")
    print(f"    Pairwise avg C: {fd['pairwise_avg']:.2f}")
    print(f"    Triple C: {fd['C_abc']}")
    print(f"    Face excess: {fd['face_excess']:+.2f}")
    print(f"    Redundancy: {fd['redundancy']:+.2f}")
    print(f"    Three-body: {'YES' if fd['is_three_body'] else 'no'}")
    
    # k=3: Cell (add a fourth)
    d = 210
    cd = cell_defect(a, b, c, d)
    print(f"\n  k=3 (Cell — four-body density, adding {d}):")
    print(f"    gcd({a},{b},{c},{d}) = {cd['gcd_abcd']}, C = {cd['C_quad']}")
    print(f"    Triple avg C: {cd['triple_avg']:.2f}")
    print(f"    Pair avg C: {cd['pair_avg']:.2f}")
    print(f"    Cell excess: {cd['cell_excess']:+.2f}")
    print(f"    Density: {cd['density']:.3f}")
    print(f"    Four-body: {'YES' if cd['is_four_body'] else 'no'}")
    
    # Summary
    print(f"\n  DIMENSION PROJECTION:")
    print(f"    k=0: {a},{b},{c} have masses {va.mass},{vb.mass},{vc.mass}")
    print(f"    k=1: Pairwise defects are {dc_ab},{dc_bc},{dc_ac}")
    print(f"    k=2: Face excess is {fd['face_excess']:+.2f} "
          f"({'three-body' if fd['is_three_body'] else 'pairwise only'})")
    print(f"    k=3: Cell excess is {cd['cell_excess']:+.2f} "
          f"({'four-body' if cd['is_four_body'] else 'three-body only'})")
    
    # What each level reveals
    print(f"\n  WHAT EACH LEVEL REVEALS:")
    print(f"    k=0: Individual identities (mass, radius, charge)")
    print(f"    k=1: How pairs react (exothermic/endothermic/iso-resonant)")
    print(f"    k=2: How triples share structure (redundancy in pairwise)")
    print(f"    k=3: How quads pack into the substrate (density)")

# ==============================================================================
# MAIN
# ==============================================================================

def run():
    print("=" * 80)
    print(" LITERAL DATA PHYSICS — Full Dimension Picture")
    print("=" * 80)
    t0 = time.time()
    
    # ── 1. Full Picture Demo ──
    print("\n[1] FULL PICTURE — one example")
    print("─" * 60)
    full_picture_demo()
    
    # ── 2. Information Per Level ──
    print("\n\n[2] INFORMATION PER FORM DEGREE")
    print("─" * 60)
    info = information_per_level((3, 200))
    for k in ['k0', 'k1', 'k2', 'k3']:
        level = info[k]
        print(f"\n  {k}:")
        for key, val in level.items():
            if key != 'total':
                print(f"    {key:25s}: {val:.4f} bits")
        print(f"    {'TOTAL':25s}: {level['total']:.4f} bits")
    
    total_all = sum(info[k]['total'] for k in ['k0', 'k1', 'k2', 'k3'])
    print(f"\n  Combined (all levels): {total_all:.4f} bits")
    
    # ── 3. Cross-Level Analysis ──
    print("\n\n[3] CROSS-LEVEL INTERACTIONS")
    print("─" * 60)
    cross = cross_level_analysis((3, 100))
    print(f"  Triples analyzed: {cross['n_triples']}")
    print(f"  Three-body rate: {cross['three_body_rate']:.1f}%")
    print(f"\n  Entropy at each level:")
    print(f"    k=0 (vertex): {cross['k0_entropy']:.4f} bits")
    print(f"    k=1 (edge):   {cross['k1_entropy']:.4f} bits")
    print(f"    k=2 (face):   {cross['k2_entropy']:.4f} bits")
    print(f"\n  Marginal information (what each level ADDS):")
    print(f"    k=1 over k=0: {cross['marginal_k1_over_k0']:+.4f} bits")
    print(f"    k=2 over k=1: {cross['marginal_k2_over_k1']:+.4f} bits")
    print(f"\n  Total joint (k=1 + k=2): {cross['total_joint']:.4f} bits")
    
    # ── 4. Systematic Scan ──
    print("\n\n[4] SYSTEMATIC SCAN — three-body rates by type")
    print("─" * 60)
    
    # Group triples by type
    type_counts = Counter()
    three_body_by_type = Counter()
    
    for a in range(3, 51):
        for b in range(a, 51):
            for c in range(b, 51):
                fd = face_defect(a, b, c)
                # Classify triple
                n_prime = sum(1 for x in [a, b, c] if is_prime(x))
                type_key = f"{n_prime}prime"
                type_counts[type_key] += 1
                if fd['is_three_body']:
                    three_body_by_type[type_key] += 1
    
    print(f"  {'Type':>10} {'Total':>6} {'3-body':>7} {'Rate':>7}")
    for type_key in sorted(type_counts):
        total = type_counts[type_key]
        tb = three_body_by_type.get(type_key, 0)
        print(f"  {type_key:>10} {total:>6} {tb:>7} {tb/total*100:>6.1f}%")
    
    # ── 5. The Dimension Map ──
    print("\n\n[5] THE DIMENSION MAP — what lives at each level")
    print("─" * 60)
    
    # Sample data at each level
    random.seed(42)
    ns = list(range(3, 101))
    
    # k=0
    k0_primes = sum(1 for n in ns if is_prime(n))
    k0_composites = len(ns) - k0_primes
    
    # k=1
    pairs = random.sample([(a, b) for a in ns for b in ns if a < b], 500)
    k1_exo = sum(1 for a, b in pairs if edge_defect(a, b) < 0)
    k1_endo = sum(1 for a, b in pairs if edge_defect(a, b) > 0)
    k1_iso = sum(1 for a, b in pairs if edge_defect(a, b) == 0)
    
    # k=2
    triples = random.sample(
        [(a, b, c) for a in range(3, 51) for b in range(a, 51) for c in range(b, 51)],
        500
    )
    k2_three = sum(1 for a, b, c in triples if face_defect(a, b, c)['is_three_body'])
    k2_pairwise = 500 - k2_three
    
    # k=3
    quads = random.sample(
        [(a, b, c, d) for a in range(3, 31) for b in range(a, 31) 
         for c in range(b, 31) for d in range(c, 31)],
        500
    )
    k3_four = sum(1 for a, b, c, d in quads if cell_defect(a, b, c, d)['is_four_body'])
    k3_three = 500 - k3_four
    
    print(f"""
  k=0 (Vertex): {len(ns)} integers
    Primes (ground): {k0_primes}
    Composites (excited): {k0_composites}

  k=1 (Edge): 500 sampled pairs
    EXOTHERMIC: {k1_exo} ({k1_exo/5:.0f}%)
    ENDOTHERMIC: {k1_endo} ({k1_endo/5:.0f}%)
    ISO-RESONANT: {k1_iso} ({k1_iso/5:.0f}%)

  k=2 (Face): 500 sampled triples
    Three-body: {k2_three} ({k2_three/5:.0f}%)
    Pairwise only: {k2_pairwise} ({k2_pairwise/5:.0f}%)

  k=3 (Cell): 500 sampled quads
    Four-body: {k3_four} ({k3_four/5:.0f}%)
    Three-body only: {k3_three} ({k3_three/5:.0f}%)
""")
    
    # ── Synthesis ──
    print("=" * 80)
    print(" SYNTHESIS — The Full Dimension Picture")
    print("=" * 80)
    print(f"""
  THE DIMENSION PROJECTION MAP:

  k=0 (Vertex)  ────  Single integers
  │                 Mass, radius, charge, zone
  │                 {k0_primes} ground states, {k0_composites} excited
  │
  k=1 (Edge)    ────  Pairwise interactions
  │                 Totient Defect ΔC(A,B)
  │                 {k1_exo} exo, {k1_endo} endo, {k1_iso} iso-resonant
  │                 Information added: {cross['marginal_k1_over_k0']:+.2f} bits
  │
  k=2 (Face)    ────  Three-body interactions
  │                 Face Defect via triple GCD
  │                 {k2_three}/500 ({k2_three/5:.0f}%) have three-body force
  │                 Information added: {cross['marginal_k2_over_k1']:+.2f} bits
  │
  k=3 (Cell)    ────  Four-body interactions
                    Cell Defect via quadruple GCD
                    {k3_four}/500 ({k3_four/5:.0f}%) have four-body force

  KEY INSIGHT:
    We built everything at k=1 and found NO three-body force.
    The Catenary Hodge framework showed us: three-body forces
    live at k=2 (face level), not k=1 (edge level).
    
    Each form degree reveals structure invisible to the levels below:
    - k=0 tells you WHAT something is
    - k=1 tells you HOW pairs interact
    - k=2 tells you HOW triples share structure
    - k=3 tells you HOW quads pack into the substrate
    
    The "dimension projection" is the map between these levels.
    The Catenary Hodge study was always about this map.
""")
    
    t1 = time.time()
    print(f"  Total time: {t1-t0:.1f}s")
    print("=" * 80)

if __name__ == "__main__":
    run()
