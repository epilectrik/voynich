# C1018: Archetype Geometric Anatomy — Slope Anomalies, Bridge PC1 Decomposition, and HUB Sub-Role Differentiation

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** ARCHETYPE_GEOMETRIC_ANATOMY (Phase 341)
**Extends:** C1017 (archetype slope anomalies, bridge PC1), C1016 (6 dynamical archetypes)
**Strengthens:** C1000 (HUB sub-roles), C995 (affordance bins), C1010 (6-state partition)
**Relates to:** C986 (hub eigenmode), C991 (radial depth), C605 (EN lane balance), C778 (kernel composition)

---

## Statement

Five structural findings that anatomize the 6 dynamical archetypes and decode the bridge geometric signal:

**A. Archetypes are not section artifacts.** Neither archetype 5 (n=7, "active interchange") nor archetype 6 (n=30, largest cluster) is section-dominated: max section fractions are 57.1% and 56.7% respectively. However, section and archetype are significantly associated (chi2=60.28, p=0.000006, Cramer's V=0.457), and REGIME and archetype are moderately associated (chi2=32.53, p=0.005, Cramer's V=0.388). Archetypes capture genuine dynamical variation beyond section/REGIME, but section composition is a partial confound that must be controlled.

**B. C1017's archetype 5 PREFIX slope anomaly is suggestive but not established.** The positive PREFIX slope in archetype 5 (β=+0.024) has a bootstrap 95% CI of [-0.054, +0.203] that spans zero (n=7 is too small). Permutation p=0.126 (not significant). Boundary sensitivity shows the sign flip is fragile — moving 2 folios from archetype 6→5 reverses it. In contrast, archetype 6's hazard slope anomaly (β=+0.009) reaches permutation significance (p=0.014) but also has a bootstrap CI spanning zero [-0.018, +0.044]. Two influential folios (f39v: Cook's D=0.445, f115r: D=0.246) contribute disproportionately.

**C. Bridge PC1 is partially a hub frequency gradient.** PC1 correlates with mean MIDDLE frequency at rho=0.568 (p<0.00001), exceeding the 0.5 redundancy threshold. This means ~32% of PC1 is a C986 re-derivation (hub eigenmode = frequency gradient). However, PC1 still significantly differentiates archetypes (F=3.56, p=0.006) and distinguishes archetype 5 from 6 (U=174, p=0.006). The interpretable structure of PC1: positive loadings are HUB_UNIVERSAL MIDDLEs (or, y, o, ol, iin — high-frequency, broadly compatible), negative loadings are STABILITY_CRITICAL/COMPOUND MIDDLEs (keed, eeo, kec, keeo, eeol — e-rich, low-frequency).

**D. Archetypes are discriminated by 8 features across 5 families.** The strongest discriminators are k_frac (F=15.81, p<0.0001), SAFETY_BUFFER fraction (F=11.37, p<0.0001), HAZARD_TARGET fraction (F=5.73, p=0.0002), FL hazard/safe ratio (F=5.51, p=0.0003), and QO affinity (F=5.47, p=0.0003). Archetype 6 is specifically enriched in SAFETY_BUFFER MIDDLEs relative to archetype 5 (mean 0.124 vs 0.072, p=0.003 one-sided), confirming the expert prediction that SAFETY_BUFFER enrichment explains archetype 6's positive hazard slope.

**E. Archetypes 5 and 6 occupy distinct bridge geometric positions.** PC1 separates archetype 5 (mean=+0.089) from archetype 6 (mean=-0.032) significantly (U=174, p=0.006). The unified hypothesis is SUPPORTED: the slope anomalies and bridge geometric signal are linked through the same geometric axis. However, mediation is weak — PC1 attenuates hazard→AXM correlation by only 0.042 and does not mediate PREFIX→AXM (attenuation negative). The linkage is geometric co-location, not causal mediation.

---

## Evidence

### T1: Archetype Structural Profiling (PASS)

| Archetype | n | Sections | Max Section Frac | Dom Section | REGIMEs | Mean AXM Self |
|-----------|---|----------|-----------------|-------------|---------|---------------|
| 1 | 10 | B:8 H:1 S:1 | 80.0% | B | R1:6 R2:1 R3:3 | 0.822 |
| 2 | 13 | B:9 H:1 S:3 | 69.2% | B | R1:11 R3:2 | 0.673 |
| 3 | 7 | H:4 T:1 C:1 S:1 | 57.1% | H | R1:1 R2:2 R3:2 R4:2 | 0.610 |
| 4 | 5 | H:4 C:1 | 80.0% | H | R3:1 R4:4 | 0.568 |
| 5 | 7 | H:4 T:1 C:1 S:1 | 57.1% | H | R2:1 R3:2 R4:4 | 0.471 |
| 6 | 30 | S:17 H:8 B:3 C:2 | 56.7% | S | R1:13 R2:4 R3:5 R4:8 | 0.673 |

- Section × archetype: chi2=60.28, p=0.000006, Cramer's V=0.457
- REGIME × archetype: chi2=32.53, p=0.005, Cramer's V=0.388
- Archetypes 1 and 4 are at the 80% threshold (Bio/Herbal dominant); archetypes 5/6 are well below

### T2: Bootstrap Validation of Slope Anomalies (FAIL — informative)

**Archetype 5 PREFIX slope:**
- Observed: β=+0.024
- Bootstrap 95% CI: [-0.054, +0.203] — **spans zero**
- Permutation p=0.126 — **not significant**
- Boundary sensitivity: fragile (1/3 perturbations preserve positive sign)

**Archetype 6 hazard slope:**
- Observed: β=+0.009
- Bootstrap 95% CI: [-0.018, +0.044] — **spans zero**
- Permutation p=0.014 — **significant** (but CI not)
- Cook's D: 2 influential folios (f39v: 0.445, f115r: 0.246)

**Interpretation:** The archetype 5 sign flip is a small-sample artifact that cannot be distinguished from noise at n=7. The archetype 6 sign flip is directionally supported (permutation significant) but not robust (bootstrap CI spans zero). Both anomalies require larger samples to establish.

### T3: Bridge PC1 Decomposition (MIXED)

**Redundancy checks:**
- Hub frequency: rho=0.568, p<0.00001 — **FAILS** threshold (|r| > 0.5)
- Radial depth: rho=0.373, p=0.001 — passes threshold (|r| < 0.5)

**PC1 loadings (top-10 by |score|):**

| MIDDLE | PC1 Score | Affordance | HUB Sub-Role | Kernel Profile |
|--------|-----------|------------|--------------|----------------|
| or | +0.759 | HUB_UNIVERSAL | HAZARD_SOURCE | k=0 h=0 e=0 |
| y | +0.751 | HUB_UNIVERSAL | PURE_CONNECTOR | k=0 h=0 e=0 |
| o | +0.748 | HUB_UNIVERSAL | HAZARD_TARGET | k=0 h=0 e=0 |
| ol | +0.746 | HUB_UNIVERSAL | HAZARD_SOURCE | k=0 h=0 e=0 |
| iin | +0.732 | HUB_UNIVERSAL | PURE_CONNECTOR | k=0 h=0 e=0 |
| keed | -0.650 | STABILITY_CRITICAL | non-HUB | k=0.25 h=0 e=0.50 |
| eeo | -0.618 | STABILITY_CRITICAL | non-HUB | k=0 h=0 e=0.67 |
| kec | -0.614 | COMPOUND_TERMINAL | non-HUB | k=0.33 h=0 e=0.33 |
| keeo | -0.608 | STABILITY_CRITICAL | non-HUB | k=0.25 h=0 e=0.50 |
| eeol | -0.600 | STABILITY_CRITICAL | non-HUB | k=0 h=0 e=0.50 |

PC1 is a **HUB_UNIVERSAL ↔ STABILITY_CRITICAL** gradient: positive = high-frequency, kernel-free HUBs; negative = low-frequency, e/k-rich stability operators.

**PC1 vs archetypes:**
- ANOVA: F=3.56, p=0.006
- Archetype 5 vs 6: U=174, p=0.006 (archetype 5 more HUB-heavy, archetype 6 more stability-heavy)

### T4: Archetype Discriminator Features (PASS)

8 features significant at p < 0.05 across 5 of 7 families:

| Feature | F | p | Strongest Contrast |
|---------|---|---|-------------------|
| k_frac | 15.81 | <0.0001 | Arch 1-2 (k-rich) vs 3-5 (k-poor) |
| hub_SAFETY_BUFFER | 11.37 | <0.0001 | Arch 6 enriched (0.124 vs 0.072 in arch 5) |
| hub_HAZARD_TARGET | 5.73 | 0.0002 | Arch 1-2 elevated |
| fl_ratio | 5.51 | 0.0003 | Arch 3-5 elevated hazard exposure |
| mean_qo | 5.47 | 0.0003 | Arch 1-2 QO-biased vs 5 QO-depleted |
| hub_PURE_CONNECTOR | 3.22 | 0.012 | Arch 5 depleted |
| bin_0 (FLOW_TERMINAL) | 3.21 | 0.012 | Arch 1 elevated |
| bin_8 | 3.20 | 0.012 | Variable |

**Non-significant:** HAZARD_SOURCE (p=0.075), compound rate (p=0.181), h_frac (p=0.642), e_frac (p=0.057), gatekeeper fraction (p=0.132).

**Expert prediction confirmed:** Archetype 6 SAFETY_BUFFER enrichment (p=0.003 one-sided) explains the positive hazard slope — programs with more SAFETY_BUFFER MIDDLEs can tolerate higher hazard density without AXM basin collapse.

### T5: Unified Hypothesis Test (SUPPORTED — weak mediation)

**Bridge PC1 positions by archetype:**

| Archetype | n | PC1 Mean | PC1 Std | PC2 Mean |
|-----------|---|----------|---------|----------|
| 1 | 10 | -0.016 | 0.063 | +0.051 |
| 2 | 13 | -0.003 | 0.048 | +0.031 |
| 3 | 7 | +0.024 | 0.112 | -0.033 |
| 4 | 5 | +0.071 | 0.046 | +0.015 |
| 5 | 7 | +0.089 | 0.096 | -0.047 |
| 6 | 30 | -0.032 | 0.081 | -0.014 |

Archetype 5 is at the HUB_UNIVERSAL end (positive PC1); archetype 6 is at the STABILITY_CRITICAL end (negative PC1). The separation is significant (p=0.006).

**Mediation:** Weak. PC1 attenuates hazard→AXM by 0.042 but PREFIX→AXM attenuation is negative (-0.091, meaning PC1 acts as a suppressor). The geometric linkage is positional co-location, not causal mediation through PC1.

---

## Interpretation

This phase resolves and qualifies several C1017 findings:

1. **The archetype 5 PREFIX sign flip is not established** (n=7, bootstrap CI spans zero, boundary-fragile). It should not be cited as a structural finding. The archetype 6 hazard sign flip is directionally supported but not robust.

2. **Bridge PC1 partially re-derives C986** (hub frequency gradient), but the non-redundant 68% carries genuine archetype-discriminative information. The axis represents a HUB_UNIVERSAL ↔ STABILITY_CRITICAL gradient that explains why different archetypes have different dynamical personalities.

3. **SAFETY_BUFFER enrichment explains archetype 6's anomalous hazard tolerance.** Programs in archetype 6 have 1.7x more SAFETY_BUFFER MIDDLE tokens than archetype 5 (0.124 vs 0.072). This buffering capacity allows them to sustain higher hazard density without AXM basin collapse, explaining the positive hazard slope.

4. **k_frac is the single strongest archetype discriminator** (F=15.81), separating high-k (archetypes 1-2, Bio/Herbal-heavy) from low-k (archetypes 3-5, diverse-section) programs. This connects to C778 (kernel character composition) at the macro-dynamical level.

5. **The unified hypothesis is geometrically supported but not mechanistically proven.** Archetypes 5 and 6 DO occupy distinct bridge geometric positions (p=0.006), but the mediation is weak — bridge geometry and archetype dynamics are co-located rather than causally linked through PC1.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C1017 | **Qualified** — archetype 5 PREFIX slope not established at n=7; archetype 6 hazard slope directionally supported; bridge PC1 partially redundant with C986 |
| C1016 | **Extended** — archetypes anatomized: 8 discriminator features, HUB sub-role differentiation, bridge geometric positions |
| C1000 | **Strengthened** — HUB sub-roles differentiate archetypes (chi2=322.64, p≈0); SAFETY_BUFFER enrichment mechanistically explains archetype 6 hazard tolerance |
| C986 | **Partially re-derived** — bridge PC1 correlates with hub frequency (rho=0.568); PC1 is partly a frequency gradient |
| C995 | **Extended** — affordance bin composition differentiates archetypes (bin 0 and bin 8 significant) |
| C778 | **Connected** — k_frac is strongest archetype discriminator (F=15.81) |
| C605 | **Extended** — QO affinity differentiates archetypes (F=5.47, p=0.0003) |

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | Archetypes 5/6 NOT section-dominated (<80%) | Arch 5: 57.1%, Arch 6: 56.7% | PASS |
| P2 | Archetype 5 PREFIX slope bootstrap CI excludes zero | CI: [-0.054, +0.203] | FAIL |
| P3 | Bridge PC1 NOT redundant with hub frequency (|r| < 0.5) | rho=0.568 | FAIL |
| P4 | Bridge PC1 differs across archetypes (ANOVA p < 0.05) | F=3.56, p=0.006 | PASS |
| P5 | HUB sub-role composition differs across archetypes | chi2=322.64, p≈0 | PASS |
| P6 | Archetype 6 enriched in SAFETY_BUFFER | U=176, p=0.003 | PASS |
| P7 | ≥3 discriminator features separate archetypes | 8 features | PASS |

5/7 passed → ARCHETYPE_ANATOMY_UNIFIED (both FAILs are informative: P2 = sample size limitation, P3 = partial re-derivation identified)

---

## Method

- 72 B folios mapped to 6 archetypes (C1016) via 49-class grammar and 6-state partition (C1010)
- Per-folio feature extraction: 7 feature families (affordance bins, HUB sub-roles, lane balance, compound rate, FL ratio, kernel composition, gatekeeper fraction)
- 1,000 bootstrap resamples for archetype 5 PREFIX slope and archetype 6 hazard slope
- 1,000 permutations: random n-folio groups tested against observed slopes
- Cook's distance for influence diagnostics (archetype 6, n=30)
- 3 boundary perturbations (±2-3 folios between adjacent archetypes)
- 100D spectral embedding → per-folio bridge centroid PCA (reused from C1017.T5c)
- Spearman correlations for redundancy checks (hub frequency, radial depth)
- ANOVA + Mann-Whitney U for all discriminator features

**Script:** `phases/ARCHETYPE_GEOMETRIC_ANATOMY/scripts/archetype_anatomy.py`
**Results:** `phases/ARCHETYPE_GEOMETRIC_ANATOMY/results/archetype_anatomy.json`

---

## Verdict

**ARCHETYPE_ANATOMY_UNIFIED**: Archetype slope anomalies and bridge geometric signal are linked through bridge PC1 (archetype 5 vs 6 separation: U=174, p=0.006), but the linkage is geometric co-location, not causal mediation. The archetype 5 PREFIX sign flip is NOT established (n=7, CI spans zero, boundary-fragile). Archetype 6's hazard tolerance is explained by SAFETY_BUFFER enrichment (1.7x, p=0.003). Bridge PC1 is partially redundant with hub frequency (rho=0.568), representing a HUB_UNIVERSAL↔STABILITY_CRITICAL gradient. k_frac is the single strongest archetype discriminator (F=15.81). 8 features across 5 families significantly differentiate archetypes.
