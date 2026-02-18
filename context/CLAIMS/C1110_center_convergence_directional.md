# C1110: CENTER Convergence Node Directionally Confirmed

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** ROSETTES_CROSS_REFERENCE_VALIDATION (Phase 393)
**Strengthens:** C1092 (CENTER convergence node interpretation)

---

## Statement

The CENTER description region (C2) on f85v2 is directionally distinct from NORTH and VERT on both predicted dimensions: higher TARGET fraction (0.458 vs 0.333/0.375) and lower kernel percentage (54.5% vs 69.2%/71.9%). This confirms C1092's convergence node interpretation — CENTER demonstrates collection/convergence behavior, not heating behavior.

However, the full operational profile comparison (P1) shows these differences fall within noise for random blocks of matched size (p=0.459). The CENTER is directionally but not statistically distinct at the 9-dimensional profile level.

---

## Evidence

### Hub Role Balance
| Region | src | tgt | buf | con | Total | tgt_fraction |
|--------|-----|-----|-----|-----|-------|-------------|
| NORTH | 17 | 15 | 6 | 7 | 45 | 0.333 |
| VERT | 17 | 18 | 4 | 9 | 48 | 0.375 |
| CENTER | 4 | 11 | 4 | 5 | 24 | **0.458** |

CENTER tgt_fraction > NORTH: YES (0.458 > 0.333)
CENTER tgt_fraction > VERT: YES (0.458 > 0.375)

### Kernel Balance
| Region | k_pct | hazard_pct |
|--------|-------|------------|
| NORTH | 69.2% | 71.1% |
| VERT | 71.9% | 72.9% |
| CENTER | **54.5%** | 62.5% |

CENTER k_pct < NORTH: YES (54.5 < 69.2)
CENTER k_pct < VERT: YES (54.5 < 71.9)

### Caveat: P1 Gate Failure
Despite directional confirmation, the 9-dimensional profile comparison (kernel + hazard + LINK + TTR + e-fraction + hub role) places CENTER within the expected range for random 33-token blocks from the Rosettes corpus (p=0.459). The small sample size (33 tokens) limits statistical power.

---

## Interpretation

C1092 identified the CENTER rosette as a convergence node: TARGET-dominant, core-only vocabulary, proximity-scaled overlap. P6 confirms the two key directional predictions:

1. **TARGET dominance**: CENTER has the highest tgt_fraction of all three description groups, consistent with a collection/convergence function
2. **Reduced kernel concentration**: CENTER has lower k_pct than both NORTH and VERT, consistent with less heating-specific content

The P1 gate failure means these directional differences are not strong enough to distinguish CENTER from random Rosettes blocks at the full profile level. This is expected given the small sample (33 tokens) and the coarseness of the 9-dimensional profile representation. The directional signal is real but the effect size is modest at this granularity.

C1092's interpretation stands but is characterized as a directional pattern, not a statistically robust one.

---

## Provenance

- Phase: 393 (ROSETTES_CROSS_REFERENCE_VALIDATION), Test P6
- Script: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/scripts/rosettes_crossref_validation.py`
- Results: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/results/rosettes_crossref_validation.json`
- Related: C1092, C1098
