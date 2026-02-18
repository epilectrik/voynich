# C1113: P-Text and Rosettes Share a Unified Bridge-Vocabulary Indexing System

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** PTEXT_ROSETTES_INDEXING_ARCHITECTURE (Phase 395)
**Strengthens:** C1096 (Rosettes bridge enrichment), C1109 (vocabulary-mediated cross-reference), C1014 (bridge MIDDLEs)
**Extends:** C486 (P-text B-transmission), C758 (P-text identity)

---

## Statement

P-text (on AZC folios) and Rosettes labels share a unified bridge-vocabulary indexing system that cross-references B paragraphs. This is supported by three converging lines of evidence:

1. **Vocabulary overlap (I1 PASS):** P-text and Rosettes labels share 72 MIDDLEs (Jaccard = 0.210), far above the random A baseline (bootstrap p95 = 0.070, p = 0.0000). This overlap is not explainable by chance vocabulary sharing.

2. **Paragraph convergence (I3 PASS):** P-text and Rosettes MIDDLEs converge on the SAME B paragraphs. Spearman rho = 0.642 (p ~ 10^-70) between paragraph-level P-text overlap and Rosettes overlap. When a paragraph is rich in P-text vocabulary, it is also rich in Rosettes vocabulary.

3. **Affordance signature match (I4 PASS):** The unified index vocabulary (P-text + Rosettes labels, 343 MIDDLEs) has an affordance bin profile that matches B paragraph header MIDDLEs with cosine = 0.949. The indexing vocabulary and the paragraph entry points share nearly identical functional composition.

Overall synthesis: **UNIFIED_INDEXING**.

---

## Evidence

### I1: Vocabulary Overlap (PASS)
| Metric | Value |
|--------|-------|
| Observed Jaccard | 0.2099 |
| Intersection size | 72 MIDDLEs |
| Bootstrap p95 | 0.0696 |
| Bootstrap mean | 0.0522 |
| p-value | 0.0000 |

### I2: Cross-Reference Target Convergence (FAIL)
| Metric | Value |
|--------|-------|
| Target folio mean fraction | 0.423 |
| Non-target mean fraction | 0.532 |
| p-value | 0.993 (wrong direction) |

P-text MIDDLEs do NOT preferentially concentrate on Phase 393 cross-reference target folios. The indexing system does not operate at the folio level — it operates at the paragraph level (I3).

### I3: Paragraph-Level Convergence (PASS)
| Metric | Value |
|--------|-------|
| Paragraphs tested | 591 |
| Spearman rho | 0.642 |
| p-value | 4.3 x 10^-70 |

This is the strongest statistical signal in the test battery. P-text and Rosettes vocabularies are paragraph-aligned, not folio-aligned.

### I4: Unified Affordance Signature (PASS)
| Metric | Value |
|--------|-------|
| Unified index size | 343 MIDDLEs |
| Header MIDDLEs | 746 |
| Cosine similarity | 0.9488 |

### I5: B-Paragraph Bridge Anatomy (FAIL)
| Metric | Value |
|--------|-------|
| Header mean bridge fraction | 0.769 |
| Body mean bridge fraction | 0.838 |
| p-value | 1.000 (wrong direction) |

Bridge MIDDLEs are slightly MORE concentrated in paragraph bodies than headers. This falsifies the prediction that bridges concentrate at paragraph entry points. Instead, bridge MIDDLEs are ubiquitous throughout paragraphs — the indexing operates through vocabulary presence, not positional enrichment.

---

## Interpretation

The manuscript has a three-layer indexing architecture:

1. **P-text** (on AZC folios): Bridge-enriched at 45.5%, the most concentrated bridge vocabulary in the manuscript. Located alongside zodiac diagrams.

2. **Rosettes labels** (on the Rosettes foldout): Bridge-enriched at 24.4% (C1096). Contains the same vocabulary as P-text (72 shared MIDDLEs).

3. **B paragraph vocabulary**: The target of the index. Both P-text and Rosettes MIDDLEs converge on the same paragraphs (rho = 0.642), and the unified index matches paragraph header affordance profiles (cosine = 0.949).

The I2 FAIL and I5 FAIL narrow the indexing mechanism:
- **Not folio-level**: The index does not point to specific folios (I2 FAIL)
- **Not header-positional**: Bridge MIDDLEs do not concentrate at paragraph entry points (I5 FAIL)
- **Vocabulary-mediated**: The index works through shared MIDDLE vocabulary, present throughout paragraphs

This is consistent with C1109 (vocabulary-mediated, not process-demonstrating) but extends it: the vocabulary mediation is not just Rosettes-to-B, but a unified P-text + Rosettes system.

---

## Constraint Implications

- **C1109 extended**: The vocabulary-mediated cross-reference is not Rosettes-specific — it is part of a unified P-text + Rosettes indexing system
- **C486 explained**: P-text's 76.7% B-transmission is a direct consequence of its extreme bridge enrichment (45.5% bridge MIDDLEs, which transmit at 100%)
- **C1096 contextualized**: Rosettes bridge enrichment (3.46x) is the same phenomenon as P-text bridge enrichment — both are components of the indexing layer

---

## Provenance

- Phase: 395 (PTEXT_ROSETTES_INDEXING_ARCHITECTURE), 10-test battery
- Script: `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/scripts/ptext_rosettes_indexing.py`
- Results: `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/results/ptext_rosettes_indexing.json`
- Related: C486, C758, C900, C1014, C1096, C1109, C1112
