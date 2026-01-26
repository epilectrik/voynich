# C601: Hazard Sub-Group Concentration

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> All 19 corpus hazard events originate from exactly 3 source sub-groups: FL_HAZ (9 events, 47%), EN_CHSH (5, 26%), FQ_CONN (5, 26%). EN_CHSH absorbs 58% of hazard targets (11/19). EN_QO never participates as source or target. Safe sub-groups (FL_SAFE, FQ_PAIR, FQ_CLOSER, all AX, all CC) never participate in hazards. Hazard topology is confined to a specific sub-group circuit.

---

## Evidence

**Test:** `phases/SUB_ROLE_INTERACTION/scripts/sub_role_conditioning.py`

### Hazard Source/Target by Sub-Group

| Sub-Group | Source | Target | Total |
|-----------|--------|--------|-------|
| FL_HAZ | 9 | 2 | 11 |
| EN_CHSH | 5 | **11** | 16 |
| FQ_CONN | 5 | 5 | 10 |
| FQ_CLOSER | 0 | 1 | 1 |

### Hazard Pair Counts

| Source -> Target | Count |
|-----------------|-------|
| EN_CHSH -> EN_CHSH | 5 |
| FL_HAZ -> FQ_CONN | 5 |
| FQ_CONN -> EN_CHSH | 4 |
| FL_HAZ -> FL_HAZ | 2 |
| FL_HAZ -> EN_CHSH | 2 |
| FQ_CONN -> FQ_CLOSER | 1 |

### Non-Participating Sub-Groups

The following sub-groups have **zero hazard involvement** (source or target):
- EN_QO (0/19) — despite QO being 42% of EN tokens
- EN_MINOR (0/19)
- FQ_PAIR (0/19) — despite being 61% of FQ tokens
- FL_SAFE (0/19)
- All AX sub-groups (0/19)
- All CC sub-groups (0/19)
- UN (0/19)

---

## Interpretation

The hazard circuit is a closed loop among 3 sub-groups: FL_HAZ initiates (47% source), FQ_CONN relays, EN_CHSH absorbs (58% target). This circuit corresponds exactly to the hazardous sub-groups identified by prior anatomy phases:
- FL_HAZ = hazardous FL classes {7, 30} (C586)
- FQ_CONN = hazardous FQ Class 9 (C593, BARE=HAZARDOUS)
- EN_CHSH = ch/sh-prefixed EN classes (10 classes)

QO's complete absence from hazards (0/19) combined with its distinct upstream routing (triggered by CC_OL_D, not daiin/ol) suggests QO and CHSH are not just lexically different (C576) but functionally different — CHSH handles hazardous operations while QO handles safe ones.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C109 | Refined - 5 failure classes now mapped to 3 sub-groups |
| C541 | Extended - hazard class enumeration now at sub-group level |
| C586 | Connected - FL hazard/safe split maps directly to hazard participation |
| C593 | Connected - FQ BARE=HAZARDOUS confirmed by hazard sub-group data |
| C598 | Extended - hazard circuit follows the same routing as non-hazard transitions |
| C596 | Refined - FQ-FL hazard alignment p=0.33 was at role level; at sub-group level, FL_HAZ->FQ_CONN is 100% of FL->FQ hazards |

---

## Provenance

- **Phase:** SUB_ROLE_INTERACTION
- **Date:** 2026-01-26
- **Script:** sub_role_conditioning.py

---

## Navigation

<- [C600_cc_trigger_subgroup_selectivity.md](C600_cc_trigger_subgroup_selectivity.md) | [INDEX.md](INDEX.md) ->
