# f68v3 / f68v2 / f68v1 Triple Foldout

**Date:** 2026-01-19
**Quire:** 9
**Note:** Verso of f68r1_f68r2_f68r3

---

## Summary

| Folio | Type | P-text | Rings | Spokes | Center |
|-------|------|--------|-------|--------|--------|
| f68v3 | ring_spoke_segmented | Yes | 2 (O,I) | 8 curved | 3 segmented areas |
| f68v2 | single_ring_spoke | Yes | 1 (C) | 8 sparse | Illustration only |
| f68v1 | double_ring_spoke | **NO** | 2 (C) | 8 | Illustration only |

---

## f68v3 (Left) - Segmented Center

### Layout
```
+----------------------------------+
|  [P] Paragraph text (4 lines)    |  <- A-like text
|  40 tokens                       |
+----------------------------------+
|         OUTER RING [O]           |  <- 49 tokens
|    +------------------------+    |
|    |    ~~~~ [S] ~~~~      |    |  <- 8 curved spokes
|    |   ~  INNER [I]   ~    |    |     (artistic)
|    |  ~  +---------+   ~   |    |
|    | ~   | [L] [L] |    ~  |    |  <- Top: 2 single tokens
|    |  ~  +---------+   ~   |    |
|    |   ~ |   [B]   |  ~    |    |  <- Bottom: 3 lines
|    |    ~+---------+~      |    |     11 tokens
|    +------------------------+    |
+----------------------------------+
```

### Transcript Structure
| Placement | Tokens | Lines | Description |
|-----------|--------|-------|-------------|
| P | 40 | 4 | Paragraph above |
| O | 49 | 1 | Outer ring |
| S | 45 | 8 | Curved spokes |
| I | 12 | 1 | Inner ring |
| L | 2 | 2 | Top center singles |
| B | 11 | 3 | Bottom center (3 lines) |

### Key Feature
Center divided into **3 areas by drawn lines**:
- Top-left: 1 token
- Top-right: 1 token
- Bottom: 3 lines of tokens (11 total)

---

## f68v2 (Center) - Single Ring + Illustration Center

### Layout
```
+----------------------------------+
|  [P] Paragraph text (5 lines)    |  <- 43 tokens
+----------------------------------+
|         OUTER RING [C]           |  <- 32 tokens
|    +------------------------+    |
|    |  /    |    \          |    |
|    | / [R] | [R] \   [S]   |    |  <- 8 spokes (sparse)
|    |/      |      \        |    |     R: 17 tokens
|    |                       |    |     S: 8 tokens
|    |   (illustration)      |    |  <- No text in center
|    |                       |    |
|    +------------------------+    |
+----------------------------------+
```

### Transcript Structure
| Placement | Tokens | Lines | Description |
|-----------|--------|-------|-------------|
| P | 43 | 5 | Paragraph above |
| C | 32 | 1 | Outer ring |
| R | 17 | 8 | Spokes (~2 tokens each) |
| S | 8 | 4 | Additional spoke-area tokens |

---

## f68v1 (Right) - Double Ring, No Paragraph

### Layout
```
+----------------------------------+
|  (NO paragraph text)             |  <- UNIQUE
+----------------------------------+
|        OUTER RING 1 [C.1]        |  <- 38 tokens
|    +------------------------+    |
|    |   OUTER RING 2 [C.2]  |    |  <- 38 tokens
|    |  +------------------+ |    |
|    |  |  /   |   \      | |    |
|    |  | /[X] |[X] \     | |    |  <- 8 spokes
|    |  |/     |     \    | |    |     20 tokens
|    |  |                 | |    |
|    |  | (illustration)  | |    |  <- No text
|    |  |                 | |    |
|    |  +------------------+ |    |
|    +------------------------+    |
+----------------------------------+
       ↑ Heavy illustration throughout
```

### Transcript Structure
| Placement | Tokens | Lines | Description |
|-----------|--------|-------|-------------|
| C | 76 | 2 | **2 rings** (38 + 38) |
| X | 20 | 8 | Spokes |

### Key Feature
**NO paragraph text** - the only folio in this foldout without P-placement.

---

## Placement Code Variation

Note: Each folio uses different codes for similar structures:

| Structure | f68v3 | f68v2 | f68v1 |
|-----------|-------|-------|-------|
| Outer ring | O | C | C |
| Inner ring | I | - | (C line 2) |
| Spokes | S | R, S | X |
| Center | B, L | - | - |
| Paragraph | P | P | (none) |

This inconsistency suggests transcriber discretion rather than strict encoding rules.

---

## Oddities

1. **Segmented center** (f68v3)
   - Center divided by drawn lines into 3 distinct areas
   - Different token counts in each area

2. **Missing paragraph** (f68v1)
   - No A-like text block above diagram
   - Unique among the three folios

3. **Illustration-only centers** (f68v2, f68v1)
   - Center areas contain artwork but no text tokens

4. **Curved spokes** (f68v3)
   - Artistic flourish, not structural
   - Other folios have straight spokes

---

## Comparison with Recto

| Feature | f68r1/r2/r3 | f68v3/v2/v1 |
|---------|-------------|-------------|
| Diagram types | Scatter + hybrid | All ring-spoke |
| P-text | 2 of 3 | 2 of 3 |
| Ring structure | Absent (scatter) | Present (all) |
| Spokes | Only f68r3 | All three |
| Center content | Text clusters | Mixed (text + illustration) |
