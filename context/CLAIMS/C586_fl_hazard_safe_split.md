# C586: FL Hazard/Safe Structural Split

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FL divides into two genuine subgroups: hazard classes {7, 30} at medial positions (mean 0.55, 12.3% final) and safe classes {38, 40} at final positions (mean 0.81, 55.7% final). Mann-Whitney p=9.4e-20 for position, p=7.3e-33 for final rate. FL is hazard-source-biased: initiates hazards 4.5x more than receives (source=9, target=2 in corpus forbidden transitions).

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_hazard_anatomy.py`, `sr_internal_structure.py`

### Hazard vs Safe Subgroups

| Subgroup | Classes | Mean Pos | Final% | Hazard |
|----------|---------|----------|--------|--------|
| Hazard | 7, 30 | 0.546 | 12.3% | YES |
| Safe | 38, 40 | 0.811 | 55.7% | NO |

### Hazard Direction

| Role | Source | Target | Ratio |
|------|--------|--------|-------|
| FL | 9 | 2 | 4.50 (initiator) |
| EN | 5 | 11 | 0.45 (receiver) |
| FQ | 5 | 6 | 0.83 (bidirectional) |

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C541 | Hazard class enumeration |
| C542 | Class 30 gateway function |
| C546 | Class 40 safe flow |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C585_cross_role_middle_sharing.md](C585_cross_role_middle_sharing.md) | [INDEX.md](INDEX.md) ->
