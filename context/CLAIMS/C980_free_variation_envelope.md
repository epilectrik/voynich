# C980: Free Variation Envelope — 48 Eigenvalues, 6 Necessary States

**Tier:** 2 | **Scope:** B | **Phase:** MINIMAL_STATE_AUTOMATON

## Statement

The 49x49 class-transition matrix has 48 significant eigenvalues (>0.01), meaning nearly all class-level transition profiles are informationally unique. Yet constraint-preserving compression requires only 6 states. The gap between 48 (information content) and 6 (structural necessity) defines the **free variation envelope**: within-state diversity that the grammar permits but does not structurally require.

## Evidence

- **Spectral analysis (T2):** Effective rank = 48 at threshold 0.01. Only 3 eigenvalues above 0.10. Role-level effective rank = 4.
- **NMF elbow (T2):** Reconstruction error drops steeply through k=3, then declines gradually. No sharp elbow above k=6.
- **Parameter layer (T7):** S4 (32 classes) has Gini=0.545, 81 unique MIDDLEs, 29 prefixes, 20 suffixes. Within-state JSD range [0.124, 0.634] — classes within the same state have genuinely different transition textures.
- **Positional variance (T7):** Between-state positional variance is 3.4x larger than within-state, confirming the 6-state partition captures real positional structure. FL_SAFE is heavily late-positioned (mean=0.816, 73% in final third).

## What the 43 Non-Essential Classes Encode

1. **Frequency variation:** Within S4, few classes dominate (C33 = 16.2%) while many are rare variants (Gini = 0.545)
2. **Morphological richness:** S4 has 81 unique MIDDLEs — material-specific execution vocabulary
3. **Transition texture:** Mean within-state JSD = 0.365 in S4 — classes have different detailed transition preferences while sharing the same macro-state identity
4. **Positional nuance:** Subtle early/late preferences within states

## Interpretation

The 49 classes provide lexical diversity; the 6 states provide structural law. The free variation envelope is not noise — it is the system's parametric control space for material-specific behavioral tuning within a fixed control topology.

## Provenance

- Extends: C121 (49 instruction classes), C973 (high-dimensional discrimination space)
- Method: `phases/MINIMAL_STATE_AUTOMATON/scripts/t2_spectral_analysis.py`, `t7_parameter_layer.py`
- Results: `phases/MINIMAL_STATE_AUTOMATON/results/t2_spectral.json`, `t7_parameter_layer.json`
