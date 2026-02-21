# C1155: Paragraph Kernel Dynamics Do Not Mediate the AXM Residual

**Tier:** 2
**Scope:** B, paragraph, kernel, AXM residual
**Phase:** PARAGRAPH_KERNEL_DYNAMICS (Phase 412)
**Depends on:** C965, C893, C944, C1022, C1035, C1153

## Statement

Within-folio paragraph kernel diversity does not mediate the C1035 AXM residual (57% irreducible). Three paragraph-level predictors — kernel heterogeneity (SD of per-paragraph k/h/e fractions), trajectory slope diversity (variance of per-paragraph h_frac slopes), and paragraph type entropy (Shannon entropy of HIGH_K/BALANCED mix) — all produce dR² < 0.002 when added to the C1035 baseline (R²=0.564), with negative LOO contributions (overfitting). Within-section correlations are effectively zero (|rho| < 0.16, all p > 0.85). Bivariate correlations with AXM self-transition are also null (T1 rho=-0.187, T2 rho=0.122, T3 rho=0.138, all p > 0.89).

## Evidence

**C1035 baseline replication:** R²=0.564, LOO R²=0.433 (n=72). Exact match.

| Predictor | dR² | F-stat | p | LOO dR² |
|-----------|-----|--------|---|---------|
| Kernel heterogeneity | 0.0012 | 0.16 | 0.690 | -0.021 |
| Trajectory slope variance | 0.0014 | 0.19 | 0.665 | -0.016 |
| Type entropy | 0.0002 | 0.03 | 0.865 | -0.018 |

**Within-section validation:** BIO rho=-0.153 (n=16), HERBAL_B rho=-0.119 (n=8), STARS_RECIPE rho=-0.042 (n=23). No section shows signal.

**Data:** 567 paragraphs across 72 valid folios, 53 folios qualifying for heterogeneity analysis (≥3 paragraphs with ≥15 tokens), 243 qualifying paragraphs for trajectory analysis (≥4 lines).

## Structural Implication

The C1035 residual is confirmed closed against paragraph-level kernel dynamics. The ~40% generative design freedom (C1153) is genuinely program-specific — not a hidden paragraph-level mediator. Paragraph kernel diversity exists (C965, C893, C944) but operates orthogonally to the AXM macro-state dynamics that define the residual. This is consistent with C1022 (6-state macro-automaton does not resolve paragraphs).
