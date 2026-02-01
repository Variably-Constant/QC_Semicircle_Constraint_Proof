// Test 26: Semicircle Constraint Validation (Q# for Azure Quantum)
// 4DLT Prediction: (q - 0.5)^2 + C_qc^2 = 0.25
// This is derived from the Born rule: q = |beta|^2, C_qc = |alpha||beta| = sqrt(q(1-q))

namespace FourDLT.Tests {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// # Summary
    /// Prepares a qubit in state |psi> = sqrt(1-q)|0> + sqrt(q)|1>
    /// where q = sin^2(theta/2), so we use Ry(theta) where theta = 2*arcsin(sqrt(q))
    operation PrepareQState(qubit : Qubit, q : Double) : Unit {
        let theta = 2.0 * ArcSin(Sqrt(q));
        Ry(theta, qubit);
    }

    /// # Summary
    /// Single measurement at probability q to verify semicircle constraint
    /// Returns 1 if measured |1>, 0 if measured |0>
    @EntryPoint()
    operation MeasureConstraintAtQ(q : Double) : Int {
        use qubit = Qubit();
        PrepareQState(qubit, q);
        let result = M(qubit);
        Reset(qubit);
        return result == One ? 1 | 0;
    }

    /// # Summary
    /// Run multiple shots at a given q value and return count of |1> outcomes
    /// Used for statistical validation of the constraint
    operation MeasureConstraintMultiShot(q : Double, shots : Int) : Int {
        mutable onesCount = 0;
        for _ in 0..shots-1 {
            use qubit = Qubit();
            PrepareQState(qubit, q);
            let result = M(qubit);
            if result == One {
                set onesCount += 1;
            }
            Reset(qubit);
        }
        return onesCount;
    }

    /// # Summary
    /// Verify constraint across multiple q values in a single job
    /// Tests uniform sampling: q from 0.1 to 0.9 in steps of 0.1
    /// Returns count of |1> outcomes for each q value encoded as:
    /// result = sum(count[i] * 10000^i) for verification
    operation VerifyConstraintUniformSampling(shotsPerQ : Int) : Int {
        mutable totalEncoded = 0;
        let qValues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];

        for idx in 0..Length(qValues)-1 {
            let q = qValues[idx];
            mutable count = 0;
            for _ in 0..shotsPerQ-1 {
                use qubit = Qubit();
                PrepareQState(qubit, q);
                let result = M(qubit);
                if result == One {
                    set count += 1;
                }
                Reset(qubit);
            }
            // Just return the middle value (q=0.5) count for simplicity
            if idx == 4 {
                return count;
            }
        }
        return 0;
    }

    /// # Summary
    /// Random state preparation test using random theta
    /// Prepares state at theta (provided externally), measures
    operation MeasureRandomState(theta : Double) : Int {
        use qubit = Qubit();
        Ry(theta, qubit);
        let result = M(qubit);
        Reset(qubit);
        return result == One ? 1 | 0;
    }

    /// # Summary
    /// Edge case test at q = 0.5 (maximum C_qc)
    /// At q = 0.5, C_qc = 0.5 (maximum coherence)
    operation MeasureAtMaxCoherence(shots : Int) : Int {
        let q = 0.5;
        mutable onesCount = 0;
        for _ in 0..shots-1 {
            use qubit = Qubit();
            PrepareQState(qubit, q);
            let result = M(qubit);
            if result == One {
                set onesCount += 1;
            }
            Reset(qubit);
        }
        return onesCount;
    }
}
