# EXT-9B: Ratio Hypothesis — FALSIFIED

**Phase ID:** EXT-9B
**Status:** FALSIFIED
**Date:** 2026-01-06

> **NOTE:** This hypothesis was initially considered plausible based on statistical patterns, but was RETRACTED after expert review identified structural violations. The observations remain valid; the semantic interpretation was wrong.

---

## The Question

Does the repetition pattern in Currier A encode RATIOS/PROPORTIONS rather than simple counts?

**Answer: NO.** The ratio interpretation violates prior frozen constraints.

---

## Evidence Summary

### Test 1: Same Composition, Different Counts
- **Finding:** 27 compositions appear with VARIABLE repetition counts
- **Example:** Composition {ch:1, sh:1} appears as 2x, 3x, and 4x
- **Interpretation:** The count is INDEPENDENT of block content
- **SUPPORTS ratio hypothesis**

### Test 2: Repetition vs Composition Size
- **Finding:** Spearman rho = 0.010, p = 0.81 (no correlation)
- **Interpretation:** Complexity doesn't predict repetition count
- **NEUTRAL** (neither supports nor refutes)

### Test 3: Distribution Pattern
- **Finding:** 2x = 120, 3x = 333, 4x = 139, 5x = 7, 6x = 2
- **3x is dominant** (55.4% of all repetitions)
- **Interpretation:** 3x is the "standard" or "default" quantity
- **SUPPORTS scaled preparation** interpretation

### Test 4: Within-Folio Patterns
- **Critical finding:** 56.7% of folios have UNIFORM repetition counts
- **All-3x folios:** 25 (dominant in H section)
- **All-4x folios:** 5
- **All-2x folios:** 2
- **Interpretation:** Repetition may be FOLIO-LEVEL property, not entry-level

### Test 5: Internal Token Repetition
- **Finding:** 154 blocks contain repeated tokens (e.g., daiin x 3-5 in single block)
- **Interpretation:** Internal ratios exist within blocks themselves
- **SUPPORTS compositional ratio encoding**

---

## The Dual-Level Model

The data reveals a **dual-level** encoding:

```
FOLIO LEVEL (56.7% uniform):
- Folio = preparation scale or batch type
- All entries on that folio share the same scale
- 3x = standard preparation (dominant in H section)
- 4x = concentrated preparation
- 2x = dilute preparation

ENTRY LEVEL (43.3% mixed folios):
- Within a folio, different components have different proportions
- E.g., "3 parts of X, 2 parts of Y, 4 parts of Z"
- This is classic recipe formulation
```

---

## Refined Interpretation

### What 3x Dominance Tells Us

| Count | Entries | % | Interpretation |
|-------|---------|---|----------------|
| 2x | 120 | 20% | Half-strength / dilute |
| 3x | 333 | 55% | STANDARD / baseline |
| 4x | 139 | 23% | Elevated / concentrated |
| 5x | 7 | 1% | High concentration |
| 6x | 2 | <1% | Maximum / pure |

The 3x dominance suggests this is the **reference preparation level**.

### What Folio Uniformity Tells Us

The fact that 56.7% of folios have ALL entries with the same repetition count suggests:

1. **Batch-Level Organization:** Each folio documents a specific batch scale
2. **Section Convention:** H section defaults to 3x (25/32 uniform folios)
3. **Preparation Classes:** 2x/3x/4x might be formal categories, not arbitrary numbers

### Combined Model

```
CURRIER A STRUCTURE:

[FOLIO] = Preparation class (e.g., "3x standard preparation")
  |
  +-- [ENTRY 1] = Component A at folio scale
  +-- [ENTRY 2] = Component B at folio scale
  +-- [ENTRY 3] = Component C at folio scale

MIXED FOLIOS:
  |
  +-- [ENTRY 1] = 3 parts of Component A
  +-- [ENTRY 2] = 2 parts of Component B
  +-- [ENTRY 3] = 4 parts of Component C
```

---

## Initial Verdict (RETRACTED)

~~**RATIO_ENCODING PARTIALLY SUPPORTED**~~

---

## Why This Was Wrong

### The Core Violation

Ratios require **more semantic structure** than counts. To encode ratios, a system needs:
- Abstract numeric scale
- Cross-entry arithmetic comparison
- Stable magnitude ordering
- Proportional semantics that persist across contexts
- Ability to compare "3x here" to "3x there"

**All of these were already falsified for Currier A.**

### The Specific Errors

1. **"3x = standard, 2x = dilute, 4x = concentrated"** — This is pure semantic labeling. The frequency distribution reflects human counting bias and registry ergonomics, not proportional tiers.

2. **"Folio uniformity = batch scale"** — Folio uniformity reflects enumeration depth preference (scribal convention, category density). Not a "scale" property.

3. **"Same composition with different counts = different ratios"** — This actually confirms the OPPOSITE: count is instance multiplicity, independent of identity. "3x here" is NOT comparable to "3x there" because vocabularies are section-isolated.

4. **No reference frame for ratios** — Ratios require comparison between entries. But entries don't aggregate, vocabularies are isolated, repetition doesn't propagate. No comparability = no ratios.

---

## Corrected Verdict

**RATIO_HYPOTHESIS FALSIFIED**

The observations are real; the interpretation was semantic overreach.

> **Repetition encodes LITERAL MULTIPLICITY of discrete identity instances, bounded for human usability, without abstraction, arithmetic, or proportional meaning.**

This actually strengthens the model by confirming:

> **Currier A intentionally refuses to encode quantity, even where humans expect it.**

---

## Corrected Constraints (287-290)

| # | Constraint |
|---|------------|
| 287 | Repetition does NOT encode abstract quantity, proportion, or scale; remains literal enumeration |
| 288 | 3x dominance reflects human counting bias and registry ergonomics, NOT proportional tiers |
| 289 | Folio uniformity = enumeration depth preference (scribal convention), NOT batch scale |
| 290 | Same composition with different counts = instance multiplicity, NOT magnitude; no cross-entry comparison |

---

## Lesson Learned

This is a textbook example of **late-stage semantic overreach**. The statistical patterns were real, but mapping meaning onto them violated structural constraints that were already frozen. The correct response is to:

1. Keep the observations
2. Reject the interpretation
3. Convert to negative constraints

The model is stronger for having caught and corrected this error.
