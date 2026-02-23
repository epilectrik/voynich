# C1227 - FL Cross-Line Reset Clustering

**Tier:** 2 | **Scope:** B | **Phase:** APPARATUS_TRANSITION_DETECTION (Phase 438)

## Statement

FL state regressions between consecutive body lines occur in 36.4% of cross-line FL pairs (257/707) and cluster at non-uniform positions within paragraphs (KS vs uniform p<0.0001). The dominant regression is LATE->MEDIAL (190/257 = 73.9%), not LATE->EARLY (33/257 = 12.8%). This partial reset pattern marks cycle boundaries within a continuous process - the process returns to active processing mode without full restart.

## Evidence

### Cross-line FL transition matrix (707 pairs from 124 paragraphs with 6+ body lines)

| Transition | Count | Rate |
|------------|-------|------|
| MEDIAL->MEDIAL | 255 | 36.1% |
| LATE->MEDIAL | 190 | 26.9% |
| MEDIAL->LATE | 94 | 13.3% |
| LATE->LATE | 70 | 9.9% |
| MEDIAL->EARLY | 34 | 4.8% |
| LATE->EARLY | 33 | 4.7% |
| EARLY->MEDIAL | 19 | 2.7% |
| EARLY->LATE | 8 | 1.1% |
| EARLY->EARLY | 4 | 0.6% |

### Key observations

1. **Regression is common**: 36.4% of cross-line FL pairs show the process going backward at least one stage
2. **Partial reset dominates**: LATE->MEDIAL (190) >> LATE->EARLY (33). Processes cycle back to active processing, not to initial setup.
3. **Structured positioning**: Regression events cluster at specific paragraph positions (KS stat=0.167, p<0.0001), not uniformly distributed
4. **Section-consistent**: Regression rate stable across sections (B: 35.4%, H: 38.0%, S: 34.8%, C: 37.3%)

### Relationship to C787

C787 establishes that LATE->EARLY is forbidden WITHIN lines (0 occurrences). This constraint shows LATE->EARLY DOES occur between lines (33 cases), and the more common regression LATE->MEDIAL occurs 190 times. The cross-line boundary permits state regressions that the within-line grammar forbids.

## Interpretation

Each line represents one processing cycle within a continuous procedure. The FL state tracks progress within each cycle (EARLY->MEDIAL->LATE). Between cycles, FL partially resets - typically to MEDIAL (active processing) rather than EARLY (initial setup) - because the next cycle picks up from the current process state rather than starting from scratch. This is consistent with iterative extraction passes through the same apparatus.

## Related constraints

- C787: FL LATE->EARLY forbidden within lines (0 occurrences)
- C777: FL state positional index (range 0.643 within lines)
- C786: FL forward bias within lines (5:1 forward:backward)
- C963: Body homogeneity at role-fraction level
- C932: Body spec->exec vocabulary gradient

## Provenance

- `phases/APPARATUS_TRANSITION_DETECTION/scripts/apparatus_transition_detection.py` (Test F)
- `phases/APPARATUS_TRANSITION_DETECTION/results/apparatus_transition_results.json`
