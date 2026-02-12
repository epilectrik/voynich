# C977: EN/AX Transitionally Indistinguishable at Topology Level

**Tier:** 2 | **Scope:** B | **Phase:** MINIMAL_STATE_AUTOMATON

## Statement

ENERGY_OPERATOR (EN) and AUXILIARY (AX) classes are transitionally indistinguishable at macro level. The constraint-preserving merge collapses all 38 EN/AX classes into two groups (S3: 6 classes, S4: 32 classes) that share the same role composition {AX, EN}. The split between S3 and S4 is maintained by depletion asymmetry, not role boundaries.

## Evidence

- **Merge result:** All EN and AX classes merge freely with each other. No role-integrity constraint blocks EN-AX merging (unlike CC-FQ or FL-EN).
- **Flow asymmetry (T6):** AXm→AXM is 24.4x stronger than AXM→AXm. The minor group feeds into the major mass almost unidirectionally.
- **AXm self-loop:** 0.025 (barely recurrent). AXM self-loop: 0.698 (strongly recurrent). The minor group is a transient feeder, not an independent operational mode.
- **Holdout sensitivity:** The AXm/AXM boundary is the primary source of partition instability (T9: 46% exact recovery, 100% state-count recovery). Which specific classes land in AXm vs AXM depends on data subset.

## What This Does NOT Mean

EN and AX remain morphologically distinct (different suffix loads, prefix families) and REGIME-conditioned differently (C602, C616). The merge is topology-level only. The 5-role taxonomy accurately captures morphological and positional differences that are invisible to transition topology.

## The Minor Group (S3: AXm)

Classes {3, 5, 18, 19, 42, 45} — 3.0% of tokens. These 6 classes are transitionally distinct from the major mass due to depletion constraints: merging them into S4 would collapse depleted pairs (C5→34) into self-transitions, destroying asymmetry.

## Provenance

- Foreshadowed by: C572 (AX behavioral collapse), C574 (EN distributional convergence), C615 (AX-UN functional integration)
- Method: `phases/MINIMAL_STATE_AUTOMATON/scripts/t3_constraint_preserving_merge.py`
- Results: `phases/MINIMAL_STATE_AUTOMATON/results/t3_merged_automaton.json`
