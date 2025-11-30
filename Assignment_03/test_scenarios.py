import simpy
import random
import statistics
import numpy as np
from surgery_simulation import SurgerySimulation, SimulationConfig
from typing import List, Dict
import json


class ScenarioTester:
    """Run multiple replications and compute confidence intervals"""

    def __init__(self, num_replications: int = 20):
        self.num_replications = num_replications

    def run_replications(
        self, config: SimulationConfig, scenario_name: str = ""
    ) -> List[Dict]:
        """Run multiple independent replications with different seeds"""
        results = []

        print(f"\n{'='*60}")
        print(f"Running {scenario_name}")
        print(f"{'='*60}")

        for i in range(self.num_replications):
            # Use different seed for each replication
            config.random_seed = 42 + i

            sim = SurgerySimulation(config)
            sim.run()
            stats = sim.get_statistics()

            if stats:
                results.append(stats)
                print(
                    f"Rep {i+1:2d}/{self.num_replications}: "
                    f"Throughput={stats['avg_throughput_time']:6.2f} min, "
                    f"OR Blocking={stats['or_blocking_probability']:6.4f} ({stats['or_blocking_probability']*100:5.2f}%), "
                    f"Prep Queue={stats['avg_prep_queue_length']:5.2f}"
                )

        return results

    def compute_confidence_interval(self, data: List[float], confidence: float = 0.95):
        """
        Compute confidence interval using t-distribution
        Based on lecture material (Lecture 5 - hypothesis testing)
        """
        n = len(data)
        if n < 2:
            return None

        mean = statistics.mean(data)
        std = statistics.stdev(data)

        # t-value for 95% confidence (two-tailed)
        # For n=20, df=19, t_0.025 ≈ 2.093
        t_values = {
            5: 2.776,
            6: 2.571,
            7: 2.447,
            8: 2.365,
            9: 2.306,
            10: 2.262,
            15: 2.145,
            20: 2.093,
            30: 2.042,
        }
        t_critical = t_values.get(n, 2.093)  # Default to n=20

        margin_of_error = t_critical * (std / np.sqrt(n))

        return {
            "mean": mean,
            "std": std,
            "ci_lower": mean - margin_of_error,
            "ci_upper": mean + margin_of_error,
            "margin_of_error": margin_of_error,
            "n": n,
        }

    def analyze_results(self, results: List[Dict]) -> Dict:
        """Compute aggregate statistics with confidence intervals"""

        # Extract metrics from all replications
        throughput_times = [r["avg_throughput_time"] for r in results]
        blocking_probs = [r["or_blocking_probability"] for r in results]
        prep_queue_lengths = [r["avg_prep_queue_length"] for r in results]

        analysis = {
            "throughput_time": self.compute_confidence_interval(throughput_times),
            "or_blocking_probability": self.compute_confidence_interval(blocking_probs),
            "prep_queue_length": self.compute_confidence_interval(prep_queue_lengths),
            "num_replications": len(results),
            "raw_throughput": throughput_times,
            "raw_blocking": blocking_probs,
            "raw_prep_queue": prep_queue_lengths,
        }

        return analysis

    def print_analysis(self, analysis: Dict, scenario_name: str = "Scenario"):
        """Print formatted analysis results"""
        print(f"\n{'='*70}")
        print(
            f"📊 {scenario_name} - Analysis Results (n={analysis['num_replications']})"
        )
        print(f"{'='*70}")

        print(f"\n🔹 Average Throughput Time (minutes):")
        tt = analysis["throughput_time"]
        print(f"   Mean: {tt['mean']:.2f} min")
        print(f"   95% CI: [{tt['ci_lower']:.2f}, {tt['ci_upper']:.2f}]")
        print(f"   Margin of Error: ±{tt['margin_of_error']:.2f} min")
        print(f"   Std Dev: {tt['std']:.2f} min")

        print(f"\n🔹 OR Blocking Probability:")
        bp = analysis["or_blocking_probability"]
        print(f"   Mean: {bp['mean']:.4f} ({bp['mean']*100:.2f}%)")
        print(f"   95% CI: [{bp['ci_lower']:.4f}, {bp['ci_upper']:.4f}]")
        print(
            f"   Margin of Error: ±{bp['margin_of_error']:.4f} (±{bp['margin_of_error']*100:.2f}%)"
        )
        print(f"   Std Dev: {bp['std']:.4f}")

        print(f"\n🔹 Average Prep Queue Length:")
        pq = analysis["prep_queue_length"]
        print(f"   Mean: {pq['mean']:.2f} patients")
        print(f"   95% CI: [{pq['ci_lower']:.2f}, {pq['ci_upper']:.2f}]")
        print(f"   Margin of Error: ±{pq['margin_of_error']:.2f}")
        print(f"   Std Dev: {pq['std']:.2f}")

        print(f"{'='*70}\n")


def test_config_3p5r():
    """Configuration 1: 3 prep, 1 OR, 5 recovery"""
    config = SimulationConfig(
        num_prep_rooms=3,
        num_operating_rooms=1,
        num_recovery_rooms=5,
        sim_duration=1000.0,  # As per assignment
        warmup_period=200.0,  # Warmup before monitoring
    )

    tester = ScenarioTester(num_replications=20)
    results = tester.run_replications(config, "Config 1: 3 Prep, 1 OR, 5 Recovery")
    analysis = tester.analyze_results(results)
    tester.print_analysis(analysis, "Config 1 (3P-1O-5R)")

    return analysis


def test_config_4p5r():
    """Configuration 2: 4 prep, 1 OR, 5 recovery"""
    config = SimulationConfig(
        num_prep_rooms=4,
        num_operating_rooms=1,
        num_recovery_rooms=5,
        sim_duration=1000.0,
        warmup_period=200.0,
    )

    tester = ScenarioTester(num_replications=20)
    results = tester.run_replications(config, "Config 2: 4 Prep, 1 OR, 5 Recovery")
    analysis = tester.analyze_results(results)
    tester.print_analysis(analysis, "Config 2 (4P-1O-5R)")

    return analysis


def test_config_3p4r():
    """Configuration 3: 3 prep, 1 OR, 4 recovery"""
    config = SimulationConfig(
        num_prep_rooms=3,
        num_operating_rooms=1,
        num_recovery_rooms=4,
        sim_duration=1000.0,
        warmup_period=200.0,
    )

    tester = ScenarioTester(num_replications=20)
    results = tester.run_replications(config, "Config 3: 3 Prep, 1 OR, 4 Recovery")
    analysis = tester.analyze_results(results)
    tester.print_analysis(analysis, "Config 3 (3P-1O-4R)")

    return analysis


def paired_comparison(
    analysis1: Dict,
    analysis2: Dict,
    name1: str,
    name2: str,
    metric: str = "or_blocking_probability",
):
    """
    Perform paired t-test for comparing two configurations
    Assignment asks: "Do any values differ significantly?"
    """
    print(f"\n{'='*70}")
    print(f"🔬 PAIRED COMPARISON: {name1} vs {name2}")
    print(f"   Metric: {metric}")
    print(f"{'='*70}")

    # Get raw data (same seeds used, so paired)
    if metric == "or_blocking_probability":
        data1 = analysis1["raw_blocking"]
        data2 = analysis2["raw_blocking"]
        unit = ""
    elif metric == "prep_queue_length":
        data1 = analysis1["raw_prep_queue"]
        data2 = analysis2["raw_prep_queue"]
        unit = " patients"
    else:  # throughput_time
        data1 = analysis1["raw_throughput"]
        data2 = analysis2["raw_throughput"]
        unit = " min"

    # Compute differences
    differences = [d1 - d2 for d1, d2 in zip(data1, data2)]

    mean_diff = statistics.mean(differences)
    std_diff = statistics.stdev(differences)
    n = len(differences)

    # t-statistic for paired test
    t_stat = mean_diff / (std_diff / np.sqrt(n))

    # t-critical for n=20, df=19, two-tailed 95% CI
    t_critical = 2.093

    # Confidence interval for difference
    margin = t_critical * (std_diff / np.sqrt(n))
    ci_lower = mean_diff - margin
    ci_upper = mean_diff + margin

    is_significant = abs(t_stat) > t_critical

    print(f"\nMean difference: {mean_diff:.4f}{unit}")
    print(f"95% CI for difference: [{ci_lower:.4f}, {ci_upper:.4f}]{unit}")
    print(f"Std Dev of differences: {std_diff:.4f}")
    print(f"t-statistic: {t_stat:.4f}")
    print(f"t-critical (α=0.05, two-tailed): ±{t_critical}")

    if is_significant:
        print(
            f"✅ SIGNIFICANT: Configurations differ significantly (|t| > {t_critical})"
        )
        print(f"   → {name1} vs {name2} show a statistically significant difference")
    else:
        print(
            f"❌ NOT SIGNIFICANT: No significant difference detected (|t| ≤ {t_critical})"
        )
        print(f"   → Cannot conclude that {name1} and {name2} differ")

    print(f"{'='*70}\n")

    return {
        "mean_difference": mean_diff,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "t_statistic": t_stat,
        "t_critical": t_critical,
        "is_significant": is_significant,
    }


def run_all_scenarios():
    """Main function to run all required scenarios"""
    print("\n" + "=" * 70)
    print("🚀 ASSIGNMENT 3 - SURGERY SIMULATION")
    print("   20 replications × 1000 time units × 3 configurations")
    print("=" * 70)

    # Run all three configurations
    config_3p5r = test_config_3p5r()
    config_4p5r = test_config_4p5r()
    config_3p4r = test_config_3p4r()

    # Comparative summary
    print("\n" + "=" * 70)
    print("📈 COMPARATIVE SUMMARY")
    print("=" * 70)

    scenarios = [
        ("3P-1O-5R", config_3p5r),
        ("4P-1O-5R", config_4p5r),
        ("3P-1O-4R", config_3p4r),
    ]

    print(
        f"\n{'Configuration':<15} {'Throughput (min)':<20} {'OR Blocking':<20} {'Prep Queue':<15}"
    )
    print("-" * 70)

    for name, analysis in scenarios:
        tt = analysis["throughput_time"]
        bp = analysis["or_blocking_probability"]
        pq = analysis["prep_queue_length"]

        print(
            f"{name:<15} {tt['mean']:6.2f} ± {tt['margin_of_error']:5.2f}    "
            f"{bp['mean']:6.4f} ± {bp['margin_of_error']:6.4f}    "
            f"{pq['mean']:5.2f} ± {pq['margin_of_error']:4.2f}"
        )

    # Paired comparisons (as required by assignment)
    print("\n" + "=" * 70)
    print("📊 STATISTICAL COMPARISONS (Paired t-tests)")
    print("=" * 70)

    # Compare 3p5r vs 4p5r (effect of more prep rooms)
    paired_comparison(
        config_3p5r, config_4p5r, "3P-5R", "4P-5R", "or_blocking_probability"
    )
    paired_comparison(config_3p5r, config_4p5r, "3P-5R", "4P-5R", "prep_queue_length")

    # Compare 3p5r vs 3p4r (effect of fewer recovery rooms)
    paired_comparison(
        config_3p5r, config_3p4r, "3P-5R", "3P-4R", "or_blocking_probability"
    )
    paired_comparison(config_3p5r, config_3p4r, "3P-5R", "3P-4R", "prep_queue_length")

    # Save results
    results_data = {
        "config_3p5r": {k: v for k, v in config_3p5r.items() if "raw_" not in k},
        "config_4p5r": {k: v for k, v in config_4p5r.items() if "raw_" not in k},
        "config_3p4r": {k: v for k, v in config_3p4r.items() if "raw_" not in k},
    }

    with open("results/assignment3_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    print("\n✅ Results saved to: results/assignment3_results.json")
    print("\n" + "=" * 70)
    print("✨ SIMULATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_all_scenarios()
