# C1037: AXM Class Composition Is Redundant — Within-AXM Class Profiles Do Not Decompose the Residual

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** AXM_CLASS_COMPOSITION (Phase 359)
**Extends:** C1035 (57% residual irreducible at folio level), C1036 (exit pathways frequency-neutral)
**Strengthens:** C1023 (PREFIX routing is load-bearing), C458 (further localizes asymmetry)
**Relates to:** C1017 (AXM self-transition variance), C1010 (6-state partition), C980 (free variation envelope)

---

## Statement

Per-folio AXM class composition profiles (which of the 32 AXM classes are active, in what proportions) do not decompose C1035's 57% irreducible AXM self-transition residual. Class profile PCA produces LOO R² = -0.071 on C1035 residuals (worse than predicting the mean). When combined with C1017's baseline model, class PCs add only +0.005 incremental LOO R² (0.433 → 0.437). The class composition information is almost entirely redundant with what REGIME, section, PREFIX entropy, hazard density, and bridge geometry already capture.

Two findings confirm the grammar's architecture: (1) PREFIX and class composition are strongly coupled (PREFIX PC1 vs Class PC1 rho = -0.55, p < 0.000001), confirming that PREFIX routing (C1023) governs within-AXM class selection; (2) REGIME explains less than 30% of class profile variance on all PCs (eta² = 0.297, 0.238, 0.080), confirming that class composition is program-specific rather than regime-determined.

This is the third consecutive elimination of a candidate stratum for the irreducible residual: C1035 eliminated aggregate folio statistics, C1036 eliminated AXM boundary transitions, and C1037 eliminates within-AXM class composition. The remaining untested stratum is micro-sequential dynamics — the temporal ordering of tokens within AXM runs.

---

## Evidence

### S2: PCA of Class Compositions

CLR-transformed (pseudocount 0.5) 72×32 class proportion matrix. PCA via SVD retains 5 components at cumulative 49.6% variance.

| PC | Variance Explained | Cumulative |
|----|-------------------|------------|
| PC1 | 17.6% | 17.6% |
| PC2 | 12.7% | 30.3% |
| PC3 | 7.7% | 38.0% |
| PC4 | 6.5% | 44.5% |
| PC5 | 5.0% | 49.6% |

### S3: Multinomial Overdispersion (PARTIAL)

Global chi² = 4365.4 (df = 2232, p < 0.0001) — class profiles are not pure multinomial sampling. However, only 7/32 classes exceed the 2.0 overdispersion threshold: classes 2 (4.75), 33 (3.77), 37 (2.97), 32 (2.82), 48 (2.32), 43 (2.09), 17 (2.04). Most classes (25/32) show mild or no overdispersion. The structured variation is concentrated in a minority of classes.

### S4: Residual Prediction (FAIL — no signal)

| Model | Train R² | LOO R² |
|-------|----------|--------|
| Class PCs alone on residual | — | -0.071 |
| C1017 baseline | 0.564 | 0.433 |
| C1017 + Class PCs (best k=2) | 0.595 | 0.437 |
| Incremental LOO | — | +0.005 |

Class PCs predict AXM self-transition rate directly (LOO R² = 0.463), but this information is entirely absorbed by the existing C1017 model. The incremental contribution (+0.005) is noise-level. Class composition captures the same variance as REGIME + section + PREFIX entropy — it is a different representation of the same underlying structure.

### S5: C458 Localization (FAIL — no differential clamping)

21 of 32 AXM classes are hazard-adjacent (>20% of their MIDDLEs are hazard-source or hazard-target MIDDLEs). Per-class CV comparison:

| Group | Mean CV | N classes |
|-------|---------|-----------|
| Hazard-adjacent | 1.048 | 21 |
| Non-hazard | 1.074 | 11 |
| Difference | -0.026 | — |

The CV difference (0.026) is far below the 0.05 threshold. C458's clamping does not manifest as differential cross-folio stability of hazard-adjacent vs non-hazard class fractions. Aggregate class proportions are too coarse to detect C458.

### S6: PREFIX Mediation (PASS — strong coupling)

PREFIX PC1 vs Class PC1: rho = -0.550, p < 0.000001

PREFIX distribution within AXM strongly co-varies with class composition. This confirms C1023: PREFIX routing governs which AXM classes are activated. The two are not independent degrees of freedom — they are coupled through the routing mechanism.

### S7: Class Diversity (FAIL — no signal)

| Metric | Value |
|--------|-------|
| Mean class entropy | 3.934 bits |
| Effective classes | 15.5 |
| Entropy vs AXM self-transition | rho = 0.070, p = 0.562 |
| Entropy vs C1035 residual | rho = 0.039, p = 0.744 |

Class diversity is neither correlated with AXM self-transition rate nor with the residual. Folios that use more classes do not have systematically different AXM dynamics.

### S8: Variance Decomposition (PASS — program-specific)

| PC | eta²(REGIME) | eta²(Section) | eta²(Archetype) |
|----|-------------|---------------|-----------------|
| PC1 | 0.297 | 0.651 | 0.434 |
| PC2 | 0.238 | 0.547 | 0.164 |
| PC3 | 0.080 | 0.037 | 0.136 |

REGIME explains <30% on all three PCs. Section explains more (up to 65%), consistent with positional effects. Class composition is predominantly program-specific within REGIME boundaries — consistent with C458's recovery freedom and C980's free variation envelope.

---

## Interpretation

This is the third consecutive elimination result in the residual decomposition series:

**1. Class composition is redundant, not absent.** The class PCs DO predict AXM self-transition (LOO R² = 0.463), confirming that class composition carries structural information. But this information is entirely captured by the existing C1017 model — REGIME, section, PREFIX entropy, hazard density, and bridge geometry already encode the class composition signal through shared upstream determinants.

**2. PREFIX and class composition are coupled.** The strong PREFIX-class correlation (rho = -0.55) confirms that PREFIX routing (C1023) governs within-AXM class activation. These are not independent axes of variation. This is architecturally consistent: PREFIX conditions which classes are available, and the class composition reflects this conditioning.

**3. The residual is not in composition but may be in sequence.** Three strata are now eliminated: aggregate statistics (C1035), boundary transitions (C1036), and within-AXM class composition (C1037). What remains untested is micro-sequential dynamics — the temporal ordering of tokens within AXM runs. C1024 shows MIDDLE carries 0.070 bits of execution asymmetry (vs PREFIX 0.018 bits). This directional information lives in token sequences, which are not captured by composition profiles.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | Overdispersion ratio > 2.0 for >= 50% of classes | 7/32 (22%) | FAIL |
| P2 | Class PCs LOO R² > 0.10 on C1035 residual | LOO R² = -0.071 | FAIL |
| P3 | CV(hazard-adjacent) < CV(non-hazard), diff > 0.05 | diff = -0.026 | FAIL |
| P4 | \|rho\| > 0.30 between PREFIX PC1 and Class PC1 | rho = -0.550 | PASS |
| P5 | \|rho\| > 0.25 between class entropy and AXM self-transition | rho = 0.070 | FAIL |
| P6 | eta²(REGIME) < 0.30 on PC1-PC3 | max = 0.297 | PASS |

2/6 passed → AXM_CLASS_COMPOSITION_REDUNDANT

---

## Method

- 72 B folios with >= 50 state transitions (C1010 6-state partition)
- Per-folio class composition: fraction of AXM tokens in each of 32 AXM classes
- CLR transform (pseudocount 0.5) for compositional data
- PCA via numpy SVD, retain PCs with >5% variance each (5 components, cumulative 49.6%)
- Multinomial overdispersion: observed variance / expected variance per class
- Hazard-adjacent class identification: gatekeeper classes {15,20,21,22,25} ∪ classes with >20% hazard MIDDLEs
- LOO cross-validation: manual implementation (fit OLS on 71, predict 1)
- Incremental R²: C1017 baseline vs C1017 + class PCs
- PREFIX mediation: PREFIX distribution PCA (30 prefixes), Spearman PC1 vs Class PC1
- Eta-squared by REGIME, section, archetype on class PCs

**Script:** `phases/AXM_CLASS_COMPOSITION/scripts/axm_class_composition.py`
**Results:** `phases/AXM_CLASS_COMPOSITION/results/axm_class_composition.json`

---

## Verdict

**AXM_CLASS_COMPOSITION_REDUNDANT**: Per-folio AXM class composition does not decompose the 57% irreducible residual (C1035). Class PCs produce LOO R² = -0.071 on the residual and add only +0.005 incremental LOO R² beyond C1017's baseline. The class composition signal is entirely absorbed by existing predictors — it is a different representation of the same structural variation. PREFIX and class composition are strongly coupled (rho = -0.55), confirming PREFIX routing (C1023) governs class activation. C458's asymmetry does not manifest as differential class-level stability. Three strata are now eliminated (aggregate statistics, boundary transitions, class composition); the remaining candidate is micro-sequential dynamics within AXM runs.
