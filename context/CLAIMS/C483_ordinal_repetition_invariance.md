# C483: Ordinal Repetition Invariance

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** Phase BvS (2026-01-13)

---

## Statement

In Currier A, intra-line repetition marks ordinal emphasis (emphasized vs unmarked) only. Repetition magnitude (2x vs 3x vs 4x) produces no detectable differences in downstream morphology, positional behavior, prefix entropy, or AZC compatibility. Therefore, repetition does not encode scalar quantity, ratio, or proportional weighting.

---

## Structural Interpretation

Repetition is a **binary salience flag**, not a graded quantity.

- **MARKED**: Token is emphasized/primary/load-bearing
- **UNMARKED**: Token is present but secondary

The system distinguishes "emphasized" from "not emphasized" but NOT "how much emphasis."

---

## Evidence

```
Phase BvS Downstream Correlation Tests:

Test 1: Repetition magnitude vs Morphological Diversity
  - Spearman rho = 0.015, p = 0.80
  - Result: NO CORRELATION

Test 2: Repetition magnitude vs Line Position
  - Spearman rho = -0.083, p = 0.16
  - Result: NO CORRELATION

Test 3: Repeated vs Non-Repeated Prefix Entropy
  - Repeated: 1.931 ± 0.483
  - Non-repeated: 1.855 ± 0.512
  - Mann-Whitney p = 0.053
  - Result: NO DIFFERENCE

Test 4: 2x vs 3x Downstream Structure
  - No morphological profile difference beyond tautological TTR
  - Magnitude is structurally invisible
```

---

## Why This Closes the Ratio Question

Ratio encoding would require:
- Cross-line normalization (absent)
- Magnitude affecting downstream structure (absent)
- Proportional scaling (absent)
- 2x vs 3x producing different effects (absent)

All four are empirically falsified. Repetition is ordinal only.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C252 | **Clarifies**: Bounded repetition (2-6x) is ordinal, not scalar |
| C287-C290 | **Strengthens**: Ratio encoding rejection now empirically confirmed |
| C254 | **Compatible**: Multiplicity isolation preserved |
| C482 | **Compatible**: Batch processing with default equal inclusion |

---

## Does NOT Modify

- C252 (descriptive structural fact unchanged)
- C287-C290 (falsification status unchanged)
- Any existing constraint wording

This constraint adds **empirical closure** to previously interpretive claims.

---

## Semantic Hygiene Lock

This constraint exists to prevent future misreadings:

> Even when repetition occurs, its magnitude is structurally invisible downstream.

The "1:1:1:1 default" interpretation is confirmed. The manuscript delegates "how much" to human practice, not to text.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
