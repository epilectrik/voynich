# C1333: Kernel Is Most Stable Dimension Across Blocks

**Tier:** 2
**Scope:** B (all sections)
**Phase:** MULTIPLEXED_PROCEDURE_TEST (467)

## Constraint

Within-folio inter-block kernel distance is the most stable (lowest variance) dimension across blocks, lower than both category JSD and PREFIX JSD. This holds in every section tested.

## Evidence

From multiplexed_procedure_test.py test M4:

**Median inter-block distances (56 folios with 3+ blocks):**

| Dimension | Median Distance | vs Kernel MW p |
|-----------|----------------|----------------|
| Kernel (cosine) | 0.027 | — |
| Category (JSD) | 0.052 | 0.007 |
| PREFIX (JSD) | 0.145 | <0.001 |

- Kernel < Category in 36/56 folios
- Kernel < PREFIX in 56/56 folios (every folio)

**Section breakdown:**

| Section | Kernel | Category | PREFIX |
|---------|--------|----------|--------|
| B | 0.015 | 0.038 | 0.078 |
| C | 0.014 | 0.016 | 0.066 |
| H | 0.032 | 0.061 | 0.178 |
| S | 0.060 | 0.064 | 0.183 |
| T | 0.035 | 0.046 | 0.135 |

Kernel is the most stable dimension in every section. The gap is smallest in Section S (kernel 0.060 vs category 0.064) where blocks are single-paragraph monitoring checkpoints.

## Interpretation

The kernel composition (k/h/e ratio) is the invariant "key signature" shared by all blocks on a folio. PREFIX and category change across blocks (different operational emphasis, per C1318), but the thermal foundation stays constant. This is consistent with a shared energy source: all operations on a folio work under the same fire conditions.

Extends C1325 (folio REGIME homogeneity, within-folio kernel distance 0.056 < between-folio 0.065) by showing kernel is specifically MORE stable than other structural dimensions, not just "similar."

## Provenance

- multiplexed_procedure_test.json: test M4
- Relates to: C1325 (folio REGIME homogeneity), C1318 (block PREFIX complementarity), C1326 (cross-block category continuity)

## Status

CONFIRMED — kernel is the most stable inter-block dimension in every section.
