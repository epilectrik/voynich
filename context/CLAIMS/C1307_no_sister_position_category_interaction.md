# C1307: No Sister x Category x Position Three-Way Interaction

**Tier:** 2
**Scope:** B
**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Date:** 2026-02-24

## Finding

The magnitude of sister pair category divergence does not vary systematically across position zones. ch/sh V range = 0.009 (perm p = 1.0), ok/ot V range = 0.114 (perm p = 1.0). No three-way interaction exists between sister identity, operational category, and line position.

## V by Zone

| Pair | EARLY | MID | LATE | Range |
|------|-------|-----|------|-------|
| ch/sh | 0.094 | 0.097 | 0.102 | 0.009 |
| ok/ot | 0.207 | 0.125 | 0.093 | 0.114 |

## Method

- Per zone: Cramer's V for sister x category
- V range = max(V) - min(V) across zones
- Permutation test: 1000 permutations of sister labels within zones, compute V range
- Significance: observed V range compared to permutation distribution

## Interpretation

For ch/sh, the V is remarkably stable across zones (0.094-0.102), confirming a uniform category effect regardless of position. For ok/ot, the V appears to decline from EARLY to LATE (0.207 to 0.093), but this pattern is within permutation bounds (p=1.0), meaning the apparent gradient is consistent with sampling variation. The sister pair's categorical signal is additive with position, not interactive: knowing the sister identity gives the same category information regardless of where in the line you are.

## Extends

- C1303 (ch/sh position-independent) -- confirms additivity, no interaction
- C1304 (ok/ot position-independent) -- apparent gradient is not significant
- C929 (ch later, sh earlier) -- positional axis truly orthogonal to category axis

## Falsifiability

Would be falsified if permutation p < 0.01 for either pair (position modulates the category effect).

## Evidence

- `phases/SISTER_CATEGORY_MECHANISM/results/sister_category_mechanism.json` (T6_three_way_interaction)
