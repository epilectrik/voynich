# C1367 — Folio Accent Vector Analysis

**Tier:** 2
**Scope:** B, folio, accent, PCA, category, archetype
**Phase:** 480 (FOLIO_ACCENT_VECTOR)
**Depends on:** C1366, C1016, C1048, C1294, C638, C458

## Constraint

The folio accent (C1366, 11 systematic gap features from M2.1 generative gap) is a low-dimensional structure dominated by a single component (PC1 = 58.9%) that is weakly correlated with C1016 archetypes (|rho| = 0.274) — the accent captures genuinely new folio-level structure that archetypes do not. THERMAL category fraction predicts the accent beyond kernel balance (partial rho = 0.588 after k/e control). BIO's accent is section-intrinsic (persists within REGIME_1, p = 0.019).

## T1: PCA Structure

| Component | Variance | Cumulative | Top loadings |
|-----------|----------|------------|-------------|
| PC1 | 58.9% | 58.9% | mean_run_length (0.372), axm_fraction (0.367), axm_self_transition (0.356) |
| PC2 | 20.5% | 79.4% | bigram_entropy (0.460), class_entropy (0.448), class_concentration (-0.416) |
| PC3 | 8.9% | 88.3% | mean_word_length (0.668), category_entropy (-0.460), suffix_rate (0.400) |

PC1 = AXM dynamics intensity (how strongly the macro-automaton orbits its home state).
PC2 = sequential complexity (how diverse the transition patterns are).
PC3 = morphological texture (word length, suffix usage, category specialization).

## T2: Gating Test — NEW_STRUCTURE

| Test | rho | p |
|------|-----|---|
| PC1 vs archetype | -0.274 | 0.020 |
| PC2 vs archetype | 0.036 | 0.761 |
| Composite anomaly vs archetype | -0.258 | 0.029 |

**GATE: NEW_STRUCTURE** (|rho| = 0.274 < 0.5). The accent and archetypes are weakly correlated. ANOVA: archetypes explain 33.4% of composite anomaly variance (F=6.61, p<0.0001, eta-sq=0.334), but 66.6% is independent.

**Interpretation:** Archetypes describe WHAT the macro-dynamics are. The accent describes WHERE the folio deviates from what M2.1 generates. These are complementary, not redundant.

## T3: THERMAL Predicts Accent Beyond Kernel

| Category | rho (PC1) | p | Partial rho (kernel ctrl) | Partial p |
|----------|-----------|---|--------------------------|-----------|
| **THERMAL** | **0.751** | **<0.0001** | **0.588** | **<0.0001** |
| TRANSITION | -0.608 | <0.0001 | -0.287 | 0.015 |
| FLOW | -0.445 | 0.0001 | -0.015 | 0.902 |
| OPERATION | 0.107 | 0.373 | -0.251 | 0.033 |
| CONTAINMENT | -0.266 | 0.024 | -0.152 | 0.203 |
| STAGING | 0.053 | 0.661 | -0.091 | 0.448 |
| MONITORING | 0.145 | 0.223 | 0.015 | 0.901 |
| MARKING | -0.015 | 0.904 | -0.205 | 0.085 |

THERMAL fraction survives kernel control (partial rho = 0.588). C1294 showed category fractions do NOT extend the AXM model. But the accent is the M2.1 RESIDUAL, not AXM — and THERMAL DOES extend the accent. The accent has a category dimension that kernel balance alone does not capture.

TRANSITION shows a weaker negative partial correlation (-0.287, p=0.015). FLOW's raw correlation (-0.445) vanishes after kernel control — it was entirely kernel-mediated.

## T4: Within-Quire Ordering — Inconclusive

No quires have 3+ valid Currier B folios, so within-quire ordering could not be tested. (B folios are spread across quires.)

## T5: Archetype 1 — BIO-Dominated, Homogeneous

10 archetype-1 folios: 8 BIO, 1 HERBAL, 1 STARS. REGIMEs: 6 R1, 3 R3, 1 R2.

| Feature | Mean |z| | Sign agreement |
|---------|---------|----------------|
| class_concentration | 4.673 | 0.90 |
| axm_fraction | 4.144 | 1.00 |
| mean_run_length | 4.100 | 1.00 |
| class_entropy | 3.489 | 1.00 |
| bigram_entropy | 3.434 | 0.90 |

Mean sign agreement = 0.88. These folios are highly homogeneous — all deviate in the same direction (more concentrated, more AXM, longer runs). Archetype 1 is effectively "the BIO accent at maximum strength."

## T6: BIO Accent Is Section-Intrinsic

Within REGIME_1 only:
- BIO (n=17): mean anomaly 1.573
- Non-BIO (n=14): mean anomaly 1.234
- Mann-Whitney: U=172, p=0.019

BIO's accent persists after REGIME control. The distinctive accent is section-intrinsic, not REGIME-mediated.

## Synthesis

The folio accent is a three-layer structure:
1. **PC1 (59%):** AXM dynamics intensity — correlated with THERMAL vocabulary emphasis (rho=0.588 after kernel control). Programs with more THERMAL vocabulary have stronger AXM orbits, longer runs, more concentrated class distributions. This is the operational tempo dial.
2. **PC2 (21%):** Sequential complexity — orthogonal to archetypes (rho=0.036). How diverse the transition patterns are, independent of AXM intensity.
3. **PC3 (9%):** Morphological texture — word length and suffix patterns, independent of both dynamics and complexity.

The accent is weakly archetype-correlated (33% shared variance) but captures 67% independent structure. Its strongest predictor is THERMAL category fraction — the accent separates programs by how thermally intensive they are, above and beyond their kernel composition.

## Provenance

Script: `phases/FOLIO_ACCENT_VECTOR/scripts/folio_accent_vector.py`
Results: `phases/FOLIO_ACCENT_VECTOR/results/folio_accent_vector.json`
