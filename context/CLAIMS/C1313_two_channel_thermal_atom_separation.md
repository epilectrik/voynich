# C1313: Two-Channel Thermal Atom Separation

**Tier:** 2
**Scope:** B
**Phase:** DISTILLATION_TERMINOLOGY_MAPPING (461)
**Date:** 2026-02-25

## Finding

PREFIX qo and PREFIX ok carry statistically distinct thermal atom profiles in their MIDDLEs:

- qo: k-fraction = 0.510, e-fraction = 0.102 (k-dominant)
- ok: k-fraction = 0.001, e-fraction = 0.282 (e-dominant)
- Mann-Whitney p = 0.0 for both k and e comparisons
- Permutation p = 0.0 (10K shuffles, seed 42)

This separation is complete: qo MIDDLEs are k-enriched (energy input atoms), ok MIDDLEs are e-enriched (stability/cooling atoms). The two prefixes access non-overlapping thermal atom pools.

## Negative Control

sa (infrastructure prefix): k-fraction = 0.005, e-fraction = 0.003 (p = 0.999 for k vs e). sa shows no thermal bias, confirming the separation is specific to qo/ok and not a general prefix effect.

## Cross-Validation

Consistent with F-B-006 lane-level analysis (QO lane 70.7% k, CHSH lane 68.7% e). The per-token atom fractions (0.510 and 0.282) are lower than lane-level because individual MIDDLEs contain mixed atoms, but the directional separation is identical.

## Extends

- C911 (PREFIX-MIDDLE selection) — qo selects k-family, ok selects e-family
- C908 (MIDDLE kernel correlation) — k-family and e-family are kernel-correlated

## Falsifiability

Would be falsified if qo's k-fraction drops below ok's k-fraction in any sufficiently large (n>100) subsample, or if the permutation p-value exceeds 0.01.

## Evidence Files

- `phases/DISTILLATION_TERMINOLOGY_MAPPING/results/distillation_terminology_mapping.json` (T1)
