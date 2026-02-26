# C1316: O-PREFIX Categorical Distinction

**Tier:** 2
**Scope:** B
**Phase:** DISTILLATION_TERMINOLOGY_MAPPING (461)
**Date:** 2026-02-25

## Finding

The four o-prefixed groups (ok, ot, ol, or) have statistically distinct 8-category operational profiles:

- Chi-square contingency (4x8): p < 0.001
- 3 of 4 o-prefixes show a distinct dominant category

| O-PREFIX | N | Top Category | Rate | Second | Rate |
|----------|---|-------------|------|--------|------|
| ok | 1,476 | FLOW | 27.6% | TRANSITION | 26.5% |
| ot | 1,448 | FLOW | 27.9% | TRANSITION | 25.2% |
| ol | 875 | THERMAL | 42.2% | TRANSITION | 17.9% |
| or | 173 | TRANSITION | 39.3% | FLOW | 29.5% |

## ok vs ot Refinement

ok and ot share similar atom composition (both e-dominant: ok=0.282, ot=0.258) but differ in category emphasis:
- ok: THERMAL 24.7%, OPERATION 12.5%
- ot: THERMAL 20.2%, OPERATION 17.3%
- Delta: ok is +4.4% THERMAL, ot is +4.9% OPERATION

Directional transition asymmetry: ok->ot = 1.18x expected (115 obs, 97.2 exp), ot->ok = 1.04x (101 obs). Asymmetry ratio = 1.14. Trigram qo->ok->ot (23) > qo->ot->ok (21). ok systematically precedes ot.

## Extends

- C408 (ok/ot sister pair) — sisters are confirmed distinct at category level
- C911 (PREFIX-MIDDLE selection) — o-prefixes select different MIDDLE families despite shared initial
- C1250 (8-category system) — categories discriminate within the o-prefix family

## Falsifiability

Would be falsified if chi-square p > 0.01 for the 4x8 contingency, or if ok->ot asymmetry reverses (ot->ok > ok->ot consistently).

## Evidence Files

- `phases/DISTILLATION_TERMINOLOGY_MAPPING/results/distillation_terminology_mapping.json` (T8)
- `phases/DISTILLATION_TERMINOLOGY_MAPPING/results/distillation_terminology_mapping.json` (post_phase_analysis)
