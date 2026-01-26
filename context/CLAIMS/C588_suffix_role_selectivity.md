# C588: Suffix Role Selectivity

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Suffix usage is strongly role-dependent (chi2=5063.2, p<1e-300). Three suffix strata: SUFFIX-RICH (EN: 17 types, 39% suffix-less), SUFFIX-MODERATE (AX: 19 types, 62% suffix-less), SUFFIX-DEPLETED (FL: 2 types, 93.8%; FQ: 1 type, 93.4%; CC: 0 types, 100%). EN and AX share suffix vocabulary (Jaccard 0.800); CC/FL/FQ are suffix-isolated.

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_suffix_analysis.py`

### Suffix Inventory by Role

| Role | Suffix Types | Suffix-less % | Top Suffix |
|------|-------------|---------------|------------|
| CC | 0 | 100.0% | (none) |
| EN | 17 | 39.0% | edy (13.7%) |
| FL | 2 | 93.8% | r (5.2%) |
| FQ | 1 | 93.4% | edy (6.6%) |
| AX | 19 | 62.3% | edy (7.9%) |

### Suffix Jaccard Matrix

| | CC | EN | FL | FQ | AX |
|-|----|----|----|----|-----|
| CC | - | 0.000 | 0.000 | 0.000 | 0.000 |
| EN | | - | 0.118 | 0.059 | 0.800 |
| FL | | | - | 0.000 | 0.105 |
| FQ | | | | - | 0.053 |
| AX | | | | | - |

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C293 | TOKEN = [ART] + [PFX] + MID + [SFX] |
| C267 | PREFIX encodes structural properties |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C587_fq_internal_differentiation.md](C587_fq_internal_differentiation.md) | [INDEX.md](INDEX.md) ->
