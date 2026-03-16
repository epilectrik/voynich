# Phase 596: REDISTILLATION_I_HYPOTHESIS

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1730, C1731

## Objective

Test whether the i-extension system (single-i vs double-ii) encodes redistillation familiarity in a distillation process (double-ii = bounded redistillation of familiar material, single-i = open first-pass iteration of unfamiliar material), or is fully explained by the existing safety-routing mechanism (C1480-C1482: i selects a-HEAD, transforms terminal profile, eliminates hazard).

## Method

- **Data:** 23,096 Currier B tokens, 11,174 Currier A tokens, 585 paragraphs
- **i-extension classification:** max consecutive i-run in MIDDLE (0=no-i, 1=single-i, 2+=double-ii)
- **T1:** Within-paragraph positional distribution of ii-tokens (quintile gradient + HEAD-atom control)
- **T2:** Paragraph type discrimination (overdispersion of ii-fraction vs beta-binomial null)
- **T3:** Paragraph ordinal distribution (C1399 negative control)
- **T4:** REGIME enrichment (ii/i ratio by folio REGIME + hazard confound control)
- **T5:** Successor entropy (Shannon entropy by predecessor i-class + terminal-atom decomposition)
- **T6:** Kernel co-occurrence (HEAD-fraction correlations with ii-fraction, corpus and within-folio)
- **T7:** Context hazard discrimination (hazard rate of non-ii tokens on ii-lines vs no-ii lines)
- **T8:** Cross-system i-extension (Currier A vs B distribution)

## Key Results

| Test | Metric | Value | Significance |
|------|--------|-------|-------------|
| T1 | ii-fraction positional rho | -0.30 | perm_p=0.673 (NOT significant) |
| T1 | a-HEAD control rho | -0.30 | Same as unconditioned |
| T2 | Overdispersion ratio | 1.31 | Below 2.0 threshold (no real types) |
| T3 | Stouffer z (ordinal) | 0.96 | perm_p=0.327 (C1399 CONFIRMED) |
| T4 | Chi2 (REGIME x i-ext) | 51.43 | p<0.001 (significant) |
| T4 | REGIME_4 ii-ratio | 0.635 | Highest (R2=0.631, R3=0.575, R1=0.468) |
| T4 | Hazard confound corr | 0.40 | Moderate, not confounded |
| T5 | single_i - double_ii entropy | -0.055 bits | perm_p=0.585 (NOT significant) |
| T6 | a-HEAD rho (within-folio) | 0.345 | Confirms C1480 (i selects a-HEAD) |
| T6 | k-HEAD rho (within-folio) | -0.116 | Confirms C1205 (i orthogonal to k/e) |
| T7 | Non-ii hazard on ii-lines | 20.6% | p<0.001 |
| T7 | Non-ii hazard on no-ii lines | 16.5% | Baseline |
| T7 | Hazard difference | +4.1% | ii deployed in high-hazard contexts |
| T8 | Currier A ii-ratio | 0.730 | Chi2=149.96, p<0.001 |
| T8 | Currier B ii-ratio | 0.540 | A > B |

## Interpretation

**Verdict: MECHANISM_CONFIRMED_PURPOSE_UNDERDETERMINED.** The safety-routing mechanism (C1480-C1482) is confirmed as the mechanism by which ii operates. However, the redistillation hypothesis (ii encodes process-level familiarity) can neither be confirmed nor rejected by these tests, because the critical discrimination test (T7) and cross-system test (T8) were built on premises that don't distinguish the two interpretations.

**T7 confirms mechanism, cannot test purpose.** Non-ii tokens on ii-lines have higher hazard (20.6%) than on no-ii lines (16.5%), p<0.001. This confirms ii is deployed in high-hazard contexts. However, redistillation IS inherently hazardous — each pass risks already-valuable product and deepens sunk cost. Both safety-routing and redistillation predict ii appears in high-hazard contexts, so T7 cannot discriminate between them. Safety-routing is the MECHANISM (how ii works); redistillation would be the PURPOSE (why the grammar needs a "repeat safely" device). These are complementary, not competing.

**T8 is consistent with both interpretations.** Currier A ii-ratio (0.730) > B (0.540), chi2=150, p<0.001. Initially interpreted as anti-redistillation, but A is the specification registry (C240) — it SPECIFIES process requirements including redistillation. A having more ii is expected if A records which products require redistillation. T8 establishes the A>B cross-system fact but cannot discriminate purpose.

**All paragraph-level tests are null.** T1 (no positional gradient, perm_p=0.673), T2 (no paragraph type separation, overdispersion 1.31), T3 (C1399 confirmed, perm_p=0.327). The i-extension does not operate at paragraph level. This is a real finding: whatever ii encodes, it is not organized by paragraph position or paragraph type.

**T4 reveals a refinement-intensity gradient.** REGIME x i-extension is significant (chi2=51.43, p<0.001). The ii-ratio ordering is: REGIME_4 (precision-constrained, 0.635) > REGIME_2 (output-intensive, 0.631) > REGIME_3 (transient-throughput, 0.575) > REGIME_1 (thermal-control-intensive, 0.468). This is a refinement-intensity gradient: REGIMEs requiring more precision or sustained output use more double-ii. The moderate hazard correlation (r=0.40) shows ii-deployment partially but not fully tracks REGIME hazard.

**T5 shows no predictability advantage.** Double-ii successors have slightly higher entropy than single-i (diff=-0.055 bits, not significant). No evidence that ii-contexts are more predictable at the token-successor level.

**T6 confirms known structural relationships.** ii-fraction correlates with a-HEAD fraction (within-folio rho=0.345) and anti-correlates with k-HEAD and e-HEAD (rho=-0.116, -0.090). Replicates C1480 and C1205.

**Within-B section variation replicated.** HERBAL has highest ii-rate (0.676), section B lowest (0.467), matching C1204.

## Constraints

### C1730: ii-deployment follows a REGIME refinement-intensity gradient
**Tier:** 2 (ESTABLISHED) | **Scope:** B

The double-ii/single-i ratio varies significantly across REGIMEs (chi2=51.43, p<0.001, Cramér's V=0.134): REGIME_4 (precision-constrained, 0.635) > REGIME_2 (output-intensive, 0.631) > REGIME_3 (transient-throughput, 0.575) > REGIME_1 (thermal-control-intensive, 0.468). This ordering follows a refinement-intensity gradient — REGIMEs demanding more precision or sustained output deploy more double-ii. The hazard correlation is moderate (r=0.40), indicating ii-deployment partially tracks REGIME hazard but is not fully explained by it. No paragraph-level i-distribution signal exists (T1 positional rho p=0.673, T2 overdispersion=1.31, T3 ordinal p=0.327, confirming C1399). Successor entropy shows no ii predictability advantage (T5 p=0.585). The safety-routing mechanism (C1480-C1482) explains HOW ii operates; the REGIME gradient characterizes WHERE the grammar deploys it most heavily. Context hazard test (T7) confirms ii appears in high-hazard contexts (non-ii hazard 20.6% on ii-lines vs 16.5% on no-ii lines, p<0.001), consistent with the safety mechanism.

### C1731: Currier A has higher double-ii concentration than B
**Tier:** 2 (ESTABLISHED) | **Scope:** A, B, cross-system

Currier A ii-ratio = 0.730 (among i-containing tokens) vs Currier B ii-ratio = 0.540 (chi2=149.96, p<0.001). Within B, HERBAL has highest ii-rate (0.676) and section B lowest (0.467), replicating C1204. REGIME_4 (precision-constrained) and REGIME_2 (output-intensive) have the highest B ii-ratios (0.635, 0.631), while REGIME_1 (thermal-control-intensive) has the lowest (0.468). The A>B pattern is consistent with A being a specification registry (C240) that records process requirements — including bounded-iteration specifications — while B's execution grammar uses more diverse iteration patterns including single-i operations. This cross-system difference does not by itself distinguish safety-routing from redistillation interpretations, as both predict A would have higher ii concentration (A specifies safety requirements / A specifies redistillation requirements).

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/redistillation_i_test.py` | ~50 sec |

## Results

| File | Content |
|------|---------|
| `results/redistillation_i_results.json` | Full results: T1-T8, per-REGIME detail, cross-system comparison, context hazard test, verdict |
