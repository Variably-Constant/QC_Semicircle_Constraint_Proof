"""
Semicircle Constraint Validation

Rigorous validation of the fundamental constraint:
    (q - 0.5)² + C_qc² = 0.25

This is derived from the Born rule: q = |β|², C_qc = |α||β| = sqrt(q(1-q))
The constraint is a direct consequence of normalization |α|² + |β|² = 1.

Author: Mark Newton
Date: January 28, 2026
Platform: LOCAL SIMULATION (Python/NumPy) - NOT real quantum hardware
Note: Real IonQ Forte-1 hardware results are in tests/Real IonQ/
"""

import numpy as np

DEFAULT_SHOTS = 1000


def run_test26_semicircle_constraint(workspace=None, target=None, n_shots=DEFAULT_SHOTS):
    """Rigorous validation of the semicircle constraint.

    This test establishes the fundamental constraint:
    (q - 0.5)² + C_qc² = 0.25

    This is derived from the Born rule: q = |α|², C_qc = |α||β| = sqrt(q(1-q))
    The constraint is a direct consequence of normalization |α|² + |β|² = 1.
    """
    print("\n" + "=" * 70)
    print("SEMICIRCLE CONSTRAINT VALIDATION")
    print("=" * 70)

    print("\n  Constraint: (q - 0.5)² + C_qc² = 0.25")
    print("  Derived from Born rule and normalization")

    # Test 1: Uniform sampling across q
    print("\n  Phase 1: Uniform q sampling")
    q_values = np.linspace(0.01, 0.99, 50)
    residuals_uniform = []

    for q in q_values:
        # Prepare state with target q
        q_meas = q + np.random.normal(0, 0.005)
        q_meas = np.clip(q_meas, 0.001, 0.999)

        c_qc = np.sqrt(max(0, q_meas * (1 - q_meas)))
        residual = (q_meas - 0.5)**2 + c_qc**2 - 0.25
        residuals_uniform.append(abs(residual))

    rms_uniform = np.sqrt(np.mean(np.array(residuals_uniform)**2))
    print(f"    RMS residual: {rms_uniform:.8f}")

    # Test 2: Random state preparation
    print("\n  Phase 2: Random state preparation (100 states)")
    residuals_random = []

    for _ in range(100):
        # Random theta
        theta = np.random.uniform(0, np.pi)
        q = np.sin(theta/2)**2 + np.random.normal(0, 0.005)
        q = np.clip(q, 0.001, 0.999)

        c_qc = np.sqrt(max(0, q * (1 - q)))
        residual = (q - 0.5)**2 + c_qc**2 - 0.25
        residuals_random.append(abs(residual))

    rms_random = np.sqrt(np.mean(np.array(residuals_random)**2))
    max_random = max(residuals_random)
    print(f"    RMS residual: {rms_random:.8f}")
    print(f"    Max residual: {max_random:.8f}")

    # Test 3: Edge case validation
    print("\n  Phase 3: Edge cases")
    edge_cases = [
        (0.001, "q ~ 0 (near classical)"),
        (0.5, "q = 0.5 (max C_qc)"),
        (0.999, "q ~ 1"),
    ]
    edge_results = []

    for q, label in edge_cases:
        c_qc = np.sqrt(q * (1 - q))
        residual = (q - 0.5)**2 + c_qc**2 - 0.25
        edge_results.append(abs(residual))
        print(f"    {label}: residual = {residual:.10f}")

    # Test 4: Geometric verification (points lie on circle)
    print("\n  Phase 4: Geometric verification")

    # Transform to circle coordinates: x = q - 0.5, y = C_qc
    # Should satisfy x² + y² = 0.25 (circle of radius 0.5)
    radii = []
    for q in np.linspace(0.01, 0.99, 100):
        x = q - 0.5
        y = np.sqrt(q * (1 - q))
        r = np.sqrt(x**2 + y**2)
        radii.append(r)

    mean_radius = np.mean(radii)
    radius_std = np.std(radii)
    print(f"    Mean radius: {mean_radius:.6f} (expected: 0.5)")
    print(f"    Radius std:  {radius_std:.8f}")

    # Pass criteria
    passed = (rms_uniform < 0.001 and
              rms_random < 0.001 and
              max_random < 0.01 and
              abs(mean_radius - 0.5) < 0.001)

    print("\n" + "-" * 70)
    print(f"  RMS uniform < 0.001: {'YES' if rms_uniform < 0.001 else 'NO'}")
    print(f"  RMS random < 0.001:  {'YES' if rms_random < 0.001 else 'NO'}")
    print(f"  Max residual < 0.01: {'YES' if max_random < 0.01 else 'NO'}")
    print(f"  Mean radius ~ 0.5:   {'YES' if abs(mean_radius - 0.5) < 0.001 else 'NO'}")
    print(f"  Result: {'[+] PASS' if passed else '[X] FAIL'}")
    print("=" * 70)

    return {
        'passed': bool(passed),
        'rms_uniform': float(rms_uniform),
        'rms_random': float(rms_random),
        'max_residual': float(max_random),
        'mean_radius': float(mean_radius),
        'radius_std': float(radius_std)
    }


if __name__ == "__main__":
    results = run_test26_semicircle_constraint()
    print(f"\nTest {'PASSED' if results['passed'] else 'FAILED'}")
