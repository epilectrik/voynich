# C1138: Dark Pipeline Has Distinct Construction Grammar

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphology
**Phase:** 407 (DARK_PIPELINE_FUNCTIONAL_TEST)

## Finding

B tokens built from dark-pipeline MIDDLEs use a **distinct morphological construction pattern** compared to general HT/UN tokens, despite being 100% HT/UN classified (C1137).

### PREFIX Distribution

| Category | Dark Pipeline | General HT/UN | Grammar |
|----------|--------------|---------------|---------|
| Grammar-standard (ch, sh, qo, etc.) | 59.1% | 53.9% | 68.7% |
| Extended (yk, sa, al, do, etc.) | 17.5% | 29.8% | 14.3% |
| No prefix | 23.4% | 16.3% | 17.0% |

Grammar-standard/extended ratio: dark = 3.39, general HT = 1.81 (87% higher in dark pipeline).

### Morphological Profile

| Feature | Dark Pipeline | General HT/UN (C610) | Grammar (C610) |
|---------|--------------|---------------------|----------------|
| Suffix rate | 89.9% | 77.3% | 38.7% |
| Articulator rate | 2.5% | 10.1% | 1.9% |

Dark-pipeline tokens have **higher suffix attachment** than general HT (+12.6pp) and **lower articulator use** (-7.6pp). They are morphologically simpler at the front (fewer articulators, more grammar-standard prefixes) but more elaborated at the back (higher suffix rate).

## Evidence

- Phase 407, Test 2: PREFIX/SUFFIX analysis of 1,696 dark-pipeline B tokens
- Bifurcation threshold: GS/EXT ratio difference > 50% (observed: 87%)
- Comparison populations: 7,042 general HT/UN tokens, 16,054 grammar tokens

## Implication

The dark pipeline constructs its HT/UN tokens using a specific morphological recipe: grammar-standard prefixes (selecting operational domains) + dark-pipeline MIDDLEs (providing compound identification content) + high suffix attachment (encoding additional context). This is distinct from both the general HT construction pattern (which uses more extended/HT-specific prefixes and more articulators) and the grammar construction pattern (which has low suffix rates). The dark pipeline is a third morphological register within B's token inventory.

## Provenance

- Source: Phase 407, Test 2
- Related: C1137 (100% HT substrate), C347 (HT prefix disjoint), C610 (UN morphological profile), C611 (UN role prediction)
