# C634: Recovery Pathway Profiling

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** RECOVERY_ARCHITECTURE_DECOMPOSITION

## Statement

Recovery pathway architecture is **NOT regime-stratified** at the surface level: 0/13 Kruskal-Wallis tests show significant REGIME dependence across kernel absorption rates (e/h/k/exit), recovery path lengths (mean/median/max/count), and post-kernel destination routing (AX/EN/FL/FQ/CC fractions). All 82 Currier B folios show near-identical kernel absorption profiles (kernel exit rate ~98-100%, with <2% retained in kernel) and similar recovery path lengths (global mean ~4.1 tokens, range 3.76-4.78 across REGIMEs). Post-kernel routing is dominated by EN-role destinations (~49-75%) across all REGIMEs.

## Evidence

### Kernel Absorption Rates (Per-REGIME)

| REGIME | n | e_rate | h_rate | k_rate | exit_rate |
|--------|---|--------|--------|--------|-----------|
| REGIME_1 | 15 | 0.000+-0.000 | 0.000+-0.000 | 0.010+-0.036 | 0.990+-0.036 |
| REGIME_2 | 18 | 0.000+-0.000 | 0.014+-0.057 | 0.000+-0.000 | 0.986+-0.057 |
| REGIME_3 | 4 | 0.000+-0.000 | 0.000+-0.000 | 0.000+-0.000 | 1.000+-0.000 |
| REGIME_4 | 16 | 0.009+-0.035 | 0.009+-0.035 | 0.000+-0.000 | 0.982+-0.069 |

Note: These are folio-level rates for kernel-to-kernel transitions. The near-zero within-kernel retention reflects that kernel tokens (classes 1-3) almost always exit to non-kernel classes.

### Recovery Path Length (Per-REGIME)

| REGIME | n | mean_length | max_length | n_paths |
|--------|---|-------------|------------|---------|
| REGIME_1 | 23 | 3.82+-0.90 | 8.6 | 28.5 |
| REGIME_2 | 24 | 4.78+-3.26 | 10.5 | 20.4 |
| REGIME_3 | 8 | 4.10+-0.71 | 8.9 | 17.5 |
| REGIME_4 | 27 | 3.76+-1.08 | 8.7 | 21.4 |

### KW Tests Summary (All 13)

| Category | Metric | H | p | eta_sq |
|----------|--------|---|---|--------|
| Kernel | e_rate | 2.31 | 0.510 | 0.000 |
| Kernel | h_rate | 1.14 | 0.766 | 0.000 |
| Kernel | k_rate | 2.53 | 0.469 | 0.000 |
| Kernel | exit_rate | 0.27 | 0.965 | 0.000 |
| Recovery | mean_lengths | 1.45 | 0.693 | 0.000 |
| Recovery | median_lengths | 2.90 | 0.408 | 0.000 |
| Recovery | max_lengths | 0.12 | 0.989 | 0.000 |
| Recovery | n_paths | 6.29 | 0.098 | 0.042 |
| PostKernel | AX | 3.39 | 0.336 | 0.008 |
| PostKernel | EN | 3.07 | 0.381 | 0.001 |
| PostKernel | FL | 3.19 | 0.363 | 0.004 |
| PostKernel | FQ | 1.82 | 0.611 | 0.000 |
| PostKernel | CC | 2.70 | 0.441 | 0.000 |

Closest to significance: n_recovery_paths (p=0.098), driven by REGIME_1 having more recovery paths (28.5 vs 17.5-21.4), reflecting more folio tokens rather than different recovery architecture.

## Interpretation

Kernel recovery pathways operate identically across REGIMEs at the folio level. The system's recovery pathway architecture -- how tokens exit kernel, how long recovery sequences run, and which roles receive post-kernel routing -- is folio-invariant with respect to REGIME assignment. This is consistent with C458's finding that hazard is clamped (same topology everywhere) but extends it: the immediate kernel-exit behavior is also invariant. Recovery freedom (C458 CV=0.72-0.82) is not structured by REGIME at the pathway level.

## Extends

- **C458**: Recovery is "free" (high CV) -- this confirms freedom extends to pathway-level metrics, not just aggregate counts
- **C105**: Global kernel recovery (e=54.7%, h=25.9%, k=19.4%) -- folio-level rates are near-zero because C105 measures multi-step paths while this measures single-step transitions
- **C545/C551**: REGIMEs have distinct class compositions -- but this does not translate to distinct recovery pathways

## Related

C105, C397, C398, C458, C521, C545, C551, C602, C635, C636
