# C1169: AXM Residual Closed — ~27% Is Genuine Design Freedom

**Tier:** 2
**Scope:** B, folio, AXM residual, closure
**Phase:** RESIDUAL_FREEDOM_CHARACTERIZATION (Phase 417)
**Depends on:** C1035, C1168, C458, C980, C976

## Statement

The ~27% AXM self-transition variance unexplained by the dual boundary model (R²=0.852, LOO=0.732, C1168) is genuinely irreducible design freedom. A 5-test exhaustive battery — 23 candidate predictors (linear scan with Holm-Bonferroni), random forest nonlinearity detection (500 trees, 200-permutation test), spatial autocorrelation (lag-1 in manuscript order, 1000 permutations), design freedom profiling (Shapiro-Wilk, C458 asymmetry, regime homogeneity), and gated OLS extension — finds zero signal. No predictor survives multiple testing correction, RF CV R²=-0.14 (permutation p=0.375), residuals are spatially random (lag-1=0.102, p=0.378), and residuals show no regime structure (Kruskal-Wallis p=0.998). The AXM residual decomposition program (Phases 412-417) is closed.

## Evidence

### Current Best Model (Phase 416 dual boundary)
| Component | Value |
|-----------|-------|
| Model | C1035 baseline + entry_div + AXM_return + jsd_exit + AXM_departure |
| R² | 0.852 |
| LOO | 0.732 |
| n_folios | 65 |

### Test 1: Univariate Residual Scan
| Metric | Value |
|--------|-------|
| Candidates tested | 23 |
| Uncorrected significant (p<0.05) | 10 |
| Holm-Bonferroni significant | 0 |
| Strongest: e_frac | rho=-0.239, p=0.035 |
| Second: mean_word_length | rho=+0.235, p=0.036 |
| Verdict | UNIVARIATE_CLOSED |

### Test 2: Random Forest Nonlinearity
| Metric | Value |
|--------|-------|
| Features | 23 |
| 5-fold CV R² | -0.141 |
| Permutation null mean | -0.212 |
| Permutation p | 0.375 |
| Verdict | NONLINEAR_CLOSED |

### Test 3: Spatial Autocorrelation
| Metric | Value |
|--------|-------|
| Lag-1 autocorrelation | 0.102 |
| Lag-1 permutation p | 0.378 |
| Lag-2 autocorrelation | -0.092 |
| Runs test p | 0.902 |
| Verdict | SPATIALLY_RANDOM |

### Test 4: Design Freedom Profile
| Metric | Value |
|--------|-------|
| Shapiro-Wilk p | 0.047 (marginal) |
| C458 free dims significant | No |
| C458 clamped dims significant | No |
| Kruskal-Wallis (regime) p | 0.998 |
| Section H residual variance | 5.2× section B (highest) |
| Verdict | SYMMETRIC_FREEDOM |

### Test 5: Exhaustive OLS Extension
| Metric | Value |
|--------|-------|
| Gate | T1=CLOSED, T2=CLOSED → SKIPPED |
| Verdict | RESIDUAL_CLOSED |

### Overall: RESIDUAL_GENUINELY_FREE

## C1035 Residual Trajectory (Complete)

| Phase | Model | R² | LOO | Irreducible |
|-------|-------|----|-----|-------------|
| 412 (C1035) | Baseline (6 predictors) | 0.636 | 0.511 | ~57% |
| 413 | + boundary_div | 0.734 | 0.601 | ~49% |
| 415 | + entry_div + AXM_return | 0.814 | 0.696 | ~32% |
| 416 | + exit features (dual) | 0.852 | 0.732 | ~27% |
| **417** | **Exhaustive closure test** | — | — | **~27% CLOSED** |

## Interpretation

Each program (folio) independently parameterizes ~27% of its AXM operational intensity through mechanisms not captured by any measured structural, morphological, positional, or boundary feature. This is consistent with C458's design asymmetry (hazard clamped, recovery free) but the freedom is symmetric — it does not preferentially occupy recovery dimensions. Programs are independently parameterized (no spatial autocorrelation, no regime residual structure). The 73% explained by the dual boundary model represents the grammar's structural constraints on operational intensity; the 27% represents genuine per-program design freedom.

## Candidate Predictors Tested

paragraph_count, ht_line1_density, gatekeeper_fraction, qo_fraction, vocab_residual, line_count, vocab_size, n_tokens, exit_routing_entropy, gatekeeper_exit_frac, hazard_exit_frac, role_entropy, opener_axm_frac, link_density, ht_density_approx, compound_rate, articulator_rate, mean_word_length, folio_unique_middle_count, n_distinct_middles, k_frac, h_frac, e_frac

## Provenance

- Phase 417: RESIDUAL_FREEDOM_CHARACTERIZATION (5-test battery)
- Script: `phases/RESIDUAL_FREEDOM_CHARACTERIZATION/scripts/residual_freedom_characterization.py`
- Results: `phases/RESIDUAL_FREEDOM_CHARACTERIZATION/results/residual_freedom_characterization.json`
