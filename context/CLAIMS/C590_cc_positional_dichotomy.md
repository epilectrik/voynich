# C590: CC Positional Dichotomy

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> CC has a genuine positional dichotomy: Class 10 (daiin) is initial-biased (mean 0.413, 27.1% initial) while Class 11 (ol) is medial (mean 0.511, 5.0% initial). Mann-Whitney p=2.8e-5. CC is 100% suffix-free (zero suffix types across all classes). Class 12 (k) is a ghost class with zero corpus tokens (C540). Class 17 (ol-derived, C560) is positionally neutral (mean ~0.5).

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_internal_structure.py`, `sr_feature_matrix.py`

### CC Class Positions

| Class | Token | Mean Pos | Init% | Final% | Suffix |
|-------|-------|----------|-------|--------|--------|
| 10 | daiin | 0.413 | 27.1% | 7.6% | NONE |
| 11 | ol | 0.511 | 5.0% | 9.5% | NONE |
| 12 | k | - | - | - | GHOST |
| 17 | olaiin... | ~0.50 | 6.6% | 9.7% | NONE |

### Statistical Tests

| Test | Value | p-value |
|------|-------|---------|
| KW Position | 17.5 | 2.8e-5 |
| KW Initial | 71.0 | 3.6e-17 |
| KW Token Length | 734.0 | 1.2e-161 |
| Mann-Whitney (10 vs 11) | 54,192 | 2.8e-5 |

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C540 | Kernel k never standalone |
| C557 | daiin line-initial trigger |
| C558 | Singleton class structure |
| C560 | Class 17 ol-derivation |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C589_small_role_genuine_structure.md](C589_small_role_genuine_structure.md) | [INDEX.md](INDEX.md) ->
