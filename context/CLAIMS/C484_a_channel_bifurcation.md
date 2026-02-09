# C484: Currier A Channel Bifurcation

**Tier:** 2 | **Status:** CLOSED | **Scope:** A, AZC (negative), HT (negative) | **Source:** Phase S1 (2026-01-13)

---

## Statement

Currier A supports **two structurally distinct content types**:

1. **Registry entries** (multi-token lines), which define compound constraint bundles that participate in the A->AZC->B pipeline.

2. **Registry control operators** (single-token lines, ~0.6% of entries), which:
   - occur only in pure-A folios (no AZC tokens present),
   - are enriched at folio boundaries (start/end; p < 0.01),
   - use a disjoint vocabulary and morphology from registry entries,
   - coincide with abrupt prefix-regime transitions,
   - do not trigger Human Track activity.

Registry control operators do **not** specify discriminative content and do **not** participate in compatibility grouping or positional encoding. Their role is meta-structural, acting on the organization or scope of the Currier A registry itself rather than on operational specification.

---

## Evidence

### Phase S2: AZC Projection Impact

```
Single-token lines in AZC folios: 0/10
AZC tokens in their folios: 0 for all 10
Baseline A token AZC presence: 19%
```

### Phase S1: Positional Anchoring

```
S1.1 Boundary Proximity:
  - Single-token mean normalized distance: 0.138
  - Random A lines mean: 0.259
  - Mann-Whitney p = 0.0099 (BOUNDARY ENRICHED)
  - At folio start (line 0-1): 30%
  - At folio end: 30%

S1.3 Prefix Regime Shifts:
  - All 4 testable cases show major prefix shifts (>3%)
  - Mean entropy change: 0.277

S1.4 HT Non-Involvement:
  - Single-char rate near single-token lines: 3.2%
  - 7/10 show 0% single-char tokens nearby
```

### Vocabulary Isolation

```
Single-token line vocabulary:
  - 10 unique tokens
  - 90% appear ONLY in single-token contexts
  - Missing core A prefixes (ch-, qo-)
  - Over-represented: yd-, so-, ke-, sa-
```

---

## The 10 Registry Control Operators

| Folio | Line | Token | Position |
|-------|------|-------|----------|
| f1r | 6 | ydaraishy | mid-folio |
| f1r | 28 | dchaiin | folio end |
| f8r | 13 | okokchodm | mid-folio |
| f8v | 11 | sorain | mid-folio |
| f24r | 20 | samchorly | folio end |
| f27r | 13 | okchodeey | folio end |
| f37v | 13 | sotoiiin | mid-folio |
| f88v | 0 | daramdal | folio start |
| f89r1 | 0 | ykyd | folio start |
| f102v1 | 0 | ker | folio start |

---

## Structural Interpretation

Registry control operators are **meta-level markers** that:

- Delineate registry scope or mode
- Signal transitions between organizational units
- Operate ABOVE the normal A->AZC->B pipeline

They answer: "What kind of registry space are we in?"
Not: "What distinctions exist here?"

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C233 | **Clarifies**: LINE_ATOMIC applies to both types |
| C240 | **Refines**: Registry includes control layer |
| C473 | **Restricts**: Constraint bundle applies to type 1 only |
| C384 | **Compatible**: No entry-level coupling for either type |
| C424 | **Supports**: Boundary clustering behavior |

---

## What This Does NOT Establish

- What the operator tokens "mean"
- Semantic categories or labels
- Header/section interpretations
- Any modification to Currier B grammar

This constraint documents **role-level behavior only**.

---

## Architectural Significance

With C484, Currier A is understood as:

> A **maintained registry with explicit control points**, not merely a list of entries.

This explains:
- Why single-token lines are rare but deliberate
- Why they avoid AZC entirely
- Why they cluster at boundaries
- Why they don't engage HT
- Why their vocabulary never appears elsewhere

They are **operators on the registry**, not entries in it.

---

## Navigation

<- [INDEX.md](INDEX.md) | [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
