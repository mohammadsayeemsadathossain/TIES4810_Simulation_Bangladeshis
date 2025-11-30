# TIES4810 Assignment 3: Surgery Unit Simulation

Process-based discrete event simulation using SimPy to analyze operating room blocking and resource allocation in a surgery unit.

## Quick Start

```bash
# Install dependencies
pip install simpy numpy matplotlib

# Run main simulation (3 configurations × 20 replications)
python test_scenarios.py

# Run personal twist (priority scheduling)
python personal_twist.py

# Generate visualizations
python create_visualizations.py
```

## Project Structure

- `surgery_simulation.py` - Core simulation model with blocking mechanism
- `test_scenarios.py` - Main experiment runner with statistical analysis
- `personal_twist.py` - Priority-based scheduling extension
- `create_visualizations.py` - Matplotlib visualization generator
- `results/` - Output JSON data and PNG visualizations

## Key Features

✅ Correct blocking mechanism (prep released at surgery start, OR released after recovery secured)  
✅ Queue monitoring (sampled every 10 time units)  
✅ Statistical hypothesis testing (paired t-tests with 95% CI)  
✅ Priority-based scheduling (emergency vs elective patients)  
✅ Publication-quality visualizations

## Results Summary

| Configuration            | OR Blocking  | Avg Throughput | Prep Queue    |
| ------------------------ | ------------ | -------------- | ------------- |
| 3P-1O-5R (baseline)      | 0.28%        | 155.90 min     | 2.04 patients |
| 4P-1O-5R (more prep)     | 0.27%        | 153.97 min     | 1.49 patients |
| 3P-1O-4R (less recovery) | **1.32%** ⚠️ | 160.04 min     | 2.26 patients |

**Key Finding:** Reducing recovery capacity significantly increases OR blocking (p<0.05)

## Personal Twist: Priority System

Emergency patients: **125.55 min** (±19.51)  
Elective patients: **170.14 min** (±43.30)  
**→ 44.59 min faster for emergencies (26% improvement)**

## Author

Mohammad Sayeem Sadat Hossain  
Group: Bangladeshis  
Course: TIES4810 Simulation  
University of Jyväskylä
