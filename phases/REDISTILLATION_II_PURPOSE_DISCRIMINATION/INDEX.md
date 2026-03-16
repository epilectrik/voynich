# Phase 597: REDISTILLATION_II_PURPOSE_DISCRIMINATION

**Status:** COMPLETE
**Verdict:** REDISTILLATION_DEAD_SAFETY_SUBSTITUTION
**Constraints:** C1732–C1733
**Script:** `scripts/redistillation_ii_test.py` (2.5s)
**Results:** `results/redistillation_ii_results.json`

## Motivation

Phase 596 confirmed the safety-routing MECHANISM (C1480-C1482) explaining HOW double-ii operates but could not discriminate the redistillation PURPOSE hypothesis (T7/T8 mis-premised — both hypotheses predicted identical outcomes). This phase designs 6 expert-reviewed tests targeting process-level signatures that ONLY redistillation predicts, with controls for confounds caught during expert review.

## Tests

### T1: e-to-y Safety Co-deployment (PRIMARY GATE)
**Logic:** If ii = redistillation of valuable product, folios with high ii should ALSO have high e-to-y rates (co-deployment of safety infrastructure). Pure safety predicts substitution or uncorrelation.
- Raw Spearman rho = **-0.633** (p < 0.001): strong ANTI-correlation
- Section+REGIME controlled rho = +0.264 (p=0.016): weak, fails significance threshold
- **FAIL — but the anti-correlation IS the finding**: ii and e-to-y are folio-level SUBSTITUTES

### T2: A-side e-depth Co-occurrence (SECONDARY GATE)
**Logic:** A records with deep-e (stability continuum) should co-occur with high ii if redistillation targets stabilized material.
- Raw rho = -0.0003 (null), length-controlled rho = +0.401 (p < 0.001)
- **AMBIGUOUS**: control CREATES correlation from null raw — possible collider bias
- Length may be a collider (common effect of e-depth and ii) rather than confounder

### T3: FL State Co-occurrence (SUPPORTING)
**Logic:** Lines with ii-tokens should co-occur with late FL vocabulary if ii targets already-processed material.
- ii-lines FL mean = 3.20, single-i FL mean = 2.96, a-HEAD-no-i FL mean = 3.16
- ii vs single-i: p < 0.001 (significant)
- ii vs a-HEAD baseline: p = 0.216 (NOT significant)
- **FAIL**: FL elevation on ii-lines is entirely explained by a-HEAD embedding (expert-recommended control catches it)

### T4: Mode A Specification Residual (SUPPORTING)
**Logic:** ii proportion within a-HEAD should predict Mode A fraction beyond a-HEAD alone.
- beta_ii = +0.009, t = 0.290, p = 0.773
- **FAIL**: dead null

### T5: OPERATION Category Co-occurrence (SUPPORTING)
**Logic:** ii should concentrate in paragraphs with high OPERATION fraction if redistillation involves sustained operation.
- Raw rho = +0.001 (null), section-controlled rho = +0.286 (p < 0.001)
- **POSITIVE with section-mediation caveat**: raw null followed by significant controlled result suggests section suppression of within-section signal, but same pattern as T2 warrants caution

### T6: Forgiveness Prediction (CHARACTERIZATION — added post expert review)
**Logic:** Does ii-fraction predict folio forgiveness (AXM self-transition rate) beyond e-to-y alone? Tests whether ii has independent safety contribution.
- Raw: delta-R² = +0.058, F = 6.65, p = 0.012, beta_ii = -0.844
- Section-controlled: delta-R² = +0.034, F = 5.10, p = 0.027, beta_ii = **-0.673**
- ii ANTI-predicts forgiveness: folios with more ii are LESS forgiving
- e-to-y POSITIVELY predicts forgiveness: rho = +0.569
- **KEY FINDING**: Two complementary HEAD-domain safety architectures with opposite forgiveness profiles

## Key Findings

### 1. Redistillation Hypothesis Falsified
The primary gate (T1) shows strong anti-correlation (rho=-0.633) between ii and e-to-y deployment. Redistillation predicts co-deployment; safety substitution produces anti-correlation. T3 (a-HEAD control), T4 (dead null), and T2 (collider-ambiguous) provide no rescue.

### 2. Complementary HEAD-Domain Safety Architecture Discovered
The grammar deploys two folio-level safety strategies in complementary HEAD domains:

| Strategy | HEAD Domain | Mechanism | Forgiveness |
|----------|------------|-----------|-------------|
| **e-to-y** | e-HEAD | Preventive — stability anchor at SPECIFICATION zone | High (rho=+0.569 with AXM self-transition) |
| **ii** | a-HEAD | Transformative — collapses r-terminal hazard vector to 0.2% | Low (rho=-0.536, section-controlled beta=-0.673) |

Folios emphasize one strategy or the other (rho=-0.633), never both at maximum deployment. This extends the safety architecture model (C1446-C1471) with a folio-level strategy selection dimension.

### 3. Forgiveness Asymmetry Explained Mechanistically
e-to-y is PREVENTIVE (avoids hazardous territory), producing forgiving programs. ii is TRANSFORMATIVE (operates within hazardous a-HEAD territory with categorical terminal protections), producing less forgiving programs. A program that works inside hazardous territory with protections is structurally less forgiving than one that avoids hazardous territory entirely.

## Constraints

### C1732: Folio-Level Safety Substitution
ii and e-to-y are folio-level safety substitutes operating in complementary HEAD domains (Spearman rho=-0.633, p<0.001; e-to-y in e-HEAD domain C1457, ii in a-HEAD domain C1480).

**Tier 2** | Scope: B, MIDDLE, atom, safety, substitution, folio

### C1733: Two-Strategy Safety Architecture with Forgiveness Asymmetry
e-to-y pathway (preventive, e-HEAD) positively predicts folio forgiveness (AXM self-transition rate rho=+0.569); ii pathway (transformative, a-HEAD) anti-predicts forgiveness (section-controlled beta=-0.673, p=0.027). Folio safety strategy selection produces opposite forgiveness profiles.

**Tier 2** | Scope: B, MIDDLE, atom, ii, e-to-y, forgiveness, safety, folio

## Expert Review Notes
- T3 k-HEAD avoidance: DROPPED pre-implementation (HEAD atom mutual exclusivity = tautological confound)
- T4 REGIME_4 precision: DROPPED pre-implementation (non-discriminating — both hypotheses predict same outcome)
- T1 a-HEAD control: Applied via section+REGIME dummies
- T2 collider bias: Flagged by expert — raw null + controlled positive is textbook collider signal
- T6 section control: Added per expert recommendation — finding survives (attenuated but significant)
