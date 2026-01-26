# C582: FL Definitive Census

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FLOW_OPERATOR comprises 4 classes {7, 30, 38, 40} with 1,078 tokens (4.7% of B). BCSC listed only 2 classes (undercount). Classes 7 (ar/al, 434 tokens) and 30 (dar/dal, 522 tokens) are hazard-involved; Classes 38 (50 tokens) and 40 (72 tokens) are non-hazardous and strongly final-biased (50-60% final rate).

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_census_and_inventory.py`

### Per-Class Counts

| Class | Tokens | Examples | Hazard | Final% |
|-------|--------|----------|--------|--------|
| 7 | 434 | ar, al | YES | 9.9% |
| 30 | 522 | dar, dal, dain | YES | 14.4% |
| 38 | 50 | aldy, aral | no | 50.0% |
| 40 | 72 | aly, ary, daly | no | 59.7% |

### MIDDLE Inventory

- 17 unique MIDDLEs, 100% PP, 0% RI, 0% B-exclusive
- 3 FL-exclusive MIDDLEs: {ii, im, n}

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C541 | Classes 7, 30 hazard-involved |
| C542 | Class 30 = hazard gateway |
| C546 | Class 40 safe flow |
| C562 | FL role structure (partially superseded) |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C581_cc_definitive_census.md](C581_cc_definitive_census.md) | [INDEX.md](INDEX.md) ->
