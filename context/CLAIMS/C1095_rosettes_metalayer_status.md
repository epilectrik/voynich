# C1095: Rosettes Metalayer Status

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 387-388H)
**Extends:** C301 (AZC is HYBRID), C430 (AZC bifurcation), C1088 (hybrid classification)
**Strengthened by:** C1089 (near-complete coverage), C1090 (section T correlation), C1091 (multi-target cross-reference), C1092 (CENTER convergence), C1093 (label-description bifurcation), C1094 (exclusive vocabulary tail)

---

## Statement

The Rosettes foldout (f85-f86, 7 folios) functions as a structural metalayer sitting above the normal A/B/AZC hierarchy. Evidence: near-complete vocabulary coverage (98% of instruction classes, 100% of hub MIDDLEs, 93.1% of core vocabulary — C1089), spatial AZC-to-B gradient (C1088), multi-target cross-reference to pharmaceutical folios (C1091), higher entropy than B corpus (1.767 vs 1.458), mixed INDEX/DESCRIPTION/BRIDGE roles (C1093), and unique convergence architecture (C1092). The Rosettes is not classifiable as pure A, B, or AZC; it indexes across all three systems.

---

## Evidence

### Metalayer Indicators (5-Test Battery, Phase 388H)

| Test | Finding | Verdict |
|------|---------|---------|
| T1: Section Correlation | All regions → Section T | SINGLE_SECTION_T |
| T2: AZC-to-B Gradient | f85v2=AZC through f86v6=B | GRADIENT_CONFIRMED |
| T3: Exclusive Vocabulary | 79 exclusive MIDDLEs, compound tail | MORPHOLOGICAL_TAIL |
| T4: Cross-Reference | Multi-section targeting | MULTI_TARGET_CROSSREF |
| T5: Structural Roles | INDEX + DESCRIPTION + BRIDGE | MIXED_ROLES_CONFIRMED |

### Quantitative Summary

| Property | Rosettes | Normal AZC | B Corpus |
|----------|----------|------------|----------|
| 49-class coverage | 98.0% | ~83% | 100% |
| Hub MIDDLE coverage | 100% | — | 100% |
| Kernel density | 38.8% | 0% (C757) | ~69% |
| LINK density | 0.97% | 0% (C757) | ~6.6% |
| Macro-state entropy | 1.767 | — | 1.458 |
| Prefix role entropy | 2.223 | — | 1.997 |

### Constraint Implications

- C757 (AZC zero kernel/link) does not apply to Rosettes — kernel (38.8%) and LINK (0.97%) are present
- C440 (uniform B-to-AZC sourcing) is broken by Rosettes multi-target cross-reference
- C437 (inter-folio Jaccard 0.056) is exceeded by Rosettes inter-region Jaccard (0.107)
- C438 (83% per-folio coverage) is exceeded (93.1% core coverage)

---

## Interpretation

The Rosettes foldout occupies a unique structural position: it is the only part of the manuscript that samples nearly the entire grammar with elevated evenness, spatially encodes the AZC-to-B transition, and cross-references specific pharmaceutical procedure folios. At Tier 3, this is consistent with a master reference chart or index to the manuscript's pharmaceutical content — a page where the expert operator could see the full vocabulary space organized by process type and operational character.

---

## Method

- Phase 387: 10-test classification battery (rosettes_classification.py)
- Phase 388H: 5-test metalayer characterization (rosettes_metalayer.py)
- Supplementary probes: system affinity, explainer, labels, decoder map, center deep analysis
- All tests use H-track where available, U-track fallback for f85v2

**Scripts:**
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/rosettes_classification.py`
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/rosettes_metalayer.py`
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_rosette_decoder_map.py`
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_center_rosette_deep.py`

**Results:**
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_classification_results.json`
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_metalayer_results.json`
- `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosette_decoder_map.json`

---

## Verdict

**METALAYER_CONFIRMED**: The Rosettes foldout is a structural metalayer above A/B/AZC, functioning as a near-complete vocabulary index with spatial encoding of the system gradient and targeted cross-references to pharmaceutical procedures.
