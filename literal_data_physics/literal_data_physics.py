"""
================================================================================
LITERAL DATA PHYSICS (LDP) — Spatial Totient Library
================================================================================
A framework where integers ARE physical objects with measurable properties,
and arithmetic operations ARE physical reactions governed by the Totient
Defect Equation.

Core discovery (Craig, 2026):
  Every integer N ≥ 3 has a "spatial body" — a regular N-gon whose
  internal diagonal structure (sub-cycles) determines its physical
  behavior. The Totient Defect Equation governs all interactions:

    ΔC(A,B) = OddPair(A,B) + (φ(A) + φ(B) − φ(A+B)) / 2

  ΔC < 0: EXOTHERMIC — energy released (complexity dissolves)
  ΔC > 0: ENDOTHERMIC — energy absorbed (complexity builds)
  ΔC = 0: ISO-RESONANT — pure transfer (conservation)

  Natural flow: COMPOSITE → PRIME (energy flows downhill to ground states)

This library provides:
  - DataObject: an integer as a physical object
  - DataReaction: the interaction between two objects
  - DataField: a collection of objects that evolve through reactions
  - MetaCheck: spatial bit arrangement (shape = meaning)
================================================================================
"""

import math
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction

# ==============================================================================
# CORE NUMBER THEORY — the "laws of physics" for data
# ==============================================================================

def phi(n: int) -> int:
    """Euler's Totient: count of integers ≤ n coprime to n.
    In spatial terms: the number of step-sizes that traverse ALL vertices
    of a regular N-gon without short-circuiting."""
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
    """Primality test. In spatial terms: C(N) = 0 (ground state)."""
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def factorize(n: int) -> Dict[int, int]:
    """Prime factorization. Returns {prime: exponent} dict."""
    f = {}; d = 2
    while d * d <= n:
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def sub_cycles(n: int) -> int:
    """C(N) = floor(N/2) - φ(N)/2.
    The number of closed internal diagonal loops in a regular N-gon.
    C(N) = 0 iff N is prime (Prime Ground State Theorem)."""
    if n < 3: return 0
    return (n // 2) - (phi(n) // 2)

def totient_defect(a: int, b: int) -> int:
    """ΔC(A,B) — the binding energy of the reaction A + B = C.
    Governs whether the reaction is exothermic, endothermic, or iso-resonant."""
    return (1 if (a % 2 == 1 and b % 2 == 1) else 0) + \
           (phi(a) + phi(b) - phi(a + b)) // 2

def radius(n: int) -> float:
    """R(N) = 1/(2·sin(π/N)) — the spatial radius of a unit-edge N-gon.
    The geometric equivalent of the logarithm."""
    if n < 3: return 1.0
    return 1.0 / (2.0 * math.sin(math.pi / n))

def tension(n: int) -> float:
    """Geometric tension: deviation from circularity.
    Approaches 0 as N → ∞ (the polygon relaxes into a circle)."""
    if n < 3: return 0.0
    area = (n / 4.0) * (1.0 / math.tan(math.pi / n))
    circle_area = (n ** 2) / (4.0 * math.pi)
    return 1.0 - (area / circle_area)

def sigma_k(n: int, k: int = 1) -> int:
    """Sum of k-th powers of divisors."""
    result = 1
    for p, e in factorize(n).items():
        result *= (p ** (k * (e + 1)) - 1) // (p ** k - 1)
    return result

def carmichael(n: int) -> int:
    """Carmichael function λ(n): smallest m such that a^m ≡ 1 (mod n)
    for all coprime a."""
    if n <= 2: return 1
    if n == 4: return 2
    def pl(p, k):
        if p == 2 and k >= 3: return 2 ** (k - 2)
        return (p - 1) * p ** (k - 1)
    f = factorize(n)
    ls = [pl(p, k) for p, k in f.items()]
    r = ls[0] if ls else 1
    for l in ls[1:]: r = r * l // math.gcd(r, l)
    return r

def mobius(n: int) -> int:
    """Möbius function μ(n): -1 if n is squarefree with odd number of
    prime factors, +1 if even, 0 if not squarefree."""
    if n == 1: return 1
    f = factorize(n)
    for e in f.values():
        if e > 1: return 0
    return (-1) ** len(f)

def dedekind_psi(n: int) -> int:
    """Dedekind psi function ψ(n) = n · ∏(1 + 1/p) for p|n."""
    r = n
    for p in factorize(n): r = r * (p + 1) // p
    return r

def jordan_totient(n: int, k: int = 1) -> int:
    """Jordan's totient J_k(n): count of k-tuples with gcd 1 mod n."""
    r = n ** k
    for p in factorize(n): r *= (1 - Fraction(1, p ** k))
    return int(r)

def liouville(n: int) -> int:
    """Liouville function λ(n) = (-1)^Ω(n)."""
    return (-1) ** sum(factorize(n).values())

def radius_of_gyration(n: int) -> float:
    """True coordinate-free Cayley-Menger radius of gyration.
    R_gyr² = (1/2N²) · Σ d_ij² — computed from pairwise distances only."""
    if n < 3: return 0.0
    def chord(n, k):
        return math.sin(k * math.pi / n) / math.sin(math.pi / n)
    total = sum(n * chord(n, k)**2 for k in range(1, n))
    return math.sqrt(total / (2 * n * n))

# ==============================================================================
# REGIME CLASSIFICATION
# ==============================================================================

class Regime(Enum):
    """The three thermodynamic regimes of a reaction."""
    EXOTHERMIC = "exothermic"    # ΔC < 0: energy released
    ENDOTHERMIC = "endothermic"  # ΔC > 0: energy absorbed
    ISO_RESONANT = "iso_resonant"  # ΔC = 0: pure transfer

def classify_regime(dc: int) -> Regime:
    if dc < 0: return Regime.EXOTHERMIC
    if dc > 0: return Regime.ENDOTHERMIC
    return Regime.ISO_RESONANT

class ZoneType(Enum):
    """Classification of integers by their sub-cycle depth."""
    GROUND = "ground"    # Primes: C=0, no internal structure
    SHALLOW = "shallow"  # Light composites: C=1-4
    MEDIUM = "medium"    # Medium composites: C=5-15
    DEEP = "deep"        # Heavy composites: C=16+

def zone_type(n: int) -> ZoneType:
    if is_prime(n): return ZoneType.GROUND
    c = sub_cycles(n)
    if c <= 4: return ZoneType.SHALLOW
    if c <= 15: return ZoneType.MEDIUM
    return ZoneType.DEEP

# ==============================================================================
# DATA OBJECT — an integer as a physical object
# ==============================================================================

@dataclass
class DataObject:
    """
    A DataObject is an integer experienced as a physical object.
    
    It has:
      MASS (topological mass): M(N) = C(N) = floor(N/2) - φ(N)/2
      RADIUS: R(N) = 1/(2·sin(π/N))
      TENSION: T(N) = 1 - Area_polygon / Area_circle
      ZONE: classification by sub-cycle depth
      CHARGE: parity (even/odd)
      
    And measurable properties:
      PRIMES are ground states (M=0, no internal structure)
      COMPOSITES are excited states (M>0, internal sub-cycles)
      The denser the factorization, the heavier the object
    """
    n: int
    
    # ── Identity ──
    @property
    def value(self) -> int:
        return self.n
    
    # ── Mass ──
    @property
    def mass(self) -> int:
        """Topological mass M(N) = C(N). Primes have zero mass."""
        return sub_cycles(self.n)
    
    @property
    def mass_density(self) -> float:
        """ρ(N) = M(N)/N. Approaches (1-6/π²)/2 ≈ 0.196 for large N."""
        return self.mass / self.n if self.n > 0 else 0
    
    # ── Spatial Properties ──
    @property
    def radius(self) -> float:
        """R(N) — the spatial radius of the N-gon."""
        return radius(self.n)
    
    @property
    def tension(self) -> float:
        """T(N) — deviation from circularity."""
        return tension(self.n)
    
    @property
    def gyration(self) -> float:
        """R_gyr — coordinate-free radius of gyration."""
        return radius_of_gyration(self.n)
    
    # ── Classification ──
    @property
    def zone(self) -> ZoneType:
        return zone_type(self.n)
    
    @property
    def charge(self) -> int:
        """Parity: 0 (even) or 1 (odd)."""
        return self.n % 2
    
    @property
    def is_ground_state(self) -> bool:
        """True iff N is prime (C=0)."""
        return is_prime(self.n)
    
    @property
    def factors(self) -> Dict[int, int]:
        return factorize(self.n)
    
    @property
    def omega_total(self) -> int:
        """Ω(n): total prime factors with multiplicity."""
        return sum(self.factors.values())
    
    @property
    def omega_distinct(self) -> int:
        """ω(n): distinct prime factors."""
        return len(self.factors)
    
    @property
    def totient(self) -> int:
        return phi(self.n)
    
    @property
    def totient_ratio(self) -> float:
        """φ(n)/n = ∏(1-1/p). Measures 'coprime density'."""
        return phi(self.n) / self.n if self.n > 0 else 0
    
    # ── Higher-order properties ──
    @property
    def sigma(self) -> int:
        """σ(n): sum of divisors."""
        return sigma_k(self.n, 1)
    
    @property
    def is_abundant(self) -> bool:
        return self.sigma > 2 * self.n
    
    @property
    def is_perfect(self) -> bool:
        return self.sigma == 2 * self.n
    
    @property
    def is_deficient(self) -> bool:
        return self.sigma < 2 * self.n
    
    # ── Display ──
    def __repr__(self):
        f_str = "×".join(f"{p}^{e}" if e > 1 else str(p) for p, e in self.factors.items())
        return (f"DataObject({self.n}, zone={self.zone.value}, "
                f"M={self.mass}, R={self.radius:.3f}, "
                f"factors={f_str})")
    
    def describe(self) -> str:
        """Human-readable physical description."""
        f_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in self.factors.items())
        lines = [
            f"DataObject: {self.n}",
            f"  Zone: {self.zone.value} (C={self.mass})",
            f"  Factors: {f_str}" if f_str else "  Factors: prime (none)",
            f"  Mass: {self.mass} (topological mass density {self.mass_density:.4f})",
            f"  Radius: {self.radius:.4f}",
            f"  Tension: {self.tension:.6f}",
            f"  Charge: {'odd' if self.charge else 'even'}",
            f"  State: {'GROUND (prime)' if self.is_ground_state else 'EXCITED (composite)'}",
            f"  φ(n)/n: {self.totient_ratio:.4f}",
            f"  Abundance: {'abundant' if self.is_abundant else 'perfect' if self.is_perfect else 'deficient'}",
        ]
        return "\n".join(lines)

# ==============================================================================
# DATA REACTION — the interaction between two objects
# ==============================================================================

@dataclass
class DataReaction:
    """
    A DataReaction is the interaction between two DataObjects.
    
    Governed by the Totient Defect Equation:
      ΔC = OddPair(A,B) + (φ(A) + φ(B) − φ(A+B)) / 2
    
    The reaction has:
      REGIME: exothermic, endothermic, or iso-resonant
      ENERGY: the magnitude of the defect |ΔC|
      PRODUCTS: the combined object A+B
    """
    a: DataObject
    b: DataObject
    
    @property
    def product(self) -> DataObject:
        """The product of the reaction: A + B."""
        return DataObject(self.a.n + self.b.n)
    
    @property
    def defect(self) -> int:
        """ΔC — the Totient Defect."""
        return totient_defect(self.a.n, self.b.n)
    
    @property
    def regime(self) -> Regime:
        return classify_regime(self.defect)
    
    @property
    def energy(self) -> int:
        """|ΔC| — the magnitude of the energy exchange."""
        return abs(self.defect)
    
    @property
    def regime_description(self) -> str:
        if self.regime == Regime.EXOTHERMIC:
            return "Internal loops dissolved → energy released"
        elif self.regime == Regime.ENDOTHERMIC:
            return "New loops bound → energy absorbed"
        else:
            return "Sub-cycles perfectly conserved → pure transfer"
    
    def describe(self) -> str:
        dc = self.defect
        regime = self.regime
        return (
            f"Reaction: {self.a.n} + {self.b.n} = {self.product.n}\n"
            f"  Regime: {regime.value.upper()} (ΔC = {dc:+d})\n"
            f"  Energy: {self.energy}\n"
            f"  {self.regime_description}\n"
            f"  Mass: {self.a.mass} + {self.b.mass} → {self.product.mass} "
            f"(change: {self.product.mass - self.a.mass - self.b.mass:+d})"
        )

# ==============================================================================
# DATA FIELD — a collection of objects that evolve
# ==============================================================================

class DataField:
    """
    A DataField is a collection of DataObjects that interact through reactions.
    
    The field evolves according to the Totient Defect Equation:
      - Objects with energy activate and send signals to neighbors
      - EXOTHERMIC reactions release energy to neighbors
      - ENDOTHERMIC reactions absorb energy from neighbors
      - ISO-RESONANT reactions conserve energy perfectly
    
    Natural state: energy flows from composites to primes (ground states).
    """
    
    def __init__(self, N_range: Tuple[int, int] = (3, 200)):
        self.lo, self.hi = N_range
        self.objects = {n: DataObject(n) for n in range(self.lo, self.hi + 1)}
        self.tick = 0
        self.energy = {n: 0.0 for n in self.objects}
        self.history = []
    
    def __len__(self):
        return len(self.objects)
    
    def __getitem__(self, n):
        return self.objects[n]
    
    def activate(self, n: int, amount: float = 1.0):
        """Inject energy into an object."""
        if n in self.energy:
            self.energy[n] += amount
    
    def react(self, a: int, b: int) -> DataReaction:
        """Perform a reaction between two objects."""
        return DataReaction(self.objects[a], self.objects[b])
    
    def step(self) -> List[Dict]:
        """One evolution step. Returns list of reactions that occurred."""
        self.tick += 1
        reactions = []
        
        # Collect transfers
        transfers = []
        for n, obj in self.objects.items():
            if self.energy[n] < 0.01:
                continue
            
            # Find neighbors
            neighbors = [m for m in self.objects 
                        if m != n and abs(m - n) <= 3]
            
            for m in neighbors:
                dc = totient_defect(n, m)
                regime = classify_regime(dc)
                
                if regime == Regime.EXOTHERMIC:
                    amount = min(abs(dc) * 0.05, self.energy[n] * 0.2)
                    transfers.append((n, m, amount, regime))
                elif regime == Regime.ENDOTHERMIC:
                    amount = min(abs(dc) * 0.05, 0.2)
                    transfers.append((m, n, amount, regime))
                # ISO_RESONANT: no transfer
        
        # Apply transfers (conservation)
        for source, target, amount, regime in transfers:
            if amount > 0.001:
                self.energy[source] -= amount
                self.energy[target] += amount
                reactions.append({
                    "tick": self.tick,
                    "source": source,
                    "target": target,
                    "amount": amount,
                    "regime": regime.value,
                })
        
        # Decay
        for n in self.energy:
            self.energy[n] *= 0.95
        
        self.history.append({
            "tick": self.tick,
            "total_energy": sum(self.energy.values()),
            "active": sum(1 for e in self.energy.values() if e > 0.01),
            "n_reactions": len(reactions),
        })
        
        return reactions
    
    def query(self, n: int) -> Dict[str, Any]:
        """Query an object's state."""
        obj = self.objects[n]
        return {
            "n": n,
            "zone": obj.zone.value,
            "mass": obj.mass,
            "energy": self.energy[n],
            "is_ground": obj.is_ground_state,
            "factors": obj.factors,
        }

# ==============================================================================
# META-CHECK — spatial bit arrangement
# ==============================================================================

def geo_class(n: int) -> Tuple[int, int, int, int]:
    """Geometric class: the Meta-Check header (10 bits)."""
    f = factorize(n)
    return (
        min(sub_cycles(n), 15),
        min(sum(f.values()), 7),
        min(len(f), 3),
        int(is_prime(n)),
    )

def arrangement_type(n: int) -> str:
    """Grid arrangement type based on geometric class."""
    gc = geo_class(n)
    if gc[3] or gc[0] == 0: return "LINEAR"
    if gc[2] == 1: return "SQUARE"
    if gc[2] == 2: return "DUAL"
    return "WIDE"

# ==============================================================================
# CONSTANTS — the "physical constants" of data space
# ==============================================================================

class DataConstants:
    """Physical constants of the Literal Data Physics framework."""
    
    # Asymptotic topological mass density (Dirichlet)
    RHO_INF = (1 - 6 / math.pi**2) / 2  # ≈ 0.196036
    
    # Observer Constant (from Catenary-Hodge)
    Y = 0.264675430405  # π/(π²+2)
    
    # Entropic Wobble
    WOBBLE = 0.817580227176  # (π·φ·e) mod 1
    
    # D-Sink Leakage
    L = WOBBLE / 13  # ≈ 0.06289
    
    # Existence Unit
    U_E = 13824  # 24³
    
    # Topological third: φ(U_E)/U_E = 1/3
    TOP_THIRD = 1 / 3
    
    # Steiner ISO-RESONANCE: 8+8=16 is perfectly conserved
    STEINER_ISO = True  # M(16) = M(8) + M(8) = 2+2 = 4

# ==============================================================================
# DEMONSTRATION
# ==============================================================================

def demo():
    """Demonstrate the Literal Data Physics framework."""
    print("=" * 70)
    print(" LITERAL DATA PHYSICS — Demonstration")
    print("=" * 70)
    
    # ── DataObjects ──
    print("\n[1] DATA OBJECTS — integers as physical objects")
    print("─" * 50)
    for n in [7, 12, 13, 24, 30, 60, 137, 169]:
        obj = DataObject(n)
        print(f"\n{obj.describe()}")
    
    # ── DataReactions ──
    print("\n\n[2] DATA REACTIONS — governed by Totient Defect")
    print("─" * 50)
    pairs = [(5, 7), (12, 3), (9, 6), (8, 8), (13, 84), (4, 4)]
    for a, b in pairs:
        reaction = DataReaction(DataObject(a), DataObject(b))
        print(f"\n{reaction.describe()}")
    
    # ── Natural Flow ──
    print("\n\n[3] NATURAL FLOW — energy flows to primes")
    print("─" * 50)
    field = DataField((3, 100))
    field.activate(60, 5.0)  # Activate a deep composite
    
    print(f"  Activated zone 60 (deep composite, M={DataObject(60).mass})")
    for step in range(5):
        reactions = field.step()
        state = field.history[-1]
        print(f"  tick {state['tick']:>2}: "
              f"active={state['active']:>3}, "
              f"energy={state['total_energy']:.3f}, "
              f"reactions={state['n_reactions']}")
    
    # Show where energy ended up
    print(f"\n  Energy distribution after 5 ticks:")
    by_zone = defaultdict(float)
    for n, e in field.energy.items():
        if e > 0.01:
            by_zone[DataObject(n).zone.value] += e
    for z, e in sorted(by_zone.items(), key=lambda x: -x[1]):
        print(f"    {z:8s}: {e:.3f}")
    
    # ── Constants ──
    print("\n\n[4] PHYSICAL CONSTANTS OF DATA SPACE")
    print("─" * 50)
    c = DataConstants
    print(f"  ρ_∞ (topological mass density): {c.RHO_INF:.6f}")
    print(f"  Y   (Observer Constant):        {c.Y:.12f}")
    print(f"  w   (Entropic Wobble):          {c.WOBBLE:.12f}")
    print(f"  L   (D-Sink Leakage):           {c.L:.12f}")
    print(f"  U_e (Existence Unit):           {c.U_E}")
    print(f"  Topological Third:              {c.TOP_THIRD:.6f}")
    print(f"  Steiner ISO-RESONANCE:          {c.STEINER_ISO}")
    
    # ── Summary ──
    print("\n" + "=" * 70)
    print(" LITERAL DATA PHYSICS — Summary")
    print("=" * 70)
    print("""
  Integers ARE physical objects:
    - Primes are ground states (M=0, no internal structure)
    - Composites are excited states (M>0, internal sub-cycles)
    - The denser the factorization, the heavier the object

  Arithmetic IS physics:
    - Addition is a reaction governed by the Totient Defect Equation
    - EXOTHERMIC: complexity dissolves, energy released
    - ENDOTHERMIC: complexity builds, energy absorbed
    - ISO-RESONANT: pure transfer, energy conserved

  The natural flow:
    Energy flows from composites to primes (always).
    Primes are the ground states — the drains of the network.
    Composites are the pipes — they process and pass energy.

  The physical constants:
    ρ_∞ ≈ 0.196 — the fraction of an integer that is "structure"
    Y ≈ 0.265 — the Observer Constant (from spatial geometry)
    The system is bounded, decaying, convergent.
    No emergent behavior. Just number-theoretic physics.
""")

if __name__ == "__main__":
    demo()
