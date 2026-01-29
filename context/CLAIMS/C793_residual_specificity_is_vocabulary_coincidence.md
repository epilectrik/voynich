# C793: Residual Specificity = Vocabulary Coincidence

**Tier:** 2
**Scope:** A<>B
**Phase:** A_B_FOLIO_SPECIFICITY (extension)

## Constraint

The 24 A folios that emerge as "best-match" after removing pool-size confound (C751) do not represent content-specific routing. They are A folios whose vocabulary happens to be a good sample of the common PP MIDDLEs that B uses broadly.

## Evidence

### f42r Dominance Analysis

f42r is residual-best for 22/82 B folios (27%). Investigation reveals:

| Metric | Value |
|--------|-------|
| f42r pool size | 55 MIDDLEs |
| MIDDLEs shared across ALL 22 B folios | 8 |
| Those 8 MIDDLEs | aiin, ar, dy, iin, k, or, r, y |

The 8 core MIDDLEs are **near-universal in A**:

| MIDDLE | Appears in N/114 A folios |
|--------|---------------------------|
| iin | 110 (96%) |
| or | 111 (97%) |
| y | 106 (93%) |
| r | 100 (88%) |
| k | 88 (77%) |
| aiin | 85 (75%) |
| dy | 84 (74%) |
| ar | 55 (48%) |

### Section Distribution

f42r-best B folios are **evenly distributed** across sections:
- Section B: 25%
- Section C: 60%
- Section H: 22%
- Section S: 26%
- Section T: 50%

No section targeting is evident.

## Interpretation

C751's "24 distinct A folios with content specificity" is misleading. After pool-size removal:

1. **The residual best-match is determined by which A folio happens to have the most commonly-needed MIDDLEs**
2. **These are universal vocabulary items** (iin, or, y, r, k, aiin, dy, ar) present in most A folios
3. **Slight variations in which A folios have which common MIDDLEs** create residual differences
4. **This is vocabulary coincidence, not content routing**

C753's reframe (constraint propagation, not content routing) is **fully confirmed**.

## Dependencies

- C751 (coverage pool-size confound)
- C753 (no content-specific A-B routing)
- C756 (coverage optimization confirmed)

## Provenance

```
phases/A_B_FOLIO_SPECIFICITY/scripts/residual_a_characterization.py
phases/A_B_FOLIO_SPECIFICITY/scripts/f42r_investigation.py
```
