# C1451: Mode B Exclusive Forbidden Violation Concentration

**Tier:** 2
**Scope:** B, suffix, mode, hazard, forbidden, violation, Mode-A, Mode-B, C109, C1229, C1280, C1309
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

Mode B (bare/continuation suffix) concentrates 100% of forbidden pair violations: all 11 actual violations occur in Mode B tokens. Mode A (terminal/specification suffix) has zero violations. Mode B hazard rate (30.8%) is 3.2x Mode A hazard rate (9.5%). Mode A HEAD distribution is kernel-dominant (k=28.7%, e=26.9%); Mode B HEAD distribution is yield/arrange-dominant (e=31.5%, a=16.9%, o=11.7%).

## Evidence

### Mode hazard comparison

| Mode | N tokens | Hazard rate | Forbidden violations |
|------|----------|------------|---------------------|
| Mode A (specification) | 5,773 | 9.5% | 0 |
| Mode B (continuation) | 17,323 | 30.8% | 11 (100%) |

### HEAD distribution by mode

**Mode A:** k=28.7%, e=26.9%, a=8.8%, o=9.2%, i=7.8%
**Mode B:** e=31.5%, a=16.9%, o=11.7%, k=8.4%, i=3.4%

Mode A is kernel-dominant (k+e = 55.6%), consistent with specification/parametric function. Mode B is yield/flow-dominant (a+o = 28.6%), consistent with execution/continuation function.

### Violation attribution

All 11 forbidden pair violations (from 20,676 adjacency pairs):
- 11/11 occur in Mode B tokens (100%)
- 0/11 occur in Mode A tokens (0%)
- Expected under null (Mode B proportion = 75.0%): ~8.25 violations

The concentration exceeds even what Mode B's higher token share (75%) would predict.

## Interpretation

Mode A (specification) lines are inherently safe: they describe WHAT to do using kernel-centric vocabulary. Mode B (execution/continuation) lines carry all hazard risk: they carry out the work using yield/flow/transition vocabulary. This extends the Mode A/B distinction (C1229, C1309) from suffix typing and category emphasis to the hazard domain. Specification is safe by construction; execution is where violations occur. This is consistent with the distillation interpretation: writing down the recipe is never dangerous; actually doing the distillation is where things can go wrong.

## Falsification Criteria

1. If Mode A forbidden violations exceed 2 (given Mode A N=5,773)
2. If Mode A hazard rate exceeds 15%

## Method

- 23,096 clean Currier B tokens classified by suffix mode (Mode A = terminal/specification suffixes, Mode B = bare/continuation)
- Hazard = FLOW + CONTAINMENT categories (C1280)
- 20,676 adjacency pairs checked for forbidden pair violations
- HEAD atom distribution computed per mode

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions)
- C1229 (alternating suffix modes within paragraphs)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1309 (mode category specialization)
- C1382 (k/a atom-initial suffix mode polarization)
