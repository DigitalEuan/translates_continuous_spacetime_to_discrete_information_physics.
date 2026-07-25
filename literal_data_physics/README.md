# Literal Data Physics (LDP)

**A framework where integers ARE physical objects and arithmetic IS physics.**

*E R A Craig & Collaborative AI Research, July 2026*

---

## What Is This?

Literal Data Physics treats integers as physical objects with measurable properties — mass, radius, charge, zone — and treats arithmetic operations as physical reactions governed by the **Totient Defect Equation**:

```
ΔC(A,B) = OddPair(A,B) + (φ(A) + φ(B) − φ(A+B)) / 2
```

This single equation governs all pairwise interactions in data space:
- **ΔC < 0**: EXOTHERMIC — energy released, complexity dissolves
- **ΔC > 0**: ENDOTHERMIC — energy absorbed, complexity builds  
- **ΔC = 0**: ISO-RESONANT — pure transfer, energy conserved

The framework operates across **four form degrees** (k=0,1,2,3), each revealing structure invisible to the levels below.

---

## Quick Start

```python
from ldp import DataObject, react, face, cell, batch_compress, constants

# Create a data-physical object
obj = DataObject(60)
print(obj.mass)      # 22 (topological mass — internal sub-cycles)
print(obj.zone)      # "deep" (heavily composite)
print(obj.is_prime)  # False
print(obj.factors)   # {2: 2, 3: 1, 5: 1}

# React two objects
result = react(5, 7)
print(result['regime'])   # "endothermic" (two primes binding)
print(result['defect'])   # +4

# Three-body interaction (invisible at pairwise level)
f = face(60, 84, 105)
print(f['three_body'])    # True
print(f['excess'])        # -3.67 (pairwise over-predicts)

# Batch compress integers
compressed = batch_compress([7, 13, 42, 100, 169])
print(compressed['savings_pct'])  # 37.8%

# Physical constants
print(constants.RHO_INF)  # 0.196036 (topological mass density)
print(constants.Y)        # 0.264675 (Observer Constant)
```

---

## The Four Form Degrees

The Catenary Hodge framework maps interactions across four levels:

### k=0 — Vertex (Single Integer)
```python
obj = DataObject(60)
obj.mass       # 22 — topological mass (internal sub-cycles)
obj.radius     # 9.554 — spatial radius of the 60-gon
obj.tension    # 0.000914 — deviation from circularity
obj.zone       # "deep" — ground/shallow/medium/deep
obj.charge     # 0 — parity (even=0, odd=1)
obj.factors    # {2:2, 3:1, 5:1} — prime factorization
```

**Primes are ground states** (mass=0, no internal structure). Composites are excited states — the denser the factorization, the heavier the object.

### k=1 — Edge (Pairwise Reaction)
```python
r = react(5, 7)    # Two primes binding
# {'regime': 'endothermic', 'defect': +4, 'energy': 4}

r = react(12, 3)   # Composite dissolving
# {'regime': 'exothermic', 'defect': -1, 'energy': 1}

r = react(8, 8)    # Perfect conservation
# {'regime': 'iso_resonant', 'defect': 0, 'energy': 0}
```

The Totient Defect ΔC is the **law of motion** — every pairwise interaction follows it exactly.

### k=2 — Face (Three-Body Interaction)
```python
f = face(60, 84, 105)
# {'three_body': True, 'excess': -3.67, 'redundancy': 3.67}
```

The Face Defect measures how the triple GCD differs from pairwise GCDs. **21% of triples have three-body forces** — invisible at k=1.

Three-body rates by type:
- All composites: **36%** have three-body force
- Mixed (1 prime): 16%
- All primes: **0%** (no shared factors → no three-body)

### k=3 — Cell (Four-Body Interaction)
```python
c = cell(60, 84, 105, 210)
# {'four_body': True, 'excess': -2.25}
```

The Cell Defect measures quadruple GCD structure. **3% of quads have four-body forces** — rare but real.

---

## Data Savings

### Batch Compression
Group integers by geometric class (10-bit header). Each group shares one header; members need only their index.

```python
import random
batch = random.sample(range(3, 1001), 100)
result = batch_compress(batch)
# bits_per_int: 5.65 (vs 9.96 raw)
# savings_pct: 43.3%
```

| Batch Size | Bits/Int | Savings |
|-----------|----------|---------|
| 10 | 6.20 | 37.8% |
| 50 | 5.48 | 45.0% |
| 100 | 5.65 | 43.3% |
| 500 | 6.76 | 32.2% |

### Meta-Check Header
The 10-bit geometric header encodes:
- Sub-cycle depth C(N): 4 bits
- Total prime factors Ω(n): 3 bits
- Distinct primes ω(n): 2 bits
- Primality flag: 1 bit

From the header alone, you can query:
- Is it prime?
- How composite is it?
- What's its factorization pattern?
- What grid shape does it occupy?

---

## Key Findings

### 1. Primes Are Ground States
```
C(N) = 0  ⟺  N is prime
```
Primes have zero topological mass — no internal diagonal sub-cycles. They are the simplest objects in data space, like fundamental particles.

### 2. Energy Flows to Primes
When you activate a composite, energy propagates through the network and **terminates at primes**. Primes are energy sinks — they absorb and hold energy. Composites are pipes — they process and pass energy.

### 3. Conservation Laws Hold Exactly
In ISO-RESONANT reactions (ΔC=0), mass is **exactly conserved**: M(A) + M(B) = M(A+B). Verified for 368/368 pairs (100%).

### 4. The "Iron-56" Is N=169
The most tightly bound composite per unit mass is **169 = 13²** (binding/mass = 8.167). The D-Sink dimension 13 produces the most stable composite structure.

### 5. Three-Body Forces Exist at k=2
At k=1 (pairwise): zero three-body force in all tests.
At k=2 (face): **21% of triples** have non-zero three-body force.

The Catenary Hodge dimension projection showed us: we were looking at the wrong level.

### 6. The Totient Defect Is Purely Pairwise
At k=1, there is no three-body term: ΔC(A,B,C) = ΔC(A,B) + ΔC(A+B,C) always. Higher-order interactions live at higher form degrees.

### 7. Physical Constants Are Transcendental
```
ρ_∞ = (1 - 6/π²)/2 ≈ 0.196036  — topological mass density
Y = π/(π²+2) ≈ 0.264675         — Observer Constant
φ(24)/24 = φ(13824)/13824 = 1/3 — topological third
Y × (π + 2/π) = 1               — observer reciprocity
```

---

## The Dimension Projection Map

```
k=0 (Vertex)  ────  Single integers
│                    Mass, radius, charge, zone
│                    7.80 bits of information
│
k=1 (Edge)    ────  Pairwise interactions
│                    Totient Defect ΔC(A,B)
│                    5.98 bits (adds +0.75 over k=0)
│
k=2 (Face)    ────  Three-body interactions
│                    Face Defect via triple GCD
│                    1.75 bits (adds +0.50 over k=1)
│
k=3 (Cell)    ────  Four-body interactions
                    Cell Defect via quadruple GCD
                    0.52 bits (adds +0.19 over k=2)
```

Each level reveals structure invisible to the levels below. The full picture requires all four.

---

## What This Is Not

- **Not compression for single integers.** The geometric encoding uses more bits than raw. The value is structural, not compressional.
- **Not a replacement for factorization.** Computing sub-cycles requires φ(n), which requires factorization. The framework describes the *structure* of factorization, not a shortcut to it.
- **Not neural-network-like.** No learning, no weights, no emergent behavior. The reactions are deterministic and bounded. The system converges to low-energy equilibrium.

---

## What This Is

- **A physics of data.** Integers have measurable physical properties. Arithmetic operations are physical reactions. Conservation laws hold.
- **A dimension projection framework.** Four form degrees (k=0,1,2,3) each reveal different structure. The Catenary Hodge study maps these projections.
- **A compression tool for batches.** 15-45% savings via shared geometric headers.
- **A structural oracle.** From a 10-bit header, you can query primality, factorization depth, and structural complexity without decoding.

---

## Files

| File | Description |
|------|-------------|
| `ldp.py` | Entry module — lightweight, importable, self-contained |
| `literal_data_physics_complete.py` | Full framework with tests and demonstration |
| `literal_data_physics.py` | Core library (clean, documented) |
| `literal_data_physics_alignment.py` | Alignment verification (4 PASS) |
| `literal_data_physics_probes.py` | Misalignment probes |
| `full_dimension_picture.py` | k=0,1,2,3 dimension analysis |
| `zone_engine.py` | Zone reactive computation |
| `zone_natural_state.py` | Natural state investigation |
| `meta_check_system.py` | Spatial bit arrangement |
| `spatial_totient_*.py` | Supporting studies |
| `catenary_hodge_updated_report.md` | Catenary-Hodge integration |

---

## Dependencies

**None.** Python 3.8+ stdlib only. No numpy, scipy, or external packages.

---

## Running

```bash
# Entry module (quick test + demo)
python3 ldp.py

# Full framework (tests + demonstration)
python3 literal_data_physics_complete.py

# Import in your code
from ldp import DataObject, react, face, cell, batch_compress, constants
```

---

## References

- Craig, E. R. A. (2026). *Catenary-Hodge & Spatial Arithmetic*. GitHub.
- Craig, E. R. A. (2026). *UBP Core Studio v4.0*. GitHub.
- Conway, J. H. & Sloane, N. J. A. (1999). *Sphere Packings, Lattices and Groups*. Springer.
- Hodge, W. V. D. (1950). "The topological invariants of algebraic varieties." *Proc. ICM*.
- Euler, L. (1763) & Dirichlet, P. G. L. (1849). Totient function and asymptotic density.

---

*Literal Data Physics — where integers are objects and arithmetic is physics.*
