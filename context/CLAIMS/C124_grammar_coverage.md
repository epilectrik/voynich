# C124: 100% Grammar Coverage

**Tier:** 0 | **Status:** FROZEN | **Phase:** Phase 20

---

## Claim

**[Corrected (Tier-0 restatement 2026-09-28): the 100% is coverage of the grammar's own 480-type vocabulary, which is 69.5% of Currier B tokens; the remaining 30.5% (HT/UN) is defined by exclusion (C566, C740). The original wording below is historical.]**

The 49-class grammar achieves 100% coverage of all Currier B tokens. Every token in the B corpus maps to exactly one instruction class.

## Evidence

- 0 unclassified tokens in Currier B
- 0 tokens requiring special handling
- All 75,248 instructions in 83 folios are grammar-compliant [historical: 75,248 is an all-transcriber count; the H track has 23,243 Currier B tokens]
- Cross-validation stable (leave-one-folio-out shows max 0.25% entropy change)

## Significance

Complete coverage proves:
- The grammar is EXHAUSTIVE (no residue)
- The text is HOMOGENEOUS (single formal system)
- Classification is DETERMINISTIC (no ambiguity)

## Contrast with Other Systems

| System | Grammar Coverage |
|--------|------------------|
| Currier B | 100% |
| Currier A | 13.6% (grammar doesn't apply) |
| Human Track | 0% (outside grammar vocabulary) |

## Related Constraints

- C121 - 49 instruction classes
- C115 - 0 non-executable tokens
- C120 - PURE_OPERATIONAL verdict

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
