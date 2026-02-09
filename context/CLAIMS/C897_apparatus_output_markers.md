# C897: Prefixed FL MIDDLEs as Line-Final State Markers

**Tier:** 2
**Scope:** B-internal
**Status:** VALIDATED
**Validated:** 2026-01-30
**Updated:** 2026-01-30 (FL connection established)

## Claim

Tokens ending in -am/-y (am, dam, otam, oly, oldy, daly, ldy, ary) are **prefixed FL MIDDLEs** that inherit FL's state-indexing function (C777). They appear line-final (72.7%) because their MIDDLEs are FL FINAL/TERMINAL markers. Different ENERGY operations produce different terminal states, explaining the operation→state mappings observed.

## Core Finding: FL MIDDLEs

All tokens contain FL MIDDLEs from C777's state index:

| Token | Prefix | MIDDLE | FL Stage (C777) | Position |
|-------|--------|--------|-----------------|----------|
| am | - | am | FINAL | 0.802 |
| dam | da | m | TERMINAL | 0.861 |
| otam | ot | am | FINAL | 0.802 |
| oly | ol | y | TERMINAL | 0.942 |
| oldy | ol | dy | TERMINAL | 0.908 |
| daly | da | ly | FINAL | 0.785 |
| ldy | - | l+dy | LATE | 0.618 |
| ary | ar | y | TERMINAL | 0.942 |

**Key insight:** These tokens are classified as AUXILIARY or FREQUENT_OPERATOR due to their prefixes, but their MIDDLEs are FL state indices. They inherit FL's state-marking function.

## Evidence

### Line-Final Concentration

| Metric | Value | Explanation |
|--------|-------|-------------|
| Line-final rate | 72.7% | FL TERMINAL MIDDLEs are positionally late (C777) |
| Mean paragraph position | 0.587 | Consistent with FINAL/TERMINAL FL stages |

### Role Classification

| Token | Role | Class | Why Not FL? |
|-------|------|-------|-------------|
| ary | FLOW_OPERATOR | 40 | IS FL (no prefix) |
| daly | FLOW_OPERATOR | 40 | IS FL |
| dam | FLOW_OPERATOR | 30 | IS FL |
| oly | AUXILIARY | 15 | Prefix 'ol' shifts role |
| oldy | AUXILIARY | 25 | Prefix 'ol' shifts role |
| ldy | AUXILIARY | 20 | Complex structure |
| am | FREQUENT_OPERATOR | 23 | Short token, different class |
| otam | FREQUENT_OPERATOR | 14 | Prefix 'ot' shifts role |

Three tokens (ary, daly, dam) ARE classified as FL. The others have FL MIDDLEs but different role classification due to prefixation.

### Operation → State Mappings

Specific ENERGY operations prefer specific FL terminal states:

| ENERGY Operation | Preferred State | FL MIDDLE |
|------------------|-----------------|-----------|
| shey | → ldy | l (LATE) |
| cheky, chedy | → daly | ly (FINAL) |
| qokain, qokeedy | → oly | y (TERMINAL) |

**Interpretation:** Different heating operations produce different terminal states in the FL state index.

### Variant Predecessor Overlap

| Variant Pair | Jaccard | Interpretation |
|--------------|---------|----------------|
| oldy vs daly | 0.03 | Different operations → different states |
| oldy vs oly | 0.03 | Minimal overlap |
| oly vs ldy | 0.07 | Distinct predecessor sets |

Low overlap confirms each FL terminal state results from specific operations.

## Relationship to FL Architecture

This finding extends C777 (FL State Index):

```
C777: FL MIDDLEs index material progression
      [i/ii] → [r/ar] → [al/l/ol] → [o/ly/am] → [y/ry/dy]
       0.30     0.51      0.61        0.78        0.92

C897: Prefixed FL MIDDLEs inherit state-indexing
      ENERGY_OP → [PREFIX + FL_TERMINAL_MIDDLE]
      shey      → ldy   (l = LATE)
      cheky     → daly  (ly = FINAL)
      qokain    → oly   (y = TERMINAL)
```

The prefix doesn't change the MIDDLE's function - it adds specificity while preserving the terminal state marker.

## Why This Wasn't Obvious

1. **Role classification masks FL MIDDLEs** - Prefixes shift tokens to AUXILIARY/FREQUENT_OPERATOR
2. **Tokens analyzed as wholes** - Morphological decomposition reveals FL core
3. **FL documented separately** - C770-C777 focus on pure FL tokens, not prefixed forms

## Falsification Criteria

1. If MIDDLEs are not from FL inventory
2. If line-final rate doesn't correlate with FL positional gradient
3. If operation→state mappings disappear

## Provenance

- Phase: APPARATUS_ANALYSIS + STATE_MARKER_TEST
- Scripts: `scripts/am_ary_apparatus_*.py`, `scripts/state_marker_hypothesis_test.py`, `scripts/check_am_ary_morphology.py`
- FL connection: `scripts/check_am_ary_roles.py`

## Related Constraints

- **C777**: FL State Index (FL MIDDLEs show positional gradient 0.30→0.94)
- **C770**: FL Kernel Exclusion (FL uses 0 kernel characters)
- **C772**: FL Primitive Substrate (FL provides base layer)
- **C267**: Compositional morphology (PREFIX + MIDDLE + SUFFIX)
- **C556**: SETUP→WORK→CHECK→CLOSE line template
