# C764 - f57v R2 Coordinate System Function

**Tier:** 2 | **Status:** CLOSED | **Scope:** AZC

## Statement

The f57v R2 single-character ring functions as a positional coordinate system unique to the cosmological diagram. The pattern is specific to f57v (no other Zodiac folio has it), uses systematic p/f gallows substitution to mark ring halves, and has 1:1 token correspondence with the content ring R1.

## Evidence

### T1: f57v Uniqueness

Surveyed all 13 Zodiac family folios (12 Z + f57v). Results:

| Folio | Max Single-Char % in Any Ring |
|-------|------------------------------|
| f57v | 100% (R2), 72% (R4) |
| All others | 0-8% |

**f57v R2/R4 single-char pattern is UNIQUE** - no other Zodiac folio exhibits this.

### T2: p/f Systematic Substitution

| Gallows | Position | Preceding Context | Following Context |
|---------|----------|-------------------|-------------------|
| p | 6 | `x k k` | `t r y c o` |
| f | 33 | `x k k` | `t r y c o` |

- First p and first f are **27 positions apart** (exactly half of 50-token ring)
- **Angular separation: ~194 degrees** (opposite sides of ring)
- Both preceded by `x k k` marker

This confirms p/f marks **two variants of the same structural position** on opposite ring halves.

### T3: R1-R2 Token Correspondence

| Ring | Total Tokens | Clean Tokens (no *) |
|------|--------------|---------------------|
| R1 | 51 | 50 |
| R2 | 69 | 50 |

**Exactly 50 tokens each** - 1:1 correspondence between coordinate layer (R2) and content layer (R1).

### 'x' as Coordinate Marker

- 'x' appears **4 times in R2** at positions [3, 20, 30, 44]
- 'x' appears **0 times in R1**
- 'x' is used exclusively for positional marking, not content

## Structural Model

```
R2 COORDINATE SYSTEM:
  [section 1]     [section 2]
  o d r X K K p...  ...X K K f...m n
        ↑              ↑        ↑
    marker 1       marker 2  terminators
    (p variant)    (f variant)
```

Components:
1. **`x k k` markers** - Section boundaries (positions 3, 30)
2. **`p`/`f` variants** - Distinguish first/second half of ring
3. **`m n` terminators** - Mark sequence end (unique chars)
4. **1:1 indexing** - R2 positions map to R1 content positions

## Functional Interpretation

R2 is deliberately non-Voynichese because it serves a **different function** than content rings:

1. **Below morphological threshold** - Single chars don't trigger C475 MIDDLE incompatibility
2. **Scaffold, not content** - Provides positional framework for R1 vocabulary
3. **Diagram-specific** - Not part of A->AZC->B pipeline (no morphology to filter)

This is consistent with expert analysis: R2 is "grid lines" of the diagram, not content.

## Cross-References

- C763 (f57v R2 Single-Char Anomaly - initial documentation)
- C430 (AZC Bifurcation - f57v in Zodiac family)
- C540 (Kernel Primitives Bound - R2 violates this, confirming non-standard function)
- C529-530 (Gallows Patterns - p/f as specialized markers)

## Source

F57V_COORDINATE_RING phase (T1-T3)
