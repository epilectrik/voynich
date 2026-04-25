# Paragraph Heat-Mode Progression

**Phase:** 645
**Status:** COMPLETE — SCOPE_LIMITED_SUPPORT (no constraint registered; effect real on heat-phase-distinct recipes only)
**Type:** Recipe-decoded prediction test for heat-mode encoding
**Started:** 2026-04-25
**Completed:** 2026-04-25
**Outcome:** Mixed result. Best metric `qok_class_frac` mean rho +0.484 across 7 matches, 5/7 positive direction, 1/7 strict significance. Clear positive signal on f84r (rho=+0.983, p=0.001) and f82r (rho=+1.000, p=0.082). Null on uniform-heat recipes (f108v sublimation, f79v sustained balneum). Heat-progression encoding holds where recipes have distinct heat-phase differences; absent where recipes are heat-uniform.

## Purpose

Test whether paragraph-level heat metrics (e-depth, qokeedy/qokedy ratio, qok-class density) on confirmed-match folios track the matched recipe's expected fire-degree progression. This converts heat-mode investigation from a corpus-correlation problem (which Phase 641-642 already showed is the wrong shape of test) into a **recipe-decoded prediction problem**, building on Phase 643's C1959 finding that paragraph layout-order tracks recipe-phase order.

Per crazy-expert's specific recommendation in the Phase 643 follow-up consultation:
> *"Test heat-mode on matched folios using paragraph layout-order as the predictor. Specifically: if Paragraph N at layout-position p encodes phase P, and phase P has expected fire-degree F (from the matched recipe), does Paragraph N's e-depth profile match F? This converts heat-mode from a corpus-correlation problem to a recipe-decoded prediction problem. Much higher resolution."*

## Existing constraint scaffold

- **C1225** — e-depth suffix parametricity
- **C1226** — ke/ek process-context conditioning
- **C1457-C1462** — e→y safe pathway / hazard-recovery architecture
- **C1735** — Brunschwig thermal intensity alignment
- **C1740, C1750, C1752** — Brunschwig fire-degree alignment in Stars section
- **C1872, C1873** — k/e channel REGIME/Stars calibration
- **C1957** — suffix-boundary fix (e_depth measurement match: 16.7% → 98.6%)
- **C1206** — paragraph kernel gradient (within-paragraph structure)
- **C1958** — ot = transfer/drip rate (thermal/transfer coupling)

## Methodology

### Heat metrics (per paragraph)

- **mean_e_depth**: average e_depth across paragraph tokens (gentle-heat indicator)
- **qokeedy_frac**: qokeedy count / total tokens (balneum/gentle signature)
- **qokedy_frac**: qokedy count / total tokens (moderate hot signature)
- **qok_class_frac**: qok-class total / paragraph length (overall heat density)
- **gentle_ratio**: tokens with e_depth ≥ 2 / total (high-gentle fraction)
- **balneum_score**: qokeedy_frac − qokedy_frac (positive = balneum-dominant)

### Recipe heat-degree predictions (per paragraph)

For each of the 7 confirmed matches, recipe content is parsed paragraph-by-paragraph for explicit heat-mode language and expected fire-degree:
- `1` = low/no heat (setup, mixing, observation, closure)
- `2` = moderate gentle heat (balneum, slow decoction, gentle fermentation)
- `3` = vigorous heat (open fire, calcination, distillation pivot)

Recipe contexts per match documented in `predictions.md` (committed before metric computation).

### Test

For each folio: Spearman rho between layout-position and recipe-predicted heat-degree. AND between layout-position and measured heat metrics. AND between predicted-heat and measured-heat directly.

If predicted-heat-vs-measured-heat correlates positively across folios at significance, heat-mode is **recipe-decoded** at the paragraph level — a major upgrade from Phase 641's failed correlation tests.

## Scripts (planned)

| Script | Purpose |
|--------|---------|
| `predictions.py` | Lock recipe-derived heat-degree predictions per paragraph |
| `compute_heat_metrics.py` | Per-paragraph atom-derived heat metrics for 7 match folios |
| `test_heat_progression.py` | Correlation test of predicted vs measured |

## Falsifiable predictions

1. **mean e-depth correlates with predicted fire-degree** at folio level (Spearman rho > 0)
2. **Aggregate effect** across 7 folios: mean rho > 0.3 (moderate effect)
3. **Specific folios** with strong heat-pattern recipes (f75r aqua vitae, f82r 3-day cendres, f78r mercury congelation) should show stronger correlations than recipes with uniform heat throughout (f108v sublimation = sustained slow)

If predictions hold → register new constraint. If null → reaffirm Phase 641's finding that aggregate correlation tests don't surface heat-mode encoding.

## Caveats

- Recipe heat-degree assignments are interpretive (parallel to phase-ordinal assignments in Phase 643)
- Predictions must be locked BEFORE metrics are computed (per pre-registration discipline)
- Small N per folio (3-18 paragraphs) limits per-folio statistical power; aggregate test is the primary inference
