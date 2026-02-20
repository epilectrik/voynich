# C1145: Dark-Exclusive and Shared Atoms Occupy Equivalent Positional Slots

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphological construction
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

In 77 multi-atom dark-pipeline compounds, dark-exclusive and shared atoms occupy **equivalent** INITIAL/MEDIAL/FINAL positional slots with no significant differentiation.

### Positional Distribution

| Slot | Dark-Exclusive | Rate | Shared | Rate |
|------|---------------|------|--------|------|
| INITIAL | 21 | 39.6% | 56 | 50.5% |
| MEDIAL | 4 | 7.5% | 6 | 5.4% |
| FINAL | 28 | 52.8% | 49 | 44.1% |
| **Total** | **53** | | **111** | |

### Chi-Square Test

| Statistic | Value |
|-----------|-------|
| Chi-square | 1.742 |
| df | 2 |
| p | 0.421 |

Both atom types show a slight FINAL preference, consistent with the general compound construction pattern. Dark-exclusive atoms show a marginally higher FINAL rate (52.8% vs 44.1%) but this does not reach significance.

## Evidence

- Phase 409, Test 3: Chi-square on 2x3 contingency table (atom type x positional slot)
- 77 multi-atom compounds analyzed (of 200 total dark-pipeline compounds)
- Position determined by `mid.find(atom)` string position, sorted

## Implication

Dark-exclusive atoms are not confined to specific slots within compounds. They are positionally interchangeable with shared atoms, functioning as equivalent building blocks. Combined with C1143 (equivalent section profiles) and C1144 (not responsible for ordering divergence), this completes a picture of the dark-exclusive atom pool as quantitatively distinct (rarer, longer) but qualitatively equivalent (same slots, same section behavior, same construction role).

## Provenance

- Source: Phase 409, Test 3
- Related: C1060 (atom position grammar), C1142 (gateway/terminal preservation), C1143 (atom profile equivalence), C1144 (grammar modification)
