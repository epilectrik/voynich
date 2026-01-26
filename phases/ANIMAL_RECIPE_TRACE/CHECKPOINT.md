# ANIMAL_RECIPE_TRACE Checkpoint

**Last Updated:** 2026-01-25
**Current Phase:** ALL COMPLETE
**Status:** COMPLETE - Ready for constraint documentation

---

## Context Preservation

This file preserves state for context recovery. Read this FIRST if resuming.

### What We Did

Tested whether animal-signature A records route to specific B folios/REGIMEs that match Brunschwig's animal procedure categories.

### Key Hypothesis Revision

**Original hypothesis:** Animal materials -> REGIME_1/2 (low fire)
**Actual finding:** Animal materials -> REGIME_4 (precision control)

This makes sense because animal products (proteins, fats) are HEAT-SENSITIVE and need precision, not just low fire.

---

## Phase 1 Results - COMPLETE

**Goal:** Score each A record for P(animal) using C505 + C527 markers.

| Metric | Value |
|--------|-------|
| Total A records scored | 1,559 |
| Threshold (mean + 1.5*std) | 1.201 |
| High-confidence animal records | **120** |
| Top marker | 'ho' (140 hits) |
| Score range | -0.188 to 6.020 |

**Output:** `results/animal_signatures.json`

---

## Phase 2 Results - COMPLETE

**Goal:** Trace animal records through AZC filtering.

| Metric | Value |
|--------|-------|
| Animal records traced | 120 |
| Mean compatible B tokens | 23.2 |
| Baseline mean | 41.9 |
| **Animal/baseline ratio** | **0.55x** (MORE restricted) |
| Unique compatible MIDDLEs | 120 |
| Enriched MIDDLEs (>1.5x) | 15 |

**Top enriched MIDDLEs:**
- 'cph' 166.67x
- 'edy' 116.67x
- 'op' 66.67x
- 'tch' 50x

**Output:** `results/animal_compatible_vocabulary.json`

---

## Phase 3 Results - COMPLETE

**Goal:** Full B folio reception analysis.

| Metric | Value |
|--------|-------|
| B folios analyzed | 82 |
| Reception rate range | 0.366 to 0.857 |
| Top/bottom ratio | **1.80x** |
| Statistical significance | p < 0.000001 |
| High-reception folios | 23 (threshold 0.641) |

**Top receiving folios:**
1. f33v: 85.7%
2. f95r2: 83.3%
3. f40v: 82.1%
4. f41v: 80.6%
5. f94v: 78.3%

**Section distribution:** 70% in herbal_b section (f26v-f56v range)

**Output:** `results/animal_folio_reception.json`

---

## Phase 4 Results - COMPLETE

**Goal:** REGIME clustering analysis.

| REGIME | Enrichment | High-reception count |
|--------|------------|---------------------|
| **REGIME_4** | **2.14x** | 15 |
| REGIME_3 | 1.11x | 5 |
| REGIME_2 | 1.07x | 3 |
| REGIME_1 | **0.00x** | 0 |

**Statistical tests:**
- Chi-square: 17.866, p = 0.000469 (SIGNIFICANT)
- ANOVA: F = 11.69, p = 0.000002 (SIGNIFICANT)

**Key finding:** REGIME_4 is enriched, REGIME_1 has zero representation

**Output:** `results/animal_regime_clustering.json`

---

## Phase 5 Results - COMPLETE

**Goal:** Compare REGIME_4 characteristics to Brunschwig animal procedures.

### REGIME_4 Characteristics (from C494)

| Property | Value | Meaning |
|----------|-------|---------|
| Escape rate | 0.107 (LOWEST) | Least forgiving |
| HIGH_IMPACT | Forbidden | No aggressive intervention |
| min_LINK_ratio | 25%+ | High monitoring |

### Animal Procedure Requirements (Brunschwig)

| Procedure | Fire | Critical Constraint |
|-----------|------|---------------------|
| Blood distillation | Balneum marie | Proteins denature >60C |
| Milk/whey | First degree | Proteins coagulate |
| Egg | Balneum marie | Albumin coagulates |
| Fat/tallow | Second degree | Burns if overheated |
| Horn/bone | Varies | Volatiles escape |

### Fit Analysis: 4/4 aspects match

1. **Precision:** Animal needs tight control -> REGIME_4 has lowest escape
2. **Monitoring:** Animal needs watching -> REGIME_4 has high LINK ratio
3. **No aggression:** Proteins denature -> REGIME_4 forbids HIGH_IMPACT
4. **Variable intensity:** Some animals need moderate heat -> REGIME_4 encodes precision, not intensity

**Output:** `results/animal_brunschwig_comparison.json`

---

## Constraint Candidate

**C536: Animal Material REGIME Routing**

> Animal-signature A records route to REGIME_4 (precision control) at 2.14x enrichment (chi-square p=0.000469, ANOVA p=0.000002). REGIME_1 receives 0% of animal materials. This matches Brunschwig's animal procedure profile: heat-sensitive materials (proteins, fats) require precision handling, not just low fire.

**Tier:** 2 (structural) | **Scope:** A->AZC->B

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/animal_signature_scoring.py` | Phase 1 |
| `scripts/animal_azc_trace.py` | Phase 2 |
| `scripts/animal_folio_reception.py` | Phase 3 |
| `scripts/animal_regime_clustering.py` | Phase 4 |
| `scripts/animal_brunschwig_comparison.py` | Phase 5 |
| `results/animal_signatures.json` | Phase 1 output |
| `results/animal_compatible_vocabulary.json` | Phase 2 output |
| `results/animal_folio_reception.json` | Phase 3 output |
| `results/animal_regime_clustering.json` | Phase 4 output |
| `results/animal_brunschwig_comparison.json` | Phase 5 output |

---

## Key Insight

**The manuscript distinguishes "precision" from "low fire"**

This is NOT obvious from naive reading of Brunschwig. Brunschwig says "use balneum marie for blood" - which sounds like "use gentle heat." But the STRUCTURAL signal is about PRECISION (tight tolerance, high monitoring, no aggressive intervention), which is ORTHOGONAL to intensity.

REGIME_4 encodes this: you can run a precision procedure at moderate intensity (e.g., fat rendering) or at low intensity (e.g., egg distillation). The commonality is the CONTROL TIGHTNESS, not the fire degree.

---

## Next Steps

1. Have expert validate C536 constraint
2. Document in INDEX.md if approved
3. Update INTERPRETATION_SUMMARY.md with animal routing model
