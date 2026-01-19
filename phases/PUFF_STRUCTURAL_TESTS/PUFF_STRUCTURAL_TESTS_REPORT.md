# PUFF_STRUCTURAL_TESTS Phase Report

**Generated:** 2026-01-19
**Status:** COMPLETE
**Tier Assessment:** No new evidence for Puff-Voynich structural linkage

---

## Executive Summary

This phase tested whether our improved understanding of AZC and Currier A enables new Puff-Voynich linkages. The expert-advisor identified T4, T8, and T9 as the highest-value tests, plus T7 as a prerequisite audit.

**Results:**
- T7 (Data Audit): Clean reference data (84/84 chapters) is sufficient
- T4 (Category -> PREFIX): CONSTRAINED by weak A-B linkage (29% above baseline)
- T9 (Danger -> HT): **FALSIFIED** - No HT elevation at dangerous positions
- T8 (Complexity -> Breadth): **FALSIFIED** - No positive vocabulary correlation

---

## Test Results Summary

| Test | Status | Key Metric | Interpretation |
|------|--------|------------|----------------|
| **T7** | COMPLETE | 84/84 clean, 47/84 noisy | Reference data usable |
| **T4** | CONSTRAINED | N/A (weak linkage) | A-B linkage too weak for meaningful test |
| **T9** | **FAIL** | rho=-0.018, p=0.79 | Dangerous positions have LOWER HT |
| **T8** | **FAIL** | rho=-0.16, p=0.15 | Later positions have SMALLER vocabulary |

---

## T7: Data Quality Audit

**Finding:** Two distinct data sources with different quality levels.

**Clean Data (usable):**
- `puff_83_chapters.json`: 84/84 chapters (100%)
- All categories, dangerous flags (5), aromatic flags (16) complete
- Category distribution: HERB (42), FLOWER (17), TREE_FLOWER (5), ROOT (5), others

**Noisy Data (limited):**
- `puff_chapter_semantics.json`: 47/84 chapters (56%)
- Application method: 57% unknown
- Humoral profile: 91% neutral (uninformative)
- Chapter alignment not preserved (OCR indices)

**Recommendation:** Use clean reference data for T8, T9. Noisy semantics insufficient for T5.

---

## T4: Category -> PREFIX Family (CONSTRAINED)

**Status:** Not testable due to weak A-B linkage

**Evidence:**
- `phase1_ab_flow_validation.json`: A->B vocabulary overlap is 29% vs 25% baseline
- Only 4% lift over random - insufficient signal for meaningful correlation

**Constraint:**
- C272 establishes physical A/B separation (114 A folios, 83 B folios, zero overlap)
- REGIMEs are B-side properties, not directly linkable to A PREFIX distributions

**Expert Assessment:** T4 would require A-B correspondence that doesn't exist at meaningful levels.

---

## T9: Danger Profile -> HT Density (FALSIFIED)

**Hypothesis:** Puff materials flagged as dangerous correlate with higher HT density at corresponding Voynich positions.

**Prediction:** C459 establishes HT as anticipatory compensation. If dangerous materials require extra caution, HT should be elevated.

**Results:**
```
Dangerous materials (n=5):
  Mean HT density: 0.1327
  Positions: 17, 38, 57, 60, 79

Safe materials (n=78):
  Mean HT density: 0.1505

Enrichment: 1.13x in SAFE (opposite of prediction)
Mann-Whitney p: 0.69
Permutation p: 0.79
```

**Verdict:** FAIL - HT is slightly LOWER at dangerous positions, not higher.

**Interpretation:** HT anticipatory compensation is NOT calibrated to Puff's danger classification. The Voynich system's danger model (if any) does not align with Puff's toxicological flags.

---

## T8: Processing Complexity -> Vocabulary Breadth (FALSIFIED)

**Hypothesis:** Later Puff chapters (more complex materials) require B programs with larger vocabulary footprints.

**Results:**
```
Position -> Vocabulary Size:
  Spearman rho: -0.16
  p-value: 0.15
  Verdict: FAIL (no positive correlation)

Position -> CEI (sanity check):
  Spearman rho: 0.88
  p-value: < 0.0001
  Verdict: PASS (expected by design)

Vocabulary Size -> CEI:
  Spearman rho: -0.38
  p-value: < 0.001
  Verdict: Significant but INVERSE
```

**Key Finding:** High-CEI folios (complex execution) have SMALLER vocabularies, not larger.

**Interpretation:** Complexity in Voynich is achieved through constraint tightening, not vocabulary expansion. Puff's material complexity (by position) does not predict Voynich vocabulary breadth.

---

## Synthesis: What This Phase Establishes

### Confirmed Boundaries

1. **Puff-Voynich linkage is CURRICULUM-LEVEL only**
   - Shared pedagogical structure (10/11 prior tests pass)
   - But no interface-level coordination (T9 danger, T8 complexity both fail)

2. **A-B linkage is too weak for Puff->A tests**
   - 29% overlap vs 25% baseline (4% lift)
   - T4 (Category -> PREFIX) cannot yield meaningful signal

3. **Voynich danger model is INTERNAL, not Puff-aligned**
   - HT elevation does NOT track Puff's toxicological classification
   - C459 compensation is for Voynich-internal states, not external material properties

4. **Complexity metrics are ORTHOGONAL**
   - Puff position complexity != Voynich vocabulary breadth
   - High CEI correlates with SMALLER vocabulary (constraint tightening)

### Updated Puff Evidence Table

| Test Battery | Status | Tests | Interpretation |
|--------------|--------|-------|----------------|
| Prior (structural) | 10/11 PASS | Position, category, number, complementarity | Curriculum alignment |
| New (AZC/A linkage) | 0/3 testable/pass | T4 constrained, T8 fail, T9 fail | No new linkage |

### Evidential Ceiling Assessment

The expert-advisor was correct:

> "The existing 10/11 tests establish curriculum alignment. New tests should probe STRUCTURAL mechanisms, not add more curriculum evidence."

We attempted structural probes (T8, T9) and found:
- **T9 (danger-HT):** No structural alignment
- **T8 (complexity-breadth):** No structural alignment

**Conclusion:** The Puff-Voynich relationship has reached its **evidential ceiling** for structural characterization. Further evidence would require:
1. External provenance research (not computational)
2. New external reference texts (not currently available)
3. Semantic interpretation (constraint-prohibited)

---

## Constraint Compliance

| Constraint | How Respected |
|------------|---------------|
| C240 | No entry-level A-to-Puff mapping attempted |
| C384 | No chapter-folio correspondences claimed |
| C171 | No material encoding assumed or inferred |
| Tier 3-4 | All findings remain SPECULATIVE |

---

## Files Created

| File | Purpose |
|------|---------|
| `phases/PUFF_STRUCTURAL_TESTS/puff_data_audit.py` | T7 audit script |
| `phases/PUFF_STRUCTURAL_TESTS/t9_danger_ht_correlation.py` | T9 test script |
| `phases/PUFF_STRUCTURAL_TESTS/t8_complexity_breadth.py` | T8 test script |
| `results/puff_data_audit.json` | T7 results |
| `results/puff_danger_ht_test.json` | T9 results |
| `results/puff_complexity_breadth_test.json` | T8 results |

---

## Recommendation

**Close Puff investigation.** The hypothesis has reached its evidential ceiling:

- **Curriculum alignment:** Established (10/11 pass)
- **Structural linkage:** Not found (0/3 new tests support)
- **Further testing:** Would require semantic interpretation (prohibited) or external evidence (unavailable)

Puff remains Tier 3-4 SPECULATIVE: contextually interesting but not structurally informative beyond curriculum-level observations.

---

*Phase completed: 2026-01-19*
*Expert consultation: Incorporated*
*Result: Evidential ceiling confirmed*
