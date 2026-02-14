# C1017: Macro-State Dynamics Decompose into PREFIX Routing, Hazard Density, and Bridge Geometry

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** MACRO_DYNAMICS_VARIANCE_DECOMPOSITION (Phase 340)
**Extends:** C1015 (T8 informative failure: PREFIX alone cannot regenerate transition matrix)
**Strengthens:** C661 (PREFIX transforms behavior), C1003 (pairwise compositionality), C1004 (SUFFIX zero info)
**Relates to:** C1010 (6-state partition), C1012 (PREFIX positive channeling), C1016 (folio archetypes), C979 (REGIME modulation), C1001 (PREFIX dual encoding), C1011 (geometric independence)

---

## Statement

Four structural findings that decompose macro-state dynamics into identifiable sources:

**A. PREFIX routing is genuine, not tautological.** Within the same MIDDLE, PREFIX changes macro-state membership with 78.7% entropy reduction (z=65.59, p≈0, 1000 permutations). This is not the C662 tautology (PREFIX constraining which classes are available) — it is tested within MIDDLEs that span multiple states, measuring whether PREFIX predicts which state a token IS in when multiple are available. Non-AXM-spanning MIDDLEs show even stronger routing (85.9% reduction). Only 19.9% of this signal is positional (C1001); the remaining 80% is genuine morphological routing that survives position-preserving shuffling (z=41.78, p≈0).

**B. PREFIX routing is REGIME-invariant.** Within each of the 4 REGIMEs, PREFIX routing magnitude is nearly identical (range: 0.785–0.832, ratio 1.06). PREFIX is a universal state-routing mechanism, not modulated by process context. This contradicts the C979 prediction that transition weights are REGIME-dependent — the routing mechanism itself is fixed even though the transition matrix it operates within is not.

**C. Folio-level AXM self-transition variance decomposes as: REGIME+section (42.0%) + PREFIX entropy (5.1%) + hazard density (6.1%) + bridge geometry (6.3%) + residual (40.1%).** PREFIX composition, hazard token density, and bridge centroid position are independent, additive predictors of "forgiveness" (AXM basin depth). Their interactions are weak (ΔR²=0.030, confirming C1003 pairwise compositionality). SUFFIX entropy is uncorrelated with the residual (p=0.280, confirming C1004). Bridge density is constant at 1.0 (85/87 B MIDDLEs are bridges) — the bridge effect operates geometrically through manifold centroid positioning (PC1: rho=-0.459, p=0.00005; ΔR²=0.063, F=9.58, p=0.003), not as a folio-level density variable. The residual is significantly structured by archetype (F=6.71, p<0.0001), confirming that archetypes capture non-linear variance beyond the linear model.

**D. Archetype-specific slopes differ qualitatively.** Within-archetype regressions show that PREFIX and hazard density have different (sometimes opposite) effects across archetypes. PREFIX slope flips sign in archetype 5 (β=+0.024 vs negative elsewhere); hazard slope flips in archetype 6 (β=+0.009 vs negative elsewhere). Mean within-archetype R²=0.230 vs global R²=0.534, confirming that the global model captures between-archetype variance that local models cannot, while archetypes capture non-linear within-group structure that the global model misses.

---

## Evidence

### T1: MIDDLE-Conditioned PREFIX Routing (PASS)

For 34 MIDDLEs with ≥2 PREFIXes and ≥2 macro-states (out of 85 total MIDDLEs):

- Within-MIDDLE entropy reduction: **78.7%** (z=65.59, p≈0 vs 1000 permutations)
- Null (shuffled PREFIX within MIDDLE): 3.8% ± 1.1%
- AXM-only spanning (9 MIDDLEs): 58.5% reduction
- Non-AXM spanning (25 MIDDLEs): **85.9% reduction** (stronger signal in minority states)

This controls for the C662 tautology: PREFIX routing is measured within the same MIDDLE, so it cannot be explained by PREFIX constraining which MIDDLEs (hence which classes) are available.

### T2: Positional Null Model (PASS)

- Positional null (PREFIX shuffled within line-position quartile): mean=0.187 ± 0.014
- Observed (0.787) vs positional null: z=41.78, p≈0
- Positional contribution: **19.9%** of routing signal
- Remaining 80.1% is genuine morphological routing independent of line position

### T3: REGIME-Stratified PREFIX Routing (FAIL — informative)

| REGIME | Eligible MIDDLEs | Mean Reduction |
|--------|-----------------|----------------|
| REGIME_1 | 34 | 0.792 |
| REGIME_2 | 29 | 0.832 |
| REGIME_3 | 29 | 0.823 |
| REGIME_4 | 31 | 0.785 |

Range ratio: 1.06 (well below 1.5 threshold). PREFIX routing is **REGIME-invariant** — it is a universal morphological mechanism that operates identically across all process contexts.

### T4: Bridge Density and Hazard Density (PASS — reframed)

Bridge density is constant at 1.0 across all folios (85/87 B MIDDLEs are bridges). This confirms that the bridge effect operates at the geometric level (manifold centroid positioning, C1016.T8: ARI=0.141 vs 0.037), not as a density variable.

Bridge/gatekeeper overlap: 21/85 bridge MIDDLEs (24.7%) are in gatekeeper classes {15,20,21,22,25}. Bridge identity is NOT equivalent to gatekeeper identity — most bridge MIDDLEs (75.3%) are non-gatekeepers.

Hazard density differentiates archetypes: F=3.89, p=0.004, eta²=0.228.

### T5: Combined Variance Decomposition (PASS)

Dependent variable: folio-level AXM self-transition rate (operationalizes "forgiveness").

| Model | R² | ΔR² | F | p |
|-------|-----|-----|---|---|
| REGIME + section | 0.420 | — | — | — |
| + PREFIX entropy | 0.470 | 0.051 | 6.04 | 0.017 |
| + hazard density | 0.481 | 0.061 | 7.39 | 0.008 |
| + PREFIX + hazard | 0.534 | 0.115 | 7.63 | 0.001 |
| + interaction | 0.564 | 0.030 | 4.14 | 0.046 |
| + gatekeeper | 0.536 | 0.002 | 0.24 | 0.627 |

Key findings:
- PREFIX entropy and hazard density are **independently significant** predictors
- Their combined ΔR² (11.5%) exceeds their individual contributions (5.1% + 6.1% = 11.2%), indicating slight complementarity
- Interaction term is weak (ΔR²=0.030), confirming C1003 pairwise compositionality
- Gatekeeper density adds nothing beyond PREFIX + hazard (ΔR²=0.002)
- Total model: R²=0.534 (53.4% explained)
- Residual: 46.6%

Within-section stability: Bio/Herbal section alone achieves R²=0.606 (n=20 folios); Stars section R²=0.112 (n=23). The model is strongest in the largest homogeneous section.

### T5b: Archetype-Stratified Models (PASS)

Within-archetype regressions using PREFIX entropy + hazard density as predictors:

| Archetype | n | R² | β_PREFIX | β_hazard | Mean AXM self |
|-----------|---|-----|----------|----------|---------------|
| 1 | 10 | 0.511 | -0.021 | -0.013 | 0.822 |
| 2 | 13 | 0.183 | -0.022 | -0.002 | 0.673 |
| 3 | 7 | 0.415 | -0.037 | -0.017 | 0.610 |
| 4 | 5 | 0.142 | -0.004 | -0.041 | 0.568 |
| 5 | 7 | 0.080 | **+0.024** | -0.006 | 0.471 |
| 6 | 30 | 0.051 | -0.016 | **+0.009** | 0.673 |

Key findings:
- Slopes differ across archetypes: PREFIX slope range = 0.061, hazard slope range = 0.050
- PREFIX slope **flips sign** in archetype 5 (β=+0.024 vs negative in all others)
- Hazard slope **flips sign** in archetype 6 (β=+0.009 vs negative in all others)
- Mean within-archetype R² = **0.230** (vs global R²=0.534)
- The global model captures between-archetype variance; archetypes capture non-linear within-group structure

### T5c: Geometric Bridge Feature (PASS)

Bridge geometry operationalized via spectral embedding of the 85-MIDDLE compatibility matrix (100D), computing per-folio bridge centroid position, then PCA across folios.

| Feature | rho with AXM self | p |
|---------|-------------------|---|
| Bridge PC1 | -0.459 | 0.00005 |
| Bridge PC2 | 0.323 | 0.006 |
| Bridge norm | -0.378 | 0.001 |

Incremental variance beyond REGIME + section + PREFIX + hazard model:

| Model extension | R² | ΔR² | F | p |
|-----------------|-----|-----|---|---|
| + bridge PC1 | 0.597 | 0.063 | 9.58 | 0.003 |
| + bridge PC1+PC2 | 0.598 | 0.064 | 4.76 | 0.012 |
| + bridge norm | 0.568 | 0.034 | 4.77 | 0.033 |

Bridge PC1 adds **ΔR²=0.063** (F=9.58, p=0.003) beyond all morphological features — bridge geometry is a **load-bearing** dynamics predictor. PCA variance explained by first 5 components: 21.6%, 9.4%, 6.5%, 5.1%, 4.9%.

This confirms and quantifies C1016.T8's finding: bridge MIDDLEs carry archetype-predictive information through their geometric positioning in the discrimination manifold, not through their density (which is constant).

### T6: Residual Characterization (PASS)

| Candidate | rho | p |
|-----------|-----|---|
| SUFFIX entropy | 0.129 | 0.280 |
| Gatekeeper fraction | 0.017 | 0.890 |
| MIDDLE diversity | -0.067 | 0.576 |

SUFFIX entropy is uncorrelated (p=0.280), confirming C1004.

Residual vs archetype: F=6.71, p<0.0001. Archetypes capture **non-linear** variance that the linear model cannot. The 46.6% residual is not random — it reflects program-specific dynamical tuning that requires archetype-level (non-linear) description.

---

## Interpretation

This phase resolves C1015.T8's informative failure ("PREFIX alone cannot regenerate the transition matrix"). The resolution has four parts:

1. **PREFIX routing IS genuine** — but it operates as a state selector (which state a token lands in), not a dynamics generator (how states transition). T1/T2 confirm this: 78.7% within-MIDDLE routing, 80% non-positional.

2. **Dynamics require hazard token density as a second variable.** Hazard density (fraction of HAZARD_SOURCE/TARGET tokens) independently modulates AXM basin depth. Programs with more hazard tokens have weaker AXM attractors — they spend more time in active interchange states.

3. **Bridge geometry provides a third independent predictor.** Since 85/87 B MIDDLEs are bridges, bridge density is constant at 1.0 — "bridge" is not selective at the token level. But bridge GEOMETRIC POSITIONING (centroid location in the 100D discrimination manifold) adds ΔR²=0.063 (p=0.003) beyond all morphological features. This quantifies C1016.T8's finding: the bridge backbone functions as a geometry→dynamics conduit, translating vocabulary structure into dynamical behavior.

4. **The remaining 40.1% is non-linear and archetype-specific.** Archetypes capture structure that no linear combination of morphological features can explain: within-archetype R²=0.230 with qualitatively different slope profiles (sign flips in archetypes 5 and 6). This is consistent with C980's free variation envelope (66.3% program-specific) — archetype-specific tuning requires non-linear description.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C1015.T8 | **Resolved** — PREFIX alone cannot regenerate transitions because dynamics also require hazard density, bridge geometry, and non-linear archetype structure |
| C661 | **Operationalized beyond C662** — T1 proves routing is genuine within-MIDDLE, not just class restriction |
| C1003 | **Confirmed** — interaction term ΔR²=0.030 (weak), consistent with pairwise compositionality |
| C1004 | **Confirmed** — SUFFIX entropy uncorrelated with residual (p=0.280) |
| C979 | **Partially refined** — REGIME modulates transition weights (C979) but NOT the PREFIX routing mechanism itself (T3: invariant across REGIMEs) |
| C1001 | **Quantified** — 19.9% of PREFIX routing is positional; 80.1% is genuinely morphological |
| C1016 | **Extended** — archetype structure captures non-linear residual (F=6.71, p<0.0001); bridge geometry quantified as ΔR²=0.063 conduit |
| C1011 | **Consistent** — bridge density constant confirms geometric (not count-based) separation; bridge PC1 operationalizes the geometric signal |

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | MIDDLE-conditioned PREFIX routing significant (p<0.05) | z=65.59, p≈0 | PASS |
| P2 | PREFIX routing survives positional shuffling (p<0.05) | z=41.78, p≈0 | PASS |
| P3 | PREFIX routing varies by REGIME (ratio > 1.5) | ratio=1.06 | FAIL |
| P4 | Hazard density differentiates archetypes (p<0.05) | eta²=0.228, p=0.004 | PASS |
| P5 | PREFIX × hazard interaction weak (ΔR²<0.05) | ΔR²=0.030 | PASS |
| P6 | Full model R²>0.40 | R²=0.534 | PASS |
| P7 | SUFFIX entropy uncorrelated with residual (p>0.05) | p=0.280 | PASS |
| P8 | Archetype-stratified slopes differ from global model | β_PREFIX flips in arch.5, β_hazard flips in arch.6 | PASS |
| P9 | Bridge geometry adds significant variance (p<0.05) | ΔR²=0.063, F=9.58, p=0.003 | PASS |

8/9 passed → DYNAMICS_DECOMPOSED (T3 is informative: routing is universal, not REGIME-specific)

---

## Method

- 16,054 B corpus tokens mapped to 6-state partition (C1010) via 49-class grammar
- Morphological extraction via `scripts/voynich.py` Morphology class
- Within-MIDDLE entropy reduction: H(State|MIDDLE) - H(State|PREFIX,MIDDLE) for 34 eligible MIDDLEs
- 1,000-permutation null models for T1 (random PREFIX shuffle) and T2 (position-preserving PREFIX shuffle)
- REGIME stratification with 4 REGIMEs for T3
- OLS regression with nested model comparison (F-tests) for T5 variance decomposition
- Per-archetype OLS regressions for T5b slope analysis
- 100D spectral embedding of 85-MIDDLE compatibility matrix, per-folio bridge centroid PCA for T5c
- Spearman correlations for T6 residual characterization

**Script:** `phases/MACRO_DYNAMICS_VARIANCE_DECOMPOSITION/scripts/macro_dynamics_decomposition.py`
**Results:** `phases/MACRO_DYNAMICS_VARIANCE_DECOMPOSITION/results/macro_dynamics_decomposition.json`

---

## Verdict

**DYNAMICS_DECOMPOSED**: Macro-state dynamics decompose into four identifiable layers: (1) PREFIX routing (genuine, non-positional, REGIME-invariant; 78.7% within-MIDDLE entropy reduction); (2) hazard token density (independent additive predictor; eta²=0.228 for archetypes); (3) bridge geometry (manifold centroid PC1 adds ΔR²=0.063, p=0.003 — geometry→dynamics conduit is load-bearing); (4) non-linear archetype structure (40.1% residual significantly captured by C1016 archetypes; within-archetype slopes differ qualitatively with sign flips). Bridge contribution is geometric, not densimetric. SUFFIX contributes nothing. The system's dynamical personality is set by morphological routing + hazard exposure + bridge geometry + program-specific non-linear tuning.
