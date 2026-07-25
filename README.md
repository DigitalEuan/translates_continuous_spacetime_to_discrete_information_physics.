# Project Catenary-Hodge & Spatial Arithmetic
### A Rigorous Framework for Discrete Information Geometry, Substrate Renormalization, and the Discrete Hodge Conjecture

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-69%20passing-brightgreen.svg)]()
[![ArXiv](https://img.shields.io/badge/Report-PDF%20v1.1.0-red.svg)](download/catenary_hodge_report.pdf)

**Project Catenary-Hodge** asks a single, fundamental question: *Can the geometric properties of a discrete error-correcting code fully characterize its algebraic structure?* 

Building on the **Universal Binary Principle (UBP)** and **Literal Data Physics (LDP)**, this repository operationalizes the discrete analog of the Hodge Conjecture. By mapping the extended binary Golay code $G_{24}$ and the Leech lattice $\Lambda_{24}$ to coordinate-free geometric manifolds, we bridge continuous differential geometry, algebraic coding theory, and geometric number theory.

---

## 🌉 The Conceptual Bridge (UBP $\rightarrow$ Standard Mathematics)

This project translates proprietary UBP/LDP concepts into standard, peer-reviewed academic frameworks. 

| UBP / LDP Concept | Standard Academic Translation | Mathematical Context |
| :--- | :--- | :--- |
| **UBP / LDP Substrate** | Discrete Information Geometry | The overarching framework mapping information to geometry. |
| **Golay/Leech Substrate** | $G_{24}$ Code & Leech Lattice $\Lambda_{24}$ | The discrete $[24,12,8]$ and continuous 24D geometric models. |
| **Ghost States** | Geometric Kernel / Discrete Hodge Gap | Vectors satisfying geometric conditions (NOISE=0) but failing algebraic membership ($v \notin G_{24}$). |
| **Spatial Arithmetic** | Discrete Distance Geometry | Computing via $R(N) = 1/(2\sin(\pi/N))$ and spatial relationships. |
| **Totient Kinetics** | Topological Spectral Analysis | Using Euler's Totient $\phi(N)$ to map internal diagonal sub-cycles $C(N)$. |
| **Coordinate-Free Hodge** | Cayley-Menger Distance Geometry | Computing metrics using *only* pairwise distances, no global frame. |

---

## 📐 Core Theorems & Embedded Mathematics

The mathematical foundations of this framework are self-contained. All algebraic computation uses Python's `fractions.Fraction` to guarantee **zero numerical drift**.

### 1. The Natural Primitive (Spatial Arithmetic)
The spatial footprint (circumradius) of an integer $N$ encoded as a unit-edge regular $N$-gon is governed by the exact radial transformation:
$$R(N) = \frac{1}{2 \sin(\pi / N)}$$
This primitive acts as the geometric equivalent of the logarithmic/exponential operator, from which all spatial arithmetic operations (addition via topology, multiplication via distance, division via radius ratio) are derived.

### 2. The Totient Sub-Cycle Theorem
The total number of closed internal diagonal sub-cycles $C(N)$ within a regular $N$-gon is given **exactly** by:
$$C(N) = \left\lfloor \frac{N}{2} \right\rfloor - \frac{\phi(N)}{2}$$
*Verified 100% against direct graph traversal for $N \in [3, 1000]$.*

### 3. The Prime Ground State Theorem
An integer $N \ge 3$ is prime **if and only if** its spatial footprint is topologically "ground state" (contains zero internal diagonal sub-cycles):
$$N \in \mathbb{P} \iff C(N) = 0$$

### 4. Topological Mass Density
The asymptotic density of topological mass $\rho(N) := C(N)/N$ converges to a fundamental constant related to Dirichlet's theorem on the average order of Euler's Totient:
$$\rho_\infty = \frac{1 - \frac{6}{\pi^2}}{2} \approx 0.196036$$

### 5. The Unifying Axiom ($d^2 = 0$)
The unifying axiom of discrete exterior calculus is $d^2 = 0$ (the boundary of a boundary is zero). In the UBP substrate, this manifests as the self-duality of the Golay code:
$$H \cdot G^T = 0 \pmod 2$$
This identity connects UBP's linear algebra directly to discrete exterior calculus, proving that the 3-axis master system is emergent, not taxonomic.

---

## 🧭 The 3-Axis Emergent Master System

The capstone of this framework maps all systems—vector operators, projection styles, higher-dimensional polytopes, and discrete codes—onto a single unified structure.

| Axis | Dimension | Mathematical Equivalent | UBP Application |
| :--- | :--- | :--- | :--- |
| **Axis 1: Form Degree** | $k \in \{0,1,2,3\}$ | de Rham Chain ($\nabla, \nabla\times, \nabla\cdot, \iiint$) | Code Weight, Syndrome, AND Mass Defect, MOG Octad Density |
| **Axis 2: Projection** | Kernel Type | Orthographic, Stereographic, Schlegel, Petrie | Hamming weights, NRCI fields, MOG adjacency, Y-harmonics |
| **Axis 3: Substrate** | $D \in \{4,8,12,14,24\}$ | Substrate Hierarchy & Phase Transitions | Golay Ladder, AND-closure collapse, Critical dimension $n_c=13$ |

---

## ⚙️ Engine Design Principles

1. **Zero Numerical Drift:** All UBP constants ($Y, w, L, L_s, U_e, \rho_\infty$) and topological mass calculations are `fractions.Fraction` objects. Transcendental inputs ($\pi, \phi, e$) are computed via `mpmath` at 80-digit precision and truncated to exact Fractions.
2. **Pure Python Core:** **No `numpy` or `scipy`** anywhere in the compute path. GF(2) and GF(3) arithmetic is exact integer arithmetic. Eigendecomposition uses a hand-rolled Fraction-free Jacobi rotation.
3. **Coordinate-Free Observation:** The Observer computes centroid distances using *only* pairwise vertex-to-vertex distances via the Blumenthal-Schoenberg identity, requiring zero global coordinate frame.
4. **Honest Science:** Structural falsifications are reported as boundary-defining discoveries, not framework failures.

---

## 🚀 Quick Start

### Full Reproducible Run (~3 minutes)
```bash
git clone https://github.com/DigitalEuan/UBP_Repo.git
cd UBP_Repo/catenary_hodge
python3 run_all.py
```

### Quick Run (~30 seconds)
```bash
python3 run_all.py --quick
```

### Run the Test Suite
```bash
pytest tests/ -v
```
*All 69 tests must pass before the report is generated.*

### Standalone Spatial Arithmetic CLI
```bash
# Run all spatial arithmetic tests
python3 spatial_arithmetic.py

# Evaluate an expression via 3D geometry
python3 spatial_arithmetic.py --eval "3+4*5"

# Build and decode a spatial scene
python3 spatial_arithmetic.py --scene 7 ADD 3

# Demonstrate natural geometric operations
python3 spatial_arithmetic.py --natural 5 3
```

---

## 📊 Key Results & Structural Falsifications

| Module | Primary Metric | Result | Status |
| :--- | :--- | :--- | :--- |
| **1. Catenary** | Critical dimension $n_c$ | 13.0 | ✅ PASS |
| **2. Ghost States** | Cardinalities (NOISE=0 / cw / ghost) | 262,144 / 128 / 262,016 | ⚠️ PARTIAL |
| **3. Z4 Projection** | Gray-map closure improvement | 0.400x (Target >2x) | ❌ **FALSIFIED** |
| **4. Dispersion** | $R^2$ of $E^2$ vs RHS | 0.0001 (Target >0.95) | ❌ **FALSIFIED** |
| **9. Duality** | Prime Ground State Theorem | Verified $N \in [3, 999]$ | ✅ PASS |
| **14. $\rho_\infty$** | Dirichlet convergence | 0.196036 (err 0.0002) | ✅ PASS |
| **Capstone** | $d^2=0$ axiom ($H \cdot G^T = 0$) | True | ✅ PASS |

> **Note on Falsifications:** The Z4 Gray map and Relativistic Dispersion hypotheses were intentionally tested and failed. These are **Structural Falsifications** that rigorously define the geometric boundaries of the substrate (e.g., proving the $E=MC^2$ analogy is strictly a near-codeword metaphor, not a global fit).

---

## 📂 Package Layout

```text
catenary_hodge/
 ├── engines/                  # Fraction-exact engine adapters
 │   ├── adapter.py            # Thin wrapper on ubp_unified_v5
 │   ├── ladder.py             # Golay ladder [4,8,12,14,24]D
 │   └── ubp_constants.py      # Exact Fraction constants
 ├── vendor/
 │   └── ubp_unified_v5.py     # Vendored upstream engine (v5.4.0)
 ├── modules/                  # The 14 computational directives
 │   ├── module1_catenary_profile_ladder.py
 │   ├── module2_ghost_state_renormalization.py
 │   ├── ...
 │   └── module14_topological_mass_density.py
 ├── capstone/
 │   └── master_system.py      # 3-axis emergent master system
 ├── viz/
 │   └── figures.py            # matplotlib rendering
 ├── tests/
 │   └── test_catenary_hodge.py # 69-test pytest suite
 ├── spatial_arithmetic.py     # Standalone 3D Spatial Arithmetic Engine
 ├── run_all.py                # Reproducible master runner
 ├── results/                  # JSON outputs + SHA256 manifest
 ├── figures/                  # 15+ PNG figures
 └── download/                 # Final PDF deliverable
```

---

## 📚 References & Academic Lineage

### Standard Academic Foundations
*   **Conway, J. H., & Sloane, N. J. A. (1999).** *Sphere Packings, Lattices and Groups*. Springer. (Golay & Leech foundations).
*   **Hodge, W. V. D. (1950).** "The topological invariants of algebraic varieties." *Proc. ICM*. (The Hodge Conjecture).
*   **Blumenthal, L. M. (1953).** *Theory and Applications of Distance Geometry*. Oxford UP. (Cayley-Menger identity).
*   **Euler, L. (1763) & Dirichlet, P. G. L. (1849).** (Totient function and asymptotic density).
*   **Hirani, A. N. (2003).** *Discrete Exterior Calculus*. PhD thesis, Caltech. ($d^2=0$ axiom).

### UBP / LDP Framework
*   **Craig, E. R. A. (2026).** *UBP Core Studio v4.0*. [[GitHub Repository](https://github.com/DigitalEuan/translates_continuous_spacetime_to_discrete_information_physics./edit/main/README.md)].
*   **Craig, E. R. A. (2026).** *Literal Data Physics and the Discrete Hodge Conjecture (LDP Paper v3)*.
*   **Craig, E. R. A. (2026).** *Spatial Arithmetic — Computing with 3D Geometry*.

---

## 📜 License & Credits

**Framework & Code:** E. R. A. Craig, Auckland, New Zealand.  
**UBP/LDP Architectural Credit:** E. R. A. Craig.  

Distributed under the MIT License. See `LICENSE` for more information.

---
*Generated: 2026-07-25 · Package v1.1.0 · "The geometry does not represent numbers; it embodies them."*
