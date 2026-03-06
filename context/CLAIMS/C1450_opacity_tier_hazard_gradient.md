# C1450: Opacity Tier Hazard Gradient

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, hazard, opacity, gradient, suffix, C1440, C1447, C1280
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

The three-tier terminal opacity gradient (C1440) produces a monotonic hazard gradient: SEMI_TRANSPARENT terminals (l, r) concentrate hazard at 56.5%, 2.5x the OPAQUE rate (22.8%), while TRANSPARENT terminals (h) are 0% hazard. Suffixed tokens have 2.44x lower hazard (14.6%) than unsuffixed tokens (35.6%). The hazard/opacity interaction reveals that suffix attachment is a hazard-reduction mechanism.

## Evidence

### Opacity tier hazard rates

| Opacity Tier | Terminals | N tokens | Hazard rate | Suffix rate |
|-------------|-----------|----------|------------|-------------|
| OPAQUE | n, y, m | 6,620 | 22.8% | 1.2% |
| SEMI_TRANSPARENT | l, r | 2,926 | 56.5% | 10.3% |
| TRANSPARENT | h | 1,236 | 0.0% | 98.6% |

### Suffix status and hazard

| Suffix status | N tokens | Hazard rate |
|--------------|----------|------------|
| Suffixed | 11,151 | 14.6% |
| Unsuffixed | 11,945 | 35.6% |

Ratio: unsuffixed/suffixed = 2.44x hazard concentration in bare tokens.

### Cross-tier pattern

- TRANSPARENT (h): obligatory suffix, zero hazard -- specification always safe
- SEMI_TRANSPARENT (l, r): partial suffix, highest hazard -- the boundary zone
- OPAQUE (n, y, m): minimal suffix, moderate hazard -- self-contained operations

The SEMI_TRANSPARENT tier sits at the hazard/suffix boundary: these terminals allow but do not require suffix attachment, and they carry the system's highest hazard concentration.

## Interpretation

The opacity gradient (C1440) is not just a morphological property -- it has hazard consequences. TRANSPARENT terminals that obligatorily take suffixes are completely safe (h at 0%). SEMI_TRANSPARENT terminals that optionally take suffixes are maximally dangerous (l, r at 56.5%). The suffix layer functions as a hazard-reduction mechanism: attaching a suffix to a MIDDLE signals specification rather than raw execution, reducing hazard exposure. This extends C1440 from a morphological finding to a safety-relevant architectural feature.

## Falsification Criteria

1. If SEMI_TRANSPARENT hazard drops below OPAQUE hazard
2. If TRANSPARENT terminals (h) exceed 5% hazard
3. If suffixed/unsuffixed hazard ratio drops below 1.5x

## Method

- 23,096 clean Currier B tokens classified by C1440 opacity tiers
- Hazard = FLOW + CONTAINMENT categories (C1280)
- Suffix status determined by Morphology extractor
- Cross-tabulation of opacity tier x hazard and suffix status x hazard

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1437 (m-terminal complete hazard exclusion)
- C1440 (three-tier terminal opacity gradient)
- C1447 (terminal atom hazard partition)
