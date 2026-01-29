# UNIQUE_VOCABULARY_ROLE

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C618-C621

## Purpose

Determine WHY 98.8% of B folios need private vocabulary (C531). Three hypotheses tested: H1 (lexical tail — unique MIDDLEs are rare hapax, behaviorally interchangeable), H2 (parametric specialization — unique MIDDLEs carry folio-specific parameters), H3 (functional specialization — unique MIDDLEs enable distinct behavior).

**Verdict: H1 confirmed.** Unique MIDDLEs are the extreme morphological tail of the UN population — 100% unclassified, 99.7% hapax, structurally dispensable.

## Scripts

| Script | Purpose |
|--------|---------|
| `unique_middle_characterization.py` | ICC role distribution, UN overlap, morphological profile, line position |
| `unique_vocabulary_behavior.py` | UN-internal transition divergence, context signatures, folio coupling, section/REGIME concentration |
| `folio_vocabulary_network.py` | Section-controlled adjacency, similarity clustering, vocabulary gradient, removal impact |

## Key Findings

### 1. Unique MIDDLEs = Extreme UN Tail (C618)

858 unique MIDDLEs (64% of B MIDDLE types) are:
- 100% UN tokens (zero classified)
- 99.7% hapax (862/865 word types appear once)
- MIDDLE length 4.55 (vs 2.12 shared), word length 7.58 (vs 5.06)
- 83.1% suffix rate (vs 49.2%), 88% B-exclusive
- 95.7% contain PP atoms as substrings

### 2. Behavioral Equivalence (C619)

Within UN, unique vs shared MIDDLE tokens have near-identical transitions:
- Successor: V=0.070 (negligible)
- Predecessor: V=0.051 (negligible)
- Main difference: unique MIDDLE tokens cluster with other UN (54.6% UN-neighbor rate vs 47.5%)
- Unique density is essentially UN proportion (rho=+0.740***)
- Section-dependent (H=20.50, p=0.000134), NOT REGIME-dependent (p=0.243)

### 3. Section-Driven Vocabulary Network (C620)

- k=2 silhouette=0.055: section H vs everything else
- ARI with section: 0.497 (strong); ARI with REGIME: 0.022 (none)
- C533 adjacency effect (1.30x class overlap) reduces to 1.057x after section control
- No manuscript gradient in unique density (rho=-0.047, p=0.676)

### 4. Structurally Dispensable Vocabulary (C621)

Removing all 868 unique MIDDLE tokens:
- 96.2% token survival (22,228/23,096)
- Mean role shift 2.80 pp, max 7.04 pp
- Only UN decreases (-2.71 pp)
- 1/82 folios loses ICC role coverage

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C618 | Unique MIDDLE Identity | 100% UN, 99.7% hapax, MIDDLE length 4.55 vs 2.12, 95.7% PP atom containment |
| C619 | Unique MIDDLE Behavioral Equivalence | Transitions V=0.070/0.051; unique density = UN proportion rho=+0.740***; H1 confirmed |
| C620 | Folio Vocabulary Network | ARI_section=0.497, ARI_REGIME=0.022; adjacency 1.057x after section control |
| C621 | Vocabulary Removal Impact | 96.2% survival, <3 pp role shift, 1/82 loses ICC role |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
| middle_classes.json | A_INTERNAL_STRATIFICATION |
| voynich.py | scripts/ |

## Verification

- Unique MIDDLE types: 858 (matches C531)
- Folios with unique MIDDLEs: 81 (matches C531)
- B-exclusive fraction: 88.0% (matches C532)
- Total B folios: 82
- Total B tokens: 23,096
- UN tokens: 7,042
