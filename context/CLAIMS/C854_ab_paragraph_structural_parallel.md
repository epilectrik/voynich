# C854: A-B Paragraph Structural Parallel

**Tier:** 2
**Scope:** A-B
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

A and B paragraphs share parallel header-body architecture. Both systems show line-1 marker enrichment (A: RI 3.84x; B: HT +0.134 delta), statistically indistinguishable line counts, and 5-cluster natural taxonomies.

## Evidence

**Size comparison:**

| Dimension | A | B | Test |
|-----------|---|---|------|
| Paragraphs | 342 | 585 | - |
| Mean lines | 4.8 | 4.37 | Mann-Whitney p=0.067 |
| Mean tokens | 32.7 | 39.5 | Cohen's d=-0.192 |
| Tokens/line | 5.81 | 8.04 | - |

**Header enrichment:**

| System | Metric | Value |
|--------|--------|-------|
| A | RI line-1 concentration | **3.84x** |
| B | HT line-1 rate | 46.5% |
| B | HT body rate | 23.7% |
| B | HT delta | **+0.134** |

**Clustering:**
- A: k=5, silhouette=0.337
- B: k=5, silhouette=0.237
- Both systems partition into similar functional types

## Interpretation

The structural parallel confirms a shared design principle:
1. **Header zone**: Line 1 carries identification/marking vocabulary (RI for A, HT for B)
2. **Body zone**: Subsequent lines carry operational vocabulary (PP for A, classified 49-class for B)
3. **Size distribution**: Similar across systems (4-5 lines typical)
4. **Type taxonomy**: Both systems have short/standard/long paragraph variants

This validates the hypothesis that A provides *vocabulary pools* that B draws from (C846), while both systems use the same paragraph-based organizational structure (C827).

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C827 | CONFIRMS - Paragraphs as operational units (both systems) |
| C846 | ALIGNS - Pool-based relationship with shared structure |
| C840 | VALIDATES - B paragraph header-body pattern |
| C831 | VALIDATES - A paragraph RI structure |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/10_cross_system_summary.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/cross_system_summary.json`

## Status

CONFIRMED
