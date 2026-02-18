# C1088: Rosettes Foldout Hybrid Classification

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 387)
**Extends:** C301 (AZC is HYBRID), C317 (hybrid architecture), C430 (AZC bifurcation)
**Relates to:** C437 (folios maximally orthogonal), C757 (AZC zero kernel/link)

---

## Statement

The Rosettes foldout (f85r1, f85r2, f85v2, f86v3, f86v4, f86v5, f86v6; 7 folios, ~2,064 tokens) shows hybrid A/B/AZC properties that do not fit any single system. A 10-test classification battery yields: 64.7% grammar coverage (intermediate), 0.054% forbidden transition violation rate (B-like), 0.97% LINK density (AZC-like), 38.8% kernel character density (AZC-like), inter-region Jaccard 0.107 (low overlap), per-folio prefix ratio gradient from f85v2=6.538 (AZC-like ok/ot dominant) to f86v6=0.296 (B-like qo/ch dominant). Overall classification: HYBRID.

---

## Evidence

### 10-Test Battery Results

| Test | Metric | Value | Verdict |
|------|--------|-------|---------|
| R1.1 Grammar Coverage | 49-class token coverage | 64.7% | INTERMEDIATE |
| R1.2 Forbidden Transitions | violation rate | 0.054% | B_LIKE_COMPLIANT |
| R1.3 LINK Density | LINK token % | 0.97% | AZC_LIKE |
| R1.4 Kernel Density | kernel char % of MIDDLEs | 38.8% | AZC_LIKE |
| R1.5 Position-Vocabulary | mean inter-region Jaccard | 0.107 | LOW_OVERLAP |
| R1.6 Bigram Reuse | unique bigram reuse % | 2.0% | LOW_REUSE |
| R1.7 Sequential Coherence | AXM self-transition rate | 0.037 | INTERMEDIATE |
| R1.8 Line Atomicity | inter-line Jaccard | 0.115 | B_LIKE_SEQUENCED |
| R1.9 Prefix Ratio | (ok+ot)/(qo+ch) | 0.649 overall | INTERMEDIATE |
| R1.10 RI Vocabulary | A-not-B MIDDLE profile | — | INCONCLUSIVE |

### Per-Folio Gradient

| Folio | Prefix Ratio | Character |
|-------|-------------|-----------|
| f85v2 | 6.538 | Strongly AZC-like |
| f85r2 | 1.167 | AZC-leaning |
| f86v5 | 0.776 | Intermediate |
| f86v3 | 0.606 | B-leaning |
| f85r1 | 0.586 | B-leaning |
| f86v4 | 0.348 | Strongly B-like |
| f86v6 | 0.296 | Strongly B-like |

Signal count: 2 B-like, 2 AZC-like, 3 intermediate. No single system classification fits.

---

## Interpretation

The Rosettes foldout spans the A/B/AZC boundary spatially, with a gradient from AZC-like reference (f85v2, the central 9-rosette page) to pure B execution text (f86v6). This spatial encoding of the system gradient is unique in the manuscript and suggests the foldout functions as a structural bridge or index connecting the reference layer to the execution layer.

---

## Method

- 10-test classification battery with pre-registered predictions for B-family, AZC-family, and hybrid outcomes
- Reference corpus rates: B LINK ~6.6% (C609), B kernel ~69% (C089), AZC Jaccard 0.056 (C437)
- T0 prerequisite: H vs U track validation on 5 dual-track folios (56.2% identity, FAIL due to segmentation differences)

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/rosettes_classification.py`
**Results:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_classification_results.json`

---

## Verdict

**HYBRID**: Rosettes foldout is not classifiable as pure A, B, or AZC. Shows a spatial gradient from AZC-like (f85v2) to B-like (f86v6) with intermediate properties throughout.
