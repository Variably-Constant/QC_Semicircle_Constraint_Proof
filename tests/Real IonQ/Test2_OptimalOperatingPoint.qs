// Test 27: Optimal Operating Point q = 0.5 (Q# for Azure Quantum)
// 4DLT Prediction: At q = 0.5, C_qc = 0.5 is maximum
// Maximum quantum-classical correlation and optimal VQE/QAOA convergence

namespace FourDLT.Tests {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// # Summary
    /// Prepares a qubit in state |psi> = sqrt(1-q)|0> + sqrt(q)|1>
    operation PrepareQState(qubit : Qubit, q : Double) : Unit {
        let theta = 2.0 * ArcSin(Sqrt(q));
        Ry(theta, qubit);
    }

    /// # Summary
    /// Measure C_qc at a given q value using interference
    /// After H gate: P(0) - P(1) = 2*sqrt(q(1-q)) = 2*C_qc
    @EntryPoint()
    operation MeasureCoherenceAtQ(q : Double) : Int {
        use qubit = Qubit();
        PrepareQState(qubit, q);
        H(qubit);  // Convert coherence to measurable probability difference
        let result = M(qubit);
        Reset(qubit);
        return result == One ? 1 | 0;
    }

    /// # Summary
    /// Multi-shot coherence measurement at given q
    operation MeasureCoherenceMultiShot(q : Double, shots : Int) : Int {
        mutable onesCount = 0;
        for _ in 0..shots-1 {
            use qubit = Qubit();
            PrepareQState(qubit, q);
            H(qubit);
            let result = M(qubit);
            if result == One {
                set onesCount += 1;
            }
            Reset(qubit);
        }
        return onesCount;
    }

    /// # Summary
    /// Compare coherence across different q values
    /// Returns encoded results for q = 0.1, 0.3, 0.5, 0.7, 0.9
    operation CompareCoherenceAcrossQ(shotsPerQ : Int) : Int {
        let qValues = [0.1, 0.3, 0.5, 0.7, 0.9];
        mutable maxCount = 0;
        mutable maxIdx = 0;

        for idx in 0..Length(qValues)-1 {
            let q = qValues[idx];
            mutable count = 0;
            for _ in 0..shotsPerQ-1 {
                use qubit = Qubit();
                PrepareQState(qubit, q);
                H(qubit);
                let result = M(qubit);
                if result == Zero {  // P(0) is related to coherence
                    set count += 1;
                }
                Reset(qubit);
            }
            if count > maxCount {
                set maxCount = count;
                set maxIdx = idx;
            }
        }
        // Return index of q with maximum coherence (should be 2 for q=0.5)
        return maxIdx;
    }

    /// # Summary
    /// VQE convergence test: prepare state, apply variational rotation, measure
    /// At q=0.5, gradient information is maximized for learning
    operation VQEGradientTest(qInit : Double, variationalAngle : Double) : Int {
        use qubit = Qubit();

        // Prepare initial state
        PrepareQState(qubit, qInit);

        // Apply variational rotation
        Ry(variationalAngle, qubit);

        // Measure
        let result = M(qubit);
        Reset(qubit);
        return result == One ? 1 | 0;
    }

    /// # Summary
    /// Gradient estimation at q by finite difference
    /// Compares measurements at theta +/- delta
    operation EstimateGradient(q : Double, delta : Double, shots : Int) : Int {
        let thetaBase = 2.0 * ArcSin(Sqrt(q));

        // Forward difference
        mutable countPlus = 0;
        for _ in 0..shots-1 {
            use qubit = Qubit();
            Ry(thetaBase + delta, qubit);
            H(qubit);
            let result = M(qubit);
            if result == One {
                set countPlus += 1;
            }
            Reset(qubit);
        }

        // Backward difference
        mutable countMinus = 0;
        for _ in 0..shots-1 {
            use qubit = Qubit();
            Ry(thetaBase - delta, qubit);
            H(qubit);
            let result = M(qubit);
            if result == One {
                set countMinus += 1;
            }
            Reset(qubit);
        }

        // Return difference (gradient proportional to this)
        return countPlus - countMinus;
    }

    /// # Summary
    /// Information efficiency test at q=0.5 vs edges
    /// At q=0.5: efficiency = C_qc^2 = 0.25 (maximum)
    operation MeasureEfficiencyAtQ(q : Double, shots : Int) : Int {
        // Efficiency is measured via two-outcome statistics
        // C_qc^2 = q(1-q) determines information transfer
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
    /// Test stationarity at q=0.5: derivative dC_qc/dq should be zero
    /// Uses parameter shift rule to estimate derivative
    operation TestStationarity(shotsPerPoint : Int) : Int {
        let delta = 0.025;  // Small shift around q=0.5

        // Measure at q = 0.5 - delta, 0.5, 0.5 + delta
        mutable countMinus = 0;
        mutable countCenter = 0;
        mutable countPlus = 0;

        for _ in 0..shotsPerPoint-1 {
            // q = 0.475
            use qubit = Qubit();
            PrepareQState(qubit, 0.475);
            H(qubit);
            if M(qubit) == One { set countMinus += 1; }
            Reset(qubit);

            // q = 0.5
            use qubit2 = Qubit();
            PrepareQState(qubit2, 0.5);
            H(qubit2);
            if M(qubit2) == One { set countCenter += 1; }
            Reset(qubit2);

            // q = 0.525
            use qubit3 = Qubit();
            PrepareQState(qubit3, 0.525);
            H(qubit3);
            if M(qubit3) == One { set countPlus += 1; }
            Reset(qubit3);
        }

        // Approximate second derivative (for stationarity check)
        // d^2/dq^2 at q=0.5 should be negative (maximum)
        let secondDeriv = countPlus - 2 * countCenter + countMinus;
        return secondDeriv;
    }
}
