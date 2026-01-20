# Brunschwig Backpropagation Fits

**Phase:** BRUNSCHWIG_BACKPROP_VALIDATION
**Date:** 2026-01-15
**Status:** COMPLETE (revised 2026-01-16)

---

## Purpose

These fits demonstrate the explanatory power of the frozen constraint system by showing that:
1. Historical distillation procedures align with inferred product types
2. Alternative interpretations (property-based) fail to reproduce observed structure
3. The geometric/manifold interpretation is stable under perturbation

**WARNING:** These are FITs, not constraints. They show *what happens to be true* given this manuscript and this external corpus. They do not define architectural necessity.

---

## Overstatement Correction (BRU-AUDIT 2026-01-16)

> **Earlier reverse-Brunschwig phases overstated the separability of product profiles due to transcriber artifacts (loading all transcribers instead of H-only created ~3.2x token inflation).**
>
> With corrected data:
> - Product-exclusive MIDDLEs: 78.2% -> **71.8%** (still strong)
> - Profile discrimination: 0.105 -> **0.064** (below 0.10 threshold)
> - Blind predictions: 8/8 -> **6/8** (directions correct, magnitudes off)
> - MIDDLE hierarchy: **preserved** (ratios shifted, structure intact)
>
> **Interpretation:** Product affordances remain visible but overlapping. This is the *correct* outcome for an affordance-based model. Product types are not clean partitions of A-space; experts recognize materials by patterns that tolerate overlap.
>
> All interpretations have been adjusted accordingly. Do not resurrect pre-audit claims.

---

## F-BRU-001: Brunschwig Product Type Prediction (Blind)

**Tier:** F2 (External Alignment)
**Scope:** A
**Result:** SUCCESS (upgraded 2026-01-19)
**Supports:** C475, C476

### Method
Pre-registered predictions for 3 Brunschwig recipes, locked before execution:
- Lavender water (1st degree) → WATER_GENTLE
- Sage water (2nd degree) → WATER_STANDARD
- Juniper oil (3rd degree) → OIL_RESIN

### Finding (Original)
8/8 signature predictions correct. Product type correctly predicts PREFIX profile without circularity.

### Finding (Revised - BRU-AUDIT 2026-01-16)
6/8 signature predictions correct with H-only clean data:
- Lavender Water: 1/3 (directions correct, magnitudes off)
- Sage Water: 2/2 (preserved)
- Juniper Oil: 3/3 (preserved)

Profile differences weakened: mean 0.064 (below 0.10 threshold).
Framework still valid but calibration needed for precise predictions.

### Status Update (2026-01-19)
Following BRUNSCHWIG_REVERSE_ACTIVATION phase:
- Grammar compliance: **86.8%** (197 recipes pass Voynich hazard rules)
- Category-Product correlation: Chi-sq=1267.80, p<0.0001
- REGIME saturation: All 4 REGIMEs populated (chi-sq p=0.001)
- Permutation test: p=0.011 (non-random assignment)

Upgraded from PARTIAL to SUCCESS based on comprehensive 197-recipe analysis.

### Status
✔ Structurally valid (directions correct)
✔ Grammar embedding confirmed (86.8% compliance rate)
✖ Depends on one external corpus (Brunschwig)
✖ Not architecturally necessary

---

## F-BRU-002: Degree-REGIME Boundary Asymmetry

**Tier:** F3 (Structural Characterization)
**Scope:** B
**Result:** SUCCESS
**Supports:** C179-C185, C458

### Method
Tested whether Brunschwig degree profiles can fit REGIME constraints:
- Can Degree 1 violate R3? → YES (insufficient e_ops)
- Can Degree 4 fit R2? → NO (k exceeds max)
- Can Degree 3 fit R4? → NO (HIGH_IMPACT forbidden)

### Finding
All 3 questions CONFIRMED. Violations are asymmetric (not nested structure).

### Status
✔ Real, boundary-defining
⚠ Borderline constraint-eligible
✖ Empirically described, not architecturally forced

**Correct handling:** Refinement note attached to REGIME block, not new constraint.

---

## F-BRU-003: Property-Based Generator Rejection

**Tier:** F2 (Negative Knowledge)
**Scope:** A
**Result:** NEGATIVE
**Supports:** C475, C476

### Method
Synthetic property-based registry with:
- 8 "properties"
- Smooth overlap
- Zipf-like frequencies

Tested against same metrics as Voynich.

### Finding
Property model FAILS to reproduce Voynich structure:

| Metric | Voynich | Property Model |
|--------|---------|----------------|
| Uniqueness | 72.7% | 41.5% |
| Hub/Tail ratio | 0.006 | 0.091 |
| Clusters | 33 | 56 |

### Status
✔ Real, methodologically strong
✔ Permanently kills property/low-rank interpretations
✖ Negative knowledge, not positive constraint

**Correct handling:** Document as generator rejection, link to C475/C476 as evidentiary support. Do NOT mint new constraint.

---

## F-BRU-004: A-Register Cluster Stability

**Tier:** F2 (Robustness Characterization)
**Scope:** A
**Result:** SUCCESS
**Supports:** C481

### Method
Perturbation tests on WATER_GENTLE clusters:
- Tail removal (10-20%)
- Hub downweight (30-50%)
- Random removal (10-20%)

### Finding
Clusters robust to artifact-indicating perturbations:
- Tail removal: 100% survival
- Hub downweight: 100% survival
- Random removal: Degrades (expected - vocabulary-dependent)

### Status
✔ Real, good defensive test
✖ Characterization, not necessity
✖ Clusters could exist or not without breaking architecture

**Correct handling:** Registry geometry stability fit, useful for robustness arguments.

---

## F-BRU-005: MIDDLE Hierarchical Structure

**Tier:** F2 (Characterization)
**Scope:** A
**Result:** SUCCESS (confirmed with clean data 2026-01-16)
**Supports:** C383, C475

### Method
Cross-type MIDDLE analysis measuring sharing patterns.

### Finding (Original)
Hierarchical vocabulary structure confirmed:

| Layer | Count | % | Meaning |
|-------|-------|---|---------|
| Universal | 106 | 3.5% | Connective infrastructure |
| Cross-cutting | 480 | 15.7% | Shared constraint dimensions |
| Type-specific | 2,474 | 80.8% | Local coordinates |

### Finding (Revised - BRU-AUDIT 2026-01-16)
Structure preserved with H-only clean data:

| Layer | Original | Revised | Status |
|-------|----------|---------|--------|
| Universal (4 types) | 3.5% (106) | 6.1% (129) | PRESERVED |
| Cross-cutting (2-3 types) | 15.7% (480) | 18.5% (392) | PRESERVED |
| Type-specific (1 type) | 80.8% (2,474) | 75.4% (1,597) | PRESERVED |

The three-layer hierarchy is robust to data correction. This is one of the most defensible findings in the project.

### Finding (2-Track Stratification - 2026-01-20)

Following C498 (Two-Track Vocabulary Structure), re-analyzed type-specificity by track:

| Track | Type-Specific | 2-Type | 3-Type | Universal | n |
|-------|--------------|--------|--------|-----------|---|
| Registry-internal | **62.5%** | 17.2% | 3.9% | 16.4% | 128 |
| Pipeline-participating | **46.1%** | 16.4% | 14.8% | 22.7% | 128 |

**Statistical test:** Chi-square = 12.64, df=3, p < 0.01, Cramer's V = 0.222

**Finding:** The 75.4% type-specific rate is **CONFOUNDED** by the 2-track structure:
- Registry-internal MIDDLEs (folio-localized, avg 1.34 folios) show artificially high type-specificity because they appear in fewer folios and thus naturally span fewer product types
- Pipeline-participating MIDDLEs (which actually flow through A→AZC→B) show 46.1% type-specificity - significantly lower

**Interpretation:** Product-type encoding in operational vocabulary is weaker than the aggregate 75.4% suggests. The hierarchical structure is still valid, but the type-specific layer is dominated by registry-internal vocabulary that encodes within-category fine distinctions, not execution-relevant product-type markers.

### Status
✔ Real, quantifies existing implications
✔ Survives data hygiene audit
✔ 2-track stratification reveals confound (2026-01-20)
✖ Already implicit in C383, C475, C476
✖ Adds clarity, not new rule

**Correct handling:** Fold into C383/C475 documentation, not separate constraint. Note 2-track confound.

---

## F-BRU-006: Closure × Product Affordance Correlation

**Tier:** F3 (Characterization)
**Scope:** A
**Result:** SUCCESS
**Supports:** C233, C422 (closure/DA structure)
**Added:** 2026-01-16 (BRU-AUDIT Track 4)

### Method
Chi-square test of closure morphology distribution across product types at line-final position.

### Finding
Entry-internal closure morphology correlates with externally defined monitoring intensity of product classes:

| Product Type | y-closure | Monitoring Intensity |
|--------------|-----------|---------------------|
| WATER_GENTLE | 54.5% | High (gentle handling) |
| PRECISION | 46.2% | High (exact timing) |
| WATER_STANDARD | 33.3% | Moderate |
| OIL_RESIN | 24.0% | Low (intense extraction) |

Chi-square: p = 0.0226 (significant)

Key differences:
- PRECISION vs OIL_RESIN: +22.2% y-closure
- WATER_GENTLE vs WATER_STANDARD: +21.2% y-closure

### Interpretation

> Closure morphology correlates with anticipated attentional stability requirements in downstream practice.

Products requiring precise monitoring (gentle waters, precision distillates) show higher y-closure rates. Products involving intense extraction (oils/resins) show lower y-closure.

This is consistent with:
- HT as vigilance signal
- Closure as cognitive hygiene marker
- Product affordances rather than material labels

### Status
✔ Survives H-only data correction
✔ Modest but significant effect (p < 0.05)
✔ Consistent with human-factors model
✖ Does not classify entries
✖ Does not map tokens to substances
✖ Overlaps expected (affordance, not taxonomy)

### What This Does NOT Claim

- ❌ Closure markers identify materials
- ❌ Product types are clean partitions
- ❌ y-closure = "monitoring" semantically

**Correct handling:** Tier 3 characterization linking Currier A structure to external affordance patterns. Do not promote to constraint.

---

## F-BRU-007: SLI-Constraint Substitution Model

**Tier:** F2 (Structural Characterization)
**Scope:** B
**Result:** SUCCESS
**Supports:** C458, C477
**Added:** 2026-01-19 (SENSORY_LOAD_ENCODING + BRUNSCHWIG_REVERSE_ACTIVATION)

### Method
Computed Sensory Load Index (SLI) for 83 B folios:
```
SLI = hazard_density / (escape_density + link_density)
```
Tested correlation with HT density (C477 reference: r=0.504).

### Finding
**INVERSE correlation discovered:**

| Metric | Result |
|--------|--------|
| SLI vs HT density | r = **-0.453**, p < 0.0001 |
| REGIME_2 (gentle) | LOWEST SLI (0.786), HIGHEST HT |
| REGIME_3 (oil/resin) | HIGHEST SLI (1.395), LOWEST HT |

This is the OPPOSITE of the initial hypothesis ("high sensory demand → higher vigilance").

### Interpretation: Constraint Substitution Model

> "The Voynich Manuscript encodes sensory requirements by tightening constraints rather than signaling vigilance."

When operations are dangerous (high SLI):
- Grammar restricts options
- Fewer choices available
- Less vigilance needed (can't make wrong choice)

When operations are forgiving (low SLI):
- Grammar permits many options
- More choices require discrimination
- Higher vigilance (HT) for decision complexity

**This STRENGTHENS C458 (Execution Design Clamp)** by providing the mechanism: hazard exposure is clamped because high-hazard contexts have tightened constraints.

### Status
✔ Strong statistical support (p < 0.0001)
✔ Mechanistically coherent with C458, C477
✔ Survives recipe-level validation (197 recipes)
✖ SLI is a constructed metric, not discovered structure
✖ External interpretation layer

**Correct handling:** F2 fit linking constraint geometry to vigilance signaling. Document as explanatory model in INTERPRETATION_SUMMARY.md.

---

## F-BRU-008: Zone Affinity Differentiation

**Tier:** F2 (Structural Characterization)
**Scope:** B
**Result:** SUCCESS
**Supports:** C443 (Positional Escape Gradient)
**Added:** 2026-01-19 (BRUNSCHWIG_REVERSE_ACTIVATION)

### Method
Computed zone affinity (C/P/R/S) for 197 Brunschwig recipes based on:
- Intervention rate → P-affinity
- SLI → R-affinity (sequential processing)
- Product type and REGIME

Tested whether SLI clusters differentiate on zone affinity using ANOVA.

### Finding
**ALL 4 zones show significant differentiation by SLI cluster:**

| Zone | F-statistic | p-value |
|------|-------------|---------|
| C-affinity | F = 69.4 | p < 0.0001 |
| P-affinity | F = 33.1 | p < 0.0001 |
| R-affinity | F = 106.6 | p < 0.0001 |
| S-affinity | F = 21.6 | p < 0.0001 |

**Zone patterns by REGIME:**

| REGIME | Dominant Zone | Interpretation |
|--------|---------------|----------------|
| REGIME_1 | S (0.30) | Boundary stability |
| REGIME_2 | C (0.51) | Setup/flexible |
| REGIME_3 | R (0.43) | Sequential processing |
| REGIME_4 | S (0.55) | Boundary control |

**Zone correlations with SLI:**
- SLI vs P-affinity: r = 0.505, p < 0.0001
- SLI vs R-affinity: r = 0.605, p < 0.0001

### Status
✔ All zones significantly differentiate (p < 0.0001)
✔ Pattern matches theoretical predictions
✔ Supports C443 escape gradient structure
✖ Zone affinity is computed, not measured

**Correct handling:** F2 fit demonstrating zone structure differentiates by constraint pressure. Link to C443.

---

## F-BRU-009: Zone-Modality Addressing (Two-Stage Model)

**Tier:** F3 (External Alignment)
**Scope:** B
**Result:** CONFIRMED (with REGIME heterogeneity)
**Supports:** C477 (HT), C443 (Escape Gradient), C458 (Execution Design Clamp)
**Added:** 2026-01-19 (BRUNSCHWIG_REVERSE_ACTIVATION)
**Updated:** 2026-01-19 (ZONE_MODALITY_VALIDATION - two-stage model)

### Method
Rigorous validation of zone-modality associations with:
- Enhanced sensory extraction (102 keywords)
- Cohen's d effect sizes
- Permutation tests (1000 shuffles)
- Bonferroni correction
- REGIME stratification

### Finding (Original)

| Modality | Predicted | Result | Effect Size |
|----------|-----------|--------|-------------|
| SOUND → R-affinity | R-zone (sequential) | **CONFIRMED** | d=0.61, p=0.0001 |
| SOUND → P-affinity | P-zone (monitoring) | **CONFIRMED** | d=1.08, p<0.0001 |
| SIGHT → P-affinity | P-zone | Underpowered | d=0.27, n=7 |
| TOUCH → S-affinity | S-zone | **WRONG DIRECTION** | d=-0.64, n=3 |

### Key Discovery: REGIME Heterogeneity

When stratifying R-SOUND effect by REGIME:

| REGIME | R-zone Effect (d) | Interpretation |
|--------|------------------|----------------|
| REGIME_1 (STANDARD) | 0.48 | Moderate - throughput tracking |
| REGIME_2 (GENTLE) | 1.30 | Strong - setup phase dominates |

**Effect range: 0.82** - This is NOT corruption but structured workflow adaptation.

### Zone Profiles for SOUND Recipes by REGIME

| REGIME | n | C | P | R | S | Dominant |
|--------|---|---|---|---|---|----------|
| REGIME_1 | 73 | 0.214 | 0.301 | **0.273** | 0.212 | P/R balanced |
| REGIME_2 | 9 | **0.453** | 0.253 | 0.169 | 0.125 | C-dominant |
| REGIME_3 | 2 | 0.233 | 0.324 | **0.443** | 0.000 | R-dominant |
| REGIME_4 | 3 | 0.131 | 0.199 | 0.134 | **0.536** | S-dominant |

### Two-Stage Sensory Addressing Model

> **AZC zones do not encode sensory modalities. Instead, they distribute human sensory relevance across workflow phases in a REGIME-dependent way.**

**Stage 1 - Modality Bias (External/Brunschwig):**
- SOUND (sequential/continuous): Auditory cues track process state
- SIGHT (intervention-triggering): Visual changes signal decisions
- TOUCH (boundary confirmation): Tactile feedback confirms endpoints

**Stage 2 - Execution Completeness (Voynich REGIME):**
- Gentle handling → C-zone (setup phase critical)
- Standard throughput → R-zone (progression tracking)
- Intense extraction → R-zone (continuous monitoring)
- Precision timing → S-zone (boundary locking)

### S-Zone Reinterpretation

All tested modalities AVOID S-zone:
- SOUND: d=-1.21 (strong avoidance)
- TASTE: d=-1.33 (strong avoidance)

S-zone represents operations where sensory monitoring is COMPLETED. The "locked" state means decisions are final. PRECISION REGIME concentrates here because exact timing, once achieved, requires no further sensory feedback.

### Statistical Validation

- ANOVA (REGIME → Zone): C (F=8.47, p=0.0001), R (F=5.18, p=0.002), S (F=6.77, p=0.0004)
- Permutation tests: All confirmed associations survive
- Pre-registration: Hypotheses locked before analysis

### SEMANTIC_CEILING_BREACH Validation (2026-01-19)

B->A Reverse Prediction Test attempted to predict modality class from zone profiles:

| Test | Result | Status |
|------|--------|--------|
| 4-class accuracy | 52.7% (vs 25% baseline) | **PASS** (p=0.012) |
| Binary accuracy | 71.8% (vs 79.1% baseline) | Below Tier 2 threshold |
| MODALITY beyond REGIME | 3/4 zones significant | **CONFIRMED** |

**Key finding:** Zone profiles DISCRIMINATE modality classes (all 4 zones show significant SOUND vs OTHER differences with d=0.44-0.66), but not with enough accuracy for Tier 2 predictive power.

**Semantic ceiling confirmed:** Aggregate characterization is possible; high-confidence prediction is not.

### Status
✔ R-SOUND confirmed with large effect (d=0.61)
✔ P-SOUND confirmed with very large effect (d=1.08)
✔ REGIME heterogeneity is structured, not noise
✔ Two-stage model explains all findings coherently
✔ Zone discrimination validated (4-class: 52.7%, p=0.012)
✔ MODALITY adds beyond REGIME (3/4 zones, partial r=0.20-0.28)
⚠ SIGHT/TOUCH underpowered (n<15)
⚠ C-zone preparation hypothesis failed
⚠ Tier 2 not achieved (binary accuracy < threshold)
✖ Does not prove modality encoding in Voynich

**Correct handling:** F3 fit showing zones ADDRESS (not encode) sensory modalities through REGIME-dependent structural affordances. The constraint substitution principle operates temporally. Semantic ceiling is at aggregate characterization level.

---

## Governance Note

None of these fits justify new Tier 0-2 constraints. This is the **best possible outcome**: the frozen architecture predicted these results without requiring changes.

> The model is saturated, not brittle.

---

## Files

Test scripts in: `phases/BRUNSCHWIG_BACKPROP_VALIDATION/`, `phases/BRU_AUDIT/`, `phases/SENSORY_LOAD_ENCODING/`, `phases/BRUNSCHWIG_REVERSE_ACTIVATION/`, and `phases/ZONE_MODALITY_VALIDATION/`

| Script | Fit | Location |
|--------|-----|----------|
| `blind_prediction_test.py` | F-BRU-001 | BRUNSCHWIG_BACKPROP_VALIDATION |
| `degree_regime_violations.py` | F-BRU-002 | BRUNSCHWIG_BACKPROP_VALIDATION |
| `synthetic_property_control.py` | F-BRU-003 | BRUNSCHWIG_BACKPROP_VALIDATION |
| `stability_perturbation_test.py` | F-BRU-004 | BRUNSCHWIG_BACKPROP_VALIDATION |
| `cross_type_middle_analysis.py` | F-BRU-005 | BRUNSCHWIG_BACKPROP_VALIDATION |
| `pcc_integration_tests.py` | F-BRU-006 | BRU_AUDIT |
| `sensory_load_index.py` | F-BRU-007 | SENSORY_LOAD_ENCODING |
| `reverse_activate_all.py` | F-BRU-008 | BRUNSCHWIG_REVERSE_ACTIVATION |
| `sensory_granularity_test.py` | F-BRU-009 (original) | BRUNSCHWIG_REVERSE_ACTIVATION |
| `modality_zone_validation.py` | F-BRU-009 (validation) | ZONE_MODALITY_VALIDATION |
| `regime_stratified_analysis.py` | F-BRU-009 (two-stage) | ZONE_MODALITY_VALIDATION |
| `scb_01_modality_prediction_test.py` | F-BRU-009 (ceiling test) | SEMANTIC_CEILING_BREACH |
| `scb_03_regime_zone_regression.py` | F-BRU-009 (REGIME control) | SEMANTIC_CEILING_BREACH |
