# f67r1 / f67r2 Double Foldout

**Date:** 2026-01-19
**Quire:** 9
**Type:** Double foldout

---

## f67r1 (Left Diagram)

### Layout
```
+----------------------------------+
|  [P] Paragraph text (4 lines)    |  <- A-like text above
|  36 tokens                       |
+----------------------------------+
|         ___________              |
|       /   Ring 3    \            |
|      /  ___________  \           |
|     / /   Ring 2   \ \           |
|    / /  _________  \ \           |
|   | | /  Ring 1  \ | |           |
|   | | |    •     | | |           |  <- Short spokes (S)
|   | | | • center | | |           |     1-2 tokens each
|   | | \__________/ | |           |
|    \ \____________/ /            |
|     \______________/             |
+----------------------------------+
```

### Transcript Structure
| Placement | Tokens | Lines | Description |
|-----------|--------|-------|-------------|
| P | 36 | 4 | Paragraph above (A-like) |
| R | 102 | 3 | 3 concentric rings |
| S | 17 | 12 | Short 1-2 token spokes |

---

## f67r2 (Right Diagram) - Complex Segmented Structure

### Layout
```
+------------------------------------------+
|              OUTER RING                   |
|           *** RED INK ***                 |
|    +-----------------------------+        |
|    |   a  |   b   |   c   |  d  |        |  <- Sector dividers
|    |  2a  |  2b   |  2c   | 2d  |  Ring 2|     (drawn lines)
|    |------+-------+-------+-----|        |
|    |  3a  |  3b   |  3c   |     |  Ring 3|
|    |------+-------+-------|     |        |
|    |     Inner rings      |     |        |  <- No dividers
|    |     (near center)    |     |        |     near center
|    +-----------------------------+        |
|                                           |
+------------------------------------------+
|  ══════════════════════════════════════  |  <- Line 1
|  ══════════ RED INK LINE ══════════════  |  <- Line 2 (center)
|  ══════════════════════════════════════  |  <- Line 3
+------------------------------------------+
     ↑ 3 horizontal lines with drawn dividers
```

### Transcript Structure
| Placement | Tokens | Encoding | Description |
|-----------|--------|----------|-------------|
| C | 87 | "1a", "2b", etc. | Segmented rings (number=ring, letter=sector) |
| P | 33 | 3 lines | Horizontal text below with dividers |
| L | 9 | - | Labels |
| X | 13 | scattered | Other positions |
| Y | 25 | grouped | Other positions |
| Z | 9 | - | Other positions |

### Key Discovery: Segmented Ring Encoding

The transcript uses **alphanumeric line codes** to encode the segmented structure:

| Code | Meaning |
|------|---------|
| 1a, 1b, 1c, 1d | Ring 1 (outer), sectors a through d |
| 2a, 2b, 2c | Ring 2, sectors a through c |
| 3a, 3b, 3c | Ring 3, sectors a through c |

The letters correspond to the **pie-slice sectors** created by the drawn radial divider lines.

---

## Visual Features

### Red Ink Usage
- **Outer ring** of f67r2 diagram
- **Center line** of the 3 horizontal lines below

This links the outer boundary to a central element.

### Drawn Divider Lines
1. **In diagram:** Radial lines dividing rings into angular sectors
2. **Below diagram:** Horizontal lines separating the 3 text rows

---

## Comparison

| Feature | f67r1 | f67r2 |
|---------|-------|-------|
| Paragraph above | Yes (A-like) | No |
| Ring structure | 3 simple rings | Segmented rings |
| Spokes | Short (1-2 tokens) | Drawn lines (dividers) |
| Special ink | No | Red (outer + center) |
| Text below | No | Yes (3 structured lines) |

---

## Implications

1. **Transcript encodes sector structure** via alphanumeric codes
2. **Red ink marks boundaries** (outer ring ↔ center line connection)
3. **Drawn dividers** create a grid-like organization within the circular form
4. **f67r2 is more complex** than typical ring diagrams
