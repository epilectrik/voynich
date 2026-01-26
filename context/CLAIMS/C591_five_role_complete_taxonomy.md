# C591: Five-Role Complete Taxonomy

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The 49 Currier B instruction classes partition into 5 roles: CC (3-4 classes, ~4.4%), EN (18 classes, 31.2%), FL (4 classes, 4.7%), FQ (3-4 classes, ~12.5%), AX (19-20 classes, ~19.7%). All roles are near-100% PP at the MIDDLE type level. Total classified tokens cover the full Currier B corpus. Pipeline vocabulary is universal across all execution roles.

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_synthesis.py`

### Five-Role Summary

| Role | Classes | Tokens | % of B | PP% | Structure |
|------|---------|--------|--------|-----|-----------|
| CC | 3-4 | ~1,023 | ~4.4% | 100% | GENUINE |
| EN | 18 | 7,211 | 31.2% | 100% | CONVERGENCE |
| FL | 4 | 1,078 | 4.7% | 100% | GENUINE |
| FQ | 3-4 | ~2,890 | ~12.5% | 100% | GENUINE |
| AX | 19-20 | ~4,559 | ~19.7% | 98.2% | COLLAPSED |

Note: Ranges reflect disputed Class 14 (FQ vs AX) and Class 17 (CC vs AX).

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C121 | 49 instruction classes (Tier 0) |
| C573 | EN = 18 classes |
| C581 | CC census |
| C582 | FL census |
| C583 | FQ census |
| C572 | AX collapse |
| C574 | EN convergence |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C590_cc_positional_dichotomy.md](C590_cc_positional_dichotomy.md) | [INDEX.md](INDEX.md) ->
