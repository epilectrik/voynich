# C624: Hazard Boundary Architecture

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** HAZARD_CLASS_VULNERABILITY

## Statement

All 17 forbidden transitions have **zero actual occurrences** in the Currier B corpus (confirmed forbidden). Near-miss transitions (same class pair, different tokens) total only 114 instances. FL and CC roles are over-represented as buffers between hazard zones (enrichment 1.55x and 1.50x respectively), while AX is under-represented (0.84x). Hazard classes themselves self-buffer at high rates (class 7: 2.23x, class 9: 1.96x). Of 1024 possible hazard-token pairs, only 265 are observed and 17 are forbidden, yielding a **selectivity ratio of 6.4%** -- forbidden transitions are highly specific within their class pairs.

## Evidence

### Forbidden Transition Confirmation

| Metric | Value |
|--------|-------|
| Total forbidden pairs | 17 |
| Actual occurrences | 0 |
| Near-miss transitions | 114 |
| Most common near-miss | s -> aiin (class 23->9): 18 |

### Buffer Class Analysis

| Role | Buffer% | Overall% | Enrichment |
|------|---------|----------|------------|
| FL | 10.4% | 6.7% | 1.55x |
| CC | 6.9% | 4.6% | 1.50x |
| FQ | 21.0% | 18.0% | 1.17x |
| EN | 40.1% | 44.9% | 0.89x |
| AX | 21.6% | 25.8% | 0.84x |

Chi-squared (buffer role vs overall): chi2=23.3, df=4. Total buffer positions: 481.

Top individual buffers: class 33 (EN, 52 positions), class 32 (EN, 45), class 9 (FQ-HAZ, 37), class 7 (FL-HAZ, 29).

### Folio-Level Hazard Density

| Metric | Value |
|--------|-------|
| Mean density | 25.1% |
| Highest | f33v: 43.0% |
| Lowest | f80r: 14.3% |
| Regime predicts density | No (Kruskal-Wallis p=0.26) |
| Density vs folio size | Spearman rho=-0.30 |

### Selectivity Ratio

| Metric | Value |
|--------|-------|
| Hazard-class tokens | 32 |
| Possible pairs (N x N) | 1024 |
| Observed unique pairs | 265 |
| Forbidden pairs | 17 |
| Selectivity (of observed) | 6.4% |
| Selectivity (of possible) | 1.7% |

Most forbidden class pairs also have many allowed transitions: c31->c8 has 2 forbidden and 11 observed pairs; c8->c9 has 2 forbidden and 2 observed.

## Interpretation

The hazard system operates as a sparse, token-specific lookup table embedded in a dense transition network. Hazard classes are not isolated -- they self-buffer and are surrounded by normal traffic. The 6.4% selectivity ratio means that within hazard class-pairs, 93.6% of transitions are permitted. Forbidden transitions are the exception, not the rule, within hazard zones. Buffer enrichment of FL and CC suggests these roles serve as structural separators, consistent with FL's role as flow operators and CC's role as core control.

Regime does not predict hazard density (p=0.26), confirming that hazard topology is a global grammar property, not a regime-specific feature.

## Extends

- **C109**: Confirms zero-occurrence enforcement of all 17 forbidden transitions
- **C554**: Hazard density is 25.1% of B tokens, consistent with 93% of lines containing hazard classes

## Related

C109, C541, C542, C554, C601, C622, C623
