# C1453: i-Modifier Frame Selection, Not Inherent Hazard

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, hazard, causal, frame-selection, C1393, C1447, C1450
**Phase:** 524 (I_MODIFIER_HAZARD)
**Date:** 2026-03-05

## Claim

The i-modifier selects into hazardous HEAD+TERM frames (61.8% of i-tokens in high-hazard frames vs 14.0% non-i) but REDUCES hazard within frames. Marginal i-effect is negative (-0.0175): i-tokens have 22.3% hazard vs non-i 24.1%. Within-frame weighted delta is -0.407 with 12/19 frames showing negative (protective) deltas and only 2/19 positive. i is a frame-selection operator, not a hazard amplifier.

## Evidence

### Marginal vs within-frame decomposition

| Metric | Value |
|--------|-------|
| i-token hazard rate | 22.3% |
| Non-i hazard rate | 24.1% |
| Marginal delta | -0.0175 |
| Frame selection component | +0.390 |
| Within-frame (inherent) component | -0.407 |
| Frames tested | 19 |
| Positive delta frames | 2 |
| Negative delta frames | 12 |
| Zero delta frames | 5 |

### HEAD-controlled hazard comparison

| HEAD | N(i) | N(non-i) | i hazard | non-i hazard | Delta | p |
|------|------|----------|----------|-------------|-------|---|
| a | 1,351 | 1,728 | 32.6% | 71.2% | -38.6pp | <0.001 |
| o | 74 | 2,643 | 4.1% | 23.0% | -18.9pp | <0.001 |
| i | 570 | 485 | 0.0% | 6.4% | -6.4pp | <0.001 |

Within every major HEAD group, i-tokens have lower hazard than non-i tokens.

### Dominant frame: (a, n)

N=1,272 total. i-tokens (N=1,254): 33.5% hazard. Non-i tokens (N=18): 100% hazard. Delta = -66.5pp. The i-modifier dramatically reduces hazard in this frame by replacing FLOW-heavy non-i tokens (an, etc.) with the safer aiin/ain population.

## Interpretation

The Phase 523 finding that "i boosts hazard to 40.6%" (C1450) was correct for single-i tokens but masked the full picture. i's marginal hazard rate (22.3%) is actually BELOW baseline because the double-ii component (aiin at 0% hazard) pulls the average down. Within HEAD+TERM frames, i tokens are consistently safer. The apparent hazard boost is entirely a Simpson's paradox: i selects frames (a-initial, n-terminal) that happen to be in the FLOW/STAGING category space, but i-modified versions of those frames are less hazardous than their non-i counterparts.

## Falsification Criteria

1. If within-frame weighted delta exceeds +0.10 (i increases hazard within frames)
2. If marginal i-effect exceeds +0.05 (i increases overall hazard)
3. If fewer than 8/19 frames show negative deltas

## Method

- 23,096 tokens decomposed into HEAD+TERM frames via C1393 slot grammar
- Within-frame comparison: i-modified vs non-i tokens in same HEAD+TERM frame
- Weighted delta: sum(delta_f * weight_f) / sum(weight_f) across all frames with N>=3 in both groups
- HEAD-controlled: within-HEAD comparison pooling all TERMs
- Fisher exact test for significance

**Script:** `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`
**Results:** `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`

## Dependencies

- C1393 (HEAD + MOD* + TERM instruction encoding)
- C1447 (a-HEAD bifurcated hazard profile)
- C1450 (Modifier quenching: c,d,f,p,s -> 0%)
