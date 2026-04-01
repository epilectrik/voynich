# FOLIO_DESIGN_FREEDOM — Phase 633

**Status:** COMPLETE
**Date:** 2026-04-01
**Verdict:** ATOM_FREEDOM_DECOMPOSED (C1917-C1924)

## Purpose
Decompose within-section folio differentiation at atom resolution to identify the operational "tuning knobs" that make each B program unique.

## Key Findings

1. **67% genuine atom freedom** (C1917): Within-section atom variance is 2.5x larger than C1169's 27% AXM residual. AXM captures <2% of atom variance — atoms measure compositional dimensions almost entirely orthogonal to AXM's single dynamical property.
2. **11 effective dimensions** (C1918): Section-residualized atom features compress to 11 PCs at 80% variance. PC1 (23.8%) = yield vs cooling emphasis.
3. **4 pure FREEDOM features** (C1919): mod_c (adjust), term_h (transparent), mod_d (mark), mod_s (sequence) — all eta² < 0.10, REGIME-orthogonal within Herbal.
4. **REGIME decomposable but narrow** (C1920): RF LOO 85.4% accuracy, but concentrates in head_k + pfx_qo. Most atoms are REGIME-independent.
5. **Freedom channels consistent across sections** (C1921): Same features differentiate folios in Herbal, Stars, and Bio (rho=0.783).
6. **PREFIX and MOD drive differentiation** (C1922): ~60% of pairwise JSD comes from PREFIX + MOD layers.
7. **Atom-operational correlations strong** (C1923): head_e↔e_ratio rho=+0.816, term_n↔checkpoint_rate rho=+0.809.
8. **Freedom concentrates in monitoring cluster** (C1924): C1207's {c,h} monitoring cluster contains 2 of 4 FREEDOM features.

## Interpretation
Each B folio is a unique program built from shared components, tuned through specific atom channels. REGIME constrains thermal intensity (head_k, pfx_qo) but leaves operational style (how much adjustment, sequencing, marking, monitoring) as design freedom. The notation provides ~11 independent tuning dimensions, of which 3-4 are completely REGIME-orthogonal.

## Scripts
| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_variance_decomposition.py | Feature matrix, ANOVA, PCA | ~15s |
| s2_freedom_constraint_partition.py | FREEDOM/CONSTRAINED/MIXED classification | ~10s |
| s3_freedom_dimensions.py | PC interpretation with atom glosses | ~15s |
| s4_regime_atom_interaction.py | REGIME predictability, four-quadrant classification | ~45s |
| s5_75pct_reconciliation.py | Reconcile 67% atom freedom with 27% AXM residual | ~30s |

## Results
All in `results/` — JSON outputs + CSV feature matrices from each script.
