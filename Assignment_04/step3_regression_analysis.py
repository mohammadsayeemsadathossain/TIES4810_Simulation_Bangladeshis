"""
Assignment 4 - Step 3: Regression Analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from scipy import stats


class RegressionAnalysis:
    """Regression analysis for factorial experiments"""

    def __init__(self, results_file="results/experiment_results.json"):
        with open(results_file, "r") as f:
            self.results = json.load(f)

        self.X, self.y, self.run_ids = self._prepare_data()

    def _prepare_data(self):
        """Prepare design matrix and responses"""
        n = len(self.results)
        X = np.ones((n, 7))  # Intercept + 6 factors
        y = np.zeros(n)
        run_ids = []

        for i, result in enumerate(self.results):
            factors = result["factors"]
            X[i, 1] = factors["A"]
            X[i, 2] = factors["B"]
            X[i, 3] = factors["C"]
            X[i, 4] = factors["D"]
            X[i, 5] = factors["E"]
            X[i, 6] = factors["F"]
            y[i] = result["avg_queue_length"]
            run_ids.append(result["run"])

        return X, y, run_ids

    def fit_model(self):
        """Fit regression using least squares"""
        XtX = self.X.T @ self.X
        Xty = self.X.T @ self.y

        if np.linalg.det(XtX) == 0:
            print("⚠️  Warning: Singular matrix!")
            beta = np.linalg.pinv(XtX) @ Xty
        else:
            beta = np.linalg.inv(XtX) @ Xty

        return beta

    def calculate_statistics(self, beta):
        """Calculate regression statistics"""
        n = len(self.y)
        p = len(beta)

        y_pred = self.X @ beta
        residuals = self.y - y_pred

        SSR = np.sum(residuals**2)
        SST = np.sum((self.y - np.mean(self.y)) ** 2)
        SSE = SST - SSR

        r_squared = 1 - (SSR / SST) if SST > 0 else 0
        adj_r_squared = 1 - ((SSR / (n - p)) / (SST / (n - 1))) if n > p else 0

        MSE = SSR / (n - p) if n > p else 0

        # Use pseudo-inverse to handle singular matrix
        try:
            var_beta = MSE * np.linalg.inv(self.X.T @ self.X)
        except np.linalg.LinAlgError:
            # Singular matrix - use pseudo-inverse
            var_beta = MSE * np.linalg.pinv(self.X.T @ self.X)

        se_beta = np.sqrt(
            np.abs(np.diag(var_beta))
        )  # abs() to avoid negative from numerical errors

        t_stats = beta / se_beta
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n - p))

        return {
            "beta": beta,
            "se_beta": se_beta,
            "t_stats": t_stats,
            "p_values": p_values,
            "y_pred": y_pred,
            "residuals": residuals,
            "r_squared": r_squared,
            "adj_r_squared": adj_r_squared,
            "MSE": MSE,
            "SSR": SSR,
            "SSE": SSE,
            "SST": SST,
        }

    def print_results(self, stats_dict):
        """Print regression results"""
        print("\n" + "=" * 100)
        print("REGRESSION ANALYSIS RESULTS")
        print("=" * 100)

        print(f"\nModel: Queue = β₀ + β₁·A + β₂·B + β₃·C + β₄·D + β₅·E + β₆·F + ε")

        print("\n" + "-" * 100)
        print("COEFFICIENTS")
        print("-" * 100)

        factor_names = [
            "Intercept",
            "A (Interarrival)",
            "B (Preparation)",
            "C (Recovery)",
            "D (Prep Rooms)",
            "E (Recovery Rooms)",
            "F (Priority)",
        ]

        coef_data = []
        for i, name in enumerate(factor_names):
            sig = ""
            if stats_dict["p_values"][i] < 0.001:
                sig = "***"
            elif stats_dict["p_values"][i] < 0.01:
                sig = "**"
            elif stats_dict["p_values"][i] < 0.05:
                sig = "*"
            elif stats_dict["p_values"][i] < 0.1:
                sig = "."

            coef_data.append(
                {
                    "Factor": name,
                    "Coefficient": f"{stats_dict['beta'][i]:>8.4f}",
                    "Std Error": f"{stats_dict['se_beta'][i]:>8.4f}",
                    "t-value": f"{stats_dict['t_stats'][i]:>8.3f}",
                    "p-value": f"{stats_dict['p_values'][i]:>8.4f}",
                    "Sig.": sig,
                }
            )

        df_coef = pd.DataFrame(coef_data)
        print(df_coef.to_string(index=False))

        print("\n" + "-" * 100)
        print("Significance: *** p<0.001, ** p<0.01, * p<0.05, . p<0.1")
        print("-" * 100)

        print("\n" + "-" * 100)
        print("MODEL FIT")
        print("-" * 100)
        print(f"  R-squared:     {stats_dict['r_squared']:.4f}")
        print(f"  Adj R-squared: {stats_dict['adj_r_squared']:.4f}")
        print(f"  RMSE:          {np.sqrt(stats_dict['MSE']):.4f}")
        print("-" * 100)

    def plot_diagnostics(self):
        """Create diagnostic plots"""
        beta = self.fit_model()
        stats_dict = self.calculate_statistics(beta)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Actual vs Predicted
        ax = axes[0, 0]
        ax.scatter(self.y, stats_dict["y_pred"], alpha=0.7, s=100)
        min_val = min(self.y.min(), stats_dict["y_pred"].min())
        max_val = max(self.y.max(), stats_dict["y_pred"].max())
        ax.plot(
            [min_val, max_val], [min_val, max_val], "r--", lw=2, label="Perfect fit"
        )
        ax.set_xlabel("Actual Queue Length", fontsize=12)
        ax.set_ylabel("Predicted Queue Length", fontsize=12)
        ax.set_title("Actual vs Predicted", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Residuals vs Fitted
        ax = axes[0, 1]
        ax.scatter(stats_dict["y_pred"], stats_dict["residuals"], alpha=0.7, s=100)
        ax.axhline(y=0, color="r", linestyle="--", lw=2)
        ax.set_xlabel("Fitted Values", fontsize=12)
        ax.set_ylabel("Residuals", fontsize=12)
        ax.set_title("Residuals vs Fitted", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Normal Q-Q plot
        ax = axes[1, 0]
        stats.probplot(stats_dict["residuals"], dist="norm", plot=ax)
        ax.set_title("Normal Q-Q Plot", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Coefficient plot
        ax = axes[1, 1]
        factor_names = ["Int", "A", "B", "C", "D", "E", "F"]
        colors = ["red" if p < 0.05 else "gray" for p in stats_dict["p_values"]]

        y_pos = np.arange(len(beta))
        ax.barh(y_pos, beta, color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(factor_names)
        ax.set_xlabel("Coefficient Value", fontsize=12)
        ax.set_title(
            "Coefficients (Red = Significant p<0.05)", fontsize=14, fontweight="bold"
        )
        ax.axvline(x=0, color="k", linestyle="-", lw=1)
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        plt.savefig("figures/regression_diagnostics.png", dpi=300, bbox_inches="tight")
        print("\n✅ Plot saved: figures/regression_diagnostics.png")
        plt.close()

        return stats_dict


def main():
    """Run regression analysis"""
    print("\n" + "=" * 100)
    print("ASSIGNMENT 4 - REGRESSION ANALYSIS")
    print("=" * 100)

    analysis = RegressionAnalysis()
    beta = analysis.fit_model()
    stats_dict = analysis.calculate_statistics(beta)

    analysis.print_results(stats_dict)
    stats_dict = analysis.plot_diagnostics()

    print("\n" + "=" * 100)
    print("REGRESSION COMPLETE!")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
