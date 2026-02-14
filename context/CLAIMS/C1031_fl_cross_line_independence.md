# C1031: FL Cross-Line Independence

**Tier:** 2 | **Scope:** B | **Phase:** FL_CROSS_LINE_CONTINUITY

## Statement

FL stage (C777) does not propagate across line boundaries. Each line independently samples its FL stages from the folio's available pool. Within-line FL coherence (68.2% SAME, C786) collapses to 27.9% at cross-line transitions, and backward transitions jump from 4.5% to 44.3%. Endpoint stage correlation is zero (rho = 0.003, p = 0.963).

## Evidence

**Test: Adjacent line pairs within paragraphs (N=1,446 broad, N=230 narrow)**

### Endpoint correlation (last FL on line N vs first FL on line N+1)

| Method | rho | p (parametric) | p (permutation, N=10000) |
|--------|-----|----------------|--------------------------|
| Broad (all FL MIDDLEs) | 0.032 | 0.221 | 0.216 |
| Narrow (FLOW_OPERATOR) | 0.003 | 0.963 | 0.963 |

No significant correlation by any test. The FL stage at which line N ends does NOT predict where line N+1 begins.

### Cross-line transition direction vs within-line (C786)

| Direction | Within-line (C786) | Cross-line (broad) | Cross-line (narrow) |
|-----------|-------------------|--------------------|--------------------|
| Forward | 27.3% | 27.9% | 32.6% |
| Same | 68.2% | 27.9% | 32.2% |
| Backward | 4.5% | 44.3% | 35.2% |

The within-line forward bias (5:1 forward:backward, C786) disappears at line boundaries. Cross-line transitions are approximately uniform across directions, with a slight backward bias driven by the within-line positional gradient (lines tend to END at late stages and START at early stages).

### Mean stage gap

| Metric | Broad | Narrow |
|--------|-------|--------|
| Mean gap (first_N+1 - last_N) | -0.429 | -0.139 |
| Null model gap | -0.429 | -0.139 |

The observed gap equals the null model gap exactly — no information beyond marginal distributions.

### Mean stage correlation (folio-mediated)

| Method | rho | p (permutation) |
|--------|-----|-----------------|
| Broad | 0.063 | 0.017 |
| Narrow | 0.067 | 0.311 |

The broad method shows marginal significance with negligible effect size (rho=0.063). This is consistent with C681's folio-mediated coupling: adjacent lines share folio context, which weakly constrains their FL profile, but no direct state propagation occurs.

## Interpretation

FL state tracking is **strictly within-line**. Each line samples independently from the folio's FL stage distribution:

1. Within a line: FL progresses forward (INITIAL → TERMINAL, C777) with 68% SAME coherence (C786)
2. At line boundaries: FL stage resets. No continuity.
3. Across folios: FL chaining already falsified (C905)

This confirms C681's model: lines are contextually-coupled (shared folio parameters) but individually-independent. The controller is stateless per-line for FL stage, just as it is stateless for vocabulary (C670) and trigger memory (C673).

## Structural Summary

```
WITHIN LINE:  FL stage progresses (INITIAL → TERMINAL, rho=0.64, C786)
AT LINE BOUNDARY: FL stage resets (rho ≈ 0, SAME collapses 68% → 28%)
ACROSS FOLIO: FL chaining falsified (C905)
```

The paragraph is NOT a multi-line FL trajectory. Each line is a complete, independent FL assessment cycle.

## Related Constraints

- **C777:** FL state index (defines stages and within-line gradient)
- **C786:** FL forward bias (within-line: 27% forward, 68% same, 5% backward)
- **C670:** No adjacent-line vocabulary coupling (Jaccard ns)
- **C681:** Sequential coupling is folio-mediated, not line-to-line
- **C905:** Cross-folio FL chaining falsified
- **C673:** No CC trigger memory across lines

## Provenance

- Script: `phases/FL_CROSS_LINE_CONTINUITY/scripts/fl_cross_line.py`
- Results: `phases/FL_CROSS_LINE_CONTINUITY/results/fl_cross_line.json`
- Date: 2026-02-14
