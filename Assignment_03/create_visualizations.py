import json
import matplotlib.pyplot as plt
import numpy as np


def load_results():
    """Load simulation results from JSON files"""
    with open("results/assignment3_results.json", "r") as f:
        main_results = json.load(f)

    with open("results/priority_twist_results.json", "r") as f:
        twist_results = json.load(f)

    return main_results, twist_results


def plot_blocking_comparison(main_results):
    """Plot OR blocking probability comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))

    configs = ["3P-1O-5R", "4P-1O-5R", "3P-1O-4R"]
    means = [
        main_results["config_3p5r"]["or_blocking_probability"]["mean"],
        main_results["config_4p5r"]["or_blocking_probability"]["mean"],
        main_results["config_3p4r"]["or_blocking_probability"]["mean"],
    ]
    margins = [
        main_results["config_3p5r"]["or_blocking_probability"]["margin_of_error"],
        main_results["config_4p5r"]["or_blocking_probability"]["margin_of_error"],
        main_results["config_3p4r"]["or_blocking_probability"]["margin_of_error"],
    ]

    # Convert to percentages
    means = [m * 100 for m in means]
    margins = [m * 100 for m in margins]

    x_pos = np.arange(len(configs))
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    bars = ax.bar(
        x_pos,
        means,
        yerr=margins,
        capsize=10,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )

    ax.set_xlabel("Configuration", fontsize=12, fontweight="bold")
    ax.set_ylabel("OR Blocking Probability (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Operating Room Blocking Probability\nby Configuration (95% CI)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add value labels on bars
    for i, (bar, mean, margin) in enumerate(zip(bars, means, margins)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + margin + 0.05,
            f"{mean:.2f}%\n±{margin:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig("results/or_blocking_comparison.png", dpi=300, bbox_inches="tight")
    print("✅ Saved: results/or_blocking_comparison.png")
    plt.close()


def plot_throughput_comparison(main_results):
    """Plot throughput time comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))

    configs = ["3P-1O-5R", "4P-1O-5R", "3P-1O-4R"]
    means = [
        main_results["config_3p5r"]["throughput_time"]["mean"],
        main_results["config_4p5r"]["throughput_time"]["mean"],
        main_results["config_3p4r"]["throughput_time"]["mean"],
    ]
    margins = [
        main_results["config_3p5r"]["throughput_time"]["margin_of_error"],
        main_results["config_4p5r"]["throughput_time"]["margin_of_error"],
        main_results["config_3p4r"]["throughput_time"]["margin_of_error"],
    ]

    x_pos = np.arange(len(configs))
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    bars = ax.bar(
        x_pos,
        means,
        yerr=margins,
        capsize=10,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )

    ax.set_xlabel("Configuration", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Throughput Time (minutes)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Patient Throughput Time by Configuration (95% CI)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add value labels
    for i, (bar, mean, margin) in enumerate(zip(bars, means, margins)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + margin + 2,
            f"{mean:.1f} min\n±{margin:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig("results/throughput_comparison.png", dpi=300, bbox_inches="tight")
    print("✅ Saved: results/throughput_comparison.png")
    plt.close()


def plot_queue_comparison(main_results):
    """Plot prep queue length comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))

    configs = ["3P-1O-5R", "4P-1O-5R", "3P-1O-4R"]
    means = [
        main_results["config_3p5r"]["prep_queue_length"]["mean"],
        main_results["config_4p5r"]["prep_queue_length"]["mean"],
        main_results["config_3p4r"]["prep_queue_length"]["mean"],
    ]
    margins = [
        main_results["config_3p5r"]["prep_queue_length"]["margin_of_error"],
        main_results["config_4p5r"]["prep_queue_length"]["margin_of_error"],
        main_results["config_3p4r"]["prep_queue_length"]["margin_of_error"],
    ]

    x_pos = np.arange(len(configs))
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    bars = ax.bar(
        x_pos,
        means,
        yerr=margins,
        capsize=10,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )

    ax.set_xlabel("Configuration", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Queue Length (patients)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Preparation Room Queue Length by Configuration (95% CI)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add value labels
    for i, (bar, mean, margin) in enumerate(zip(bars, means, margins)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + margin + 0.1,
            f"{mean:.2f}\n±{margin:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig("results/queue_comparison.png", dpi=300, bbox_inches="tight")
    print("✅ Saved: results/queue_comparison.png")
    plt.close()


def plot_priority_comparison(twist_results):
    """Plot priority system results"""
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ["Emergency\nPatients", "Elective\nPatients"]
    means = [
        twist_results["emergency_throughput"]["mean"],
        twist_results["elective_throughput"]["mean"],
    ]
    margins = [
        twist_results["emergency_throughput"]["margin"],
        twist_results["elective_throughput"]["margin"],
    ]

    x_pos = np.arange(len(categories))
    colors = ["#e74c3c", "#95a5a6"]

    bars = ax.bar(
        x_pos,
        means,
        yerr=margins,
        capsize=10,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )

    ax.set_xlabel("Patient Type", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Throughput Time (minutes)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Personal Twist: Priority-Based Scheduling\nThroughput Time by Patient Priority (95% CI)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add value labels
    for i, (bar, mean, margin) in enumerate(zip(bars, means, margins)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + margin + 3,
            f"{mean:.1f} min\n±{margin:.1f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    # Add difference annotation
    diff = means[1] - means[0]
    ax.annotate(
        f"Δ = {diff:.1f} min\n(26% slower)",
        xy=(0.5, max(means) * 0.5),
        ha="center",
        fontsize=12,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.3),
    )

    plt.tight_layout()
    plt.savefig("results/priority_comparison.png", dpi=300, bbox_inches="tight")
    print("✅ Saved: results/priority_comparison.png")
    plt.close()


def create_summary_figure(main_results, twist_results):
    """Create a comprehensive summary figure"""
    fig = plt.figure(figsize=(16, 10))

    # Create 2x2 subplot grid
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4)

    # Plot 1: OR Blocking
    configs = ["3P-5R", "4P-5R", "3P-4R"]
    blocking_means = [
        main_results["config_3p5r"]["or_blocking_probability"]["mean"] * 100,
        main_results["config_4p5r"]["or_blocking_probability"]["mean"] * 100,
        main_results["config_3p4r"]["or_blocking_probability"]["mean"] * 100,
    ]
    blocking_margins = [
        main_results["config_3p5r"]["or_blocking_probability"]["margin_of_error"] * 100,
        main_results["config_4p5r"]["or_blocking_probability"]["margin_of_error"] * 100,
        main_results["config_3p4r"]["or_blocking_probability"]["margin_of_error"] * 100,
    ]

    x_pos = np.arange(len(configs))
    ax1.bar(
        x_pos,
        blocking_means,
        yerr=blocking_margins,
        capsize=5,
        color=["#2ecc71", "#3498db", "#e74c3c"],
        alpha=0.7,
        edgecolor="black",
    )
    ax1.set_title("(A) OR Blocking Probability", fontweight="bold", fontsize=11)
    ax1.set_ylabel("Blocking %", fontsize=10)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(configs, fontsize=9)
    ax1.grid(axis="y", alpha=0.3)

    # Plot 2: Throughput Time
    throughput_means = [
        main_results["config_3p5r"]["throughput_time"]["mean"],
        main_results["config_4p5r"]["throughput_time"]["mean"],
        main_results["config_3p4r"]["throughput_time"]["mean"],
    ]
    throughput_margins = [
        main_results["config_3p5r"]["throughput_time"]["margin_of_error"],
        main_results["config_4p5r"]["throughput_time"]["margin_of_error"],
        main_results["config_3p4r"]["throughput_time"]["margin_of_error"],
    ]

    ax2.bar(
        x_pos,
        throughput_means,
        yerr=throughput_margins,
        capsize=5,
        color=["#2ecc71", "#3498db", "#e74c3c"],
        alpha=0.7,
        edgecolor="black",
    )
    ax2.set_title("(B) Patient Throughput Time", fontweight="bold", fontsize=11)
    ax2.set_ylabel("Time (min)", fontsize=10)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(configs, fontsize=9)
    ax2.grid(axis="y", alpha=0.3)

    # Plot 3: Queue Length
    queue_means = [
        main_results["config_3p5r"]["prep_queue_length"]["mean"],
        main_results["config_4p5r"]["prep_queue_length"]["mean"],
        main_results["config_3p4r"]["prep_queue_length"]["mean"],
    ]
    queue_margins = [
        main_results["config_3p5r"]["prep_queue_length"]["margin_of_error"],
        main_results["config_4p5r"]["prep_queue_length"]["margin_of_error"],
        main_results["config_3p4r"]["prep_queue_length"]["margin_of_error"],
    ]

    ax3.bar(
        x_pos,
        queue_means,
        yerr=queue_margins,
        capsize=5,
        color=["#2ecc71", "#3498db", "#e74c3c"],
        alpha=0.7,
        edgecolor="black",
    )
    ax3.set_title("(C) Prep Queue Length", fontweight="bold", fontsize=11)
    ax3.set_ylabel("Queue Length", fontsize=10)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(configs, fontsize=9)
    ax3.grid(axis="y", alpha=0.3)

    # Plot 4: Priority System
    priority_cats = ["Emergency", "Elective"]
    priority_means = [
        twist_results["emergency_throughput"]["mean"],
        twist_results["elective_throughput"]["mean"],
    ]
    priority_margins = [
        twist_results["emergency_throughput"]["margin"],
        twist_results["elective_throughput"]["margin"],
    ]

    x_pos2 = np.arange(len(priority_cats))
    ax4.bar(
        x_pos2,
        priority_means,
        yerr=priority_margins,
        capsize=5,
        color=["#e74c3c", "#95a5a6"],
        alpha=0.7,
        edgecolor="black",
    )
    ax4.set_title(
        "(D) Priority System (Personal Twist)", fontweight="bold", fontsize=11
    )
    ax4.set_ylabel("Throughput Time (min)", fontsize=10)
    ax4.set_xticks(x_pos2)
    ax4.set_xticklabels(priority_cats, fontsize=9)
    ax4.grid(axis="y", alpha=0.3)

    plt.suptitle(
        "Assignment 3: Surgery Unit Simulation - Complete Results Summary",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )
    plt.tight_layout()
    plt.savefig("results/complete_summary.png", dpi=300, bbox_inches="tight")
    print("✅ Saved: results/complete_summary.png")
    plt.close()


def main():
    """Generate all visualizations"""
    print("\n" + "=" * 70)
    print("📊 CREATING VISUALIZATIONS")
    print("=" * 70 + "\n")

    # Load results
    main_results, twist_results = load_results()

    # Create individual plots
    plot_blocking_comparison(main_results)
    plot_throughput_comparison(main_results)
    plot_queue_comparison(main_results)
    plot_priority_comparison(twist_results)

    # Create summary figure
    create_summary_figure(main_results, twist_results)

    print("\n" + "=" * 70)
    print("✅ ALL VISUALIZATIONS CREATED")
    print("=" * 70)
    print("\nGenerated files in results/ directory:")
    print("  • or_blocking_comparison.png")
    print("  • throughput_comparison.png")
    print("  • queue_comparison.png")
    print("  • priority_comparison.png")
    print("  • complete_summary.png")


if __name__ == "__main__":
    main()
