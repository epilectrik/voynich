# SID-01.1: Section Regime Clustering Test -- VERDICT

**Status:** COMPLETE
**Date:** 2026-01-05
**Test ID:** SID-01.1
**Parent Test:** SID-01 (Global Residue Convergence)
**Objective Class:** Conditional structure reduction

---

## SECTION A: FEATURE SUMMARY

| # | Feature | Description |
|---|---------|-------------|
| 1 | residue_density | Fraction of tokens that are residue |
| 2 | exclusive_fraction | Fraction of residue types unique to this section |
| 3 | prefix_entropy | Shannon entropy of 2-char prefixes |
| 4 | suffix_entropy | Shannon entropy of 2-char suffixes |
| 5 | mean_hazard_distance | Mean distance to nearest hazard token |
| 6 | repetition_rate | Fraction of types appearing >1 time |
| 7 | bigram_entropy | Shannon entropy of character bigrams |
| 8 | type_token_ratio | Vocabulary diversity (types/tokens) |

### Section Feature Values

| Section | Density | Exclusive | PfxEnt | SfxEnt | HazDist | RepRate | BigramEnt | TTR |
|---------|---------|-----------|--------|--------|---------|---------|-----------|-----|
| A | 0.388 | 0.572 | 4.982 | 4.909 | 10.48 | 0.500 | 6.116 | 0.440 |
| B | 0.164 | 0.550 | 5.290 | 4.130 | 4.38 | 0.617 | 5.867 | 0.201 |
| C | 0.333 | 0.503 | 5.104 | 4.861 | 4.53 | 0.503 | 6.182 | 0.346 |
| H | 0.254 | 0.670 | 5.470 | 4.805 | 7.36 | 0.632 | 6.144 | 0.203 |
| P | 0.250 | 0.600 | 5.193 | 4.895 | 8.36 | 0.481 | 6.296 | 0.397 |
| S | 0.208 | 0.620 | 5.439 | 4.454 | 5.48 | 0.641 | 5.949 | 0.256 |
| T | 0.299 | 0.469 | 5.419 | 4.566 | 8.09 | 0.637 | 6.187 | 0.349 |
| Z | 0.429 | 0.575 | 4.095 | 4.775 | 7.68 | 0.404 | 5.993 | 0.454 |

---

## SECTION B: CLUSTERING RESULTS

### K-Means Results

| k | Silhouette | Stability Mean | Stability Std |
|---|------------|----------------|---------------|
| 2 | 0.292 | 0.505 | 0.101 |
| 3 | 0.218 | 0.570 | 0.156 |
| 4 | 0.140 | 0.569 | 0.180 |
| 5 | 0.164 | 0.579 | 0.121 |
| 6 | 0.121 | 0.458 | 0.062 |
| 7 | 0.084 | 0.250 | 0.000 |

**Best k (silhouette):** 2
**Best k (variance):** 6

---

## SECTION C: REGIME DESCRIPTIONS

### REGIME_0

- **Sections:** A, C, P, T, Z
- **Count:** 5
- **Mean residue density:** 0.340
- **Mean exclusive fraction:** 0.544
- **Mean hazard distance:** 7.83

### REGIME_1

- **Sections:** B, H, S
- **Count:** 3
- **Mean residue density:** 0.209
- **Mean exclusive fraction:** 0.613
- **Mean hazard distance:** 5.74

---

## SECTION D: PREDICTIVE COMPARISON

| Metric | Value |
|--------|-------|
| Section-ID accuracy | 0.361 (+/- 0.003) |
| Cluster-ID accuracy | 0.724 (+/- 0.000) |
| Compression effective | True |

---

## SECTION E: REDUCIBILITY ASSESSMENT

- **Section count:** 8
- **Best k:** 2
- **Best silhouette:** 0.292
- **Reducibility:** PARTIAL_REDUCTION

---

## SECTION F: SID-01.1 VERDICT

```
+-----------------------------------------------------------------------+
|                                                                       |
|   WEAK STRUCTURE ONLY                                               |
|                                                                       |
+-----------------------------------------------------------------------+
```

Partial structure detected, but not sufficient for reliable compression.
Section identity remains the primary conditioning variable.

---

*SID-01.1 Complete.*
