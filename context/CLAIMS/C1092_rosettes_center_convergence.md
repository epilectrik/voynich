# C1092: Rosettes CENTER Convergence Node

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Relates to:** C074 (dominant convergence to STATE-C, 57.8%), C079 (only STATE-C essential), C542 (gateway/terminal hazard asymmetry)

---

## Statement

The CENTER rosette (C2, 33 tokens) on f85v2 shows a TARGET-dominant hub profile: SOURCE:TARGET ratio = 0.36 (11 targets vs 4 sources), exclusive use of core vocabulary (0 exclusive MIDDLEs, all 18 MIDDLEs are high-frequency), heavy `aiin` suffix (5 instances, sustained-state marker), and proximity-scaled vocabulary overlap with surrounding regions (BOTTOM 55%, MIDDLE 50%, UPPER 28%, D_W 5%). Hub roles are conserved across regions (same MIDDLE plays same hub role in labels and CENTER).

---

## Evidence

### Hub Role Comparison (SOURCE:TARGET Ratio)

| Region | Ratio | Character |
|--------|-------|-----------|
| CENTER (C2) | 0.36 | TARGET-dominant (receives 3x more) |
| NORTH (N1+N2) | 1.13 | Balanced |
| VERT (V1+V2) | 0.94 | Balanced |
| Typical B (f76r) | 2.0 | SOURCE-dominant |

### Proximity-Scaled Vocabulary Overlap

| Surrounding Group | Shared MIDDLEs / 18 | % |
|-------------------|---------------------|---|
| BOTTOM (adjacent) | 10 | 55% |
| MIDDLE (adjacent) | 9 | 50% |
| UPPER (distant) | 5 | 28% |
| D_W (furthest) | 1 | 5% |

### Hub Role Conservation

When a MIDDLE appears in both surrounding labels and CENTER, it plays the same hub role:
- `ar` = HAZARD_SOURCE in both
- `al` = HAZARD_TARGET in both
- `od` = SAFETY_BUFFER in both
- `o` = HAZARD_TARGET in both

---

## Interpretation

The CENTER rosette functions as a structural convergence node — the point where multiple processing streams terminate. Its TARGET-dominant profile, core-only vocabulary, sustained-state markers, and proximity-scaled connectivity are consistent with C074 (57.8% convergence to STATE-C) instantiated spatially. The proximity gradient suggests the physical layout of f85v2 encodes operational proximity, with regions closer to CENTER sharing more vocabulary.

---

## Method

- Full token analysis of C2 region (33 tokens, U-track)
- Hub role sequence analysis with transition counting
- Vocabulary Jaccard with each surrounding label group
- Hub role conservation check across regions

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_center_rosette_deep.py`

---

## Verdict

**CENTER_CONVERGENCE**: The CENTER rosette is a structural convergence node — TARGET-dominant, core-vocabulary-only, sustained-state, with proximity-scaled connectivity to surrounding regions.
