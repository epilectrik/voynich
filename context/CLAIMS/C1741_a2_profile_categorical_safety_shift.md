# C1741: A2 Profile Categorical Safety-Style Shift

**Tier:** 2
**Phase:** SAFETY_STYLE_MODERATION (Phase 601)
**Scope:** B, apparatus, safety, A2, profile, REGIME, Herbal, Stars, Brunschwig

## Finding

Apparatus family A2 categorically shifts safety strategy toward transformative intervention (ii) over preventive stabilization (e→y). This operates as a discrete profile-level effect, not a continuous forgivingness gradient.

Evidence:
- **S3 (A2 dummy)**: section-controlled OLS coefficient=-0.124, t=-5.31, p=1.2×10⁻⁶, R²=0.579. A2 mean safety_balance=-0.022 vs non-A2=0.096.
- **P3 (surgery)**: removing A2 from Herbal recovers thermal-intensity → safety-balance signal among A3 folios. H(A3):R4=0.101 > H(A3):R3=0.032, p=0.021.
- **S2 (Stars anchor)**: safety_balance R1=0.122 > R3=0.012, p=0.002. Stars (all A3) replicates combined metric from C1740.
- **P1/P2 (continuous tests) FAIL**: section-controlled partial Spearman rho=-0.047, p=0.686. Herbal nested OLS F=0.457, p=0.506, dR²=0.006. Continuous mean_null_dye adds nothing beyond categorical REGIME contrasts.

## What This Shows and Does Not Show

**Shows:** The H:R2 reversal (C1739) is attributable to A2 profile: H:R2 = all A2, and A2 categorically loads onto transformative safety. This is the mechanism behind Phase 600's 0/4 Herbal failure. Among A3 folios only (P3 surgery), the thermal-intensity ordering works in Herbal just as in Stars: higher REGIME = more preventive safety. The Brunschwig-Voynich alignment extends to Herbal A3 once A2's categorical shift is accounted for.

**Does NOT show:** That forgivingness is a continuous modulator of safety style. P1 (section-controlled) and P2 (Herbal within-REGIME) both fail. The moderation is real but categorical: A2 vs non-A2. Within A3 folios, mean_null_dye shows no gradient effect on safety. The perfect confound between family and REGIME in Herbal (H:R2=all A2, H:R3/R4=all A3) prevents separating profile from REGIME effects parametrically.

## Significance

This explains why the Phase 600 Brunschwig bridge failed at the cell level: the bridge assumed a monotone mapping from containment to safety, but A2 profile inverts the expected direction. A2's high null-recoverability + high authenticity threshold (C1639-C1647) makes preventive safety insufficient — weak closures get counterfeited, so the grammar deploys transformative rescue. The mechanism is profile-architectural, not a smooth continuum.

## Key Metrics

- A2 dummy: coeff=-0.124, t=-5.31, p=1.2×10⁻⁶ (section-controlled OLS, n=76)
- A2 mean safety_balance: -0.022 vs non-A2: 0.096
- Stars anchor: R1=0.122 > R3=0.012, p=0.002 (Mann-Whitney)
- Herbal A3 surgery: R4=0.101 > R3=0.032, p=0.021 (Mann-Whitney)
- P1 partial rho=-0.047, p=0.686 (FAIL); raw rho=-0.383, p=0.0006
- P2 F=0.457, p=0.506, dR²=0.006 (FAIL); REGIME-only R²=0.696

## Provenance

- Source: `phases/SAFETY_STYLE_MODERATION/results/safety_style_moderation_results.json`
- Pre-registration: `phases/SAFETY_STYLE_MODERATION/PREDICTIONS.md`
- Depends on: C1739 (H:R2 reversal), C1740 (Stars safety substitution), C1735 (ey_rate within Stars), C1732/C1733 (safety substitution architecture), C1639-C1647 (apparatus forgivingness/authenticity)
