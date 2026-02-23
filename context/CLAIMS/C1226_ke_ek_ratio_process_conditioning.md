# C1226 - ke/ek Ratio Process-Context Conditioning

**Tier:** 2 | **Scope:** B | **Phase:** KE_THERMAL_CYCLING_VALIDATION (Phase 437)

## Statement

The ratio of ke to ek tokens is strongly conditioned by both REGIME and section. REGIME_1 (energy-intensive): 81.4% ke / 18.6% ek; REGIME_4 (precision): 36.0% ke / 64.0% ek; section B (BIO): 80.3% ke / 19.7% ek; section H (HERBAL): 20.9% ke / 79.1% ek. Both chi-squared p<0.0001. The k-e ordering within tokens is a process-sensitivity marker, not free variation.

## Evidence

### REGIME conditioning (chi-squared = 77.71, p < 0.0001)

| REGIME | ke | ek | ek fraction |
|--------|----|----|-------------|
| REGIME_1 | 290 | 66 | 18.6% |
| REGIME_2 | 12 | 21 | 63.6% |
| REGIME_3 | 76 | 45 | 37.2% |
| REGIME_4 | 27 | 48 | 64.0% |

### Section conditioning (chi-squared = 138.50, p < 0.0001)

| Section | ke | ek | ek fraction |
|---------|----|----|-------------|
| B (BIO) | 180 | 44 | 19.7% |
| C       | 6  | 3  | 33.3% |
| H (HERBAL) | 18 | 68 | 79.1% |
| S (STARS) | 208 | 51 | 19.7% |
| T       | 9  | 3  | 25.0% |

### Predecessor context (T1)

- ke follows E-DOM predecessors (MIDDLEs where e is majority kernel) 54.9% of the time
- ek follows E-DOM predecessors only 22.5% (Fisher p<0.0001, OR=4.20)
- ke is preferentially placed after stability-rich context; ek after energy-rich context

### Sequential responsiveness (T5)

- ke predecessors have higher e-kernel mean (27.2%) than kch predecessors (21.7%), p=0.005
- ke placement responds to preceding thermal/stability state

## Pattern

ek concentrates where processes require precision and tight tolerance (REGIME_4, HERBAL). ke concentrates where processes are energy-intensive and tolerant (REGIME_1, BIO). The k-before-e vs e-before-k ordering encodes the relationship between energy application and stability assessment in the current process context.

## Negative findings (documented for completeness)

- ke-family tokens do NOT route preferentially to CHSH lane (permutation p=0.9996); ke routes to QO at 34.7% vs baseline 43.2%. This null applies to PREFIX-level lane routing; it does not constrain what ke encodes within the token.
- ke-family is indistinguishable from general e-containing MIDDLEs at the lane routing level (Fisher p=0.088). The ke/ek distinction operates at MIDDLE-internal level, not at cross-token routing level.

## Interpretation

The ke/ek ratio functions as a process-sensitivity indicator within B's execution grammar. Contexts requiring corrective feedback and tight monitoring favor ek (stability-check-first); contexts tolerating sustained energy application favor ke (energy-first). The structural pattern is consistent with — but does not require — a thermal cycling interpretation where ke = "apply heat then equilibrate" and ek = "verify conditions then apply heat."

## Related constraints

- C521: k→e elevated 4.32× (directional bias within tokens)
- C1200: k-terminal → e-initial carryover 70.6%
- C1225: E-depth suffix parametricity (companion finding)
- F-BRU-013: ke vs kch section differentiation (85% BIO/HERBAL)
- F-BRU-017: REGIME_4 sustained equilibration
- C998: Thermal physics cannot generate the grammar (but grammar can encode thermal control)

## Provenance

- `phases/KE_THERMAL_CYCLING_VALIDATION/scripts/ek_corrective_test.py`
- `phases/KE_THERMAL_CYCLING_VALIDATION/results/ek_corrective_results.json`
- `phases/KE_THERMAL_CYCLING_VALIDATION/scripts/ke_thermal_test.py` (T5)
- `phases/KE_THERMAL_CYCLING_VALIDATION/results/ke_thermal_results.json`
