# C585: Cross-Role MIDDLE Sharing

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The 5 roles share MIDDLE vocabulary non-uniformly. EN-AX highest (Jaccard 0.402), CC minimal (Jaccard < 0.06 with all roles). EN has 29 exclusive MIDDLEs (45.3%), AX 17 (29.3%), FL 3 (17.6%). CC and FQ have 0 exclusive MIDDLEs — their entire MIDDLE vocabulary is shared with other roles.

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_census_and_inventory.py`

### 5x5 Jaccard Matrix

|    | CC | EN | FL | FQ | AX |
|----|----|----|----|----|-----|
| CC | 1.000 | 0.031 | 0.053 | 0.048 | 0.052 |
| EN | 0.031 | 1.000 | 0.125 | 0.297 | 0.402 |
| FL | 0.053 | 0.125 | 1.000 | 0.333 | 0.230 |
| FQ | 0.048 | 0.297 | 0.333 | 1.000 | 0.328 |
| AX | 0.052 | 0.402 | 0.230 | 0.328 | 1.000 |

### Exclusive MIDDLEs

| Role | Total | Exclusive | % |
|------|-------|-----------|---|
| CC | 3 | 0 | 0.0% |
| EN | 64 | 29 | 45.3% |
| FL | 17 | 3 | 17.6% |
| FQ | 19 | 0 | 0.0% |
| AX | 58 | 17 | 29.3% |

FL-exclusive: {ii, im, n}

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C567 | AX-operational sharing (71.9% shared) |
| C578 | EN 30 exclusive MIDDLEs (note: 29 by different computation) |
| C576 | EN MIDDLE bifurcation by PREFIX |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26

---

## Navigation

<- [C584_near_universal_pipeline_purity.md](C584_near_universal_pipeline_purity.md) | [INDEX.md](INDEX.md) ->
