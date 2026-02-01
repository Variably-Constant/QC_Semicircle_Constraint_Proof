#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Quantum Test Runner for Semicircle Constraint Q# Tests

Runs the three Q# test files on real quantum hardware via Azure Quantum:
  - Test1_SemicircleConstraintValidation.qs
  - Test2_OptimalOperatingPoint.qs
  - Test3_BarrenPlateauGeometry.qs

NOTE: For local Python simulations, see tests/Simulations/ folder instead.
      This runner is ONLY for real quantum hardware execution.

Usage:
    python azure_quantum_tests.py --test 1 --shots 100 \\
        --resource-id "/subscriptions/.../Microsoft.Quantum/Workspaces/..." \\
        --location "eastus" \\
        --target "ionq.qpu"

    # Run all tests:
    python azure_quantum_tests.py --test all --shots 100 --resource-id "..." --location "eastus"

Requirements:
    pip install azure-quantum qsharp numpy
    az login

Author: Mark Newton
Date: January 2026
"""

import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# AZURE QUANTUM IMPORTS
# ============================================================================

AZURE_AVAILABLE = False
QSHARP_AVAILABLE = False

try:
    from azure.quantum import Workspace
    AZURE_AVAILABLE = True
    print("Azure Quantum SDK loaded successfully")
except ImportError:
    print("Warning: azure-quantum not installed. Install with: pip install azure-quantum")

try:
    import qsharp
    QSHARP_AVAILABLE = True
    print("Q# SDK loaded successfully")
except ImportError:
    print("Warning: qsharp not installed. Install with: pip install qsharp")

# ============================================================================
# TEST DEFINITIONS
# ============================================================================

TESTS = {
    1: {
        "name": "Semicircle Constraint Validation",
        "file": "Test1_SemicircleConstraintValidation.qs",
        "description": "Validates (q - 0.5)^2 + C_qc^2 = 0.25",
        "entry_point": "FourDLT.Tests.MeasureConstraintAtQ",
        "q_values": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
                    0.50, 0.55, 0.60, 0.65, 0.70, 0.75],
    },
    2: {
        "name": "Optimal Operating Point",
        "file": "Test2_OptimalOperatingPoint.qs",
        "description": "Verifies q = 0.5 maximizes C_qc",
        "entry_point": "FourDLT.Tests.MeasureCoherenceAtQ",
        "q_values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    },
    3: {
        "name": "Barren Plateau Geometry",
        "file": "Test3_BarrenPlateauGeometry.qs",
        "description": "Tests gradient variance scaling with q",
        "entry_point": "FourDLT.Tests.MeasureGradientAtQ",
        "q_values": [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95],
    },
}

# ============================================================================
# AZURE QUANTUM CONNECTION
# ============================================================================

def connect_to_azure(resource_id: str, location: str):
    """Connect to Azure Quantum workspace."""
    if not AZURE_AVAILABLE:
        raise RuntimeError("Azure Quantum SDK not available. Install with: pip install azure-quantum")

    workspace = Workspace(
        resource_id=resource_id,
        location=location
    )
    print(f"Connected to Azure Quantum workspace")
    print(f"  Location: {location}")
    return workspace

def list_targets(workspace):
    """List available targets in the workspace."""
    print("\nAvailable targets:")
    for target in workspace.get_targets():
        print(f"  - {target.name}")
    return workspace.get_targets()

# ============================================================================
# Q# TEST EXECUTION
# ============================================================================

def run_qsharp_test(test_num: int, workspace, target: str, shots: int, q_values: list = None):
    """
    Run a Q# test file on Azure Quantum.

    Args:
        test_num: Test number (1, 2, or 3)
        workspace: Azure Quantum workspace
        target: Target backend (e.g., "ionq.qpu", "ionq.simulator")
        shots: Number of shots per measurement
        q_values: List of q values to test (uses defaults if None)

    Returns:
        dict: Test results
    """
    if test_num not in TESTS:
        raise ValueError(f"Invalid test number: {test_num}. Must be 1, 2, or 3.")

    test_info = TESTS[test_num]
    test_file = Path(__file__).parent / test_info["file"]

    if not test_file.exists():
        raise FileNotFoundError(f"Q# test file not found: {test_file}")

    if q_values is None:
        q_values = test_info["q_values"]

    print(f"\n{'='*60}")
    print(f"Test {test_num}: {test_info['name']}")
    print(f"{'='*60}")
    print(f"File: {test_info['file']}")
    print(f"Target: {target}")
    print(f"Shots: {shots}")
    print(f"Q values: {len(q_values)} points from {min(q_values)} to {max(q_values)}")

    results = {
        "test_number": test_num,
        "test_name": test_info["name"],
        "description": test_info["description"],
        "target": target,
        "shots": shots,
        "timestamp": datetime.now().isoformat(),
        "measurements": []
    }

    # Check Q# availability
    if not QSHARP_AVAILABLE:
        print("ERROR: Q# SDK not available. Install with: pip install qsharp")
        results["error"] = "Q# SDK not installed"
        return results

    try:
        # Load and compile Q# file
        print(f"\nLoading Q# file: {test_file.name}")
        with open(test_file, 'r') as f:
            qs_code = f.read()

        qsharp.eval(qs_code)
        print("Q# code compiled successfully")

        # Run measurements for each q value
        for i, q in enumerate(q_values):
            print(f"\n  [{i+1}/{len(q_values)}] Testing q = {q:.3f}...")

            # Submit job to Azure Quantum
            entry_point = test_info["entry_point"]
            job = qsharp.azure.submit(
                f"{entry_point}({q})",
                target=target,
                shots=shots,
                workspace=workspace
            )

            print(f"    Job ID: {job.id}")
            print(f"    Status: Waiting for completion (may take 10-30 min on hardware)...")

            # Wait for job completion - no timeout (hardware jobs can take 30+ minutes)
            # The default SDK timeout is often too short for queued hardware jobs
            job.wait_for_completion(timeout_secs=None)  # None = wait indefinitely
            result = job.get_results(timeout_secs=None)

            # Parse results - count |1> outcomes
            ones_count = sum(1 for r in result if r == 1)
            q_measured = ones_count / shots
            c_qc = np.sqrt(q_measured * (1 - q_measured))

            # Calculate theoretical C_qc for comparison
            c_qc_theory = np.sqrt(q * (1 - q))

            measurement = {
                "q_theory": q,
                "q_measured": round(q_measured, 4),
                "c_qc_measured": round(c_qc, 4),
                "c_qc_theory": round(c_qc_theory, 4),
                "ones_count": ones_count,
                "zeros_count": shots - ones_count,
                "job_id": job.id
            }
            results["measurements"].append(measurement)

            print(f"    Results: q_measured = {q_measured:.3f}, C_qc = {c_qc:.3f}")
            print(f"    Theory:  q_theory = {q:.3f}, C_qc = {c_qc_theory:.3f}")

        # Calculate summary statistics
        if results["measurements"]:
            q_theory = np.array([m["q_theory"] for m in results["measurements"]])
            q_meas = np.array([m["q_measured"] for m in results["measurements"]])

            if len(q_theory) > 1:
                correlation = np.corrcoef(q_theory, q_meas)[0, 1]
            else:
                correlation = 1.0

            results["summary"] = {
                "total_measurements": len(results["measurements"]),
                "total_shots": len(results["measurements"]) * shots,
                "correlation": round(float(correlation), 4),
                "mean_q_error": round(float(np.mean(q_meas - q_theory)), 4),
                "std_q_error": round(float(np.std(q_meas - q_theory)), 4),
                "max_q_error": round(float(np.max(np.abs(q_meas - q_theory))), 4),
            }

            print(f"\n  {'='*40}")
            print(f"  Test {test_num} Summary:")
            print(f"  {'='*40}")
            print(f"    Total measurements: {results['summary']['total_measurements']}")
            print(f"    Total shots: {results['summary']['total_shots']}")
            print(f"    Correlation (theory vs measured): {correlation:.4f}")
            print(f"    Mean q error: {results['summary']['mean_q_error']:.4f}")
            print(f"    Std q error: {results['summary']['std_q_error']:.4f}")

            # Determine pass/fail based on correlation
            passed = correlation > 0.9
            results["passed"] = passed
            print(f"    Status: {'PASSED' if passed else 'NEEDS REVIEW'} (r > 0.9)")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        results["passed"] = False

    return results

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run Q# semicircle constraint tests on Azure Quantum (real hardware only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Test 1 (Semicircle Constraint) on IonQ hardware:
  python azure_quantum_tests.py --test 1 --shots 52 \\
      --resource-id "/subscriptions/.../Microsoft.Quantum/Workspaces/TOF" \\
      --location eastus --target ionq.qpu

  # Run all tests on IonQ simulator:
  python azure_quantum_tests.py --test all --shots 100 \\
      --resource-id "..." --location eastus --target ionq.simulator

  # List available targets:
  python azure_quantum_tests.py --list-targets \\
      --resource-id "..." --location eastus

Available Tests:
  1 - Semicircle Constraint Validation: (q - 0.5)^2 + C_qc^2 = 0.25  (15 points)
  2 - Optimal Operating Point: q = 0.5 maximizes C_qc               (9 points)
  3 - Barren Plateau Geometry: Gradient variance ~ q(1-q)           (9 points)

COST WARNING:
  Running on real quantum hardware incurs PER-JOB MINIMUM charges!

  IonQ Per-Job Minimums (as of 2025):
    - Forte-1 (ionq.qpu.forte-1):  $25.00 per job minimum
    - Aria-1 (ionq.qpu.aria-1):    $12.50 per job minimum
    + Additional per-shot/per-gate costs on top of minimum

  Each q-value = 1 job, so:
    - Test 1: 15 jobs → $375 minimum (Forte-1) or $187.50 (Aria)
    - Test 2: 9 jobs  → $225 minimum (Forte-1) or $112.50 (Aria)
    - Test 3: 9 jobs  → $225 minimum (Forte-1) or $112.50 (Aria)
    - All tests: 33 jobs → $825 minimum (Forte-1) or $412.50 (Aria)

  FREE alternatives:
    - ionq.simulator: Free cloud simulation with noise model
    - tests/Simulations/: Free local Python simulations

NOTE: For FREE local Python simulations, see tests/Simulations/ folder instead.
      This runner is ONLY for real quantum hardware execution via Azure Quantum.
        """
    )

    parser.add_argument("--test", type=str, default="1",
                        help="Test number (1, 2, 3) or 'all' (default: 1)")
    parser.add_argument("--shots", type=int, default=52,
                        help="Number of shots per measurement (default: 52)")
    parser.add_argument("--resource-id", type=str, required=False,
                        help="Azure Quantum workspace resource ID (required)")
    parser.add_argument("--location", type=str, default="eastus",
                        help="Azure region (default: eastus)")
    parser.add_argument("--target", type=str, default="ionq.qpu",
                        help="Target backend (default: ionq.qpu)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file (default: auto-generated)")
    parser.add_argument("--list-targets", action="store_true",
                        help="List available targets and exit")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip cost confirmation prompt")

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Semicircle Constraint - Azure Quantum Test Runner")
    print("="*60)
    print("\nThis runner executes Q# tests on REAL quantum hardware.")
    print("For local simulations, see tests/Simulations/ folder.\n")

    # Check requirements
    if not AZURE_AVAILABLE:
        print("\nERROR: Azure Quantum SDK not installed.")
        print("Install with: pip install azure-quantum")
        print("\nFor local simulations, use the files in tests/Simulations/ instead.")
        sys.exit(1)

    if not QSHARP_AVAILABLE:
        print("\nERROR: Q# SDK not installed.")
        print("Install with: pip install qsharp")
        sys.exit(1)

    if not args.resource_id:
        print("\nERROR: --resource-id is required for Azure Quantum connection.")
        print("\nGet your resource ID from the Azure Portal:")
        print("  Azure Portal > Quantum Workspaces > Your Workspace > Properties > Resource ID")
        print("\nExample:")
        print('  --resource-id "/subscriptions/YOUR-SUB/resourceGroups/YOUR-RG/providers/Microsoft.Quantum/Workspaces/YOUR-WS"')
        sys.exit(1)

    # Connect to Azure Quantum
    workspace = connect_to_azure(args.resource_id, args.location)

    # List targets if requested
    if args.list_targets:
        list_targets(workspace)
        sys.exit(0)

    # Determine which tests to run
    if args.test.lower() == "all":
        test_nums = [1, 2, 3]
    else:
        try:
            test_nums = [int(args.test)]
        except ValueError:
            print(f"ERROR: Invalid test number '{args.test}'. Use 1, 2, 3, or 'all'.")
            sys.exit(1)

    # Validate test numbers
    for t in test_nums:
        if t not in TESTS:
            print(f"ERROR: Test {t} not found. Available tests: 1, 2, 3")
            sys.exit(1)

    # Calculate and display cost estimate
    total_jobs = sum(len(TESTS[t]["q_values"]) for t in test_nums)
    total_shots = total_jobs * args.shots

    # IonQ per-job minimum costs (as of 2025)
    FORTE_MIN = 25.00  # Forte-1 per-job minimum
    ARIA_MIN = 12.50   # Aria-1 per-job minimum

    print("\n" + "="*60)
    print("COST ESTIMATE")
    print("="*60)
    print(f"Tests to run: {test_nums}")
    print(f"Total jobs (1 per q-value): {total_jobs}")
    print(f"Shots per job: {args.shots}")
    print(f"Total shots: {total_shots}")
    print(f"Target: {args.target}")
    print()

    if "simulator" in args.target.lower():
        print("Using SIMULATOR - No cost (FREE)")
    else:
        forte_cost = total_jobs * FORTE_MIN
        aria_cost = total_jobs * ARIA_MIN

        print("IonQ Per-Job MINIMUM Costs:")
        print(f"  Forte-1: {total_jobs} jobs × ${FORTE_MIN:.2f} = ${forte_cost:.2f} USD minimum")
        print(f"  Aria-1:  {total_jobs} jobs × ${ARIA_MIN:.2f} = ${aria_cost:.2f} USD minimum")
        print()
        print("  + Additional per-shot and per-gate costs on top of minimum")
        print()
        print("WARNING: These are MINIMUM costs. Actual costs may be higher.")
        print("         Check Azure Quantum pricing for current rates.")
        print()
        print("FREE alternatives:")
        print("  --target ionq.simulator  (cloud simulator with noise model)")
        print("  tests/Simulations/       (local Python simulations)")

    print("="*60)

    # Confirm before running on real hardware (unless --yes flag)
    if "simulator" not in args.target.lower() and not args.yes:
        print()
        response = input("Proceed with real hardware execution? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Aborted. Use tests/Simulations/ for free local testing.")
            sys.exit(0)

    # Run tests
    all_results = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "target": args.target,
            "shots_per_point": args.shots,
            "platform": "Azure Quantum",
            "hardware": "Real Quantum Hardware (NOT simulation)",
            "tests_run": test_nums
        },
        "tests": {}
    }

    passed_count = 0
    for test_num in test_nums:
        results = run_qsharp_test(
            test_num=test_num,
            workspace=workspace,
            target=args.target,
            shots=args.shots
        )
        all_results["tests"][f"test{test_num}"] = results
        if results.get("passed", False):
            passed_count += 1

    # Save results
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"azure_results_{args.target.replace('.', '_')}_{timestamp}.json"

    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Output saved to: {output_path}")
    print(f"\nTests: {passed_count}/{len(test_nums)} PASSED")
    print("-"*40)

    for test_key, test_result in all_results["tests"].items():
        status = "PASSED" if test_result.get("passed", False) else "FAILED/ERROR"
        name = test_result.get("test_name", test_key)
        corr = test_result.get("summary", {}).get("correlation", "N/A")

        print(f"  {test_key}: {name}")
        print(f"           Status: {status}")
        if isinstance(corr, float):
            print(f"           Correlation: {corr:.4f}")
        if "error" in test_result:
            print(f"           Error: {test_result['error']}")
        print()

    print("="*60)

if __name__ == "__main__":
    main()
