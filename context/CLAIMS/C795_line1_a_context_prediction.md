# C795: Line-1 A-Context Prediction

**Tier:** 2
**Scope:** A<>B
**Phase:** B_LINE_POSITION_HT (extension)

## Constraint

The PP portion of line-1 HT vocabulary predicts which A folio provides best coverage for that B folio at 15.8x random baseline.

## Evidence

### Prediction Test

Using only PP MIDDLEs from line-1 HT to predict best-match A folio:

| Metric | Value |
|--------|-------|
| Correct predictions | 10/72 (13.9%) |
| Random baseline | 1/114 (0.88%) |
| **Lift** | **15.8x** |

### Mechanism

The predictive MIDDLEs include both common and rare vocabulary:

| MIDDLE | Line-1 Occurrences | A-Folio Coverage |
|--------|-------------------|------------------|
| ed | 15 | 4% (rare) |
| pch | 7 | 9% (rare) |
| edy | 7 | 5% (rare) |
| fch | 6 | 4% (rare) |
| y | 7 | 93% (common) |
| dy | 13 | 74% (common) |

The rare MIDDLEs are discriminative - their presence in line-1 identifies a specific A folio context.

## Interpretation

Line-1 HT is not random vocabulary padding. Its PP component carries **structured information about which A folio context applies** to this B program.

This connects A→B constraint propagation (C753) to the program level: each B program declares its A-context in line-1, then executes within those constraints on lines 2+.

## Relation to Coverage Architecture

- C734: A folio identity explains 72% of B coverage variance
- C795: Line-1 HT encodes this A folio identity at 15.8x random
- Together: B programs carry their A-context declaration in their header

## Dependencies

- C794 (Line-1 composite header structure)
- C734 (A-B coverage architecture)
- C753 (No content-specific routing - constraint propagation)

## Provenance

```
phases/B_LINE_POSITION_HT/scripts/line1_a_context.py
```
