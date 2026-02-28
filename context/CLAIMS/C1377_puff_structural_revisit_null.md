# C1377: Puff-Voynich Structural Revisit (NULL)

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** 490 (PUFF_VOYNICH_STRUCTURAL_REVISIT)
**Depends on:** C1250, C1247, C1248, C1249
**Cross-ref:** Puff von Schrick, *Büchlein von den ausgebrannten Wässern* (~1455)

## Statement

Voynich Currier B herbal folios do NOT differentiate by plant material type (ROOT, FLOWER, HERB) in either 8-category operational profiles (C1250) or 5-apparatus profiles (C1247-C1249). Using blind PPC morphological classification of 21 folios into 3 groups (8 ROOT, 7 FLOWER, 6 HERB), pre-registered before testing:

- **Test D (categories):** Pseudo-F = 0.90, eta² = 0.091, p = 0.51. No category reaches individual significance. NULL.
- **Test A (apparatus):** Pseudo-F = 1.62, eta² = 0.153, p = 0.15. No apparatus profile reaches individual significance. NULL.
- **Test B (triangulation):** SKIPPED (requires D + A signal).

The early evidential ceiling (v2.20-2.62) is confirmed with modern structural tools. Puff's material categories do not predict Voynich folio structural profiles. The Puff connection remains suggestive at the coarse distributional level but is not structurally diagnostic.

## Key Findings

### Test D: 8-Category Profiles — NULL
- Multivariate pseudo-F = 0.90 (p = 0.51, 10,000 permutations)
- eta² = 0.091 (well below 0.25 threshold)
- Strongest individual category: CONTAINMENT (H = 3.81, p = 0.15)
- Pre-registered directional predictions: 3/4 hit but with noise-level effect sizes
- ROOT, FLOWER, HERB groups have nearly identical category distributions

### Test A: 5-Apparatus Profiles — NULL
- Multivariate pseudo-F = 1.62 (p = 0.15, 10,000 permutations)
- eta² = 0.153 (below 0.25 threshold)
- Strongest individual apparatus: SUSTAINED_HEAT (H = 4.35, p = 0.11)
- Pre-registered directional predictions: 1/5 hit
- FLOWER folios do NOT have elevated DISTILLATION (opposite of prediction)

### Test B: Triangulation — SKIPPED
- Conditional test: Only runs if both D and A show signal
- Both D and A are NULL → B was not computed

## Interpretation

The Voynich manuscript's operational grammar does not encode plant material type at the folio level. A folio processing a root looks structurally identical to one processing a flower — the same categories, the same apparatus profiles, the same REGIME distribution. This is consistent with C458 (hazard clamping): the grammar deliberately equalizes structural properties across folios, making material-type discrimination impossible from grammar alone.

This does NOT mean the Puff connection is wrong at all levels. Puff's organizational structure (material-first) may correspond to Voynich's organizational structure at a level our grammar cannot resolve — e.g., the specific MIDDLE sequences may encode material identity while the statistical profiles (categories, apparatus) reflect processing structure that is material-independent.

## Evidence

- Script: `phases/PUFF_VOYNICH_STRUCTURAL_REVISIT/scripts/puff_voynich_structural_revisit.py`
- Results: `phases/PUFF_VOYNICH_STRUCTURAL_REVISIT/results/puff_voynich_structural_revisit.json`
- Pre-registered assignments: `phases/PUFF_VOYNICH_STRUCTURAL_REVISIT/results/pre_registered_assignments.json`
- 21 folios (8 ROOT, 7 FLOWER, 6 HERB), 10,000 permutations, Bonferroni threshold p < 0.0033
- Assignments from PPC blind morphological classification (independent of structural data)

## Falsification Conditions

This constraint would be revised if:
1. A larger sample (including non-herbal Currier B folios or Currier A) shows material-type differentiation
2. A finer-grained material classification (e.g., AROMATIC cross-cut) reveals hidden structure
3. Paragraph-level analysis (rather than folio-level) shows material-type effects
4. MIDDLE-level analysis (specific MIDDLE sequences, not aggregate profiles) reveals material encoding
