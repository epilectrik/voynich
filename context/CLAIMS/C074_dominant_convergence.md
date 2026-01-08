# C074: Dominant Convergence to Stable States

**Tier:** 0 | **Status:** FROZEN | **Phase:** Phase 13-14, SEL-F

---

## Claim

The Currier B grammar exhibits dominant convergence to STATE-C, with 57.8% of folios terminating in this stable state.

## Evidence

- 57.8% of folios terminate in STATE-C (stable endpoint)
- 42.2% end in transitional states (not failures, just incomplete)
- STATE-C percentage increases with folio position (rho=+0.24, p=0.03)
- Sections H/S show ~50% STATE-C; Sections B/C show 70-100%

## Revision History

- **Original claim:** "100% convergence to STATE-C"
- **SEL-F revision:** Only 57.8% terminate in STATE-C; 42.2% in transitional states
- Convergence is DOMINANT, not UNIVERSAL

## Related Constraints

- C079 - Only STATE-C essential
- C084 - System targets MONOSTATE
- C323 - Terminal state distribution details
- C324 - Terminal state is section-dependent
- C325 - Completion gradient exists

## Key Metric

| Terminal State | Percentage |
|----------------|------------|
| STATE-C | 57.8% |
| Transitional | 38.6% |
| Initial/Reset | 3.6% |

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
