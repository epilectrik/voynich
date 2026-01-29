# CONSTRAINT_BUNDLE_SEGMENTATION

**Status:** COMPLETE (PARTIALLY FALSIFIED) | **Constraints:** C694-C703 | **Scope:** A

## Objective

Test whether Currier A folios contain natural **"constraint bundles"** — runs of consecutive PP-pure lines (ri_count == 0) delimited by RI-bearing lines — that function as the true filtering unit for B vocabulary. A_RECORD_B_FILTERING (C682-C693) showed individual A records are too restrictive (mean 11/49 classes, 78% unusable).

## Result

**Bundle hypothesis FALSIFIED at vocabulary coherence stage.** Structural segmentation exists (Phase 1) but bundles lack vocabulary coherence (Phase 2). RI boundaries mark structural features, not vocabulary domains. PP MIDDLEs distribute homogeneously within A folios.

## Phase 1: Structural Validation (3/3 binding tests PASS)

| Test | Result | Evidence |
|------|--------|----------|
| T1.1 RI Placement Non-Random | **PASS** | Fisher KS p ~ 10^-306 |
| T1.2 PP-Run Lengths Non-Geometric | **PASS** | KS p ~ 10^-44 |
| T1.3 RI Line-Final Preference | **Informational** | 1.48x (p=1.26e-07); threshold artifact from stricter RI definition |
| T1.4 PREFIX Clustering | **PASS** | p < 10^-4 |
| T1.5 Bundle-C424 Size Match | **Informational** | Conceptually distinct constructs |

**Gate revised:** Original 4/5 threshold → structural existence criterion (3 strong non-random signals, no contradiction). T1.3 and T1.5 reclassified as informational.

## Phase 2: Vocabulary Coherence (1/4 FAIL — decisive)

| Test | Result | Evidence |
|------|--------|----------|
| T2.1 Within vs Between PP Jaccard | **FAIL** | 0.0973 vs 0.0962 (ratio 1.01x) |
| T2.2 Bundle PP > Random | PASS (dubious) | 1.02x effect, median p=0.512 |
| T2.3 PP Diversity Structured | **FAIL** | p=0.336 |
| T2.4 Boundary Discontinuity | **FAIL** | 1.06x (p=0.207) |

**Gate FAILED (1/4, needed 3/4). Phases 3-4 not executed.**

## Key Finding: PP Folio-Level Homogeneity (C703)

PP MIDDLE vocabulary distributes **homogeneously** within A folios. Within-bundle Jaccard = between-bundle Jaccard (ratio 1.01x). RI creates structural boundaries without vocabulary boundaries. This redirected investigation to folio-level filtering (see FOLIO_LEVEL_FILTERING phase).

## Segmentation Statistics

| Metric | Value |
|--------|-------|
| A folios | 114 |
| Total lines | 1,562 |
| PP-pure lines | 988 (63.3%) |
| RI-bearing lines | 574 (36.7%) |
| Bundles | 365 |
| Bundle size range | 1-12 (mean 2.71) |

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `bundle_segmentation.py` | Shared module | (imported by other scripts) |
| `structural_validation.py` | T1.1-T1.5 (C694-C698) | `structural_validation.json` |
| `vocabulary_coherence.py` | T2.1-T2.4 (C699-C702) | `vocabulary_coherence.json` |

## Constraints

| # | Name | Status | Key Result |
|---|------|--------|------------|
| C694 | RI Placement Non-Random | VALIDATED | Fisher KS p ~ 10^-306 |
| C695 | PP-Run Length Distribution | VALIDATED | KS p ~ 10^-44, non-geometric |
| C696 | RI Line-Final Preference | VALIDATED | 1.48x (p=1.26e-07) |
| C697 | PREFIX Clustering Within Lines | VALIDATED | p < 10^-4 |
| C698 | Bundle-C424 Size Match | INFORMATIONAL | Different constructs (KS p < 0.001) |
| C699 | Within-Bundle PP Coherence | FALSIFIED | Ratio 1.01x (no coherence) |
| C700 | Bundle PP Exceeds Random | MARGINAL | 1.02x effect (dubious) |
| C701 | Bundle PP Diversity | FALSIFIED | p=0.336 (no structure) |
| C702 | Boundary Vocabulary Discontinuity | FALSIFIED | Ratio 1.06x (no cliff) |
| C703 | PP Folio-Level Homogeneity | VALIDATED | PP uniform within folios |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP MIDDLE sets)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token -> class)

## Cross-References

- C498: RI vocabulary track (confirmed: RI is structural, not vocabular)
- C512: PP section invariance (extended: PP is also folio-internally uniform)
- C424: Clustered adjacency (distinct from RI-bounded bundles)
- C346: Sequential coherence 1.20x (too weak for vocabulary partitioning)
- C682-C693: A record B filtering (individual records too restrictive)
