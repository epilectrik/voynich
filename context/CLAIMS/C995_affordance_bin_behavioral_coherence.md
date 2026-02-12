# C995: Affordance Bin Behavioral Coherence

**Tier:** 2
**Scope:** B
**Phase:** AFFORDANCE_STRESS_TEST

## Constraint

The 9 functional affordance bins (406 MIDDLEs, excluding 566 BULK_OPERATIONAL hapax) show independent behavioral discrimination across hazard distance, lane distribution, within-line position, and regime concentration. Cross-bin differentiation is significant at p < 10^-30 on every dimension tested.

## Evidence

### Cross-Bin Statistical Tests

| Dimension | Test | Statistic | p-value |
|-----------|------|-----------|---------|
| Hazard distance | Kruskal-Wallis | H=351.4 | 4.55e-71 |
| Lane distribution (QO/CHSH/NEUTRAL) | Chi-square | chi2=4556 | ~0 |
| Within-line position | Kruskal-Wallis | H=191.4 | 4.21e-37 |
| Regime concentration | Chi-square | chi2=887 | 8.38e-172 |
| Radial depth | Kruskal-Wallis | H=157.2 | 6.09e-30 |

### Key Bin Signatures

| Bin | Lane | Hazard Dist | Position | Regime |
|-----|------|-------------|----------|--------|
| STABILITY_CRITICAL (8) | **0% QO, 79.4% CHSH** | Close (2.07) | Mid-line | R1=60% |
| ENERGY_SPECIALIZED (7) | 47.7% QO | Distant (2.71) | Initial (29%) | **R1=89%** |
| SETTLING_SPECIALIZED (5) | 63.2% CHSH | Distant (3.18) | Initial (23%) | **R3=93%** |
| PRECISION_SPECIALIZED (2) | 49.0% CHSH | Most distant (3.58) | Q1=41% | **R4=71%** |
| FLOW_TERMINAL (0) | 66.8% neutral | Moderate | **Final (23%)** | R1=46% |
| HUB_UNIVERSAL (6) | Balanced | Closest (2.02) | Uniform | R1=53% |

### STABILITY_CRITICAL Absolute QO Exclusion

Bin 8 has 0.0% QO tokens across 3,905 observations. Combined with e_ratio=0.515 (4x median), this bin sits in pure stabilization space. This is structural exclusion, not statistical lean.

### Lane Inertia Differentiation

Bins separate into lane anchors and lane switchers:
- **Anchors**: PRECISION_SPECIALIZED (0.786), SETTLING_SPECIALIZED (0.784)
- **Switchers**: ENERGY_SPECIALIZED (0.396)
- Chi-square on bin x lane inertia: chi2=30.6, p=1.65e-04

### Near-Deterministic Regime Enrichment

Regime specialization is encoded directly at the MIDDLE bin level:
- ENERGY_SPECIALIZED: 89.4% REGIME_1
- SETTLING_SPECIALIZED: 93.0% REGIME_3
- PRECISION_SPECIALIZED: 70.6% REGIME_4

REGIME is not just folio-level weight modulation (C979) — it has vocabulary selection implications.

## Ablation Validation

Bin-level ablation (removing all tokens per bin) shows distributed structural importance: normalized degradation ranges 2.28-3.50 across all 9 bins. No single bin is catastrophically load-bearing (threshold >5 not crossed). The grammar distributes load rather than concentrating it.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C647 | EXTENDS - kernel signatures (k→QO, e→CHSH) confirmed at bin level with absolute boundaries |
| C649 | EXTENDS - lane partition now includes inertia dimension (anchor vs switcher) |
| C979 | EXTENDS - regime modulation shown to operate at MIDDLE vocabulary level, not just folio level |
| C987 | CONSISTENT - silhouette ceiling respected; bins validated by behavioral coherence, not clustering sharpness |
| C991 | CONSISTENT - radial depth differentiates bins (KW p=6.09e-30) |

## Provenance

- Scripts: `phases/AFFORDANCE_STRESS_TEST/scripts/t1_hazard_exposure.py` through `t4_energy_recovery.py`
- Results: `phases/AFFORDANCE_STRESS_TEST/results/t1_hazard_exposure.json` through `t4_energy_recovery.json`
- Ablation: `phases/BIN_HAZARD_NECESSITY/scripts/bin_ablation.py`
- Phase: AFFORDANCE_STRESS_TEST + BIN_HAZARD_NECESSITY

## Status

VALIDATED
