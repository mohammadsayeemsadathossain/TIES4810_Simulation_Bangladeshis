# Assignment 04

**Course:** TIES4810 Simulation  
**Assignment:** Experiment design and metamodelling 
<br>**Author:** Md Ashraful Alam 
<br>**Institution:** University of Jyväskylä 

# Hospital Surgery Unit Simulation Study

This project studies congestion behavior in a hospital surgery unit using **discrete-event simulation**, **designed experiments**, and **statistical modeling**.  
The primary performance metric is the **average entrance queue length** before preparation.

---

## Key Takeaways (Executive Summary)

- **Arrival rate and arrival variability are the dominant drivers** of congestion.
- **Preparation capacity has the largest impact** on entrance queue length.
- **Recovery capacity has minimal effect** on entrance congestion.
- **Uniform arrivals significantly reduce queues** compared to exponential arrivals.
- The system exhibits **strong serial correlation**, confirming long memory effects.
- A regression model explains **94–95% of variance**, validating the experimental design.

---

## STEP 1 — Data Generation & Experimental Design

### 1.1 Simulation Model Overview

The hospital system is modeled as an **event-based discrete-event simulation** with the following flow:

1. Patient arrival
2. Preparation
3. Operation (OR)
4. Recovery
5. Exit

Resources:
- Preparation units
- Operating rooms
- Recovery units

The model explicitly handles:
- Blocking between OR and recovery
- Warm-up removal
- Independent replications
- Optional variability and distribution changes

---

### 1.2 Experimental Factors

A **full factorial design (64 configurations)** was used with the following factors:

| Factor | Levels |
|------|-------|
| Arrival mean | {22.5, 25.0} |
| Prep units | {3, 4} |
| Recovery units | {4, 5} |
| Arrival distribution | {Exponential, Uniform} |
| Prep distribution | {Exponential, Uniform} |
| Recovery distribution | {Exponential, Uniform} |

Each configuration was simulated with:
- 20 replications
- 200 time units warm-up
- 1000 time units observation window

---

### 1.3 Output Dataset

Each row in the dataset represents **one configuration**, aggregated across replications.

Columns include:
- `avg_queue` (mean entrance queue length)
- `avg_block` (probability OR is blocked)
- Factor levels (arrival mean, capacities, distributions)

**Table 1** summarizes the dataset.

> **Table 1 — Summary statistics of main outputs**
|	    | avg_queue	| avg_block |
|-------|-----------|-----------|
| count	|64.000000	|64.000000  |
| mean	|1.109516	|0.009542   |
| std	|0.904116	|0.007911   |
| min	|0.041828	|0.000168   |
| 25%	|0.327171	|0.002599   |
| 50%	|0.933896	|0.006370   |
| 75%	|1.739680	|0.016041   |
| max	|3.123512	|0.026620   |



---

## STEP 2 — Data Sanity Checks

The dataset was validated before analysis:

- `avg_queue` is continuous and non-negative
- `avg_block` lies strictly in `[0, 1]`
- No missing values
- Exactly **64 rows** confirmed

![Distribution of average entrance queue length](https://github.com/mohammadsayeemsadathossain/TIES4810_Simulation_Bangladeshis/tree/main/Assignment_04/event_base/images/Figure_1_-_Distribution_of_Average_Queue.png)
> **Figure 1 — Distribution of average entrance queue length**  
<br>
![Distribution of OR blocking probability](https://github.com/mohammadsayeemsadathossain/TIES4810_Simulation_Bangladeshis/tree/main/Assignment_04/event_base/images/Figure_2_-_Distribution_of_OR_blocking_probability.png)

> **Figure 2 — Distribution of OR blocking probability**


---

## STEP 3 — Serial Correlation Analysis

### 3.1 Motivation

Simulation outputs are time-dependent. Before applying statistical inference, we must assess **temporal dependence**.

### 3.2 Method

For a fixed configuration:
- Multiple long simulations were run
- Entrance queue length sampled at fixed intervals
- Lag-1 autocorrelation computed for each run

---

### 3.3 Results

- **Mean lag-1 autocorrelation ≈ 0.87**
- Individual runs ranged from **0.70 to 0.96**

![Figure 3 — Lag-1 autocorrelation across independent runs](https://github.com/mohammadsayeemsadathossain/TIES4810_Simulation_Bangladeshis/tree/main/Assignment_04/event_base/images/Figure_3_-_Lag-1_autocorrelation_across_independent_runs.png)
> **Figure 3 — Lag-1 autocorrelation across independent runs**  
<br>
![Figure 4 — Example queue length time series](https://github.com/mohammadsayeemsadathossain/TIES4810_Simulation_Bangladeshis/tree/main/Assignment_04/event_base/images/Figure_4_-_Example_queue_length_time_series.png)

> **Figure 4 — Example queue length time series**

---

### 3.4 Interpretation

The system exhibits **strong serial correlation**, indicating:

- Long memory effects
- Slow decay to equilibrium
- Justification for:
  - Warm-up removal
  - Independent replications
  - Time-averaged statistics

This behavior is typical of **high-utilization queueing systems**.

---

## STEP 4 — Regression Modeling

### 4.1 Main Effects Model

A linear regression model was fit using all 64 configurations.

- **R² = 0.940**
- **Adjusted R² = 0.934**

Significant predictors:
- Arrival mean
- Number of prep units
- Arrival distribution
- Prep distribution (marginal)

> **Table 2 — Regression coefficients (main effects)**

                            OLS Regression Results                            

|                   |                    |                          |              |
|-------------------|--------------------|--------------------------|--------------|
|Dep. Variable:     |         avg_queue  | R-squared:               |        0.940 |
|Model:             |               OLS  | Adj. R-squared:          |        0.934 |
|Method:            |     Least Squares  | F-statistic:             |        149.9 |
|Date:              |  Tue, 16 Dec 2025  | Prob (F-statistic):      |     4.98e-33 |
|Time:              |          20:13:00  | Log-Likelihood:          |       6.3827 |
|No. Observations:  |                64  | AIC:                     |        1.235 |
|Df Residuals:      |                57  | BIC:                     |        16.35 |
|Df Model:          |                 6  |                          |              |
|Covariance Type:   |         nonrobust  |                          |              |
-----

|                   |     coef |    std err |         t |      P>\|t\| |      [0.025 |     0.975] |
|-------------------|----------|------------|-----------|--------------|-------------|------|
|Intercept          |  11.7174 |     0.666  |   17.596  |    0.000     | 10.384      |13.051 |
|arrival_mean       |  -0.2952 |     0.023  |  -12.720  |    0.000     | -0.342      |-0.249 |
|prep_units         |  -0.5628 |     0.058  |   -9.701  |    0.000     | -0.679      |-0.447 |
|rec_units          |  -0.0583 |     0.058  |   -1.006  |    0.319     | -0.175      | 0.058 |
|arrival_dist_unif  |  -1.4656 |     0.058  |  -25.263  |    0.000     | -1.582      |-1.349 |
|prep_dist_unif     |  -0.1159 |     0.058  |   -1.998  |    0.050     | -0.232      | 0.000 |
|rec_dist_unif      |  -0.0227 |     0.058  |   -0.391  |    0.697     | -0.139      | 0.093 |

----

| | | | |
|---|---|---|---|
|Omnibus:                       | 8.608 |  Durbin-Watson:                  | 1.042 |
|Prob(Omnibus):                 | 0.014 |  Jarque-Bera (JB):               | 9.117 |
|Skew:                          | 0.892 |  Prob(JB):                       |0.0105 |
|Kurtosis:                      | 2.518 |  Cond. No.                       |  567. |



---

### 4.2 Interaction Model

Key interaction terms were added:

- Arrival mean × Prep units
- Prep units × Recovery units

Results:
- **R² increased to 0.947**
- Only **arrival × prep** interaction significant

> **Table 3 — Regression coefficients with interactions**

                            OLS Regression Results                            
|   |   |   |   |
|---|---|---|---|
|Dep. Variable:      |         avg_queue |   R-squared:                   |    0.947 |
|Model:              |               OLS |   Adj. R-squared:              |    0.940 |
|Method:             |     Least Squares |   F-statistic:                 |    124.0 |
|Date:               |  Tue, 16 Dec 2025 |   Prob (F-statistic):          | 2.38e-32 |
|Time:               |          20:17:54 |   Log-Likelihood:              |   10.421 |
|No. Observations:   |                64 |   AIC:                         |   -2.843 |
|Df Residuals:       |                55 |   BIC:                         |    16.59 |
|Df Model:           |                 8 |                                |          |
|Covariance Type:    |         nonrobust |                                |          |
-----
|                          | coef     |   std err |         t |   P>\|t\| |     [0.025 |     0.975] |
|--------------------------|----------|-----------|-----------|-----------|------------|------------|
|Intercept                 |  24.8613 |     5.284 |     4.705 |     0.000 |     14.271 |     35.451 |
|arrival_mean              |  -0.8376 |     0.201 |    -4.171 |     0.000 |     -1.240 |     -0.435 |
|prep_units                |  -3.4837 |     1.167 |    -2.985 |     0.004 |     -5.823 |     -1.145 |
|rec_units                 |  -0.1162 |     0.502 |    -0.231 |     0.818 |     -1.122 |      0.890 |
|arrival_dist_unif         |  -1.4656 |     0.055 |   -26.432 |     0.000 |     -1.577 |     -1.355 |
|prep_dist_unif            |  -0.1159 |     0.055 |    -2.090 |     0.041 |     -0.227 |     -0.005 |
|rec_dist_unif             |  -0.0227 |     0.055 |    -0.410 |     0.684 |     -0.134 |      0.088 |
|arrival_mean:prep_units   |   0.1205 |     0.044 |     2.718 |     0.009 |      0.032 |      0.209 |
|prep_units:rec_units      |   0.0129 |     0.111 |     0.116 |     0.908 |     -0.209 |      0.235 |

-----
|   |   |   |   |
|---|---|---|---|
|Omnibus:                       | 1.715 |  Durbin-Watson:              |     0.989 |
|Prob(Omnibus):                 | 0.424 |  Jarque-Bera (JB):           |     1.231 |
|Skew:                          | 0.049 |  Prob(JB):                   |     0.540 |
|Kurtosis:                      | 2.328 |  Cond. No.                   |  2.19e+04 |



---

### 4.3 Interpretation of Effects

- **Arrival rate:** Strongest driver of congestion
- **Prep capacity:** Most effective lever for reducing queues
- **Recovery capacity:** Minimal upstream impact
- **Arrival variability:** Reducing variability is nearly as effective as adding capacity
- **Interactions:** Capacity benefits diminish under heavy load

---

## STEP 5 — Interpretation & Conclusions

### 5.1 System Behavior

The system operates near saturation. Small changes in arrival rate or variability lead to **disproportionate queue growth**, consistent with queueing theory.

### 5.2 Design Insights

- Invest in **preparation capacity first**
- Manage **arrival variability** where possible
- Recovery expansion primarily affects downstream blocking, not entrance congestion

### 5.3 Validity of Results

- Strong explanatory power
- Plausible effect directions
- Consistency with theory
- Robust experimental design

---

## Final Conclusion

This study demonstrates how **simulation + experimental design + regression modeling** can provide actionable insights for complex hospital systems.  
The results highlight that **variability management and upstream capacity decisions** are critical for congestion control in surgery units.
