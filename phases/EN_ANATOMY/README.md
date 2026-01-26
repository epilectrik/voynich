# EN_ANATOMY Phase

**Goal:** Characterize the internal structure of the ENERGY (EN) role — the largest operational role in Currier B.

**Status:** COMPLETE

## Key Findings

### Census Resolution (C573)
- **18 EN classes** (ICC-based): {8, 31-37, 39, 41-49}
- BCSC said 11: UNDERCOUNTED. CSV said 6: UNDERCOUNTED. ICC=18 is correct.
- 7,211 tokens = 31.2% of Currier B
- Core 6 classes = 79.5% of EN; Minor 12 = 20.5%

### Structural Verdict: Distributional Convergence (C574)
- k=2 silhouette: **0.180** — QO and CHSH occupy identical positions, REGIME, context
- J-S divergence: 0.0024 (near-identical transition profiles)
- But **vocabulary divergence**: MIDDLE Jaccard=0.133 (87% non-overlapping)
- And **trigger divergence**: chi2=134, p<0.001
- Grammatically equivalent, lexically and contextually partitioned
- Instantiates C276/C423 (PREFIX-MIDDLE binding) within a single role

### Pipeline Purity (C575)
- **100% PP MIDDLEs** — zero RI, zero B-exclusive
- Even purer than AX (98.2% PP)
- EN vocabulary entirely inherited from Currier A

### MIDDLE Bifurcation (C576)
- QO uses 25 MIDDLEs, CHSH uses 43, only 8 shared (Jaccard=0.133)
- PREFIX gates which MIDDLE subvocabulary is accessible (C276, C423)
- 30 EN-exclusive MIDDLEs (46.9%) not shared with any other role

### Interleaving Mechanism (C577)
- NOT positional (p=0.104 — same positions)
- Content-driven: BIO 58.5%, PHARMA 27.5%
- PHARMA collapse confirms C555 (Class 33 depleted)
- REGIME_4 lower interleaving (52.2% vs ~58%)

### Context Differentiation (C579, C580)
- CHSH-first ordering bias: 53.9% (p=0.010)
- Trigger profiles differ: CHSH from AX/CC context, QO from EN-self/boundary

## Interpretation

EN exhibits **distributional convergence with lexical partitioning**. The two prefix families (QO and CHSH) occupy the same grammatical positions, follow the same REGIME patterns, and produce near-identical transition profiles. But they carry different MIDDLE subvocabularies (87% non-overlapping) and enter through different contextual pathways (CHSH from AX/CC, QO from EN-self/boundary).

This is PREFIX-MIDDLE binding (C276, C423) operating within a single execution role: PREFIX gates which subset of pipeline-derived materials is accessible. The material discrimination remains in the MIDDLE (C293); PREFIX determines which materials are available for a given energy operation. Two entry points into the same distributional behavior, carrying different tools.

Section-dependent selection (PHARMA suppresses QO, enriches CHSH) reflects the content requirements of different procedural types — different sections need different material subsets.

## New Constraints

| # | Name | Key Finding |
|---|------|-------------|
| C573 | EN Definitive Count | 18 classes, 31.2% of B |
| C574 | EN Distributional Convergence | Silhouette 0.180; convergent position/REGIME, divergent vocabulary/triggers |
| C575 | EN 100% Pipeline-Derived | 64 PP MIDDLEs, 0 RI, 0 B-exclusive |
| C576 | MIDDLE Vocabulary Bifurcation | QO:25, CHSH:43, Jaccard=0.133 |
| C577 | Interleaving Content-Driven | Same positions, different section rates |
| C578 | 30 Exclusive MIDDLEs | 46.9% EN-only vocabulary |
| C579 | CHSH-First Ordering | 53.9%, p=0.010 |
| C580 | Trigger Profile Differentiation | chi2=134, p<0.001 |

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| en_census_and_inventory.py | Census reconciliation, MIDDLE inventory | en_census.json |
| en_feature_matrix.py | Per-class distributional profiles | en_features.json |
| en_subfamily_test.py | Clustering, KW, J-S divergence tests | en_subfamily_test.json |
| en_interleaving_anatomy.py | Interleaving mechanism analysis | en_interleaving.json |
| en_synthesis.py | Unified synthesis and constraint enumeration | en_synthesis.json |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| middle_classes.json | A_INTERNAL_STRATIFICATION |
| ax_census.json | AUXILIARY_STRATIFICATION |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
