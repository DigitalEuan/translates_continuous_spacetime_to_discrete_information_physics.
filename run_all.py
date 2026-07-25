#!/usr/bin/env python3
"""
run_all.py — Reproducible master runner for Project Catenary-Hodge.

Executes all 5 modules + capstone, generates figures, and produces a
reproducibility manifest with timestamps and Python environment info.

Usage:
    python3 run_all.py              # full run
    python3 run_all.py --quick      # quick run (smaller samples)
"""
import os
import sys
import json
import time
import platform
import hashlib
import subprocess
from pathlib import Path

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULTS_DIR = "/home/z/my-project/results"
FIGURES_DIR = "/home/z/my-project/figures"
DOWNLOAD_DIR = "/home/z/my-project/download"


def module_dir():
    return os.path.dirname(os.path.abspath(__file__))


def step(msg):
    print(f"\n{'=' * 70}\n  {msg}\n{'=' * 70}")


def run_module(module_path: str, name: str):
    """Run a module and return (elapsed_seconds, success)."""
    print(f"\n>>> Running {name} ({module_path}) ...")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "-m", module_path],
        cwd="/home/z/my-project",
        capture_output=False,
    )
    elapsed = time.time() - t0
    return elapsed, result.returncode == 0


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    quick = "--quick" in sys.argv
    print(f"PROJECT CATENARY-HODGE — Master Runner")
    print(f"Mode: {'QUICK' if quick else 'FULL'}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    manifest = {
        "project": "Project Catenary-Hodge",
        "version": "1.0.0",
        "run_mode": "quick" if quick else "full",
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "started_at": time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        "modules": {},
    }

    # Run all 14 modules + capstone
    modules = [
        ("catenary_hodge.modules.module1_catenary_profile_ladder", "Module 1: Catenary Profile Ladder"),
        ("catenary_hodge.modules.module2_ghost_state_renormalization", "Module 2: Ghost State Renormalization"),
        ("catenary_hodge.modules.module3_z4_quaternary_projection", "Module 3: Z_4 Quaternary Projection"),
        ("catenary_hodge.modules.module4_relativistic_dispersion_audit", "Module 4: Relativistic Dispersion Audit"),
        ("catenary_hodge.modules.module5_leech_harmonic_projection", "Module 5: Leech Harmonic Projection"),
        ("catenary_hodge.modules.module6_spatial_catenary", "Module 6: Spatial Catenary"),
        ("catenary_hodge.modules.module7_coordinate_free_hodge", "Module 7: Coordinate-Free Hodge"),
        ("catenary_hodge.modules.module8_spatial_y_constant", "Module 8: Spatial Y-Constant"),
        ("catenary_hodge.modules.module9_intrinsic_extrinsic_duality", "Module 9: Intrinsic-Extrinsic Duality"),
        ("catenary_hodge.modules.module10_multiplication_tensor", "Module 10: Multiplication Tensor Product"),
        ("catenary_hodge.modules.module11_topological_mass", "Module 11: Topological Mass & Asymptotic Density"),
        ("catenary_hodge.modules.module12_steiner_iso_resonance", "Module 12: Steiner ISO-RESONANCE Sweep [NEW]"),
        ("catenary_hodge.modules.module13_y_hexadecad_totient", "Module 13: Y-Hexadecad-Totient Hidden Structure [NEW]"),
        ("catenary_hodge.modules.module14_topological_mass_density_constant", "Module 14: Topological Mass Density as New UBP Constant [NEW]"),
        ("catenary_hodge.capstone.master_system", "Capstone: 3-Axis Master System"),
    ]

    for mod_path, name in modules:
        step(f"Running {name}")
        elapsed, ok = run_module(mod_path, name)
        manifest["modules"][mod_path] = {
            "name": name,
            "elapsed_seconds": round(elapsed, 2),
            "success": ok,
        }
        print(f"  → {name}: {'OK' if ok else 'FAIL'} ({elapsed:.1f}s)")

    # Generate figures
    step("Generating figures")
    t0 = time.time()
    from catenary_hodge.viz.figures import generate_all
    generate_all()
    from catenary_hodge.viz.spatial_figures import generate_spatial_figures
    generate_spatial_figures()
    from catenary_hodge.viz.totient_figures import generate_totient_figures
    generate_totient_figures()
    from catenary_hodge.viz.refine_figures import generate_refine_figures
    generate_refine_figures()
    manifest["figures_elapsed_seconds"] = round(time.time() - t0, 2)

    # Run tests (both the original and the refine_directive test suite)
    step("Running test suite")
    t0 = time.time()
    test_result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_catenary_hodge.py", "tests/test_refine_directive.py", "-v"],
        cwd="/home/z/my-project",
        capture_output=True,
        text=True,
    )
    manifest["tests_passed"] = "PASSED" in test_result.stdout and "FAILED" not in test_result.stdout
    manifest["tests_elapsed_seconds"] = round(time.time() - t0, 2)
    print(test_result.stdout[-1500:])

    # Compute result file hashes
    step("Computing reproducibility manifest")
    result_hashes = {}
    for fname in sorted(os.listdir(RESULTS_DIR)):
        fpath = os.path.join(RESULTS_DIR, fname)
        if os.path.isfile(fpath):
            result_hashes[fname] = file_sha256(fpath)
    manifest["result_files"] = result_hashes
    manifest["finished_at"] = time.strftime('%Y-%m-%d %H:%M:%S %Z')

    # Save manifest
    manifest_path = os.path.join(RESULTS_DIR, "reproducibility_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"\nManifest: {manifest_path}")
    print(f"\nDone. Total modules: {len(modules)}")
    print(f"All modules successful: {all(m['success'] for m in manifest['modules'].values())}")
    print(f"Tests passed: {manifest['tests_passed']}")


if __name__ == "__main__":
    main()
