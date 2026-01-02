# Option A: Failure Mode Analysis

## Failure Rates by Geometry

| Geometry | Failure Rate | Primary Failure Mode |
|----------|--------------|---------------------|
| G1 | 0.935 | PROPAGATION_INSTABILITY |
| G2 | 0.007 | MIXING_DELAY |
| G3 | 0.001 | CONSERVATION_LOSS |
| G4 | 0.000 | None (stable) |
| G5 | 0.000 | None (stable) |

## Failure Mode Definitions

| Mode | Dynamical Meaning |
|------|-------------------|
| PROPAGATION_INSTABILITY | Perturbations travel through system without damping |
| MIXING_DELAY | Slow homogenization prevents timely response |
| CONSERVATION_LOSS | Material leakage destabilizes state tracking |

## Geometry-Specific Analysis

### G1 — Linear Open Flow

- **Primary issue:** No recirculation means perturbations propagate unchecked
- **LINK ineffective:** No natural delay path for waiting behavior
- **State tracking:** Poor conservation makes target maintenance difficult

### G2 — Batch Vessel

- **Primary issue:** Slow mixing (long timescale) causes delayed response
- **LINK mapping:** Delay exists but not from circulation
- **Stability:** Good conservation but poor controllability

### G3 — Partial Recirculation

- **Primary issue:** Material leakage from incomplete loop
- **Competing paths:** Forward and return flows interfere
- **Marginal stability:** Some LINK effectiveness but inconsistent

### G4 — Fully Closed Loop

- **Stable:** Perfect conservation, natural delay from path length
- **LINK effective:** Maps to intrinsic transport delay
- **Damping:** Circulation smooths perturbations

### G5 — Multi-Loop Nested

- **Most stable:** Multiple timescales provide robust damping
- **LINK highly effective:** Nested delays match waiting behavior
- **Buffering:** Internal volumes smooth all disturbances

## Interpretation

The Voynich control grammar shows **differential compatibility** with geometry classes.

Compatible geometries:
- G2: Convergence 99.3%, LINK effectiveness 20.0%
- G3: Convergence 99.9%, LINK effectiveness 20.0%
- G4: Convergence 100.0%, LINK effectiveness 80.0%
- G5: Convergence 100.0%, LINK effectiveness 135.0%

Incompatible geometries:
- G1: Failure rate 93.5%, mode: PROPAGATION_INSTABILITY
