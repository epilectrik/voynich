# C1109: Rosettes Cross-Reference is Vocabulary-Mediated, Not Process-Demonstrating

**Tier:** 2 (STRUCTURAL INFERENCE — NEGATIVE)
**Scope:** B
**Phase:** ROSETTES_CROSS_REFERENCE_VALIDATION (Phase 393)
**Qualifies:** C1098 (structural index 0.92/1.0), C1091 (cross-reference map)
**Leaves open:** Whether the Rosettes index function encodes any information beyond bridge vocabulary overlap

---

## Statement

The hypothesis that Rosettes B-like folios demonstrate the operational character of their cross-referenced target folios (Stars/Pharma) is NOT supported. Five tests (P1-P5) produced 1 PARTIAL and 4 FAIL:

1. **Description regions operationally homogeneous** (P1 GATE FAIL): f85v2 description groups (NORTH, VERT, CENTER) show pairwise cosine distances within the permuted range (54th percentile, p=0.459). No process-type differentiation at the profile level.
2. **B-like folios do NOT preferentially match Stars** (P2 PARTIAL): Only 1/2 B-like folios (f86v3) has Stars cosine > Herbal cosine. f86v6 matches Herbal better (0.9405 vs 0.8953).
3. **Non-bridge vocabulary matches Herbal, not Stars** (P3 FAIL): ALL 7 Rosettes folios match Herbal best in non-bridge MIDDLE Jaccard. Stars is last or near-last for every folio.
4. **No AZC-to-B gradient predicts Stars similarity** (P4 FAIL): Spearman rho = -0.086, p=0.872. Zero relationship between B-likeness and Stars-similarity.
5. **Target folios not more similar than random** (P5 FAIL): Lift = 0.996x (p=0.698). B-like Rosettes folios are no more similar to the 5 cross-referenced target folios than to random B-corpus folios.

The Rosettes index function operates through vocabulary overlap (bridges per C1100), not operational demonstration.

---

## Evidence

### P1: Description Region Heterogeneity (GATE)
| Pair | Cosine | Distance |
|------|--------|----------|
| NORTH-VERT | 0.9834 | 0.0166 |
| NORTH-CENTER | 0.9633 | 0.0367 |
| VERT-CENTER | 0.9576 | 0.0424 |

Mean pairwise distance: 0.0319. Permuted mean: 0.0364 (sd=0.0250). Percentile: 54.1th. p=0.459. **FAIL.**

### P2: B-Like Folios vs Section Character
| Folio | Stars cos | Herbal cos | Bio cos | Stars > Herbal? |
|-------|-----------|------------|---------|-----------------|
| f86v3 (B-like) | 0.9670 | 0.9667 | 0.9345 | YES (margin: 0.0003) |
| f86v6 (B-like) | 0.8953 | 0.9405 | 0.9269 | NO |

1/2 B-like folios match Stars. f86v3 margin is negligible (0.03%). **PARTIAL.**

### P3: Non-Bridge Section Signal
| Folio | B Jaccard | H Jaccard | S Jaccard | Best |
|-------|-----------|-----------|-----------|------|
| f85r1 | 0.0644 | 0.0756 | 0.0470 | H |
| f85r2 | 0.0328 | 0.0324 | 0.0154 | B |
| f85v2 | 0.0312 | 0.0514 | 0.0280 | H |
| f86v3 | 0.0409 | 0.0435 | 0.0322 | H |
| f86v4 | 0.0320 | 0.0346 | 0.0217 | H |
| f86v5 | 0.0406 | 0.0491 | 0.0281 | H |
| f86v6 | 0.0490 | 0.0514 | 0.0440 | H |

6/7 folios match H best. S is LAST for 5/7 folios. **FAIL.**

### P4: Gradient Correlation
Spearman rho(B-likeness, Stars_cosine) = -0.086, p=0.872. No gradient. **FAIL.**

### P5: Target Folio Specificity
Mean target cosine: 0.9374. Mean random cosine: 0.9412. Lift: 0.996x. p=0.698. **FAIL.**

---

## Interpretation

The Rosettes foldout is a structural index (C1098, score 0.92/1.0) whose cross-reference function operates entirely through bridge vocabulary overlap (C1100). Its B-like folios do NOT adopt the operational character of their target section (Stars/Pharma). Instead:

1. **Non-bridge vocabulary is Herbal-like**: The Rosettes' non-bridge MIDDLEs overlap most with Herbal, suggesting the descriptive content (as opposed to the bridge scaffolding) draws from the most vocabulary-diverse section.
2. **No specificity to target folios**: The 5 cross-referenced folios (f111r, f108r, f76r, f108v, f116r) are no more operationally similar to the Rosettes than any random B-corpus folios.
3. **No gradient effect**: The AZC-to-B spatial gradient (C1088) does not predict increasing Stars-similarity. B-likeness reflects morphological structure, not section affinity.

This is consistent with C1100 (bridge mediation) and strengthens the interpretation that the Rosettes serves as a universal vocabulary index — it connects to everything through bridges but demonstrates nothing section-specific in its procedural content.

**What the Rosettes IS:** A bridge-vocabulary index with universal manuscript scope (C1101).
**What the Rosettes is NOT:** A process-type reference guide that demonstrates target section operations.

---

## Provenance

- Phase: 393 (ROSETTES_CROSS_REFERENCE_VALIDATION), Tests P1-P5
- Script: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/scripts/rosettes_crossref_validation.py`
- Results: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/results/rosettes_crossref_validation.json`
- Related: C1091, C1098, C1100, C1101
