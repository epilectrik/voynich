# C384: NO Entry-Level A-B Coupling

**Tier:** 2 | **Status:** CLOSED | **Phase:** A-ARCH

---

## Claim

Although Currier A and B share vocabulary and type system, there is NO entry-level or folio-level cross-reference. A does NOT function as a lookup catalog for B programs.

## Evidence

| Test | Finding | Interpretation |
|------|---------|----------------|
| B folio A-vocab sharing | Jaccard 0.998 | ALL B folios use IDENTICAL A pool |
| One-to-one tokens | 215 tokens → 207 unique pairings | No repeated pairings beyond noise |
| Rare token distribution | Rare globally, not relationally | No targeting of specific A entries |

## What This Means

- B programs don't "look up" specific A entries
- A doesn't function as material index for B procedures
- Coupling occurs ONLY at global type-system level
- The relationship is architectural, not referential

## What IS Shared

Despite no entry-level coupling:
- 69.8% vocabulary integration (C335)
- Global type system (C383)
- Hybrid access pattern exists (C336)

## Contrast

| Model | Status |
|-------|--------|
| A = lookup catalog for B | FALSIFIED |
| A and B share global vocabulary pool | CONFIRMED |
| A entries map 1:1 to B procedures | FALSIFIED |
| A and B share type system | CONFIRMED |

## Related Constraints

- C335 - 69.8% vocabulary integration
- C336 - Hybrid A-access pattern
- C383 - Global type system

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
