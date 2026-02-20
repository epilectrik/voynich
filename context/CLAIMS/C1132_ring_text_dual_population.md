# C1132: Ring Text Dual Population Structure

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout — ring text
**Phase:** 404 (RING_TEXT_REGISTER_CHARACTERIZATION)

## Finding

Ring text tokens bifurcate into two distinct populations with contrasting morphological and functional properties:

### Population 1: B-Grammar Bridge Component (150 tokens, 52.4%)

| Property | Value |
|----------|-------|
| Mean token length | 4.0 characters |
| Kernel density | 27.3% |
| MIDDLE compound rate | 22.6% |
| Bridge MIDDLE fraction | **100%** |
| Instruction classes | 33 of 49 |

These are short, simple, bridge-connected tokens that all appear in the 479-type B grammar. Every single classified ring token has a bridge MIDDLE.

### Population 2: Unclassified Identification Component (136 tokens, 47.6%)

| Property | Value |
|----------|-------|
| Mean token length | 6.4 characters |
| Kernel density | 47.8% |
| MIDDLE compound rate | 49.5% |
| Bridge MIDDLE fraction | 22.1% |
| Instruction classes | N/A (outside B grammar) |

These are longer, more complex tokens with higher kernel density and compound rates. They are mostly non-bridge, suggesting vocabulary specific to the foldout's identification function.

### Contrast Summary

| Metric | Classified | Unclassified | Delta |
|--------|-----------|--------------|-------|
| Mean length | 4.0 | 6.4 | +2.4 chars |
| Kernel | 27.3% | 47.8% | +20.5pp |
| Compound | 22.6% | 49.5% | +26.9pp |
| Bridge | 100% | 22.1% | -77.9pp |

## Evidence

- Phase 404 test A4: Classified vs Unclassified comparison
- Length difference of 2.4 characters with kernel and compound rate divergence
- Bridge fraction divergence of 77.9 percentage points

## Implication

Ring text interleaves two functional vocabularies:
1. A **reference component** drawn entirely from bridge MIDDLEs — the vocabulary that connects A and B systems. These short, common tokens serve as the index entries.
2. An **identification component** of longer, more complex tokens outside the B grammar — foldout-specific vocabulary that labels or specifies concepts unique to the Rosettes diagram.

This dual structure mirrors the metalayer function (C1126): ring text both indexes into the B execution vocabulary (via bridges) and provides its own identification labels (via unclassified tokens).

## Provenance

- Source: Phase 404, Test A4
- Related: C1131 (register classification), C1126 (metalayer), C1013 (bridge = topological generality filter)
