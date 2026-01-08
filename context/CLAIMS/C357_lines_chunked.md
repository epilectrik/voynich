# C357: Lines are DELIBERATELY CHUNKED

**Tier:** 2 | **Status:** CLOSED | **Phase:** LINE

---

## Claim

Line lengths in Currier B are 3.3x more regular than random breaks. Lines are DELIBERATELY CHUNKED formal control blocks, not scribal wrapping.

## Evidence

| Metric | Observed | Random | Ratio |
|--------|----------|--------|-------|
| Length CV | 0.263 | 0.881 | 3.3x more regular |
| Z-score | -3.60 | - | Highly significant |

## Line Architecture

| Position | Enriched Tokens | Enrichment |
|----------|-----------------|------------|
| Line-initial | daiin, saiin, sain | 3-11x |
| Line-final | am, oly, dy | 4-31x |
| Boundaries | LINK suppressed | 0.60x |

## Key Findings

- Grammar forbidden transitions respected across line breaks (0 violations in 2,338 cross-line bigrams)
- Grammar is LINE-INVARIANT
- LINK tokens are suppressed at boundaries (not pause points)
- Lines are formal structural units

## What Lines ARE

Lines function as **micro-stages** within programs:
- Each line is a control block
- Boundary tokens mark entry/exit
- Grammar flows continuously across lines
- Physical line ≈ conceptual instruction group

## Related Constraints

- C358 - Boundary token identification
- C359 - LINK suppressed at boundaries
- C360 - Grammar LINE-INVARIANT

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
