# f68r1 / f68r2 / f68r3 Triple Foldout

**Date:** 2026-01-19
**Type:** Triple foldout with MIXED diagram types

## Summary

This foldout is **exceptionally unique** - the first two diagrams are NOT typical ring structures.

| Folio | Diagram Type | Key Feature |
|-------|--------------|-------------|
| f68r1 | Scatter circular | Tokens scattered in circle, NOT rings |
| f68r2 | Scatter circular | Same as f68r1 |
| f68r3 | Ring-spoke hybrid | Outer ring + spokes + inner ring |

---

## f68r1 (Left)

### Layout
```
+----------------------------------+
|  [P] Paragraph text (4 lines)    |  <- A-like text
|  28 tokens                       |
+----------------------------------+
|                                  |
|    ·    ·      ·    ·           |
|       ·     ·        ·          |
|    ·       ·    ·       ·       |  <- Scattered tokens (S)
|       ·  ·    ·    ·            |     29 tokens, 1 per "line"
|    ·      ·       ·    ·        |
|                                  |
+----------------------------------+
```

### Transcript Encoding
- `P`: 28 tokens, 4 lines - paragraph above
- `S`: 29 tokens, **29 separate lines** - each scattered token gets own line
- `X`, `Y`: 8 tokens - other positions

---

## f68r2 (Center)

### Layout
Same pattern as f68r1:
- Paragraph text above (P: 37 tokens, 5 lines)
- Scatter circular diagram below (S: 25 tokens)
- Labels (L: 11 tokens)

---

## f68r3 (Right) - More Typical Structure

### Layout
```
+----------------------------------+
|         OUTER RING (C1)          |  <- 38 tokens, continuous
|    +------------------------+    |
|    |   /    |    \         |    |
|    |  / [R] | [R] \   [X]  |    |  <- R = 8 spoke lines
|    | /      |      \       |    |     X = scattered between
|    |/   INNER (C2)  \      |    |  <- 10 tokens, continuous
|    |\       |       /      |    |
|    | \      |      /       |    |
|    +------------------------+    |
|                                  |
+----------------------------------+
```

### Transcript Encoding
- `C1`: 38 tokens, **all "line 1"** = continuous outer ring
- `C2`: 10 tokens, **all "line 1"** = continuous inner ring
- `R`: 38 tokens, **8 lines** = 8 radial spokes (~5 tokens each)
- `X`: 16 tokens - scattered between spokes

---

## Transcript Encoding Pattern

**Key insight:** The line number encodes spatial arrangement:

| Pattern | Line Numbers | Meaning |
|---------|--------------|---------|
| Ring/circle | All same line | Continuous circular text |
| Spokes | N lines | N radial spokes |
| Scattered | 1 token/line | Non-sequential positions |

---

## Oddities

1. **Non-ring circular diagrams** (f68r1, f68r2)
   - Circular area but tokens are scattered, not in rings
   - Encoded as S-placement with 1 token per line

2. **A-like paragraph on AZC folio** (f68r1, f68r2)
   - Paragraph text above diagrams
   - Linguistically resembles Currier A

3. **Hybrid structure** (f68r3)
   - Combines rings (C1, C2), spokes (R), and scatter (X)
   - More complex than zodiac pages

---

## Implications

- Not all AZC diagrams are "ring diagrams"
- The S placement code may indicate scatter patterns, not just "star" shapes
- Paragraph text on AZC folios may be functionally Currier A
