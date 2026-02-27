# C1364: Position-Conditioned Generation (M2.1)

**Tier:** 2
**Scope:** B
**Phase:** 476 (POSITION_CONDITIONED_GENERATION)
**Depends on:** C1025, C1030, C1034, C1358, C1362, C1363

## Claim

M2.1 (quintile-conditioned 49-class Markov chain with symmetric forbidden suppression) passes 16/18 generative metrics with zero regressions versus M2-SF baseline (13/18). Position conditioning closes the entire positional blind spot diagnosed in C1362 while preserving all 15 original structural metrics.

## Evidence

Two models compared side-by-side, 10 independent runs each, 18 metrics:

- **M2-SF baseline**: 13/18 pass (fails B4, C2, P1, P2, P3)
- **M2.1**: 16/18 pass (fails B4, C2 only)
- **Tests gained**: P1, P2, P3 (all 3 positional metrics)
- **Tests lost**: 0 (no regressions on any original metric)

### Position metric improvements (mean across 10 runs)

| Metric | M2-SF | M2.1 | Ratio |
|--------|-------|------|-------|
| P1: quintile class KL | 0.066 | 0.029 | 2.2x |
| P2: quintile trans JSD | 0.299 | 0.146 | 2.0x |
| P3: specialist accuracy | 0.149 | 0.062 | 2.4x |

### Remaining failures

- **B4** (role rank order FQ > FL > EN): 0% pass. Known PREFIX-factoring blind spot (Phase 477 target).
- **C2** (CC suffix-free >= 99%): 0% pass. Known class-conditioned suffix blind spot (Phase 478 target).

### Architecture

- 5 corpus-wide quintile-specific 49x49 transition matrices (C1363: gradient universal, not folio-specific)
- Symmetric forbidden suppression on each matrix (C1034: bidirectional zeroing)
- Source-token quintile determines which matrix is used (matching C1362 M2p protocol)
- Same opener distribution and token-from-class sampling as M2

### Key diagnostic

- 168 symmetric forbidden class pairs (84 forward + 84 reverse)
- Q4 has 10 zero-row classes (sparse line-final data) — handled by opener fallback
- B5 (fwd-rev JSD) passes at 90% confirming C1034 symmetric fix
- Hallucination rate: 0% (no novel tokens generated)

## Interpretation

Position conditioning is the single largest improvement available to the M2 architecture. The 2.0-2.4x improvement across all three positional metrics confirms C1362's diagnosis: line position was M2's primary blind spot, and it is fully correctable by quintile-conditioning the transition matrices without changing the grammar. The remaining 2 failures (B4, C2) are morphological, not sequential — they require different architectural changes (PREFIX factoring and class-conditioned suffix generation).

## Status

M2.1 is the new generative frontier: 16/18 = 88.9% pass rate. The projected M3 (M2.1 + PREFIX factoring + class-conditioned suffix) targets 18/18.

## Files

- Script: `phases/POSITION_CONDITIONED_GENERATION/scripts/position_conditioned_generation.py`
- Results: `phases/POSITION_CONDITIONED_GENERATION/results/position_conditioned_generation.json`
