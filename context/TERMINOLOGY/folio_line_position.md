# Folio, Line, Position

**Status:** CLOSED | Coordinate system for the manuscript

---

## Folio

**Definition:** A single leaf (page) of the manuscript.

| Property | Value |
|----------|-------|
| Total folios | 227 (original estimate) |
| Currier B folios | 83 |
| Currier A folios | 114 |
| AZC folios | 30 |

**Naming convention:** `f` + number + `r` (recto/front) or `v` (verso/back)

Examples:
- f1r = folio 1, front side
- f57v = folio 57, back side

---

## Line

**Definition:** A horizontal row of text within a folio.

| System | Median tokens/line |
|--------|-------------------|
| Currier A | 22 |
| Currier B | 31 |
| AZC | 8 |

**Lines are formal control blocks** (C357):
- 3.3x more regular than random chunking
- Specific boundary tokens mark entry/exit
- Grammar is line-invariant (transitions respected across breaks)

---

## Position

**Definition:** Location within a line (line-initial, mid-line, line-final).

### Positional Grammar (C371, C375)

| Position | Enriched Elements |
|----------|-------------------|
| Line-initial | so (6.3x), ych (7.0x), daiin (3x) |
| Line-final | -am (7.7x), -om (8.7x), am (31x) |
| Mid-line | Most tokens (default) |

### Boundary Properties

| Finding | Constraint |
|---------|------------|
| LINK suppressed at boundaries | C359 (0.60x) |
| Hazards depleted at line-initial | C400 (5-7x) |
| Zero hazards at folio-initial | C400 (0/82) |

---

## Coordinate Reference Format

When citing locations: `folio:line` or `folio:line:position`

Examples:
- f1r:3 = folio 1 recto, line 3
- f57v:12:initial = folio 57 verso, line 12, line-initial position

---

## Quire

**Definition:** A gathering of folios bound together.

| Finding | Value |
|---------|-------|
| Total quires | 18 |
| Single-section quires | 12/18 |
| Section-quire alignment | 4.3x random |

Quires are organizational units (C367-C370).

---

## Navigation

← [token_vs_type.md](token_vs_type.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
