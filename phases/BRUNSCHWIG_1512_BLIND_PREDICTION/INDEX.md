# Phase 598: BRUNSCHWIG_1512_BLIND_PREDICTION

**Status:** IN PROGRESS
**Verdict:** PENDING
**Constraints:** TBD
**Script:** `scripts/extract_1512_recipes.py`, `scripts/blind_prediction_test.py`
**Results:** `results/brunschwig_1512_recipes.json`, `results/blind_prediction_results.json`

## Motivation

The original blind prediction test (F-BRU-001) failed its pre-registered threshold (6/8, profile discrimination 0.064 vs 0.10). It was rescued by a different 197-recipe analysis, which is methodologically questionable. All 34 existing Brunschwig fits used the 1500 *Liber de arte distillandi de simplicibus*.

The 1512 *Liber de arte distillandi de compositis* is genuinely held-out data — never used in any fit. This phase extracts recipes from the 1512 book and designs a clean blind prediction test using structural features that did not exist when F-BRU-001 was written.

## Design (Expert-Reviewed)

### Approach A: Class-Level Prediction (No Folio Mapping)

Per expert recommendation, we do NOT map individual recipes to individual folios. Instead:
1. Bin recipes by fire degree class (inferred from distillation method)
2. Pre-register structural parameter RANGES for each class
3. Test against the DISTRIBUTION of all B folios
4. This avoids circularity entirely

### Predictive Features (Ranked by Discriminating Power)

**Strong (use):**
- k/(k+ke) ratio — ke-family parametric depth (C1225, F-BRU-032)
- e→y safe pathway rate — predicts folio forgiveness (C1457-C1462)
- Terminal routing r→a rate — novel prediction (C1563)
- REGIME assignment — with section control (C1404)

**Negative controls (should NOT correlate):**
- Headless compound rate — system-level infrastructure (C1523-C1527)
- Modifier grammar universality — should not vary by process type (C1504)

**Dropped (per expert):**
- Category distributions — THERMAL dominates, passes trivially
- Suffix mode balance — circular with category

### Fire Degree Inference from Method

The 1512 book rarely specifies fire degrees explicitly. Inferred from method:
- Balneum Mariae / water bath → Degree 1 (gentle)
- Horse dung / putrefaction → Degree 1 (gentle, sustained)
- Ashes / sand bath → Degree 2-3 (moderate)
- Open fire / strong fire → Degree 3-4 (intense)
- Circulatio / pelican → Degree 1-2 (gentle, recirculating)

### Pre-Registration Protocol

Predictions will be committed as SHA-256 hash before any analysis against the Voynich transcript.

## Sub-Phases

### Phase 598a: Recipe Extraction
Extract and catalog all recipes from the 1512 English translation with:
- Fire degree (inferred from method)
- Product type (water, oil, balsam, quintessence, aqua vitae)
- Distillation method
- Vessel type
- Duration indicators
- Procedural complexity (number of steps)

### Phase 598b: Prediction Lock
Pre-register specific quantitative predictions per fire degree class.
Commit SHA-256 hash to repository.

### Phase 598c: Blind Test Execution
Run predictions against Voynich transcript. Score pass/fail.

## Data Sources

- **1512 text:** `sources/brunschwig_1512/brunschwig_1512_english.txt` (45,926 lines)
- **1500 comparison:** `data/brunschwig_curated_v3.json` (245 recipes, latest curated)
- **Voynich transcript:** Standard H-track via `scripts/voynich.py`
