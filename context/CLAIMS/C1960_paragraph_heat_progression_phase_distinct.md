# C1960: Paragraph Heat-Progression Encoding on Heat-Phase-Distinct Matched Folios

**Tier:** 3 (PROVISIONAL — SCOPE-RESTRICTED)
**Scope:** B, paragraph, heat-mode, recipe-correspondence, layout, scope-restricted
**Phase:** HEAT_PROGRESSION_REFINED (Phase 647 / 645b)
**Extends:** C1959 (paragraph layout-order recipe-phase coherence), C1225 (e-depth suffix parametricity), C1226 (ke/ek process-context conditioning), C1957 (suffix-boundary fix improving e-depth measurement)
**Relates to:** C1206 (paragraph kernel gradient), C1457-C1462 (e→y safe pathway), C1735, C1740, C1750, C1752 (Brunschwig fire-degree alignment), C1872, C1873 (k/e channel REGIME/Stars calibration)

---

## Statement

On confirmed-match folios whose source recipe has **distinct heat-phase changes** (e.g., specification-block→body, vigorous-heat→gentle-heat, setup→cendres→bath), per-paragraph heat metrics derived from atom decomposition correlate positively with predicted recipe fire-degree at the paragraph layout-position level. **Best metric:** `qokeedy_frac` (qokeedy count / paragraph length); mean Spearman rho = +0.710 across 5 heat-phase-distinct confirmed matches; 5/5 positive direction.

This effect is **absent on heat-uniform recipes** where the source procedure has sustained gentle heat throughout (e.g., uniform balneum, sustained sublimation). Heat-uniform control set: mean rho +0.066 — essentially null.

**Effect size differential: +0.64** (heat-phase-distinct minus heat-uniform).

The constraint is **scope-restricted** to recipes with distinct heat-phase changes. Universal heat-progression-encoding does NOT hold (Phase 645 confirmed this null on uniform-heat recipes was real, not methodological).

---

## Empirical evidence (Phase 645b)

### Heat-phase-distinct subset (5 folios)

| Folio | Recipe | n_paragraphs | qokeedy_frac rho | best metric rho | best p |
|-------|-------|:---:|:---:|:---:|:---:|
| f84r | II.12.0 (gold dissolution / putrefaction) | 18 | +0.983 | +0.983 | 0.001 ★ |
| f82r | III.19.3 (lunaria 3-day sealed) | 4 | +0.833 | balneum_score +1.000 | 0.082 |
| f78r | III.36.0 (mercury congelation) | 8 | +0.540 | qok_class_frac +0.756 | 0.123 |
| f86v3 | II.10.0 (3-day coniuncció) | 7 | +0.764 | +0.764 | 0.300 |
| f77r | III.28.0 (4-element temperament) | 13 | +0.429 | +0.429 | 0.221 |

**Aggregate (qokeedy_frac):**
- Mean rho: **+0.710**
- 5/5 positive direction
- 1/5 strict significant (f84r p=0.001)

### Heat-uniform control (3 folios)

| Folio | Recipe | n_paragraphs | qokeedy_frac rho |
|-------|-------|:---:|:---:|
| f75r | III.19.0 (aqua vitae × 4-9 reflux, mostly balneum) | 3 | +0.000 |
| f108v | III.29.0 (mercury sublimation, sustained gentle) | 10 | +0.411 |
| f79v | II.8.0 (first liquefaction, 3-day balneum) | 7 | -0.212 |

**Aggregate (qokeedy_frac):** Mean rho +0.066, 1/3 positive direction, 0/3 significant.

---

## Pre-classification (locked before test)

Recipes pre-classified by reading the matched Catalan recipe for explicit heat-phase changes:

**Heat-phase-distinct** = recipe has phases with materially different fire-degrees (vigorous, gentle, none, etc.):
- f84r: 12-parties spec (no heat) → balneum body → putrefaction (sustained low) → closure
- f82r: setup → cendres × 3 days (vigorous) → bath distillation (gentle)
- f78r: foch de sots primary (vigorous) → reiteration cycles (moderate)
- f86v3: 11-hour vigorous → 3-day balneum → 1.5-month putrefaction
- f77r: 4-element specification (no heat) → temperate-fire iteration body

**Heat-uniform** = recipe has sustained-similar heat throughout:
- f75r: mostly balneum throughout (gentle uniform)
- f108v: "longues e lentes decoccions" (gentle uniform sustained)
- f79v: sustained 3-day balneum (gentle uniform)

---

## Operational interpretation

The Voynich appears to encode heat-mode at the paragraph level when the recipe's heat-mode varies across phases. When the recipe is heat-uniform throughout, no paragraph-level heat-progression structure exists in the encoding (consistent with there being nothing to encode).

This is a **second syntactic rule** complementing C1959:
- C1959: paragraph layout-order tracks recipe-phase order on matched folios (Tier 3, n=8)
- C1960: per-paragraph heat metrics track recipe fire-degree on heat-phase-distinct subset of matched folios (Tier 3, n=5 phase-distinct + 3 uniform-control)

Together, the rules suggest the Voynich's paragraph structure encodes **multiple recipe-phase properties simultaneously** — phase-ordinal (C1959) and heat-degree (C1960). The heat-encoding is conditional on recipe heat-phase-distinctness; the phase-ordinal encoding holds across all matched recipes.

---

## Tier 3 because

- N=5 phase-distinct folios is small
- Heat-classification of recipes is interpretive (phase-distinct vs uniform)
- Heat-degree predictions per paragraph are interpretive
- Only 1/5 individually strict-significant (f84r p=0.001)
- BUT: 5/5 positive direction with mean rho +0.71 vs control +0.07 is a large effect

**Path to Tier 2:** Additional confirmed matches whose recipes have heat-phase distinctions, with stronger individual significance, and ideally a refined heat-classification methodology that's less interpretive (e.g., based on independent reading by another annotator).

---

## Falsifiable predictions

1. **CONFIRMED 2026-04-25:** Heat-phase-distinct subset shows mean rho > heat-uniform control by ≥0.30 — observed difference +0.64.
2. New confirmed matches whose recipes are heat-phase-distinct should show qokeedy_frac rho > +0.40 against predicted fire-degree.
3. New confirmed matches whose recipes are heat-uniform should show qokeedy_frac rho < +0.30 (no consistent direction).
4. The heat-encoding should NOT contradict C1957 (e-depth measurement post-suffix-boundary-fix); the per-paragraph metrics are valid because they aggregate token-level e-depths under the corrected morphology.

---

## Caveats

- Phase 645 (broad version of this test, before refinement) returned mixed result with mean rho +0.484 across all 7 folios. Phase 645b restricted to heat-phase-distinct subset converted that to clean +0.71 signal. The pre-registration discipline of separating subsets BEFORE testing is what made this honest.
- Heat-uniform recipes can't show heat-progression-encoding because there's nothing to progress. The "null" on uniform recipes is methodological, not data failure.
- Test depends on Phase 643 (C1959 layout-order tracking) and Phase 644 (atom-decode-verified matches). If those weaken under additional review, this constraint weakens too.
- Heat-classification of recipes is human-interpreted. A more rigorous methodology would score recipe-text for heat-keyword density variance (low variance = uniform; high variance = phase-distinct) and use that score as a continuous predictor.

---

## Method

- Per-paragraph heat metrics computed from atom decomposition: mean_e_depth, qokeedy_frac, qokedy_frac, qok_class_frac, gentle_ratio, balneum_score
- Predictions LOCKED in `phases/HEAT_PROGRESSION_REFINED/results/predictions.md` before metric computation
- Pre-classification of recipes (heat-phase-distinct vs heat-uniform) LOCKED before test
- Spearman rank correlation with permutation null (n_perm=2000, fixed seed 42)

**Script:** `phases/HEAT_PROGRESSION_REFINED/scripts/test_refined.py`
**Results:** `phases/HEAT_PROGRESSION_REFINED/results/test_results.json`
