# C1192: SUFFIX Additive Composition

**Tier:** 2
**Phase:** 423 (POSITIONAL_ATOMICITY)
**Scope:** Currier B SUFFIX position

## Statement

SUFFIX compounds compose additively from position-specific atom profiles. Using SUFFIX-position behavioral profiles for each constituent atom, compound SUFFIX behavior is predicted with high accuracy (r=0.953, z=2.59, p=0.029, 16/17 testable compounds, leave-one-out circularity control). This extends C1190 (MIDDLE additive composition) to SUFFIX position.

## Key Results

| Metric | Value |
|--------|-------|
| Position-specific r | 0.953 |
| Cross-position baseline r | 0.676 |
| Improvement (delta) | +0.277 |
| Z-score | 2.59 |
| p-value | 0.029 |
| Compounds tested | 16/17 |

Cross-position baseline uses MIDDLE atom profiles to predict SUFFIX compounds (the "wrong variant") — position-specific profiles improve prediction by +0.277.

## Relationship to C1190 and C1191

- C1190 established additive composition for MIDDLE position (r=0.754)
- C1191 established position-dependent composition (different rules per position)
- C1192 proves SUFFIX follows the same additive principle as MIDDLE when position-specific atom profiles are used
- Composition is additive in both MIDDLE and SUFFIX; only PREFIX shows partial emergence

## Provenance

- Script: `phases/POSITIONAL_ATOMICITY/scripts/positional_atomicity_test.py` (T2)
- Strengthens: C1190, C1191
- Cross-references: C929 (PREFIX emergence expected for ch/sh)
