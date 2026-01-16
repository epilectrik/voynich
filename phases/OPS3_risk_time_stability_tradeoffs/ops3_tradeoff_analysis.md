# Phase OPS-3: Risk-Time-Stability Tradeoff Analysis

**Date:** 2026-01-15

---

## 1. Regime Tradeoff Summary

| Regime | N | Time Cost | Risk | Stability | Pareto |
|--------|---|-----------|------|-----------|--------|
| REGIME_1 | 31 | 0.600 +/- 0.078 | 0.529 +/- 0.046 | 0.450 +/- 0.059 | PARETO_EFFICIENT |
| REGIME_2 | 11 | 0.545 +/- 0.142 | 0.341 +/- 0.055 | 0.425 +/- 0.084 | PARETO_EFFICIENT |
| REGIME_3 | 16 | 0.347 +/- 0.109 | 0.594 +/- 0.056 | 0.350 +/- 0.079 | DOMINATED |
| REGIME_4 | 25 | 0.342 +/- 0.079 | 0.455 +/- 0.042 | 0.359 +/- 0.085 | PARETO_EFFICIENT |

*Higher Time Cost = slower operation*
*Higher Risk = more exposure to hazards*
*Higher Stability = better resilience/recoverability*

---

## 2. Pareto Front Analysis

**Objective:** Minimize Time, Minimize Risk, Maximize Stability

**Pareto-Efficient Regimes:** REGIME_1, REGIME_2, REGIME_4
**Dominated Regimes:** REGIME_3

### Risk vs Time Plane

```
Risk (higher=worse)
  ^
  |             REGIME_1
  |           REGIME_2
  |       REGIME_3
  |       REGIME_4
  +--------------------> Time (higher=slower)
```

### Risk vs Stability Plane

```
Stability (higher=better)
  ^
  |           REGIME_1
  |       REGIME_2
  |            REGIME_3
  |          REGIME_4
  +--------------------> Risk (higher=worse)
```

---

## 3. Regime Separation (Cohen's d)

Effect size interpretation: |d|<0.2=negligible, 0.2-0.5=small, 0.5-0.8=medium, >0.8=large

### TIME Axis

| Comparison | Cohen's d | Effect |
|------------|-----------|--------|
| REGIME 1 vs REGIME 2 | +0.543 | medium |
| REGIME 1 vs REGIME 3 | +2.765 | large |
| REGIME 1 vs REGIME 4 | +3.240 | large |
| REGIME 2 vs REGIME 3 | +1.543 | large |
| REGIME 2 vs REGIME 4 | +1.927 | large |
| REGIME 3 vs REGIME 4 | +0.052 | negligible |

### RISK Axis

| Comparison | Cohen's d | Effect |
|------------|-----------|--------|
| REGIME 1 vs REGIME 2 | +3.791 | large |
| REGIME 1 vs REGIME 3 | -1.278 | large |
| REGIME 1 vs REGIME 4 | +1.669 | large |
| REGIME 2 vs REGIME 3 | -4.378 | large |
| REGIME 2 vs REGIME 4 | -2.390 | large |
| REGIME 3 vs REGIME 4 | +2.852 | large |

### STABILITY Axis

| Comparison | Cohen's d | Effect |
|------------|-----------|--------|
| REGIME 1 vs REGIME 2 | +0.375 | small |
| REGIME 1 vs REGIME 3 | +1.477 | large |
| REGIME 1 vs REGIME 4 | +1.255 | large |
| REGIME 2 vs REGIME 3 | +0.892 | large |
| REGIME 2 vs REGIME 4 | +0.761 | medium |
| REGIME 3 vs REGIME 4 | -0.106 | negligible |

---

## 4. Internal Consistency Check

*Criterion: Within-regime variance < Between-regime variance*

| Axis | Within Var | Between Var | Ratio | Status |
|------|------------|-------------|-------|--------|
| TIME | 0.0111 | 0.0134 | 0.824 | PASS |
| RISK | 0.0025 | 0.0090 | 0.276 | PASS |
| STABILITY | 0.0060 | 0.0018 | 3.240 | FAIL |

---

## 5. Cross-Checks

| Check | Result | Status |
|-------|--------|--------|
| Aggressive regimes = high-risk, low-time | Risk-Time r=-0.340 | PASS |
| Conservative regimes = low-risk, high-time | REGIME_2 time=0.545 | PASS |
| Restart-capable = high stability | Restart=0.589 vs Other=0.393 | PASS |
| No regime dominates all axes | Best: T=REGIME_4, R=REGIME_2, S=REGIME_1 | PASS |

---

## 6. Regime Switching Pressures

*Non-semantic directional tendencies derived from tradeoff position*

### REGIME_1

**Coordinates:** Time=0.600, Risk=0.529, Stability=0.450

- high time cost -> pressure toward faster regimes if time-constrained

### REGIME_2

**Coordinates:** Time=0.545, Risk=0.341, Stability=0.425

- low risk -> tolerable for risk-averse conditions

### REGIME_3

**Coordinates:** Time=0.347, Risk=0.594, Stability=0.350

- low time cost -> efficient for throughput-critical conditions
- low stability -> pressure toward more resilient regimes

### REGIME_4

**Coordinates:** Time=0.342, Risk=0.455, Stability=0.359

- low time cost -> efficient for throughput-critical conditions
- low stability -> pressure toward more resilient regimes

---

> **"OPS-3 is complete. Risk-time-stability tradeoffs between control-strategy regimes 
> have been quantified using purely operational metrics. No semantic or historical 
> interpretation has been introduced."**

*Generated: 2026-01-15T23:47:11.193906*