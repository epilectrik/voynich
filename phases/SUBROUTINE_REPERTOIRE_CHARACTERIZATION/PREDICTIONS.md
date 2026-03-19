# Phase 608: SUBROUTINE_REPERTOIRE_CHARACTERIZATION — Pre-Registered Predictions

## Pre-Phase Finding

Null test established folio zone repertoire breadth is significantly narrower than chance
(observed 1.675 vs expected 2.153, z=-0.781, t=-7.112, p<0.0001). 50% mono-type vs 33.8% expected.

## Predictions

### P1: THERMAL-MONITORING co-occurrence depletion (T1)
TQ-MP pair will be significantly depleted under section-stratified null (O/E < 0.70, p < 0.0083).
Basis: C1399 THERMAL-MONITORING mutual avoidance in transitions.

### P2: Low repertoire entropy (T2)
Observed signature entropy below section-stratified null mean.
Fewer than 8 of 15 possible signatures observed with n >= 3 folios.

### P3: Repertoire does NOT predict features beyond PREFIX (T3)
After controlling for PREFIX + section + paragraph_count via nested model comparison,
repertoire type will explain < 5% additional variance on all 5 features (F-test p > 0.05).

### P4: Section predicts repertoire (T4)
Section x repertoire significant (Fisher p < 0.01, V > 0.25). Expected/uninteresting.
Herbal has highest within-section signature entropy.

### P5: THERMAL-QO dominant mono-type (T5)
THERMAL-QO most common mono-type among 2+-paragraph folios (plurality).

### P6: Mono-type differs from multi-type (T5)
Mono-type folios differ from multi-type on >= 2/5 continuous features (MW p < 0.05).

## Verdict Tree

```
T1 hard exclusion (O/E=0, p<0.001 section-stratified) -> REPERTOIRE_CONSTRAINT_DISCOVERED
T3 >= 2 features significant (F + perm p<0.05)        -> REPERTOIRE_INDEPENDENTLY_INFORMATIVE
T1 >= 2 pairs significant, T3 null                     -> REPERTOIRE_STRUCTURED_PREFIX_MEDIATED
T1 < 2 pairs AND T3 null                               -> REPERTOIRE_WEAK
```

## Data Integrity
- Zone assignments: C1398 (4 zones, 264 paragraphs, silhouette=0.113)
- Section-stratified null is the primary inferential comparison
- T4 is descriptive only, does not drive verdict
