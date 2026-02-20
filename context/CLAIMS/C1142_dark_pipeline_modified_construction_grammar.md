# C1142: Dark Pipeline Uses Modified Construction Grammar

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphological construction
**Phase:** 408 (PP_PIPELINE_ATOM_DECOMPOSITION)

## Finding

Dark-pipeline compounds follow a **modified** version of B's general atom ordering grammar (C1065), with 50% agreement on directional pairs but preserved gateway/terminal positioning.

### C1065 Comparison

| Metric | Value |
|--------|-------|
| C1065 asymmetric pairs tested | 14 (of 20; 6 not found in dark pipeline) |
| Matches (same direction) | 7 |
| Mismatches (opposite direction) | 7 |
| Agreement rate | 50.0% |

### Gateway/Terminal Positioning

| Atom Type | Mean Position | C1060 Expectation |
|-----------|--------------|-------------------|
| Gateway (opch, eol, op) | 0.083 | INITIAL (< 0.15) |
| Terminal (ai, kc, ed, eod) | 0.352 | FINAL (> 0.40) |
| Preserved? | **Yes** | |

Gateway atoms still appear near the beginning of compounds and terminal atoms near the end, consistent with C1060. The positional framework is shared; the specific pair orderings diverge.

### Atom Pool Comparison

| Pool | Atom Count | Jaccard with Dark |
|------|-----------|-------------------|
| Grammar compounds (matched PP) | 27 | 0.481 |
| Dark-pipeline compounds | 50 | 1.000 |
| All B compounds | 57 | 0.877 |

25 atoms are shared between grammar and dark-pipeline compounds. 25 atoms are dark-exclusive (not found in grammar compounds but mostly found in all-B). 2 atoms are grammar-exclusive.

### Dark-Pipeline Bigram Statistics

| Metric | Value |
|--------|-------|
| Compounds with 2+ atoms | 77 |
| Bigram types | 67 |
| Bigram tokens | 87 |
| Asymmetric pairs (>80%, n>=3) | 4 |

## Evidence

- Phase 408, Test 3 (atom pool overlap) and Test 5 (construction grammar comparison)
- Bigram extraction via `middle.find()` position sorting, same method as C1065

## Implication

The dark pipeline uses a **variant dialect** of B's general construction grammar. The positional framework is preserved (gateway atoms lead, terminal atoms trail), but the specific sequencing rules for atom pairs diverge in half the cases. The dark pipeline also uses a larger atom vocabulary (50 vs 27 for grammar compounds), including 25 dark-exclusive atoms that extend the construction alphabet. This is consistent with the dark pipeline serving a different functional purpose (identification vs execution) while sharing the same morphological infrastructure.

Section concentration (C1135 Herf 0.716) is NOT atom-driven (Phase 408 Test 4: permutation p = 0.303). The same atoms appear across sections; section specificity arises from how atoms are combined into compounds and how those compounds are frequency-modulated (C1134), not from which atoms are selected.

## Provenance

- Source: Phase 408, Tests 3 + 5 (with Test 4 null result)
- Related: C1065 (atom bigram ordering grammar), C1060 (atom position grammar), C1066 (construction-execution independence), C1134 (frequency modulation), C1135 (section concentration)
