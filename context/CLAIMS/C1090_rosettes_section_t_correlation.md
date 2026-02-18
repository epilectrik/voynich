# C1090: Rosettes Section T Correlation

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Relates to:** C909 (section T h-monitoring enrichment), C554 (section S FQ elevation)

---

## Statement

Every Rosettes folio and every f85v2 region correlates most strongly with Section T (Stars/monitoring) by vocabulary Jaccard. This is uniform across all folios (f85r1 through f86v6) and all 16 f85v2 regions, despite the per-folio AZC-to-B gradient (C1088).

---

## Evidence

All 7 Rosettes folios show highest vocabulary Jaccard with Section T. All 16 f85v2 placement regions show highest correlation with Section T.

The Section T affinity is stable across the AZC-to-B gradient: both the most AZC-like folio (f85v2) and the most B-like folio (f86v6) correlate most with T.

---

## Interpretation

Section T was previously interpreted (INTERPRETATION_SUMMARY Section V) as "Product collection/quality control" — the output end of the manufacturing process. The Rosettes' uniform T-correlation suggests it functions as a reference or overview for the monitoring/quality-control layer of the procedural content.

---

## Method

- Vocabulary Jaccard between each Rosettes region and each B manuscript section (H, S, B, T, C)
- Per-folio and per-region comparison

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/rosettes_metalayer.py` (T1)
**Results:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_metalayer_results.json`

---

## Verdict

**SINGLE_SECTION_T**: Uniform Section T correlation across all Rosettes folios and regions, suggesting a monitoring/reference function.
