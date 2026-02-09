# C729: C475 Record-Level Scope

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

MIDDLE incompatibility (C475) operates perfectly at the Currier A record (line) level. **Zero** within-folio avoidance pairs appear on the same line across all 114 A folios.

| Metric | Value |
|--------|-------|
| Within-folio avoidance pairs | 15,518 |
| Observed avoidance violations | 0 |
| Illegal pair rate | 0.000 |
| Mean avoidance pairs in free shuffle | 2,530 per iteration |

When PP MIDDLEs are freely shuffled across lines within a folio (preserving line lengths), an average of 2,530 avoidance pairs land on the same line per iteration. The observed data has exactly zero. This perfect compliance confirms that MIDDLE incompatibility is enforced at the line level, not just at the folio level.

## Implication

C475 was originally established on AZC folios. This result confirms the same incompatibility structure operates on Currier A records. MIDDLEs that never co-occur in AZC contexts also never co-occur within A lines. The incompatibility constraint is system-wide, applying to all text contexts where MIDDLEs appear together.

This means that each A record (line) is a **legal combination** of MIDDLEs drawn from the folio pool — incompatible combinations simply don't appear (they reflect fixed positional encoding).

## Key Numbers

| Metric | Value |
|--------|-------|
| Co-occurring pair types | 5,460 |
| Avoidance pair types | 15,518 |
| Violations | 0 |
| Legal-only observed variance | 80.93 |
| Legal-only null variance | 142.97 +/- 3.75 |
| p (legal excess) | 1.000 |

The legal-only variance being BELOW null (p=1.0) means that among compatible pairs, co-occurrence is actually more uniform than random — no concentration effects beyond what frequency alone predicts.

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_cooccurrence_tests.py` (T2)
- Extends: C475 (MIDDLE incompatibility), now confirmed at A record level
- Consistent with: C728 (co-occurrence fully explained by incompatibility)
