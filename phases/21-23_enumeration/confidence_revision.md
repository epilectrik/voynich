# Adversarial Audit - Confidence Revision

*Generated: 2025-12-31T22:32*

---

## Executive Summary

Based on adversarial testing:

- **Model existence: HIGH confidence** - the structure is real, not artifactual or generic
- **Model parameters: MEDIUM confidence** - two specific claims need clarification

The core claim that the Voynich has meaningful, non-random, kernel-centric structure **survives with HIGH confidence**. Only two specific parametric claims (cycle count, constraint enforcement) require revision.

---

## Pre-Audit Confidence

| Claim | Phase | Original Confidence |
|-------|-------|---------------------|
| Kernel centrality (k, h, e) | 15, 17 | HIGH |
| Universal 2-cycle structure | 22B | HIGH (CV=0.00) |
| 49 instruction classes | 20 | HIGH |
| 17 forbidden transitions | 18 | HIGH |
| 8 recipe families | 20 | MEDIUM |
| Monostate convergence | 14 | HIGH |
| Folio distinctiveness | 22B | HIGH |
| OVERALL: REVERSE_ENGINEERING COMPLETE | 20 | HIGH |

---

## Post-Audit Confidence Revisions

| Claim | Original | Revised | Delta | Reason |
|-------|----------|---------|-------|--------|
| Kernel centrality | HIGH | HIGH | 0 | Survived attack 1 |
| Universal 2-cycle | HIGH | **LOW** | -2 | Attack 2: cycle varies with segmentation |
| 49 instruction classes | HIGH | MEDIUM-HIGH | -0.5 | Not directly tested, but grammar simplifiable |
| 17 forbidden transitions | HIGH | **LOW** | -2 | Attack 3: 100% legality with or without |
| 8 recipe families | MEDIUM | MEDIUM | 0 | Preconditions met but not directly tested |
| Monostate convergence | HIGH | HIGH | 0 | Survived attack 4 |
| Folio distinctiveness | HIGH | MEDIUM-HIGH | -0.5 | Borderline MI, but CV confirms |
| **OVERALL** | **HIGH** | **MEDIUM** | **-1** | Two core claims weakened |

---

## Specific Revisions Required

### Revision 1: "Universal 2-Cycle" Claim

**Original Statement (Phase 22B):**
> "Universal 2-cycle structure (CV=0.00 across 83 folios)"

**Revised Statement:**
> "Dominant cycle structure at 5-6 characters, varying by segmentation scheme. The '2-cycle' may refer to instruction-class-level alternation, not character-level periodicity. CV=0.00 claim requires methodological clarification."

**Action Required:**
- Define "2-cycle" explicitly (is it A→B state alternation? Character period? Something else?)
- Re-run cycle analysis with clear methodology
- Report actual CV with confidence intervals

### Revision 2: "17 Forbidden Transitions" Claim

**Original Statement (Phase 18):**
> "17 forbidden transitions = failure modes (flooding, weeping, channeling)"

**Revised Statement:**
> "17 forbidden character-level transitions are not observed in the corpus. It is unclear whether these represent genuine constraints (never violated by design) or artifacts (never occurring by chance). Physical interpretation requires verification that these transitions WOULD violate legality if inserted."

**Action Required:**
- Test whether forbidden transitions are actually forbidden (insert them into valid sequences, check if execution fails)
- Distinguish between "never occurs" (descriptive) and "would break system" (prescriptive)
- If possible, identify near-violations to demonstrate constraint is meaningful

---

## Confidence Scaling

Two distinct confidence dimensions:

### Model Existence (Is the structure real?)
- **Pre-Audit:** HIGH
- **Post-Audit:** **HIGH** (unchanged)
- Kernel structure: 0/100 surrogates reproduced (not frequency artifact)
- Monostate behavior: 0% in random systems (not generic)
- Folio distinctiveness: CV=35.7% (not redundant samples)

### Model Parameters (Are specific claims accurate?)
- **Pre-Audit:** HIGH
- **Post-Audit:** **MEDIUM**
- 2-cycle claim: varies with segmentation (needs clarification)
- Forbidden transitions: never violated (enforcement unclear)

---

## What Remains Valid

Despite confidence reduction, the following are UNWEAKENED:

1. **Kernel structure is real.** The k, h, e triad is not a frequency artifact.

2. **Behavior is specific.** Monostate convergence and cyclic structure are not generic to constraint systems.

3. **Folios are distinct.** Statistical signatures differ meaningfully across folios.

4. **Grammar exists.** The 49-class compression is not falsified (though constraint enforcement is questionable).

5. **Recipe families are plausible.** Preconditions for meaningful clustering are met.

---

## What Is Now Uncertain

1. **Cycle invariance.** The specific claim of CV=0.00 for 2-cycles is not supported by this analysis.

2. **Constraint enforcement.** Whether forbidden transitions are actually *forbidden* vs merely *unobserved* is unclear.

3. **Hazard model validity.** If constraints don't enforce anything, the 5-class failure typology may be post-hoc rationalization.

---

## Recommendation

**Do NOT abandon the model.** The core structure survives. However:

1. **Revise Phase 22B** to clarify cycle definition
2. **Revise Phase 18** to demonstrate constraint enforcement
3. **Lower overall confidence to MEDIUM** pending revisions
4. **The "REVERSE_ENGINEERING COMPLETE" verdict remains plausible** but should be qualified with "pending cycle and constraint clarification"

---

## Frozen Conclusion Status

The frozen conclusion from Phase 22B:

> "The Voynich Manuscript encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, using universal 2-cycle regulation and hazard-aware ordering."

**Should be revised to:**

> "The Voynich Manuscript encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime. **Cycle regulation and hazard-aware ordering claims require methodological clarification.**"

**Status:**
- **Model existence: FROZEN (HIGH confidence)** - the structure is real
- **Model parameters: PARTIALLY FROZEN (MEDIUM confidence)** - 2 claims need clarification

The core claim that the Voynich has meaningful, non-random, kernel-centric structure is **validated with HIGH confidence**. The specific claims about 2-cycle universality and forbidden transition enforcement require methodological clarification but do not threaten the existence of the model itself.
