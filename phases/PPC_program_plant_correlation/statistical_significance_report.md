# Statistical Significance Report

> **PURPOSE**: Formal statistical tests of program-plant correlation hypotheses.
> **METHOD**: Chi-square, Fisher's exact, permutation tests with effect sizes.

---

## Test 1: Overall Association (Chi-Square)

### Aggressiveness × Primary Morphology

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| Chi-square | **4.762** | — |
| Degrees of freedom | 6 | — |
| **p-value** | **0.5747** | NOT SIGNIFICANT |
| Cramer's V | 0.315 | Small-medium effect (if real) |
| Required p for significance | <0.05 | — |

**Verdict**: No statistically significant association between program aggressiveness and plant morphology type.

---

### LINK Class × Primary Morphology

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| Chi-square | **2.891** | — |
| Degrees of freedom | 6 | — |
| **p-value** | **0.8224** | NOT SIGNIFICANT |
| Cramer's V | 0.245 | Small effect (if real) |

**Verdict**: No statistically significant association between LINK class and plant morphology type.

---

## Test 2: Specific Hypotheses (Fisher's Exact)

### H1: AGGRESSIVE ↔ ROOT_HEAVY Association

| Statistic | Value |
|-----------|-------|
| Observed co-occurrence | 2 |
| Expected by independence | 2.00 |
| 2×2 contingency | [[2, 6], [4, 12]] |
| **Odds ratio** | **1.000** |
| **p-value (two-tailed)** | **1.0000** |

**Interpretation**: Odds ratio of exactly 1.0 indicates perfect independence. The p-value of 1.0 confirms no association whatsoever.

---

### H2: CONSERVATIVE ↔ FLOWER_DOMINANT Association

| Statistic | Value |
|-----------|-------|
| Observed co-occurrence | 3 |
| Expected by independence | 2.62 |
| 2×2 contingency | [[3, 4], [6, 11]] |
| **Odds ratio** | **1.375** |
| **p-value (two-tailed)** | **1.0000** |

**Interpretation**: Slight enrichment (OR=1.375) but extremely far from significance.

---

## Test 3: Permutation Test

### Non-Parametric Test for AGGRESSIVE + ROOT_HEAVY

| Parameter | Value |
|-----------|-------|
| Observed count | 2 |
| Number of permutations | 10,000 |
| Proportion ≥ observed | 0.6762 |
| **p-value** | **0.6762** |

**Interpretation**: In 67.6% of random shuffles, we see equal or greater co-occurrence. This is consistent with pure chance.

---

## Test 4: Effect Sizes

| Measure | Value | Interpretation |
|---------|-------|----------------|
| Cramer's V (Aggression×Morph) | 0.315 | Small-medium |
| Cramer's V (LINK×Morph) | 0.245 | Small |
| Cohen's w equivalent | ~0.27 | Small |
| Power at n=24, α=0.05 | ~0.35 | UNDERPOWERED |

**Note**: With only 24 observations, statistical power is limited. However, effect sizes are also small, suggesting true absence of association rather than detection failure.

---

## Summary of All p-values

| Test | p-value | Significant? |
|------|---------|--------------|
| Chi-square (Aggression×Morph) | 0.5747 | NO |
| Chi-square (LINK×Morph) | 0.8224 | NO |
| Fisher's (AGGRESSIVE↔ROOT_HEAVY) | 1.0000 | NO |
| Fisher's (CONSERVATIVE↔FLOWER) | 1.0000 | NO |
| Permutation (AGGRESSIVE+ROOT_HEAVY) | 0.6762 | NO |

**All tests return p >> 0.05. No significant associations detected.**

---

## Null Model Comparison

### Expected Distribution Under Independence

If program assignment were random with respect to morphology:

| Morphology | Expected AGGRESSIVE | Expected CONSERVATIVE |
|------------|---------------------|----------------------|
| ROOT_HEAVY | 2.00 | 2.67 |
| FLOWER_DOMINANT | 1.75 | 2.33 |
| LEAFY_HERB | 1.50 | 2.00 |

### Observed vs Null Model

| Combination | Observed | Null Expected | χ² contribution |
|-------------|----------|---------------|-----------------|
| AGG+ROOT | 2 | 2.00 | 0.000 |
| AGG+FLOWER | 1 | 1.75 | 0.321 |
| AGG+LEAFY | 3 | 1.50 | 1.500 |
| CON+ROOT | 2 | 2.67 | 0.167 |
| CON+FLOWER | 3 | 2.33 | 0.192 |
| CON+LEAFY | 2 | 2.00 | 0.000 |

**Largest deviation**: AGGRESSIVE + LEAFY_HERB (3 observed vs 1.5 expected)
- But this is the OPPOSITE of the material-aware hypothesis
- Leafy herbs would not require aggressive processing

---

## Power Analysis

### What effect size could we detect?

| Sample size | Detectable OR (α=0.05, power=0.80) |
|-------------|-----------------------------------|
| n=24 | OR > 5.0 (very large effect) |
| n=50 | OR > 3.0 |
| n=100 | OR > 2.2 |

**Interpretation**: Our sample can only reliably detect very large effects. However, observed odds ratios are near 1.0, suggesting no meaningful effect exists.

---

## Conclusion

### Statistical Verdict

| Criterion | Result |
|-----------|--------|
| Any p < 0.05? | **NO** |
| Any p < 0.10? | **NO** |
| Smallest p-value observed | 0.5747 |
| Effect sizes | Small (Cramer's V < 0.35) |
| Direction consistent? | **NO** (contradictory patterns) |

### Interpretation

The data are **fully consistent with statistical independence** between:
- Program behavior (aggressiveness, LINK density, hazard proximity)
- Plant morphology (root emphasis, flower dominance, leaf structure)

No evidence supports the hypothesis that Voynich programs are systematically paired with specific plant morphology types.

---

*Statistical analysis performed using scipy.stats with n=24 botanical folios.*
