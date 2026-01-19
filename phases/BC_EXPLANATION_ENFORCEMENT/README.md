# BC_EXPLANATION_ENFORCEMENT Phase

**Status:** PRE-REGISTERED
**Created:** 2026-01-19
**Hypotheses:** 4 (LOCKED)

---

## Purpose

Test the **Explanation-Enforcement Complementarity** hypothesis: Does Brunschwig's pedagogical verbosity correlate inversely with AZC scaffold constraint rigidity?

> **Core question:** Where Voynich enforces more, does Brunschwig explain less?

---

## Expert Rationale

The external expert identified the **one remaining legitimate reverse-Brunschwig test**:

> "The only remaining semantic layer is **operator-experience alignment**: how Brunschwig's pedagogy modulates explanation density in response to where AZC leaves freedom vs removes it."

This tests whether Voynich and Brunschwig partition responsibility between system and human in a complementary way.

---

## Pre-Registered Hypotheses

### H1: Explanation Density Inversely Correlates with Judgment Freedom
**Prediction:** Recipes mapped to LOW judgment freedom zones (S-dominated) have LOWER explanation density than recipes mapped to HIGH freedom zones (R-dominated).
**Test:** Spearman correlation of explanation_density vs judgment_freedom_index
**Threshold:** rho < -0.3, p < 0.05

### H2: Explanation Density Inversely Correlates with Scaffold Rigidity
**Prediction:** Recipes mapped to UNIFORM scaffolds (Zodiac) have LOWER explanation density than recipes mapped to VARIED scaffolds (A/C).
**Test:** Mann-Whitney U comparing explanation density by scaffold family
**Threshold:** p < 0.05, effect size d > 0.3

### H3: Interaction Term Dominates Main Effects
**Prediction:** The freedom x pacing interaction explains more variance than either main effect alone.
**Test:** Hierarchical regression comparing models with/without interaction
**Threshold:** Interaction delta-R-squared > 0.05, p < 0.05

### H4: Complementarity Ratio
**Prediction:** Brunschwig verbosity / Voynich constraint shows consistent inverse relationship.
**Test:** Per-recipe complementarity score: explanation_density / (1 - judgment_freedom)
**Threshold:** Ratio variance < baseline expectation, chi-squared p < 0.05

---

## Explanation Density Metrics

Extract from `brunschwig_text` fields:

| Metric | Keywords/Patterns | Formula |
|--------|-------------------|---------|
| M1: Warning Density | hut, acht, gefahr, gift, pruf, vorsicht | count / total_words |
| M2: Conditional Density | wenn, aber, doch, sonst, falls, gesetzt | count / total_words |
| M3: Sensory Density | (from sensory_content) | total_matches / total_words |
| M4: Quantification Density | digits, lot, mass, tage, woch, stund | count / total_words |
| M5: Medical Outcome Density | hilft, gut, heilt, schadet, totet, giftig | count / total_words |
| M6: Aggregate | mean(M1..M5) normalized | composite |

---

## Data Sources

| File | Contents | Used By |
|------|----------|---------|
| `data/brunschwig_materials_master.json` | 197 recipes, 594 steps, brunschwig_text | bc_01 |
| `results/ats_monotonicity.json` | Per-folio scaffold pacing (rho) | bc_02 |
| `results/ts_judgment_trajectories.json` | Zone-level judgment freedom | bc_02 |
| `results/regime_folio_mapping.json` | Regime to folio linkage | bc_02 |
| `results/azc_folio_features.json` | Folio family assignment | bc_02 |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `bc_01_explanation_extraction.py` | Extract M1-M6 from brunschwig_text |
| `bc_02_regime_scaffold_mapping.py` | Map regime to scaffold pacing + freedom |
| `bc_03_freedom_correlation.py` | H1: explanation vs judgment freedom |
| `bc_04_scaffold_correlation.py` | H2: explanation vs scaffold rigidity |
| `bc_05_interaction_test.py` | H3: interaction > main effects |
| `bc_06_complementarity_ratio.py` | H4: verbosity/constraint ratio |
| `bc_07_synthesis.py` | Tier assessment |

---

## Tier Assessment

| H1 | H2 | H3 | H4 | Combined | Verdict |
|----|----|----|----| ---------|---------|
| PASS | PASS | PASS | PASS | 4/4 | **Tier 2** - Strong complementarity |
| PASS | PASS | PASS | FAIL | 3/4 | **Tier 3** - Partial complementarity |
| PASS | PASS | FAIL | FAIL | 2/4 | **Tier 4** - Weak signal |
| 1+ | - | - | - | 1/4 | **Tier 4** - Suggestive |
| FAIL | FAIL | FAIL | FAIL | 0/4 | **FALSIFIED** - No complementarity |

---

## Constraint Compliance

| Constraint | How Respected |
|------------|---------------|
| C384 | No token-to-referent mapping; aggregate pedagogical behavior only |
| C430 | Family separation (Zodiac vs A/C) maintained |
| No semantic decoding | Testing explanation DENSITY, not meaning |

---

## Expected Outcomes

**If test succeeds:**
> Voynich and Brunschwig partition responsibility between system and human in a complementary way - one enforces, the other explains.

**If test fails:**
> Brunschwig pedagogy is NOT systematically complementing Voynich enforcement. Alignment is curriculum-level, not interface-level.

Both outcomes are informative.

---

*Builds on: AZC_TRAJECTORY_SHAPE (scaffold fingerprint), TRAJECTORY_SEMANTICS (judgment matrix)*
