"""
Assignment 4 - Step 2: Design of Experiments
2^(6-3) Fractional Factorial Design
"""

import numpy as np
import pandas as pd
import json
from surgery_simulation_a4 import SurgerySimulation, SimulationConfig, DistributionType


class ExperimentDesign:
    """2^(6-3) Fractional Factorial Design for 6 factors"""

    def __init__(self):
        self.factors = ["A", "B", "C", "D", "E", "F"]
        self.factor_names = {
            "A": "Interarrival Time",
            "B": "Preparation Time",
            "C": "Recovery Time",
            "D": "Prep Units",
            "E": "Recovery Units",
            "F": "Priority System",
        }

    def create_2_6_3_design(self):
        """Create 2^(6-3) design (8 runs)"""
        n_runs = 8
        design_matrix = np.zeros((n_runs, 6), dtype=int)

        # Full factorial for 3 factors
        for i in range(n_runs):
            design_matrix[i, 0] = 1 if (i & 4) else -1  # A
            design_matrix[i, 1] = 1 if (i & 2) else -1  # B
            design_matrix[i, 2] = 1 if (i & 1) else -1  # C

        # Generators
        for i in range(n_runs):
            A, B, C = design_matrix[i, :3]
            design_matrix[i, 3] = A * B * C  # D = ABC
            design_matrix[i, 4] = A * B  # E = AB
            design_matrix[i, 5] = C * design_matrix[i, 3]  # F = CD

        return design_matrix

    def design_to_config(self, design_row):
        """Convert design row to SimulationConfig"""
        A, B, C, D, E, F = design_row

        config = SimulationConfig()

        # Factor A: Interarrival
        if A == -1:
            config.interarrival_dist = DistributionType.EXPONENTIAL
            config.interarrival_param1 = 25.0
        else:
            config.interarrival_dist = DistributionType.EXPONENTIAL
            config.interarrival_param1 = 22.5

        # Factor B: Preparation
        if B == -1:
            config.prep_dist = DistributionType.EXPONENTIAL
            config.prep_param1 = 40.0
        else:
            config.prep_dist = DistributionType.UNIFORM
            config.prep_param1 = 30.0
            config.prep_param2 = 50.0

        # Factor C: Recovery
        if C == -1:
            config.recovery_dist = DistributionType.EXPONENTIAL
            config.recovery_param1 = 40.0
        else:
            config.recovery_dist = DistributionType.UNIFORM
            config.recovery_param1 = 30.0
            config.recovery_param2 = 50.0

        # Factor D: Prep units
        config.num_prep_rooms = 4 if D == -1 else 5

        # Factor E: Recovery units
        config.num_recovery_rooms = 4 if E == -1 else 5

        # Factor F: Priority system
        config.emergency_probability = 0.0 if F == -1 else 0.2

        # Fixed settings
        config.sim_duration = 5000.0
        config.warmup_period = 1000.0

        return config

    def print_design_table(self, design_matrix):
        """Print design matrix"""
        print("\n" + "=" * 100)
        print("EXPERIMENT DESIGN MATRIX - 2^(6-3) Fractional Factorial")
        print("=" * 100)

        rows = []
        for i, row in enumerate(design_matrix, 1):
            row_dict = {
                "Run": i,
                "A": "+" if row[0] == 1 else "-",
                "B": "+" if row[1] == 1 else "-",
                "C": "+" if row[2] == 1 else "-",
                "D": "+" if row[3] == 1 else "-",
                "E": "+" if row[4] == 1 else "-",
                "F": "+" if row[5] == 1 else "-",
            }
            rows.append(row_dict)

        df = pd.DataFrame(rows)
        print(df.to_string(index=False))

        print("\n" + "=" * 100)
        print("FACTOR DEFINITIONS:")
        print("=" * 100)
        print("A (Interarrival):  - = exp(25)      | + = exp(22.5)    [faster]")
        print("B (Preparation):   - = exp(40)      | + = Unif(30,50)  [variable]")
        print("C (Recovery):      - = exp(40)      | + = Unif(30,50)  [variable]")
        print("D (Prep Units):    - = 4 units      | + = 5 units")
        print("E (Recovery Units):- = 4 units      | + = 5 units")
        print("F (Priority):      - = disabled     | + = enabled (20% emergency)")
        print("=" * 100 + "\n")


def run_single_experiment(config, num_replications=10):
    """Run single experiment with replications"""
    queue_lengths = []

    for rep in range(num_replications):
        config.random_seed = 42 + rep
        sim = SurgerySimulation(config)
        sim.run()
        stats = sim.get_statistics()
        queue_lengths.append(stats["avg_queue_length"])

    return {
        "mean": np.mean(queue_lengths),
        "std": np.std(queue_lengths, ddof=1),
        "replicates": queue_lengths,
    }


def run_full_experiment_series():
    """Run complete design of experiments"""
    print("\n" + "=" * 100)
    print("ASSIGNMENT 4 - DESIGN OF EXPERIMENTS")
    print("=" * 100)
    print("\nRunning 2^(6-3) fractional factorial (8 experiments)")
    print("Each experiment: 10 replications = 80 total runs")
    print("=" * 100 + "\n")

    design = ExperimentDesign()
    design_matrix = design.create_2_6_3_design()
    design.print_design_table(design_matrix)

    results = []

    for run_id, design_row in enumerate(design_matrix, 1):
        print(f"\n{'='*100}")
        print(f"Running Experiment {run_id}/8")
        print(f"{'='*100}")

        config = design.design_to_config(design_row)

        print(f"\nConfiguration:")
        print(f"  A: {config.interarrival_dist.value}({config.interarrival_param1})")
        print(
            f"  B: {config.prep_dist.value}({config.prep_param1}, {config.prep_param2})"
        )
        print(
            f"  C: {config.recovery_dist.value}({config.recovery_param1}, {config.recovery_param2})"
        )
        print(f"  D: {config.num_prep_rooms} prep rooms")
        print(f"  E: {config.num_recovery_rooms} recovery rooms")
        print(
            f"  F: Priority {'Enabled' if config.emergency_probability > 0 else 'Disabled'}"
        )

        print(f"\nRunning 10 replications...")
        result = run_single_experiment(config, num_replications=10)

        print(f"\n📊 Results:")
        print(f"   Avg Queue Length: {result['mean']:.3f} ± {result['std']:.3f}")
        print(f"   Replicates: {[f'{q:.2f}' for q in result['replicates']]}")

        results.append(
            {
                "run": run_id,
                "design": design_row.tolist(),
                "factors": {
                    "A": int(design_row[0]),
                    "B": int(design_row[1]),
                    "C": int(design_row[2]),
                    "D": int(design_row[3]),
                    "E": int(design_row[4]),
                    "F": int(design_row[5]),
                },
                "avg_queue_length": result["mean"],
                "std_queue_length": result["std"],
                "replicates": result["replicates"],
            }
        )

    # Save results
    with open("results/experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Summary table
    print("\n" + "=" * 100)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 100)

    summary_data = []
    for r in results:
        summary_data.append(
            {
                "Run": r["run"],
                "A": "+" if r["factors"]["A"] == 1 else "-",
                "B": "+" if r["factors"]["B"] == 1 else "-",
                "C": "+" if r["factors"]["C"] == 1 else "-",
                "D": "+" if r["factors"]["D"] == 1 else "-",
                "E": "+" if r["factors"]["E"] == 1 else "-",
                "F": "+" if r["factors"]["F"] == 1 else "-",
                "Avg Queue": f"{r['avg_queue_length']:.3f}",
                "Std": f"{r['std_queue_length']:.3f}",
            }
        )

    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))
    print("=" * 100)

    df_summary.to_csv("results/experiment_summary.csv", index=False)

    print(f"\n✅ Results saved:")
    print(f"   - results/experiment_results.json")
    print(f"   - results/experiment_summary.csv")

    return results


if __name__ == "__main__":
    results = run_full_experiment_series()

    print("\n" + "=" * 100)
    print("EXPERIMENTS COMPLETE!")
    print("=" * 100)
    print("\nNext: Run step3_regression_analysis.py")
    print("=" * 100 + "\n")
