# C1261: A Record Category Coherence

**Tier:** 2
**Scope:** A
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

A records (folio, line) draw PP MIDDLEs from fewer operational categories (C1250) than expected by random assignment. Mean within-record category entropy 1.810 vs null 1.886 (d=9.7, p<0.001, 1000 permutations). 1,539 records with 2+ categorized PP MIDDLEs tested, 10,382 tokens total, 99.8% PP category coverage.

## Architecture

- **Records are category-themed.** When A writes a registry entry on a line, the PP MIDDLEs on that line tend to share an operational category. A THERMAL-heavy record doesn't randomly include MONITORING vocabulary.
- **Extends C475 into category dimension.** C475 established MIDDLE incompatibility at the structural level; C1261 shows that the compatible MIDDLEs that DO co-occur are further organized by operational theme.
- **Effect is massive.** Cohen d=9.7 means the observed entropy is ~10 standard deviations below the null. This is not a subtle signal.

## Key Findings

| Metric | Value |
|--------|-------|
| Observed mean entropy | 1.810 |
| Null mean entropy | 1.886 +/- 0.008 |
| Cohen d | 9.7 |
| p-value | <0.001 |
| Records tested | 1,539 |
| PP tokens | 10,382 |

## Provenance

- Builds on C1250 (8 operational categories), C475 (MIDDLE incompatibility), C233, C473
- Category assignment: 91 human-glossed + 1144 dark auto-assigned = 1235 MIDDLEs
