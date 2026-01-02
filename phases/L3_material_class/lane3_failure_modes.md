# Lane 3: Failure Mode Analysis

## Failure Modes by Material Class

| Material | PHASE_COLLAPSE | Total |
|----|----|----|
| CLASS_A | 0 | 0 |
| CLASS_B | 0 | 0 |
| CLASS_C | 480 | 480 |
| CLASS_D | 0 | 0 |
| CLASS_E | 0 | 0 |

## Dominant Failure Modes

- **CLASS_A**: None
- **CLASS_B**: None
- **CLASS_C**: PHASE_COLLAPSE
- **CLASS_D**: None
- **CLASS_E**: None

## Failure Mode Definitions

| Mode | Physical Meaning |
|------|------------------|
| PHASE_COLLAPSE | Material phase transition destabilizes system |
| BOUNDARY_RUPTURE | Swelling causes containment failure |
| TIMING_FAILURE | Latency-sensitive material cannot track control |
| OSCILLATION_DIVERGENCE | Undamped perturbations grow without bound |
| GENERIC_OVERSHOOT | State exceeds hazard boundary |

## Interpretation

The Voynich control grammar shows **differential compatibility** with material classes.

Compatible classes:
- CLASS_A: Maintains stability (failure rate 0.00%)
- CLASS_B: Maintains stability (failure rate 0.00%)
- CLASS_D: Maintains stability (failure rate 0.00%)
- CLASS_E: Maintains stability (failure rate 0.00%)

Incompatible classes:
- CLASS_C: Destabilizes (failure rate 19.76%, mode: PHASE_COLLAPSE)
