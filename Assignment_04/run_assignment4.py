"""
Assignment 4 - Main Runner
Executes all analysis steps
"""

print("\n" + "=" * 70)
print("ASSIGNMENT 4 - COMPLETE ANALYSIS PIPELINE")
print("=" * 70)
print("\nThis will run:")
print("  1. Serial Correlation Analysis")
print("  2. Design of Experiments (8 experiments x 10 replications)")
print("  3. Regression Analysis")
print("=" * 70 + "\n")

input("Press ENTER to start...")

# Step 1: Serial Correlation
print("\n" + "=" * 70)
print("STEP 1: SERIAL CORRELATION ANALYSIS")
print("=" * 70 + "\n")

import step1_serial_correlation

step1_serial_correlation.run_correlation_tests()

print("\nStep 1 completed.")
input("\nPress ENTER to continue to Step 2...")

# Step 2: Design of Experiments
print("\n" + "=" * 70)
print("STEP 2: DESIGN OF EXPERIMENTS")
print("=" * 70 + "\n")

import step2_design_of_experiments

results = step2_design_of_experiments.run_full_experiment_series()

print("\nStep 2 completed.")
input("\nPress ENTER to continue to Step 3...")

# Step 3: Regression Analysis
print("\n" + "=" * 70)
print("STEP 3: REGRESSION ANALYSIS")
print("=" * 70 + "\n")

import step3_regression_analysis

step3_regression_analysis.main()

print("\n" + "=" * 70)
print("Analysis complete.")
print("=" * 70)
print("\nGenerated files:")
print("  - results/experiment_results.json")
print("  - results/experiment_summary.csv")
print("  - figures/autocorr_interval100.png")
print("  - figures/autocorr_interval200.png")
print("  - figures/regression_diagnostics.png")
print("=" * 70 + "\n")
