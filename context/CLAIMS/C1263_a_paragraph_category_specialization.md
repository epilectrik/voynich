# C1263: A Paragraph Category Specialization

**Tier:** 2
**Scope:** A
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

A paragraphs specialize by operational category. Within-paragraph category entropy 2.533 vs null 2.623 (d=12.5, p<0.001, 1000 permutations). 242 paragraphs with 3+ categorized PP MIDDLEs tested, median paragraph size 34 tokens.

## Architecture

- **Paragraphs are category-themed.** Each A paragraph focuses on a subset of operational categories more than random MIDDLE selection would produce.
- **Extends C1039.** C1039 established paragraph cluster selectivity via C475 compatibility clusters. C1263 shows this extends into operational category space -- paragraphs select not just compatible MIDDLEs but thematically related ones.
- **Effect even larger than record-level.** Cohen d=12.5 (vs 9.7 at record level, C1261), suggesting category coherence accumulates at higher organizational scales.

## Key Findings

| Metric | Value |
|--------|-------|
| Observed mean entropy | 2.533 |
| Null mean entropy | 2.623 +/- 0.007 |
| Cohen d | 12.5 |
| p-value | <0.001 |
| Paragraphs tested | 242 |
| PP tokens | (across all paragraphs) |
| Par size median | 34 tokens |
| Par size range | [3, 266] |

## Provenance

- Builds on C1039 (paragraph cluster selectivity), C1040 (folio paragraph compatibility), C850
- Extends C1250 (8 operational categories) to paragraph organizational unit
- Paragraph boundaries from par_initial/par_final flags in transcript
