# C815: Phase Position Significance

## Constraint

Phase membership has **statistically significant** but **practically weak** positional preferences:

- ANOVA F = 70.28, p < 10⁻⁷³ (highly significant)
- Eta-squared = 0.0150 (only 1.5% variance explained)
- Prediction improvement: MSE -1.5%, MAE -0.8%
- Tercile prediction: 33.5% (baseline 33.3%)

## Evidence

Phase position statistics:
| Phase | N | Mean | Std | Median |
|-------|---|------|-----|--------|
| FL | 1,078 | 0.576 | 0.332 | 0.625 |
| HT | 1,251 | 0.602 | 0.372 | 0.698 |
| KERNEL_LINK | 1,783 | 0.440 | 0.322 | 0.400 |
| KERNEL_ONLY | 14,160 | 0.482 | 0.306 | 0.500 |
| LINK_ONLY | 1,251 | 0.527 | 0.340 | 0.533 |
| OTHER | 3,551 | 0.535 | 0.334 | 0.556 |

Most predictive phases (furthest from 0.5):
1. HT: mean = 0.602 (late)
2. FL: mean = 0.576 (late)
3. KERNEL_LINK: mean = 0.440 (early)

Prediction comparison:
| Method | MSE | MAE |
|--------|-----|-----|
| Baseline (grand mean) | 0.1031 | 0.2778 |
| Phase-based | 0.1015 | 0.2757 |
| Improvement | 1.5% | 0.8% |

## Interpretation

The control loop has **real but diffuse spatial structure**:

1. **Significant effect**: Phases DO have positional preferences (p < 10⁻⁷³)
2. **Weak effect**: Only 1.5% of position variance is explained
3. **Practical irrelevance**: Knowing phase barely helps predict position

This means: phases operate throughout lines with mild positional tendencies (LINK/KERNEL early, FL/HT late), not in strict sequential zones. The control loop is **temporally flexible**, not rigidly positional.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t6_sequence_prediction.py
- Related: C813

## Tier

2 (Validated Finding)
