# C1452: Non-Monotonic i-Extension Hazard Gradient

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, extension, hazard, non-monotonic, C1197, C1234, C1280, C1450
**Phase:** 524 (I_MODIFIER_HAZARD)
**Date:** 2026-03-05

## Claim

The i-modifier extension gradient is non-monotonic: no-i = 24.1% hazard (N=21,044), single-i = 39.8% (N=1,151), double-ii = 0.0% (N=901). Single-i tokens (ain, iin, aii) are STAGING-dominant (53.3%) with high FLOW (39.8%), producing elevated hazard. Double-ii tokens (aiin, oiin) are TRANSITION-dominant (92.6%) with zero FLOW, producing zero hazard. aiin (N=834) has exactly 0% hazard rate.

## Evidence

### Extension gradient

| Level | N | Hazard Rate | FLOW fraction | TRANSITION fraction |
|-------|---|-------------|---------------|---------------------|
| No i | 21,044 | 24.1% | 18.9% | 12.2% |
| Single i | 1,151 | 39.8% | 39.8% | 0.7% |
| Double ii | 901 | 0.0% | 0.0% | 92.6% |

### Double-ii complete safety

All 34 distinct double-ii MIDDLEs have 0.0% hazard rate. aiin (834 tokens) = 0 forbidden violations, 0 FLOW/CONTAINMENT tokens. oiin (32 tokens) = 0 hazard. No exceptions.

### Category split

Single-i category: STAGING 53.3%, FLOW 39.8%, UNKNOWN 2.9%
Double-ii category: TRANSITION 92.6%, STAGING 7.1%, MARKING 0.2%

The FLOW component is the hazard source. Single-i has it (39.8%), double-ii does not (0.0%).

## Interpretation

The extensibility split (C1197) has a direct hazard consequence. Single-i encodes open/unbounded iteration (cycling through material), which involves FLOW operations with inherent physical risk. Double-ii encodes formal bounded iteration (predetermined endpoint), which maps to TRANSITION (state change) with zero risk. This aligns with C1234: iin = cycle setup (FLOW, potentially hazardous), aiin = bounded loop control (TRANSITION, safe).

In the distillation model: open cycling involves moving material through the apparatus (overflow risk), while bounded iteration means waiting for equilibrium (no material movement = no risk).

## Falsification Criteria

1. If double-ii MIDDLEs exceed 2% hazard rate
2. If single-i FLOW fraction drops below 25%
3. If the gradient becomes monotonic with new data

## Method

- 23,096 clean Currier B tokens decomposed by MIDDLE atom structure
- i-count classified: 0 (no-i), 1 (single-i), 2+ (double-ii)
- Hazard = FLOW + CONTAINMENT categories (C1280)
- Category assignment via atom gloss plurality vote (CategoryClassifier)

**Script:** `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`
**Results:** `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`

## Dependencies

- C1197 (Only e and i repeat consecutively at structural levels)
- C1234 (Iteration two-track: iin cycle setup, aiin bounded loop)
- C1280 (Hazard concentrates in FLOW/CONTAINMENT)
- C1309 (Mode category specialization)
- C1450 (Modifier quenching is categorical for c,d,f,p,s)
