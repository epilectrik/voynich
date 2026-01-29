# C805: LINK Positional Bias (C365 Refutation)

## Constraint

C365 claims LINK is spatially uniform. This is **REFUTED**.

LINK tokens show significant positional bias:
- Mean position: 0.476 vs 0.504 for non-LINK (p < 0.0001, earlier in line)
- First token: 17.2% LINK rate (chi2=44.1 vs middle, p < 0.0001)
- Last token: 15.3% LINK rate (chi2=16.4 vs middle, p = 0.0001)
- Middle tokens: 12.4% LINK rate

LINK shares the **same boundary enrichment pattern as HT** (C803).

## Evidence

Position quintile distribution:
| Quintile | LINK% | Non-LINK% | Ratio |
|----------|-------|-----------|-------|
| 0.0-0.2 | 25.1% | 21.2% | 1.18x |
| 0.2-0.4 | 18.7% | 18.0% | 1.04x |
| 0.4-0.6 | 16.9% | 18.1% | 0.94x |
| 0.6-0.8 | 16.0% | 18.5% | 0.87x |
| 0.8-1.0 | 23.2% | 24.2% | 0.96x |

Chi-square for shape: chi2=36.0, p < 0.0001

## Interpretation

LINK's boundary enrichment (shared with HT) suggests monitoring checkpoints at control block boundaries (C360: line = control block). This is consistent with C366's "boundary between monitoring and intervention" characterization, but contradicts C365's uniformity claim.

## Provenance

- Phase: LINK_OPERATOR_ARCHITECTURE
- Script: t2_link_position_distribution.py
- Refutes: C365

## Tier

2 (Validated Finding)
