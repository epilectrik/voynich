# C685: LINK and Kernel Survival Rates

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

Kernel access is highly preserved under filtering: **97.4% of records retain at least one token containing k, h, or e** (confirming C503.c).

> **Aggregation Note (2026-01-30):** This constraint analyzes at line level (1,562 units).
> Per C881, A records are paragraphs (342 units). Per C885, the operational unit for
> A-B vocabulary correspondence is the A FOLIO (114 units, 81% coverage).

LINK token survival is more fragile: 36.5% of records have zero legal LINK tokens.

## Key Numbers

| Metric | Value |
|--------|-------|
| B LINK token types | 801 (16.4% of B vocabulary) |
| Mean LINK density (legal LINK / legal total) | 0.168 |
| Records with zero LINK tokens | 570 (36.5%) |

### Kernel Character Access

| Character | Records Retaining | % |
|-----------|------------------|---|
| k | 1,265 | 81.0% |
| h | 1,491 | 95.5% |
| e | 948 | 60.7% |
| Any (k/h/e) | 1,521 | 97.4% |

## Interpretation

The kernel triad (k, h, e) has a natural survival hierarchy: **h > k > e**. The 'h' character appears in the most common MIDDLEs and survives nearly universally. The 'e' character is most fragile — 39.3% of records lose all e-containing tokens. Despite this, the union (any k/h/e) is preserved at 97.4%, meaning the three kernel characters provide redundant coverage.

LINK token loss (36.5%) is significant: these records lose monitoring/intervention capacity (C609). This correlates with low PP MIDDLE counts — records that admit few B tokens also lose the 'ol'-containing LINK vocabulary.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/survivor_population_profile.py` (Test 4)
- Extends: C503.c (kernel access), C609 (LINK operator definition)
