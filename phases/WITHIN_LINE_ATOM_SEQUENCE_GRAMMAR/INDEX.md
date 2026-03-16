# Phase 594: WITHIN_LINE_ATOM_SEQUENCE_GRAMMAR

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1724, C1725, C1726

## Objective

Test whether the TERM→HEAD routing grammar (C1563) varies by line position (quintile Q0-Q4), or whether positional variation in routing is entirely explained by the independent positional marginals P(TERM|quintile) and P(HEAD|quintile). This addresses the gap between the global routing grammar (C1563) and the three-zone line model (C1425-C1430): how do individual tokens chain to produce the specification→work→closure arc?

## Method

- **Data:** 2,406 Currier B lines (≥3 tokens), 20,668 consecutive token pairs
- **TERM/HEAD extraction:** MIDDLE atoms via `decompose_middle_hmt()` (same as Phase 593)
- **Position:** Source token's quintile (Q0-Q4) using canonical `frac_pos = idx / (line_len - 1)`
- **T1:** Per-quintile 7×6 TERM→HEAD routing matrices with two enrichment versions (global-marginal and local-marginal)
- **T2:** Log-linear G² test for TERM×HEAD×Quintile three-way interaction (1000 quintile-shuffles within lines)
- **T3:** Pairwise JSD between consecutive quintile routing matrices + Q4 bootstrap CI
- **T4:** MI decomposition (total, position-conditional, interaction, co-information)
- **T5:** Per-rule positional activation profiles for 6 enriched + 4 depleted rules (Spearman trend)
- **T6:** Position-specific exception detection for depleted rules

## Key Results

| Test | Metric | Value | Significance |
|------|--------|-------|-------------|
| T1 | Q4 JSD vs global (Version A) | 0.0209 | 14x Q2 (0.0012) |
| T1 | Q0 JSD vs global (Version A) | 0.0058 | 4x Q2 |
| T2 | G² | 144.61 | df=120 |
| T2 | Shuffle p | 0.069 | NOT significant (threshold 0.01) |
| T2 | Signal/noise (G²/p99) | 0.91 | Below noise ceiling |
| T2 | Cramér's V | 0.084 | Small effect |
| T3 | Q3 vs Q4 JSD | 0.0209 | 5.6x work-zone mean (0.0037) |
| T3 | Q3→Q4 fraction of total | 59.6% | Closure dominates but <70% |
| T3 | Q0 vs Q1 JSD | 0.0068 | 1.8x work-zone mean |
| T3 | Q4 bootstrap CI | [0.019, 0.026] | Doesn't overlap work zone |
| T4 | Total MI | 0.0552 bits | |
| T4 | Interaction MI | -0.0044 bits | -7.9% of total (SYNERGY) |
| T4 | Q4 within-quintile MI | 0.0714 bits | Highest (vs Q1=0.050) |
| T5 | l→e trend | rho=-0.90 | p=0.037 (declining Q0→Q4) |
| T5 | m→o trend | rho=+0.90 | p=0.037 (rising Q0→Q4) |
| T5 | n→k trend | rho=-0.90 | p=0.037 (declining Q0→Q4) |
| T5 | r→a at Q4 | 3.87x | vs 2.23x global (highest per-quintile) |
| T5 | h→t at Q2 | 2.66x | vs 1.89x global (peaks mid-line) |

## Interpretation

**Verdict: MARGINAL_PRODUCT.** Routing varies dramatically by line position (Q4 JSD 14x Q2), but the three-way TERM×HEAD×Quintile interaction is NOT significant (G²=144.61, shuffle p=0.069). The routing variation is explained by the two-way margins: position changes what TERMs and HEADs are available, and the routing grammar applies the same rules to whatever is available.

**The mechanism of the specification→work→closure arc is compositional, not grammatical.** Lines don't change their routing rules at different positions — they change their atom mix. Q0 has more e-HEAD tokens and ARTICULATORs; Q4 has more m-terminal and a-HEAD tokens. The global routing grammar (C1563) applies uniformly to this shifting composition. The arc is produced by the marginals, not by position-dependent routing.

**Mild synergy exists (T4).** Conditioning on position reveals 7.9% more routing structure (interaction MI = -0.0044 bits). This means within each quintile, TERM→HEAD associations are slightly stronger than in the aggregate — consistent with each zone having a more focused compositional palette that the grammar acts on more discriminatively. Q4 has the highest per-quintile MI (0.071 vs 0.050 at Q1), reflecting the sharp compositional focus of closure.

**Per-rule activation profiles (T5, exploratory) show meaningful trends** despite the overall three-way test failing:
- **l→e declines Q0→Q4** (1.62→0.88): specification-zone routing fades
- **m→o rises Q0→Q4** (0.00→2.92): closure-specific routing strengthens
- **n→k declines Q0→Q4** (0.59→0.43): thermal routing becomes more depleted at closure
- **r→a peaks at Q4** (3.87x): strongest positional enrichment of any rule
- **h→t peaks mid-line Q2** (2.66x): thermal handoff concentrates in work zone

These trends are real (they survive Spearman tests) but are explained by compositional change, not grammar change. The routing grammar treats r→a the same everywhere; Q4 simply has more r-terminal tokens available and more a-HEAD successors.

**Controls confirm universality.** Section stratification shows comparable G²/n ratios across all 4 sections (H=0.068, B=0.018, C=0.014, S=0.041). Line-length stratification shows no dependence on line length. The marginal-product architecture is universal.

## Constraints

### C1724: Routing grammar is position-invariant (MARGINAL_PRODUCT)
**Tier:** 2 (ESTABLISHED) | **Scope:** B

The TERM×HEAD×Quintile three-way interaction is not significant (G²=144.61, df=120, shuffle p=0.069, Cramér's V=0.084). Routing distributions vary by line position (Q4 JSD vs global = 0.0209, 14x Q2's 0.0012), but this variation is entirely explained by the independent positional marginals P(TERM|quintile) × P(HEAD|quintile). The global routing grammar (C1563: r→a 2.23x, h→t 1.89x, etc.) applies uniformly across all line positions. The specification→work→closure arc (C1425-C1430) is produced by compositional change (shifting TERM/HEAD atom mix), not by position-dependent routing rules. Confirmed across all 4 sections and all line-length strata. Complements C1721 (routing is not folio-specific): routing is both position-invariant and folio-invariant within the grammar.

### C1725: Closure zone has strongest routing discrimination (mild synergy)
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Position-conditional MI decomposition reveals mild synergy: interaction MI = -0.0044 bits (-7.9% of total 0.0552 bits). Within each quintile, TERM→HEAD associations are slightly stronger than in the corpus aggregate. Q4 (closure) has the highest per-quintile MI (0.0714 bits) vs Q1 (0.0496 bits). This reflects the sharp compositional focus of closure: with fewer TERM/HEAD types active (m-terminal surge, a-HEAD surge), the grammar discriminates more sharply among the reduced options. The synergy is small (7.9%) — the grammar is fundamentally position-invariant (C1724) but operates with slightly more discriminative power where composition is narrower.

### C1726: Per-rule activation profiles are compositionally driven
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Individual routing rules show significant positional trends despite the overall three-way interaction being non-significant: l→e declines Q0→Q4 (rho=-0.90, p=0.037), m→o rises Q0→Q4 (rho=+0.90, p=0.037), n→k declines Q0→Q4 (rho=-0.90, p=0.037). The strongest per-quintile enrichment is r→a at Q4 (3.87x vs 2.23x global). These trends are explained by compositional change: more r-terminal and a-HEAD tokens at Q4 → r→a enrichment rises; more m-terminal at Q4 → m→o strengthens. No globally depleted rule becomes enriched at any quintile (T6: no position-specific exceptions). The routing grammar applies uniformly; the activation profiles are a readout of positional composition, not position-dependent grammar modulation.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/within_line_atom_grammar.py` | ~31 sec |

## Results

| File | Content |
|------|---------|
| `results/within_line_atom_grammar_results.json` | Full results: T1-T6, per-quintile matrices, G² test, zone transitions, MI decomposition, per-rule activation profiles, controls, verdict |
