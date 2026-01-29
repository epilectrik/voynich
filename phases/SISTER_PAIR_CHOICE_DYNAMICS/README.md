# SISTER_PAIR_CHOICE_DYNAMICS

**Phase status:** COMPLETE | **Constraints:** C637-C639 | **Date:** 2026-01-26

## Objective

Determine what governs sister pair choice (ch vs sh preference) beyond section membership. Decompose folio-level ch_preference variance into MIDDLE composition, quire membership, REGIME, section, and lane balance contributions, identifying how much remains as folio-level "free choice."

## Key Findings

1. **MIDDLE composition explains 22.9% of ch_preference variance** (C637). 77 B MIDDLEs meet threshold; 8 are >90% ch-preferring, 0 >90% sh-preferring. B is less differentiated than A (0.140 vs 0.254 mean deviation). Cross-system A-B MIDDLE preferences correlate (rho=0.440, p=0.003).

2. **Quire predicts ch_preference but is CONFOUNDED with section** (C638). Quire KW H=32.002 (p=0.0001, eta_sq=0.329) but Cramer's V=0.875 with section. Within section H, quire is not significant (p=0.665). ICC(1,1)=0.362 (FAIR) reflects section, not independent quire clustering.

3. **52.9% of ch_preference is free choice** (C639). Hierarchical regression with all 5 predictor groups explains 47.1% total (adj R2=32.3%). Shared variance dominates (36.4%); unique contributions are small: quire 3.8%, lane balance 2.7%, MIDDLE comp 2.6%, REGIME 1.2%, section 0.4%. Residuals are clean (no autocorrelation, no size effects).

## Verdict

Sister pair choice is a **majority free-choice variable**: section sets a baseline, but each folio independently determines over half of its ch/sh preference. The tight coupling between predictors (36.4% shared variance) means no single factor "owns" the choice -- section, REGIME, composition, and MIDDLE identity all capture overlapping aspects of the same underlying folio structure.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `middle_sister_preference.py` | Per-MIDDLE ch/sh ratios, folio composition score, A vs B comparison, ok/ot analysis | `results/middle_sister_preference.json` |
| `quire_sister_consistency.py` | Quire mapping, descriptive stats, KW tests, ICC(1,1), quire-section confound | `results/quire_sister_consistency.json` |
| `choice_variance_decomposition.py` | Predictor battery, hierarchical regression, semipartial correlations, residual analysis | `results/choice_variance_decomposition.json` |

## Data Dependencies

- `scripts/voynich.py`
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json`
- `data/transcriptions/interlinear_full_words.txt` (quire column)
