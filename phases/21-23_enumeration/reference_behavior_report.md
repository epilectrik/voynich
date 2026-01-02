# Reference Behavior Test Report

*Generated: 2026-01-01T07:34:25.913492*

## Test Summary

This is the **DECISIVE** test (2x weight in final verdict).

**Question:** Do B-text sequences depend on A-text content non-locally?

---

## A-Text vs B-Text Statistics

| Metric | A-Text | B-Text |
|--------|--------|--------|
| Total records | 36620 | 75173 |
| Unique tokens | 4737 | 6985 |
| Unique 3-grams | 22297 | 75007 |

---

## Overlap Analysis

| Metric | Value |
|--------|-------|
| Shared tokens | 1485 |
| A-only tokens | 3252 |
| B-only tokens | 5500 |
| Jaccard similarity | 0.1451 |
| Reference rate (3-grams) | 0.0019 |
| Unique referenced patterns | 55 |

---

## DEFINITION_CORE Analysis

| Metric | Value |
|--------|-------|
| Definition cores in A | 5 |
| Definition cores in B | 3 |
| Present in BOTH | 3 |
| Cross-reference rate | 0.6000 |

**Sample cross-references:** sy, tcho, otch

---

## Non-Local Dependency Analysis

| Finding | Value |
|---------|-------|
| Non-local dependency detected | **False** |
| Evidence strength | LOW |
| A defines for B | True |

---

## Verdict

**CONTROL_SIGNAL**

### Interpretation

If Control Grammar: A-text and B-text are independent operational sequences with only local dependencies.

The reference rate of 0.0019 suggests primarily local dependencies.
