# C1350: Dark MIDDLEs Are Atomistically Distributed, Not Combinatorially Grouped

**Tier:** 2
**Scope:** B
**Phase:** DARK_PIPELINE_STRUCTURE (472)

## Constraint

Dark pipeline MIDDLEs show no stable co-occurrence groups within folios beyond what section concentration (C1148) predicts. Within-section pairwise Jaccard does not exceed permutation null in any of 5 sections (0 significant at p<0.05). Dark-dark adjacency on lines matches random placement exactly (observed/null ratio=1.024, p=0.76). Dark MIDDLEs operate as independent atomistic signals, not as combinatorial groups (ruling out material-list or ingredient-set behavior).

## Evidence

From dark_pipeline_structure.py tests T1 and T5 (92 reliable dark MIDDLEs with ≥5 B tokens):

**T1 within-section co-occurrence (Jaccard):**

| Section | MIDDLEs | Mean Jaccard | Null mean | Perm p |
|---------|---------|-------------|-----------|--------|
| B | 64 | 0.093 | 0.090 | 0.165 |
| C | 43 | 0.241 | 0.231 | 0.143 |
| H | 70 | 0.046 | 0.043 | 0.103 |
| S | 92 | 0.109 | 0.108 | 0.137 |
| T | 35 | 0.521 | 0.531 | 0.857 |

No section shows co-occurrence significantly above null. Within-section mean Jaccard (0.127) is higher than global (0.082) because sections compress the folio space, but the structure is entirely explained by span overlap under random folio assignment.

**T5 dark-dark adjacency:**

| Metric | Value |
|--------|-------|
| Dark-dark adjacent pairs | 134 |
| Total adjacent pairs | 20,676 |
| Observed rate | 0.00648 |
| Null rate | 0.00633 |
| Ratio | 1.024 |
| Perm p (two-sided) | 0.76 |

Dark tokens are randomly interspersed among grammar tokens at exactly the density their frequency predicts.

## Interpretation

If dark MIDDLEs were material referents (substances/ingredients), they would form stable co-occurrence groups (recipes share ingredient sets) and might cluster adjacently on lines (ingredient listings). Neither pattern is observed. Dark MIDDLEs are atomistic — each operates independently within its folio, without requiring the presence of specific other dark MIDDLEs. This is consistent with dark MIDDLEs as independent context-setting signals rather than members of combinatorial sets.

## Provenance

- dark_pipeline_structure.json: tests T1, T5
- Extends: C1148 (section concentration — T1 shows no structure beyond section)
- Extends: C1147 (interior enrichment — T5 shows random placement within that interior zone)
- Extends: C657 (PP behavioral profile continuity — dark pipeline follows the same continuous, non-clustered pattern)

## Status

CONFIRMED — dark MIDDLEs are atomistic: no within-section co-occurrence structure (0/5 sections significant), no adjacency clustering (ratio=1.02, p=0.76).
