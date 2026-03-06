# C1474: s-Modifier Universal Connector via Centroid Proximity and FQ Context

**Tier:** 2
**Scope:** B, MIDDLE, atom, modifier, s, co-occurrence, universality
**Phase:** MODIFIER_FUNCTIONAL_GROUPING (Phase 532)
**Depends on:** C1472 (modifier co-occurrence avoidance), C1473 (frame incompatibility), C1391 (s-atom staging sequence profile)

## Constraint

Atom s is the only modifier that co-occurs with ALL 5 other modifiers {p,c,i,f,d}. Three mechanisms explain this universality: (1) s has the LOWEST mean behavioral distance to all other modifiers (0.1176 vs next-lowest c at 0.1518) -- it is the behavioral centroid of the modifier space, (2) s has a BROAD HEAD distribution (entropy 1.909, 4 HEADs above 6.5%) compatible with all narrow-HEAD modifiers' frame demands, and (3) s primarily operates in the FQ macro-state (C1391: 64.6%, 3.59x enrichment) rather than AXM, providing an orthogonal execution context that does not compete with AXM-confined modifiers p (88.7% AXM) and c (93.5% AXM). s is a **sequencing connector** -- it adds temporal/ordering structure to any modifier without conflicting with that modifier's frame demands.

## Key Evidence

| Metric | s | Next closest |
|--------|---|-------------|
| Mean JSD to all others | 0.1176 | c: 0.1518 |
| HEAD entropy | 1.909 | f: 1.696 |
| Section entropy | 2.022 | f: 2.101 |
| Co-occurring partners | 5/5 (100%) | c: 4/5, d: 3/5 |

### s Distance to Each Modifier

| Partner | JSD to s | Co-occurs? |
|---------|----------|-----------|
| c | 0.0180 | Yes |
| p | 0.0603 | Yes |
| f | 0.0482 | Yes |
| d | 0.1882 | Yes |
| i | 0.2734 | Yes |

s is closest to c (JSD 0.018) and farthest from i (JSD 0.273), yet co-occurs with both. This is consistent with universal frame compatibility rather than behavioral similarity as the co-occurrence mechanism.

## Falsification

Would be falsified if: (1) s were shown to have a narrow HEAD selectivity comparable to d or i, or (2) s lost co-occurrence with any modifier in a larger corpus, or (3) s's FQ macro-state assignment were shown to be an artifact.

## Provenance

- `phases/MODIFIER_FUNCTIONAL_GROUPING/scripts/modifier_functional_grouping.py` -- Phase 532 analysis
- `phases/MODIFIER_FUNCTIONAL_GROUPING/results/modifier_functional_grouping.json` -- structured results
