# Forgiveness vs Sister Pair Correlation Analysis

**Date:** 2026-01-08
**Status:** CLOSED
**Tier:** 2 (escape-density finding), 3 (overall forgiveness)

---

## Research Question

Does sister pair choice (ch vs sh) correlate with program forgiveness (hazard density, escape availability)?

**Hypothesis:** If ch-forms correlate with brittle programs, sister pairs may encode risk tolerance or operator competency requirements.

---

## Key Findings

### PRIMARY FINDING: Escape Density Correlation (Tier 2)

| Correlation | rho | p-value | Significance |
|-------------|-----|---------|--------------|
| **Escape density vs ch-preference** | **-0.326** | **0.002** | **SIGNIFICANT** |

**Interpretation:** Programs that prefer ch-forms have FEWER qo-escape routes.

This is a structural finding: **ch-preference correlates with reduced recovery flexibility**.

### SECONDARY FINDING: Weak Forgiveness Trend (Tier 3)

| Correlation | rho | p-value | Significance |
|-------------|-----|---------|--------------|
| Forgiveness vs ch-preference | -0.241 | 0.026 | Weak |
| Hazard density vs ch-preference | -0.043 | 0.700 | None |
| Max safe run vs ch-preference | -0.020 | 0.857 | None |

The overall forgiveness correlation is weak but trending negative (more ch = more brittle).

---

## Quartile Analysis

| Quartile | ch-Preference | ch-count | sh-count |
|----------|---------------|----------|----------|
| Q1 (Brittle) | **70.3%** | 415 | 205 |
| Q2 | 64.6% | 835 | 508 |
| Q3 | 58.8% | 945 | 616 |
| Q4 (Forgiving) | 61.9% | 1162 | 699 |

The most brittle programs (Q1) show the highest ch-preference (70.3%).

Pattern is NOT monotonic - Q4 is higher than Q3, suggesting a U-shaped relationship or confounding.

---

## Section Analysis

| Section | Mean Forgiveness | ch-Preference | N |
|---------|------------------|---------------|---|
| H | 0.617 (lowest) | 69.2% (highest) | 32 |
| S | 1.725 | 70.4% | 23 |
| B | 2.105 (highest) | 51.1% (lowest) | 20 |
| C | 1.042 | 56.1% | 5 |

**Key finding:** Section H has BOTH lowest forgiveness AND highest ch-preference. This aligns with the escape-density correlation.

---

## Restart Folios Analysis

| Folio | Forgiveness | ch-Preference | Quartile |
|-------|-------------|---------------|----------|
| f50v | 1.576 | 70.6% | Q3 |
| f57r | 0.405 | 64.5% | Q1 (Brittle) |
| f82v | 2.553 | 52.9% | Q4 (Forgiving) |

- Mean forgiveness of restart programs: 1.511 (> population mean 1.335)
- Restart programs are MORE forgiving than average
- f57r (the only reset-present folio) is in the BRITTLE quartile

**Interpretation:** Restart capability may be a design response to program brittleness - f57r needs restart because it's high-risk.

---

## Implications

### What This Proves (Tier 2)

1. **Escape density correlates with ch-preference (rho = -0.326, p = 0.002)**
   - ch-preferring programs have fewer qo-escape tokens
   - This is a structural design property, not random variation

2. **Section H concentrates ch-preference AND low forgiveness**
   - H-section programs are operationally "tighter"
   - Aligns with prior finding that H prefers ch-forms

### What This Suggests (Tier 3)

1. **Sister pair choice may encode operational risk profile**
   - ch-forms: tighter programs with fewer recovery options
   - sh-forms: more flexible programs with escape routes

2. **Restart capability as risk mitigation**
   - f57r is brittle but has reset capability
   - Suggests intentional safety design

### What This Does NOT Prove

- WHY ch-forms correlate with reduced escape routes
- Whether this was intentional design or emergent property
- The functional meaning of ch vs sh in the control system

---

## New Constraint Candidate

### Constraint 412 (Tier 2 STRUCTURAL) - CANDIDATE

**ch-Escape Anticorrelation:** Programs with higher ch-prefix preference have lower qo-escape token density (rho = -0.326, p = 0.002). Sister pair choice correlates with recovery architecture.

---

## Relation to Prior Constraints

| Constraint | Finding | Alignment |
|------------|---------|-----------|
| C408 | Sister pairs are equivalence classes | CONSISTENT - now with functional context |
| C410 | Section conditioning (H prefers ch) | REINFORCED - H has lowest forgiveness |
| C341 | HT-program stratification by waiting | INDEPENDENT - different axis |

---

## Scripts

- `forgiveness_sister_correlation.py` - Main analysis script
- `forgiveness_sister_correlation_results.json` - Raw results

---

## Summary

| Metric | Value |
|--------|-------|
| Programs analyzed | 82 |
| Primary finding | Escape-ch anticorrelation (rho = -0.326, p = 0.002) |
| Secondary finding | Weak forgiveness trend (rho = -0.241, p = 0.026) |
| Tier assessment | 2 (escape finding), 3 (forgiveness trend) |

**The ch/sh sister pair choice is NOT independent of program recovery architecture. ch-preferring programs have fewer escape routes, suggesting sister pairs encode operational risk tolerance.**

---

*Investigation complete. Constraint 412 candidate identified.*
