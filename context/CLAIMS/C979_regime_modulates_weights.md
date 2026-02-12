# C979: REGIME Modulates Transition Weights, Not Topology

**Tier:** 2 | **Scope:** B | **Phase:** MINIMAL_STATE_AUTOMATON

## Statement

The 6-state automaton topology is shared across all 4 REGIMEs, but transition probabilities shift significantly (global chi2 = 475.5, p = 1.47e-48). REGIME modulates execution density within the fixed state graph. FL_HAZ and FL_SAFE are regime-independent (p > 0.10); the operational states (FQ, CC, AXm, AXM) are regime-dependent.

## Per-Source-State REGIME Dependence

| Source State | chi2 | p-value | REGIME-dependent? |
|-------------|-------|---------|-------------------|
| FL_HAZ | 21.3 | 0.127 | No |
| FQ | 41.7 | 2.5e-04 | **Yes** |
| CC | 41.7 | 2.5e-04 | **Yes** |
| AXm | 30.3 | 0.011 | **Yes** |
| AXM | 134.8 | 2.4e-21 | **Yes** |
| FL_SAFE | 22.0 | 0.107 | No |

## Key REGIME Shifts

| REGIME | AXM self-loop | AXM→FQ | Interpretation |
|--------|--------------|--------|----------------|
| R1 (control-heavy) | 0.713 | 0.164 | Dense operational mass |
| R2 (output-intensive) | 0.659 | 0.203 | More scaffold interruption |
| R3 (high-intervention) | 0.741 | 0.143 | Deepest recurrence |
| R4 (precision) | 0.586 | 0.237 | Most FQ scaffolding = precision control |

## Architectural Significance

- **FL regime-independence** means flow markers (hazard/safe) have fixed semantics regardless of execution mode. The boundary states are constants; the interior is parameterized.
- **REGIME_4's high FQ rate** (0.237 from AXM vs pooled 0.173) confirms C494 (precision-constrained execution): more frequent error-correction/scaffolding interruptions.
- **REGIME_3's deep AXM recurrence** (0.741 self-loop) confirms C185 (high-throughput transient): longer uninterrupted operational runs.

## Provenance

- Extends: C179 (4 stable REGIMEs), C494 (REGIME_4 precision axis), C458 (hazard clamped, recovery free)
- Method: `phases/MINIMAL_STATE_AUTOMATON/scripts/t8_regime_conditioned.py`
- Results: `phases/MINIMAL_STATE_AUTOMATON/results/t8_regime_conditioned.json`
