# C1122: Rosettes-B Bridge-Dominant Vocabulary Architecture

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** ROSETTES_B_VOCABULARY_TRACING (Phase 401)
**Extends:** C1098 (structural index), C1109 (vocabulary-mediated cross-reference)
**Relates to:** C1091 (multi-target cross-reference), C1096 (bridge enrichment), C1013 (bridge topological generality)

---

## Statement

Rosettes-to-B vocabulary connection is 77% bridge-mediated. Of the Rosettes vocabulary that also appears in B programs, only 26 MIDDLEs (across 9 rosettes) are non-bridge informative tokens. Each rosette's informative vocabulary is completely non-overlapping with every other rosette's (all pairwise Jaccard = 0.000). Individual B-folio targeting does not survive bridge-stripping (C1091 lift=1.55x, p=0.114 NS at informative level). The connection between Rosettes and B operates through universal bridge vocabulary (C1013), not through specific shared content.

---

## Evidence

### Vocabulary Partition (Per-Rosette)

| Rosette | Total MIDDLEs | Bridge | Exclusive | Informative |
|---------|---------------|--------|-----------|-------------|
| CENTER | 33 | 22 | 3 | 8 |
| WEST | 24 | 17 | 2 | 5 |
| NW | 25 | 18 | 3 | 4 |
| SW | 24 | 15 | 5 | 4 |
| NORTH | 23 | 18 | 3 | 3 |
| SOUTH | 20 | 18 | 0 | 2 |
| NE | 2 | 1 | 1 | 0 |
| SE | 4 | 3 | 1 | 0 |

Union of informative MIDDLEs: 26. Bridge set: 85. Exclusive set: 101.

### Zero Pairwise Overlap

All 28 pairwise Jaccard values between rosette informative vocabularies are 0.000. No two rosettes share ANY non-bridge MIDDLE that also appears in B. This means the Rosettes achieves vocabulary coverage through complementary specialization, not redundancy.

### C1091 Validation at Informative Level

Pharma target folios (f76r, f108r, f111r, f108v, f116r): mean shared informative MIDDLEs = 3.4 vs non-target mean = 2.2 (lift 1.55x, permutation p=0.114). Not significant — the folio-level targeting documented in C1091 is carried by bridge vocabulary, not informative vocabulary.

### No Positional Concentration

Rosette-shared MIDDLEs appear uniformly throughout B paragraphs: mean position 0.480 vs all-token mean 0.479 (Wilcoxon p=0.779). No specification-zone or execution-zone bias. No C932 rarity artifact.

### PREFIX+MIDDLE Exhaustion

PREFIX+MIDDLE combinations add 0 new MIDDLEs beyond individual MIDDLE analysis. PM F-ratio (14.15) is lower than MIDDLE-only F-ratio (42.57). Investigation exhausted at all resolution levels.

---

## Provenance

- Phase: 401 (ROSETTES_B_VOCABULARY_TRACING)
- Scripts: `phases/ROSETTES_B_VOCABULARY_TRACING/scripts/rosettes_b_tracing.py`, `rosettes_grouping_test.py`
- Results: `phases/ROSETTES_B_VOCABULARY_TRACING/results/rosettes_b_tracing_results.json`, `rosettes_grouping_results.json`
- Related: C1091, C1096, C1098, C1109, C1013, C932
