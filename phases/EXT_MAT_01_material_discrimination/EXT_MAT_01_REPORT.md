# Phase EXT-MAT-01: Material Domain Discrimination

**Status:** COMPLETE
**Date:** 2026-01-05
**Tier:** 3 (External Alignment Only)

---

## Purpose

Stress test to determine whether structural evidence better supports:
- **ALCHEMICAL-MINERAL** (mercury, antimony, gold preparations)
- **AROMATIC-BOTANICAL** (rose water, essential oils, resins)

---

## Test Results

### Test 1: Illustration Content Alignment

| Metric | Value |
|--------|-------|
| perfumery_aligned_rate | 0.867 |
| root_emphasis | 0.73 |
| blue_purple_flowers | 0.47 |
| food_plants | 0.033 |
| dye_plants | 0.0 |

**Alchemical Prediction:** Apparatus, symbols, abstract forms expected; aromatic plants unexpected
**Botanical Prediction:** Aromatic plant illustrations expected

**Observed:** 86.7% perfumery-aligned, 73% root emphasis

| Domain | Score |
|--------|-------|
| Alchemical | 0.133 |
| Botanical | 0.94 |

**Verdict:** BOTANICAL (Confidence: HIGH)

---

### Test 2: Danger/Toxicity Profile

| Metric | Value |
|--------|-------|
| premature_hazards | 0.647 |
| late_hazards | 0.0 |
| opportunity_loss_fit | STRONG |
| physical_instability_fit | WEAK |

**Alchemical Prediction:** Mercury/antimony hazards should encode mortal danger
**Botanical Prediction:** Aromatic hazards encode economic loss only

**Observed:** Opportunity-loss DOMINANT, physical-instability WEAK

| Domain | Score |
|--------|-------|
| Alchemical | 0.2 |
| Botanical | 0.9 |

**Verdict:** BOTANICAL (Confidence: HIGH)

---

### Test 3: Product/Program Diversity

| Metric | Value |
|--------|-------|
| total_programs | 83 |
| total_families | 8 |
| programs_per_family | 10.4 |

**Alchemical Prediction:** Few products (4-6), many variations → expect 10-20 programs
**Botanical Prediction:** Many products (dozens), similar process → expect 50-100 programs

**Observed:** 83 programs in 8 families

| Domain | Score |
|--------|-------|
| Alchemical | 0.3 |
| Botanical | 0.8 |

**Verdict:** BOTANICAL (Confidence: MODERATE)

---

### Test 4: Duration Semantics

| Metric | Value |
|--------|-------|
| attention_model_wins | True |
| position_independent | True |
| boundary_reset | True |

**Alchemical Prediction:** Weeks to months duration
**Botanical Prediction:** Hours to days duration

**Observed:** SID-05: Attentional pacing = active monitoring (hours)

| Domain | Score |
|--------|-------|
| Alchemical | 0.2 |
| Botanical | 0.9 |

**Verdict:** BOTANICAL (Confidence: HIGH)

---

### Test 5: Restart Cost Semantics

| Metric | Value |
|--------|-------|
| restart_rate | 0.036 |
| binary_penalty | True |

**Alchemical Prediction:** Restart loses expensive purchased materials
**Botanical Prediction:** Restart loses perishable time-bound opportunity

**Observed:** 3.6% restart-capable, binary penalty

| Domain | Score |
|--------|-------|
| Alchemical | 0.5 |
| Botanical | 0.7 |

**Verdict:** BOTANICAL (Confidence: LOW)

---

### Test 6: Historical Documentation Pattern

| Metric | Value |
|--------|-------|
| theoretical_content | 0.0 |
| material_specifications | 0.0 |
| pure_operational | 1.0 |

**Alchemical Prediction:** Symbolic, encoded, theoretical elements expected
**Botanical Prediction:** Practical, operational, direct instruction expected

**Observed:** 0% theory, 100% operational, structurally exceptional

| Domain | Score |
|--------|-------|
| Alchemical | 0.4 |
| Botanical | 0.6 |

**Verdict:** BOTANICAL (Confidence: LOW)

---

### Test 7: Section Structure Interpretation

| Metric | Value |
|--------|-------|
| total_sections | 8 |
| vocabulary_exclusivity | 0.807 |

**Alchemical Prediction:** 3-4 stages or 7 metals; shared operational vocabulary
**Botanical Prediction:** Multiple material types; distinct vocabularies per material

**Observed:** 8 sections, 80.7% vocabulary exclusivity

| Domain | Score |
|--------|-------|
| Alchemical | 0.4 |
| Botanical | 0.7 |

**Verdict:** BOTANICAL (Confidence: MODERATE)

---

### Test 8: Apparatus Usage Pattern

| Metric | Value |
|--------|-------|
| link_density | 0.376 |
| premature_hazards | 0.647 |
| no_endpoint_markers | True |

**Alchemical Prediction:** Pelican for months-long philosophical circulation
**Botanical Prediction:** Pelican for hours-long cohobation/concentration

**Observed:** Pelican compatible, but SID-05 duration favors short cycles

| Domain | Score |
|--------|-------|
| Alchemical | 0.5 |
| Botanical | 0.7 |

**Verdict:** BOTANICAL (Confidence: LOW)

---

## Summary

### Score Totals

| Domain | Total Score | Test Wins |
|--------|-------------|-----------|
| Alchemical | 2.63 | 0 |
| Botanical | 6.24 | 8 |

**Score Ratio (Botanical/Alchemical):** 2.37

### High-Confidence Tests

| Metric | Value |
|--------|-------|
| High-confidence tests | 3 |
| Botanical wins (high conf) | 3 |
| Alchemical wins (high conf) | 0 |

---

## Overall Verdict

**BOTANICAL_FAVORED** (Confidence: **HIGH**)

### Why Botanical Wins

The structural evidence favors aromatic-botanical interpretation because:

1. **Illustrations are 86.7% perfumery-aligned** — If this were alchemical, why aromatic plant drawings?
2. **Hazards encode opportunity-loss, not physical danger** — Mercury kills; rose water doesn't
3. **83 programs suggests diverse product space** — Alchemical work has few products
4. **Duration is hours, not weeks** — SID-05 contradicts alchemical timescales
5. **Section vocabulary is highly exclusive** — Different materials = different vocabulary

### Caveats

- Pelican apparatus fits both domains
- Expert-only context fits both domains
- Some alchemical texts are purely operational
- Historical documentation patterns overlap

---

## Interpretive Boundary

This analysis evaluates structural fit only. It does NOT:
- Identify specific products
- Assign semantics to tokens
- Prove historical identity
- Exclude either interpretation definitively

---

*EXT-MAT-01 COMPLETE.*
