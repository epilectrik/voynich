# C1033: C2 Test Misspecification — CC Definition Mismatch

**Tier:** 2 | **Scope:** B | **Phase:** C2_CC_SUFFIX_FREE

## Statement

The C2 test (CC suffix-free >= 99%) is misspecified. The test uses CC = {10, 11, 12, 17} (5-role taxonomy) but the underlying constraint C588 established CC as 100% suffix-free using CC = {10, 11, 12} (macro-state partition). Class 17 has 59% suffixed tokens (170/288), dragging the measured rate to 83.4%. Real data itself fails the test. M2 reproduces the real CC suffix-free rate exactly (0.824 +/- 0.010 vs real 0.834). Correcting C2 pushes M2 from 13/15 to 14/15 = 93.3%. Only B5 (forward-backward asymmetry, C1032) remains.

## Evidence

### Class 17 Suffix Composition

| Class | Tokens | Suffixed | Suffix-Free Rate | In CC? |
|-------|--------|----------|-----------------|--------|
| 10 (daiin) | 314 | 0 | 1.000 | Yes (both) |
| 11 (ol) | 421 | 0 | 1.000 | Yes (both) |
| 12 (k) | 0 | 0 | ghost | Yes (both) |
| **17 (ol-derived)** | **288** | **170** | **0.410** | ROLE only |

Class 17 tokens are all ol-prefixed: olkeedy (n=41, sfx=edy), olkeey (n=38, sfx=eey), olkain (n=33, sfx=ain), olkaiin (n=31, sfx=aiin), olkedy (n=27, sfx=edy). These are compound tokens with prefix "ol" and kernel "k" plus various suffixes.

### Two CC Definitions

| Definition | Classes | Tokens | Suffix-Free | Source |
|------------|---------|--------|-------------|--------|
| Macro-state partition | {10, 11, 12} | 735 | 1.000 | C1010, C1030 |
| 5-role taxonomy | {10, 11, 12, 17} | 1023 | 0.834 | generative_sufficiency.py |

C588 found CC = 100% suffix-free. C590 listed class 17 with suffix = NONE (incorrect — class 17 has 59% suffixed tokens). The C2 test inherited the wrong CC definition.

### M2 Under Corrected C2

| CC Definition | Real | M2 | Match? |
|--------------|------|-----|--------|
| ROLE {10,11,12,17} | 0.834 | 0.824 +/- 0.010 | Yes (within 1.2pp) |
| MACRO {10,11,12} | 1.000 | 1.000 +/- 0.000 | Yes (exact) |

Under either definition, M2 reproduces the real value. The test failure was caused by checking against a fixed 99% threshold that the real data itself doesn't meet.

### Pass Rate Under Different C2 Tests

| Test Definition | M2 Pass Rate |
|----------------|-------------|
| Original: ROLE CC >= 0.99 | 0% |
| Fix A: MACRO CC >= 0.99 | 100% |
| Fix B: |gen - real| < 3pp (ROLE) | 95% |
| Fix B: |gen - real| < 3pp (MACRO) | 100% |

### C590 Correction

C590 claimed class 17 suffix = NONE. This is incorrect. Class 17 has 4 suffix types: edy (68 tokens), eey (38), ain (33), aiin (31). The original SMALL_ROLE_ANATOMY analysis may have used a different morphological extraction method or a narrower class 17 definition.

## Impact on M2 Pass Rate

| Correction | Tests | Pass Rate |
|------------|-------|-----------|
| M2 original (C1025) | 12/15 | 80.0% |
| + B4 correction (C1030) | 13/15 | 86.7% |
| + C2 correction (this) | 14/15 | 93.3% |
| + B5 PREFIX-aware (C1032, future) | 15/15 | 100% (projected) |

Two of the three M2 failures were test misspecifications (B4, C2). Only B5 is a genuine model limitation requiring PREFIX-factored generation architecture.

## Related Constraints

- **C588:** Suffix role selectivity — CC is 100% suffix-free (using CC={10,11,12})
- **C590:** CC positional dichotomy — claims class 17 suffix = NONE (needs correction)
- **C1025:** Generative sufficiency — original 12/15 = 80%
- **C1030:** M2 gap decomposition — B4 misspecified, corrected to 13/15
- **C1032:** B5 asymmetry mechanism — genuine failure, needs PREFIX routing

## Provenance

- Scripts: `phases/C2_CC_SUFFIX_FREE/scripts/c2_diagnosis.py`, `c2_fix.py`
- Results: `phases/C2_CC_SUFFIX_FREE/results/c2_diagnosis.json`, `c2_fix.json`
- Date: 2026-02-14
