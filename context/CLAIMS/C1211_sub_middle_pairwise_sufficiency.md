# C1211: Sub-MIDDLE Pairwise Sufficiency -- No Three-Way Synergy

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MIDDLE_SLOT_INTERACTION (Phase 429)
**Extends:** C1003 (no three-way morphological synergy at PREFIX x MIDDLE x SUFFIX)
**Relates to:** C1209 (MIDDLE positional grammar), C1210 (MIDDLE slot syntax)

---

## Statement

Within 3+ character MIDDLEs (8,466 tokens), the INITIAL, MEDIAL, and TERMINAL positional slots show REDUNDANCY, not synergy. Knowing both INITIAL and MEDIAL predicts TERMINAL 57.5% of its entropy, but the sum of individual predictions (35.9% + 49.1% = 85.0%) exceeds this. The excess (-0.83 bits) is shared information, not synergistic interaction.

### Entropy Analysis

| Measure | Bits |
|---------|------|
| H(Terminal) | 3.011 |
| H(Terminal \| Initial) | 1.930 |
| H(Terminal \| Medial) | 1.534 |
| H(Terminal \| Initial, Medial) | 1.279 |

### Mutual Information

| Measure | Bits | % of H(Terminal) |
|---------|------|-----------------|
| I(Terminal; Initial) | 1.081 | 35.9% |
| I(Terminal; Medial) | 1.478 | 49.1% |
| I(Terminal; Initial+Medial) | 1.732 | 57.5% |
| Additive prediction | 2.559 | 85.0% |
| **Synergy (excess)** | **-0.827** | — |

### Interpretation

This extends C1003 to the sub-MIDDLE level. Just as PREFIX, MIDDLE, and SUFFIX show no three-way synergy (C1003), INITIAL, MEDIAL, and TERMINAL within a MIDDLE also show no three-way synergy. Pairwise interactions are sufficient at both levels of the morphological hierarchy.

The redundancy means INITIAL and MEDIAL carry overlapping information about TERMINAL. This is consistent with C1210's finding that slot syntax respects C1207 cluster boundaries -- if INITIAL = a (iteration axis) and MEDIAL = i (also iteration axis), both independently predict TERMINAL = n (iteration axis). The overlap is the cluster membership signal.

### Pairwise Interaction Strengths

| Pair | Cramer's V | MI (bits) |
|------|-----------|-----------|
| INITIAL x MEDIAL | 0.394 | 1.311 |
| MEDIAL x TERMINAL | 0.387 | 1.478 |
| INITIAL x TERMINAL | 0.371 | 1.180 |

All three pairwise interactions are strong and comparable in magnitude. The MEDIAL slot carries the most information about TERMINAL (MI=1.478), consistent with the MEDIAL atom being the operational core of the instruction.

---

## Method

- 8,466 Currier B tokens with MIDDLE length >= 3
- INITIAL = first character, MEDIAL = second character, TERMINAL = last character
- Conditional entropy H(T|X) computed for each conditioning variable
- Mutual information I(T; X) = H(T) - H(T|X)
- Synergy = I(T; I,M) - I(T; I) - I(T; M)

**Script:** `phases/MIDDLE_SLOT_INTERACTION/scripts/slot_interaction_test.py` (T3)
**Results:** `phases/MIDDLE_SLOT_INTERACTION/results/slot_interaction_results.json`
