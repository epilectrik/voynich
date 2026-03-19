# Phase 603: Pre-Registration of Predictions

**Status:** FROZEN — do not modify after SHA-256 hash is recorded.

## S1: Calibration Anchor

Stars ey_rate: R1 > R3, Mann-Whitney p < 0.05.
If FAIL: CALIBRATION_FAILURE, stop all tests.

## P1: Monitor->Action Chain Outcome Distribution

(a) Stabilization ratio: (continue + stop + correct) / (proceed + adjust) >= 2.0
(b) Abort fraction: abort / total < 5%
(c) DIAGNOSTIC: Stabilization ratio higher in operational parts (Practica+Mercuriorum+Furnis) than Theorica

Pass: (a) AND (b)

## P2: Recovery Doctrine <-> Safety-Style Split

(a) Pseudo-Lull recovery ratio (156/25 = 6.24) > 1.0 AND Voynich mean ey_rate / mean ii_rate > 1.0 (both preventive-dominant)
(b) DIAGNOSTIC: Part with highest correction density maps to section with highest safety_balance

Pass: (a)

## P3: Thresholded Termination <-> Closure Authenticity

(a) Pseudo-Lull threshold/count ratio >= 3x Brunschwig threshold/count ratio
(b) DIAGNOSTIC: Voynich AXM fraction > 50% in all B sections (MONOSTATE compatibility)

Pass: (a)

## P4: Recovery Asymmetry (Clamped Hazard / Free Recovery)

(a) Pseudo-Lull failure_modes / correction_strategies > 2.0
(b) Voynich hazard_density CV < 0.15 AND recovery_ops CV > 0.50 (replicating C458)
(c) DIAGNOSTIC: Per-part correction density CV > 0.30

Pass: (a) AND (b)

## P5: Register Architecture (Same Inventory, Different Weighting)

(a) ALL pairwise JSD > 0.05 AND ALL pairs share >= 60% of families
(b) DIAGNOSTIC: Mean pairwise JSD in [0.05, 0.50]

Pass: (a)

## N1: Negative Control

Spearman rank correlation between pseudo-Lull aggregated operation-family frequencies and Voynich aggregated instruction-class frequencies: p > 0.10 (NOT significant).

Pass: p > 0.10

## D1: Diagnostic

Pseudo-Lull formalized/discretionary ratio (61/35 = 1.74) vs Voynich encodable/non-encodable ratio (49/13 = 3.77). Report only, no pass/fail.

## Verdict Tree

```
S1 fails -> CALIBRATION_FAILURE
S1 passes:
  N1 fails (p < 0.05) -> LEVEL_CONFUSION
  N1 passes (p > 0.10):
    >= 4 of P1-P5 pass -> MIDPROCESS_CONTROL_ALIGNMENT_CONFIRMED
    3 of P1-P5 pass    -> PARTIAL_MIDPROCESS_ALIGNMENT
    <= 2 of P1-P5 pass -> MIDPROCESS_ALIGNMENT_NOT_CONFIRMED
  N1 ambiguous (0.05 < p < 0.10): report with caution
```
