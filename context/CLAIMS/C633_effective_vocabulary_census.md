# C633: Effective Vocabulary Census

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** INTRA_CLASS_DIVERSITY

## Statement

The Currier B effective functional vocabulary is **56 sub-types** (49 classes + 7 binary splits), compressing 480 classified token types by 8.6x. Role decomposition: FLOW_OPERATOR is most diverse (mean k = 1.50, 2/4 classes heterogeneous), CORE_CONTROL and FREQUENT_OPERATOR are fully uniform (mean k = 1.00). Hazard classes are significantly MORE heterogeneous than non-hazard (50% vs 9%, Fisher p = 0.031), contradicting the hypothesis that the hazard system enforces within-class uniformity. Class size negatively correlates with heterogeneity (rho = -0.321, p = 0.025): smaller classes are more likely to split.

## Evidence

### Role-Level Decomposition

| Role | Classes | Effective | Heterogeneous | Mean k |
|------|---------|-----------|---------------|--------|
| AUXILIARY | 20 | 22 | 2 | 1.10 |
| CORE_CONTROL | 3 | 3 | 0 | 1.00 |
| ENERGY_OPERATOR | 18 | 21 | 3 | 1.17 |
| FLOW_OPERATOR | 4 | 6 | 2 | 1.50 |
| FREQUENT_OPERATOR | 4 | 4 | 0 | 1.00 |

### Hazard vs Non-Hazard

| Metric | Hazard (n=6) | Non-Hazard (n=43) | p-value |
|--------|-------------|-------------------|---------|
| Mean k | 1.50 | 1.09 | 0.0089 |
| Mean JSD | 0.508 | 0.662 | 0.0010 |
| Het rate | 50% (3/6) | 9% (4/43) | 0.0310 |
| Mean size | 5.3 | 10.4 | 0.0217 |

### Correlations

| Variables | Spearman rho | p-value |
|-----------|-------------|---------|
| n_tokens vs k | -0.321 | 0.025 |
| total_freq vs k | -0.101 | 0.490 |
| n_eligible vs k | -0.331 | 0.020 |
| mean_jsd vs k | 0.004 | 0.978 |
| n_tokens vs mean_jsd | 0.372 | 0.008 |

### Key Findings

1. **Size predicts heterogeneity inversely**: smaller classes split more (rho = -0.321, p = 0.025). This is a mechanical effect: small classes with 2-3 members can show discrete behavior differences; large classes average them out.

2. **JSD does NOT predict heterogeneity** (rho = 0.004, p = 0.978). Classes with high mean JSD (0.7+) remain uniform. The divergence is distributed across many dimensions without clean separation.

3. **Hazard classes split more** despite being smaller and having LOWER mean JSD (0.508 vs 0.662). The hazard system appears to contain more functionally distinct roles within its classes.

4. **FLOW_OPERATOR is the most internally diverse role** (mean k = 1.50): both FL_HAZ classes (7, 30) split into 2.

## Interpretation

The 49-class cosurvival system is nearly the effective vocabulary of Currier B. The expansion from 49 to 56 is marginal (14% increase). The high within-class JS divergence (C506.b) represents continuous variation within functional types -- analogous to allophonic variation in phonology rather than discrete phonemic contrast.

The hazard system's higher heterogeneity is noteworthy: the 6 hazard classes contain proportionally more functional distinctions than the 43 non-hazard classes. This may reflect the hazard system's role as a precision mechanism (C622-C624) requiring fine-grained within-class differentiation, particularly in FLOW_OPERATOR classes where directional control ({ar vs al}, {dar,dal,dain,dair vs dam}) demands token-level specificity.

## Extends

- **C506.b**: 73% > 0.4 JS divergence is continuous, not discrete -- 86% of classes remain k=1
- **C629**: Class 23's sub-populations (restart vs generalist) do NOT discretely cluster (sil = 0.225, below threshold)
- **C622-C624**: Hazard system's precision is reflected in higher within-class heterogeneity

## Related

C506, C506.a, C506.b, C622, C623, C624, C629, C631, C632
