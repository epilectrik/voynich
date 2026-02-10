# C961: WORK Zone Is Unordered

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

Within the WORK zone (medial positions), tokens of the same role show no systematic ordering. Neither ENERGY nor AUXILIARY tokens follow a class-number, prefix, or kernel-content sequence.

## Evidence

- 1,201 lines with 3+ EN tokens in WORK zone
- EN Kendall tau vs class number: mean = -0.0001 (p = 0.498 vs shuffle)
- EN tau vs prefix index: -0.088 (slight but not significant)
- EN tau vs kernel content: -0.045 (not significant)
- 328 lines with 3+ AX tokens: tau = -0.033 (p = 0.828)
- Kernel-bearing EN mean position 0.473 vs kernel-free 0.494 (negligible difference)
- 3 directional class pairs found (>3:1 bias) out of 78 tested, but global signal absent

## Interpretation

Within a control block's operational interior, the specific ordering of same-role tokens is free. The system specifies WHICH operations to include (role selection) but not their internal sequence. This is consistent with parallel rather than sequential processing within a line's WORK zone.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/06_within_zone_ordering.py`
- Related: C556, C563-C565, C574
