# C925: B Vocabulary Morphological Partition

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: B, A↔B
- **Status**: CLOSED
- **Source**: Phase EXTENSION_DISTRIBUTION_PATTERNS

## Statement

B's PP vocabulary partitions by morphological composition. B-exclusive MIDDLEs (66% of B) exhibit higher kernel-character density than shared/RI-base MIDDLEs. A's RI derivation draws selectively from the lower-density subset (~20% of B's PP).

## Evidence

### Vocabulary Partition

| Subset | Count | % of B | Kernel Density |
|--------|-------|--------|----------------|
| B-exclusive (A never uses) | 885 | 66.1% | ~1.00 (pure kernel) |
| RI bases (A derives from) | 264 | 19.7% | 0.76 |
| Shared directly with A | 404 | 30.2% | 0.77 |

### B-Exclusive Composition

Top B-exclusive MIDDLEs by frequency (all pure kernel):
- `ked` (32), `ched` (20), `lke` (20), `ted` (17)
- `ech` (34), `teed` (9), `keec` (8), `kech` (8)
- `tched` (7), `lt` (7), `eolk` (9)

These are composed entirely of kernel primitives (k, e, d, c, h, l, t, o, s, r).

### RI Base Selection

A-only MIDDLEs (RI) derive from only 264 PP bases - 19.7% of B's total vocabulary. RI bases show mixed composition (kernel density 0.76) rather than pure-kernel patterns.

## Interpretation

### What This Means

B's vocabulary has two morphologically distinct subsets:
1. **High-density subset** (B-exclusive): Pure kernel compositions, not used by A
2. **Lower-density subset** (shared/RI-base): Mixed compositions, A draws from this

A's RI derivation system (PP + extension) operates on the lower-density subset.

### What This Does NOT Mean

Per C522 (Construction-Execution Layer Independence), kernel-character composition and execution-level function are **independent regimes** (r=-0.21, p=0.07). This finding does NOT support:
- "Pure kernel = actions/verbs" (semantic over-interpretation)
- "Mixed composition = materials/nouns" (external category import)
- "A derives from B" (both derive from shared type system per C383)

The partition is **morphological**, not semantic.

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C501 | B-Exclusive MIDDLE Stratification - compatible |
| C522 | Construction-Execution Layer Independence - respected |
| C383 | Global Morphological Type System - compatible |
| C913 | RI Derivational Morphology - refined |
| C498 | Registry-Internal vocabulary track - compatible |

## Falsification Criteria

Disproven if:
1. Kernel density difference not significant on expanded analysis
2. B-exclusive vocabulary shown to have same composition as shared
3. RI bases shown to draw uniformly from all PP
