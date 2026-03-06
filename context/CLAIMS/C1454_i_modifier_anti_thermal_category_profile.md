# C1454: i-Modifier Anti-Thermal Category Profile

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, category, anti-thermal, STAGING, TRANSITION, C1205, C1300, C1309
**Phase:** 524 (I_MODIFIER_HAZARD)
**Date:** 2026-03-05

## Claim

i-modified MIDDLEs are categorically anti-thermal: THERMAL = 0.05% (0.002x baseline of 23.4%). Category distribution is TRANSITION 41.0% (2.78x), STAGING 33.0% (2.58x), FLOW 22.3% (1.17x). PREFIX profile confirms: thermal PREFIXes (qo, ch, sh) carry i at 0.087-0.097x baseline rate, while non-thermal PREFIXes (da 3.5x, sa 3.6x, ok 2.4x, or 3.8x) concentrate i-tokens.

## Evidence

### Category distribution

| Category | i-fraction | Baseline | Ratio |
|----------|-----------|----------|-------|
| THERMAL | 0.05% | 23.4% | 0.002x |
| STAGING | 33.0% | 12.8% | 2.58x |
| TRANSITION | 41.0% | 14.8% | 2.78x |
| FLOW | 22.3% | 19.2% | 1.17x |
| OPERATION | 0.6% | 14.2% | 0.04x |
| MARKING | 1.1% | 7.7% | 0.14x |
| CONTAINMENT | 0.0% | 4.8% | 0.00x |
| MONITORING | 0.2% | 1.8% | 0.14x |

### PREFIX avoidance/concentration

| PREFIX | i-rate ratio | Domain |
|--------|-------------|--------|
| qo | 0.089x | Thermal (AVOIDED) |
| ch | 0.087x | Test (AVOIDED) |
| sh | 0.097x | Monitor (AVOIDED) |
| da | 3.51x | Infrastructure (CONCENTRATED) |
| sa | 3.59x | Non-thermal (CONCENTRATED) |
| or | 3.77x | Non-thermal (CONCENTRATED) |
| ok | 2.43x | Vessel (CONCENTRATED) |

### Section distribution

Bio section (most thermal) has lowest i-rate: 5.6% vs corpus 8.9% (0.64x). Stars/Recipe section has highest: 10.6% (1.19x).

## Interpretation

i is the anti-thermal modifier. It operates exclusively in the STAGING/TRANSITION/FLOW domain -- the "what to do between heating cycles" space. This structural finding independently confirms C1205 (i-atom orthogonal to k/e energy system) at the category level. The thermal PREFIXes (qo=heat source, ch/sh=testing) categorically exclude i, while the infrastructure/vessel PREFIXes (da, ok, sa) concentrate it. i marks iteration of non-thermal operations: cycling, staging, arranging, transitioning.

## Falsification Criteria

1. If i-token THERMAL fraction exceeds 5%
2. If qo-prefix i-rate ratio exceeds 0.5x
3. If Section B (Bio/thermal) i-rate exceeds corpus average

## Method

- 2,052 i-modified tokens classified by operational category (atom gloss plurality vote)
- PREFIX distribution compared between i-tokens and all tokens
- Section-level i-rates computed

**Script:** `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`
**Results:** `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`

## Dependencies

- C1205 (i-atom orthogonal to k/e energy system)
- C1250 (Gloss category structural coherence -- 8 categories)
- C1300 (qo near-pure THERMAL channel)
- C1309 (Mode category specialization)
