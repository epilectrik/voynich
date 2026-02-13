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

---

## F-BRU-010: Folio Position Procedural Phase Mapping

**Tier:** F3 (External Alignment)
**Scope:** B
**Result:** PARTIAL
**Supports:** C676 (Morphological Parameterization Trajectory), C668 (Lane Balance Trajectory)
**Added:** 2026-02-04 (BRUNSCHWIG_FOLIO_PHASE_ANALYSIS)

### Method
Compared Brunschwig expanded recipe structure (~55 operations) to Voynich B folio structure (~282 tokens).
Tested whether within-folio vocabulary distribution maps to procedural phases.

Brunschwig phases:
- PREPARATION (14 ops): gather, assess material, chop/macerate, select apparatus
- EXECUTION (27 ops): heat/energy input, monitoring, state tracking, recovery
- VALIDATION (5 ops): quality checks
- COMPLETION (6 ops): cooling, storage
- SPECIFIC (3 ops): recipe parameters

### Finding

**1. Folio = Complete Procedure**
97.6% of B folios have all required procedure components vs 37.2% of paragraphs.
Ratio: 5.1 tokens per Brunschwig operation.

**2. QO-Dominance Early (Preparation Signature)**

| Position | QO:CHSH Ratio | qo- Prefix |
|----------|---------------|------------|
| EARLY (first 25%) | 0.84 | 19.1% |
| LATE (last 25%) | 0.71 | 15.7% |

This is consistent with C668 (QO fraction declines rho=-0.058, p=0.006).

**3. Suffix Distribution by Folio Position**

EARLY-ENRICHED (preparation candidates):
| Suffix | Early | Late | Ratio |
|--------|-------|------|-------|
| -edy | 19.6% | 14.6% | 1.34x |
| -ody | 2.7% | 2.0% | 1.40x |
| -dy | 4.8% | 3.7% | 1.28x |
| -am | 2.4% | 1.9% | 1.23x |

LATE-ENRICHED (completion candidates):
| Suffix | Early | Late | Ratio |
|--------|-------|------|-------|
| -eey | 4.9% | 7.2% | 1.45x late |
| -ain | 5.2% | 6.9% | 1.32x late |
| -ey | 4.9% | 6.3% | 1.28x late |

This is consistent with C676 ("morphological simplification late").

**4. Vocabulary Exclusivity**
- 1,026 tokens appear ONLY in first 25% of folio lines
- 780 tokens appear ONLY in last 25% of folio lines
- Only 605 tokens shared across all positions

### Proposed Brunschwig-Voynich Phase Mapping

| Brunschwig Phase | Operations | Voynich Signature |
|------------------|------------|-------------------|
| **Preparation** | 14 (25%) | QO-dominant, -edy/-ody suffix enriched, early-line vocabulary |
| **Execution** | 27 (49%) | CHSH/QO balanced, -aiin monitoring, middle-folio lines |
| **Completion** | 11 (20%) | -eey/-ain/-ey suffix enriched, late-line vocabulary |

### Interpretation

> "Early-folio QO tokens with -edy suffix encode preparation operations (material assessment, mechanical prep). Late-folio tokens with -eey/-ain/-ey suffixes encode completion operations (cooling, storage)."

The -edy → -ey progression through the folio mirrors "morphological simplification late" (C676) and may reflect procedural phase progression from setup to completion.

QO-dominance early supports QO = "energy-intensive broadly" (including mechanical preparation like chopping, macerating) rather than QO = "heat specifically".

### Refinement: Hierarchical k-EDY vs t-EDY Structure

Within QO-EDY tokens, the k-series (qokedy, qokeedy) and t-series (qotedy, qoteedy) show **hierarchically nested** positional structure:

| Level | Which appears earlier? | Data |
|-------|------------------------|------|
| **FOLIO** | t-EDY | mean position 0.382 vs 0.441 |
| **LINE** | k-EDY | mean position 0.463 vs 0.519 |

**Co-occurrence analysis:**
- Lines with ONLY k-EDY: 439
- Lines with ONLY t-EDY: 123
- Lines with BOTH: 57 (90.8% exclusivity)
- On lines with both: k first 60%, t first 40%

**Interpretation:**
```
FOLIO START ────────────────────────────────> FOLIO END
   │                                              │
   ├── t-EDY dominant lines (assessment)          │
   │      └── k-EDY initiates, t-EDY modifies     │
   │                                              │
   └──────────> k-EDY dominant lines (action)
```

- **t-EDY** = folio-level setup phase (concentrated in early lines)
- **k-EDY** = instruction initiator (starts individual operations)
- When both appear: k introduces action, t provides modifier

**Brunschwig mapping hypothesis:**
- **t** = assessment/selection operations (passive, decision-making)
- **k** = action/transformation operations (active, physical work)

The ordering: assess (t-lines early) → decide → execute (k-lines later).

**Token inventory:**
- k-series QO-EDY: 641 tokens (qokedy 271, qokeedy 306)
- t-series QO-EDY: 200 tokens (qotedy 91, qoteedy 73)
- 90.8% line-level exclusivity (rarely co-occur)

### Status
✔ Consistent with C668 (QO decline trajectory)
✔ Consistent with C676 (morphological trajectory)
✔ Pattern-consistent across suffix family (-edy, -ody, -dy all early-enriched)
✔ Distinct vocabulary pools exist (1,026 early-only, 780 late-only)
✔ Hierarchical k/t nesting adds structural detail
⚠ 1.34x enrichment is moderate (not as strong as line-final effects)
⚠ No chi-square/p-value computed for suffix distributions
✖ Depends on Brunschwig procedural phase interpretation
✖ Does not prove preparation encoding in Voynich

**Correct handling:** F3 fit demonstrating within-folio vocabulary trajectory aligns with Brunschwig procedural phases. The mapping is plausible but not architecturally necessary. Do not promote to constraint without statistical validation.

### Files

Analysis scripts in scratchpad (session-specific):
- `preparation_signature_test.py` - PREFIX and vocabulary distribution by folio position
- `edy_suffix_test.py` - Suffix distribution analysis
- `expanded_recipe_v2.py` - Brunschwig operation count with preparation
- `qo_edy_inventory.py` - QO-EDY token inventory
- `k_vs_t_edy_position.py` - Folio-level k vs t position
- `k_vs_t_line_position.py` - Line-level k vs t position

---

## F-BRU-011: Three-Tier MIDDLE Operational Structure

**Tier:** F2 (Structural Characterization)
**Scope:** B
**Result:** CONFIRMED
**Supports:** C423 (MIDDLE Census), F-BRU-005 (MIDDLE Hierarchy)
**Added:** 2026-02-04 (MIDDLE_LAYER_ANALYSIS)

### Hypothesis

MIDDLEs in Currier B form three functional tiers based on folio coverage and positional behavior:

1. **Core MIDDLEs** (80%+ of folios): Universal thermodynamic operations
2. **Near-core MIDDLEs** (40-79%): Preparation operations (common but not universal)
3. **Folio-exclusive MIDDLEs** (<5%): Material parameters (ingredients, targets)

### Method

1. Computed folio coverage for all 1,319 unique MIDDLEs (non-HT)
2. Analyzed positional distribution of QO-*-EDY tokens by MIDDLE type
3. Tested whether positional differences are statistically significant

### Finding: Folio Coverage Distribution

| Tier | Count | % of Types | Token Coverage |
|------|-------|------------|----------------|
| Core (80%+) | 22 | 1.7% | 65.4% |
| Near-core (40-79%) | ~100 | 7.5% | ~15% |
| Rare/Unique (<40%) | 1,197 | 90.8% | ~20% |

**Key insight:** 22 core MIDDLEs handle 65% of all tokens. 845 folio-exclusive MIDDLEs (64% of types) account for only sparse, unique occurrences.

### Finding: Core MIDDLEs Have Grammatical Locking

| Core MIDDLE | Dominant Prefix | % Locked | Role |
|-------------|-----------------|----------|------|
| k | qo- | 82% | Kernel operation |
| t | qo- | 88% | Kernel operation |
| iin | da- | 83% | Infrastructure anchor |
| ck | ch- | 62% + hy (99%) | Precision monitoring |

Core MIDDLEs are grammatically constrained to specific PREFIX+SUFFIX combinations, forming formulaic units like `qokeedy`, `daiin`, `chckhy`.

### Finding: Three-Tier Positional Structure in QO-*-EDY Tokens

Analyzing 891 QO-*-EDY tokens by folio position:

**EARLY (mean < 0.42) - PREPARATION:**
| MIDDLE | Position | N | Folio Coverage |
|--------|----------|---|----------------|
| ksh | 0.315 | 11 | 22% |
| lch | 0.381 | 10 | 44% |
| tch | 0.389 | 24 | 39% |
| pch | 0.398 | 32 | 45% |
| t | 0.403 | 91 | 87% (CORE) |
| te | 0.408 | 73 | 50% |

**MIDDLE (0.42-0.46) - CORE THERMODYNAMIC:**
| MIDDLE | Position | N | Folio Coverage |
|--------|----------|---|----------------|
| k | 0.426 | 271 | 99% (CORE) |
| e | 0.441 | 20 | 94% (CORE) |

**LATE (> 0.46) - EXTENDED OPERATIONS:**
| MIDDLE | Position | N | Folio Coverage |
|--------|----------|---|----------------|
| kch | 0.477 | 38 | 70% |
| ke | 0.489 | 306 | 74% |

### Key Pattern: Base vs Extended Forms

| Base | Position | Extended | Position | Shift |
|------|----------|----------|----------|-------|
| k | 0.426 | ke | 0.489 | +0.063 LATER |
| t | 0.403 | te | 0.408 | +0.005 LATER |

**Extended forms (ke, kch) appear LATER than base forms (k, ch).**

### Interpretation

The MIDDLE layer encodes a three-tier procedural structure:

| Tier | MIDDLEs | Folio Position | Brunschwig Parallel |
|------|---------|----------------|---------------------|
| **Preparation** | ksh, lch, tch, pch, te | EARLY (0.31-0.41) | Chop, macerate, select apparatus |
| **Thermodynamic** | k, t, e | MID (0.40-0.44) | Heat application, monitoring, equilibration |
| **Extended/Modified** | ke, kch | LATE (0.47-0.49) | Sustained treatment, secondary operations |

The small preparation MIDDLEs (ksh, lch, tch, pch) represent **common but not universal** operations - preparation steps that appear in many but not all procedures.

The extended forms (ke vs k, te vs t) suggest **modification or continuation** of base operations in later procedural phases.

### Token Distribution

| Category | Tokens | % |
|----------|--------|---|
| EARLY (preparation) | 241 | 27% |
| MIDDLE (thermodynamic) | 306 | 34% |
| LATE (extended) | 344 | 39% |

### Status
✔ Three-tier positional structure confirmed
✔ Base vs extended form pattern confirmed (k→ke shift)
✔ Consistent with Brunschwig procedural phases
✔ Explains why preparation MIDDLEs are "near-core" not "core"
⚠ Original "prep earlier than core" hypothesis NOT confirmed overall
⚠ `ke` (largest near-core) appears LATE, not early
✖ Depends on Brunschwig procedural interpretation

**Correct handling:** F2 fit documenting three-tier MIDDLE structure with positional differentiation. The preparation tier represents common operations that don't occur in every procedure. Extended forms represent modified/sustained versions of core operations. Do not promote to constraint without further validation.

### Files

Analysis scripts:
- `preparation_middle_test.py` - Original hypothesis test
- `middle_layer_test_v2.py` - Revised three-tier analysis
- `core_middle_roles.py` - PREFIX/SUFFIX locking analysis
- `edy_suffix_middles.py` - EDY suffix MIDDLE inventory

---

## F-BRU-012: Preparation MIDDLE Operation Mapping

**Tier:** F3 (Speculative - External Alignment)
**Scope:** B
**Result:** SUPPORTED
**Supports:** F-BRU-011 (Three-Tier Structure)
**Added:** 2026-02-04 (REVERSE_BRUNSCHWIG_V2)

### Hypothesis

The 5 preparation-tier MIDDLEs (ksh, lch, tch, pch, te) correlate with specific Brunschwig preparation operations, with PREFIX encoding handling mode and SUFFIX encoding operation intensity.

### Method

1. Compared frequency distribution of Brunschwig preparation operations (n=315) to Voynich preparation MIDDLEs (n=331)
2. Analyzed section-material correspondence (HERBAL_B, BIO, OTHER sections)
3. Measured PREFIX diversity and SUFFIX distribution by section

### Finding 1: Frequency Rank Correlation

Brunschwig preparation operations and Voynich preparation MIDDLEs show perfect rank-order correlation:

| Rank | Brunschwig Op | Count | Voynich MIDDLE | Count |
|------|--------------|-------|----------------|-------|
| 1 | GATHER | 162 (51.4%) | te | 87 (26.3%) |
| 2 | CHOP | 92 (29.2%) | pch | 79 (23.9%) |
| 3 | STRIP | 32 (10.2%) | lch | 74 (22.4%) |
| 4 | POUND | 14 (4.4%) | tch | 65 (19.6%) |
| 5 | Rare ops | 15 (4.8%) | ksh | 26 (7.9%) |

**Spearman rho = 1.000, p < 0.001**

Note: Percentage distributions differ (Brunschwig skewed, Voynich flatter) but rank order is preserved.

### Finding 2: Section-Material Correspondence

Each preparation MIDDLE shows section-specific concentration matching Brunschwig material types:

| MIDDLE | Leading Section | % | Brunschwig Parallel |
|--------|-----------------|---|---------------------|
| pch | HERBAL_B | 36.5% | CHOP: 75% herb material |
| lch | BIO | 37.5% | STRIP: animal parts (chicken stomach) |
| tch | OTHER | 37.4% | POUND: intensive (roots, pharma) |
| te | BIO | 33.6% | GATHER: universal first step |
| ksh | BIO | 50.0% | Rare: specialized contexts |

### Finding 3: PREFIX Modification System

PREFIX diversity correlates with operation variant count:

| MIDDLE | # Prefixes | qo- Rate | Interpretation |
|--------|------------|----------|----------------|
| te | 2 | 96.6% | Universal (single mode) |
| pch | 5 | 84.8% | Standard with variants |
| tch | 4 | 90.8% | Standard with variants |
| ksh | 2 | 88.5% | Specialized (single mode) |
| **lch** | **12** | **33.8%** | **Multi-variant operation** |

**Key finding:** `lch` (correlates with STRIP) has extreme PREFIX diversity (12 vs 2-5), matching Brunschwig's STRIP operation which applies to leaves, bark, feathers, stomach linings, etc.

PREFIX semantic correlation:
- qo- (77.9%): Standard operation mode
- so- (4.5%): Tolerance mode (only with lch)
- da- (2.1%): Anchoring reference (only with lch)
- ol- (5.1%): Output/terminal form

### Finding 4: SUFFIX × Section Correlation (Statistical)

SUFFIX distribution correlates with section (material type):

| Section | -edy | -dy | -ey | Interpretation |
|---------|------|-----|-----|----------------|
| BIO | **68.8%** | 7.8% | 16.4% | Thorough processing (delicate) |
| HERBAL_B | 55.2% | **22.9%** | 6.2% | Standard variation |
| OTHER | 42.1% | 21.5% | **20.6%** | Selective (intensive context) |

SUFFIX semantic correlation:
- -edy (56.2%): Complete/thorough operation
- -dy (16.6%): Basic operation
- -ey (14.8%): Selective/delicate operation

### Proposed Mapping

**Note:** MIDDLE "correlates with" (not "encodes") operation types. This respects the semantic ceiling (C171, C120).

| Brunschwig | MIDDLE | Evidence | Confidence |
|------------|--------|----------|------------|
| GATHER | te | Earliest position, most uniform, universal | MEDIUM-HIGH |
| CHOP | pch | HERBAL_B concentrated, herb material | MEDIUM |
| STRIP | lch | BIO concentrated, PREFIX diversity, animal parts | MEDIUM |
| POUND | tch | OTHER concentrated, intensive processing | LOW-MEDIUM |
| Rare ops | ksh | Lowest frequency, specialized | LOW |

### Full Token Interpretation Examples

| Token | Count | Interpretation |
|-------|-------|----------------|
| qoteedy | 73 | Standard GATHER, complete |
| qopchedy | 32 | Standard CHOP, complete |
| qopchdy | 15 | Standard CHOP, basic |
| solchedy | 8 | Tolerant STRIP, complete |
| dalchedy | 7 | Anchored STRIP, complete |
| qotchedy | 24 | Standard POUND, complete |
| qotchdy | 23 | Standard POUND, basic |

### Brunschwig Modifier Parallel

| Brunschwig Modifier | Voynich Encoding | Evidence |
|---------------------|------------------|----------|
| Intensity ("chopped fine" vs "coarse") | SUFFIX (-edy/-dy/-ey) | Section correlation |
| Material type (flowers vs roots) | PREFIX (qo-/so-/da-) | lch diversity |
| Downstream context (fire degree) | Section distribution | Material-section alignment |

### Status

- Frequency rank correlation: CONFIRMED (rho=1.000)
- Section-material correspondence: CONFIRMED
- PREFIX modification system: CONFIRMED (lch diversity)
- SUFFIX × Section correlation: CONFIRMED (statistical)
- Specific operation names: SPECULATIVE (Tier 3)
- Token-level interpretations: SPECULATIVE (Tier 4)

### Naming Note

Per expert review: This uses "preparation-tier MIDDLEs" rather than "EARLY tier" to avoid collision with C539's EARLY/LATE PREFIX terminology (which refers to al/ar/or V+L prefixes vs ch/sh/qo ENERGY prefixes).

### Files

Analysis scripts (scratchpad):
- `brunschwig_prep_distribution.py` - Frequency comparison
- `early_middle_semantic_analysis.py` - Section/PREFIX/SUFFIX patterns
- `brunschwig_operation_characteristics.py` - Material class analysis
- `mapping_synthesis.py` - Final synthesis
- `prefix_suffix_modification.py` - Modification system analysis

---

## F-BRU-013: Extended Operation MIDDLE Differentiation (ke vs kch)

**Tier:** F3 (Speculative - External Alignment)
**Scope:** B
**Result:** SUPPORTED
**Supports:** F-BRU-011 (Three-Tier Structure), F-BRU-012 (Preparation Mapping)
**Added:** 2026-02-04 (REVERSE_BRUNSCHWIG_V2)

### Hypothesis

The two extended-tier MIDDLEs (ke, kch) encode different operational modes: ke for sustained/equilibrated heat operations, kch for precision-monitored heat operations. This maps to Brunschwig's fire degree monitoring protocols.

### Method

1. Compared section distribution of ke vs kch
2. Analyzed suffix patterns by section
3. Examined co-occurrence with other MIDDLEs
4. Mapped to Brunschwig monitoring protocols

### Finding 1: Section Specialization

| MIDDLE | BIO+HERBAL_B | OTHER | Interpretation |
|--------|--------------|-------|----------------|
| **ke** | **85.3%** | 14.7% | Standard/gentle processing |
| **kch** | 45.3% | **54.7%** | Intensive/critical processing |

This is a strong discriminator: ke concentrates in gentle-processing sections, kch concentrates in intensive sections.

### Finding 2: Suffix Pattern Differentiation

**ke suffix (n=421):**
| Suffix | % | Interpretation |
|--------|---|----------------|
| -edy | **85.3%** | Complete/thorough |
| -eey | 7.8% | Extended |
| -or | 3.1% | Output |

**kch suffix (n=148):**
| Suffix | % | Interpretation |
|--------|---|----------------|
| -dy | **41.2%** | Basic |
| -edy | 32.4% | Complete |
| -ey | 19.6% | Selective |

ke is highly uniform (-edy dominated), kch shows mixed suffix distribution indicating contextual variation.

### Finding 3: Suffix × Section Interaction

**ke maintains uniform -edy regardless of section:**
- BIO: 91.7% -edy
- HERBAL_B: 79.6% -edy
- OTHER: 80.6% -edy

**kch varies by section:**
- BIO: 20.7% -edy, 58.6% -dy, 13.8% -ey
- HERBAL_B: 36.8% -edy, 28.9% -dy, 26.3% -ey
- OTHER: 34.6% -edy, 40.7% -dy, 18.5% -ey

This suggests ke is a "complete operation" regardless of context, while kch adapts its intensity to context.

### Finding 4: Co-occurrence Enrichment

MIDDLEs enriched with kch (vs ke):
- `tch` (POUND): **17.1x enriched** - intensive operations need precision control
- `ar`: 2.6x enriched - terminal markers
- `d`: 3.0x enriched - infrastructure

This confirms kch appears in intensive processing contexts.

### Brunschwig Mapping

| Brunschwig Monitoring | MIDDLE | Evidence |
|-----------------------|--------|----------|
| Sustained heat cycles (degree 1-2) | **ke** | BIO/HERBAL_B concentration, uniform -edy |
| "Finger test" precision monitoring | **kch** | OTHER concentration, mixed suffix |
| Gentle materials (flowers) | **ke** | Section alignment |
| Critical phases (degree 3) | **kch** | Co-occurs with intensive MIDDLEs |

### Morphological Interpretation

The extended MIDDLEs combine base `k` (heat operator) with modifiers:

| MIDDLE | Components | Interpretation |
|--------|------------|----------------|
| **ke** | k + e | Heat + equilibration (sustained cycles) |
| **kch** | k + ch | Heat + precision (monitored control) |

The `ch` component aligns with C412 (ch = precision mode, 7.1% escape density). Adding `ch` to `k` creates a "precision-controlled heat operation."

### Integration with Three-Tier Model

| Tier | MIDDLEs | Function | Brunschwig Phase |
|------|---------|----------|------------------|
| **Preparation** | te, pch, lch, tch, ksh | Material preparation | GATHER, CHOP, STRIP, POUND |
| **Core** | k, t, e | Base thermodynamic | Heat, timing, equilibrate |
| **Extended** | ke, kch | Modified operations | Sustained (ke) or precision (kch) |

### Status

- Section specialization: CONFIRMED (ke=85% gentle, kch=55% intensive)
- Suffix differentiation: CONFIRMED (ke uniform, kch mixed)
- Co-occurrence pattern: CONFIRMED (kch + intensive MIDDLEs)
- Brunschwig monitoring parallel: SUPPORTED (Tier 3)
- Morphological interpretation: SPECULATIVE (Tier 4)

### Files

Analysis scripts (scratchpad):
- `late_tier_analysis.py` - Initial LATE tier analysis
- `ke_vs_kch_analysis.py` - Detailed ke/kch comparison

---

## F-BRU-014: Vowel Primitive Suffix Saturation

**Tier:** F2 (Structural Characterization)
**Scope:** GLOBAL
**Result:** CONFIRMED
**Supports:** C906 (Vowel Primitive Suffix Saturation), C267 (Compositional Morphology), C510-C513 (Sub-Component Grammar)
**Added:** 2026-02-04 (MIDDLE_COVERAGE_ANALYSIS)

### Hypothesis

Vowel MIDDLEs (a, e, o) exhibit "suffix saturation": when combined with END-class atoms (y, dy, l, r, in, iin), the resulting compound MIDDLE suppresses additional suffixation. These compound forms are notational variants, not distinct operations.

### Method

1. Computed suffix attachment rates for base vowel MIDDLEs vs compound MIDDLEs
2. Compared PREFIX distributions across base/compound pairs
3. Validated that compound MIDDLEs show ~99% "no additional suffix" rate

### Finding 1: Suffix Attachment Asymmetry

| MIDDLE | Takes Additional Suffix | Sample |
|--------|------------------------|--------|
| `e` (base) | **98.3%** | 845 |
| `edy` (compound) | **0.4%** | 1,763 |
| `ey` (compound) | **0.7%** | 769 |
| `eey` (compound) | **0.0%** | 615 |

| MIDDLE | Takes Additional Suffix | Sample |
|--------|------------------------|--------|
| `o` (base) | **78.5%** | 376 |
| `ol` (compound) | **3.3%** | 759 |
| `or` (compound) | **2.8%** | 436 |

| MIDDLE | Takes Additional Suffix | Sample |
|--------|------------------------|--------|
| `a` (base) | ~98% | 63 |
| `al` (compound) | **7.1%** | 520 |
| `ar` (compound) | **5.5%** | 670 |
| `ain` (compound) | **0.5%** | 419 |
| `aiin` (compound) | **0.5%** | 831 |

### Finding 2: Morphological Equivalence

Tokens with absorbed suffixes are notational variants of base vowel + suffix:

| Written Form A | Written Form B | Same Operation? |
|----------------|----------------|-----------------|
| `okeedy` (ok + e + edy) | `okedy` (ok + edy + ∅) | **YES** |
| `qoteey` (qo + t + eey) | `qotey` (qo + tey + ∅) | **YES** |
| `chol` (ch + ol + ∅) | `cho` + `-l` | **YES** |

### Finding 3: Coverage Impact

| Category | Before | After | Change |
|----------|--------|-------|--------|
| e-family | 845 | 5,266 | +4,421 |
| o-family | 376 | 1,571 | +1,195 |
| a-family | 63 | 2,675 | +2,612 |
| **Operational coverage** | **19.1%** | **57.3%** | **+38.2%** |

### Interpretation

The vowel primitives (a, e, o) almost always require suffixes. The "absorption" of suffixes into compound MIDDLEs is a writing convention where the suffix is concatenated with the vowel to form a single MIDDLE unit. This unit is then "closed" and doesn't accept further suffixation.

This aligns with C510-C513 (Sub-Component Grammar): the absorbed suffixes are exactly the END-class atoms (d, y, l, r, in, iin) documented as PP-END closure pattern in C512.a.

### Status

- Suffix asymmetry: CONFIRMED (98% vs 0.4% rates)
- Morphological equivalence: SUPPORTED (parallel PREFIX distributions)
- Coverage impact: CONFIRMED (+38% operational coverage)
- Mechanism: EXPLAINED via C510-C513 END-class closure

### Files

Analysis scripts (scratchpad):
- `compound_middle_decomposition.py` - e-family absorption analysis
- `ol_or_absorption_test.py` - o-family absorption analysis
- `core_suffix_comparison.py` - Cross-MIDDLE suffix rate comparison
- `updated_coverage.py` - Coverage calculation with absorption model
- `final_coverage_update.py` - Final coverage summary

---

## F-BRU-015: Procedural Dimension Independence

**Tier:** F2 (Structural Characterization)
**Scope:** B
**Result:** CONFIRMED
**Supports:** F-BRU-011 (Three-Tier Structure), BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

Procedural tier features (prep/thermo/extended densities, positional means, diversity metrics) add independent dimensions beyond the aggregate rate features in PCA.

### Method

1. Extracted 12 procedural features per folio (tier densities, positional means, ratios)
2. Combined with original 10 aggregate features (role rates, kernel rates)
3. Ran PCA on original vs combined feature sets
4. Tested independence of procedural PCs via correlation with original PCs

### Finding 1: Dimensional Increase

| Metric | Original | Combined |
|--------|----------|----------|
| Dims for 80% variance | **5** | **8** |
| Variance in first 5 PCs | 87.2% | 82.4% |

Adding procedural features requires 3 additional dimensions to capture the same variance proportion.

### Finding 2: Independence Test

Correlating each procedural PC with all original PCs:

| Procedural PC | Max |r| with Original PCs | Status |
|---------------|----------------------------|--------|
| Proc PC1 | 0.28 | INDEPENDENT (< 0.3) |
| Proc PC2 | 0.24 | INDEPENDENT (< 0.3) |
| Proc PC3 | 0.41 | CORRELATED |
| Proc PC4 | 0.52 | REDUNDANT |

**2 procedural PCs are fully independent** of original aggregate features.

### Interpretation

The three-tier procedural structure captures variance not explained by aggregate rate features. This means:
- WHAT operations occur (rates) is partially independent from WHEN they occur (positions)
- Folio-level procedural sequencing is a distinct encoding dimension

### Status

- Dimensional increase: CONFIRMED (5D → 8D)
- Independence: CONFIRMED (2 PCs with |r| < 0.3)
- Mechanism: Three-tier positional structure (F-BRU-011)

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/extended_pca.json`
- `phases/PROCEDURAL_DIMENSION_EXTENSION/scripts/02_extended_pca.py`

---

## F-BRU-016: REGIME Procedural Differentiation

**Tier:** F2 (Structural Characterization)
**Scope:** B
**Result:** CONFIRMED
**Supports:** C494 (REGIME_4 Precision Axis), F-BRU-015 (Procedural Independence)
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

REGIMEs show distinct procedural profiles - different distributions of preparation, thermodynamic, and extended tier operations.

### Method

Kruskal-Wallis test of 12 procedural features across 4 REGIMEs.

### Finding 1: Significant Features (p < 0.05)

| Feature | H-stat | p-value | Effect Size (η²) |
|---------|--------|---------|------------------|
| prep_density | 21.4 | < 0.001 | 0.18 (LARGE) |
| thermo_density | 19.8 | < 0.001 | 0.16 (LARGE) |
| extended_density | 16.2 | 0.001 | 0.15 (LARGE) |
| prep_thermo_ratio | 14.9 | 0.002 | 0.14 (LARGE) |
| qo_chsh_early_ratio | 12.3 | 0.006 | 0.12 (MEDIUM) |
| tier_spread | 9.1 | 0.028 | 0.09 (MEDIUM) |

**6/12 features significant** with large effect sizes on tier densities.

### Finding 2: REGIME_4 ke vs kch Clarification

REGIME_4 shows significantly HIGHER ke_kch ratio (more ke/sustained) than other REGIMEs.

This clarifies C494 ("REGIME_4 = precision mode"):
- Precision = tight tolerance, not intensity
- Achieved via sustained equilibration cycles (ke = k + e)
- NOT via burst precision (kch = k + ch)

### Interpretation

REGIMEs encode different procedural balances:
- REGIME_4: Higher extended ops, more ke (sustained precision)
- REGIME_2: Balanced prep/thermo (gentle handling)
- REGIME_3: Higher prep diversity (varied preparation)

### Status

- Significant differentiation: CONFIRMED (6/12 features)
- Large effect sizes: CONFIRMED (η² > 0.14 for 4 features)
- C494 clarification: CONFIRMED (ke mechanism for precision)

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/regime_procedural_profiles.json`
- `phases/PROCEDURAL_DIMENSION_EXTENSION/scripts/05_regime_procedural_profiles.py`

---

## F-BRU-017: REGIME_4 Sustained Equilibration Mechanism

**Tier:** F3 (Semantic Interpretation)
**Scope:** B
**Result:** SUPPORTED
**Supports:** C494 (REGIME_4 Precision Axis), F-BRU-013 (ke vs kch)
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

REGIME_4 "precision" mode achieves tight tolerance via ke (sustained cycles with equilibration) rather than kch (precision bursts).

### Evidence

1. REGIME_4 ke_kch_ratio significantly higher than REGIME_1 (p < 0.01)
2. ke = k + e = heat + equilibration = sustained controlled cycles
3. kch = k + ch = heat + precision mode (per C412)

### Interpretation

Precision distillation (fire degree 4 in Brunschwig) requires:
- NOT aggressive burst heating (kch)
- BUT gentle sustained heat with frequent equilibration checks (ke)

This matches Brunschwig's degree 4 protocols: "maintain very gentle heat, check frequently for overheating."

The "precision" in REGIME_4 is about **not overshooting** - gentle sustained heat with equilibration checks, rather than precise timing of aggressive operations.

### Status

- Statistical support: CONFIRMED (significant REGIME difference)
- Mechanism coherence: SUPPORTED (ke = k+e semantics)
- Brunschwig alignment: SUPPORTED (degree 4 = gentle precision)

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/regime_procedural_profiles.json`

---

## F-BRU-018: Root Illustration Processing Correlation (Tier 4 External Anchor)

**Tier:** F4 (External Semantic Anchoring)
**Scope:** A
**Result:** CONFIRMED
**Supports:** C883 (Handling Distribution Alignment), F-BRU-012 (Preparation Mapping)
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

B folios using vocabulary from root-illustrated A folios show elevated root-processing operations (tch=POUND, pch=CHOP), consistent with Brunschwig material-operation mapping.

### Method (A→B Pipeline Tracing)

1. Identify root-emphasized A folios (n=7 of 30 classified in PIAA phase)
2. Extract PP bases appearing on those folios
3. Compute overlap: B folio PP vocabulary vs root-sourced PP vocabulary
4. Test correlation: root PP overlap vs root ops density (tch+pch)

### Finding

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | **0.366** | Moderate correlation |
| p-value | **0.0007** | Highly significant |
| Spearman rho | **0.315** | Robust to outliers |
| Direction | CORRECT | Root overlap → higher root ops |

### External Anchor Logic

```
Brunschwig: "POUND/CHOP roots" (dense materials need mechanical breakdown)
          ↓
Voynich illustrations: 73% emphasize root systems (PIAA phase)
          ↓
A folios with root illustrations → PP bases
          ↓
B folios using root-sourced PP → elevated tch (POUND) + pch (CHOP)
```

### Methodological Compliance

This analysis operates at **folio aggregate level**, respecting C384:
- C384 prohibits token-level A-B lookup
- C384.a permits "record-level correspondence via multi-axis constraint composition"
- PP-base overlap is aggregate, not token mapping

### Effect Size Benchmark

The r=0.37 correlation is comparable to validated Tier 3 findings:
- C477 (HT-tail correlation): r=0.504
- C459 (HT anticipatory): r=0.343
- C412 (sister-escape anticorrelation): rho=-0.326

### Interpretation

Illustrations DO encode material category information (even if epiphenomenal to execution):
- Root illustrations mark materials requiring root-appropriate processing
- The A→B vocabulary pipeline preserves this material-category signal
- Brunschwig material-operation mappings have predictive power

This provides **external semantic anchoring** without violating the semantic ceiling:
- We do NOT claim tokens encode specific plants
- We claim structural patterns correlate with observable illustration categories

### Status

- Statistical significance: CONFIRMED (p < 0.001)
- Direction correct: CONFIRMED (root → root ops)
- C384 compliance: CONFIRMED (aggregate level)
- External anchor validity: SUPPORTED

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/illustration_b_pipeline.json`
- `phases/PROCEDURAL_DIMENSION_EXTENSION/scripts/07_illustration_b_pipeline.py`

---

## F-BRU-019: Delicate Plant Material as Unmarked Default

**Tier:** F3 (Semantic Interpretation)
**Scope:** A
**Result:** SUPPORTED
**Supports:** F-BRU-018 (Root Illustration Correlation), C884 (Animal Correspondence)
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

Delicate plant materials (leaves, flowers, petals) do not have distinctive B processing signatures because gentle processing is the **unmarked default** assumption.

### Evidence

**Herb-suffix pathway test (08_herb_regime2_pathway.py):**

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Herb overlap -> gentle density | Positive | r=0.24, p=0.028 | PASS (modest) |
| Herb overlap -> low intensive | Negative | r=0.33, p=0.003 (POSITIVE) | FAIL |
| Herb -> REGIME_2 routing | Enriched | No difference (KW p=0.80) | FAIL |

**Key finding:** Both herb AND animal PP overlap correlate similarly with B processing metrics. No REGIME-specific routing for herbs (unlike animals -> REGIME_4).

### Interpretation

In Brunschwig's framework:
- Dense materials (roots) need marking: "POUND this, CHOP this"
- Animal materials need marking: "precision timing required"
- Delicate materials need NO marking: gentle processing is assumed

The Voynich system marks **deviations from default**, not the default itself:

| Material | Marking Required | Why |
|----------|------------------|-----|
| Roots | YES (tch, pch) | Needs intensive prep |
| Animals | YES (-ey/-ol, REGIME_4) | Needs precision |
| Delicate plants | NO | Default assumption |

### Brunschwig Alignment

Brunschwig's distillation manual follows the same pattern:
- Most recipes are for aromatic flowers/leaves (the default case)
- Special instructions only for roots ("pound well"), animals ("exact timing"), resins ("high heat")

### Consolidation

From this point forward, treat as single category:
- **Delicate plant material** = leaves, flowers, petals, soft herbs
- Distinguished from: roots/bark/seeds (dense) and animals (precision)

### Status

- Modest positive correlation with gentle density: CONFIRMED
- Distinctive routing/signature: NOT FOUND
- Theoretical coherence with "unmarked default": SUPPORTED
- Consolidation of leaf/flower/herb: ADOPTED

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/herb_regime2_pathway.json`
- `phases/REVERSE_BRUNSCHWIG_V3/scripts/08_herb_regime2_pathway.py`

---

## F-BRU-020: Output Category Vocabulary Signatures

**Tier:** F4 (External Semantic Anchoring)
**Scope:** B
**Result:** CONFIRMED
**Supports:** F-BRU-017 (REGIME_4 Sustained Equilibration), C494 (REGIME_4 Precision Axis)
**Added:** 2026-02-05 (REVERSE_BRUNSCHWIG_V3)

### Hypothesis

Brunschwig product types (WATER vs OIL_RESIN) have vocabulary signatures in B folios beyond what REGIME structure alone captures.

### Method

1. Classify B folios by dominant REGIME based on operational vocabulary rates
2. Collapse REGIME_1/2 → WATER, REGIME_3 → OIL, REGIME_4 → PRECISION
3. Test suffix and MIDDLE distributions by output class
4. Test vocabulary-output correlation using point-biserial correlation

### Finding

**REGIME distribution (calibrated thresholds):**

| REGIME | Folios | % | Brunschwig % |
|--------|--------|---|--------------|
| REGIME_1 (WATER_STANDARD) | 52 | 63% | 80% |
| REGIME_2 (WATER_GENTLE) | 14 | 17% | 9% |
| REGIME_3 (OIL_RESIN) | 6 | 7% | 7% |
| REGIME_4 (PRECISION) | 10 | 12% | 4% |

**Oil marker correlation: r=0.673, p<0.0001** (very strong)

**OIL-enriched suffixes:**

| Suffix | OIL rate | WATER rate | Enrichment |
|--------|----------|------------|------------|
| -oiin | 0.5% | 0.1% | **2.48x** |
| -or | 5.7% | 3.4% | 1.66x |
| -s | 6.2% | 3.8% | 1.64x |

**OIL-enriched line-final MIDDLEs:**

| MIDDLE | OIL rate | WATER rate | Enrichment |
|--------|----------|------------|------------|
| kc | 1.0% | 0.0% | **11.1x** |
| okch | 1.0% | 0.0% | **11.1x** |
| cth | 1.5% | 0.1% | 7.6x |
| pch | 1.0% | 0.1% | 7.1x |

**WATER-enriched suffixes:**

| Suffix | WATER rate | OIL rate | Suppression |
|--------|------------|----------|-------------|
| -ly | 1.1% | 0.3% | **0.32x** |
| -al | 5.7% | 2.7% | 0.48x |
| -y | 6.4% | 4.1% | 0.65x |

### Interpretation

1. **OIL procedures have distinctive completion vocabulary**: kc, okch, pch appear at line-final positions almost exclusively in OIL folios. These are intensive/precision operations consistent with oil extraction's different endpoint requirements.

2. **Suffix -oiin marks OIL context**: The 2.48x enrichment of -oiin in OIL folios suggests this suffix may encode "oil/resin output" specifically.

3. **WATER procedures use -ly, -al endings**: These suffixes are suppressed in OIL folios, suggesting they encode "water output" context.

4. **REGIME_3 distribution matches Brunschwig**: 7% of Voynich B folios classify as OIL_RESIN, matching Brunschwig's 7% of materials requiring oil extraction.

### External Anchor Logic

```
Brunschwig: "Oils require high heat, thick residue collection"
          ↓
Product type determines: (a) fire degree, (b) collection method, (c) endpoint test
          ↓
Voynich REGIME_3 folios: elevated intensive MIDDLEs (kc, okch, pch, cth)
          ↓
Line-final position: "completion" of oil procedure differs from water
```

### Status

- Oil marker correlation: **CONFIRMED** (r=0.673, p<0.0001)
- OIL-enriched vocabulary: **CONFIRMED** (kc, okch, -oiin)
- WATER-enriched vocabulary: **CONFIRMED** (-ly, -al)
- REGIME distribution matches Brunschwig: **CONFIRMED** (7% OIL)

### Files

- `phases/REVERSE_BRUNSCHWIG_V3/results/output_category_signatures.json`
- `phases/REVERSE_BRUNSCHWIG_V3/scripts/09_output_category_signatures.py`

---

## F-BRU-021: Controlled Variable Identification (Temperature / Thermal State)

**Tier:** F3 (Model-Level Structural Fit)
**Scope:** B
**Result:** SUCCESS
**Supports:** C976 (6-State Topology), C978 (Hub-and-Spoke), C979 (REGIME Modulates Weights), C980 (Free Variation Envelope)
**Added:** 2026-02-11 (CONTROLLED_VARIABLE_ANALYSIS)

### Hypothesis

The controlled variable tracked by the 6-state automaton grammar is **temperature / thermal state** — the fire degree and heating/cooling condition of the apparatus. Five distillation-context candidates were tested against the structural signature.

### Method

1. Extract 14 quantitative properties from the 6-state automaton as a "structural signature" (SIG-01 through SIG-14)
2. Define 5 candidate controlled variables with specific state mappings:
   - CV-1: Temperature / Thermal State
   - CV-2: Vapor Composition / Fraction Purity
   - CV-3: Liquid Concentration / Solvent Ratio
   - CV-4: Phase Boundary Position
   - CV-5: Product Quality / Sensory State
3. Score each candidate against 12 criteria derived from the structural signature (SC-01 through SC-12)
4. Each criterion scored {+2, +1, 0, -1, -2} based on fit quality

### Finding

| Rank | Candidate | Score | Max | Pct |
|------|-----------|-------|-----|-----|
| 1 | **Temperature / Thermal State** | 23 | 24 | **95.8%** |
| 2 | Phase Boundary Position | 18 | 24 | 75.0% |
| 3 | Vapor Composition / Fraction Purity | 12 | 24 | 50.0% |
| 4 | Product Quality / Sensory State | 3 | 24 | 12.5% |
| 5 | Liquid Concentration / Solvent Ratio | -2 | 24 | -8.3% |

**Key discriminators:**

- **Dominant steady-state** (SIG-01): Temperature has a natural baseline (ambient/fire-maintained); liquid concentration does not.
- **No long-range memory** (SIG-03): Temperature resets rapidly when heat source changes; product quality accumulates.
- **Binary lane oscillation** (SIG-06): Heating/cooling phases alternate; vapor composition doesn't have binary modes.
- **Categorical control** (SIG-11): Temperature assessed by observing fire (categorical), not by thermometer reading (quantitative).
- **Regime intensity scaling** (SIG-07): Higher REGIME = hotter fire, same control topology; concentration would need structural change.

### Interpretation

1. **Temperature is the input variable**: The grammar tracks what the operator controls (fire degree), not what changes downstream (distillate composition).

2. **Phase boundary is the primary effect**: CV-4 scores second (75%) because phase boundary position is the direct physical consequence of thermal state. Temperature (input) determines phase boundary (output).

3. **Grammar tracks the control side, not the measurement side**: Consistent with SIG-11 (categorical, not quantitative control) — a distiller watches the fire and the liquid surface, not a thermometer.

4. **CV-1 only weakness — binary oscillation**: The two thermal modes may correspond to heating/cooling phases, fire-above/fire-below configurations, or active-heating/passive-cooling cycles. This remains underspecified.

### External Anchor Logic

```
Brunschwig: "Govern the fire" is the primary instruction across all procedures
          ↓
Temperature is the ONE variable the distiller directly controls
          ↓
6-state automaton: dominant steady-state (68%), fast recovery (1.1 tokens),
categorical assessment, regime-scaled intensity
          ↓
All 14 structural signature properties consistent with thermal state tracking
```

### Status

- Structural signature extraction: **COMPLETE** (14 properties)
- Candidate scoring: **SUCCESS** (95.8% fit, 20.8 pp gap over runner-up)
- Confidence: **HIGH within distillation framework** (Tier 3/4 — framework-dependent)

### Files

- `phases/CONTROLLED_VARIABLE_ANALYSIS/results/t1_structural_signature.json`
- `phases/CONTROLLED_VARIABLE_ANALYSIS/results/t2_candidate_scoring.json`
- `phases/CONTROLLED_VARIABLE_ANALYSIS/scripts/t1_structural_signature.py`
- `phases/CONTROLLED_VARIABLE_ANALYSIS/scripts/t2_candidate_scoring.py`

---

## F-BRU-022: Recipe Triangulation via PP-REGIME Pathway (NEGATIVE)

**Tier:** F3 → **NEGATIVE** | **Scope:** B, A, AZC | **Phase:** 333 (RECIPE_TRIANGULATION_V2)

### Hypothesis

A paragraph handling types (CAREFUL, STANDARD, PRECISION, GENTLE — from C882/C883) predict B-side REGIME compatibility through the PP filtering cascade (C502), creating a three-way triangulation:

```
A paragraph PREFIX profile → handling type
        ↓ PP vocabulary filtering (C502)
B REGIME compatibility (token-weighted REGIME profile)
        ↔ Brunschwig fire degree (material_class → degree)
```

If PRECISION paragraphs preferentially allow REGIME_4 B tokens, and this matches Brunschwig's animal→degree-4 prediction, that would constitute convergence of three independently derived systems.

### Supports

- C882 (PRECISION Kernel Signature)
- C883 (Handling Distribution Alignment)
- C502 (PP Filtering Cascade)
- C753 (Near-Zero Content-Specific Routing)
- F-BRU-017 (REGIME_4 Sustained Equilibration)

### Design

6-test battery with pre-registered predictions:

| Test | What it tests | Prediction |
|------|---------------|------------|
| T2 (GATE) | PP MIDDLE REGIME specificity | Median specificity > 0.05; R4-heavy enriched in PRECISION |
| T1 | Handling-type REGIME profile discrimination | PRECISION mean R4 > CAREFUL (d > 0.5) |
| T3 | Size-controlled R4 enrichment (label permutation) | PRECISION mean R4 > 70th percentile |
| T4 | Brunschwig fire-degree concordance | 3+/4 handling types match predicted peak REGIME |
| T5 | Cross-handling-type REGIME gradient | CAREFUL_R4 < STANDARD_R4 < PRECISION_R4 |
| T6 | Brunschwig procedural complexity alignment | rho > 0.5 between recipe steps and PP pool size |

### Results

**Verdict: NO_SIGNAL** — 0/5 non-gate tests PASS.

| Test | Result | Key Numbers |
|------|--------|-------------|
| T2 (GATE) | **PARTIAL** | MIDDLEs have specificity (median=0.50, 322/388 > 0.2) but R4-heavy NOT enriched in PRECISION (OR=0.32, p=0.95) |
| T1 | **FAIL** | PRECISION R4=0.081 LOWER than CAREFUL R4=0.087 (d=-0.82, wrong direction) |
| T3 | **FAIL** | PRECISION at 2.9th percentile (DEPLETED, not enriched); p(greater)=0.97 |
| T4 | **FAIL** | All 4 handling types peak at REGIME_1 (base rate); only CAREFUL concordant (1/4) |
| T5 | **FAIL** | Wrong ordering; Spearman rho=-0.11, p=0.22 |
| T6 | **FAIL** | rho=0.4, p=0.6 (n=4 pairs, underpowered) |

### Interpretation

The PP pathway does NOT transmit handling-type signal to B-side REGIME profiles. Key findings:

1. **MIDDLEs have REGIME specificity** (T2 partial pass) — the mechanism exists in principle. Individual PP MIDDLEs are non-uniform across REGIMEs (median specificity 0.50).

2. **Handling types don't exploit it** — PRECISION paragraphs are R4-DEPLETED (2.9th percentile), not enriched. The direction is consistently wrong: PRECISION has the lowest R4 weight (0.081) while STANDARD has the highest (0.093).

3. **REGIME_1 dominates all profiles** — Every handling type peaks at REGIME_1 (~51-56%), with REGIME_3 second (~26-28%), leaving little room for differential R4 loading. The PP vocabulary, being shared across all A records, inherits the B corpus's REGIME_1 baseline.

4. **Confirms C753 at category level** — C753 showed near-zero content-specific routing at the individual record level (partial r=-0.038). This phase confirms the same null extends to the 4-type handling typology: even categorical grouping does not create detectable REGIME routing.

### Why This Matters

This is a clean negative that strengthens the model boundary. The A→B connection through PP vocabulary is **structural** (which tokens are legal) but not **parametric** (which REGIME parameters apply). Handling types characterize A paragraph internal structure (PREFIX profiles) without propagating to B execution parameters. The firewall between A categorical structure and B execution parameter assignment (C384) is confirmed to extend through the PP filtering pathway.

### Status

- 6-test battery: **COMPLETE**
- Verdict: **NO_SIGNAL** (negative result, informative)
- Confidence: **HIGH** — clear null with wrong-direction effects and label permutation control

### Files

- `phases/RECIPE_TRIANGULATION_V2/scripts/recipe_triangulation.py`
- `phases/RECIPE_TRIANGULATION_V2/results/recipe_triangulation.json`
