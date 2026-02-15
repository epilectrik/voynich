# C1056: MIDPROCESS is Structurally Absent from Brunschwig Recipe-Level Encoding

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** BRUNSCHWIG_MIDPROCESS_ABSENCE (Phase 371)
**Relates to:** F-BRU-029 (semantic boundary probe, Path C failure), C1025 (M2 generative sufficiency), C1055 (section-decomposable M2)

---

## Statement

Distillation process monitoring (MIDPROCESS) is **structurally absent** from Brunschwig's recipe-level specification, confirmed across 5 independent data sources. This is not a curation gap — it reflects a fundamental property of the source text where monitoring is tacit operator knowledge (OJLM-1 boundary).

### Evidence (5 sources)

| Source | N | Finding |
|--------|---|---------|
| V3 curation procedural_steps | 245 recipes, 573 steps | 0 MIDPROCESS actions |
| Master data monitoring_intensity | 509 materials | 37 non-zero values, but ALL derive from medical USAGE monitoring |
| Master data MONITORING step_type | 58 instances | 0 distillation process monitoring; 47 medical usage |
| Source text keyword extraction | 95 matches | 77% in Book 1 general chapters, 23% incidental |
| Master data LINK instruction class | 44 instances | Classified from usage-oriented text |

### Dimensional Impact

The Brunschwig operational manifold has **5 active dimensions** (COLLECTION, PREPARATION, PRETREATMENT, DISTILLATION, POSTPROCESS) with MIDPROCESS and STORAGE both zero-variance. Removing these zero columns does not change PCA structure: 3 PCs for 80% variance in both 7D and 5D.

The Voynich operational PCA needs **5 PCs for 80%** (of 10 features). The 2-dimensional gap (Brunschwig 3/5 vs Voynich 5/10) reflects the Voynich's richer operational vocabulary, with 0.752 more bits of variance entropy.

### Path C Closure

Path C (F-BRU-029 C-3) requires MIDPROCESS loading > 0.3 on some PC. Fabricated uniform MIDPROCESS data mechanically achieves loading 0.571, but this is circular: adding 4 identical actions to all recipes creates denominator-driven variance that confirms the design, not the data. Path C cannot be meaningfully resolved without genuine per-recipe MIDPROCESS variation, which does not exist in the source text.

### OJLM-1 Boundary (Partial Parallel)

The Voynich M2 residual (3 universally-failing tests: B4, B5, C2) spans 3 categories — STRUCTURAL, SEQUENTIAL, MORPHOLOGICAL — and does NOT cluster in a single "monitoring" category. However, 2/3 failing tests (B5 directional asymmetry, C2 pairwise MI) capture dynamic/pairwise structure consistent with monitoring-type information. B4 (static role hierarchy) breaks the strict parallel.

The OJLM-1 boundary concept — that monitoring represents tacit operator knowledge not codifiable in specification text — is supported for Brunschwig but only partially paralleled in the Voynich residual.

---

## Interpretation

Brunschwig's *Liber de arte distillandi* describes MIDPROCESS protocols (finger test, drip counting, air vent regulation) in Book 1 general chapters, applying system-wide by distillation method. Individual recipes do NOT specify monitoring instructions because:

1. Monitoring is method-dependent, not recipe-dependent
2. Monitoring is operator judgment (tacit knowledge)
3. The book format does not support conditional/dynamic instructions

This structural absence is characteristic of pre-modern technical specification: the text encodes what the practitioner must DO (prepare, distill, collect) but not what they must MONITOR (temperature, drip rate, process state). Monitoring is learned through apprenticeship, not written specification.

---

## Method

- 5 data sources audited for per-recipe MIDPROCESS variation
- PCA on 7D (with zero columns) vs 5D (without) to verify neutral removal
- Variance entropy comparison: Brunschwig 1.908 bits vs Voynich 2.660 bits
- Fabrication analysis: uniform MIDPROCESS injection reaches loading 0.571 but is circular
- M2 failure categorization: B4=STRUCTURAL, B5=SEQUENTIAL, C2=MORPHOLOGICAL
- Monitoring-relevance assessment: 2/3 failures capture dynamic/pairwise structure
- Verdict: 4/5 (H1 PASS, H2 PASS, H4 THEORETICALLY_POSSIBLE, H5 strict FAIL / soft PASS)

**Script:** `phases/BRUNSCHWIG_MIDPROCESS_ABSENCE/scripts/brunschwig_midprocess_absence.py`
**Results:** `phases/BRUNSCHWIG_MIDPROCESS_ABSENCE/results/brunschwig_midprocess_absence.json`
