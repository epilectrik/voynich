# C411: Deliberate Over-Specification

**Tier:** 2 | **Status:** CLOSED | **Phase:** SITD

---

## Claim

The Currier B grammar is deliberately over-specified. It contains substantially more instruction classes (49) than minimally required to preserve transition entropy and hazard topology.

## Evidence

| Metric | Original | Reducible | Reduction |
|--------|----------|-----------|-----------|
| Instruction classes | 49 | 29 | ~40% |
| Entropy cost | - | ≤1% per merge | Negligible |
| Hazard preservation | 17 | 17 | Complete |

## What Collapses

| Category | Original | Reduced | Notes |
|----------|----------|---------|-------|
| ENERGY_OPERATOR | 11 | 2 | Massive redundancy |
| AUXILIARY | 8 | 1 | Fully collapsible |
| CORE_CONTROL | 2 | 2 | REFUSES to merge |

## What This Means

The 49-class system exists for HUMAN reasons:
- Mnemonic distinctiveness
- Ergonomic variety
- Readability
- Learnability

NOT for minimal information encoding.

## CORE_CONTROL Resistance

`daiin` and `ol` refuse to merge despite similar transition profiles. These tokens serve infrastructural roles that require distinct identity.

## Forgiving/Brittle Axis (Tier 4)

Programs vary along a forgiveness dimension (5σ spread):
- Brittle: f33v, f48v, f39v (concentrated hazards, few escapes)
- Forgiving: f77r, f82r, f83v (many escape routes)

This axis is partially orthogonal to aggressive/conservative.

## Related Constraints

- C121 - 49 instruction classes
- C331 - Minimality confirmed (but not optimal)
- C293 - Component essentiality hierarchy

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
