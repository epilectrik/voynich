# CURRIER_A_STRUCTURE_V2 Phase

## Objective

Move from "descriptive statistics" to "explanatory model" for Currier A structure.

## Background

Previous work (C848, C850, C881) characterized A's statistical distributions but not its generative logic. Key unexplained phenomena:

| Gap | Numbers | Question |
|-----|---------|----------|
| No initial RI | 53% of paragraphs | Why? Continuations? Different record type? |
| Paragraph size variance | 2-12 lines | What determines short vs long? |
| Middle-line RI | Present but unexplained | Same function as initial RI? |
| 5 cluster types | 34% short RI-heavy, 8% long linker-rich, 58% standard | What produces this? |
| Linker sparsity | Only 4 of 609 RI | Why these 4? Why ct-prefix? |

## Tests

### Test 1: Folio Position vs Cluster Type (MOST DISCRIMINATING)
Does paragraph ordinal position (first/middle/last in folio) predict cluster membership?
- If YES → structural organization (position matters)
- If NO → content-driven variance (material determines structure)

### Test 2: PP Composition in Non-RI First Lines
Do first lines WITH initial RI have different PP profiles than first lines WITHOUT?
- Tests whether there are two types of paragraph openings

### Test 3: Middle-RI Morphology
Compare PREFIX profiles of initial-RI vs middle-RI vs final-RI.
- Different morphology → different functions

### Test 4: Linker Target Characterization
Are collector folios (f93v, f32r) structurally distinct?
- Broader PP pools? Different cluster distribution?

### Test 5: Sequential Coherence Within Paragraph Types
Do different paragraph types have different internal coherence patterns?
- Tests if cluster types reflect functional differences

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_position_vs_cluster.py | Test 1 | position_cluster_analysis.json |
| 02_pp_composition.py | Test 2 | pp_composition_analysis.json |
| 03_ri_morphology.py | Test 3 | ri_morphology_analysis.json |
| 04_linker_targets.py | Test 4 | linker_target_analysis.json |
| 05_sequential_coherence.py | Test 5 | sequential_coherence_analysis.json |

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | Position predicts cluster type (chi2 p<0.01) + explains 2+ gaps |
| MODERATE | 1 discriminating factor found, explains 1 gap |
| WEAK | No clear discriminators, gaps remain statistical |

## Depends On

- C848: A paragraph structure
- C850: RI token behavior
- C881: A record paragraph structure
- RecordAnalyzer from scripts/voynich.py
