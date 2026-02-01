# The Semicircle Constraint

**A Fundamental Geometric Principle in Quantum Mechanics**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18408825.svg)](https://doi.org/10.5281/zenodo.18408825)

## Overview

This repository contains the paper, code, and experimental data establishing the **semicircle constraint** as a fundamental geometric principle in quantum mechanics:

```
(q - 1/2)^2 + C_qc^2 = 1/4
```

where `q` is measurement probability and `C_qc = sqrt(q(1-q))` is the quantum-classical correlation.

## Key Results

| Result | Status |
|--------|--------|
| Semicircle constraint derived from Born rule | **Proven** |
| q = 0.5 is unique maximum of C_qc | **Proven** |
| Fisher information constant along semicircle | **Proven** |
| Geometric origin of barren plateaus | Simulation validated |
| Core constraint validation on IonQ Forte-1 | **Hardware validated** (r = 0.943) |

## Repository Structure

```
.
├── semicircleconstraint_foundations.tex   # LaTeX source
├── semicircleconstraint_foundations.pdf   # Compiled paper
├── tests/
│   ├── Real IonQ/                         # Hardware test results
│   │   ├── Test1_SemicircleConstraintValidation.qs
│   │   ├── Test2_OptimalOperatingPoint.qs
│   │   ├── Test3_BarrenPlateauGeometry.qs
│   │   ├── azure_quantum_tests.py         # Python runner
│   │   └── SC_Constraint_*.json           # IonQ Forte-1 results
│   └── Simulations/                       # Local simulation tests
│       ├── test_semicircle_constraint.py
│       ├── test_optimal_operating_point.py
│       └── test_barren_plateau_geometry.py
├── .zenodo.json                           # Zenodo metadata
└── LICENSE                                # CC BY 4.0
```

## Hardware Validation

Partial experimental validation on **IonQ Forte-1** via Azure Quantum:
- **15 test points** across q = 0.05 to 0.75
- **52 shots** per measurement
- **Correlation**: r = 0.943 (theory vs measured)
- **Date**: January 30, 2026

## Running Tests

### Local Simulation (free)
```bash
cd tests/Simulations/
python test_semicircle_constraint.py
```

### Real Hardware (requires Azure Quantum)
```bash
pip install azure-quantum qsharp numpy
az login

cd "tests/Real IonQ/"
python azure_quantum_tests.py \
    --resource-id "/subscriptions/.../Microsoft.Quantum/Workspaces/..." \
    --location "eastus" \
    --target "ionq.qpu.forte-1" \
    --shots 52
```

## Citation

```bibtex
@misc{newton2026semicircle,
  author       = {Newton, Mark},
  title        = {The Semicircle Constraint: A Fundamental Geometric Principle in Quantum Mechanics},
  year         = {2026},
  doi          = {10.5281/zenodo.18408825},
  url          = {https://doi.org/10.5281/zenodo.18408825}
}
```

## Related Work

This is paper 1 of a three-paper series:
1. **Semicircle Constraint** (this work) - Fundamental principle
2. **Complete Circle** - Extension to full 2π with CPT conjecture
3. **Fractals & Coherence** - Connection to fractal structures

## Author

**Mark Newton**
mark@variablyconstant.com
ORCID: [0009-0003-2200-2226](https://orcid.org/0009-0003-2200-2226)

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
