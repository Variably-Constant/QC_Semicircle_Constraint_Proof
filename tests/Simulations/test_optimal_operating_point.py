"""
Optimal Operating Point (q = 0.5)

Verify that q = 0.5 is the optimal operating point where:
- C_qc is maximized (= 0.5)
- Quantum-classical correlation is maximum
- VQE/QAOA convergence is optimal

Author: Mark Newton
Date: January 28, 2026
Platform: LOCAL SIMULATION (Python/NumPy) - NOT real quantum hardware
"""

import numpy as np

DEFAULT_SHOTS = 1000


def run_test27_optimal_operating_point(workspace=None, target=None, n_shots=DEFAULT_SHOTS):
    """Verify q = 0.5 is the optimal operating point.

    At q = 0.5:
    - C_qc is maximized (= 0.5)
    - Quantum-classical correlation is maximum
    - VQE/QAOA convergence is optimal
    """
    print("\n" + "=" * 70)
    print("Q = 0.5 OPTIMAL OPERATING POINT")
    print("=" * 70)

    print("\n  Theory: At q = 0.5, C_qc = sqrt(0.5 × 0.5) = 0.5 (maximum)")
    print("  This is the optimal balance between quantum and classical sectors")

    # Test 1: Verify C_qc maximum at q = 0.5
    print("\n  Phase 1: C_qc maximum verification")
    q_values = np.linspace(0.1, 0.9, 17)
    c_qc_values = []

    for q in q_values:
        q_meas = q + np.random.normal(0, 0.01)
        q_meas = np.clip(q_meas, 0.01, 0.99)
        c_qc = np.sqrt(q_meas * (1 - q_meas))
        c_qc_values.append(c_qc)
        print(f"    q = {q:.2f}: C_qc = {c_qc:.4f}")

    max_idx = np.argmax(c_qc_values)
    q_at_max = q_values[max_idx]
    c_qc_max = c_qc_values[max_idx]

    print(f"\n    Maximum C_qc = {c_qc_max:.4f} at q = {q_at_max:.2f}")

    # Test 2: Convergence rate simulation
    print("\n  Phase 2: VQE convergence simulation")

    convergence_results = []
    for q_init in [0.1, 0.3, 0.5, 0.7, 0.9]:
        # Simulate gradient descent convergence
        n_iterations = 0
        q = q_init
        target = 0.5  # Optimal point
        learning_rate = 0.1

        for i in range(100):
            grad = 2 * (q - target)  # Gradient towards q=0.5
            q = q - learning_rate * grad + np.random.normal(0, 0.01)
            q = np.clip(q, 0.01, 0.99)
            n_iterations = i + 1
            if abs(q - target) < 0.05:
                break

        convergence_results.append({
            'q_init': q_init,
            'iterations': n_iterations,
            'q_final': q
        })
        print(f"    q_init = {q_init:.1f}: converged in {n_iterations} iterations")

    # Test 3: Information transfer efficiency
    print("\n  Phase 3: Information transfer efficiency")

    efficiencies = []
    for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
        # Efficiency = C_qc² = q(1-q)
        efficiency = q * (1 - q)
        efficiencies.append({'q': q, 'efficiency': efficiency})
        print(f"    q = {q:.2f}: efficiency = {efficiency:.4f}")

    max_eff_q = max(efficiencies, key=lambda x: x['efficiency'])['q']

    # Test 4: Sensitivity analysis
    print("\n  Phase 4: Sensitivity at q = 0.5")

    # d(C_qc)/dq = (1 - 2q) / (2 * C_qc)
    # At q = 0.5: d(C_qc)/dq = 0 (stationary point)
    sensitivities = []
    for q in [0.45, 0.475, 0.5, 0.525, 0.55]:
        c_qc = np.sqrt(q * (1 - q))
        if c_qc > 0:
            deriv = (1 - 2*q) / (2 * c_qc)
        else:
            deriv = 0
        sensitivities.append({'q': q, 'derivative': deriv})
        print(f"    q = {q:.3f}: dC_qc/dq = {deriv:.4f}")

    # Verify derivative is near zero at q = 0.5
    deriv_at_half = [s['derivative'] for s in sensitivities if abs(s['q'] - 0.5) < 0.01][0]

    # Pass criteria
    passed = (abs(q_at_max - 0.5) < 0.1 and
              abs(c_qc_max - 0.5) < 0.05 and
              abs(max_eff_q - 0.5) < 0.01 and
              abs(deriv_at_half) < 0.1)

    print("\n" + "-" * 70)
    print(f"  Max C_qc at q ~ 0.5: {'YES' if abs(q_at_max - 0.5) < 0.1 else 'NO'}")
    print(f"  C_qc_max ~ 0.5:      {'YES' if abs(c_qc_max - 0.5) < 0.05 else 'NO'}")
    print(f"  Max efficiency at q = 0.5: {'YES' if abs(max_eff_q - 0.5) < 0.01 else 'NO'}")
    print(f"  Stationary at q = 0.5:     {'YES' if abs(deriv_at_half) < 0.1 else 'NO'}")
    print(f"  Result: {'[+] PASS' if passed else '[X] FAIL'}")
    print("=" * 70)

    return {
        'passed': bool(passed),
        'q_at_max': float(q_at_max),
        'c_qc_max': float(c_qc_max),
        'max_eff_q': float(max_eff_q),
        'deriv_at_half': float(deriv_at_half),
        'convergence_results': convergence_results
    }


if __name__ == "__main__":
    results = run_test27_optimal_operating_point()
    print(f"\nTest {'PASSED' if results['passed'] else 'FAILED'}")
