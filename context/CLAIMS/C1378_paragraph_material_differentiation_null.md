# C1378: Paragraph-Level Material Differentiation (NULL)

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_MATERIAL_DIFFERENTIATION (Phase 492)
**Date:** 2026-02-28

## Statement

Within-folio paragraphs do NOT show MIDDLE vocabulary differentiation consistent with encoding different plant materials. Dark-pipeline MIDDLEs (the identification substrate) are nearly identical across paragraphs within a folio (Jaccard 0.972 within vs 0.963 between, ratio 1.009x, p=0.98). The semantic ceiling (C171) extends to paragraph granularity.

## Hypothesis Tested

Each Voynich folio represents a multi-material distillation session (Brunschwig 6-still water bath, 15th-C 4-vent furnaces). Each paragraph encodes one material's procedure. If so, paragraphs within a folio should share operational vocabulary (same apparatus) but differentiate on identification vocabulary (different materials).

**Two-level prediction (pre-registered):**
- Category profiles CONVERGE within folio (same fire degree, same apparatus) — confirmed by C1288
- Dark-pipeline MIDDLEs DIVERGE within folio (different materials) — **TESTED HERE**

## Evidence

### T1: All MIDDLEs (baseline)
- Within-folio Jaccard: 0.786, between-folio (same REGIME): 0.719
- Ratio: 1.094x (within > between — wrong direction)
- p = 0.997, **NULL**

### T2: Dark-Pipeline MIDDLEs (KEY TEST)
- Within-folio Jaccard: 0.972, between-folio (same REGIME): 0.963
- Ratio: 1.009x (near-identical, wrong direction)
- p = 0.980, **NULL**
- 1,858 within-pairs, 691 between-pairs

### T3: Bridge MIDDLEs (control)
- Within-folio Jaccard: 0.717, between-folio: 0.572
- Ratio: 1.254x — **CONTROL_PASS** (bridge vocabulary IS folio-coherent, as expected)

### T4: Header vs Body Diversity
- Header Jaccard: 0.885, Body Jaccard: 0.797
- Ratio: 1.111x, p = 0.0001, **PASS**
- Headers are significantly more diverse than bodies within folio
- New structural finding: paragraph headers sample from wider MIDDLE vocabulary

### T5: Paragraph Counts (exploratory)
- Section-driven: H=4.2, S=12.5, B=6.6, C=5.8
- REGIME-correlated: R2=4.9, R3=11.1, R4=4.3, R1=8.2

## Interpretation

Dark-pipeline MIDDLEs — the identification-substrate vocabulary (C1135) — show near-perfect within-folio sharing (0.972 Jaccard). Paragraphs on the same folio use essentially the same dark-pipeline vocabulary, not different subsets that would indicate different materials. The multi-material hypothesis remains structurally plausible (C845 self-containment, C855 role templates) but is not recoverable from MIDDLE vocabulary at paragraph granularity.

The T4 finding (header diversity) qualifies C855: while paragraphs share role profiles, their headers draw from a wider vocabulary pool than their bodies. This is consistent with headers performing identification/setup while bodies execute constrained programs.

## Qualifies

- C171 (semantic ceiling) — extends to paragraph-level MIDDLE vocabulary
- C845 (paragraph self-containment) — confirmed; independent programs, shared vocabulary
- C855 (folio role template) — qualified; headers more diverse than bodies (1.11x)
- C1257 (consecutive paragraph vocabulary coupling) — consistent; weak coupling is equipment-sharing, not material-differentiation
- C1377 (Puff structural revisit NULL) — converges; material identity irrecoverable at both folio and paragraph level

## Method

- 72 folios with 3+ paragraphs, 461 paragraphs total
- Pairwise Jaccard diversity between paragraph MIDDLE sets
- Within-folio vs between-folio (same REGIME) comparison
- 10,000 permutations, Bonferroni-corrected p < 0.0025
- Dark-pipeline (300 MIDDLEs, C1135) vs bridge (85 MIDDLEs, C1139) separation

## Provenance

- Script: `phases/PARAGRAPH_MATERIAL_DIFFERENTIATION/scripts/paragraph_material_test.py`
- Results: `phases/PARAGRAPH_MATERIAL_DIFFERENTIATION/results/paragraph_material_test.json`
- Pre-registration: `phases/PARAGRAPH_MATERIAL_DIFFERENTIATION/results/pre_registration.json`
- Depends: C171, C845, C855, C1083, C1135, C1139, C1257, C1288

## Status

CONFIRMED NULL — Material differentiation not recoverable at paragraph granularity. Semantic ceiling holds.
