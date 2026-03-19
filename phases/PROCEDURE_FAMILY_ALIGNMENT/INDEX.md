# Phase 604: PROCEDURE_FAMILY_ALIGNMENT

**Status:** COMPLETE
**Verdict:** SPECIFICITY_FAILURE (N1 fails — theoretical not worst-fitting family)
**Constraints:** C1749-C1751
**Script:** `scripts/procedure_family_alignment.py` (~7s)
**Results:** `results/procedure_family_alignment_results.json` (10.5 KB)
**Pre-registration:** `PREDICTIONS.md` (SHA-256: `2775f975...`)

## Motivation

Phase 603 confirmed that pseudo-Lull's Testamentum and the Voynich share the same midprocess control architecture (C1744-C1748). Phase 604 tests whether that shared architecture extends to **procedure-family alignment** — whether pseudo-Lull's explicitly characterized operation families (distillation, fixation, sublimation, dissolution) predict specific groupings of Voynich operational units.

**Design principle:** Compare signature bundles, not single axes. Internal discrimination gate before touching Voynich data. Pre-registered verdict tree with negative controls.

## Results

### S1: Calibration Anchor -- PASS
- Stars R1 ey_rate: 0.1823 (n=10) vs R3: 0.1039 (n=12)
- Mann-Whitney U=112.0, p=0.0003
- Replicates C1735/C1740

### Stage 1: Internal Discrimination Gate -- PASS (Gate A)
- **Gate A (Univariate):** 2 Bonferroni dimensions survive (termination_rate H=16.0 p=0.0012; chain_rate H=13.9 p=0.003). 3 nominal (+ monitoring_density p=0.011).
- **Gate B (LOO Classifier):** FAIL (accuracy 0.333 < chance 0.356)
- Gate passes via Gate A.

### Family Prototypes (7D)
| Family | n_ch | monitoring | correction | heat | judgment | termination | chain | operational |
|--------|------|-----------|------------|------|----------|-------------|-------|-------------|
| distillation | 16 | 0.77 | 3.99 | 13.33 | 1.52 | 4.87 | 3.91 | 3.84 |
| fixation | 10 | 1.50 | 4.22 | 11.23 | 1.62 | 11.55 | 9.73 | 5.20 |
| sublimation | 7 | 1.57 | 3.57 | 11.37 | 0.00 | 12.20 | 9.35 | 3.71 |
| dissolution | 12 | 0.58 | 0.76 | 7.09 | 2.48 | 2.59 | 2.78 | 2.25 |
| theoretical_neg | 45 | 1.26 | 2.99 | 10.24 | 1.52 | 3.08 | 4.11 | 5.33 |

### Approach A Assignments (82 folios, 3D cosine)
| Family | n | Sections | REGIMEs | Apparatus |
|--------|---|----------|---------|-----------|
| distillation | 29 | 15 Bio, 8 Stars, 6 Herbal | 24 REGIME_1 | 15 A1 |
| fixation | 6 | 5 Bio, 1 Herbal | 5 REGIME_1 | 5 A1 |
| sublimation | 22 | 14 Herbal, 5 Stars | 11 REGIME_3, 7 REGIME_2 | 11 A3, 8 A2 |
| dissolution | 25 | 11 Herbal, 10 Stars | 9 REGIME_3, 9 REGIME_4 | 16 A3, 7 A2 |

### P1: Conservative Anchor (Distillation -> Stars/A3) -- PASS
- Stars enrichment: OR=0.965, p=0.624 (not enriched)
- A3 enrichment: OR=0.375, p=0.988 (not enriched)
- **Within-A3 specificity: p=0.0006** (distillation-assigned A3 folios have higher k_ratio)
- Passes via within-stratum specificity

### P2: Bold Target (Fixation -> A2/Herbal) -- FAIL
- Herbal enrichment: OR=0.290, p=0.955 (not enriched)
- A2 enrichment: OR=0.0, p=1.0 (not enriched — 0/6 fixation folios are A2)
- Within-Herbal specificity: p=1.0 (only 1 fixation-assigned Herbal folio)

### P3: Safety Discriminant -- FAIL (WRONG DIRECTION)
- Fixation mean safety_balance: 0.182 (n=6)
- Distillation mean safety_balance: 0.116 (n=29)
- **Predicted fixation < distillation; actual fixation > distillation**
- U=35.0, p=0.991 (one-sided, wrong direction)
- Rank-biserial: 0.598

### P4: Monitoring Contrast -- PASS
- Sublimation mean h_ratio: 0.235 (n=22)
- Distillation mean h_ratio: 0.113 (n=29)
- U=638.0, p=6.9e-10, rank_biserial=-1.0 (perfect separation)

### P5: Cross-Approach Concordance -- PASS (diagnostic)
- 46 common folios
- Agreement: 45.7%
- Cohen's kappa: 0.163

### N1: Theoretical Negative Control -- FAIL
- Approach A worst: distillation (mean cosine -0.027)
- Approach B worst: dissolution (mean EMD 1.000)
- Theoretical NOT worst on either approach

### N2: Permutation Control -- FAIL
- Real directional score: 0.056
- Permutation 95th percentile: 0.223
- Fraction exceeding: 0.435 (43.5% of random permutations beat real)

### Verdict Tree Path
```
S1 passes -> Stage 1 passes -> N1 FAILS -> SPECIFICITY_FAILURE
```

## Key Findings

1. **Procedure-family prototype assignment does not project onto V folio structure (C1749).** The z-scored cosine bridge maps PL families onto the already-known Voynich REGIME/section manifold, not onto family-specific residual structure. Distillation captures REGIME_1/Bio (thermal baseline), sublimation captures REGIME_3/Herbal (high monitoring), dissolution captures mixed high-REGIME folios. The assignments carry zero family-specific information beyond axis position (N2: 43.5% of permutations beat real).

2. **Sublimation vs distillation monitoring contrast is real (C1750).** P4 shows perfect rank separation (p=6.9e-10) between sublimation-assigned and distillation-assigned folios on h_ratio. This strengthens C1744 at family resolution — PL's monitoring-intensive family corresponds to a real V axis contrast. This is the strongest surviving signal and suggests family-level contrasts exist along the monitoring dimension.

3. **Fixation is not a valid A2/recirculation proxy (C1751).** Only 6/82 folios assigned to fixation, 5/6 in Bio, 0/6 A2, safety direction inverted. The high-termination/high-chain fixation prototype, when projected through the 3D bridge, selects for Bio/REGIME_1/A1 folios with strong preventive safety — the opposite of the predicted A2/Herbal/transformative target.

4. **The PL dimensions that discriminate families have no folio-level V analog.** Stage 1 shows PL families separate on termination_rate and chain_rate (the only Bonferroni survivors), but the V bridge uses h_ratio, safety_balance, k_ratio — none of which correspond to termination or chaining. PL termination and chaining are recipe-level structural properties; V closure and chaining are line-local (C1471).

5. **Axis-level alignment is genuine; categorical alignment is not.** P1 (within-A3 k_ratio specificity, p=0.0006) and P4 (h_ratio separation, p=6.9e-10) show the operational dimensions are shared. But the V system imposes its own organizational structure (sections, REGIMEs, apparatus profiles) rather than preserving PL's family taxonomy.

## Interpretive Note

Phase 604 failed its pre-registered specificity controls and therefore does not support a general procedure-family assignment model in its current form. However, the result is not a uniform null. Internal pseudo-Lull families were separable (Stage 1), and two theoretically targeted contrasts succeeded: distillation-assigned A3 folios showed elevated thermal signature (P1), and sublimation-assigned folios showed dramatically elevated monitoring signature (P4). The main failure was the fixation-based bold target, which did not recover the predicted A2/Herbal alignment and likely reflects either an inadequate recirculation proxy or excessive compression of pseudo-Lull family structure into coarse Voynich section/REGIME axes. The phase therefore rejects the current prototype-assignment bridge, not the broader possibility of pseudo-Lullian procedure-family contrasts.

## What This Phase Does NOT Do

- No chapter-to-folio mapping
- No token-to-word mapping
- No cipher letter decoding
- No cross-section rank concordance (C1739)
- No semantic content mapping
- No apparatus-name matching
