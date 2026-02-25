# C1305: MIDDLE Determines Category -- Sister Pairs Diverge by Vocabulary Selection

**Tier:** 2
**Scope:** B
**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Date:** 2026-02-24

## Finding

0 of 33 qualifying MIDDLEs shift dominant category between ch and sh contexts (binomial p = 1.0). Sister pairs achieve category divergence entirely through MIDDLE vocabulary SELECTION, not MIDDLE category TRANSFORMATION.

## Method

- 115 MIDDLEs shared between ch and sh tokens
- 33 qualify (N >= 10 under both ch and sh)
- For each qualifying MIDDLE: compare 8-category profile under ch vs sh
- Per-MIDDLE Fisher exact test with Bonferroni correction
- Count MIDDLEs with shifted dominant category AND p < 0.00625

## Detail

All 33 tested MIDDLEs retain the same dominant category regardless of whether they appear after ch or sh:

| MIDDLE | N_ch | N_sh | ch dominant | sh dominant | Same? |
|--------|------|------|-------------|-------------|-------|
| e | 196 | 180 | THERMAL | THERMAL | Yes |
| dy | 135 | 57 | CONTAINMENT | CONTAINMENT | Yes |
| ck | 122 | 54 | MARKING | MARKING | Yes |
| d | 92 | 38 | MARKING | MARKING | Yes |
| ckh | 68 | 21 | CONTAINMENT | CONTAINMENT | Yes |
| ct | 59 | 26 | FLOW | FLOW | Yes |
| ... | ... | ... | ... | ... | All Yes |

## Interpretation

A MIDDLE's operational category is intrinsic -- it does not change based on which sister PREFIX selects it. The category divergence between ch and sh (C1299, V=0.121) arises because ch draws more heavily from certain MIDDLEs (CONTAINMENT, FLOW) while sh draws more heavily from others (THERMAL). The PREFIX acts as a vocabulary selector, choosing which MIDDLEs to deploy. It does not redefine what those MIDDLEs mean.

This is the mechanism behind sister pair divergence: differential MIDDLE selection, not contextual reinterpretation.

## Extends

- C1299 (ch/sh B category divergence) -- explains the mechanism
- C911 (PREFIX-MIDDLE selectivity) -- vocabulary selection is the operational channel
- C1219 (base determines MIDDLE content) -- MIDDLE category is a property of the MIDDLE, not the PREFIX

## Falsifiability

Would be falsified if >5 of 33 MIDDLEs shifted dominant category between ch and sh (shift rate > 15%).

## Evidence

- `phases/SISTER_CATEGORY_MECHANISM/results/sister_category_mechanism.json` (T3_middle_category_shift)
