# C607: Line-Level QO-Density Prediction (Revised)

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase LINE_LEVEL_LANE_VALIDATION
**Scope:** B_INTERNAL | EN | LANE_BALANCE

> **TERMINOLOGY NOTE (2026-01-31):** "Escape density" replaced with "qo-density"
> per C397/C398 revision. QO is the energy lane (k-rich) operating hazard-distant.
> The anticorrelation with CHSH reflects lane balance, not escape behavior.

## Statement

Line-level EN_CHSH proportion predicts line-level qo-density at rho=-0.707 (n=2240, p<10^-6) — more than twice the folio-level effect (C412: rho=-0.304). Line-level lane balance predicts qo-density at rho=-0.363 (n=409, p<10^-6). The EN-QO relationship is a structural property of individual lines, not an artifact of folio-level aggregation.

## Evidence

### EN_CHSH -> QO-density (line-level)
- Spearman rho=-0.707, p<10^-6, n=2240 lines (>=3 tokens with EN)
- Folio-level benchmark (C412): rho=-0.304
- **Line-level effect is 2.3x stronger than folio-level**

### Lane balance -> QO-density (line-level)
- Spearman rho=-0.363, p<10^-6, n=409 lines (with both CC and EN)
- Folio-level benchmark (C605): rho=-0.506
- Line-level weaker (expected: lane balance requires CC which not all lines have)

### Line-level CC composition -> EN composition
- Spearman rho=0.110, p=0.003, n=743 lines
- Folio-level benchmark (C603): rho=0.345
- Significant but 3x weaker — composition smooths at folio level

## Interpretation (Revised 2026-01-31)

The amplification of EN_CHSH -> QO-density at line level (rho=-0.707 vs -0.304) demonstrates that QO-density is primarily a line-level phenomenon. This reflects **lane balance**: lines with high CHSH activity (stabilization) have low QO activity (energy), and vice versa. The grammar assigns lane balance per-line, not per-folio.

Given the lane model (C643, C645):
- CHSH (e-rich) and QO (k-rich) are complementary lanes
- Lines emphasize one or the other, creating the strong anticorrelation

## Related

- C412 (sister-QO anticorrelation - folio level, REVISED)
- C605 (two-lane folio-level validation)
- C603 (CC folio-level subfamily prediction)
- C606 (CC->EN line-level routing)
- C643 (QO-CHSH rapid alternation)
- C645 (CHSH post-hazard dominance)
