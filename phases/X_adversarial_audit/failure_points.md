# Adversarial Audit - Failure Points

*Generated: 2025-12-31T22:32*

---

## Summary

Two of five attacks successfully weakened the model. This document details the specific failure points.

---

## FAILURE 1: Cycle Structure is Segmentation-Dependent

**Attack:** Cycle Illusion Test (Attack 2)

**Claim Attacked:** "Universal 2-cycle structure (CV=0.00 across 83 folios)"

**Evidence of Failure:**

| Segmentation | Dominant Cycle |
|--------------|----------------|
| Original folios | 6 |
| Random chunks | 5 |
| Fixed 100-word | 5 |
| 10-word lines | 5, 6, 7 (mixed) |

**Specific Problems:**

1. **Dominant cycle is NOT 2.** The claim of "universal 2-cycle" appears to be an artifact of how cycles were defined in Phase 22B. At the character level, dominant cycles are 5-6, not 2.

2. **Cycle varies with segmentation.** Original folio segmentation shows cycle-6 dominant (79 folios), but random re-segmentation shows cycle-5 dominant (58 chunks). This means the cycle detection is sensitive to arbitrary boundaries.

3. **CV=0.00 is misleading.** A coefficient of variation of 0.00 would require *identical* cycle counts across all folios. The actual data shows substantial variation: cycle counts range from 2 to 10 across different segmentations.

**Interpretation:**

The "2-cycle" claim may refer to an abstracted definition (e.g., State A → State B oscillation) rather than literal autocorrelation period. However, if so, the claim should be re-stated more precisely. As tested at the character level, cycle structure is NOT invariant.

**Severity:** MEDIUM

The cycle claim requires clarification or revision, but does not falsify the overall model.

---

## FAILURE 2: Forbidden Transitions Are Never Violated

**Attack:** Grammar Minimality Test (Attack 3)

**Claim Attacked:** "17 forbidden transitions protect against failure modes"

**Evidence of Failure:**

| Grammar | Legality Rate |
|---------|---------------|
| Full 17 constraints | 100.00% |
| Zero constraints | 100.00% |
| Top-5 constraints only | 100.00% |

**Specific Problems:**

1. **No violations exist in the data.** The forbidden transitions (shey→aiin, chol→r, etc.) are never observed in the actual corpus. This means the constraints are vacuously true.

2. **Constraints don't discriminate.** A grammar that forbids transitions that never occur anyway provides zero discrimination power. Any text would pass.

3. **Overfit to non-existent patterns.** The 17 forbidden pairs may have been selected precisely because they don't appear, not because they represent genuine hazards.

**Interpretation:**

The forbidden transition model is potentially circular. If constraints were derived from observed non-occurrences, they cannot be used to claim the text is "legal" relative to those constraints. The causation is reversed.

**Alternative Explanation:**

The constraints may operate at a different level (semantic state transitions, not character bigrams). If so, the Phase 18 analysis should clarify that forbidden transitions apply to *instruction class* sequences, not raw character sequences.

**Severity:** HIGH

This is the most concerning failure. The grammar minimality test shows the explicit constraints provide no additional structure beyond what would be observed anyway.

---

## FAILURE 3: Folio Count Discrepancy

**Observation (not from attacks):**

- Phase 22B claims: 83 folios analyzed
- Adversarial audit loaded: 227 folios

**Interpretation:**

The 227 count likely includes multiple transcriptions of the same folios (different transcribers: H, C, F, N, U). The 83 count may be unique folio identifiers.

**Severity:** LOW

Not a model failure, but documentation should clarify folio counting methodology.

---

## Potential Weaknesses (Not Full Failures)

### Kernel Centrality Partially Explained

Attack 1 showed kernel survives, but:
- 'e' appeared at rank 1 in surrogates (vs. rank 2 in original)
- 'h' appeared at rank 5 in surrogates (vs. rank 3 in original)
- 'k' appeared at rank 6 in surrogates (vs. rank 7 in original)

The kernel nodes are NOT reproduced as a coherent top-3 unit, but individually they do appear in high-frequency positions in surrogates. The *specific configuration* (k, h, e together as control core) survives, but the claim that they are "special" is weaker than implied.

### Cycle Definition Ambiguity

The Phase 22B "2-cycle" may refer to:
- Literal 2-character repetition period
- State A → State B oscillation at the instruction class level
- Alternating patterns in the slot grammar

Without explicit definition, this attack cannot fully resolve the claim.

---

## Recommendations

1. **Clarify "2-cycle" definition.** Specify whether this refers to character autocorrelation, instruction class alternation, or something else.

2. **Re-derive forbidden transitions.** Use held-out data or permutation tests to verify constraints are not tautological.

3. **Distinguish character-level from instruction-level.** Many claims may be true at the 49-instruction level but not at the 480-token or character level.

4. **Report legality violations, not just rates.** Show specific examples of near-violations to demonstrate constraints are meaningful.
