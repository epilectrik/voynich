# C587: FQ Internal Differentiation

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FQ shows 4-way genuine structure (100% KW significance, mean J-S 0.014). Class 9 (aiin/o/or) is medial, prefix-free, self-chaining (8.6%); Classes 13/14 (ok/ot-prefixed) are medial, large, non-hazardous, suffix-poor; Class 23 (d/l/r/s/y) is final-biased (29.8%), morphologically minimal. Class 9 vs others: p=3.9e-7; Classes 13 vs 14: p=1.6e-10 (positional).

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_internal_structure.py`

### Class Profiles

| Class | Tokens | Prefix | Position | Final% | Self-chain |
|-------|--------|--------|----------|--------|------------|
| 9 | 630 | NONE | 0.504 | 3.6% | 8.6% |
| 13 | 1,191 | ok | 0.530 | 5.6% | 8.6% |
| 14 | 707 | ot | 0.615 | 11.2% | 5.7% |
| 23 | 362 | NONE | 0.627 | 29.8% | 1.4% |

### Statistical Tests

| Test | H/U | p-value | Significant |
|------|-----|---------|-------------|
| KW Position | 84.7 | 3.0e-18 | YES |
| KW Initial | 75.3 | 3.1e-16 | YES |
| KW Final | 220.4 | 1.6e-47 | YES |
| KW Token Length | 2516.9 | 0.0 | YES |
| Class 9 vs others | U=618K | 3.9e-7 | YES |

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C559 | SUPERSEDED (wrong membership) |
| C561 | Class 9 or->aiin bigram |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C586_fl_hazard_safe_split.md](C586_fl_hazard_safe_split.md) | [INDEX.md](INDEX.md) ->
