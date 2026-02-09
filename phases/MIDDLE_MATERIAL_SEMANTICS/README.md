# Phase: MIDDLE_MATERIAL_SEMANTICS

**Status**: COMPLETE
**Verdict**: WEAK — Phase-position semantics confirmed; material-level identity NOT supported
**Tests**: 14 completed (4 SUPPORTED, 3 PARTIAL/WEAK, 6 NOT SUPPORTED, 1 ELABORATION)

## Research Question

Do tail MIDDLEs (rare, <15 folios) encode material-specific identity? If so, where in the distributional structure does material semantics live?

**Motivation**: Analysis of f78r revealed phase-exclusive vocabulary, rare/unique MIDDLEs concentrated at line-final positions, and a procedural structure (SETUP → PROCESS → FINISH) that seemed to require material specification for complex multi-material procedures like soap making.

## Results Summary

### Core Distributional Tests (1-6)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 1 | Phase-Position Exclusivity | **SUPPORTED** | Rare 55.1% vs common 25.5% zone-exclusive, d=0.67 |
| 2 | Section Clustering | **SUPPORTED** | Concentration 0.654 vs 0.438, p≈0 |
| 3 | Line-Final Distinctiveness | **SUPPORTED** | Mean folio-count 57 vs 63, OR=1.83 |
| 4 | BIO Folio Sharing | NOT SUPPORTED | Silhouette=0.035, no meaningful clusters |
| 5 | Section Tail Vocabulary | **SUPPORTED** | 48.5% section-exclusive, ratio=1.40 |
| 6 | Line-Final Material Slot | NOT SUPPORTED | Suffix confound explains enrichment |

### Confound Controls (7-9)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 7 | Compound Atom Sharing | NOT SUPPORTED | Spearman r=0.119, below 0.2 threshold |
| 8 | Null Permutation | NOT SUPPORTED | p=0.275, not significant vs random |
| 9 | Material Slot Count | NOT SUPPORTED | Mean=1.01 slots, 52% folios have 0 |

### Discrimination Tests (10-14) — Critical

| # | Test | Verdict | Implication |
|---|------|---------|-------------|
| 10 | C619 Phase-Level Retest | NOT SUPPORTED | C619 holds — unique MIDDLEs behave identically within phases |
| 11 | Frequency-Controlled | PARTIAL | Signal at MW (p=0.009) but not permutation (p=0.144) |
| 12 | FL State vs Material | **MATERIAL** | Finish-exclusive NOT FL-enriched (p=0.224) |
| 13 | Cross-Folio Consistency | WEAK | rho=0.123, below 0.2 threshold |
| 14 | Compositional Distance | **ELABORATION** | 89.4% are distance-1 from common MIDDLEs |

## Key Findings

### 1. Phase-Position Semantics is REAL (Constraint-Worthy)
Rare MIDDLEs are significantly more zone-exclusive than common MIDDLEs (55.1% vs 25.5%, d=0.67). This is a genuine structural feature, not an artifact of rarity. Different procedural phases use different operational variants.

### 2. Material-Level Identity is NOT Supported
The discrimination tests (weighted most heavily) consistently favor the operational interpretation:
- **C619 holds within phases** (Test 10): If rare MIDDLEs encoded different materials, they should show different behavioral profiles. They don't.
- **89.4% are compositional elaborations** (Test 14): Zone-exclusive rare MIDDLEs are single-character insertions/substitutions from common MIDDLEs, not independent identifiers.
- **No cross-folio material consistency** (Tests 4, 7, 13): If MIDDLEs encoded materials, folios performing similar procedures should share rare vocabulary. They don't cluster.

### 3. FL State Marking Ruled Out (Test 12)
Finish-zone exclusive MIDDLEs are NOT enriched for FL-characteristic characters (p=0.224). This rules out one specific operational explanation (C777 FL state index). The phase-exclusivity has a procedural explanation that goes beyond state indexing.

### 4. Section-Specific Tail Vocabulary (Constraint-Worthy)
Each section maintains distinct tail vocabulary (42-66% section-exclusive, Section S highest at 65.9%). This extends C675 (MIDDLE positional invariance) — while common MIDDLEs show minimal positional drift, rare/tail MIDDLEs are section-structured.

### 5. Line-Final Rarity Explained by Morphology
Line-final position IS enriched for rare MIDDLEs (OR=1.83), but this is explained by suffix morphology (C539), not a dedicated "material slot." The suffix system, not semantic encoding, drives line-final rarity.

## Semantic Ceiling Impact

**C120 STANDS with refinement.** Tail MIDDLEs show phase-position specificity but are compositional variants of common operational MIDDLEs, not independent material identifiers. Material encoding, if present, does NOT live in MIDDLE morphology.

Where materials might be encoded (outside this phase's scope):
- Contextual patterns (which MIDDLEs co-occur)
- Illustrations (visual reference)
- External knowledge the reader brings
- Prefix+MIDDLE combinations (untested)

## Candidate Constraints

| Finding | Constraint | Tier |
|---------|-----------|------|
| Rare MIDDLE zone-exclusivity (55.1% vs 25.5%, d=0.67) | **C937** | 2 |
| Section-specific tail vocabulary (42-66% exclusive, concentration 0.654 vs 0.438) | **C938** | 2 |
| Zone-exclusive MIDDLEs are compositional variants (89.4% dist-1) | **C939** | 2 |
| FL state marking via rare MIDDLEs FALSIFIED (p=0.224) | **C940** | 1 |
| C619 confirmed within procedural phases | Revision note on C619 | — |

## Pre-Registered Alternative Evaluations

| Alternative | Status | Evidence |
|---|---|---|
| A. Operational phase-specificity | **CONFIRMED** | Tests 10, 14 |
| B. FL state markers | **RULED OUT** | Test 12 |
| C. Compositional artifact | **PARTIALLY CONFIRMED** | Test 14 |
| D. Folio identity vocabulary | NOT SUPPORTED | Tests 4, 7 |

## Scripts

```
scripts/
├── 01_phase_exclusivity_corpus.py
├── 02_rare_middle_section_clustering.py
├── 03_line_final_distinctiveness.py
├── 04_bio_folio_middle_sharing.py
├── 05_section_tail_vocabulary.py
├── 06_line_final_material_slot.py
├── 07_compound_atom_sharing.py
├── 08_null_permutation_test.py
├── 09_material_slot_count.py
├── 10_c619_phase_level_retest.py
├── 11_frequency_controlled_exclusivity.py
├── 12_fl_state_vs_material_discriminator.py
├── 13_cross_folio_material_consistency.py
└── 14_compositional_distance.py
```

## Provenance

- **Trigger**: Russian YouTuber "Voynich Engineer" (Artem) claimed material-specific translations of f78r
- **Observation**: f78r shows phase-exclusive vocabulary and line-final rare MIDDLE concentration
- **Hypothesis**: Tail MIDDLEs may encode material-level semantics within the operational grammar
- **Expert consultation**: Expert-advisor recommended Tests 10-14 as discrimination tests (bias toward operational noted)
- **Result**: Phase-position structure confirmed (structural finding). Material identity not supported (semantic ceiling holds).
