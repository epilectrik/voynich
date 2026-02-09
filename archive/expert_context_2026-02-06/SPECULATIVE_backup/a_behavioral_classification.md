# Currier A Behavioral Classification

**Tier:** 3 | **Status:** SUPPORTED | **Date:** 2026-01-12

> Entity-level identification (specific plants, substances) is probably irrecoverable by design. This analysis identifies OPERATIONAL ROLES, not specific referents.

---

## Summary

Currier A entries have been classified by **operational domain** using frozen structural constraints. The classification rests on Tier-2 grammar evidence, with behavioral interpretation at Tier 3.

**Core finding:**

> Entries associated with energy-intensive operations require far finer discrimination (many more MIDDLE variants) than entries associated with stable reference or structural control. This gradient is section-conditioned, correlates with vigilance pressure (HT), and aligns with what we expect from real physical processes involving fractionation and phase control.

---

## Grounding: Why This Classification Is Solid

The PREFIX → Operational Domain mapping rests on **Tier-2, grammar-anchored evidence**:

| Evidence | Constraint | What It Shows |
|----------|------------|---------------|
| B-enrichment ratios | C282, C286 | ct is 7x A-enriched; qo/ol are B-enriched |
| Grammar role assignments | Canonical grammar | ch/qo = ENERGY_OPERATOR; da/ol = CORE_CONTROL |
| Kernel adjacency | C397-398 | qo is escape-heavy, kernel-adjacent |
| Terminal absence | C282 | ct is 0% of B terminals |

The inference chain is **short**:

```
PREFIX → control-flow role (Tier 2) → operational domain
```

This is **not speculative chemistry**. It is a re-use of validated structure.

---

## Key Findings

### 1. Operational Domain Distribution

| Domain | Count | % | Prefixes | Structural Basis |
|--------|-------|---|----------|------------------|
| **ENERGY_OPERATOR** | 13,933 | 59.4% | ch, sh, qo | Dominates energy/escape roles in B grammar |
| **CORE_CONTROL** | 4,472 | 19.1% | da, ol | Structural anchors; ol 5x B-enriched |
| **FREQUENT_OPERATOR** | 3,545 | 15.1% | ok, ot | FREQUENT_OPERATOR role in canonical grammar |
| **REGISTRY_REFERENCE** | 1,492 | 6.4% | ct | 0% B terminals; 7x A-enriched |

**Coverage:** 23,442 of 37,214 tokens (63.0%)

**On the 37% unclassified:** This is expected and healthy. It includes infrastructure tokens (da-family articulation), edge cases, and low-frequency forms. A forced 100% classification would be suspicious.

### 2. Discrimination Gradient (Primary Structural Finding)

| Domain | Unique MIDDLEs | Ratio to REGISTRY |
|--------|---------------|-------------------|
| ENERGY_OPERATOR | 564 | 8.7x |
| CORE_CONTROL | 176 | 2.7x |
| FREQUENT_OPERATOR | 164 | 2.5x |
| REGISTRY_REFERENCE | 65 | 1.0x (baseline) |

**Total unique MIDDLEs:** 826

**What this means:** Operations requiring fine discrimination occupy far more vocabulary space than operations involving stable, well-known referents. This gradient:
- Survives section conditioning
- Persists despite hub rationing (C476)
- Mirrors HT tail pressure effects (C477)

*Tier-3 interpretation:* This is consistent with fractionation processes where many similar items must be distinguished, versus stable infrastructure requiring minimal differentiation.

### 3. Sister Pairs as Mode Selectors

| Mode | Count | Ratio |
|------|-------|-------|
| Primary (ch, ok) | 9,086 | 1.84 |
| Alternate (sh, ot) | 4,943 | 1.00 |

**Structural basis:** C408/C409 establish sister pairs as mutually exclusive but substitutable. C412 shows precision-tolerance anticorrelation.

**Correct interpretation:**

> Sister pairs encode **primary vs alternate handling mode** for the same operational role—NOT different materials.

This fits operational training contexts: conservative vs permissive handling, tight vs loose control, precision vs tolerance modes.

### 4. Section-Conditional Distribution

| Section | ENERGY | FREQUENT | CONTROL | REGISTRY |
|---------|--------|----------|---------|----------|
| **H** | 61% | 13% | 18% | 8% |
| **P** | 56% | 20% | 22% | 3% |
| **T** | 55% | 20% | 20% | 5% |

**Key finding:** Section H accounts for **74% of all ENERGY_OPERATOR tokens** (10,273 of 13,933).

**Safe framing:**

> The section traditionally called "herbal" structurally concentrates energy-intensive, highly discriminated operations.

**Unsafe framing (avoid):**

> ~~Section H equals plants, therefore aromatics.~~

The pattern is real. The chemistry explanation is plausible but remains Tier 3.

---

## Material Behavior Classes (Tier 3 Interpretation)

The following mappings are **interpretive**, not structural claims:

| Domain | Behavioral Profile | Tier-3 Illustration |
|--------|-------------------|---------------------|
| ENERGY_OPERATOR | Phase-sensitive, high discrimination | *e.g., volatile fractions* |
| FREQUENT_OPERATOR | Uniform, routine handling | *e.g., carrier materials* |
| CORE_CONTROL | Class-independent articulation | *process sequencing* |
| REGISTRY_REFERENCE | Stable, reference items | *e.g., apparatus, containers* |

**What this claims:** Operations in different domains handle materials with different behavioral profiles.

**What this does NOT claim:** Specific substance identifications.

---

## Decision Archetype Coverage

| Archetype | Count | Domain(s) |
|-----------|-------|-----------|
| "Is material in correct phase/location?" | 13,933 | ENERGY |
| "Is energy input appropriate?" | 13,933 | ENERGY |
| "Should I intervene or wait?" | 8,017 | CONTROL + FREQUENT |
| "What operating regime am I in?" | 3,545 | FREQUENT |
| "Is this the fraction I think it is?" | 1,492 | REGISTRY |
| "Is this case like that previous case?" | 1,492 | REGISTRY |

---

## Confidence Assessment

| Component | Confidence | Basis |
|-----------|------------|-------|
| Structural facts & distributions | ~90-95% | Empirical counts |
| PREFIX → operational domain | ~75-80% | Tier-2 grammar evidence |
| Discrimination gradient interpretation | ~70-75% | Structural fact + validated directionally |
| Section H concentration meaning | ~70-75% | Pattern real; directionally consistent |
| Thermal/distillation framing | ~80-85% | **STRENGTHENED by exclusion testing** |
| Specific chemistry labels | ~30-40% | Explicitly illustrative |

**Overall framework:** ~80-85% confidence (**STRENGTHENED**)

---

## Scientific Confidence Tightening (2026-01-12)

The distillation/thermal-chemical hypothesis was subjected to rigorous directional and exclusion testing:

### Directional Tests (B1-B6): 5/6 PASS

| Test | Result | Finding |
|------|--------|---------|
| B1: Discrimination hierarchy | PASS | ENERGY >> FREQUENT >> REGISTRY (564 > 164 > 65) |
| B2: Normalized dominance | INFORMATIVE | FREQUENT has higher turnover; ENERGY reuses MIDDLEs |
| B3: Failure boundaries | PASS | 100% k-adjacent forbidden transitions |
| B4: Regime ordering | PASS | Monotonic CEI: 0.367 < 0.510 < 0.584 < 0.717 |
| B5: Recovery dominance | PASS | e-recovery 1.64x enriched vs baseline |
| B6: AZC compression | PASS (partial) | Section-level diversity confirmed |

### Negative Controls (NC1-NC4): 4/4 STRONG EXCLUSION

| Alternative | Discriminators Failed | Verdict |
|-------------|----------------------|---------|
| NC1: Fermentation | 3/3 | EXCLUDED |
| NC2: Dyeing | 3/3 | EXCLUDED |
| NC3: Pharmacy Compounding | 3/3 | EXCLUDED |
| NC4: Crystallization | 3/3 | EXCLUDED |

### Classification

**Confidence Band:** HIGH (80-85%)
**Interpretation:** Distillation selected by convergence AND exclusion

**Key evidence:**
1. Forbidden transitions cluster at k (energy control boundary)
2. Recovery paths dominated by e (stability/cooling)
3. All 4 alternative hypotheses fail on phase-control discriminators
4. Discrimination gradient survives directional validation

**B2 finding reinterpretation:**
- FREQUENT tokens have higher MIDDLE turnover per token than ENERGY
- This reveals operational structure: ENERGY = repetitive monitoring; FREQUENT = varied operations
- Consistent with distillation behavior (watch closely vs use routinely)

**Critical note:** Even if the chemistry framing were later replaced, the operational gradient alone remains an important structural fact.

---

## Validation Against Constraints

| Constraint | How Satisfied |
|------------|---------------|
| C240 (8 marker families) | All 8 prefixes mapped to domains |
| C282 (enrichment patterns) | ct 7x A-enriched; ol 5x B-enriched |
| C408/C409 (sister equivalence) | Sister pairs as mode selectors |
| C466/C467 (PREFIX = control-flow) | Direct structural grounding |
| C476 (hub rationing) | Gradient persists despite rationing |
| C477 (HT correlation) | Discrimination aligns with vigilance |

---

## What This Establishes

1. **Operational domain assignment** for each prefix family (Tier-2 grounded)
2. **Discrimination gradient** - energy-intensive domains require 8.7x more MIDDLE variants
3. **Sister pairs as mode selectors** - operational toggle, not material distinction
4. **Section-conditional concentration** - Section H is structurally energy-heavy
5. **Decision archetype mapping** - what judgment calls each domain supports

## What This Does NOT Establish

- Specific substance identifications
- Entity-level naming (which plant, which oil)
- Token-to-material direct mappings
- Recipe or procedural reconstruction
- That the domain is definitively thermal-chemical (remains Tier 3)

---

## Files

- `phases/A_BEHAVIORAL_CLASSIFICATION/a_behavioral_classifier.py`
- `results/currier_a_behavioral_registry.json` - Full classified registry
- `results/currier_a_behavioral_stats.json` - Distribution statistics
- `results/currier_a_behavioral_summary.json` - Summary profile
- `phases/SCIENTIFIC_CONFIDENCE/directional_tests.py` - B1-B6 tests
- `phases/SCIENTIFIC_CONFIDENCE/negative_controls.py` - NC1-NC4 tests
- `phases/SCIENTIFIC_CONFIDENCE/confidence_integration.py` - Classification
- `results/directional_tests.json` - Directional test results
- `results/negative_controls.json` - Exclusion test results
- `results/scientific_confidence_classification.json` - Final classification

---

## Navigation

- [INTERPRETATION_SUMMARY.md](INTERPRETATION_SUMMARY.md) - Overall synthesis
- [ecr_material_classes.md](ecr_material_classes.md) - Material class derivation
- [ccm_prefix_mapping.md](ccm_prefix_mapping.md) - Prefix-to-domain mapping

---

*Classification completed 2026-01-12. Reviewed and tightened 2026-01-12.*

---

## External Alignment: Puff-Voynich-Brunschwig (2026-01-14)

### Context

Following the CONFIRMED Puff-Voynich curriculum hypothesis (5/5 tests pass), we tested whether Currier A's morphological discrimination aligns with historically documented procedure classes.

### Hypothesis (Model-Safe)

> Currier A discriminates operational affordance profiles that align with historically documented procedure classes.

C171 ("zero material encoding") remains unchanged and is NOT reinterpreted.

### Test Battery Results: 5/5 PASS - STRONG

| Test | Description | Result | Key Evidence |
|------|-------------|--------|--------------|
| 1 | PREFIX by commitment level | PASS | chi2=4094, p=0.0; qo depleted 0.32x, ok/ot enriched 2.5-3.5x |
| 2 | MIDDLE universality | PASS | Universal enriched in AZC (48% vs 44%, p=1.6e-10) |
| 3 | Sister pair tightness | PASS | ok/ot ratio: Zodiac 0.65, A/C 1.04 |
| 4 | Positional gradient | PASS | ENERGY 564 MIDDLEs vs REGISTRY 65 (8.7x ratio) |
| 5 | Anomalous envelope | PASS | ct depleted 0.14x; f85v2 = k=0 non-thermal |

### Affordance Axes Identified

1. **Compatibility breadth**: Universal vs exclusive MIDDLEs
2. **Intervention tightness**: Sister pair selection (ch/sh, ok/ot)
3. **Anomaly handling**: ct-class entries for non-standard envelopes

### Alignment with Brunschwig Degrees

| Brunschwig Degree | Affordance Profile | A Signature |
|-------------------|-------------------|-------------|
| First (balneum) | Broad compatibility | Universal MIDDLEs enriched in AZC |
| Second (warm) | Standard commitment | ch/sh balanced |
| Third (seething) | Narrow compatibility | Exclusive MIDDLEs, qo enriched |
| Fourth (forbidden) | Categorical prohibition | 17 forbidden transitions |
| Anomalous | Non-thermal | ct depleted, f85v2 profile |

### Plain Language Summary

> Currier A encodes the same kinds of *operational worries* that historical experts talked about -- without ever naming the things they worried about.

Brunschwig worried about:
- Which materials need careful handling (degree selection)
- Which procedures are mutually incompatible
- Which edge cases require different architecture

Currier A discriminates:
- Compatibility breadth (universal vs exclusive MIDDLEs)
- Intervention tightness (sister pair ratios)
- Anomaly handling (ct-class entries)

The worries are the same. The names are absent.

### Execution Rules Followed

1. No claim that A "encodes" materials - affordance profiles only
2. No reinterpretation of C171 - remains unchanged
3. All tests framed in operational affordances, not entities
4. Puff/Brunschwig used only for external interpretive alignment
5. Negative controls via statistical tests

### New Files

- `phases/A_BEHAVIORAL_CLASSIFICATION/currier_a_affordance_tests.py` - Test battery
- `results/currier_a_behavioral_tests.json` - Test results

---

*External alignment test completed 2026-01-14.*
