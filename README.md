# AIDA Athlete Performance Gradient Analysis

---

## Overview

This repository analyzes longitudinal performance trajectories of competitive freediving athletes using AIDA ranking data.

The study focuses on identifying **performance gradients over time**, specifically:

* Time to peak performance
* Onset of performance decline
* Variation across career lengths

The analysis follows a structured, reproducible workflow combining descriptive statistics and temporal trend extraction.

---

## Research Questions

1. How long does it take athletes to reach peak performance?
2. How soon does performance decline occur after peak?
3. How do these patterns vary with career length?

---

## Methodology

### 1. Data Preparation

* Group observations by athlete
* Sort records chronologically
* Filter incomplete trajectories

### 2. Peak Detection

Peak year is defined as:

* Maximum total points
* Best (lowest) rank

### 3. Decline Detection

Decline onset is defined as the first sustained:

* Decrease in total points
* Increase in rank

### 4. Metric Computation

* **Years Until Peak**
  `Peak Year − First Year`

* **Years Before Decline**
  `Decline Year − Peak Year`

### 5. Aggregation

* Compute mean and median metrics
* Segment by career length bins

---

## Results

### Aggregate Metrics

| Metric               | Mean | Median |
| -------------------- | ---- | ------ |
| Years Until Peak     | 2.20 | 1.00   |
| Years Before Decline | 1.34 | 1.00   |

---

### Career Length Stratification

| Career Length (Years) | Avg Years Until Peak | Avg Years Before Decline |
| --------------------- | -------------------- | ------------------------ |
| 0–5                   | 1.30                 | 1.22                     |
| 6–10                  | 5.84                 | 1.64                     |
| 11–15                 | 10.49                | 1.73                     |
| 16+                   | 15.30                | 2.12                     |

---

## Interpretation

* Peak performance typically occurs early in an athlete’s career
* Decline follows shortly after peak for most athletes
* Longer careers exhibit delayed peak timing
* Median values indicate strong skew toward early peak achievement

---

## Repository Structure

```
.
├── data/
│   ├── raw/                # Original AIDA ranking datasets
│   └── processed/          # Cleaned and derived datasets
├── scripts/
│   ├── data_preparation/   # Cleaning and dataset preparation
│   ├── analysis/           # Descriptive and trend analysis
│   └── modeling/           # Predictive models
├── results/
│   ├── figures/            # Generated plots
│   └── reports/            # Presentation and report files
├── notebooks/              # Optional notebooks
└── README.md

---
```

---

## Limitations

* Career lengths vary significantly across athletes
* Decline definition depends on threshold criteria
* External factors (age, injury, training) are not included
* Results are descriptive, not predictive

---

## Future Work

* Survival analysis for career longevity
* Regression modeling of performance trends
* Inclusion of physiological or demographic variables
* Visualization of performance trajectories

---
