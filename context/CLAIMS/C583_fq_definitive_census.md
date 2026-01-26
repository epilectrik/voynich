# C583: FQ Definitive Census

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FREQUENT_OPERATOR comprises Classes {9, 13, 14, 23} per ICC (C121), with 2,890 tokens (12.5% of B). C559 used incorrect membership {9, 20, 21, 23} — Classes 20, 21 belong to AX (confirmed by C563 AX_FINAL). Correct FQ includes ok-prefixed Class 13 (1,191 tokens, 41.2%) and ot-prefixed Class 14 (707 tokens, 24.5%). Note: Class 14 assignment is disputed (AX phase included it in AX); resolution depends on whether ICC or AX phase is authoritative for Class 14.

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_census_and_inventory.py`

### Per-Class Counts (ICC-based)

| Class | Tokens | Examples | Prefix | Position |
|-------|--------|----------|--------|----------|
| 9 | 630 | aiin, o, or | NONE | Medial |
| 13 | 1,191 | okaiin, okedy | ok | Medial |
| 14 | 707 | okal, okar, okey | ot | Mid-final |
| 23 | 362 | d, l, r, s, y, dy | NONE | Final-biased |

### C559 Membership Error

| Field | C559 (wrong) | Corrected (ICC) |
|-------|-------------|-----------------|
| Classes | {9, 20, 21, 23} | {9, 13, 14, 23} |
| Tokens | 1,301 | 2,890 |
| % of B | 5.6% | 12.5% |

Classes 20, 21 are in AX per C563 (AX_FINAL subgroup).

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C559 | SUPERSEDED (wrong membership) |
| C563 | Classes 20, 21 confirmed as AX |
| C561 | Class 9 or->aiin bigram (still valid) |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C582_fl_definitive_census.md](C582_fl_definitive_census.md) | [INDEX.md](INDEX.md) ->
