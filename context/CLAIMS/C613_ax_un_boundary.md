# C613: AX-UN Boundary

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase UN_COMPOSITIONAL_MECHANICS
**Scope:** B_INTERNAL | AX | UN

## Statement

AX-predicted UN tokens (2,150) occupy statistically similar positions (p=0.084) and have similar transition contexts to classified AX tokens. The ICC cosurvival threshold excludes morphologically complex AX variants that are behaviorally indistinguishable from classified AX. If absorbed, AX would grow from 4,140 (17.9%) to 6,290 (27.2% of B). The threshold is not "too strict" — it correctly identifies the core, high-frequency operators — but the boundary is continuous, not categorical.

## Evidence

### Position Test

| Metric | AX-predicted UN | Classified AX |
|--------|-----------------|---------------|
| Mean position | 0.445 | 0.483 |
| Std position | 0.374 | 0.340 |
| Mann-Whitney p | 0.084 (not significant) |

AX-predicted UN tokens occupy similar line positions to classified AX.

### Transition Context

| Preceding role | AX-predicted UN | Classified AX |
|---------------|-----------------|---------------|
| CC | 2.9% | 2.2% |
| EN | 31.9% | 33.4% |
| FL | 5.1% | 4.1% |
| FQ | 10.7% | 13.2% |
| AX | 16.4% | 17.3% |
| UN | 33.0% | 29.8% |

| Following role | AX-predicted UN | Classified AX |
|---------------|-----------------|---------------|
| CC | 4.3% | 2.7% |
| EN | 29.3% | 35.6% |
| FL | 5.7% | 4.3% |
| FQ | 10.9% | 15.0% |
| AX | 14.2% | 16.6% |
| UN | 35.7% | 26.0% |

Context distributions are qualitatively similar. The main difference: AX-predicted UN tokens are more likely to be surrounded by other UN tokens (33-36% vs 26-30%), which is expected — UN clusters with UN.

### Boundary Nature

The AX/UN boundary is **continuous, not categorical**:
- AX-predicted UN tokens have the same prefixes, similar positions, similar contexts
- They differ in morphological complexity: more suffixes, more articulators, longer forms
- The cosurvival threshold creates a clean cut through a continuous morphological gradient

### Absorption Impact

| If AX absorbed UN | Before | After |
|-------------------|--------|-------|
| AX token count | 4,140 | 6,290 |
| AX % of B | 17.9% | 27.2% |
| AX unique types | ~1,200 | ~3,500 |

## Related

- C570 (AX prefix patterns)
- C610 (UN morphological profile)
- C611 (UN role prediction — AX = 34.6% of UN)
- C612 (UN population structure)
