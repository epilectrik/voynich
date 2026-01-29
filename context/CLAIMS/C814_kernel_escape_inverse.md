# C814: Kernel-Escape Inverse Relationship

## Constraint

KERNEL density is the strongest negative predictor of FL (escape) rate at folio level:

- KERNEL vs FL: rho = -0.528, p < 0.0001
- KERNEL-only (no 'ol') vs FL: rho = -0.390, p = 0.0003

High kernel density predicts low escape; low kernel density predicts high escape.

## Evidence

Folio-level correlations with FL rate:
| Predictor | rho | p-value |
|-----------|-----|---------|
| KERNEL | -0.528 | <0.0001 |
| KERNEL-only | -0.390 | 0.0003 |
| LINK | -0.222 | 0.045 |
| HT | 0.150 | 0.179 |
| LINK-only | -0.101 | 0.368 |

FL tertile analysis:
| FL Level | Mean KERNEL | Mean LINK | Mean HT |
|----------|-------------|-----------|---------|
| Low (≤3.9%) | 72.3% | 15.1% | 29.0% |
| Mid | 67.6% | 11.3% | 32.3% |
| High (>5.6%) | 64.4% | 11.1% | 31.6% |

Rate distributions across 82 folios:
| Phase | Mean | Std | Min | Max |
|-------|------|-----|-----|-----|
| KERNEL | 68.1% | 7.0% | 50.5% | 85.6% |
| LINK | 12.5% | 6.2% | 1.0% | 30.0% |
| FL | 4.9% | 2.0% | 1.3% | 11.0% |
| HT | 31.0% | 7.6% | 15.5% | 47.2% |

## Interpretation

Folios with high kernel (processing) density have low escape rates - they run "smoothly" without frequent recovery events. Folios with low kernel density need more escape operations. This suggests:

1. Kernel density reflects program stability
2. Escape (FL) compensates for low kernel coverage
3. Well-designed programs maximize kernel, minimize escape

The LINK-HT strong negative correlation (rho=-0.524) is also notable but separate from the escape prediction.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t5_folio_program_profiles.py
- Related: C796, C797

## Tier

2 (Validated Finding)
