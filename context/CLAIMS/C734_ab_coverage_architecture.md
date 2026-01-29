# C734: A-B Coverage Architecture

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

The C502.a three-axis filtering cascade applied per-A-folio to B vocabulary produces a **low-coverage, A-dominated routing architecture**. A single A folio makes only 26.1% of any B folio's vocabulary legal on average. Which A folio is active explains 72.0% of coverage variance; which B folio is the target explains only 18.1%.

### Coverage Matrix (114 A x 82 B)

| Metric | Value |
|--------|-------|
| Mean coverage | 0.2613 |
| Median coverage | 0.2451 |
| Min coverage | 0.0260 |
| Max coverage | 0.7927 |
| Std | 0.1085 |

### Variance Decomposition

| Source | Variance | % of Total |
|--------|----------|------------|
| A folio (row effect) | 0.008475 | 72.0% |
| B folio (column effect) | 0.002133 | 18.1% |
| Residual (interaction) | 0.001161 | 9.9% |
| Total | 0.011769 | 100% |

### Per-A-Folio Coverage

| Metric | Value |
|--------|-------|
| Mean of A-folio means | 0.2613 |
| Std of A-folio means | 0.0921 |
| Min A folio (f5v) | 0.1077 |
| Max A folio (f58v) | 0.6257 |
| Range | 0.5179 |

### Per-B-Folio Coverage

| Metric | Value |
|--------|-------|
| Mean of B-folio means | 0.2613 |
| Std of B-folio means | 0.0462 |
| Min B folio (f57r) | 0.1791 |
| Max B folio (f95r2) | 0.3905 |
| Range | 0.2114 |

## Implication

A folios are not interchangeable. The identity of the active A folio is the dominant factor determining which B vocabulary is accessible. This is a routing architecture: different A folios open different corridors through B's execution space. The A-B relationship is structured, not flat.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py`
- Depends: C502.a (three-axis filtering), C703 (folio-level PP pooling)
- Extends: C384 (B vocabulary sharing at aggregate level is 99.8%, but per-A-folio coverage is only 26.1%)
