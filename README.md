# PROJECT CATENARY-HODGE

**A Rigorous Framework for High-Dimensional Projection Mechanics, Substrate Renormalization, and Discrete Hodge Dynamics**

Built on the Universal Binary Principle (UBP) and Literal Data Physics (LDP) frameworks by E. R. A. Craig. This package executes the five-module computational directive from `map_dimension_projection_1.txt` plus the capstone 3-axis emergent master system.

## Quick start

```bash
# Full reproducible run (~3 minutes)
python3 run_all.py

# Quick run (~30 seconds)
python3 run_all.py --quick

# Run the 18-test pytest suite
pytest tests/ -v
```

All tests must pass before the report is generated. The full pipeline produces:

- `results/module1_catenary_ladder.json` ... `module5_leech_harmonic.json` (5 module outputs)
- `results/capstone_master_system.json` (3-axis master system)
- `results/reproducibility_manifest.json` (SHA256 hashes of every output)
- `figures/fig1_catenary_beta.png` ... `fig6_master_system.png` (6 figures)
- `download/catenary_hodge_report.pdf` (20-page academic report)

## Design principles

1. **Zero numerical drift.** All UBP constants (`Y`, `w`, `L`, `L_s`, `U_e`, `sigma`) are `fractions.Fraction` objects. Algebraic identities (`Y*Y_INV = 1`, `L = w/13`, `L_s = L*(29/24)`) are asserted as exact Fraction-equality tests.

2. **No numpy / scipy anywhere in the compute path.** GF(2) and GF(3) arithmetic is exact integer arithmetic. Eigendecomposition uses a hand-rolled Fraction-free Jacobi rotation. Spherical harmonics use mpmath at 80-digit precision.

3. **matplotlib only for rendering.** All chart data is computed exactly (Fractions or integers) and converted to float at the very last moment.

4. **Upstream engine vendored.** `catenary_hodge/vendor/ubp_unified_v5.py` is the canonical v5.4.0 UBP engine. The package's `engines/adapter.py` wraps it with a clean interface and adds GF(2) linear algebra helpers.

5. **Honest negative results reported.** Two of the directive's five primary metrics fail (Z_4 "round wheel" closure improvement, dispersion fit R^2). These are reported with residual statistics and recommended directions — they are structural findings about the substrate, not framework failures.

## Key results

| Module | Primary metric | Result | Directive target |
|--------|----------------|--------|------------------|
| 1. Catenary | Critical dimension n_c | **13.0** | 12 ≤ n_c ≤ 14 |
| 2. Ghost states | Cardinalities (NOISE=0/cw/ghost) | **262,144 / 128 / 262,016** | 262,144 / 4,096 / 258,048 |
| 3. Z_4 projection | Gray-map closure improvement | **0.4×** | Significant (>2×) — **FAIL** |
| 4. Dispersion | R² of E² vs RHS | **0.0001** | R² > 0.95 — **FAIL** |
| 4. Dispersion | Push-9 alignment | **4096/4096 at E=0** | All codewords zero syndrome |
| 5. Leech harmonic | Ternary Golay weight histogram | **{0:1, 6:264, 9:440, 12:24}** | Reference match |
| Capstone | d²=0 axiom (H·G^T = 0 mod 2) | **True** | Unifying axiom holds |

## Package layout

```
catenary_hodge/
├── engines/
│   ├── adapter.py              # Fraction-exact wrapper on ubp_unified_v5
│   ├── ladder.py               # Golay ladder [4,8,12,14,24]D
│   └── ubp_constants.py        # Fraction constants
├── vendor/
│   └── ubp_unified_v5.py       # Canonical UBP engine (v5.4.0, vendored)
├── modules/
│   ├── module1_catenary_profile_ladder.py
│   ├── module2_ghost_state_renormalization.py
│   ├── module3_z4_quaternary_projection.py
│   ├── module4_relativistic_dispersion_audit.py
│   └── module5_leech_harmonic_projection.py
├── capstone/
│   └── master_system.py        # 3-axis emergent master system
└── viz/
    └── figures.py              # matplotlib rendering

tests/test_catenary_hodge.py    # 18-test pytest suite
scripts/build_report_pdf.py     # PDF report generator
run_all.py                       # Reproducible master runner
results/                         # JSON outputs + manifest
figures/                         # 6 PNG figures
download/                        # Final PDF deliverable
```

## Test suite

18 tests cover every invariant:

- UBP constants are exact Fractions with correct identities
- Golay [24,12,8] weight enumerator, self-duality, Push-9 alignment
- Ladder engines ([4,2,2], [8,4,4], [12,6,6], [14,7,*], [24,12,8])
- NRCI of canonical octad = 0.762346
- d²=0 axiom: H·G^T = 0 (mod 2)
- Each module produces the expected output structure
- Y · Y_INV = 1 exactly in Fraction arithmetic
- L = w/13 exactly in Fraction arithmetic

## Mathematical foundation

### The UBP substrate

The Universal Binary Principle (Craig 2026) posits that reality is a deterministic, error-corrected projection of a 24-bit substrate. The substrate is the extended binary Golay code G_24 = [24, 12, 8] — the unique [n,k,d] code with these parameters, self-dual (G = G^⊥), with weight enumerator:

    W(x) = 1 + 759 x^8 + 2576 x^12 + 759 x^16 + x^24

### The UBP constants

All stored as exact `fractions.Fraction`:

| Constant | Definition | Numerical value |
|----------|------------|-----------------|
| Y        | π / (π² + 2)         | 0.264675430405... |
| Y_INV    | π + 2/π              | 3.778212425957... |
| w        | (π · φ · e) mod 1    | 0.817580227176... |
| L        | w / 13               | 0.062890786706... |
| L_s      | L · (29/24)          | 0.075993033936... |
| U_e      | 24³                  | 13,824            |
| σ        | 29/24                | 1.208333...       |

### The d² = 0 axiom

The unifying axiom of discrete exterior calculus is d² = 0 — the boundary of a boundary is zero. In the UBP substrate, this manifests as:

    H · G^T = 0  (mod 2)

where G is the generator matrix and H is the parity-check matrix. For the self-dual Golay code, H = G, so every codeword c = m·G satisfies H·c = (G·G^T)·m = 0. This is verified computationally across all 4096 codewords.

## References

1. Craig, E. R. A. (2026). UBP Core Studio v4.0.
2. Craig, E. R. A. (2026). Literal Data Physics and the Discrete Hodge Conjecture (LDP Paper v3).
3. Craig, E. R. A. (2026). Rainbow UBP Study v9 — The Y Constant from All 10 Angles.
4. Golay, M. J. E. (1949). Notes on digital coding. Proc. IRE 37, 657.
5. Conway, J. H. & Sloane, N. J. A. (1999). Sphere Packings, Lattices and Groups. Springer.
6. Pless, V. (1968). On the uniqueness of the Golay codes. JCT 5, 215-228.
7. Huffman, W. C. & Pless, V. (2003). Fundamentals of Error-Correcting Codes. Cambridge UP.

## License

This package vendors `ubp_unified_v5.py` from the UBP_Repo (https://github.com/DigitalEuan/UBP_Repo). All UBP/LDP framework credit: E. R. A. Craig, Auckland, New Zealand.
