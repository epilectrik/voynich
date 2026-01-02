# Human-Track Ordering vs Risk Analysis

> Structural analysis of folio ordering relative to program risk metrics

---

## TEST 1: Order vs Risk Gradient

**Verdict:** SIGNAL: Non-random risk ordering with monotonic gradient

### Correlations with Folio Order

| Metric | Spearman rho | p-value | Kendall tau | p-value |
|--------|--------------|---------|-------------|----------|
| hazard_density | 0.0761 | 0.4933 | 0.0490 | 0.5120 |
| near_miss_count | 0.4373 | 0.0001 | 0.2980 | 0.0001 |
| risk_score | 0.3918 | 0.0004 | 0.2610 | 0.0005 |
| link_density | -0.0207 | 0.8522 | -0.0174 | 0.8159 |
| recovery_ops | 0.3376 | 0.0024 | 0.2224 | 0.0029 |

### Permutation Test

- Observed risk-order correlation: rho = 0.3918
- Null distribution: mean = 0.0003, std = 0.1101
- Permutation p-value: 0.0004
- Percentile: 100.0%

### Staged Risk (Thirds)

| Segment | Mean Risk Score |
|---------|----------------|
| First third | 1.6894 |
| Middle third | 2.0049 |
| Last third | 2.0729 |

**Pattern:** MONOTONIC INCREASE
