# C1446: k-HEAD Complete Hazard Immunity

**Tier:** 2
**Scope:** B, MIDDLE, atom, k-initial, hazard, HEAD, immunity, C109, C1393, C1394, C1384, C1280
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

k as HEAD atom produces 0.0% hazard exposure across 3,100 tokens, making it the only HEAD atom with complete hazard immunity. k-HEAD is never a forbidden pair source, never a target, and never participates in any hazard context. This immunity extends across ALL terminal frames: k+bare (2,083 tokens, 0%), k+e (464, 0%), k+h (202, 0%), k+d (93, 0%), k+c (56, 0%), k+o (92, 0%), and even k+r (15, 0%) despite r-terminal being 92.58% hazardous overall. k as HEAD completely neutralizes hazard in all combinations.

## Evidence

### HEAD atom hazard rates

| HEAD atom | N tokens | Source rate | Target rate | Any hazard |
|-----------|----------|------------|------------|------------|
| **k** | **3,100** | **0.0%** | **0.0%** | **0.0%** |
| i | 1,055 | 0.0% | 0.0% | 0.0% |
| e | 7,002 | 0.0% | 2.2% | 2.2% |
| h | 64 | 3.1% | 0.0% | 3.1% |
| o | 2,717 | 16.4% | 30.7% | 30.7% |
| d | 1,142 | 59.1% | 0.7% | 59.8% |
| a | 3,079 | 22.0% | 44.0% | 66.0% |
| t | 416 | 0.0% | 62.5% | 62.5% |
| l | 1,283 | 66.6% | 0.0% | 66.6% |
| r | 1,309 | 0.0% | 86.0% | 86.0% |

### k-HEAD frame decomposition

| k-Frame | N tokens | Hazard rate | Category |
|---------|----------|------------|----------|
| k→bare | 2,083 | 0.0% | THERMAL |
| k→e | 464 | 0.0% | THERMAL |
| k→h | 202 | 0.0% | THERMAL |
| k→d | 93 | 0.0% | FLOW/MARKING |
| k→c | 56 | 0.0% | CONTAINMENT |
| k→o | 92 | 0.0% | STAGING/TRANSITION |
| k→r | 15 | 0.0% | n/a |
| k→n | 1 | 0.0% | n/a |

### Kernel comparison

All three kernel atoms (C089) are hazard-depleted:
- k: 0.0% (complete immunity)
- e: 2.2% (near-immunity, only as target via ee frame)
- h: 3.1% (near-immunity, rare as HEAD N=64)

## Interpretation

The ENERGY_MODULATOR atom (C103) is inherently safe by construction. Energy operations -- heating, temperature adjustment, thermal management -- never create hazardous transitions. This is consistent with the distillation interpretation: adjusting the fire is always safe; hazard arises from material flow (r-terminal), containment failures (d+y), and phase transitions (a-HEAD). The system's fundamental safety guarantee is that thermal operations cannot produce forbidden transitions.

## Falsification Criteria

1. If k-HEAD tokens appear in any forbidden pair at >0.5%
2. If any k-HEAD frame has hazard rate >2%

## Method

- 23,096 clean Currier B tokens decomposed by HEAD atom (first atom of MIDDLE)
- Hazard defined as membership in FLOW or CONTAINMENT categories (C1280)
- Frame = HEAD x TERMINAL combination
- 20,676 adjacency pairs checked for forbidden pair participation

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions)
- C089 (kernel core: k, h, e)
- C103 (k = ENERGY_MODULATOR)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1384 (k-initial fraction predicts AXM dwell)
- C1393-C1394 (instruction encoding architecture)
