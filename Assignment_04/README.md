# TIES4810 Simulation - Assignment 4

**Course:** TIES4810 Simulation  
**Assignment:** Design of Experiments and Metamodeling  
**Author:** Mohammad Sayeem Sadat Hossain  
**Institution:** University of Jyväskylä

---
## An alternative solution using Event-Based model Implementation is available in following directory
``event_base``

---

## Overview

This project implements a comprehensive simulation study of a surgery unit system using **Design of Experiments (DOE)** methodology and **regression metamodeling**. The study investigates how six different system parameters affect the average queue length at the entrance to the preparation stage.

### System Description

The simulation models a surgery unit with three sequential stages:

- **Preparation** (4 or 5 units)
- **Operating Room** (1 unit, fixed)
- **Recovery** (4 or 5 units)

Patients flow through all three stages, with potential blocking when downstream resources are unavailable.

---

## Experimental Factors

The study examines six factors, each at two levels:

| Factor            | Code | Level (-) | Level (+)               |
| ----------------- | ---- | --------- | ----------------------- |
| Interarrival Time | A    | exp(25)   | exp(22.5)               |
| Preparation Time  | B    | exp(40)   | Unif(30,50)             |
| Recovery Time     | C    | exp(40)   | Unif(30,50)             |
| Preparation Units | D    | 4 units   | 5 units                 |
| Recovery Units    | E    | 4 units   | 5 units                 |
| Priority System   | F    | Disabled  | Enabled (20% emergency) |

**Note:** Operating time is fixed at exp(20) for all scenarios.

---

## Methodology

### 1. Serial Correlation Analysis

- Tests for autocorrelation in queue length samples
- Ensures successive observations are independent
- Uses high-utilization scenario (fast arrivals, slow prep)
- Computes autocorrelation coefficients ρ₁, ρ₂, ..., ρ₉

### 2. Design of Experiments

- **Design:** 2^(6-3) Fractional Factorial (Resolution III)
- **Runs:** 8 experiments
- **Replications:** 10 per experiment (80 total simulation runs)
- **Generators:** D=ABC, E=AB, F=CD
- **Primary metric:** Average queue length at entrance

### 3. Regression Analysis

- **Model:** Queue Length = β₀ + β₁·A + β₂·B + β₃·C + β₄·D + β₅·E + β₆·F + ε
- **Method:** Ordinary Least Squares (OLS)
- **Diagnostics:** Residual analysis, normality tests, model fit assessment

---

## Project Structure

```
TIES4810_Assignment4/
│
├── surgery_simulation_a4.py          # Main simulation model
├── step1_serial_correlation.py       # Autocorrelation testing
├── step2_design_of_experiments.py    # DOE execution
├── step3_regression_analysis.py      # Regression metamodel
├── run_assignment4.py                # Master execution script
│
├── results/
│   ├── experiment_results.json       # Full experimental data
│   └── experiment_summary.csv        # Summary table
│
├── figures/
│   ├── autocorr_interval100.png      # Autocorrelation (100 units)
│   ├── autocorr_interval200.png      # Autocorrelation (200 units)
│   └── regression_diagnostics.png    # Regression diagnostics
│
└── README.md                         # This file
```

---

## Requirements

### Python Version

- Python 3.11 or higher

### Dependencies

```bash
pip install simpy numpy pandas scipy matplotlib
```

**Package versions used:**

- simpy >= 4.0
- numpy >= 1.24
- pandas >= 2.0
- scipy >= 1.10
- matplotlib >= 3.7

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/TIES4810_Assignment4.git
cd TIES4810_Assignment4
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install simpy numpy pandas scipy matplotlib
```

### 4. Create Required Directories

```bash
mkdir results figures
```

---

## Usage

### Quick Start - Run Complete Pipeline

Execute all three analysis steps sequentially:

```bash
python run_assignment4.py
```

**Execution time:** Approximately 5-10 minutes

This will:

1. Run serial correlation tests (generates 2 plots)
2. Execute 80 simulation experiments (8 configurations × 10 replications)
3. Perform regression analysis and generate diagnostics

---

### Run Individual Steps

#### Step 1: Serial Correlation Analysis

```bash
python step1_serial_correlation.py
```

**Output:**

- `figures/autocorr_interval100.png`
- `figures/autocorr_interval200.png`
- Console output with autocorrelation coefficients

**Purpose:** Determine appropriate sampling strategy to ensure independent observations.

---

#### Step 2: Design of Experiments

```bash
python step2_design_of_experiments.py
```

**Output:**

- `results/experiment_results.json` - Full data from all runs
- `results/experiment_summary.csv` - Summary table

**Purpose:** Execute systematic experiments covering all factor combinations.

---

#### Step 3: Regression Analysis

```bash
python step3_regression_analysis.py
```

**Output:**

- `figures/regression_diagnostics.png` - 4-panel diagnostic plot
- Console output with regression coefficients and statistics

**Purpose:** Build metamodel and identify significant factors.

---

## Results Summary

### Key Findings

1. **Model Fit:** R² = 0.8643 (86.43% variance explained)
2. **Significant Factors:** No individual main effects reached statistical significance (α = 0.05)
3. **Largest Effect:** Factor D (Prep Rooms) with β = -0.604 (p = 0.31)

### Interpretation

The high R² combined with non-significant main effects suggests that queue length is influenced by **interaction effects** between factors rather than simple additive effects. This indicates that:

- Factors work together in complex ways
- A model including interaction terms (e.g., A×D, B×D) would likely improve interpretation
- The current main-effects-only model explains variance well but individual contributions are not isolated

---

## File Descriptions

### Core Implementation

**`surgery_simulation_a4.py`**

- Main simulation engine using SimPy
- Supports all 6 experimental factors
- Implements both FIFO and priority-based queuing
- Tracks queue lengths at patient arrivals

**`step1_serial_correlation.py`**

- Tests for autocorrelation in time series
- Computes Pearson correlation coefficients at various lags
- Generates autocorrelation plots
- Recommends sampling strategy

**`step2_design_of_experiments.py`**

- Implements 2^(6-3) fractional factorial design
- Converts design matrix to simulation configurations
- Executes replicated experiments
- Saves results in JSON and CSV formats

**`step3_regression_analysis.py`**

- Fits linear regression model
- Computes coefficient statistics (t-tests, p-values)
- Generates diagnostic plots (Actual vs Predicted, Residuals, Q-Q plot, Coefficients)
- Assesses model quality (R², adjusted R², RMSE)

**`run_assignment4.py`**

- Master script to execute all steps
- Provides user prompts between steps
- Consolidates output reporting

---

## Simulation Parameters

### Fixed Settings

- **Warmup period:** 1000 time units
- **Simulation duration:** 5000 time units
- **Replications per experiment:** 10
- **Random seed base:** 42 (incremented for each replication)

### Variable Settings (Factors)

See "Experimental Factors" section above.

---

## Outputs Explained

### results/experiment_results.json

Complete experimental data including:

- Design matrix for each run
- Factor levels
- Average queue length (mean and std deviation)
- All 10 replicate values

### results/experiment_summary.csv

Summary table with columns:

- Run number (1-8)
- Factor levels (A, B, C, D, E, F as +/-)
- Average queue length
- Standard deviation

### figures/autocorr_interval\*.png

Autocorrelation function plots showing:

- Autocorrelation coefficient (ρ) vs lag
- Threshold lines at ±0.3 (moderate correlation)
- Assessment of sample independence

### figures/regression_diagnostics.png

4-panel diagnostic plot:

1. **Actual vs Predicted:** Model fit quality
2. **Residuals vs Fitted:** Homoscedasticity check
3. **Normal Q-Q Plot:** Normality assumption
4. **Coefficient Magnitudes:** Significant factors (red bars)

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'simpy'"

**Solution:**

```bash
pip install simpy numpy pandas scipy matplotlib
```

### Issue: "Singular matrix" warning in regression

**Solution:** This is expected for fractional factorial designs due to aliasing. The code handles this using pseudo-inverse (`np.linalg.pinv`).

### Issue: Plots not displaying

**Solution:** Plots are saved to `figures/` directory as PNG files. View them with an image viewer or include in report.

### Issue: No significant factors found

**Explanation:** This is a valid result indicating:

- High variance in stochastic system
- Interaction effects dominate main effects
- Small sample size (8 experiments) limits statistical power

**Recommendation:** Report findings as-is and discuss implications.

---

## Extensions & Future Work

Potential improvements to this study:

1. **Include Interaction Terms:** Add A×D, B×D, A×B to regression model
2. **Increase Replications:** 20-30 replications per experiment for more statistical power
3. **Full Factorial Design:** Run all 64 combinations for complete analysis
4. **Response Surface Methodology:** Use quadratic models for optimization
5. **Additional Metrics:** Analyze throughput time, blocking probability

---

## Academic Integrity

This code was developed as part of coursework for TIES4810 Simulation. The implementation follows standard simulation and experimental design methodologies. All external libraries (SimPy, NumPy, etc.) are properly attributed.

---

## References

- **SimPy Documentation:** https://simpy.readthedocs.io/
- Course Lecture & Videos: TIES4810 Simulation (Lectures 1-8)

---

## Contact

**Author:** Mohammad Sayeem Sadat Hossain, Rakibul Hasan Remon, MD. Ashraful Alam  
**Course:** TIES4810 Simulation  
**Institution:** University of Jyväskylä  
**Date:** 14 December 2024

For questions about this implementation, please contact through the course management system.
