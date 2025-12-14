"""
Assignment 4 - Step 1: Serial Correlation Analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import statistics
from surgery_simulation_a4 import SurgerySimulation, SimulationConfig, DistributionType


def compute_autocorrelation(time_series_list, max_lag=9):
    """Compute autocorrelation for multiple time series"""
    autocorrelations = []

    for lag in range(1, max_lag + 1):
        correlations = []

        for series in time_series_list:
            if len(series) <= lag:
                continue

            x = series[:-lag]
            y = series[lag:]

            if len(x) < 2:
                continue

            try:
                corr = np.corrcoef(x, y)[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
            except:
                pass

        if correlations:
            autocorrelations.append(np.mean(correlations))
        else:
            autocorrelations.append(0.0)

    return autocorrelations


def test_serial_correlation_scenario(
    config, num_replications=10, num_samples=10, sample_interval=100
):
    """Run serial correlation test"""
    print(f"\n{'='*70}")
    print(f"Testing Serial Correlation")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(
        f"  Interarrival: {config.interarrival_dist.value}({config.interarrival_param1})"
    )
    print(
        f"  Preparation: {config.prep_dist.value}({config.prep_param1}, {config.prep_param2})"
    )
    print(
        f"  Prep rooms: {config.num_prep_rooms}, Recovery rooms: {config.num_recovery_rooms}"
    )
    print(f"\nTest parameters:")
    print(f"  Replications: {num_replications}")
    print(f"  Samples per replication: {num_samples}")
    print(f"  Sample interval: {sample_interval} time units")
    print(f"{'='*70}\n")

    all_time_series = []

    for rep in range(num_replications):
        config.random_seed = 42 + rep
        config.warmup_period = sample_interval
        config.sim_duration = config.warmup_period + (num_samples * sample_interval)

        sim = SurgerySimulation(config)
        sim.run()

        queue_samples = sim.queue_length_on_arrivals

        # Downsample to regular intervals
        time_series = []
        valid_patients = [
            p for p in sim.patients if p.arrival_time >= config.warmup_period
        ]

        for i in range(num_samples):
            t_start = config.warmup_period + i * sample_interval
            t_end = t_start + sample_interval

            patients_in_window = [
                p for p in valid_patients if t_start <= p.arrival_time < t_end
            ]

            if patients_in_window:
                avg_queue = statistics.mean(
                    [p.prep_queue_length_on_arrival for p in patients_in_window]
                )
                time_series.append(avg_queue)
            else:
                time_series.append(0.0)

        all_time_series.append(time_series)
        print(
            f"Rep {rep+1:2d}: Queue samples = {[f'{q:.1f}' for q in time_series[:5]]}... (first 5)"
        )

    # Compute autocorrelations
    autocorr = compute_autocorrelation(all_time_series, max_lag=9)

    print(f"\n{'='*70}")
    print(f"Autocorrelation Results")
    print(f"{'='*70}")
    print(f"{'Lag':<6} {'ρ(lag)':<10} {'Interpretation'}")
    print(f"{'-'*70}")

    for lag, corr in enumerate(autocorr, 1):
        interpretation = "None - samples independent"
        if abs(corr) >= 0.7:
            interpretation = "Very Strong - samples highly dependent"
        elif abs(corr) >= 0.5:
            interpretation = "Strong - significant correlation"
        elif abs(corr) >= 0.3:
            interpretation = "Moderate - some correlation"
        elif abs(corr) >= 0.1:
            interpretation = "Weak - minimal correlation"

        print(f"{lag:<6} {corr:>8.4f}  {interpretation}")

    # Assessment
    print(f"\n{'='*70}")
    print(f"Assessment:")
    print(f"{'='*70}")

    max_corr = max([abs(c) for c in autocorr]) if autocorr else 0

    if max_corr > 0.5:
        recommendation = (
            f"⚠️  HIGH CORRELATION DETECTED!\n"
            f"   Maximum |ρ| = {max_corr:.3f}\n"
            f"   Recommendation: Increase sample interval to {sample_interval * 2}"
        )
    elif max_corr > 0.3:
        recommendation = (
            f"⚠️  MODERATE CORRELATION\n"
            f"   Maximum |ρ| = {max_corr:.3f}\n"
            f"   Recommendation: Consider increasing interval to {int(sample_interval * 1.5)}"
        )
    elif max_corr > 0.1:
        recommendation = (
            f"✓  WEAK CORRELATION\n"
            f"   Maximum |ρ| = {max_corr:.3f}\n"
            f"   Current strategy acceptable (interval={sample_interval})"
        )
    else:
        recommendation = (
            f"✓✓ EXCELLENT - NO SIGNIFICANT CORRELATION\n"
            f"   Maximum |ρ| = {max_corr:.3f}\n"
            f"   Samples are independent."
        )

    print(recommendation)
    print(f"{'='*70}\n")

    return {
        "autocorrelations": autocorr,
        "max_correlation": max_corr,
        "time_series": all_time_series,
    }


def plot_autocorrelation(results, save_path="figures/autocorrelation.png"):
    """Plot autocorrelation function"""
    autocorr = results["autocorrelations"]
    lags = list(range(1, len(autocorr) + 1))

    plt.figure(figsize=(10, 6))

    plt.stem(lags, autocorr, basefmt=" ", linefmt="b-", markerfmt="bo")
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)
    plt.axhline(
        y=0.3,
        color="r",
        linestyle="--",
        linewidth=1,
        alpha=0.5,
        label="Moderate threshold (±0.3)",
    )
    plt.axhline(y=-0.3, color="r", linestyle="--", linewidth=1, alpha=0.5)

    plt.xlabel("Lag", fontsize=12)
    plt.ylabel("Autocorrelation ρ", fontsize=12)
    plt.title(
        "Serial Correlation Analysis - Queue Length Samples",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"✅ Autocorrelation plot saved to: {save_path}")
    plt.close()


def run_correlation_tests():
    """Run serial correlation tests"""

    print("\n" + "=" * 70)
    print("ASSIGNMENT 4 - SERIAL CORRELATION ANALYSIS")
    print("=" * 70)
    print("\nTesting HIGH UTILIZATION scenario (likely long memory):")
    print("  - Fast arrivals: exp(22.5)")
    print("  - Slow prep: Unif(30,50)")
    print("  - Limited capacity: 4 prep, 4 recovery")
    print("=" * 70)

    config_high_util = SimulationConfig(
        interarrival_dist=DistributionType.EXPONENTIAL,
        interarrival_param1=22.5,
        prep_dist=DistributionType.UNIFORM,
        prep_param1=30.0,
        prep_param2=50.0,
        recovery_dist=DistributionType.EXPONENTIAL,
        recovery_param1=40.0,
        num_prep_rooms=4,
        num_recovery_rooms=4,
        emergency_probability=0.0,
    )

    print("\n### TEST 1: Sample interval = 100 time units ###")
    results_100 = test_serial_correlation_scenario(
        config_high_util, num_replications=10, num_samples=10, sample_interval=100
    )
    plot_autocorrelation(results_100, "figures/autocorr_interval100.png")

    print("\n### TEST 2: Sample interval = 200 time units ###")
    results_200 = test_serial_correlation_scenario(
        config_high_util, num_replications=10, num_samples=10, sample_interval=200
    )
    plot_autocorrelation(results_200, "figures/autocorr_interval200.png")

    print("\n" + "=" * 70)
    print("RECOMMENDATION FOR MAIN EXPERIMENTS")
    print("=" * 70)

    if results_200["max_correlation"] < 0.3:
        print("\n✅ Use independent replications (different seeds)")
        print(f"   Autocorrelation acceptable: {results_200['max_correlation']:.3f}")
        recommended_interval = 200
    else:
        print("\n⚠️  Need larger intervals or more warmup")
        recommended_interval = 300

    print(f"\n📝 For experiments:")
    print(f"   - Independent replications (different seeds)")
    print(f"   - Warmup: 1000 time units")
    print(f"   - Duration: 5000 time units")
    print("=" * 70 + "\n")

    return recommended_interval


if __name__ == "__main__":
    run_correlation_tests()

    print(f"\n{'='*70}")
    print("SERIAL CORRELATION ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"\nPlots saved:")
    print(f"  - figures/autocorr_interval100.png")
    print(f"  - figures/autocorr_interval200.png")
    print("=" * 70 + "\n")
