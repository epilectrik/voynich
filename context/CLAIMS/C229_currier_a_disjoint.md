# C229: Currier A is DISJOINT

**Tier:** 2 | **Status:** CLOSED | **Phase:** CAud

---

## Claim

Currier A is grammatically DISJOINT from Currier B. The 49-class B grammar does not apply to A text.

## Evidence

| Metric | Currier A | Currier B | Verdict |
|--------|-----------|-----------|---------|
| Grammar coverage | 13.6% | 100% | FAIL |
| Transition validity | 2.1% | 100% | FAIL |
| Forbidden violations | 5 | 0 | FAIL |
| LINK density | 3.0% | 6.6% | Different |
| Token density | 0.35x B | 1.0x | Different |
| Silhouette score | 0.049 | Structured | No grammar |

## What This Means

- A and B use DIFFERENT formal systems
- A has NO sequential grammar
- A is REGULAR but NOT GRAMMATICAL
- The 49-class model is B-ONLY

## What IS Shared

Despite grammar disjunction:
- Same morphological type system (C383)
- Same prefix/suffix vocabulary (C281)
- Same token types, different usage patterns

## Related Constraints

- C224-228 - A coverage, transition, violation details
- C230 - A silhouette = 0.049
- C231 - A is REGULAR but NOT GRAMMATICAL
- C240 - A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
- C383 - GLOBAL TYPE SYSTEM shared

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
