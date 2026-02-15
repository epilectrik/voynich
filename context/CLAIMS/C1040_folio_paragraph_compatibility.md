# C1040: A Folio-Level Paragraph Compatibility Coherence

**Tier:** 2
**Scope:** Currier-A
**Phase:** A_PARAGRAPH_COMBINATORICS (Phase 364)

## Constraint

Within-folio paragraph pairs show significantly higher MIDDLE compatibility than between-folio pairs, and this effect survives section matching. Folio identity imposes compatibility structure beyond section membership.

## Evidence

Cross-paragraph PP MIDDLE compatibility (fraction of cross-paragraph pairs that are C475-legal):

| Comparison | N pairs | Median compatibility | Mann-Whitney p |
|------------|---------|---------------------|----------------|
| Within-folio | 728 | 0.880 | - |
| Between-folio | 4,997 | 0.811 | ~0 |
| Section-matched between-folio | 2,409 | 0.810 | ~0 |

Both comparisons highly significant. The within-folio advantage (0.880 vs 0.810-0.811) is not explained by section structure.

## Interpretation

This is the paragraph-level analog of C704 (folio PP pool size). Folios don't just have a shared PP pool -- the paragraphs within a folio draw from a compatibility-coherent subset of the MIDDLE space. The folio is a designed unit of compatibility, not just a container.

## Supports

- **C233:** LINE_ATOMIC -- paragraphs are independent but folio constrains their vocabulary pool
- **C704:** Folio PP pool size
- **C729:** C475 record-level scope

## Provenance

- 728 within-folio pairs, 4997 between-folio pairs (sampled), 2409 section-matched
- Data: `phases/A_PARAGRAPH_COMBINATORICS/results/a_paragraph_combinatorics.json`
