# C1363: Line Gradient Steepness Is Universal, Not Program-Specific

**Tier:** 2
**Scope:** B, line, folio, gradient
**Phase:** GRADIENT_STEEPNESS (Phase 475)
**Depends on:** C1359, C1168

## Statement

The within-line stability→escape gradient (C1359: AXM self 0.737→0.549) does not vary meaningfully across folios. Per-folio gradient slope variance does not exceed permutation null (p=0.105, 1000 permutations shuffling token positions within lines). Gradient slope adds negligible explanatory power beyond C1168's dual boundary architecture (delta-R-squared=0.010). REGIME does not predict gradient steepness (KW p=0.22), nor does section (KW p=0.13). The gradient is a universal property of the B grammar's class frequency structure, not a tunable program parameter.

## Evidence

| Test | Result |
|------|--------|
| T1 (gate): Slope variance vs noise | p=0.105 — GATE CLOSED |
| T2 (gate): Delta-R-squared beyond C1168 | 0.010 — GATE CLOSED |
| T3: REGIME predicts slope | KW p=0.22, R1-R3 MW p=0.67 — FAIL |
| T4: Section predicts slope | KW p=0.13 — FAIL |
| T5: Shape taxonomy | Silhouette=0.50 at k=2 but only n=10 — unreliable |

**Per-folio statistics (53 folios with >=100 classified tokens):**
- Mean slope: -0.027
- Slope range: [-0.114, +0.127]
- Slope-entry divergence correlation: rho=-0.055, p=0.63
- Slope-exit divergence correlation: rho=0.131, p=0.29

**Pre-registered prediction (R1 gentler than R3):** Direction correct (R1=-0.022, R3=-0.032) but non-significant (MW p=0.67).

## Structural Implication

The line gradient is not a design parameter — programs cannot tune how steeply their lines transition from stability to escape. This is consistent with C821 (line syntax REGIME-invariant at role level) and extends it: not only are role proportions invariant, but the within-line positional deployment of classes is also invariant. The gradient is an emergent property of the shared 49-class grammar operating over universal class frequency distributions. Programs differ in WHAT they execute (REGIME, vocabulary, hazard density) but not in HOW their lines unfold positionally.

**Results:** `phases/GRADIENT_STEEPNESS/results/gradient_steepness.json`
