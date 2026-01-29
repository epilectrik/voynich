# C607: Line-Level Escape Prediction

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase LINE_LEVEL_LANE_VALIDATION
**Scope:** B_INTERNAL | EN | ESCAPE

## Statement

Line-level EN_CHSH proportion predicts line-level escape density at rho=-0.707 (n=2240, p<10^-6) — more than twice the folio-level effect (C412: rho=-0.304). Line-level lane balance predicts escape at rho=-0.363 (n=409, p<10^-6). The EN-escape relationship is a structural property of individual lines, not an artifact of folio-level aggregation.

## Evidence

### EN_CHSH -> Escape (line-level)
- Spearman rho=-0.707, p<10^-6, n=2240 lines (>=3 tokens with EN)
- Folio-level benchmark (C412): rho=-0.304
- **Line-level effect is 2.3x stronger than folio-level**

### Lane balance -> Escape (line-level)
- Spearman rho=-0.363, p<10^-6, n=409 lines (with both CC and EN)
- Folio-level benchmark (C605): rho=-0.506
- Line-level weaker (expected: lane balance requires CC which not all lines have)

### Line-level CC composition -> EN composition
- Spearman rho=0.110, p=0.003, n=743 lines
- Folio-level benchmark (C603): rho=0.345
- Significant but 3x weaker — composition smooths at folio level

## Interpretation

The amplification of EN->escape at line level (rho=-0.707 vs -0.304) demonstrates that escape density is primarily a line-level phenomenon. Folio aggregation dilutes the signal by mixing lines with different EN compositions. The grammar assigns escape potential per-line, not per-folio.

## Related

- C412 (sister-escape anticorrelation - folio level)
- C605 (two-lane folio-level validation)
- C603 (CC folio-level subfamily prediction)
- C606 (CC->EN line-level routing)
