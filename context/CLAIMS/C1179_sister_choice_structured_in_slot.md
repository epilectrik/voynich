# C1179: Sister Choice Is Structured Even Within Identical MIDDLE+SUFFIX Slots

**Tier:** 2
**Scope:** B, sister pairs, within-class variation
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C408, C409

## Statement

Sister-pair choice (ch vs sh) is NOT purely random even when MIDDLE and SUFFIX are held constant. Of 174 testable MIDDLE+SUFFIX+section slots (both sisters present, n>=5), 14 (8.0%) show Bonferroni-significant deviation from equal probability. The aggregate chi-squared test is highly significant (chi2=709.8, df=174, p<0.0001). The grand ch/(ch+sh) ratio in testable slots is 0.629, confirming the known ch-dominance (C637) persists even within matched morphological environments.

## Evidence

| Metric | Value |
|--------|-------|
| Testable slots (MIDDLE+SUFFIX+section) | 174 |
| Grand ch/(ch+sh) | 0.629 |
| Bonferroni-significant slots | 14/174 (8.0%) |
| Aggregated chi2 | 709.8 |
| Aggregated df | 174 |
| Aggregated p | <0.0001 |

## Interpretation

The 52.9% unexplained variance in C639 contains genuine structure, not just noise. Even in the most controlled comparison possible (same MIDDLE, same SUFFIX, same section, only PREFIX differs), sister choice deviates from randomness. This rules out the null hypothesis that sister pairs are fully interchangeable within morphological context.

## Provenance

- Phase 420 Test 0: SLOT_EQUIVALENCE
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test0_slot_equivalence
