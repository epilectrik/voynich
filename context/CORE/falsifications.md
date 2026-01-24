# Consolidated Falsifications (Tier 1)

**Status:** CLOSED | **Tier:** 1

---

## Purpose

These hypotheses have been **explicitly tested and rejected**. Each has documented falsifying evidence. Do not retry these approaches.

---

## Major Falsifications

### Language Encoding
**Status:** FALSIFIED
**Evidence:** Phase X.5 found 0.19% reference rate
**Meaning:** Tokens do not behave like words. No referential structure exists.

### Cipher Encoding
**Status:** FALSIFIED
**Evidence:** Phase G showed cipher transforms DECREASE mutual information
**Meaning:** If this were cipher, decryption would increase structure. The opposite happens.

### Glyph-Level Semantics
**Status:** FALSIFIED
**Evidence:** Phase 19 found 0 identifier tokens
**Meaning:** Individual glyphs don't carry meaning. Tokens are the minimal unit.

### Illustration-Dependent Logic
**Status:** FALSIFIED
**Evidence:** Phase ILL showed swap invariance p=1.0; Phase ILL-TOP-1 tested 8 hypotheses (topology, order, quire, scaffolding, geometry) - all failed
**Meaning:** Swapping illustrations doesn't affect text analysis. Visual similarity does not predict constraint similarity at any level. Illustrations are epiphenomenal to grammar.

### Step-by-Step Recipe Format
**Status:** FALSIFIED
**Evidence:** Phase FSS showed families are emergent, not designed
**Meaning:** The text is not organized as discrete recipes with beginnings and endings.

---

## Specific Claim Falsifications

| Claim | Evidence | Phase |
|-------|----------|-------|
| Fire degree predicts PP signature | Material class conflation, p>0.05 | PP_MULTICLASS_TEST |
| Bayesian posteriors valid for PP prediction | 0.9x enrichment in Bayesian-only records | PP_DILUTION_TEST |
| Text encodes language | 0.19% reference rate | X.5 |
| Tokens have translatable meanings | 0 identifier tokens | 19 |
| Illustrations are instructional | Swap invariance p=1.0 | ILL |
| Illustrations organize constraints | 8/8 tests failed | ILL-TOP-1 |
| Plants indicate ingredients | Dual-use history (perfumery, medicine) | PCIP |
| Sections = apparatus configs | F-ratio 0.37 | PCS |
| Programs correlate with plant morphology | All p>>0.05 | PPC |
| 49-class grammar generalizes to full manuscript | 13.6% Currier A coverage | CAud |
| Hazard topology is universal | 5 violations in Currier A | CAud |
| "100% convergence to STATE-C" | Only 57.8% terminate in STATE-C | SEL-F |
| Procedural chaining (folios form macro-sequences) | Tests 1-6 falsified | SEL-F |
| STATE-C marks material-family boundaries | TEST 11 p=1.0 | SEL-F |
| Sharp material-family clustering | Silhouette=0.018 (highly overlapping) | SEL-F |
| Hazard "100% bidirectional" | 65% asymmetric | SEL-D |
| Hazard "KERNEL_ADJACENT clustering" | 59% distant from kernel | SEL-D |
| Human-track "7 coordinate functions" | Overfitting | SEL-E |
| HT 99.6% LINK-proximal | ρ=0.010, p=0.93 (decoupled) | HTD |
| Repetition encodes ratios/proportions | No cross-entry comparison, no reference frame | EXT-9B |

---

## Adversarial Audit Results

Eight attack vectors were tested against the model:

| Attack | Result |
|--------|--------|
| Kernel Collapse | SURVIVES |
| Cycle Illusion | WEAKENED (documented) |
| Grammar Minimality | WEAKENED (documented) |
| Random Baseline | SURVIVES |
| Folio Independence | SURVIVES |
| Grammar Collapse | SURVIVES |
| DSL Discriminator | SURVIVES |
| Family Syntax | SURVIVES |

**Overall:** 6/8 attacks failed to falsify the model. 2/8 weakened specific claims (now documented with caveats).

---

## Purpose Classes Eliminated

The following purpose classes were eliminated by structural incompatibility:

- Cipher/hoax
- Encoded language
- Recipe/pharmacology
- Herbarium/taxonomy
- Medical procedure
- Astronomical calculation
- Ritual/symbolic practice
- Educational text
- Discrete batch operations
- Fermentation
- Glassmaking/metallurgy
- Dyeing/mordanting

**Only surviving purpose class:** Continuous closed-loop process control

---

## PP Analysis Falsifications (2026-01-23)

### Fire Degree as PP Axis (FALSIFIED)
**Hypothesis:** Fire degree (thermal tolerance from Brunschwig: 1=gentle, 2=standard, 3=moderate) predicts PP signature.
**Test:** Compared PP profiles across fire degree groups using material_class_priors.json mapping.
**Result:** Fire 1 conflates animals + flowers + fungi (all "gentle" thermal tolerance). The conflation dilutes PP signal. Only 1 PP ('ke') showed >2x enrichment, p=0.06 (not significant).
**Conclusion:** Thermal tolerance ≠ handling complexity. Material class (animal vs herb) is the relevant PP axis, not fire degree.
**Status:** Do not retry fire degree → PP mapping.

### Bayesian Class Posteriors for PP Prediction (FALSIFIED)
**Hypothesis:** Bayesian class posteriors (from material_class_priors.json) can identify material-class records for PP analysis.
**Test:** Compared PP enrichment in C505's 13 procedurally-identified animal records vs 40 Bayesian-identified "animal" records.
**Result:**
- C505 records: 15.8x, 8.7x, 5.1x enrichment for 'te', 'ho', 'ke'
- Bayesian records: 5.1x, 3.8x, 2.5x (diluted)
- Bayesian-only records (extra 27): 0.0x, 1.4x, 1.2x (baseline noise)
**Conclusion:** Bayesian posteriors identify taxonomically similar records, not procedurally equivalent records. The extra 27 records are false positives with baseline PP rates.
**Status:** Do not use Bayesian class posteriors for PP discrimination. Use procedural trace methodology (B→A via product-type-exclusive MIDDLEs).

### PP Composition Predicts B Class Survival (FALSIFIED)
**Hypothesis:** PP MIDDLE composition (which specific PPs are present) predicts B class survival count or composition.
**Test:** Compared 16 animal records (identified via RI MIDDLEs) to 1,563 baseline records.
**Results:**
- Survival count: Animal 30.7±10.4 vs Baseline 32.3±8.3 classes (t-test p=0.448, NS)
- Class composition: Cosine similarity = 0.995, JS divergence = 0.0019
- Per-class Fisher's exact: 0 of 49 classes significant at p<0.05
**Conclusion:** PP composition does NOT predict B-side behavior. PP is a capacity variable (count matters, r=0.72), not a routing variable (composition irrelevant). Material-class PP profile differences (C505) are A-side organizational markers that do not propagate to B execution.
**Status:** Do not test PP composition → B execution. PP functional role is now fully characterized.

### PP Profiles Select B-Side Tactics (FALSIFIED)
**Hypothesis:** Different PP profiles cause different operational strategies or grammar biases in B.
**Test:** Class composition analysis across PP profile groups.
**Result:** Cosine similarity = 0.995 between animal and baseline class profiles.
**Conclusion:** PP does not select tactics. It only widens the arena (capacity). This null result protects the semantic ceiling (C171, C469) — if PP encoded material-specific execution, it would violate the pure operational constraint.
**Status:** PP composition → B tactics pathway is closed.

---

## Rule

**Do not retry falsified approaches.**

If you believe a falsification was incorrect, first review the phase documentation. The evidence is documented. If you still disagree, you are likely misunderstanding the scope or methodology.

---

## Navigation

← [model_boundary.md](model_boundary.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
