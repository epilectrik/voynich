# C1032: B5 Asymmetry Mechanism — Forbidden Suppression + PREFIX Routing

**Tier:** 2 | **Scope:** B | **Phase:** PREFIX_ASYMMETRY_CORRECTION

## Statement

The M2 B5 failure (forward-backward JSD: M2 generates 0.178 vs real 0.090) is caused by asymmetric forbidden transition suppression. 15% detailed-balance blending corrects B5 to 0.111 (within 24% of real, passes the 50% criterion at 100% rate). However, generic blending regresses B1 (spectral gap 0.770 vs 0.894, fails 10% criterion) and B3 (reintroduces 5 forbidden violations). The real mechanism (PREFIX symmetric routing, C1024) achieves symmetry without reducing spectral structure — a more targeted correction is needed.

## Evidence

### B5 Failure Diagnosis

| Model | Mean B5 | Pass Rate | Mechanism |
|-------|---------|-----------|-----------|
| M1 (no forbidden) | 0.129 | 85% | Empirical matrix only |
| M2 (C1025 forbidden) | 0.178 | 0% | 75 extra zero cells (asymmetric suppression) |
| Real data | 0.090 | — | Ground truth |

The forbidden transitions in Phase 18A are token-level pairs mapped to MIDDLE-level class suppression. Only 1 of 17 forbidden pairs has the reverse direction also forbidden. This asymmetric zeroing makes the M2 matrix more directional than the empirical matrix.

### Partial Symmetrization Fix

Blending M2 with its detailed-balance reverse: T_blend = (1-alpha) * T_M2 + alpha * T_reverse

| Alpha | B5 | B5 Pass | Notes |
|-------|-----|---------|-------|
| 0.00 | 0.178 | 0% | M2 original |
| 0.10 | 0.130 | 80% | Marginal |
| **0.15** | **0.111** | **100%** | **Best B5 fix** |
| 0.20 | 0.096 | 100% | Closest to real |
| 0.50 | 0.055 | 100% | Over-symmetrized |

### Regression at alpha=0.15

| Test | M2 | M2.5 (alpha=0.15) | Real | Verdict |
|------|-----|-------------------|------|---------|
| B5 (fwd-bwd JSD) | 0.178 (FAIL) | 0.111 (PASS) | 0.090 | Fixed |
| B1 (spectral gap) | ~0.89 (PASS) | 0.770 (FAIL) | 0.894 | Regressed |
| B3 (forbidden violations) | 0 (PASS) | 5 (FAIL) | 0 | Regressed |

Generic blending gains B5 but loses B1 and B3. Net pass rate unchanged.

### C1024 Consistency

| Metric | Value |
|--------|-------|
| C1024 PREFIX MI asymmetry fraction | 20.5% |
| Optimal blending alpha | 15% |
| Ratio | 0.73 |

The 15% symmetrization needed is in the right range relative to C1024's 20.5% PREFIX fraction. The discrepancy (15% vs 20.5%) is consistent with the forbidden suppression creating ADDITIONAL asymmetry beyond what PREFIX routing compensates.

## Interpretation

The B5 failure has two independent causes:
1. **Forbidden suppression asymmetry:** 16 of 17 forbidden transitions are one-directional (C111). Zeroing them makes the matrix asymmetric.
2. **Missing PREFIX routing:** Real data uses PREFIX symmetric routing (C1024) to maintain approximate detailed balance despite asymmetric forbidden suppression. M2 doesn't model this.

Generic matrix blending corrects the net asymmetry but destroys spectral structure (reducing the spectral gap from 0.894 to 0.770). The real mechanism is more sophisticated: PREFIX routing adds symmetry to SPECIFIC transitions (the PREFIX-mediated routing paths) without flattening the overall transition structure.

## Open Problem

A true M2.5 fix requires PREFIX-aware generation:
1. Decompose each transition into PREFIX routing (symmetric) and MIDDLE execution (directional)
2. Generate using the factored model: sample PREFIX symmetrically, then MIDDLE directionally
3. Apply forbidden suppression after generation, not in the matrix

This is beyond simple matrix modification and would require a new generation architecture.

## Impact on M2 Pass Rate

| Correction | Tests | Pass Rate |
|------------|-------|-----------|
| M2 original (C1025) | 12/15 | 80.0% |
| + B4 correction (C1030) | 13/15 | 86.7% |
| + B5 generic blending | 13/15 | 86.7% (B5 pass, but B1+B3 regress) |
| + B5 PREFIX-aware (future) | 14/15 | 93.3% (projected) |

The M2 pass rate remains at 13/15 = 86.7%. True B5 correction via PREFIX-aware generation would push to 14/15 = 93.3%.

## Related Constraints

- **C1024:** PREFIX is symmetric router, MIDDLE is directional executor
- **C1025:** M2 generative sufficiency (12/15 original, corrected to 13/15 via C1030)
- **C1030:** B4 is misspecified, B5 and C2 are independent mechanisms
- **C111:** 65% of forbidden transitions are asymmetric
- **C391:** Conditional entropy symmetry (H(X|past) = H(X|future))
- **C886:** Transition probability directionality

## Provenance

- Scripts: `phases/PREFIX_ASYMMETRY_CORRECTION/scripts/b5_diagnosis.py`, `b5_fix.py`
- Results: `phases/PREFIX_ASYMMETRY_CORRECTION/results/b5_diagnosis.json`, `b5_fix.json`
- Date: 2026-02-14
