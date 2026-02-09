# MIDDLE_SEMANTIC_MAPPING Phase

**Date:** 2026-02-04
**Status:** COMPLETE
**Verdict:** PRODUCTIVE - Major functional clustering discovered
**Goal:** Map MIDDLEs to functional categories (heat, apparatus, material type)

---

## Research Questions

### 1. Kernel-MIDDLE Correlation (Heat Proxy)
Do specific MIDDLEs correlate with kernel profiles (HIGH_K, HIGH_H, HIGH_E)?
- HIGH_K paragraphs = energy-intensive operations (C893: 2x distillation)
- If MIDDLE X concentrates in HIGH_K, it may encode high-heat operations

### 2. Section-MIDDLE Differentiation (Material Proxy)
Do different sections use systematically different MIDDLE vocabularies?
- HERBAL_B, BIO, PHARMA, OTHER process different materials
- F-BRU-012 hints at this (lch concentrated in BIO)
- Full section × MIDDLE matrix not yet computed

### 3. MIDDLE Co-occurrence Networks
Which MIDDLEs appear together vs. are mutually exclusive?
- Co-occurring MIDDLEs may share apparatus/fuel requirements
- Mutually exclusive MIDDLEs may indicate incompatible setups

### 4. REGIME × MIDDLE Interaction
Do precision vs tolerance regimes use different MIDDLEs?
- REGIME_4 = precision axis (C494)
- If MIDDLEs cluster by REGIME, they encode execution mode requirements

---

## Semantic Ceiling (C120, C171)

**What we CAN recover:**
- Functional clusters that BEHAVE like apparatus/fuel/heat categories
- Statistical associations between MIDDLEs and operational parameters
- Co-occurrence patterns revealing compatible/incompatible operations

**What we CANNOT recover:**
- "MIDDLE X = alembic" (specific apparatus identity)
- "MIDDLE Y = charcoal fuel" (specific material identity)
- Direct entity-level semantics

---

## Prior Work

| Source | Finding |
|--------|---------|
| C777 | FL MIDDLEs encode state progression (i→y = initial→terminal) |
| C893 | HIGH_K predicts distillation (2x FQ rate) |
| C895 | Kernel-recovery correlation asymmetry |
| F-BRU-011 | Three-tier MIDDLE structure (PREP/CORE/EXT) |
| F-BRU-012 | Preparation MIDDLEs correlate with Brunschwig operations |
| F-BRU-013 | ke vs kch differentiation (sustained vs precision heat) |

---

## Completed Analyses

| Script | Purpose | Status | Key Finding |
|--------|---------|--------|-------------|
| `01_kernel_middle_correlation.py` | MIDDLE distribution by kernel profile | COMPLETE | 55% significant correlation |
| `02_section_middle_matrix.py` | Section × MIDDLE vocabulary comparison | COMPLETE | 96% section-specific |
| `03_regime_middle_interaction.py` | REGIME × MIDDLE clustering | COMPLETE | 67% REGIME-specific, m=7.24x in precision |

---

## Expected Outputs

- Kernel-MIDDLE correlation matrix with significance tests
- Section-specific MIDDLE vocabularies with enrichment ratios
- MIDDLE co-occurrence network (nodes = MIDDLEs, edges = co-occurrence)
- REGIME-MIDDLE heatmap showing clustering

---

## Success Criteria

**PRODUCTIVE if:**
- At least one clear functional clustering emerges (p < 0.01)
- Clusters align with Brunschwig operational categories
- New Tier 2-3 constraints documentable

**NULL if:**
- MIDDLEs distribute uniformly across all parameters
- No significant clustering by kernel/section/regime
- (Would still document as negative result)

