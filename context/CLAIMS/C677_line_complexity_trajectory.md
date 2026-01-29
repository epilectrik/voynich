# C677: Line Complexity Trajectory

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

Lines become **shorter and simpler** later in folios. Unique token count (rho=-0.196, p<1e-21), unique MIDDLE count (rho=-0.174, p<1e-17), and mean token length (rho=-0.093, p=5.1e-6) all decline. Type-token ratio is flat (rho=+0.017, p=0.409) — simplification comes from shorter lines, not from increased repetition.

## Key Numbers

| Metric | rho | p | Q1 | Q4 |
|--------|-----|---|----|----|
| Unique tokens | -0.196 | 3.2e-22 | 9.82 | 8.45 |
| Unique MIDDLEs | -0.174 | 7.7e-18 | 8.58 | 7.48 |
| Unique classes | -0.075 | 2.5e-4 | 5.73 | 5.28 |
| Mean token length | -0.093 | 5.1e-6 | 5.27 | 5.08 |
| Type-token ratio | +0.017 | 0.409 | 0.962 | 0.962 |

## Interpretation

The late-program simplification combines three converging signals:
1. Lines get physically shorter (fewer tokens)
2. Fewer distinct MIDDLEs per line (narrower vocabulary per assessment)
3. Shorter token forms (more bare tokens from C676)

But each token remains nearly unique within its line (TTR~0.962 throughout). This is not repetition — it is concision. Late-program control blocks use fewer, shorter, simpler operators while maintaining the grammar's compositional diversity. Combined with C664 (role proportions flat), C675 (MIDDLE identity stable), and C676 (morphological simplification), this describes a controller that converges toward a minimal-parameter operating mode.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_token_trajectory.py` (Test 10)
- Extends: C664-C669 (class-level stationarity with convergence signals)
