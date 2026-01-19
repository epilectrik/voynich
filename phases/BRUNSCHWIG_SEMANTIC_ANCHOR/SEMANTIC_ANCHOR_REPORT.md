# Brunschwig Semantic Anchor Report

**Phase:** BRUNSCHWIG_SEMANTIC_ANCHOR
**Status:** FALSIFIED
**Date:** 2026-01-18

---

## Executive Summary

The investigation attempted to close the semantic anchoring chain from Brunschwig recipes through Product types to A entry MIDDLEs. **The anchor chain FAILED to close.** MIDDLEs do not encode material-processing compatibility at a level we can detect.

### Results Summary

| Phase | Test | Result | Threshold |
|-------|------|--------|-----------|
| 1 | A->B flow via MIDDLE overlap | 29.4% | >70% |
| 2 | Top-10 discriminator disjointness | 100% | >80% |
| 2 | Overall MIDDLE exclusivity | 46.6% | >50% |
| 3 | GENTLE x RESIN incompatibility | 69.4% | >95% |
| 3 | Cross > Self incompatibility | +7.7% | >0% |
| 4 | Entry-level prediction | 28.9% | >60% |
| 4 | Folio-level prediction | 27.7% | >60% |

**Overall Status:** 4/7 criteria failed

---

## Detailed Findings

### Phase 1: A->B Flow Validation

**Question:** Do A folios classified as WATER_GENTLE feed B folios in REGIME_2?

**Finding:** A->B flow via direct MIDDLE vocabulary overlap is essentially random (29.4% vs 25% baseline).

**Interpretation:** A and B have 77.4% non-overlapping MIDDLE vocabularies. The relationship is mediated by AZC position-indexed legality, not direct vocabulary sharing. This architecture prevents simple A->B MIDDLE tracing.

### Phase 2: Discriminating MIDDLEs

**Question:** Are product-type MIDDLEs disjoint?

**Finding:**
- Top-10 discriminating MIDDLEs are 100% disjoint across product types (positive)
- But overall exclusivity is only 46.6% (below 50% threshold)

**Interpretation:** High-discrimination MIDDLEs exist and are product-specific, but they're rare. The bulk of MIDDLE vocabulary is shared across product types.

### Phase 3: Material Incompatibility

**Question:** Does MIDDLE incompatibility align with material processing incompatibility?

**Finding:**
- WATER_GENTLE x OIL_RESIN: 69.4% incompatible (fails 95% threshold)
- Cross-product incompatibility IS higher than self-incompatibility (+7.7%)

**Interpretation:** Weak directional evidence. Cross-product MIDDLEs are MORE incompatible than same-product MIDDLEs, which is consistent with material grouping. But the effect is too weak for semantic anchoring.

### Phase 4: Entry-Level Prediction

**Question:** Can we predict an A entry's product affinity from its MIDDLE?

**Finding:**
- Only 2.7% of entries have discriminating MIDDLEs
- Prediction accuracy: 28.9% (barely above 25% baseline)
- Folio-level: 27.7%

**Interpretation:** Discriminating MIDDLEs are too rare to enable entry-level semantic prediction. The strong product signals exist at the corpus level, not the entry level.

---

## Conclusions

### What We Confirmed

1. **Brunschwig alignment remains valid** (F-BRU-001, F-BRU-002)
   - REGIMEs map to fire degrees
   - Product types are structurally real
   - The procedural framework holds

2. **Cross-product MIDDLEs have higher incompatibility**
   - Weak but present directional signal
   - Consistent with material grouping hypothesis
   - Not strong enough for semantic anchoring

3. **Top discriminating MIDDLEs are disjoint**
   - Some MIDDLEs are genuinely product-specific
   - But they're too rare for practical use

### What Failed

1. **A->B flow is not traceable via MIDDLE overlap**
   - The AZC mediation abstracts away direct vocabulary connection
   - This is architecturally expected but blocks semantic tracing

2. **Entry-level semantic prediction fails**
   - MIDDLEs don't encode material compatibility at the individual entry level
   - Product signals are emergent from folio-level aggregation

3. **Incompatibility rates don't reach material-chemistry levels**
   - 69.4% is not "CANNOT be processed together"
   - It's "less often appear together"

---

## Updated Interpretation

**F-BRU-003 (Property Rejection) Extends to Semantic Anchoring:**

MIDDLEs encode **operational state constraints**, not **material compatibility**:

```
REJECTED: "MIDDLEs in cluster X indicate gentle-extraction-compatible materials"

SUPPORTED: "MIDDLEs encode what operational configurations are allowed"
           "Product types emerge from aggregate operational patterns"
           "The Brunschwig alignment is procedural, not material"
```

### What MIDDLEs Actually Do

MIDDLEs constrain the operational space:
- Which interventions are legal
- What state transitions are allowed
- How the control loop can proceed

They do NOT identify:
- What material is being processed
- What product will result
- Which Brunschwig recipe applies

The Brunschwig fit is real because **procedures are real** - but the encoding is at the process-constraint level, not the material-identity level.

---

## Implications for Decoding

1. **Cannot decode materials from MIDDLEs**
   - C171 (zero material encoding) is confirmed at entry level
   - Product types are statistical aggregates, not per-entry signals

2. **Brunschwig comparison is procedural only**
   - Useful for understanding system design
   - Not useful for identifying specific recipes/materials

3. **Semantic decoding path remains closed**
   - No anchor from manuscript to real-world substances
   - The operational interpretation is our ceiling

---

## Files Generated

| File | Purpose |
|------|---------|
| `results/phase1_ab_flow_validation.json` | A->B flow test data |
| `results/phase2_discriminating_middles.json` | MIDDLE enrichment analysis |
| `results/phase3_material_incompatibility.json` | Cross-product incompatibility |
| `results/phase4_entry_prediction.json` | Entry-level prediction results |
| `results/semantic_anchor_report.json` | Consolidated summary |

---

## Constraints Updated

**C171 (Zero Material Encoding):** CONFIRMED at entry level
- MIDDLEs do not encode material identity or compatibility
- Product signals require folio-level aggregation

**F-BRU-003 (Property Rejection):** EXTENDED
- Now applies to semantic anchoring attempts
- MIDDLEs are process-state markers, not material descriptors

---

## Falsification Record

| Hypothesis | Test | Result |
|------------|------|--------|
| MIDDLEs encode material compatibility | Phase 3 | FALSIFIED |
| A entries carry product signals | Phase 4 | FALSIFIED |
| Brunschwig provides semantic anchor | Full chain | FALSIFIED |
