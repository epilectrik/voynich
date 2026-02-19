# C1092: Rosettes SOUTH (C2) Convergence Profile

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Relates to:** C074 (dominant convergence to STATE-C, 57.8%), C079 (only STATE-C essential), C542 (gateway/terminal hazard asymmetry)
**Revised:** Phase 396 mapping correction — C2 is the SOUTH cardinal rosette, not CENTER. See correction note below.

---

## Statement

The SOUTH cardinal rosette (C2, 33 tokens) on f85v2 shows a TARGET-dominant hub profile: SOURCE:TARGET ratio = 0.36 (11 targets vs 4 sources), exclusive use of core vocabulary (0 exclusive MIDDLEs, all 18 MIDDLEs are high-frequency), heavy `aiin` suffix (5 instances, sustained-state marker), and proximity-scaled vocabulary overlap with surrounding label groups (BOTTOM 55%, MIDDLE 50%, UPPER 28%, D_W 5%). Hub roles are conserved across regions (same MIDDLE plays same hub role in labels and SOUTH ring text).

---

## Mapping Correction (Phase 396)

The original analysis (Phase 388H) identified C2 as "CENTER" based on the region code letter C. Corrected mapping from voynich.nu fRos_tr.txt reveals the grid system: Letter=ROW (V=top, N=middle, C=bottom), Number=COL (1=left, 2=center, 3=right).

| Original label | Region code | Correct position |
|---------------|-------------|-----------------|
| "CENTER" | C2 | **SOUTH cardinal** |
| "NORTH" (N1+N2) | N1, N2 | **WEST + CENTER** |
| "VERT" (V1+V2) | V1, V2 | **NW + NORTH** |

**Impact:** The convergence behavior (TARGET-dominant, core-only vocabulary) belongs to the SOUTH rosette, not CENTER. The "spatial convergence node" interpretation that CENTER is where processing streams terminate is weakened — SOUTH is a cardinal that connects to CENTER via conical funnel, SW, and SE. The actual CENTER rosette (N2, 37 tokens) was analyzed as part of the "NORTH" group and shows a more balanced profile.

The proximity-scaled overlap pattern (55% adjacent to 5% distant) used label groups BOTTOM/MIDDLE/UPPER/D_W, which are ROW-based groupings. BOTTOM (B1-B3) labels the bottom row (SW+SOUTH+SE) — so high overlap between C2 (SOUTH ring text) and BOTTOM labels (which include SOUTH labels B2) is expected, not evidence of centrality.

---

## Evidence (data valid, positional interpretation revised)

### Hub Role Comparison (SOURCE:TARGET Ratio)

| Region | Correct Position | Ratio | Character |
|--------|-----------------|-------|-----------|
| C2 | SOUTH | 0.36 | TARGET-dominant (receives 3x more) |
| N1+N2 | WEST + CENTER | 1.13 | Balanced |
| V1+V2 | NW + NORTH | 0.94 | Balanced |
| Typical B (f76r) | — | 2.0 | SOURCE-dominant |

### Proximity-Scaled Vocabulary Overlap

| Label Group | Correct Positions | Shared MIDDLEs / 18 | % |
|------------|-------------------|---------------------|---|
| BOTTOM (B1-B3) | SW + SOUTH + SE labels | 10 | 55% |
| MIDDLE (M1-M3) | WEST + CENTER + SE labels | 9 | 50% |
| UPPER (U1-U3) | NW + NORTH + NE labels | 5 | 28% |
| D_W (D1, W1) | SW doodle + NW margin | 1 | 5% |

Note: The "proximity" gradient actually reflects ROW proximity (bottom row labels share more with bottom-row ring text C2), not radial distance from CENTER.

### Hub Role Conservation

When a MIDDLE appears in both surrounding labels and C2 (SOUTH), it plays the same hub role:
- `ar` = HAZARD_SOURCE in both
- `al` = HAZARD_TARGET in both
- `od` = SAFETY_BUFFER in both
- `o` = HAZARD_TARGET in both

---

## Revised Interpretation

C2 (SOUTH) has a genuine TARGET-dominant profile and uses only core vocabulary. These structural facts remain valid. However, the interpretation that this represents a spatial convergence node (the center where processing streams terminate) is **weakened** because:

1. C2 is SOUTH, not CENTER — it's a cardinal rosette, not the spatial hub
2. The proximity gradient reflects row-based label grouping, not radial distance
3. The actual CENTER rosette (N2) has a different profile (balanced, not TARGET-dominant)

The TARGET-dominant profile of SOUTH may instead reflect: a terminal/output stage in a process sequence (consistent with SOUTH's visual similarity to NORTH — both have blue spoke patterns, suggesting a paired input/output relationship), or a collection point for the bottom row of the grid.

---

## Method

- Full token analysis of C2 region (33 tokens, U-track)
- Hub role sequence analysis with transition counting
- Vocabulary Jaccard with each surrounding label group
- Hub role conservation check across regions

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_center_rosette_deep.py`

---

## Verdict

**SOUTH_TARGET_PROFILE**: The SOUTH rosette (C2) is TARGET-dominant, core-vocabulary-only, with sustained-state markers. Originally interpreted as CENTER convergence node (Phase 388H); positional interpretation revised after mapping correction (Phase 396). The structural data remains valid but the "spatial convergence" interpretation is weakened.
