# C1238 - Kernel Initiation Order

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

First-occurrence kernel ordering within lines is e -> k -> h: e appears before k in 64.6% of lines with both (+14.6 percentage points above chance), e before h in 71.6%, but h before k in only 28.3% (h typically appears AFTER k). The initiation sequence is cool -> process -> monitor. This refines C873's mean-position ordering (e 0.404 < h 0.410 < k 0.443) which measures center of mass rather than initiation sequence; both are valid projections.

## Evidence

### First-occurrence ordering

| Kernel pair | Lines with both | Observed order | % |
|-------------|-----------------|----------------|---|
| e and k | 1864 | e before k | 64.6% |
| e and h | 1052 | e before h | 71.6% |
| h and k | 915 | h before k | 28.3% |

### Random baseline

| Metric | Value |
|--------|-------|
| Random baseline | 50% |
| Shuffle test (10000 iterations) | 49.3% |
| Effect size (e-before-k) | +14.6 percentage points above chance |

### Relationship to C873

C873 measures **mean normalized position** of ALL occurrences:
- e: 0.404
- h: 0.410
- k: 0.443

This constraint measures **first occurrence**. The apparent discrepancy (h has early mean position in C873 but appears after k in first-occurrence ordering) is resolved: h has an early mean position because when it appears, it clusters early-to-mid. But k's first occurrence tends to be earlier because k is more frequent (31% of kernel mass vs h at 10%). Both measurements are valid; they capture different properties.

### Key observations

1. **e initiates**: e appears first in 64.6-71.6% of lines — the stability anchor leads
2. **k follows e**: Processing energy is applied after stability reference is established
3. **h follows k**: Monitoring occurs after energy application, not before
4. **+14.6 pp effect size**: Substantially above chance, not a weak trend

## Interpretation

The initiation sequence (cool -> process -> monitor) is consistent with kernel roles: establish stability reference first (e), then apply energy (k), then monitor the result (h). This is the temporal order of a controlled extraction cycle.

## Related constraints

- C873: Kernel positional ordering (mean position)
- C103: k = ENERGY_MODULATOR
- C104: h = PHASE_MANAGER
- C105: e = STABILITY_ANCHOR

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/loop_deep_analysis.py` (Test 3)
- `phases/CONTROL_LOOP_ARCHITECTURE/results/loop_deep_analysis.json`
