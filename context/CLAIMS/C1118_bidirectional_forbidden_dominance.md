# C1118: Bidirectional Forbidden Co-occurrence Dominance

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** READING_DIRECTION_TEST (Phase 399)
**Extends:** C109 (17 forbidden transitions), C783 (forbidden pair asymmetry), C1034 (symmetric forbidden fix)
**Relates to:** C475 (95.7% MIDDLE incompatibility), C391 (symmetric entropy)

---

## Statement

75.2% of MIDDLE-level forbidden co-occurrences (1244/1655 pairs across 58 active MIDDLEs) are bidirectional adjacency prohibitions — forbidden in BOTH LTR and RTL reading. Only 24.8% (411/1655) are direction-specific. This resolves the C1034 puzzle: symmetric forbidden suppression improves the generative model because most forbidden pairs are co-occurrence incompatibilities (adjacency constraints), not sequential prohibitions. The 17 class-level forbidden transitions (C109, C783) are directional; the broader MIDDLE co-occurrence landscape is predominantly symmetric.

---

## Evidence

### MIDDLE-Level Forbidden Pair Analysis (threshold: degree > 10)

| Metric | Value |
|--------|-------|
| Active MIDDLEs (both directions) | 58 |
| Total forbidden pairs (LTR) | 1655 |
| Total forbidden pairs (RTL) | 1655 |
| Symmetric (bidirectional) | 1244 (75.2%) |
| Direction-specific | 411 (24.8%) |
| Jaccard similarity LTR vs RTL | 0.602 |

### Mathematical Note

Forbidden pair landscapes under LTR and RTL are exact mirror images by construction: if (A→B) is forbidden under LTR, then (B→A) is forbidden under RTL. The forbidden pair count is identical. The symmetric fraction (75.2%) represents pairs where BOTH (A→B) and (B→A) have zero count — these MIDDLEs are never adjacent regardless of order.

### Connection to C1034

C1034 found that making forbidden pairs bidirectional (suppressing both A→B and B→A) fixes the B5 asymmetry test. This makes structural sense: the model's primary job is enforcing co-occurrence incompatibility (75.2% of the forbidden landscape), not directional sequencing (24.8%). The symmetric model captures the dominant constraint mode.

### Connection to C475

The symmetric forbidden pairs are the transition-grammar expression of C475's static MIDDLE incompatibility lattice. When two MIDDLEs are incompatible in C475 (95.7% incompatibility rate), they tend to be forbidden in both directions as adjacent tokens.

---

## Provenance

- Phase: 399 (READING_DIRECTION_TEST)
- Script: `phases/READING_DIRECTION_TEST/scripts/reading_direction_test.py` (T1)
- Results: `phases/READING_DIRECTION_TEST/results/reading_direction_results.json`
- Related: C109, C783, C1034, C475, C391
