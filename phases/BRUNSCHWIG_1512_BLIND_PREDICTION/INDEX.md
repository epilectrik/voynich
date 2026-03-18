# Phase 598: BRUNSCHWIG_1512_BLIND_PREDICTION

**Status:** COMPLETE
**Verdict:** WEAK_THERMAL_INTENSITY_ALIGNMENT (not apparatus alignment)
**Constraints:** C1735-C1736
**Scripts:** `scripts/extract_1512_recipes.py`, `scripts/compute_1512_distributions.py`, `scripts/blind_prediction_test.py`, `scripts/followup_apparatus_gradient.py`
**Results:** `results/brunschwig_1512_recipes.json`, `results/blind_prediction_results.json`, `results/followup_results.json`
**Runtime:** ~7s total across all scripts

## Motivation

The original blind prediction test (F-BRU-001) failed its pre-registered threshold (6/8, profile discrimination 0.064 vs 0.10). All 34 existing Brunschwig fits used the 1500 *Liber de arte distillandi de simplicibus*.

The 1512 *Liber de arte distillandi de compositis* is genuinely held-out data — never used in any fit. This phase extracts recipes from the 1512 book and tests whether its fire degree distributions predict Voynich grammar features.

## Design (Expert-Reviewed)

### Approach A: Class-Level Prediction (No Folio Mapping)

Per expert recommendation, we do NOT map individual recipes to individual folios. Instead:
1. Bin recipes by fire degree class (inferred from distillation method)
2. Pre-register structural parameter RANGES for each class
3. Test against the DISTRIBUTION of all B folios
4. This avoids circularity entirely

### Pre-Registration

SHA-256: `ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d`
Committed before any test execution (commit 542e150).

## Sub-Phases

### 598a: Recipe Extraction
- 431 confirmed recipes from 1512 English translation
- Fire degree: 83.2% gentle (d1), 16.8% elevated (d2-4), ratio 4.9:1
- Methods, vessels, product types, distillation step depth tracked per recipe

### 598b: Prediction Lock
- 5 positive predictions + 2 negative controls pre-registered
- SHA-256 hash committed to repository

### 598c: Blind Test Execution (v2, expert-corrected)
Expert post-hoc review caught 6 methodological issues. v2 corrections:
- R1 vs R3+R4 consistently (R2 excluded as ambiguous)
- Section-stratified replication for P2/P3 (Stars, n=10+13)
- Partial correlation for P5 (log(n_tokens) size control)
- N2 dropped (Jaccard=1.000, trivially passes per C1499)

| Test | Result | Survives Control? |
|------|--------|-------------------|
| P1 (REGIME distribution) | FAIL -- R1 = 47.8% (needed >60%) | N/A |
| P2 (k/(k+ke) ratio) | PASS full, FAIL stratified (p=0.058) | No -- section confound |
| P3 (e->y rate) | PASS full AND stratified (p=0.0007) | **Yes -- CLEAN** |
| P4 (r->a routing) | FAIL (p=0.315) | N/A -- genuine null (C1724) |
| P5 (complexity~ke-depth) | PASS -- partial rho=0.248, p=0.024 | Yes -- attenuated but real |
| N1 (headless) | FAIL -- expected per C1574 | Informative, not damaging |

Verdict: WEAK_ALIGNMENT_CONTROLS_NOTED (3/5 positive, 0/1 negative)

### 598d: Follow-up Apparatus + Within-Folio Gradient

**Block 1: Apparatus Profile Test (within Herbal, MIDDLE-based C1248 scores)**
- R1 vs R2+R3+R4 within Herbal: 2/4 directions correct, 0/4 significant
- DISTILLATION: both R1 folios scored 93rd-100th percentile (WRONG direction)
- **Verdict: APPARATUS_PROFILE_NOT_CONFIRMED**
- Key finding: apparatus profiles are section-level, not REGIME-within-section

**Block 2: Within-Folio Paragraph Gradient**
- H1: No ordinal gradient (mean rho=-0.006, t-test p=0.919) -- PASS, confirms C1399/C1400
- H2: THERMAL->e->y within-folio (rho=0.155, p=0.0015) -- PASS
- H3: THERMAL->ke-depth within-folio (rho=0.303, p<0.0001) -- PASS
- **Verdict: WITHIN_FOLIO_GRADIENT_CONFIRMED**

## Key Finding

The 1512 alignment is about **thermal intensity modulating safety infrastructure**, not about apparatus identity following fire degrees. The alignment is real but narrow:

- **What passes:** e->y safety rate discriminates REGIMEs within Stars (C1735). THERMAL-enriched paragraphs show higher e->y and deeper ke engagement within individual folios (C1736).
- **What fails:** REGIME distribution, apparatus profiles within sections, k/(k+ke) within sections, r->a routing.
- **Implication:** The 1512's gentle/elevated process distinction predicts paragraph-level safety and kernel-depth modulation, but does NOT predict apparatus type or population proportions. A proper apparatus alignment test requires multi-axis apparatus-bundle comparison, not a binary intensity split.

## Section-REGIME Cross-tab (Critical Structural Finding)

```
B: R1=20 R2=0  R3=0  R4=0   (100% R1 -- no intensity contrast possible)
H: R1=2  R2=13 R3=5  R4=12  (all REGIMEs, but R1 only n=2)
S: R1=10 R2=0  R3=12 R4=1   (best test site: R1 vs R3)
C: R1=0  R2=2  R3=2  R4=1
T: R1=0  R2=0  R3=1  R4=1
```

## Constraints

| ID | Finding |
|----|---------|
| C1735 | 1512 thermal intensity alignment -- e->y safe pathway rate: held-out 1512 gentle/elevated fire degree distinction predicts e->y rate between R1 and R3+R4 within Stars section (p=0.0007, section-controlled); class_entropy~ke-depth partial rho=0.248 (size-controlled, p=0.024); alignment is thermal intensity, not apparatus identity |
| C1736 | Within-folio THERMAL-safety paragraph gradient -- THERMAL-enriched paragraphs show higher e->y rate (rho=0.155, p=0.0015) and deeper ke engagement (rho=0.303, p<0.0001) within individual folios; no systematic ordinal gradient (C1399/C1400 confirmed); section confound impossible at paragraph level |
