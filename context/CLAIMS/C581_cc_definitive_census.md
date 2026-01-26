# C581: CC Definitive Census

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> CORE_CONTROL comprises Classes {10, 11, 12, 17} with 1,023 tokens (4.4% of B). ICC originally assigned CC = {10, 11, 12} (3 classes), but C560 establishes Class 17 as morphologically and functionally CC (ol-PREFIX + ENERGY elaboration). Class 12 (k) is a ghost class with zero corpus tokens (C540). Active CC: Class 10 (daiin, 314 tokens, initial-biased), Class 11 (ol, 421 tokens, medial), Class 17 (ol-derived, 288 tokens, neutral).

---

## Evidence

**Test:** `phases/SMALL_ROLE_ANATOMY/scripts/sr_census_and_inventory.py`

### Census Reconciliation

| Source | CC Classes | Count |
|--------|-----------|-------|
| ICC README | {10, 11, 12} | 3 |
| C560 analysis | {10, 11, 12, 17} | 4 |
| AX phase scripts | {10, 11, 12, 17} | 4 |
| CLASS_SEMANTIC_VAL | {10, 11, 17} | 3 |

Resolution: C560 (validated Tier 2) provides morphological evidence that Class 17 is CC.

### Per-Class Counts

| Class | Tokens | Examples | Position |
|-------|--------|----------|----------|
| 10 | 314 | daiin | Initial-biased (27.1%) |
| 11 | 421 | ol | Medial (5.0% initial) |
| 12 | 0 | k | Ghost (C540) |
| 17 | 288 | olaiin, olchedy... | Neutral (6.6% initial) |

---

## Related Constraints

| Constraint | Relationship |
|-----------|-------------|
| C540 | Class 12 never standalone |
| C558 | Singleton class structure |
| C560 | Class 17 ol-derivation |
| C121 | 49 instruction classes |

---

## Provenance

- **Phase:** SMALL_ROLE_ANATOMY
- **Date:** 2026-01-26
- **Script:** sr_census_and_inventory.py

---

## Navigation

<- [C580_en_trigger_profiles.md](C580_en_trigger_profiles.md) | [INDEX.md](INDEX.md) ->
