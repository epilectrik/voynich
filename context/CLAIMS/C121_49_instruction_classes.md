# C121: 49 Instruction Equivalence Classes

**Tier:** 0 | **Status:** FROZEN | **Phase:** Phase 20

---

## Claim

The Currier B grammar compresses 479 unique token types into exactly 49 instruction equivalence classes, achieving 9.8x compression.

## Evidence

- 479 distinct token types in canonical B vocabulary
- Merge to 49 classes preserving transition structure
- 9.8x compression ratio (479 ÷ 49)
- Asymptotic: further merging loses structural information
- Cross-validated: no single folio dominates (max 0.25% entropy change)

## Significance

This compression proves the text is:
- NOT random (would not compress)
- NOT natural language (different compression signature)
- A FORMAL SYSTEM with finite instruction set

## Related Constraints

- C124 - 100% grammar coverage
- C331 - 49-class minimality confirmed
- C411 - Grammar deliberately over-specified (~40% reducible)

## Key Metric

| Metric | Value |
|--------|-------|
| Raw token types | 479 |
| Equivalence classes | 49 |
| Compression ratio | 9.8x |
| Grammar coverage | 100% |

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
