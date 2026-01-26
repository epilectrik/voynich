# C592: C559 Membership Correction

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> C559 (FREQUENT Role Structure) used incorrect membership {9, 20, 21, 23}. Correct ICC-based membership is {9, 13, 14, 23} (C583). Classes 20, 21 belong to AX (confirmed by C563 AX_FINAL subgroup). C559's statistical findings about positional patterns, self-chaining rates, REGIME distributions, and section distributions were computed on a mixed AX/FQ set and should be treated as unreliable for FQ-specific claims.

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_census_and_inventory.py`

### Membership Comparison

| Field | C559 (wrong) | Corrected (C583) |
|-------|-------------|------------------|
| Classes | {9, 20, 21, 23} | {9, 13, 14, 23} |
| Token types | 35 | 33 |
| Token count | 1,301 | 2,890 |
| % of B | 5.6% | 12.5% |

### Downstream Impact

Constraints that referenced FQ behavior and may need re-verification:

| Constraint | FQ-specific claim |
|-----------|-------------------|
| C550 | FQ self-chaining 2.38x |
| C551 | FQ flat REGIME (entropy 1.38) |
| C552 | FQ section distribution |
| C556 | FQ 1.67x final |

Note: C550/C551/C552/C556 computed FQ statistics using role-level aggregation. The FQ role label assignment in those scripts must be checked to determine if they used the correct or incorrect membership.

### C559 Status

**SUPERSEDED** by C583 (FQ Definitive Census) and C587 (FQ Internal Differentiation).
C561 (or->aiin bigram) remains valid as it concerns Class 9 specifically.

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C559 | SUPERSEDED |
| C563 | Classes 20, 21 are AX |
| C583 | Correct FQ census |
| C587 | Correct FQ differentiation |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C591_five_role_complete_taxonomy.md](C591_five_role_complete_taxonomy.md) | [INDEX.md](INDEX.md) ->
