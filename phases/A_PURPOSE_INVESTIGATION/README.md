# A_PURPOSE_INVESTIGATION Phase

**Date:** 2026-02-04
**Status:** COMPLETE
**Tier:** 2-3 (Structural/Speculative)
**Motivation:** B is self-sufficient for execution, so what is A for?
**Verdict:** INCONCLUSIVE - No hypothesis validated

---

## Problem Statement

We have detailed structural knowledge of Currier A but no functional interpretation that makes sense given B's self-sufficiency:

- B folios have complete vocabulary (C531)
- B grammar is universal across all 83 folios (C124)
- B can execute without A input
- RI is invisible to B pipeline: 90.1% recovery without RI (C718)
- RI is independent of PP: 0/6 binding tests pass (C719)

Yet A has elaborate structure (RI linkers, paragraph organization, positional preferences) that seems too complex for mere logging or historical accident.

**Core question:** What functional role does A serve?

---

## Hypotheses Tested

### H4b: Selection Interface
**Status:** FALSIFIED

A might be the selection interface for B procedures.

**Test Result:** A only covers 30.2% of B vocabulary types (but 93% of B tokens by frequency). The coverage is too incomplete for meaningful selection filtering.

### H5: Vocabulary Evolution Log
**Status:** PARTIALLY SUPPORTED

A might be a chronological log of vocabulary development.

**Test Result:** Early folios have 87.6% shared rate vs late folios 83.6% (p=0.0039). Temporal pattern exists but doesn't explain RI structure.

### H6: A-B Positional Overlap
**Status:** NEUTRAL

A vocabulary might concentrate in specific B MIDDLE positions.

**Test Result:** Coverage uniform across positions (~44-47% types, 93-94% tokens). No positional specialization.

### H7: Quire Organization
**Status:** WEAK/NEUTRAL

A might be organized by physical manuscript structure (quires = work sessions).

**Test Result:** RI Jaccard within-quire (1.08x cross-quire, p=0.57). No significant quire clustering.

### H8: Brunschwig Preparation-Execution Flow
**Status:** NOT SUPPORTED

RI might encode preparation-phase distinctions, PP might encode execution-phase operations (per Brunschwig's process flow).

**Test Results:**
1. **Linker destination flow (Test 5):** Source RI ratio 7.4%, Destination RI ratio 10.7%. Both are PP-dominated (>90% PP). No directional flow from RI-rich to PP-rich contexts. Result: NEUTRAL.

2. **WITH-RI/WITHOUT-RI profiles (Test 6):** Execution prefix enrichment identical (20.2% vs 20.3%, p=0.9918). No differentiation. WITHOUT-RI paragraphs quickly return to WITH-RI (77.8%). Result: NEUTRAL.

---

## Prior RI Research Reviewed

### RI_AZC_LINKING_INVESTIGATION
- Vocabulary clustering hypothesis: **FALSIFIED**

### RI_BINDING_ANALYSIS
- 0/6 binding tests pass
- RI is independent of PP

### RI_FUNCTIONAL_IDENTITY
- RI invisible to B pipeline (90.1% recovery without RI)
- 87.3% of RI are singletons

### BRUNSCHWIG_PP_RI_TEST
- PP = procedural affordances, RI = material identity hypothesis
- 0/7 tests support, 7/7 inconclusive

---

## Summary of Findings

| Hypothesis | Test | Result |
|------------|------|--------|
| Selection Interface | Coverage | FALSIFIED (30% type coverage) |
| Vocabulary Evolution | Temporal pattern | PARTIALLY SUPPORTED (p=0.0039) |
| Positional Overlap | B MIDDLE positions | NEUTRAL (uniform) |
| Quire Organization | RI clustering | WEAK (1.08x, p=0.57) |
| Prep-Execution Flow | Linker destinations | NEUTRAL (no directional flow) |
| Prep-Execution Flow | WITH/WITHOUT-RI profiles | NEUTRAL (p=0.9918) |

---

## Key Quantitative Findings

- **RI vocabulary:** 60.1% of A MIDDLEs never appear in B
- **PP vocabulary:** 39.9% of A MIDDLEs shared with B
- **Type coverage:** A covers 30.2% of B vocabulary types
- **Token coverage:** A vocabulary appears in 93% of B tokens (high-frequency overlap)
- **RI singletons:** 87.3% appear only once in A
- **Linker contexts:** Both source (7.4% RI) and destination (10.7% RI) are PP-dominated
- **Execution prefixes:** Identical in WITH-RI (20.2%) and WITHOUT-RI (20.3%) paragraphs

---

## What We Know About A's Structure

From constraints and testing:

1. **Paragraph structure (C881):** RI concentrates in first lines (3.84x baseline) - "header zone"
2. **Sequential flow (C887):** WITH-RI paragraphs followed by WITHOUT-RI reference prior materials
3. **Linkers (C835):** 4 linkers (cthody, ctho, ctheody, qokoiiin) connect PP-heavy contexts
4. **ct-prefix (C889):** Marks specialized registry function (98-100% on h/hy/ho MIDDLEs)
5. **Section differences (C888):**
   - Section H: 48.7% WITHOUT-RI, ct-enriched (3.87x)
   - Section P: 20.8% WITHOUT-RI, qo/ok/ol-enriched

---

## Remaining Questions

1. **Why does RI exist at all?** It doesn't affect B execution, doesn't cluster meaningfully, doesn't map to Brunschwig dimensions.

2. **What distinguishes RI from PP functionally?** Morphologically they're identical; the only difference is B-occurrence.

3. **Is A contemporaneous with B or a later addition?** The elaborate structure suggests intentionality, but no functional role is evident.

4. **Could A be a different document type entirely?** (Index? Glossary? Planning notes? Teaching material?)

---

## Files

```
phases/A_PURPOSE_INVESTIGATION/
├── README.md
├── scripts/
│   ├── 01_selection_interface_viability.py
│   ├── 02_vocabulary_evolution_pattern.py
│   ├── 03_a_b_positional_overlap.py
│   ├── 04_a_quire_organization.py
│   ├── 05_linker_destination_flow.py
│   └── 06_withri_withoutri_profiles.py
└── results/
    ├── selection_interface_viability.json
    ├── vocabulary_evolution_pattern.json
    ├── a_b_positional_overlap.json
    ├── a_quire_organization.json
    ├── linker_destination_flow.json
    └── withri_withoutri_profiles.json
```

---

## Constraints Referenced

| Constraint | Relevance |
|------------|-----------|
| C498 | 60.1% RI, 39.9% shared vocabulary |
| C531 | B folios have unique vocabulary |
| C689 | 97.6% of A records produce unique filter fingerprints |
| C718 | 90.1% B class survival recoverable without RI |
| C719 | 0/6 RI-PP binding tests pass |
| C824 | 81.3% A-record filtering rate |
| C831 | Three-tier RI structure (95.3% singletons) |
| C835 | 4 linkers identified |
| C887 | WITHOUT-RI backward reference pattern |
| C888 | Section-specific WITHOUT-RI rates |
| C889 | ct-ho reserved PP vocabulary |
| C124 | B grammar universal |
