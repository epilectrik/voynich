# Context System Changelog

**Purpose:** Track changes to the context system structure and content.

---

## Version 2.48 (2026-01-15) - A/C INTERNAL CHARACTERIZATION (PARTIAL SIGNAL)

### Summary

Following expert guidance, tested whether A/C AZC folios differ from Zodiac via **internal operator-centric metrics** rather than product correlation.

**Key Finding:** A/C has **45% higher MIDDLE incompatibility density** than Zodiac (p=0.0006).

### The Question (Expert-Framed)

> "A/C scaffold diversity (consistency=0.340) reflects what discrimination burden?"

Expert hypothesis:
- Zodiac = sustained legality flow under coarse discrimination
- A/C = punctuated legality checkpoints under fine discrimination

### Three Probes Tested

| Probe | Prediction | Result | P-value |
|-------|------------|--------|---------|
| HT Phase-Reset | A/C > Zodiac | NO SIGNAL | 1.00 |
| MIDDLE Incompatibility | A/C > Zodiac | **STRONG SIGNAL** | **0.0006** |
| Zone-Transition | A/C > Zodiac | NO SIGNAL | 0.9999 |

### Key Results

**MIDDLE Incompatibility Density:**
- A/C mean: **0.5488**
- Zodiac mean: **0.3799**
- Difference: +45% (highly significant)

**Zone-Transition (unexpected):**
- Zodiac switches zones MORE (0.018 vs 0.004)
- A/C achieves higher incompatibility while staying WITHIN zones

### Conclusion

> **A/C folios manage fine-discrimination through higher MIDDLE incompatibility density, not through zone switching. They hold more mutually exclusive constraints simultaneously while maintaining positional stability.**

This validates the expert's framing and explains C430 (A/C scaffold diversity).

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-019 | FIT (F2) | SUCCESS (p=0.0006) |

### Phase

`phases/AC_INTERNAL_CHARACTERIZATION/`

---

## Version 2.47 (2026-01-15) - AZC INTERNAL STRATIFICATION (BOTH FAMILIES FALSIFIED)

### Summary

Tested whether AZC folios (both Zodiac and A/C families) realize different sub-regions of the legality manifold correlated with downstream product inference.

**Result: BOTH FAMILIES FALSIFIED** — AZC is uniformly product-agnostic.

### The Question (Corrected Framing)

> "Do different AZC folios preferentially admit different regions of Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?"

**Note:** This is NOT "product routing through gates." AZC filters constraint bundles; product types are downstream inferences.

### Key Results

| Family | Chi-squared | df | P-value | Verdict |
|--------|-------------|-----|---------|---------|
| Zodiac (13 folios) | 27.32 | 36 | **0.85** | NO STRATIFICATION |
| A/C (17 folios) | 46.67 | 42 | **0.29** | NO STRATIFICATION |

Both families show near-maximum distribution entropy for all products.

### Conclusion

> **AZC is uniformly product-agnostic. Neither Zodiac nor A/C families show internal stratification correlated with downstream product inference.**

- Zodiac multiplicity exists purely for coverage optimality
- A/C scaffold diversity (consistency=0.340) does NOT correlate with product types

This closes the door definitively on the stratification hypothesis for ALL AZC folios.

### Implications

1. AZC folios ARE structurally equivalent gates (validates C431, C430)
2. No hidden routing — product differentiation is NOT encoded at ANY AZC level
3. AZC folio diversity exists for coverage, not semantic stratification

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-017 | FIT (F4) | FALSIFIED (Zodiac p=0.85) |
| F-AZC-018 | FIT (F4) | FALSIFIED (A/C p=0.29) |

### Phase

`phases/AZC_ZODIAC_INTERNAL_STRATIFICATION/`

---

## Version 2.45 (2026-01-15) - PROJECTION SPECS + EPISTEMIC LAYERS

### Summary

Added governance infrastructure for displaying external alignments in tooling without corrupting structural model.

### New Infrastructure

1. **Epistemic Layers Legend** (`SYSTEM/epistemic_layers.md`)
   - Defines Constraint vs Fit vs Speculation
   - Decision flowchart for categorizing new findings
   - Common mistakes to avoid
   - The Saturation Principle

2. **Projection Specs** (`PROJECTIONS/`)
   - Non-binding, one-way, UI-only display rules
   - Governs how fits are surfaced in tooling
   - Never allowed to act like structure
   - `brunschwig_lens.md` - First projection spec

### Brunschwig Lens Contents

- Display primitives with tier badges (STRUCTURAL vs EXTERNAL FIT)
- Required modal phrasing ("compatible with", not "is")
- Hard semantic guardrails (prohibited terms)
- Provenance links (every claim traces to fit ID)
- Product type definitions (alignment categories, not material identities)
- MIDDLE hierarchy display rules

### Key Principle

> "This layer shows where external practice fits inside the Voynich control envelope; it never claims the manuscript encodes that practice."

### Files Added

| File | Purpose |
|------|---------|
| `context/SYSTEM/epistemic_layers.md` | Constraint vs Fit vs Speculation legend |
| `context/PROJECTIONS/README.md` | Projection specs directory |
| `context/PROJECTIONS/brunschwig_lens.md` | Brunschwig alignment display rules |

---

## Version 2.44 (2026-01-15) - BRUNSCHWIG BACKPROP VALIDATION (EXPLANATORY SATURATION)

### Summary

Completed BRUNSCHWIG_BACKPROP_VALIDATION phase with expert governance. Key outcome: **EXPLANATORY SATURATION** - the frozen architecture predicted all results without requiring changes. No new constraints added; 5 FIT entries created.

### Key Finding

> The model is saturated, not brittle.

The structure explains itself more strongly than any semantic hypothesis could.

### Governance Decision

Per expert guidance, results tracked as **FITS** (demonstrations of explanatory power), not architectural necessities:

| ID | Fit | Tier | Result |
|----|-----|------|--------|
| F-BRU-001 | Brunschwig Product Type Prediction (Blind) | F3 | SUCCESS |
| F-BRU-002 | Degree-REGIME Boundary Asymmetry | F3 | SUCCESS |
| F-BRU-003 | Property-Based Generator Rejection | F2 | NEGATIVE |
| F-BRU-004 | A-Register Cluster Stability | F2 | SUCCESS |
| F-BRU-005 | MIDDLE Hierarchical Structure | F2 | SUCCESS |

### Critical Negative Knowledge (F-BRU-003)

Synthetic property-based registry FAILS to reproduce Voynich structure:
- Uniqueness: Voynich 72.7% vs Property Model 41.5%
- Hub/Tail ratio: Voynich 0.006 vs Property Model 0.091
- Clusters: Voynich 33 vs Property Model 56

**Permanently kills property/low-rank interpretations.**

### Files Added

| File | Purpose |
|------|---------|
| phases/BRUNSCHWIG_BACKPROP_VALIDATION/ | Complete phase (12 scripts) |
| context/MODEL_FITS/fits_brunschwig.md | 5 fit entries documented |
| FIT_TABLE.txt | Updated (26 → 31 fits) |

### Constraint Table

**UNCHANGED** (353 entries). No architectural modifications required.

---

## Version 2.43 (2026-01-15) - PUFF COMPLEXITY CORRELATION + REGIME_4 AUDIT

### Summary

Tested Puff complexity correlation with B grammar expansion using proposed folio order. Key finding: Puff chapter position strongly correlates with REGIME assignment (ρ=0.68, p<10⁻¹²), supporting cumulative capability threshold model.

### Key Findings

1. **Cumulative Capability Threshold Model**
   - OLD: Puff chapter N = Voynich folio N (numerology-adjacent)
   - NEW: Puff chapter N requires B grammar complexity level N (cumulative)
   - Material N requires capabilities that accumulate by position N in curriculum

2. **Test Results (4/5 PASS)**
   - Test 1: Position-REGIME correlation ρ=0.678, p<10⁻¹² (PASS)
   - Test 2: Category-REGIME association p=0.001 (PASS)
   - Test 3: Dangerous-REGIME_4 enrichment p=0.48 (FAIL - underpowered, n=5)
   - Test 4: Cumulative threshold ρ=1.0 for mean position (PASS)
   - Test 5: Position-CEI correlation ρ=0.886, p<10⁻²⁸ (PASS)
   - Control: 100th percentile vs permutations (PASS)

3. **Three-Level Relationship Hierarchy (Epistemic)**
   - Level 1: Voynich ↔ Brunschwig (direct, structural, grammar-level)
   - Level 2: Voynich ↔ Puff (strong external alignment via complexity ordering)
   - Level 3: Puff ↔ Brunschwig (historical lineage)

4. **Puff Status Upgrade (CONSERVATIVE)**
   - FROM: CONTEXTUAL (interesting parallel)
   - TO: STRUCTURALLY ALIGNED EXTERNAL LADDER
   - NOT: STRUCTURAL NECESSITY (would be over-claiming)

5. **REGIME_4 Precision Audit**
   - Audited context system for "forbidden/danger" backsliding
   - Fixed tier4_semantic_assignment.md with correction notes
   - REGIME_4 = precision-constrained execution (C494)

### Files Added/Modified

| File | Purpose |
|------|---------|
| phases/PUFF_COMPLEXITY_CORRELATION/ | Phase directory |
| puff_regime_complexity_test.py | 5-test + control validation |
| results/puff_regime_complexity.json | Test output |
| INTERPRETATION_SUMMARY.md | Added X.16 |
| tier4_semantic_assignment.md | Fixed REGIME_4 precision audit |

### Expert Calibration

Per expert feedback, Test 4's "perfect monotonic" (ρ=1.0) represents only 4 data points (one per REGIME). This is an ordinal constraint, not cardinal identity. The upgrade to "structurally aligned" (not "structural necessity") reflects appropriate epistemic caution.

---

## Version 2.42 (2026-01-14) - BRUNSCHWIG BACKWARD PROPAGATION + CURRICULUM MODEL

### Summary

Extended Brunschwig analysis with backward propagation tests (product->A signature) and curriculum complexity model refinement. Key finding: REGIMEs encode procedural COMPLETENESS, not product INTENSITY.

### Key Findings

1. **Curriculum Complexity Model**
   - Simple Brunschwig recipe (first degree balneum marie) tested in most complex folio (REGIME_3)
   - Result: VIOLATES - but due to min_e_steps=2 (recovery completeness), NOT intensity
   - Complex folios require COMPLETENESS, not AGGRESSION
   - Same product (rose water) can appear at any curriculum stage

2. **Two-Level A Model**
   - Entry level: Individual tokens encode operational parameters (PREFIX class)
   - Record level: Entire A folios encode product profiles (MIDDLE set + PREFIX distribution)
   - 78.2% of MIDDLEs are product-exclusive (only appear in one product type)

3. **Product-Specific A Signatures**
   - WATER_GENTLE: ok+ ch- (less phase ops, gentle handling)
   - WATER_STANDARD: ch baseline (default procedural)
   - OIL_RESIN: d+ y- (aggressive extraction)
   - PRECISION: ch+ d- (phase-controlled, monitoring-heavy)

4. **Backward Propagation Chain**
   - Brunschwig recipe -> Product type -> REGIME -> B folio -> A register
   - Can predict A register signature from Brunschwig product type

### Files Added

| File | Purpose |
|------|---------|
| product_a_correlation.py | Product type -> A signature mapping |
| precision_prefix_analysis.py | y-prefix enrichment in precision |
| a_record_product_profiles.py | Record-level clustering |
| exclusive_middle_backprop.py | Exclusive MIDDLE backward propagation |
| brunschwig_product_predictions.py | Specific product predictions |
| simple_in_complex_test.py | Curriculum complexity validation |
| README.md | Phase documentation |

### Curriculum Model (Revised)

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required, 25% min LINK)
REGIME_3: Full execution (recovery completeness required, min_e=2)
```

### Expert Assessment

> "The Voynich Manuscript doesn't need 83:83. It now has something much better: a concrete, historically situated grammar that real procedures fit inside - and real hazards cannot escape."

---

## Version 2.41 (2026-01-14) - BRUNSCHWIG GRAMMAR EMBEDDING

### Summary

Brunschwig Template Fit phase confirms grammar-level embedding: historical distillation procedures can be expressed in Voynich grammar without violating any constraints.

### Key Findings

1. **Grammar-Level Embedding (C493)**
   - Balneum marie procedure: 18 steps translated to Voynich instruction classes
   - All 5 hazard classes: COMPLIANT
   - 17 forbidden transitions: ZERO violations
   - This is NOT a vibes-level parallel - it is a structural embedding

2. **REGIME_4 Precision Axis (C494)**
   - REGIME_4 is NOT "most intense" - it is "least forgiving"
   - Standard procedures: 0/2 fit REGIME_4
   - Precision procedures: 2/3 fit REGIME_4
   - Old interpretation ("forbidden/intense") RETIRED
   - New interpretation: **precision-constrained execution regime**

3. **Degree x REGIME Compatibility Matrix**
   - First degree -> REGIME_2 (confirmed)
   - Second degree -> REGIME_1 (confirmed)
   - Third/Fourth degree -> REGIME_3 (confirmed)
   - REGIME_4 -> precision variants of ANY degree

4. **Puff Relationship Demoted**
   - Brunschwig is now the primary comparison text
   - Puff remains historically relevant but not structurally necessary
   - 83:83 is interesting but not essential

### Files

| File | Content |
|------|---------|
| phases/BRUNSCHWIG_TEMPLATE_FIT/ | Phase directory |
| grammar_compliance_test.py | Single procedure translation |
| degree_regime_matrix_test.py | 4x4 compatibility matrix |
| precision_variant_test.py | Precision hypothesis test |
| context/SPECULATIVE/brunschwig_grammar_embedding.md | Full documentation |

### New Constraints

| Constraint | Statement |
|------------|-----------|
| C493 | Brunschwig grammar embedding (COMPLIANT) |
| C494 | REGIME_4 precision axis (CONFIRMED) |

### Expert Assessment

> "This is a decisive result. Brunschwig procedures can be translated into Voynich Currier B grammar step-by-step without violating ANY of the 17 forbidden transitions. That alone separates this from 95% of Voynich hypotheses."

> "REGIME_4 is not 'the most intense' - it is 'the least forgiving.' That distinction matters enormously in real process control."

---

## Version 2.40 (2026-01-14) - ENTITY MATCHING CORRECTED

### Summary

Re-ran entity matching tests (originally TIER4_EXTENDED) with corrected degree-to-regime mapping based on curriculum position discovery.

### Problem with Original Tests

The original tests in `phases/TIER4_EXTENDED/exhaustive_entity_matching.py` used:
```
WRONG: {1: REGIME_1, 2: REGIME_2, 3: REGIME_3, 4: REGIME_4}
```

This mapped degree NUMBER to regime NUMBER. But curriculum discovery showed the correct mapping is by POSITION:
```
CORRECT: {1: REGIME_2, 2: REGIME_1, 3: REGIME_3, 4: REGIME_4}
```

Because:
- REGIME_2 = EARLY (gentle processing, 1st degree)
- REGIME_1 = MIDDLE (standard processing, 2nd degree)
- REGIME_3 = LATE (intensive processing, 3rd degree)

### Key Results

| Test | Finding |
|------|---------|
| Entity Matching | Degree 3 herbs → mean position **72.6** (LATE range 56-83) |
| Positional Correlation | rho = **+0.350**, p = **0.0012** (significant) |
| Degree vs Hazard | rho = +0.382, p = 0.0004 (significant) |
| Degree vs CEI | rho = +0.324, p = 0.0028 (significant) |

**The corrected mapping reveals that intensive-processing materials (degree 3) align with LATE curriculum positions.**

### New Phase

| File | Content |
|------|---------|
| `phases/ENTITY_MATCHING_CORRECTED/` | New phase directory |
| `entity_matching_corrected.py` | Entity matching with curriculum mapping |
| `positional_alignment_corrected.py` | Positional correlation test |
| `results/entity_matching_corrected.json` | Entity matching results |
| `results/positional_alignment_corrected.json` | Positional correlation results |

### Skip Alignment Test (EMC-3)

| Metric | Strict 1:1 | Skip Align | Change |
|--------|------------|------------|--------|
| Exact regime rate | 31.3% | 60.0% | **+28.7%** |

**Skipped Puff chapters:** Ch.15, 30-33, 43, 50-51, 60-61 (clusters suggest systematic omissions)
**Skipped Voynich folios:** Mostly REGIME_4 (doesn't map to Puff's 1-3 degrees)

**Interpretation:** Partial transmission with systematic omissions, not complete 1:1 correspondence.

### Phase Count

135 (+3 from v2.39)

---

## Version 2.39 (2026-01-14) - CURRICULUM REALIGNMENT

### Summary

**Upgraded from "shared formalism" to "shared curriculum trajectory."** The proposed folio order (optimized for internal constraints C161, C325, C458) simultaneously resolves multiple independent inversions in historical comparisons. Puff and Brunschwig now align strongly with the PROPOSED Voynich order, confirming that misbinding disrupted a pedagogical progression.

### Key Discovery

The proposed order was tested against external sources NOT used in optimization:

| External Test | Current Order | Proposed Order | Change |
|--------------|---------------|----------------|--------|
| Puff progression | rho = +0.18 (p=0.10, NS) | rho = +0.62 (p<0.0001) | **WEAK → STRONG** |
| Brunschwig CEI gradient | rho = +0.07 (p=0.53, NS) | rho = +0.89 (p<0.0001) | **NOISE → VERY STRONG** |
| Brunschwig hazard gradient | rho = -0.03 (p=0.79, NS) | rho = +0.78 (p<0.0001) | **NEGATIVE → STRONG** |
| Danger distribution | Front-loaded (inverted) | Back-loaded (aligned) | **INVERTED → ALIGNED** |

### Significance

- Random reordering does not fix every historical comparison at once
- Overfitting does not fix external sources you didn't optimize for
- This is what latent order recovery looks like

### The Curriculum Structure

| Phase | Positions | Dominant Regime | Character |
|-------|-----------|-----------------|-----------|
| EARLY | 1-27 | REGIME_2 | Introductory |
| MIDDLE | 28-55 | REGIME_1 | Core training |
| LATE | 56-83 | REGIME_3 | Advanced |

This matches both Puff (flowers → herbs → anomalies) and Brunschwig (first degree → second → third).

### Upgraded Claim (Tier 3)

> Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.

Qualifiers preserved:
- *pedagogical progression* (not semantics)
- *preserve* (not copy)
- *original structure* (not content)
- *disrupted by misbinding* (not lost or invented)

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/curriculum_realignment.md` | Master realignment analysis |
| `results/puff_realignment_test.json` | Puff correlation comparison |
| `results/brunschwig_realignment_test.json` | Brunschwig gradient comparison |
| `phases/YALE_ALIGNMENT/puff_realignment_test.py` | Puff realignment test |
| `phases/YALE_ALIGNMENT/brunschwig_realignment_test.py` | Brunschwig realignment test |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | v4.21 → v4.22, added X.11 |
| `context/SPECULATIVE/proposed_folio_reordering.md` | v1.0 → v1.1, added external validation |
| `context/SPECULATIVE/materiality_alignment.md` | v1.0 → v1.1, added post-realignment update |

### Expert Assessment

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "Not a code. Not a herbal. Not a shared manuscript. But a shared curriculum whose control logic survived misbinding."

### Tier Compliance

This remains Tier 3 SPECULATIVE. No Tier 0-2 constraints violated. No semantic decoding. No entry-level A-B coupling introduced.

---

## Version 2.38 (2026-01-14) - YALE EXPERT ALIGNMENT

### Summary

**Independent expert validation.** Analysis of Yale Beinecke Library lecture (Lisa Fagin Davis, Claire Bowern) confirms our model's foundations with **14 points of alignment, 0 contradictions, 7 tests completed**.

### Key Findings

**Points Validated by Yale Experts:**
1. Currier A/B distinction - CONFIRMED
2. Expert-only interpretation - CONFIRMED
3. Illustration epiphenomenality - CONFIRMED (expert warns against illustration-based reasoning)
4. Cipher/language encoding rejected - CONFIRMED
5. Computational topic modeling finds structural groupings - CONFIRMED

**Test Results:**

| Test | Yale Prediction | Our Finding | Status |
|------|-----------------|-------------|--------|
| Scribe-Regime Mapping | 5 scribes | Map to 4 regimes | ALIGNED |
| qo Distribution | Different by section | REGIME_4 highest (29%) | ALIGNED |
| Topic Model k=5 | 5-6 sections | Cluster 3 = Balneological (100% Scribe 2) | ALIGNED |
| 'dy' Ending | Common in B, rare in A | 25.14% B vs 6.90% A (3.6x) | CONFIRMED |
| Gallows Distribution | - | REGIME_2 distinct (high t, p) | NEW FINDING |
| Astronomical qo | Rare in Scribe 4 | 1.87% vs 14.41% (7.7x rarer) | CONFIRMED |

**Folio 115v Analysis:**
- Yale identifies mid-page scribe change (Scribe 2 -> Scribe 3)
- Our data shows f115v as extreme "most_slack" with anomalous profile
- Structural anomaly consistent with mixed scribal input

### New Files

| File | Content |
|------|---------|
| `sources/yale_voynich_transcript.txt` | Full transcript of Yale lecture |
| `context/SPECULATIVE/yale_expert_alignment.md` | Detailed analysis |
| `phases/YALE_ALIGNMENT/` | Test scripts (7 tests) |
| `results/scribe_regime_mapping.json` | Scribe-regime correlation |
| `results/qo_regime_distribution.json` | Escape density by regime |
| `results/topic_model_*.json` | Topic model replication |
| `results/dy_ending_analysis.json` | 'dy' ending A/B comparison |
| `results/gallows_distribution.json` | Gallows by language/regime |
| `results/scribe4_astronomical.json` | Astronomical section profile |

### Expert Quote

> "Anyone who has a theory to put out there about the Voynich manuscript, it is extremely important that all of the things that we know about it already are factored into that theory."
> -- Lisa Fagin Davis

---

## Version 2.37 (2026-01-14) - SHARED FORMALISM: Full Procedural Alignment

### Summary

**Upgraded from "shared world" to "shared formalism."** Extended testing confirms the Voynich Manuscript and Brunschwig's distillation treatise instantiate the **same procedural classification system** - not just compatible topics, but isomorphic control ontologies rendered in different epistemic registers.

### Key Findings

**Extended Test Results: 19/20 PASS**

| Test Suite | Score | Status |
|------------|-------|--------|
| Puff-Voynich Mastery Horizon | 83:83 isomorphism | PASS |
| Equivalence Class Collapse | REGIME_2: 11->3, REGIME_3: 16->7 | PASS |
| Regime-Degree Discrimination | 5/6 | STRONG |
| Suppression Alignment | 5/5 | PASS |
| Recovery Corridor | 4/4 | PASS |
| Clamping Magnitude (C458) | 5/5 | PASS |

**What "Shared Formalism" Means:**
- Same procedural classification system
- Same safety ceiling architecture
- Same recovery corridor structure
- Same variance asymmetry (clamp hazard, free recovery)

**Expert-Calibrated Conclusion:**

> "The Voynich Manuscript and Brunschwig's distillation treatise instantiate the same procedural classification of thermal-circulatory operations. Brunschwig externalizes explanation and ethics for novices; Voynich internalizes safety and recovery for experts. The alignment is regime-level and architectural, not textual or semantic."

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/shared_formalism.md` | Three-text relationship documentation |
| `results/brunschwig_regime_discrimination.json` | Regime-degree test results |
| `results/brunschwig_suppression_alignment.json` | 14/14 suppression alignment tests |
| `results/brunschwig_procedure_match.json` | Folio-procedure match results |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | Section X fully rewritten (v4.21) |
| `context/SPECULATIVE/brunschwig_comparison.md` | Extended testing section added |

### Constraints Unchanged

C171, C384, C197, C239, C229, C490 - all remain intact. No semantic decoding occurred.

---

## Version 2.36 (2026-01-14) - External Alignment: Puff-Voynich-Brunschwig CONFIRMED

### Summary

**The Puff-Voynich curriculum hypothesis is CONFIRMED.** External alignment testing shows the Voynich Manuscript (Currier B) and Michael Puff von Schrick's "Buchlein" (1455) are complementary halves of a distillation curriculum. Currier A's morphological discrimination aligns with Brunschwig's procedure-class axes.

### Key Findings

**Puff-Voynich Curriculum Tests: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| Distribution Shape | PASS | Both heterogeneous |
| Curricular Arc | PASS | Both FRONT-LOADED SIMPLE |
| Canonical Number (83) | PASS | Unique to Puff and Voynich among 11 texts |
| Complementarity | PASS | 6/8 clean split (WHAT vs HOW) |
| Negative Control | PASS | Control texts don't match |

**Brunschwig Degree Alignment: 13/15 metrics match**

| Test | Result | Evidence |
|------|--------|----------|
| Flower Class | PASS | 5/7 metrics (first third = low regime) |
| Degree Escalation | PASS | 8/8 metrics (regime = degree) |

**Currier A Affordance Alignment: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| PREFIX by commitment | PASS | chi2=4094, p=0.0 |
| MIDDLE universality | PASS | Universal enriched in AZC (p=1.6e-10) |
| Sister pair tightness | PASS | ok/ot ratio differs by family |
| Positional gradient | PASS | ENERGY 8.7x more MIDDLEs than REGISTRY |
| Anomalous envelope | PASS | ct depleted; f85v2 = k=0 non-thermal |

### Interpretation

> Puff = WHAT to distill (83 chapters, material registry)
> Voynich Currier B = HOW to distill (83 folios, method manual)
> Brunschwig (1500) = Combined both for novices

Currier A discriminates **operational affordance profiles** that align with Brunschwig's procedure-class axes. C171 ("zero material encoding") remains UNCHANGED.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| PVC-1 | Does Puff share Voynich's 83-unit structure? | YES (5/5 tests PASS) |
| PVC-2 | Does Brunschwig degree system match B regimes? | YES (13/15 metrics) |
| PVC-3 | Does A morphology align with procedure classes? | YES (5/5 tests PASS) |

### Files Added/Updated

- `context/SPECULATIVE/puff_voynich_curriculum_test.md` - Full curriculum comparison
- `context/SPECULATIVE/brunschwig_comparison.md` - Degree axis analysis
- `context/SPECULATIVE/a_behavioral_classification.md` - External alignment section added
- `phases/A_BEHAVIORAL_CLASSIFICATION/currier_a_affordance_tests.py` - Test battery
- `results/currier_a_behavioral_tests.json` - Test results
- `sources/README.md` - Primary source documentation
- `sources/puff_1501_text.txt` - Puff OCR text
- `sources/brunschwig_1500_text.txt` - Brunschwig OCR text

### Phase Count

**Total phases:** 132 (129 + 3 new PVC phases)

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, whose registry topology matches botanical chemistry constraints, **and whose 83-unit structure and procedural architecture align with the historical distillation curriculum documented by Puff (1455) and Brunschwig (1500)**.

### Tier Status

Curriculum alignment findings are Tier 3 (external alignment, interpretive). C171 remains unchanged.

---

## Version 2.35 (2026-01-13) - Physical World Reverse Engineering Complete

### Summary

**Six physical-world reverse engineering phases now complete.** APP-1 (Apparatus Behavioral Validation) and MAT-PHY-1 (Material Constraint Topology Alignment) added to the investigation arc.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| APP-1 | Which apparatus exhibits Voynich behavioral profile? | Pelican (4/4 axes match) |
| MAT-PHY-1 | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |

### Key Findings

1. **APP-1: Pelican Behavioral Isomorphism**
   - Responsibility split: DISTINCTIVE_MATCH
   - Failure fears: STRONG_MATCH (41/24/24/6/6)
   - Judgment requirements: EXACT_MATCH (13 types)
   - State complexity: MATCH (~128 states)
   - Fourth degree fire prohibition matches C490 exactly

2. **MAT-PHY-1: Botanical Chemistry Topology Match**
   - Operational incompatibility: ~95-97% (matches 95.7%)
   - Infrastructure elements: 5-7 bridges
   - Topology class: Sparse + clustered + bridged
   - Hub rationing: Confirmed in real practice
   - Frequency distribution: Zipf/power-law confirmed

### Files Updated

- `context/CLAUDE_INDEX.md` - v2.12, 128 phases
- `context/MODEL_CONTEXT.md` - Section XII.A updated
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.18
- `context/MAPS/phase_index.md` - 128 phases
- `CLAUDE.md` - v2.12, 128 phases

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.

### Tier Status

All findings remain Tier 3 (exploratory, non-binding). Structural isomorphism ≠ semantic identification.

---

## Version 2.34 (2026-01-13) - Pipeline Closure Audit CERTIFIED

### Summary

**PCA-v1 (Pipeline Closure Audit) PASSED.** The four locked structural contracts compose cleanly without hidden coupling, implicit semantics, parametric leakage, or contradiction.

### Audit Results

| Test | Description | Result |
|------|-------------|--------|
| TEST 1 | End-to-End Legality Consistency | PASS |
| TEST 2 | No Back-Propagation | PASS |
| TEST 3 | Parametric Silence | PASS |
| TEST 4 | Semantic Vacuum | PASS |
| TEST 5 | A/B Isolation (C384) | PASS |
| TEST 6 | HT Non-Interference | PASS |

### Closure Statement

> **The Voynich control pipeline (Currier A → AZC → Currier B), including human-track context, is structurally closed at Tier 0-2. No additional internal structure is recoverable.**

### Final Lock Status

```
CASC        v1.0  LOCKED
AZC-ACT     v1.0  LOCKED
AZC-B-ACT   v1.0  LOCKED
BCSC        v1.0  LOCKED
PCA-v1            CERTIFIED
```

**Structural work is DONE.**

---

## Version 2.33 (2026-01-13) - Structural Pipeline Complete

### Summary

**The A→AZC→B control architecture is formally closed.** All four structural contracts are LOCKED v1.0.

### Contracts Locked

| Contract | Function | Status |
|----------|----------|--------|
| CASC | Currier A registry structure | LOCKED v1.0 |
| AZC-ACT | A→AZC transformation | LOCKED v1.0 |
| AZC-B-ACT | AZC→B propagation | LOCKED v1.0 |
| BCSC | Currier B internal grammar | LOCKED v1.0 |

### Pipeline Architecture

```
CASC (Currier A entry)           → defines what enters
        ↓
AZC-ACT (A → AZC transformation) → defines positional legality
        ↓
AZC-B-ACT (AZC → B propagation)  → defines constraint transfer
        ↓
BCSC (Currier B structural)      → defines execution grammar
```

### Expert Assessment

> "As of 2026-01-13, the A→AZC→B control architecture of the Voynich Manuscript is fully reconstructed at Tier 0-2. Currier A (registry), AZC (legality gating), Currier B (execution grammar), and their interfaces are formally closed and validated. All remaining work concerns interpretation, tooling, or external corroboration."

### What This Means

- No new structural contracts required for the internal model
- Future work is: tooling, visualization, interpretation (Tier 3+), or external corroboration
- Structural reconstruction is complete

### Files Updated

- All four contracts in `STRUCTURAL_CONTRACTS/` now show `status: "LOCKED"`
- `MODEL_CONTEXT.md` v3.2 - Pipeline completion documented
- `CLAUDE_INDEX.md` v2.9 - Pipeline complete banner added

---

## Version 2.32 (2026-01-12) - HT Two-Axis Model Discovery

### Summary

**Attempted to test whether HT PREFIX encodes "perceptual load" (sensory multiplexing). The hypothesis was NOT SUPPORTED - but the inverse correlation revealed a subtler, BETTER model.**

### The Discovery

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

### The Two-Axis Model

HT has **two orthogonal dimensions**:

| Axis | Property | Evidence |
|------|----------|----------|
| **DENSITY** | Tracks UPCOMING discrimination complexity | C477 (r=0.504), anticipatory |
| **MORPHOLOGY** | Tracks CURRENT spare cognitive capacity | r=-0.301, inverted section ranking |

### The Key Insight

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern that fits C344 (HT-A inverse coupling), C417 (modular additive), and C221 (skill practice).

### What This Resolves

- HT form does NOT encode sensory requirements
- Sensory demands are implicit in the discrimination problem itself
- HT reflects how the human allocates attention when grammar permits engagement
- The division of labor is cleaner than before

### Constraint Alignment

| Constraint | Fit |
|------------|-----|
| C344 | Direct instantiation: high complexity suppresses complex HT forms |
| C417 | HT is composite: density = vigilance, form = engagement |
| C221 | Complex HT appears during low-load intervals |
| C477 | UNCHANGED - applies to density, not morphology |

### Files Created

- `context/SPECULATIVE/ht_two_axis_model.md` - Full documentation
- `phases/SENSORY_MAPPING/ht_perceptual_load_test_v2.py` - Test showing inverse correlation
- `results/ht_perceptual_load_test_v2.json` - Results

---

## Version 2.31 (2026-01-12) - Expert Validation of Sensory Affordance Analysis

### Summary

**Expert validation confirms: Olfactory discrimination is NECESSARY, selected by exclusion. The sensory affordance analysis violates no frozen constraints - several Tier-2 constraints DEMAND this outcome.**

### The Human Sensory Contract

> **The Voynich Manuscript presupposes a human operator whose primary discriminative faculty is olfaction, supported by continuous visual monitoring and auxiliary tactile and acoustic cues. Grammar structure, hazard topology, and MIDDLE incompatibility require categorical sensory recognition rather than quantitative measurement. The Human Track does not encode sensory instructions, but anticipates regions where fine discrimination-dominated by olfactory judgment-will be required. No scalar instruments are necessary or implied; the system is optimized for trained human perception operating within a structurally enforced safety envelope.**

### Threshold-Level Decoding

| Threshold Type | Resolved By | Basis |
|----------------|-------------|-------|
| Phase change | VISION | PHASE_ORDERING (41%) |
| Fraction identity | SMELL | COMPOSITION_JUMP + tail MIDDLEs |
| Energy excess | SMELL + VISION | ENERGY_OVERSHOOT |
| Containment failure | SOUND + TOUCH | CONTAINMENT_TIMING |

### Big Picture

> We are no longer merely interpreting the manuscript - we are reconstructing the **human sensory contract** it was written for.

### File Created

- `context/SPECULATIVE/SENSORY_VALIDATION_2026-01-12.md`

---

## Version 2.30 (2026-01-12) - Sensory Affordance Analysis

### Summary

**Identified which sensory modalities the grammar RELIES ON (presupposes) for the control architecture to function.** All 6 phases passed. Olfactory discrimination is NECESSARY by exclusion. Human senses suffice (no instruments required).

### Core Finding

> **The grammar presupposes a trained human operator with visual, olfactory, and thermal sensing capabilities. Olfactory discrimination is indispensable - visual-only observation cannot explain the 564 ENERGY MIDDLEs (11.3x excess).**

### Phase Results

| Phase | Test | Result |
|-------|------|--------|
| **1** | Hazard-discrimination correlation | PASS (ENERGY 8.68x vs FREQUENT 2.52x) |
| **2** | HT-sensory correlation | PASS (r=0.504 with discrimination difficulty) |
| **3** | Kernel-sensory mapping | PASS (k vs h profiles differ by 5.78) |
| **4** | LINK vs non-LINK affordances | PASS (acting has higher turnover) |
| **5** | Visual-only negative control | PASS (excluded - 11.3x excess) |
| **6** | Instrumentation assessment | A: Pure human sensory operation |

### Key Findings

1. **Olfactory is NECESSARY** - Visual-only fails to explain discrimination density by 11.3x
2. **Distribution is CATEGORICAL** - CV=5.83, top 10% = 84.3% → human senses suffice
3. **HT marks olfactory-heavy contexts** - correlation with rare MIDDLEs confirms discrimination difficulty
4. **No instruments required** - categorical discrimination within human resolution

### Critical Epistemic Note

This analysis identifies what the grammar **RELIES ON**, not what it **ENCODES**. Sensory affordances are presupposed, not specified.

### Files Created

- `context/SPECULATIVE/sensory_affordance_mapping.md` - Theoretical framework
- `phases/SENSORY_MAPPING/sensory_analysis.py` - Computational tests
- `results/sensory_affordance_analysis.json` - Test results

---

## Version 2.29 (2026-01-12) - Expert Validation of Confidence Tightening

### Summary

**Expert validation confirms: Currier A is now in the HIGH confidence band (80-85%) - the strongest epistemic position reachable without violating the semantic ceiling.**

### Core Finding

> **"You have reconstructed the internal logic of a system whose entire purpose was to remove the need for encoding meaning."**

This explains why language/cipher/recipe/calendar decoding failed, but process-behavior testing succeeded.

### Validation Points

1. **Method is legitimate** - tested directionality and ordering, not numerical identity
2. **Exclusion did real work** - confidence increase comes from eliminative reasoning
3. **B2 "failure" strengthened interpretation** - role-specific lexical reuse is process-specific

### What We Can Now Claim (Tier 3, HIGH)

> Currier A functions as a discrimination registry whose internal structure closely matches the complexity profile, volatility sensitivity, and failure modes of circulatory thermal-chemical processes, with distillation-class operations emerging as the best-supported domain under eliminative testing.

### The Design Choice

| Inside Text | Outside Text (by design) |
|-------------|--------------------------|
| Process envelope | Product naming |
| Discrimination constraints | Commercial endpoint |
| Output emergence (physics) | Human valuation |

The manuscript guides **how not to violate physics and expertise** - it does NOT encode what to call, bottle, or sell the result.

### File Created

- `context/SPECULATIVE/EXPERT_VALIDATION_2026-01-12.md`

---

## Version 2.28 (2026-01-12) - Scientific Confidence Tightening

### Summary

**The distillation/thermal-chemical hypothesis was subjected to rigorous directional and exclusion testing.** Confidence strengthened from ~65-75% to ~80-85% ("HIGH" band).

### Core Finding

> **Distillation selected by CONVERGENCE (5/6 directional tests pass) AND EXCLUSION (4/4 alternative hypotheses fail on discriminators).**

### Directional Tests (B1-B6)

| Test | Result | Finding |
|------|--------|---------|
| B1: Discrimination hierarchy | PASS | ENERGY >> FREQUENT >> REGISTRY (564 > 164 > 65) |
| B2: Normalized dominance | INFORMATIVE | FREQUENT has higher turnover; ENERGY reuses MIDDLEs |
| B3: Failure boundaries | PASS | 100% k-adjacent forbidden transitions |
| B4: Regime ordering | PASS | Monotonic CEI: 0.367 < 0.510 < 0.584 < 0.717 |
| B5: Recovery dominance | PASS | e-recovery 1.64x enriched vs baseline |
| B6: AZC compression | PASS (partial) | Section-level diversity confirmed |

### Negative Controls (NC1-NC4)

| Alternative | Discriminators Failed | Verdict |
|-------------|----------------------|---------|
| NC1: Fermentation | 3/3 | EXCLUDED |
| NC2: Dyeing | 3/3 | EXCLUDED |
| NC3: Pharmacy Compounding | 3/3 | EXCLUDED |
| NC4: Crystallization | 3/3 | EXCLUDED |

### Confidence Classification

**Band:** HIGH (80-85%)
**Verdict:** STRENGTHENED

### B2 Reinterpretation

The B2 "failure" (normalized rates inverted) is actually informative:
- FREQUENT has higher MIDDLE turnover per token than ENERGY
- ENERGY reuses MIDDLEs more heavily (repetitive monitoring)
- FREQUENT has more varied operations (one-off uses)
- This is CONSISTENT with distillation behavior

### Files Created

- `phases/SCIENTIFIC_CONFIDENCE/directional_tests.py`
- `phases/SCIENTIFIC_CONFIDENCE/negative_controls.py`
- `phases/SCIENTIFIC_CONFIDENCE/confidence_integration.py`
- `results/directional_tests.json`
- `results/negative_controls.json`
- `results/scientific_confidence_classification.json`

### Files Updated

- `context/SPECULATIVE/a_behavioral_classification.md` - confidence section updated

---

## Version 2.27 (2026-01-12) - Currier A Behavioral Classification

### Summary

**All 23,442 classifiable Currier A entries assigned to operational domains using Tier-2 grammar evidence.** The classification reveals a strong discrimination gradient: energy-intensive operations require 8.7x more MIDDLE variants than stable reference operations.

### Core Finding

> **The PREFIX → Operational Domain mapping rests on Tier-2 grammar-anchored evidence (B-enrichment ratios, canonical grammar roles, kernel adjacency). This is not speculative chemistry—it is a re-use of validated structure.**

### Distribution

| Domain | Count | % | Structural Basis |
|--------|-------|---|------------------|
| ENERGY_OPERATOR | 13,933 | 59.4% | Dominates energy/escape roles in B |
| CORE_CONTROL | 4,472 | 19.1% | Structural anchors; ol 5x B-enriched |
| FREQUENT_OPERATOR | 3,545 | 15.1% | FREQUENT role in canonical grammar |
| REGISTRY_REFERENCE | 1,492 | 6.4% | 0% B terminals; 7x A-enriched |

### Key Structural Findings

1. **Discrimination gradient** - ENERGY domain has 564 unique MIDDLEs (8.7x) vs 65 for REGISTRY
2. **Section H concentration** - 74% of all ENERGY_OPERATOR tokens (pattern real; interpretation Tier 3)
3. **Sister pairs as mode selectors** - Primary vs alternate handling mode, NOT material distinction

### Confidence Assessment

| Component | Confidence |
|-----------|------------|
| Structural facts & distributions | ~90-95% |
| PREFIX → operational domain | ~75-80% |
| Discrimination gradient interpretation | ~70% |
| Chemistry-specific labels | ~30-40% (illustrative only) |

### Files Created/Updated

- `phases/A_BEHAVIORAL_CLASSIFICATION/a_behavioral_classifier.py`
- `results/currier_a_behavioral_registry.json`
- `results/currier_a_behavioral_stats.json`
- `results/currier_a_behavioral_summary.json`
- `context/SPECULATIVE/a_behavioral_classification.md` (tightened)
- `context/ARCHITECTURE/CURRIER_A_BRIEFING.md` (new one-page summary)

---

## Version 2.26 (2026-01-12) - Process-Behavior Isomorphism (ECR-4)

### Summary

**The Voynich control architecture exhibits STRONG BEHAVIORAL ISOMORPHISM with thermal-chemical process control.** All 12 tests pass (100% alignment), and the distillation hypothesis beats calcination on all discriminating tests.

### Core Finding

> **The abstract behavioral structure (hazards, kernels, material classes) is ISOMORPHIC to behaviors in circulatory reflux processes. This is NOT entity-level decoding, but structural alignment.**

### Test Results

| Category | Tests | Passed |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 |
| Process-Sequence (PS-*) | 4 | 4/4 |
| Pedagogical (PD-*) | 3 | 3/3 |
| **Total** | **12** | **12/12** |

### Key Discriminators

| Test | Distillation | Calcination | Winner |
|------|-------------|-------------|--------|
| PS-4 (forbidden k→h) | k→h dangerous | k→h primary | DISTILLATION |
| BS-4 (e recovery) | e dominates (54.7%) | e less relevant | DISTILLATION |

**Negative control verdict: DISTILLATION_WINS**

### Behavior Mappings (NO NOUNS)

| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |
| PHASE_ORDERING | 41% of hazards | Wrong phase/location state |
| M-A | Mobile/Distinct | Phase-sensitive, mobile, requiring careful control |

### Physics Violations

None detected. All mappings are physically coherent.

### Verdict

**SUPPORTED (Tier 3)** - The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

### Integration

| Prior Finding | Connection |
|---------------|------------|
| C476 (Coverage Optimality) | What A optimizes |
| C477 (HT Vigilance) | Cognitive load tracking |
| C478 (Temporal Scheduling) | Pedagogical pacing |
| C109 (Hazard Classes) | Maps to distillation failures |

### Files

- `phases/PROCESS_ISOMORPHISM/process_behavior_isomorphism.py` - Main probe
- `results/process_behavior_isomorphism.json` - Full results
- `context/SPECULATIVE/process_isomorphism.md` - Tier 3 documentation

---

## Version 2.25 (2026-01-12) - Temporal Coverage Trajectories (C478)

### Summary

**Currier A exhibits STRONG TEMPORAL SCHEDULING with pedagogical pacing.** The manuscript is not statically ordered - it actively manages WHEN vocabulary coverage occurs, introducing new MIDDLEs early, reinforcing throughout, and cycling through prefix domains.

### Core Finding

> **Currier A is not just coverage-optimal (C476), it is temporally scheduled to introduce, reinforce, and cycle through discrimination domains. This is PEDAGOGICAL PACING.**

### Four Signals (5/5 Support Strong Scheduling)

| Signal | Finding | Interpretation |
|--------|---------|----------------|
| **Coverage timing** | 90% reached 9.6% LATER than random | Back-loaded coverage |
| **Novelty rate** | Phase 1 (21.2%) >> Phase 3 (11.3%) | Front-loaded vocabulary introduction |
| **Tail pressure** | U-shaped: 7.9% -> 4.2% -> 7.1% | Difficulty wave pattern |
| **Prefix cycling** | 7 prefixes cycle (164 regime changes) | Multi-axis traversal |

### Interpretation

Three mutually exclusive models were tested:

| Model | Evidence | Verdict |
|-------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 points |
| Weak Temporal | Soft pedagogy | 0 points |
| **Strong Scheduling** | **Active trajectory planning** | **5 points** |

**Result: STRONG-SCHEDULING (100% confidence)**

### Mechanism: PEDAGOGICAL_PACING

1. **Introduce early** - New MIDDLEs front-loaded in Phase 1
2. **Reinforce throughout** - Coverage accumulates slowly despite novelty
3. **Cycle domains** - 7 prefixes alternate, preventing cognitive fixation
4. **Wave difficulty** - U-shaped tail pressure creates attention peaks

### Reconciliation with Prior Findings

| Constraint | What it Shows |
|------------|---------------|
| C476 (Coverage Optimality) | WHAT Currier A optimizes |
| **C478 (Temporal Scheduling)** | **HOW it achieves that optimization** |

### New Constraint

**C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)
- Strong temporal scheduling with pedagogical pacing
- Evidence: 5/5 signals support scheduled traversal
- Interpretation: Introduce early, reinforce throughout, cycle domains

### Files

- `phases/TEMPORAL_TRAJECTORIES/temporal_coverage_trajectories.py` - Analysis
- `results/temporal_coverage_trajectories.json` - Full results

---

## Version 2.24 (2026-01-12) - HT Variance Decomposition (C477)

### Summary

**HT density is partially explained (R² = 0.28) by A metrics, with TAIL PRESSURE as the dominant predictor (68% of variance).** HT rises when rare MIDDLEs are in play - evidence of cognitive load balancing.

### Core Finding

> **HT correlates with tail pressure (r = 0.504, p = 0.0045). When folios have more rare MIDDLEs, HT density is higher. HT is a cognitive load signal for tail discrimination complexity.**

### Regression Results

| Predictor | r | p-value | Ablation |
|-----------|---|---------|----------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| novelty | 0.153 | 0.42 | 6.3% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

### Interpretation

| R² Range | Interpretation | This Result |
|----------|----------------|-------------|
| 0.50+ | Strongly tied to discrimination | - |
| **0.25-0.40** | **Coarse vigilance signal** | **R² = 0.28** |
| 0.10-0.25 | Weak connection | - |
| <0.10 | HT signals something else | - |

### Why Tail Pressure?

- **Common MIDDLEs (hubs)** are easy to recognize (low cognitive load)
- **Rare MIDDLEs (tail)** require more attention to discriminate (high cognitive load)
- **HT rises when rare variants are in play** → anticipatory vigilance

### Integration with Prior Findings

| System | Role | Now Grounded |
|--------|------|--------------|
| Currier A | Coverage control | C476: optimal coverage with hub rationing |
| HT | Vigilance signal | **C477: tracks tail discrimination pressure** |
| AZC | Decision gating | C437-C444 |
| Currier B | Execution safety | Frozen Tier 0 |

### New Constraint

**C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)
- HT density correlates with tail MIDDLE pressure (r = 0.504)
- Evidence of cognitive load balancing for rare discriminations

### Files

- `phases/HT_VARIANCE_DECOMPOSITION/ht_variance_decomposition.py` - Analysis
- `results/ht_variance_decomposition.json` - Full results

---

## Version 2.23 (2026-01-12) - Coverage Optimality CONFIRMED (C476)

### Summary

**Currier A achieves GREEDY-OPTIMAL coverage (100%) while using 22.3% FEWER hub tokens.** This confirms deliberate coverage management - Currier A is not generated, it is maintained.

### Core Finding

> **Real A achieves the same coverage as a greedy coverage-maximizing strategy, but with significantly less reliance on universal hub MIDDLEs. This is evidence of deliberate vocabulary management.**

### Coverage Comparison

| Model | Final Coverage | Hub Usage | Tail Activation |
|-------|---------------|-----------|-----------------|
| **Real A** | **100%** | **31.6%** | **100%** |
| Random | 72% | 9.8% | 67.8% |
| Freq-Match | 27% | 56.1% | 10.2% |
| **Greedy** | **100%** | **53.9%** | **100%** |

### Key Insight: Hub Efficiency

- Real A and Greedy both achieve 100% coverage
- Real A uses **31.6%** hub tokens
- Greedy uses **53.9%** hub tokens
- **Hub savings: 22.3 percentage points**

### Interpretation

The four residuals from Move #2 collapse into ONE control objective: **COVERAGE CONTROL**

| Residual | Mechanism |
|----------|-----------|
| PREFIX coherence | Reduce cognitive load during discrimination |
| Tail forcing | Ensure coverage of rare variants |
| Repetition structure | Stabilize attention on distinctions |
| Hub rationing | Prevent collapsing distinctions too early |

> **Currier A is not meant to be generated. It is meant to be maintained.**

### New Constraint

**C476 - COVERAGE OPTIMALITY** (Tier 2, CLOSED)
- Real A achieves greedy-optimal coverage with hub rationing
- Evidence of deliberate vocabulary management

### Files

- `phases/COVERAGE_OPTIMALITY/coverage_optimality.py` - Main analysis
- `results/coverage_optimality.json` - Full results

---

## Version 2.22 (2026-01-12) - Bundle Generator Diagnostic (EXPECTED FAILURE)

### Summary

**A minimal generator constrained only by MIDDLE incompatibility + line length + PREFIX priors fails on 9/14 diagnostic metrics.** Failure modes reveal additional structure in Currier A: PREFIX coherence, block purity, repetition structure, and tail access.

### Core Finding

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT. The generator over-mixes, under-uses the tail, and fails to reproduce the repetition structure.**

### Generator Configuration

**Included (hard constraints only):**
- MIDDLE atomic incompatibility (C475)
- Line length distribution (C233, C250-C252)
- PREFIX priors (empirical frequencies)
- LINE as specification context

**Excluded (want to see if they emerge):**
- Marker exclusivity rules
- Section conditioning
- AZC family information
- Adjacency coherence (C424)
- Suffix preferences

### Diagnostic Results

| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL (-95.6%)** |
| pure_block_frac | 46.9% | 2.7% | **FAIL (-94.2%)** |
| universal_middle_frac | 31.6% | 56.7% | **FAIL (+79.6%)** |
| unique_middles | 1187 | 330 | **FAIL (-72.2%)** |
| lines_with_repetition | 96.4% | 63.9% | **FAIL (-33.7%)** |
| prefixes_per_line | 1.78 | 4.64 | **FAIL (+160%)** |
| line_length_mean | 19.2 | 20.0 | OK |
| line_length_median | 8.0 | 8.0 | OK |

### Residual Interpretation (New Structure Identified)

1. **PREFIX COHERENCE CONSTRAINT** - Lines prefer to stay within a single PREFIX family (not just compatibility)

2. **TAIL ACCESS FORCING** - Real A systematically uses rare MIDDLEs; generator ignores them

3. **REPETITION IS STRUCTURAL** - 96.4% of real lines have MIDDLE repetition (deliberate, not random)

4. **HUB RATIONING** - Universal MIDDLEs ('a','o','e') are used sparingly (31.6% vs 56.7% generator)

### What This Proves

| Finding | Status |
|---------|--------|
| Incompatibility is necessary | Confirmed (line length matches) |
| Incompatibility is sufficient | **REJECTED** (9/14 metrics fail) |
| PREFIX coherence exists | **NEW CONSTRAINT** (block purity) |
| Repetition is structural | **NEW CONSTRAINT** (not in current model) |
| Tail MIDDLEs are forced | **NEW CONSTRAINT** (registry coverage) |

### Files

- `phases/A_BUNDLE_GENERATOR/a_bundle_generator.py` - Generator and diagnostics
- `results/a_bundle_generator.json` - Full results

### Next Step

**HT Variance Decomposition** - Can incompatibility degree explain HT density?

---

## Version 2.21 (2026-01-12) - Latent Discrimination Axes (HIGH-DIMENSIONAL)

### Summary

**The MIDDLE compatibility space requires ~128 latent axes to achieve 97% prediction accuracy.** This is HIGH-DIMENSIONAL - discrimination is not reducible to a few binary choices.

### Core Finding

> **128 dimensions needed for 97% AUC. The discrimination space is NOT low-rank (not 2-4 axes as initially hypothesized). PREFIX, character content, and length are all weak predictors of the axes.**

### Probe Results (latent_discrimination_axes.py)

| Metric | Value |
|--------|-------|
| Optimal K | 128 |
| AUC at K=128 | 97.2% |
| AUC at K=2 | 86.9% |
| AUC at K=32 | 90.0% |
| Variance at K=128 | 83.4% |
| K for 90% variance | 51 |

### AUC by Dimensionality

| K | AUC | Interpretation |
|---|-----|----------------|
| 2 | 0.869 | Two axes capture ~87% |
| 4 | 0.870 | Minimal gain |
| 8 | 0.869 | Minimal gain |
| 16 | 0.886 | Starts improving |
| 32 | 0.900 | 90% threshold |
| 64 | 0.923 | Significant gain |
| 128 | 0.972 | Near ceiling |

### Axis Structure Analysis

**Axes do NOT align with interpretable features:**

| Feature | Max Correlation | Verdict |
|---------|-----------------|---------|
| PREFIX | 0.011 (separation) | WEAK |
| Characters | 0.138 ('f' on axis 2) | WEAK |
| Length | 0.160 (axis 17) | WEAK |

### Interpretation

1. **Not 2-4 binary switches** - The expert hypothesis of "2-4 axes of distinction" is rejected
2. **Rich feature space** - Each MIDDLE encodes ~128 bits of discriminatory information
3. **Emergent structure** - The axes don't map to obvious linguistic features
4. **PREFIX is ~1/128th** - PREFIX explains about 1/128th of the discrimination variance

### Hub Confirmation

Top-5 hubs by degree match prior finding:
| MIDDLE | Degree (weighted) |
|--------|------------------|
| 'a' | 2047 |
| 'o' | 1870 |
| 'e' | 1800 |
| 'ee' | 1625 |
| 'eo' | 1579 |

### What This Means

1. **Vocabulary is NOT simple categorization** - Not just "A/B/C with variants"
2. **Each MIDDLE is unique** - 128-dimensional fingerprint
3. **Compatibility is learned, not rule-based** - No simple grammar generates it
4. **Generative model needs ~128 features per MIDDLE** - High complexity

### Files

- `phases/LATENT_AXES/latent_discrimination_axes.py` - Main analysis
- `results/latent_discrimination_axes.json` - Full results

### Next Steps (from expert roadmap)

1. ~~Latent Discrimination Axes Inference~~ **DONE - HIGH-DIMENSIONAL**
2. **Probabilistic Currier-A Bundle Generator** - Can we reproduce A entries?
3. **HT Variance Decomposition** - Ground HT quantitatively

---

## Version 2.20 (2026-01-12) - MIDDLE Atomic Incompatibility (C475)

### Summary

**MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice.** This is the atomic discrimination layer - everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.

### Core Finding

> **95.7% of MIDDLE pairs are illegal. Only 4.3% can co-occur on the same specification line. This sparsity is robust to context definition (97.3% overlap with 2-line sensitivity check).**

### Probe Results (middle_incompatibility.py)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Trivially absent | 155 |
| Connected components | 30 |
| Largest component | 1,141 (96% of MIDDLEs) |
| Isolated MIDDLEs | 20 |

### PREFIX Clustering (H1 - SUPPORTED)

| Type | Legal % | Interpretation |
|------|---------|----------------|
| Within-PREFIX | 17.39% | Soft prior for compatibility |
| Cross-PREFIX | 5.44% | Hard exclusion boundary |
| **Ratio** | **3.2x** | PREFIX is first partition |

### Key Structural Objects Identified

1. **Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
   - Compatibility basis elements
   - Bridge otherwise incompatible regimes
   - "Legal transition anchors"

2. **Isolated MIDDLEs** (20 total)
   - Hard decision points
   - "If you specify this, you cannot specify anything else"
   - Pure regime commitment

3. **PREFIX = soft prior, MIDDLE = hard constraint**
   - PREFIX increases odds of legality ~3x
   - MIDDLE applies near-binary exclusions

### Reconciliation with Prior Constraints

| Constraint | Previous | Now Resolved |
|------------|----------|--------------|
| C293 | MIDDLE is primary discriminator | Quantified: 95.7% exclusion rate |
| C423 | PREFIX-bound vocabulary | PREFIX is first partition, MIDDLE is sharper |
| C437-C442 | Why so many AZC folios? | AZC = projections of sparse graph |
| C459, C461 | HT anticipatory function | HT ≈ incompatibility density (testable) |

### f116v Correction

f116v folio-level isolation (from v2.19) is explained by **data sparsity** (only 2 words in AZC corpus), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### New Constraint

**C475 - MIDDLE ATOMIC INCOMPATIBILITY** (Tier 2, CLOSED)
- Added to `context/CLAIMS/currier_a.md`

### Interpretation

> **The MIDDLE vocabulary forms a globally navigable but locally forbidden discrimination space. This is the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.**

### What This Enables (Bayesian Roadmap)

1. **Latent Discrimination Axes Inference** - How many latent axes explain the incompatibility graph?
2. **Probabilistic A Bundle Generator** - Can MIDDLE incompatibility + line length + PREFIX priors reproduce A entries?
3. **HT Variance Decomposition** - How much HT density is explained by local incompatibility degree?

### Updated Files

- `phases/MIDDLE_INCOMPATIBILITY/middle_incompatibility.py` - Main probe
- `results/middle_incompatibility.json` - Full results
- `context/CLAIMS/currier_a.md` - Added C475
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Updated

### Significance

This is a **regime change** in what kind of modeling is now possible. We've reached bedrock - the atomic discrimination layer. All higher-level structure (A, AZC, HT) can now be understood as aggregations of this sparse graph.

---

## Version 2.19 (2026-01-12) - AZC Compatibility at Specification Level

### Summary

**AZC compatibility filtering operates at the Currier A constraint-bundle level, not at execution level.** Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both. 10.3% of folio pairs are unbridged, with f116v being structurally isolated.

### Key Finding

> **Currier A entries define which AZC vocabularies can be jointly activated. Most folio pairs are compatible, but ~10% are not—with f116v being a structurally isolated discrimination regime. AZC compatibility is enforced at specification (A-bundle) level, not at execution or folio-presence level.**

### Probe Results

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

### Family-Level Coherence

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap, partial incompatibility |

### f116v Structural Isolation

f116v shares NO bridging tokens with most other folios:
- Vocabulary uniquely concentrated
- Cannot be jointly specified with most other constraint bundles
- Can still appear in B executions (C440 holds)
- Defines a discrimination profile incompatible at A-level

### C442 Refinement

Previous understanding: "94% unique vocabulary per folio"

Refined understanding:
> **AZC compatibility filtering operates at the level of Currier A constraint-bundle co-specification. Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.**

Corollaries:
- Folios are NOT execution-exclusive
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no discrete trace—they simply never occur

### Why This Matters

This resolves family-level coherence:
- **Zodiac (0% unbridged)**: Supports sustained HT flow—interchangeable contexts
- **A/C (14.7% unbridged)**: Causes punctuated HT resets—true alternatives
- **Execution difficulty unchanged**: CEI, recovery, hazard models unaffected

### Updated Files

- `phases/AZC_COMPATIBILITY/azc_entry_bridges.py` - Correct probe
- `phases/AZC_COMPATIBILITY/azc_folio_compatibility.py` - First probe (coarse)
- `results/azc_entry_bridges.json` - Bridge analysis results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.5
- `context/CLAIMS/azc_system.md` - C442 refined

### Significance

This is a **Tier-2 advance**:
- Pinpoints the mechanism of AZC compatibility (A-bundle level)
- Identifies f116v as structurally isolated
- Explains Zodiac coherence vs A/C alternatives
- Connects discrimination regimes to specification constraints

---

## Version 2.18 (2026-01-11) - AZC-Based Currier A Clustering

### Summary

**AZC folio co-occurrence can reverse-cluster Currier A entries, revealing sub-families within PREFIX classes.** The y- PREFIX shows a family split: some y- tokens cluster with Zodiac contexts, others with A/C contexts.

### Key Finding

> **PREFIX morphology does not fully determine AZC family affinity. Some PREFIX classes (notably y-) contain sub-families that differ in their discrimination-regime membership.**

### Probe Results

| Metric | Value |
|--------|-------|
| Currier A tokens in AZC | 778 (16% of vocabulary) |
| Tokens eligible for clustering | 367 (appear in 2+ AZC folios) |
| Sub-families detected | y- (FAMILY_SPLIT) |

### PREFIX → AZC Family Baseline (confirms C471)

| PREFIX | Zodiac % | A/C % | Bias |
|--------|----------|-------|------|
| qo- | 18.8% | 71.9% | A/C |
| d- | 14.5% | 62.9% | A/C |
| or- | 58.3% | 16.7% | Zodiac |
| ot- | 25.0% | 25.0% | BALANCED |
| **y-** | 28.1% | 46.9% | **SPLIT** |

### y- Family Split Evidence

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

### Interpretation

y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

### Extreme Family Clusters (100% bias)

| Cluster | Bias | Tokens | Shared Folios |
|---------|------|--------|---------------|
| 67 | 100% Zodiac | okeoly, dalal, otalal | f70v2, f72v1 |
| 38 | 100% A/C | om, oir, ykaly | f67v2, f67r2 |
| 139 | 100% Zodiac | okam, okaldy, chas | f72r2, f72v3 |

### Updated Files

- `phases/EFFICIENCY_REGIME_TEST/azc_based_a_clustering.py` - Clustering probe
- `results/azc_based_a_clustering.json` - Full results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.4, y- finding
- `context/SPECULATIVE/efficiency_regimes.md` - Added y- evidence

### Significance

This probe demonstrates that AZC can be used in reverse to reveal structure within Currier A vocabulary that PREFIX morphology alone doesn't show. The y- split provides evidence that some morphological markers encode regime-independent properties.

---

## Version 2.17 (2026-01-11) - Perceptual Discrimination Regime Synthesis

### Summary

**HT oscillation analysis completes the regime interpretation.** The concurrency management probe falsified the parallel-batch hypothesis but revealed the correct explanatory axis: discrimination complexity determines attentional flow patterns.

### Key Finding

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

### HT Oscillation Results

| Family | HT Density | Oscillation Score | Interpretation |
|--------|-----------|-------------------|----------------|
| Zodiac | 0.131 | 0.060 | Sustained attentional flow |
| A/C | 0.236 | 0.110 | Punctuated attentional checkpoints |

**A/C shows ~80% higher HT oscillation than Zodiac.**

### Falsified Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Parallel batch management | FALSIFIED | HT oscillation reversed from prediction |
| Zodiac = high context switching | FALSIFIED | Zodiac has LOWER oscillation |

### The Coherent Explanatory Axis (All Layers Aligned)

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

### Final Interpretation (Tier 3 - VALIDATED)

> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Final validated interpretation
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.3, coherent axis table
- `phases/EFFICIENCY_REGIME_TEST/test_concurrency_management.py` - HT probe
- `results/concurrency_management_probe.json` - HT test output

### Significance

This is the first interpretation that cleanly integrates ALL layers (A, AZC, B, HT, CEI) without contradiction. The internal evidence has been exhausted correctly, by falsification rather than narrative preference.

---

## Version 2.16 (2026-01-11) - Lexical Granularity Regime Validation

### Summary

**This phase empirically tested the "efficiency regime" interpretation of Zodiac vs A/C.** The results localized the signal to the vocabulary layer and falsified behavioral-level claims.

### Key Finding

> **Zodiac vs A/C encodes regimes of lexical discrimination, not regimes of operational difficulty; the control grammar absorbs lexical complexity so that execution behavior remains stable.**

### Test Results

| Test | Result | Interpretation |
|------|--------|----------------|
| MIDDLE Discrimination Pressure | WEAK SUPPORT | 5/15 prefixes show gradient, 0 reversed |
| Residual Brittleness Analysis | **FAILED** | Effect is PREFIX-morphological, not regime-based |
| Universal MIDDLE Negative Control | **PASSED** | Universal MIDDLEs regime-neutral (58.7%), Exclusive biased (64.8%) |
| Family Escape Transfer | PARTIAL | Weak positive correlation (r=0.265) |

**Overall Verdict: WEAK_PARTIAL**

### What IS Supported (Lexical Level)

- MIDDLE discrimination is genuinely family-biased
- Universal MIDDLEs are regime-neutral; Exclusive MIDDLEs show A/C bias
- A/C contexts require finer vocabulary distinctions; Zodiac uses broader categories

### What Is NOT Supported (Behavioral Level - FALSIFIED)

- A/C = operationally brittle (REJECTED)
- Zodiac = operationally forgiving (REJECTED)
- Family affects CEI or recovery (REJECTED)
- Efficiency stress propagates to B programs (REJECTED)

### New Insight

**CEI measures control strain *within* execution, not *between* lexical regimes.**

CEI and AZC family live on orthogonal axes:
- CEI = trajectory management within execution
- AZC family = what distinctions exist ahead of time

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Renamed, tested, revised
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.2, updated regime section
- `phases/EFFICIENCY_REGIME_TEST/` - Four test scripts + synthesis
- `results/efficiency_regime_*.json` - All test outputs

### Methodology Note

This represents a proper falsification attempt, not confirmation bias. The test suite was designed with pre-declared stop conditions and negative controls. The partial failure is a scientific success: it precisely located where the signal exists (vocabulary) vs where it does not (behavior).

---

## Version 2.15 (2026-01-11) - Morphological Binding Phase Closure

### Summary

**This phase resolved the interface between Currier A, AZC, and Currier B.** The binding logic that connects vocabulary composition to constraint activation is now morphologically encoded, causally active, and empirically validated.

### The One-Sentence Takeaway

> **Currier A records define which worlds are allowed to exist, AZC defines what is legal in each world and when recovery is possible, and Currier B blindly executes - leaving the consequences of earlier discriminations unavoidable but structurally bounded.**

### New Constraints

- **C471** - PREFIX Encodes AZC Family Affinity (Tier 2)
  - qo- and ol- strongly enriched in A/C AZC folios (91% / 81%)
  - ot- enriched in Zodiac folios (54%)
  - ch-, sh-, ok- broadly distributed
  - Statistical affinity, not exclusive mapping

- **C472** - MIDDLE Is Primary Carrier of AZC Folio Specificity (Tier 2)
  - PREFIX-exclusive MIDDLEs (77%) exhibit median entropy = 0.0
  - Typically appear in exactly one AZC folio
  - Shared MIDDLEs span multiple folios (18.7% vs 3.3% coverage)
  - MIDDLE is principal determinant of folio-level constraints

- **C473** - Currier A Entry Defines a Constraint Bundle (Tier 2)
  - A entry does not encode addressable object or procedure
  - Morphological composition specifies compatibility signature
  - Determines which AZC legality envelopes are applicable

### Final Definitions (Locked)

- **Currier A record** = Pre-execution compatibility declaration
- **AZC folio** = Complete legality regime (permissions + recoveries)
- **Currier B program** = Blind execution against filtered vocabulary

### Closure Declarations

**Pipeline Resolution & Morphological Binding: CLOSED**

No remaining degrees of freedom. The binding logic is:
- PREFIX -> AZC family affinity
- MIDDLE -> AZC folio specificity
- Together: each vocabulary item carries a compatibility signature

**Additional closures (do NOT reopen):**
- Naming or meaning of AZC folios (they are legality regimes)
- Aligning A entries to specific B programs (vocabulary-mediated)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C471-C473, morphological binding section
- `context/CLAUDE_INDEX.md` - Updated to v2.8, 335 constraints
- `context/MAPS/claim_to_phase.md` - Added C471-C473 mapping
- `phases/INTEGRATION_PROBE/` - Three probe scripts archived
- `results/integration_probe_*.json` - Probe results saved

---

## Version 2.14 (2026-01-11) - Pipeline Resolution Phase Closure

### Summary

**This phase achieved structural closure on the A -> AZC -> B pipeline.** The decisive finding: AZC constraint profiles propagate causally into Currier B execution behavior.

### New Constraints

- **C468** - AZC Legality Inheritance (Tier 2)
  - Tokens from high-escape AZC contexts show 28.6% escape in B
  - Tokens from low-escape AZC contexts show 1.0% escape in B
  - 28x difference confirms causal constraint transfer

- **C469** - Categorical Resolution Principle (Tier 2)
  - Operational conditions represented categorically via token legality
  - Not parametrically via encoded values
  - Physics exists externally; representation is categorical

- **C470** - MIDDLE Restriction Inheritance (Tier 2)
  - Restricted MIDDLEs (1-2 AZC folios): 4.0 B folio spread
  - Universal MIDDLEs (10+ AZC folios): 50.6 B folio spread
  - 12.7x difference confirms constraint transfer

### New Fits

- **F-AZC-015** - Windowed AZC Activation Trace
  - Case B confirmed: 70% of AZC folios active per window
  - High persistence (0.87-0.93): same folios persist
  - AZC is ambient legality field, not dynamic selector

- **F-AZC-016** - AZC->B Constraint Fit Validation
  - MIDDLE restriction transfers: CONFIRMED (12.7x)
  - Escape rate transfers: CONFIRMED (28x)
  - Pipeline causality validated

### Closure Declarations

**Pipeline Resolution Phase: CLOSED**

The A -> AZC -> B control pipeline is structurally and behaviorally validated.

**Do NOT reopen:**
- Entry-level A->B mapping (ruled out by pipeline mechanics)
- Dynamic AZC decision-making (F-AZC-015 closed this)
- Parametric variable encoding (no evidence exists)
- Semantic token meaning (all evidence against)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C468-C470, closure statement
- `context/MODEL_FITS/fits_azc.md` - Added F-AZC-015, F-AZC-016
- `context/MODEL_CONTEXT.md` - Added Section X.C (Representation Principle)
- `context/CLAUDE_INDEX.md` - Updated to v2.7, 320+ constraints

### Archived Scripts

29 scripts from `phases/AZC_constraint_hunting/` archived to `archive/scripts/AZC_constraint_hunting/`

---

## Version 2.13 (2026-01-10)

### E4: AZC Entry Orientation Trace (C460)

**Summary:** Tested whether AZC folios serve as cognitive entry points by analyzing HT trajectories in their neighborhood. Found significant step-change pattern, but it resembles random positions more than A/B entries.

**New Constraint:**

- **C460** - AZC Entry Orientation Effect (Tier 2)
  - Step-change at AZC: p < 0.002 (all window sizes)
  - Pre-entry HT: above average (+0.1 to +0.28 z-score)
  - Post-entry HT: below average (-0.08 to -0.30 z-score)
  - Gradient: decay, R^2 > 0.86

**Critical Nuance:**
- AZC trajectory differs from A and B systems (p < 0.005)
- AZC trajectory does NOT differ from random (p > 0.08)
- Interpretation: AZC is **placed at** natural HT transitions, not **causing** them

**Zodiac vs Non-Zodiac:**
- Zodiac step-change: -0.39 (stronger)
- Non-zodiac step-change: -0.36

**New Files:**
- `phases/exploration/azc_entry_orientation_trace.py`
- `results/azc_entry_orientation_trace.json`
- `context/CLAIMS/C460_azc_entry_orientation.md`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.13, 310 constraints

**Status:** E4 COMPLETE

### E5: AZC Internal Oscillation (Observation Only)

**Question:** Does AZC show internal micro-oscillations matching the global HT rhythm?

**Answer:** No. AZC does not replicate manuscript-wide dynamics internally.
- No significant autocorrelation
- Faster cadence (~3.75 folios vs global ~10)
- Zodiac internally flat; non-Zodiac shows decreasing trend

**Status:** Documented as observation, NOT a constraint. Line of inquiry closed.

**New File:**
- `results/azc_internal_oscillation.json`

---

## Version 2.11 (2026-01-10)

### Intra-Role Differentiation Audit (C458-C459)

**Summary:** Complete audit of intra-folio variation across all four systems. Discovered that risk is globally constrained while human burden and recovery strategy are locally variable. Established HT as anticipatory (not reactive) attention layer.

**Core Finding:**
> The Voynich Manuscript does not vary in how risky its procedures are; it varies in how much *slack, recovery capacity, and human attention* each situation demands - and it encodes that distinction with remarkable consistency across systems.

**New Constraints:**

- **C458** - Execution Design Clamp vs Recovery Freedom (Tier 2)
  - Hazard exposure: CV = 0.04-0.11 (CLAMPED)
  - Recovery operations: CV = 0.72-0.82 (FREE)
  - Regime separation: eta² = 0.70-0.74
  - C458.a: Hazard/LINK mutual exclusion (r = -0.945)

- **C459** - HT Anticipatory Compensation (Tier 2)
  - Quire-level correlation: r = 0.343, p = 0.0015
  - HT before B: r = 0.236, p = 0.032 (significant)
  - HT after B: r = 0.177, p = 0.109 (not significant)
  - Pattern: HT_ANTICIPATES_STRESS
  - C459.a: REGIME_2 shows inverted compensation

**Additional Findings (not constraints):**

- **D2 (AZC Zodiac):** Zodiac folios vary in monitoring vs transition emphasis (CV = 0.15-0.39), no position gradient
- **P1 (Clustering):** 4 natural folio clusters; 4 anomalous folios cluster by HT burden across systems (f41r, f65r, f67r2, f86v5)
- **P2 (Recto-Verso):** No systematic asymmetry (p = 0.79); HT balanced across spreads

**Theoretical Impact:**

| Category | Effect |
|----------|--------|
| Strengthened | Control-artifact model, human-centric design, non-semantic stance |
| Constrained | Danger tied to pages, diagrams encoding execution, HT as reactive |
| Disfavored | Recipe difficulty gradients, didactic sequences, per-page semantics |

**New Files:**
- `phases/exploration/unified_folio_profile.py` - D0
- `phases/exploration/b_design_space_cartography.py` - D1
- `phases/exploration/azc_zodiac_fingerprints.py` - D2
- `phases/exploration/ht_compensation_analysis.py` - D3
- `phases/exploration/folio_personality_clusters.py` - P1
- `phases/exploration/recto_verso_asymmetry.py` - P2
- `phases/exploration/INTRA_ROLE_DIFFERENTIATION_SUMMARY.md` - Synthesis
- `context/CLAIMS/C458_execution_design_clamp.md`
- `context/CLAIMS/C459_ht_anticipatory_compensation.md`

**Results Files:**
- `results/unified_folio_profiles.json` (227 profiles)
- `results/b_design_space_cartography.json`
- `results/azc_zodiac_fingerprints.json`
- `results/ht_compensation_analysis.json`
- `results/folio_personality_clusters.json`
- `results/recto_verso_asymmetry.json`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.11, 309 constraints

**Status:** Intra-Role Differentiation Audit COMPLETE.

### Extended Analysis: HT Temporal Dynamics + Anomalous Folios

**HT Temporal Dynamics:**
- Global decreasing trend: r=-0.158, p=0.017 (HT falls through manuscript)
- ~10-folio periodicity: SNR=4.78 (quire-scale oscillation)
- 9 changepoints detected
- Front-loaded: f39r-f67v2 is HIGH region (48 folios), ending is LOW

**Anomalous Folio Investigation:**

All 4 folios that cluster across system boundaries are HT HOTSPOTS:
| Folio | System | HT | Escape | Status |
|-------|--------|-----|--------|--------|
| f41r | B | 0.296 | 0.197 | HOTSPOT |
| f65r | AZC | 0.333 | n/a | HOTSPOT |
| f67r2 | AZC | 0.294 | n/a | HOTSPOT |
| f86v5 | B | 0.278 | 0.094 | HOTSPOT |

**New Files (Extended):**
- `phases/exploration/ht_temporal_dynamics.py`
- `phases/exploration/anomalous_folio_investigation.py`
- `results/ht_temporal_dynamics.json`
- `results/anomalous_folio_investigation.json`

**Deepest Pattern Discovered:**
> The Voynich is not primarily a manual of actions. It is a manual of **responsibility allocation** between system and human.

---

## Version 2.12 (2026-01-10)

### Post-Differentiation Explorations (E1-E3)

**E1: Quire Rhythm Alignment**
- HT changepoints do NOT align with quire boundaries (enrichment=0.59x, p=0.35)
- HT rhythm is CONTENT-DRIVEN, not production-driven
- Quires differ significantly in mean HT level (H=48.2, p<0.0001, eta²=0.149)
- No consistent internal pattern (43% flat)

**E2: Zero-Escape Characterization (CORRECTION)**
- Only 2 B folios have near-zero escape: f33v (0.009), f85v2 (0.010)
- Neither is an HT hotspot
- Zero-escape is RARE (2.4% of B folios)
- No HT difference between zero-escape and normal B (p=0.22)
- **CORRECTED:** f41r and f86v5 are NOT zero-escape (original finding was due to field name bug)

**E3: Anomalous Folio Deep Dive**
- 13 total HT hotspots (6 A, 5 B, 2 AZC)
- The "anomalous 4" (f41r, f65r, f67r2, f86v5) are not unique
- Only f65r is at a system boundary (A→AZC)
- B hotspots span different regimes (REGIME_2, REGIME_4)
- All anomalous folios have ~2x median HT for their system

**Key Corrections:**
- C459.b "zero-escape → max HT" WITHDRAWN (data error)
- Escape density for f41r: 0.197 (not 0)
- Escape density for f86v5: 0.094 (not 0)

**New Files:**
- `phases/exploration/quire_rhythm_analysis.py`
- `phases/exploration/zero_escape_characterization.py`
- `phases/exploration/anomalous_folio_deep_dive.py`
- `results/quire_rhythm_analysis.json`
- `results/zero_escape_characterization.json`
- `results/anomalous_folio_deep_dive.json`

**Updated Files:**
- `context/CLAIMS/C459_ht_anticipatory_compensation.md` - C459.b corrected

**Status:** Post-Differentiation Explorations COMPLETE

---

## Version 2.10 (2026-01-10)

### B Design Space Cartography (C458)

**Summary:** Interim version during Intra-Role audit. See v2.11 for complete documentation.

---

## Version 2.9 (2026-01-10)

### HT-AZC Placement Affinity (C457)

**Summary:** Single focused test of HT-AZC relationship, following the architectural synthesis. Discovered that HT preferentially marks boundary (S) positions over interior (R) positions in Zodiac AZC.

**New Constraint:**

- **C457** - HT Boundary Preference in Zodiac AZC (Tier 2)
  - S-family HT rate: 39.7%
  - R-family HT rate: 29.5%
  - Difference: 10.3 percentage points (p < 0.0001, V = 0.105)
  - HT preferentially marks BOUNDARIES (sector positions)
  - Supports "attention at phase boundaries" interpretation

**Key Insight:**
> AZC defines the boundary structure of experience; HT marks when human attention should increase inside that structure.

**Files Created:**
- `context/CLAIMS/C457_ht_boundary_preference.md`
- `results/ht_azc_placement_affinity.json`
- `phases/exploration/ht_azc_placement_test.py`

**Status:** HT-AZC investigation CLOSED. No further tests needed.

---

## Version 2.8 (2026-01-10)

### Apparatus-Topology Hypothesis Testing (C454-C456)

**Summary:** Rigorous hypothesis testing of whether AZC encodes apparatus-stage alignment. Properly designed tests with pre-registered kill conditions. Hypothesis FALSIFIED, but produced valuable architectural insights.

**New Constraints:**

- **C454** - AZC-B Adjacency Coupling FALSIFIED (Tier 1)
  - B folios near AZC show NO significant metric differences from B folios far from AZC
  - All window sizes (1-5 folios) returned p > 0.01
  - AZC does NOT modulate B execution
  - AZC and B are topologically segregated

- **C455** - AZC Simple Cycle Topology FALSIFIED (Tier 1)
  - Zodiac AZC is NOT a single ring/cycle
  - Multiple independent cycles (cycle_rank = 5)
  - Non-uniform degree distribution (CV = 0.817)
  - "Literal apparatus diagram" interpretation rejected

- **C456** - AZC Interleaved Spiral Topology (Tier 2)
  - Zodiac shows R-S-R-S alternating pattern
  - R1 -> S1 -> R2 -> S2 -> R3
  - Consistent with cognitive orientation scaffolding
  - Alternation represents interior (R) vs boundary (S) states

**Architectural Synthesis:**

Created `context/ARCHITECTURE/layer_separation_synthesis.md` explaining:
- Why execution (B) must be context-free
- Why orientation (AZC) must be execution-free
- Why legality != prediction
- Why humans need spatial scaffolds for cyclic processes

**The Answer:**
> Why are there spatial diagrams that don't seem to describe anything?
> Because they describe *orientation*, not *operation*.

**Files Created:**
- `context/CLAIMS/C454_azc_b_adjacency_falsified.md`
- `context/CLAIMS/C455_azc_simple_cycle_falsified.md`
- `context/CLAIMS/C456_azc_interleaved_spiral.md`
- `context/ARCHITECTURE/layer_separation_synthesis.md`
- `phases/exploration/apparatus_topology_tests_v2.py`
- `phases/exploration/azc_topology_test.py`
- `results/apparatus_topology_critical_tests_v2.json`
- `results/azc_topology_analysis.json`

**Methodological Note:**
This phase demonstrated proper hypothesis testing:
1. Proposed falsifiable Tier-3 hypothesis
2. Pre-registered kill conditions (K1, K2)
3. Fixed test design flaws when detected
4. Accepted null results
5. Refined understanding based on evidence

**Status:** Apparatus-topology investigation CLOSED. Doors permanently closed on:
- AZC diagrams "representing" apparatus
- R/S/C positions mapping to physical components
- Diagram complexity correlating with execution difficulty

---

## Version 2.7 (2026-01-10)

### AZC-DEEP: Folio Family Architecture (C430-C432)

**Summary:** Completed AZC-DEEP Phases 1-3, discovering that AZC comprises two architecturally distinct folio families. This parallels the CAS-DEEP analysis of Currier A and reveals internal structure beyond "hybrid with placement."

**New Constraints:**

- **C430** - AZC Bifurcation (Tier 2)
  - AZC divides into two families with no transitional intermediates
  - Family 0: Zodiac-dominated, placement-stratified (13 folios)
  - Family 1: A/C-dominated, placement-flat (17 folios)
  - Bootstrap stability = 0.947, Silhouette = 0.34

- **C431** - Zodiac Family Coherence (Tier 2, refines C319)
  - All 12 Zodiac folios form single homogeneous cluster
  - JS similarity = 0.964
  - Higher TTR (0.54), placement entropy (2.25), AZC-unique rate (0.28)
  - Confirms Zodiac as distinct structural mode, not just template reuse

- **C432** - Ordered Subscript Exclusivity (Tier 2)
  - R1-R3, S1-S2 occur exclusively in Zodiac family
  - Binary diagnostic feature (0.96 vs 0.00 depth)
  - Ordered subscripts are family-defining, not AZC-general

**Architectural Impact:**
- AZC is now demonstrably non-monolithic
- Zodiac pages define a separate AZC control mode
- Ordered subscripts become diagnostic, not incidental
- Hybrid story sharpens: Cluster 1 has more shared vocabulary, Cluster 0 has more AZC-unique

**Files Modified:**
- `context/CLAIMS/azc_system.md` - Added C430-C435
- `context/CLAIMS/INDEX.md` - Updated AZC section

### AZC-DEEP Phase 4a: Zodiac Placement Grammar (C433-C435)

**Summary:** Discovered that Zodiac pages implement an extremely strict, block-based placement grammar - stricter than Currier B grammar, not looser.

**New Constraints:**

- **C433** - Zodiac Block Grammar (Tier 2)
  - Placement codes occur in extended contiguous blocks (mean 40-80 tokens)
  - Self-transition rate exceeds 98% for all major codes
  - Zero singletons - once a placement starts, it locks for dozens of tokens
  - **Stricter than Currier B grammar**

- **C434** - R-Series Strict Forward Ordering (Tier 2)
  - R1→R2→R3 only - no backward, no skipping
  - Backward transitions: 0 observed (349 expected)
  - Skip transitions: 0 observed (139 expected)

- **C435** - S/R Positional Division (Tier 2)
  - S-series: Boundary layer (95%+ at line edges)
  - R-series: Interior layer (89-95% interior positions)
  - Two-layer grammar: S marks entry/exit, R fills interior in ordered stages

**Key Insight:**
> The Zodiac pages are not "diagrams with labels." They are a rigid, page-bound control scaffold - the same structure reused twelve times with local vocabulary variation but identical placement logic.

### AZC-DEEP Phase 4b: A/C Family Placement Grammar (C436)

**Summary:** Discovered that the A/C family is ALSO rigid (98% self-transition, zero singletons), but differs from Zodiac in cross-folio consistency. The contrast is uniform-vs-varied, not rigid-vs-permissive.

**New Constraint:**

- **C436** - AZC Dual Rigidity Pattern (Tier 2)
  - Both families: >=98% self-transition, zero singletons
  - Zodiac family: 0.945 cross-folio consistency (uniform scaffold)
  - A/C family: 0.340 cross-folio consistency (folio-specific scaffolds)
  - The contrast is uniform-versus-varied rigidity

**Key Insight:**
> AZC is not "one mode with variation" - it implements two distinct coordination strategies. Every AZC page enforces a hard placement lock. The difference is whether that lock is standardized (Zodiac) or custom (A/C).

**Four-Layer Stack Now Complete:**
- Currier B: Controls systems (execution grammar)
- Currier A: Catalogs distinctions (complexity frontier)
- AZC: Locks context (uniform or custom scaffolds)
- HT: Keeps the human oriented once the lock is engaged

**AZC-DEEP Status:** COMPLETE (discovery phase). All four Voynich systems now show internal, non-trivial, testable architecture

---

## Version 2.6 (2026-01-10)

### C424: Clustered Adjacency + A-B Correlation Investigation + CFR Interpretation

**Summary:** Added C424 (Clustered Adjacency) with three refinements. Completed A-B hazard correlation investigation that falsified failure-memory hypothesis. Established Complexity-Frontier Registry (CFR) as unified interpretation for Currier A. Declared Currier A structurally exhausted.

**New Constraint:**
- **C424** - Clustered Adjacency in Currier A (Tier 2)
  - 31% of adjacent entries share vocabulary (clustered), 69% do not (singletons)
  - Mean cluster size: 3 entries (range 2-20)
  - Autocorrelation r=0.80 exceeds section-controlled null (z=5.85)

**Refinements:**
- **C424.a** - Structural correlates (68% vocabulary divergence between populations)
- **C424.b** - Run-size threshold (size 5+ shows J=0.36 vs size-2 J=0.08)
- **C424.c** - Section P inversion (singletons concentrate at top of pages)

**A-B Correlation Investigation (Exploratory - NO CONSTRAINT):**

| Test | Result | Interpretation |
|------|--------|----------------|
| Hazard density correlation | rho=0.228, p=0.038 | Initial positive |
| Permutation control | p=0.111 | FAILED |
| Frequency-matched control | p=0.056 | FAILED |
| **Pre-registered low-freq MIDDLE** | **rho=-0.052, p=0.651** | **FAIL** |

**Conclusion:** Apparent A-B hazard correlation entirely explained by token frequency. No residual risk-specific signal. Failure-memory hypothesis falsified.

**Unified Interpretation: Complexity-Frontier Registry (CFR)**

> Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

- Currier B provides sequences (how to act)
- Currier A provides discrimination (where fine distinctions matter)
- AZC constrains availability
- HT supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

**Structural Exhaustion Declared:**
Currier A has reached its structural analysis limit. No further purely structural analyses expected to yield new constraints.

**Closed Tests (DO NOT RE-RUN):**
- Hazard density correlation - CLOSED (frequency-explained)
- Forgiveness/brittleness discrimination - CLOSED (inseparable from complexity)

**New files:**
- `CLAIMS/C424_clustered_adjacency.md` - Full constraint documentation
- `phases/exploration/a_b_hazard_correlation.py` - Main correlation script
- `phases/exploration/preregistered_low_freq_test.py` - Decisive final test
- `phases/exploration/a_b_connection_map.py` - Connection map generator
- `phases/exploration/A_B_CORRELATION_RESULTS.md` - Correlation results
- `phases/exploration/A_B_CONNECTION_MAP.md` - Connection map summary
- `phases/exploration/a_b_connection_map.json` - Machine-readable map

**Updated files:**
- `CLAIMS/INDEX.md` - Added C424, version 2.6, count 424
- `CLAIMS/currier_a.md` - Added C424 section, exploratory note with CFR interpretation

**Research phase:** Exploration (1838 entries, 83 folios analyzed)

---

## Version 2.5 (2026-01-09)

### Record Structure Analysis + C250.a Refinement

**Summary:** Complete analysis of Currier A record-level structure using DA-segmented block boundaries.

**Findings (validated but not all constraint-worthy):**
- Block count distribution: 57% single-block, 43% multi-block
- Block size pattern: FRONT-HEAVY (first block ~11 tokens, later ~5)
- Positional prefix tendencies: qo/sh prefer first, ct prefers last (V=0.136)
- Block-level repetition: 58.7% exact, 91.5% high similarity (J>=0.5)
- Record templates: 3-5 patterns cover 77%

**Expert review outcome:**
- C424-C426 initially proposed but REJECTED as constraints
- Positional preferences = tendencies, not rules (no constraint)
- Templates = emergent patterns, not grammar (no constraint)
- Block-aligned repetition = valid refinement of C250

**Accepted:**
- **C250.a** - Block-Aligned Repetition (refinement)
  - Repetition applies to DA-segmented blocks, not partial segments
  - Non-adjacent blocks more similar than adjacent (interleaved enumeration)

**Rejected (kept as descriptive findings only):**
- Positional prefix preferences (tendency, not constraint)
- Record structure templates (emergent, not grammar)

**New files:**
- `phases/exploration/record_structure_analysis.py`
- `phases/exploration/block_position_prefix_test.py`
- `phases/exploration/repetition_block_alignment.py`
- `phases/exploration/RECORD_STRUCTURE_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C250.a refinement under Multiplicity Encoding

**Note:** Constraint count unchanged (423). Findings describe USE of structure, not design limits.

---

## Version 2.4 (2026-01-09)

### C410.a: Sister Pair Micro-Conditioning (Refinement)

**Summary:** Refinement documenting compositional conditioning of sister-pair choice in Currier A.

**Findings:**
- MIDDLE is the PRIMARY conditioning factor (25.4% deviation from 50%)
- Some MIDDLEs are >95% one sister (yk: 97% ch, okch: 96% ch)
- Suffix compatibility provides secondary conditioning (22.1% deviation)
- Adjacent-token effects favor run continuation (ch->ch: 77%)
- DA context has ZERO effect (V=0.001) - confirms DA is structural
- Section effect is background bias (V=0.078)

**Interpretation:**
Sister pairs encode equivalent classificatory roles but permit compositionally conditioned surface variation. Preferences are local within the compositional system - no new categories, semantics, or hierarchies.

**New files:**
- `phases/exploration/sister_pair_conditioning.py`

**Updated files:**
- `CLAIMS/C408_sister_pairs.md` - Added C410.a refinement section

**Note:** This closes Priority 3 (sister-pair conditioning). Does not break equivalence class status.

---

## Version 2.3 (2026-01-09)

### C346.b: Component-Level Adjacency Drivers (Refinement)

**Summary:** Refinement note added to C346 documenting component-level analysis of adjacency coherence.

**Findings:**
- Removing DA tokens increases adjacency coherence (+18.4%)
- MIDDLE-only adjacency is LOWER than full-token (2.10x vs 2.98x)
- PREFIX and SUFFIX drive local adjacency more than MIDDLE
- DA-segmented blocks show 26.8x internal coherence

**Key insight:** Currier A adjacency reflects domain-level continuity (PREFIX) with item-level variation (MIDDLE). This is registry organization, not semantic chaining.

**New files:**
- `phases/exploration/payload_refinement.py`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C346.b refinement note

**Note:** This is a refinement, not a new constraint. Does not change C346's core finding.

---

## Version 2.2 (2026-01-09)

### C423: PREFIX-BOUND VOCABULARY DOMAINS + C267 Amendment

**Summary:** New Tier-2 constraint establishing MIDDLE as the primary vocabulary layer in Currier A, with prefixes defining domain-specific vocabularies. Amendment to C267 corrects "42 common middles" to full census of 1,184.

**Finding (MIDDLE census):**
- 1,184 distinct MIDDLEs identified (full inventory)
- 80% (947) are PREFIX-EXCLUSIVE
- 20% (237) are shared across prefixes
- 27 UNIVERSAL middles appear in 6+ prefixes
- Top 30 account for 67.6% of usage
- MIDDLE entropy: 6.70 bits (65.6% efficiency)

**PREFIX vocabulary sizes:**
| Prefix | Exclusive MIDDLEs |
|--------|-------------------|
| ch | 259 (largest) |
| qo | 191 |
| da | 135 |
| ct | 87 |
| sh | 85 |
| ok | 68 |
| ot | 55 |
| ol | 34 (smallest) |

**DA-MIDDLE coherence finding:**
- DA-segmented sub-records do NOT exhibit increased MIDDLE similarity
- Adjacent segment J=0.037 vs random segment J=0.039 (0.94x)
- DA separates structure, not vocabulary content

**Interpretation:**
- Prefixes define domain-specific vocabularies
- MIDDLEs are selected from prefix-specific inventories
- Shared/universal middles form small cross-domain core
- This is the vocabulary layer of Currier A

**C267 amendment:**
- Original: "42 common middles" (discovery-era simplification)
- Updated: "1,184 unique (27 universal)" with cross-reference to C423
- Added note explaining scope mismatch

**New files:**
- `phases/exploration/middle_census.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C423, version 2.2, count 423
- `CLAIMS/currier_a.md` - Added Vocabulary Domains section, MIDDLE coherence note to C422
- `CLAIMS/C267_compositional_morphology.md` - Amended MIDDLE count and added note

**Research phase:** Exploration (25,890 tokens parsed, 17,589 with MIDDLE)

---

## Version 2.1 (2026-01-09)

### C422: DA as Internal Articulation Punctuation

**Summary:** New Tier-2 constraint documenting DA's structural punctuation role within Currier A entries.

**Finding:**
- 75.1% of internal DA occurrences separate adjacent runs of different marker prefixes (3:1 ratio)
- All DA tokens (daiin and non-daiin) exhibit identical separation behavior (74.9% vs 75.4%)
- Entries with DA are significantly longer (25.2 vs 16.4 tokens) and more prefix-diverse (3.57 vs 2.01)
- DA-segmented regions form prefix-coherent blocks

**Section gradient:**
- H (Herbal): 76.9% separation rate (3.3:1)
- P (Pharmaceutical): 71.7% (2.5:1)
- T (Text-only): 65.0% (1.9:1)
- Direction invariant across all sections

**Interpretation:**
- DA does not encode category identity
- DA marks internal sub-record boundaries within complex registry entries
- DA functions as punctuation rather than classifier
- Role is globally infrastructural, intensity correlates with section complexity

**New files:**
- `phases/exploration/da_punctuation_analysis.py`
- `phases/exploration/da_deep_dive.py`
- `phases/exploration/da_section_invariance.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C422, version 2.1, count 422
- `CLAIMS/currier_a.md` - Added DA Internal Articulation section

**Research phase:** Exploration (1838 entries, 3619 DA tokens analyzed)

---

## Version 2.0 (2026-01-09)

### C421: Section-Boundary Adjacency Suppression + C346.a Refinement

**Summary:** New Tier-2 constraint documenting section boundary effects on adjacent entry similarity. Refinement note added to C346 explaining similarity decomposition.

**C421 Finding:**
- Adjacent entries crossing section boundaries exhibit 2.42x lower vocabulary overlap
- Same-section adjacent: J=0.0160
- Cross-section adjacent: J=0.0066
- p < 0.001

**C346.a Refinement:**
- 1.31x adjacency similarity driven by MIDDLE (1.23x) and SUFFIX (1.18x)
- Weak contribution from marker prefixes (1.15x)
- Local ordering reflects subtype/property similarity, not marker class

**Interpretation:**
- Section boundaries (H/P/T) are primary hard discontinuities in Currier A
- Catalog organized by content/topic first, markers classify within clusters
- Does NOT change what Currier A represents; tightens characterization

**New files:**
- `phases/exploration/adjacent_entry_analysis.py`
- `phases/exploration/adjacent_section_boundary.py`
- `phases/exploration/ADJACENT_ENTRY_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C421, version 2.0, count 421
- `CLAIMS/currier_a.md` - Added C346.a refinement, C421 section

**Research phase:** Exploration (1838 entries, 114 folios analyzed)

---

## Version 1.9 (2026-01-09)

### C420: Currier A Folio-Initial Positional Exception

**Summary:** New Tier-2 constraint documenting positional tolerance at folio boundaries in Currier A.

**Finding:**
- First-token position in Currier A permits otherwise illegal C+vowel prefix variants (ko-, po-, to-)
- 75% failure rate at position 1 vs 31% at positions 2-3
- C+vowel prefixes: 47.9% at position 1, 0% elsewhere
- Fisher exact p < 0.0001
- Morphologically compatible (ko- shares 100% suffix vocabulary with ok-)

**Interpretation:**
- Positional tolerance at codicological boundaries (common in medieval registries)
- Does NOT imply headers, markers, semantic categories, or enumeration
- No revision to C240 (marker families) or C234 (position-free) required

**New files:**
- `CLAIMS/C420_folio_initial_exception.md` - Full constraint documentation
- `phases/exploration/first_token_*.py` - Research scripts
- `phases/exploration/FIRST_TOKEN_SYNTHESIS.md` - Research synthesis

**Updated files:**
- `CLAIMS/INDEX.md` - Added C420, version 1.9, count 420
- `CLAIMS/currier_a.md` - Added Positional Exception section

**Research phase:** Exploration (48 folios analyzed)

---

## Version 1.8 (2026-01-09)

### HT/AZC FINAL CLOSED

**Summary:** Completed final constraint audit; verified C412; declared HT and AZC sections FINAL CLOSED.

**Audit results:**
- HT: 21 constraints + 1 superseded - ALL PASS
- AZC: 23 constraints - ALL PASS
- Notes: HT-AZC-NOTE-01, AZC-NOTE-01 correctly scoped

**C412 verification:**
- Original methodology replicated exactly
- Results reproduced: rho=-0.327 (original -0.326), p=0.0027 (original 0.002)
- Prior discrepancy explained: wrong metric used in re-analysis (ch-density vs ch-preference)
- Review flag removed

**Updated files:**
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added verification section
- `CLAIMS/INDEX.md` - Removed ⚠️ REVIEW marker

**New files:**
- `phases/exploration/c412_verification.py` - Verification script

**Final status:**
| Section | Status |
|---------|--------|
| Human Track (HT) | FINAL CLOSED |
| AZC System | FINAL CLOSED |
| Sister Pairs | FINAL CLOSED |

---

## Version 1.7 (2026-01-09)

### HT-AZC Third Anchoring Pressure

**Summary:** Identified AZC-specific HT pattern (diagram label concentration).

**Updated files:**
- `CLAIMS/human_track.md` - Added HT-AZC-NOTE-01, updated frozen statement

**Key finding:**
- AZC HT uniquely shows BOTH line-initial AND line-final enrichment
- Driven by L-placement (label) text: 88.8% initial, 95% final
- L-placement lines are short (1-3 tokens) with 15.1% HT density
- Establishes **third anchoring pressure**: diagram geometry (label positions)

**Three-system refinement:**
| System | Anchoring Pressure |
|--------|-------------------|
| Currier A | Registry layout (entry boundaries) |
| Currier B | Temporal/attentional context |
| AZC | Diagram geometry (label positions) |

---

## Version 1.6 (2026-01-09)

### Data Source Documentation + AZC/C412 Updates

**Summary:** Added data source documentation; documented AZC findings; flagged C412 discrepancy.

**Updated files:**
- `SYSTEM/METHODOLOGY.md` - Added "Canonical Data Source" section
- `CLAIMS/azc_system.md` - Added AZC-NOTE-01 (qo-depletion refinement)
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added review flag
- `CLAIMS/INDEX.md` - Added review marker to C412

**Key additions:**

1. **Data source documentation:**
   - PRIMARY DATA FILE: `data/transcriptions/interlinear_full_words.txt`
   - WARNING about EVA vs standard vocabulary encoding

2. **AZC-NOTE-01:** qo-prefix depletion (2.8x lower than B), refines C301/C313

3. **C412 review flag:** Re-analysis finds anticorrelation in Currier A (rho=-0.334, p=0.0003), NOT in B (rho=-0.089, p=0.42). Requires reconciliation with original SISTER phase.

**Issue caught:** During AZC exploration, wrong transcription file was initially used. All previous constraints verified safe.

---

## Version 1.5 (2026-01-09)

### HT Formal Hierarchy

**Summary:** Established canonical hierarchy for Human Track layer. Adds C414-C419.

**New files:**
- `CLAIMS/HT_HIERARCHY.md` - Formal hierarchy document (canonical)

**Updated files:**
- `CLAIMS/human_track.md` - Added C414-C419, system-specific refinement
- `CLAIMS/HT_CONTEXT_SUMMARY.md` - Updated with hierarchy reference
- `CLAIMS/INDEX.md` - Count 411→419, added 6 new constraints
- `CLAUDE_INDEX.md` - Count update, navigation to HT_HIERARCHY.md

**Constraints added:**
| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C414 | Strong Grammar Association | 2 | chi2=934, p<10^-145 |
| C415 | Non-Predictivity | 1 (FALSIFICATION) | MAE worsens with HT conditioning |
| C416 | Directional Asymmetry | 2 | V=0.324 vs 0.202 (1.6x) |
| C417 | Modular Additive | 2 | No synergy (p=1.0) |
| C418 | Positional Without Informativeness | 2 | Bias exists but non-predictive |
| C419 | HT Positional Specialization in A | 2 | Entry-aligned, seam-avoiding |

**Terminology guardrail established:**
- DO: "aligned with", "correlated with", "position-biased"
- DON'T: "marks", "encodes", "annotates", "means"

**Model refinement:**
- Currier A: HT aligned with registry layout (entry boundaries)
- Currier B: HT aligned with temporal/attentional context
- Same layer, different anchoring pressures

---

## Version 1.4 (2026-01-09)

### Phase: STRUCTURE_FREEZE_v1

**Summary:** Formal freeze of structural inspection layer. Transitions project from foundational reconstruction to deliberate post-structure paths.

**Components frozen:**
- **Basic Inspection v1** (`apps/script_explorer/BASIC_INSPECTION.md`)
  - Currier A registry parsing and roles
  - Currier B grammar roles (49-class, conservative binding)
  - AZC placement binding (`R/R1/R2/R3`, `S/S1/S2`, `C`, `MULTI`)
  - HT isolation and override behavior
  - Global properties (prefix family, kernel affinity, escape)

- **Execution Inspector v0.1** (`apps/script_explorer/EXECUTION_INSPECTOR.md`)
  - Grammar-only execution inspection
  - `grammar_bound` semantics
  - Conservative UNKNOWN handling
  - No hazards, order, or kernel contact beyond grammar anchors

**Repository rules enforced:**
- ❌ Do not alter parsing logic
- ❌ Do not alter classification logic
- ❌ Do not alter role assignment tables
- ❌ Do not alter system boundaries
- ❌ Do not reinterpret UNKNOWNs
- ❌ Do not extend execution semantics implicitly
- ❌ Do not weaken system gating (A/B/AZC/HT)

**Post-freeze paths available:**
1. Documentation & Consolidation (RECOMMENDED)
2. Visualization / UX (SAFE)
3. Deeper Execution Semantics (ADVANCED, requires new phase)

**Intent:** Preserve structural integrity. Expansion is a choice, not an accident.

---

## Version 1.0 (2026-01-08)

### Initial Release

**Created:** Context expansion system to replace monolithic CLAUDE.md

**Structure:**
- `context/` directory with 9 subdirectories
- `CLAUDE_INDEX.md` as primary entry point (~4k tokens)
- Progressive disclosure architecture
- 57 markdown files total

**Directories:**
- `SYSTEM/` - Meta-rules, tiers, methodology (5 files)
- `CORE/` - Tier 0-1 facts (3 files)
- `ARCHITECTURE/` - Structural analysis by text type (5 files)
- `OPERATIONS/` - OPS doctrine, program taxonomy (3 files)
- `CLAIMS/` - 411 constraints indexed (24 files: 1 index, 16 individual claims, 7 grouped registries)
- `TERMINOLOGY/` - Key definitions (3 files)
- `METRICS/` - Quantitative facts (4 files)
- `SPECULATIVE/` - Tier 3-4 content (4 files)
- `MAPS/` - Cross-references (3 files)

**Design Principles:**
1. Entry point stays slim (<10k tokens)
2. One concept per file
3. ≤15k tokens per file
4. Every claim declares Tier + closure
5. No analysis in context files
6. Archive is append-only
7. Context points to archive

**Migration:**
- Content extracted from CLAUDE.md v1.8 (95KB, ~30k tokens)
- Original preserved as `archive/CLAUDE_v1.8_2026-01-08.md`
- CLAUDE.md converted to redirect

---

## Version 1.3 (2026-01-08)

### Added: Constraint-First Reasoning Protocol

**Summary:** Added methodology for checking constraints before speculating, and guidance on when/how to question constraints.

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added two new sections:
  - "Constraint-First Reasoning" - rule to search constraints before interpreting
  - "Questioning Constraints" - when and how to challenge existing claims
- `context/CLAUDE_INDEX.md` - Added stop condition reminder and note that questioning is allowed

**Motivation:** During conversation, speculated that "Currier A entries might reference the same categories B executes" — but C384 explicitly falsifies this. Checking constraints first would have prevented the error.

**Key principles added:**
- Search CLAIMS/ before reasoning about relationships
- Distinguish "constrained" from "undocumented" (gap ≠ permission)
- Cite constraint numbers or flag as research gap
- Questioning is allowed but must be explicit, not silent override
- Tier determines revisability (0=frozen, 2=reopenable with evidence)

---

## Version 1.2 (2026-01-08)

### Added: Structural Intuition Clarification

**Summary:** Added documentation to prevent the misinterpretation that "neutral/unhighlighted tokens are unknown."

**Files updated:**
- `context/CLAUDE_INDEX.md` - Added three new sections:
  - "How to Think About Tokens (Structural Layer)"
  - "Why Visualization Tools Highlight Only Some Tokens"
  - "Structural Analysis vs Interpretive / Probabilistic Reasoning"

**Clarifications made:**
- Tokens are surface realizations, not functional operators
- Functional behavior determined at instruction-class level
- High hapax rates explained by compositional morphology
- "Neutral" means "non-contrastive", not "unknown"
- Visualization highlighting is a UI choice, not knowledge boundary
- Bayesian/probabilistic reasoning explicitly supported in interpretive layer

**No constraint changes:** This is a documentation-only update for human intuition alignment. No tiers, claims, or conclusions were altered.

---

## Version 1.1 (2026-01-08)

### Added: Research Automation

**Summary:** Added skills, hooks, and workflow documentation for automated research.

**Files created:**
- `.claude/skills/phase-analysis/SKILL.md` - Automatic phase analysis
- `.claude/skills/constraint-lookup/SKILL.md` - Constraint search and citation
- `.claude/settings.json` - Hook configuration
- `archive/scripts/validate_constraint_reference.py` - Constraint validation
- `archive/scripts/extract_phase_metrics.py` - Metrics extraction

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added "Research Workflow (Automated)" section
- `context/SYSTEM/HOW_TO_READ.md` - Added multi-branch access patterns
- `context/CLAUDE_INDEX.md` - Added "Automation" section

**New workflows:**
- Phase Analysis Protocol (automatic)
- Constraint Lookup Protocol (automatic)
- Constraint reference validation (hook)

---

## Future Entries

When updating context, add entries in this format:

```markdown
## Version X.Y (YYYY-MM-DD)

### [Type: Added/Changed/Removed/Fixed]

**Summary:** Brief description

**Files affected:**
- `path/to/file.md` - what changed

**Constraint changes:**
- C### added/updated/removed

**Source:** Phase PHASE_NAME (if applicable)
```

---

## Navigation

← [HOW_TO_READ.md](HOW_TO_READ.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
