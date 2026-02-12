# C1003: TOKEN is Pairwise Composite — No Three-Way Synergy

**Tier:** 2 | **Scope:** B | **Phase:** PREFIX_MIDDLE_SUFFIX_SYNERGY | **Date:** 2026-02-12

## Statement

The full TOKEN (PREFIX+MIDDLE+SUFFIX) carries no genuine three-way synergistic information. Co-Information is non-significant on all 4 targets (ROLE, REGIME, POSITION, SECTION). R² increment from two-way to three-way interaction is 0.0001 (zero). However, TOKEN is an **atomic lookup unit**: full-token lookup beats naive Bayes independence by +0.097 bits/token (t=8.64, p=0.001) for next-class prediction. This means TOKEN captures pairwise interactions (PREFIX×MIDDLE, PREFIX×SUFFIX, MIDDLE×SUFFIX) more efficiently than component independence, but adds no emergent three-way structure. Synergy is uniform across suffix strata (not concentrated in EN as hypothesized), and the strongest Co-Information is REGIME at -0.011 bits (below the 0.02-bit significance threshold).

## Evidence

### T1: Three-Way Co-Information (NO SYNERGY)
- **ROLE**: Co-I = +0.110 bits (REDUNDANCY), p=1.000
- **REGIME**: Co-I = -0.011 bits (synergy but below 0.02 threshold), p=0.000
- **POSITION**: Co-I = -0.005 bits (noise level), p=0.496
- **SECTION**: Co-I = 0.0 bits (null — Currier B is single section)
- 0/4 targets show significant three-way synergy
- Permutation null (1000 shuffles) confirms REGIME synergy is real but small
- TOKEN information is well-described by pairwise component interactions

### T2: Three-Way Interaction R² Increment (NO INTERACTION)
- R² main effects only: 0.078
- R² with two-way interactions: 0.104
- R² with three-way interaction: 0.104
- **R² increment: 0.00006** (effectively zero)
- F-test: F=0.004, p=1.000 (not significant)
- 232 PCS combo features tested (MIN_COMBO=10 for stability)

### T3: Token Atomicity — Full Token vs Naive Bayes (CONFIRMED)
- 5-fold cross-validated log-likelihood:
  - Full-token lookup: mean LL = -4.907 bits
  - Naive Bayes: mean LL = -5.003 bits
  - **Improvement: +0.097 bits/token**
- Paired t-test: t=8.64, p=0.001
- TOKEN lookup is consistently better than P(class|PREFIX)×P(class|MIDDLE)×P(class|SUFFIX)
- The improvement comes from pairwise correlations (e.g., certain PREFIX-SUFFIX pairs predict specific classes), not from three-way structure

### T4: Synergy by Suffix Stratum (UNIFORM)
- EN (suffix-rich, n=7211): Co-I position=-0.0001, regime=-0.007
- AX (moderate, n=4140): Co-I position=-0.022, regime=-0.012
- DEPLETED (FL/FQ/CC, n=4703): Co-I position=+0.001, regime=+0.002
- **AX shows most synergy, not EN** — contradicts C588 stratum hypothesis
- Synergy is not concentrated in suffix-rich tokens

## Implications

- **Confirms C417**: HT three-way synergy = 0.0 bits (now extended to full PREFIX×MIDDLE×SUFFIX)
- **Extends C1001**: PREFIX-MIDDLE synergy for REGIME = -0.009 bits (C1001 T1) — adding SUFFIX does not increase synergy
- **Extends C661/C662**: PREFIX transforms behavior and reclassifies, but through pairwise interaction with MIDDLE, not three-way interaction
- **New**: TOKEN is an atomic lookup unit for sequential prediction (+0.097 bits/token over independence), but this atomicity arises from pairwise correlations, not emergent three-way structure
- **Design implication**: Any model of Currier B needs only pairwise component interactions — P(class|PREFIX,MIDDLE) + P(class|MIDDLE,SUFFIX) + P(class|PREFIX,SUFFIX) captures all available information

## Provenance

- `phases/PREFIX_MIDDLE_SUFFIX_SYNERGY/results/t1_three_way_coinformation.json`
- `phases/PREFIX_MIDDLE_SUFFIX_SYNERGY/results/t2_interaction_r2.json`
- `phases/PREFIX_MIDDLE_SUFFIX_SYNERGY/results/t3_token_atomicity.json`
- `phases/PREFIX_MIDDLE_SUFFIX_SYNERGY/results/t4_synergy_by_stratum.json`
