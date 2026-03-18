# C1743: Removing A2 Restores Herbal Thermal-Intensity Ordering

**Tier:** 2
**Phase:** SAFETY_STYLE_MODERATION (Phase 601)
**Scope:** B, Herbal, A2, A3, REGIME, safety, surgery

## Finding

Within Herbal A3 folios (excluding all A2), R4 > R3 on safety_balance (p=0.021, Mann-Whitney), indicating the Phase 600 Herbal reversal (C1739) was driven specifically by A2 profile structure rather than general Herbal section behavior.

- H(A3):R4 mean safety_balance = 0.101 (n=9)
- H(A3):R3 mean safety_balance = 0.032 (n=5)
- Mann-Whitney U=38.0, p=0.021

The Herbal failure in Phase 600 (0/3 concordant in P4, H:R2 reversal) was not "Herbal is just different" — it was specifically A2 contamination. All H:R2 folios are A2 (n=11), and A2 categorically inverts the safety-balance ordering (C1741). Once A2 is removed, the remaining A3 Herbal folios show the expected direction.

## What This Shows and Does Not Show

**Shows:** The A2 profile is the specific source of the Phase 600 Herbal reversal. Among A3 Herbal folios, the expected safety-balance ordering (R4 > R3) reappears at p=0.021. This is a clean surgery result: removing a mechanistically identified subpopulation (A2) recovers the predicted signal in the remaining data. Combined with C1741 (A2 dummy p=1e-6), this provides a complete account of why the closure-response bridge failed in Herbal.

**Does NOT show:** That "higher REGIME = more preventive safety" is a general law. C1730 shows ii ratio is highest in R4 and R2 globally, not monotonically ordered. C494 identifies R4 as a precision axis, not a sheer intensity axis. The P3 result is specific to the A3 Herbal context — it recovers a local comparison ordering, not a universal REGIME rule. The small sample (n=5 vs n=9) also limits power; the result is directionally strong but should be treated as a rescue/recovery finding rather than an independent discovery.

## Key Metrics

- H(A3):R4 safety_balance = 0.101 (n=9)
- H(A3):R3 safety_balance = 0.032 (n=5)
- Mann-Whitney U=38.0, p=0.021
- H:R2 (all A2, removed): safety_balance = -0.053 (n=11)

## Provenance

- Source: `phases/SAFETY_STYLE_MODERATION/results/safety_style_moderation_results.json`
- Pre-registration: `phases/SAFETY_STYLE_MODERATION/PREDICTIONS.md`
- Depends on: C1741 (A2 categorical shift), C1739 (H:R2 reversal), C1740 (Stars safety substitution), C494 (REGIME_4 precision axis), C1730 (ii ratio by REGIME)
