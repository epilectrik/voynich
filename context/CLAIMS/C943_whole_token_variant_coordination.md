# C943: Whole-Token Variant Coordination Carries Section Signal

**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** MATERIAL_LOCUS_SEARCH

## Statement

PREFIX+SUFFIX coordination on the same MIDDLE is section-specific, with 60% of variant-section mutual information persisting after conditioning on PREFIX compatibility (C911). Residual MI = 0.105 bits (p=0.0, permutation test). 97.6% of tested MIDDLEs show Cramer's V > 0.2 for variant × section association. The way tokens are assembled (which prefix+suffix combination wraps a given MIDDLE) carries section information beyond what PREFIX-MIDDLE compatibility alone explains.

## Evidence

### Mutual Information Decomposition

| Metric | Value |
|--------|-------|
| Raw MI (variant; section) | 0.174 bits |
| Conditional MI (variant; section | prefix_class) | 0.105 bits |
| Residual fraction | 60% |
| Permutation p-value | 0.0 (0/1000 permutations exceeded) |

### Per-MIDDLE Cramer's V (variant × section)

| Metric | Value |
|--------|-------|
| MIDDLEs tested | 41 (3+ sections, 10+ tokens/section) |
| Mean V | 0.298 |
| MIDDLEs with V > 0.2 | 40/41 (97.6%) |
| MIDDLEs significant at p<0.01 | 38/41 (92.7%) |

### Method

23,096 Currier B tokens. Token variants defined as (PREFIX, SUFFIX) pairs on each MIDDLE. MI decomposition: I(variant; section) - I(variant; section | prefix_class) = residual section signal. 1,000 permutations.

## Implication

Token-level assembly carries section identity. When the same MIDDLE (e.g., `ed`) appears in different sections, it is wrapped with different prefix+suffix combinations at rates that exceed what PREFIX-MIDDLE compatibility (C911) predicts. This is the strongest evidence that material/section identity is encoded combinatorially — distributed across the assembly pattern rather than concentrated in any single morphological slot.

## Related

C733, C911, C909, C941, C942
