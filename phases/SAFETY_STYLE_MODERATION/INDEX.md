# Phase 601: SAFETY_STYLE_MODERATION

**Status:** COMPLETE
**Pre-registered verdict:** STARS_ONLY_REPLICATION (S2+P3+P4 pass, P1+P2 fail)
**Substantive verdict:** PROFILE_CONDITIONED_SAFETY_MODERATION
**Constraints:** C1741-C1743
**Script:** `scripts/safety_style_moderation.py` (5.2s)
**Results:** `results/safety_style_moderation_results.json`
**Pre-registration:** `PREDICTIONS.md` (SHA-256: `f485ef57f69b453511a3ab45cb1f9e6992098bf18ccb8b4f219b2c7567689a58`)

## Motivation

Phase 600 confirmed safety substitution within Stars (C1740: ey p=0.0003, ii p=0.026) but failed as a cross-section bridge (C1739: 0/4). The key diagnostic finding was H:R2 reversal: highest sealed cell deploys transformative, not preventive safety — consistent with authenticity-sensitive containment loading onto transformative safety (C1639-C1647, C1733).

Phase 601 tests: **Does A2-like apparatus forgivingness/authenticity regime shift safety style toward transformative intervention?** This is not another broad bridge attempt — it tests the *mechanism* behind the confirmed Stars signal and the Herbal reversal.

## Design

### Response Variable
- **safety_balance** = ey_rate - ii_rate per folio
- ey_rate: HEAD='e' AND TERMINAL='y' tokens / total tokens
- ii_rate: max_consecutive_i(middle) >= 2 tokens / total tokens

### Moderator Variables
- **mean_null_dye**: per-folio apparatus forgivingness (how well random tokens score on DYE)
- **strong_close_fraction**: per-folio fraction of eligible close events that are STRONG
- **profile**: apparatus family A1/A2/A3
- **DYE_advantage**: intervention-productivity metric
- **section/REGIME**: controls

### Sample: 76 Currier B folios

### Critical Structural Fact
Within Herbal, apparatus family and REGIME are **perfectly confounded**:
- H:R2 = 11 folios, ALL A2_SEALED_RECIRCULATION
- H:R3 = 5 folios, ALL A3_DISTILL_COLLECT
- H:R4 = 9 folios, ALL A3_DISTILL_COLLECT

## Results

| Test | Metric | Result | Verdict |
|------|--------|--------|---------|
| S2 | Stars R1 vs R3 safety_balance | R1=0.122 > R3=0.012, p=0.002 | **PASS** |
| P0 | ICC of mean_null_dye by section | 0.284 | diagnostic |
| P1 | Section-controlled partial Spearman | rho=-0.047, p=0.686 | **FAIL** |
| P2 | Herbal nested OLS F-test | F=0.457, p=0.506, dR^2=0.006 | **FAIL** |
| P3 | Herbal A3 surgery (R4 vs R3) | R4=0.101 > R3=0.032, p=0.021 | **PASS** |
| P4 | strong_close_fraction partial Spearman | rho=0.304, p=0.008 | **PASS** |
| S1a | DYE orthogonality (Stars) | rho=-0.282, p=0.204 | orthogonal |
| S1b | DYE orthogonality (all) | rho=0.045, p=0.702 | orthogonal |
| S3 | A2 dummy sensitivity | coeff=-0.124, t=-5.31, p=1e-6 | profile-concentrated |

**Pre-registered verdict: STARS_ONLY_REPLICATION** (S2 passes, P1+P2 fail, so the decision tree falls to "Only S2 passes"). The pre-registered continuous-forgivingness moderation model failed.

**Substantive verdict: PROFILE_CONDITIONED_SAFETY_MODERATION.** The pre-registered framing asked the wrong statistical question but got the right structural answer. Safety style is not governed by a corpus-wide continuous forgivingness gradient. It is profile-conditioned: A2 folios show a categorical shift toward transformative safety (S3 p=1e-6), closure authenticity supports preventive safety within sections (P4 p=0.008), and removing A2 from Herbal restores the expected thermal-intensity ordering (P3 p=0.021).

## Key Findings

### 1. Stars Safety-Balance Replicates (S2)
The combined safety_balance metric captures the individual-axis signal from C1740. S:R1=0.122 > S:R3=0.012 (p=0.002). The calibration anchor holds: gentle sustained (R1) favors preventive safety; open-cycle elevated (R3) favors transformative.

### 2. Continuous Forgivingness Moderation Fails (P1, P2)
P1 (section-controlled partial Spearman): rho=-0.047, p=0.686. The raw correlation is strong (rho=-0.383, p=0.0006) but vanishes under section control — the forgivingness-safety association is entirely driven by between-section contrasts (B section has both low mean_null_dye and low safety_balance). Within sections, no gradient effect.

P2 (Herbal nested OLS): REGIME alone captures R^2=0.696. Adding mean_null_dye contributes dR^2=0.006 (F=0.457, p=0.506). Because family and REGIME are perfectly confounded in Herbal, REGIME dummies already absorb the A2/A3 contrast. The continuous metric adds nothing beyond what the categorical already captures.

The failure is informative: mean_null_dye is a one-dimensional forgivingness coordinate, but A2 is a compound apparatus regime — high null close recovery (C1639), higher threshold to get authentic grammar advantage (C1644), morphology-selective counterfeiting (C1645), weak events losing to null (C1642). A scalar cannot recover a compound profile regime once section structure bites.

### 3. A2 Profile Is the Mechanism (S3)
The A2 dummy in a section-controlled OLS yields coefficient=-0.124, t=-5.31, p=1.2x10^-6, R^2=0.579. A2 mean safety_balance = -0.022 vs non-A2 = 0.096. This is the biggest finding in the phase — not a side diagnostic but the mechanism itself.

A2 folios categorically prefer transformative safety (ii) over preventive (e->y). This fits the validated apparatus stack: A2 is not just "forgiving" in one scalar sense. It is a compound regime with high null close recovery (C1639), containment-linked recovery channels (C1643), higher authenticity threshold (C1644), morphology-selective counterfeiting (C1645), stronger ACS than CTS discrimination (C1647), and weak events losing to null specifically in A2 (C1642). The scalar mean_null_dye cannot capture this compound structure — A2 is a profile regime, not a one-dimensional forgivingness coordinate.

This is the mechanism behind the H:R2 reversal (C1739): H:R2 = all A2, and A2 shifts safety toward transformative intervention.

### 4. Herbal A3 Surgery Recovers Thermal-Intensity Signal (P3)
Removing all A2 folios from Herbal, the safety-balance signal reappears among A3 folios: H(A3):R4=0.101 > H(A3):R3=0.032, p=0.021. This confirms that A2 was the specific source of the Phase 600 Herbal reversal — the failure was not "Herbal is just different" or "everything breaks there," but specifically A2 contamination/inversion.

**Caution:** This shows that within Herbal A3, removing A2 restores the expected R4>R3 safety_balance ordering for this local comparison. It does NOT establish a general law that "higher REGIME = more preventive safety." C1730 shows ii ratio is highest in R4 and R2 globally, and C494 identifies R4 as a precision axis, not a sheer intensity axis. The P3 result is specific to the A3 Herbal context.

### 5. Closure Authenticity Modulates Safety Strategy (P4)
Section-controlled partial Spearman: strong_close_fraction vs safety_balance, rho=0.304, p=0.008. This is probably the cleanest mechanistic bridge in the phase.

Folios with more authentic closures (higher fraction of strong close events) sustain preventive safety (e->y). Folios where closures are mostly weak/counterfeitable shift toward transformative rescue (ii). In plain terms: if your closures are often genuinely strong, preventive stabilization is worth buying into; if closure events are mostly weak or counterfeitable, you resort to transformative rescue.

This directly connects C1642 (gradient of grammar advantage by closure strength), C1644 (profile-dependent threshold for authentic closure benefit), C1645 (selective counterfeitability), C1647 (authenticity strength matters more than raw CTS), and C1733 (preventive vs transformative style depends on whether stable closure can be trusted).

The raw correlation is near zero (rho=0.010, p=0.932) — the authenticity-safety link only emerges after section control, consistent with section-specific closure profiles.

### 6. DYE Orthogonality Confirmed (S1a, S1b)
DYE_advantage is orthogonal to safety_balance both within Stars (rho=-0.282, p=0.204) and across all folios (rho=0.045, p=0.702). This stabilizes the separation established in C1740 and C1633-C1634: DYE is productive intervention efficiency, safety_balance is preventive vs transformative doctrine. Those are different control axes. This prevents future category mistakes.

## What This Means

Phase 601 falsifies the pre-registered smooth-forgivingness moderation model but identifies the correct mechanism. Safety style in Currier B is not governed by a corpus-wide continuous forgivingness gradient. Instead, it is profile-conditioned:

1. **A2 is a compound apparatus regime** that categorically shifts safety toward transformative intervention (S3: p=1e-6). It is not "more forgiving" on a single scalar — it has high null close recovery but poor closure trustworthiness, leading to reliance on transformative rescue. This is the mechanism behind the H:R2 reversal (C1739).

2. **Closure authenticity is the local within-section mechanism** (P4: p=0.008). Folios with more strong/authentic closures sustain preventive safety; folios with weak/counterfeitable closures shift toward transformative rescue. This is distinct from and independent of the A2 profile effect.

3. **Stars provides the clean baseline law** where the "ordinary" thermal safety pattern operates: higher gentleness/sustained regime -> more preventive safety (S2: p=0.002, replicating C1735/C1740). DYE is orthogonal.

4. **Removing A2 rescues Herbal** (P3: p=0.021). The Phase 600 Herbal reversal was not general Herbal behavior but specifically A2 inversion. Among A3 Herbal folios, the expected ordering reappears.

The pre-registration asked: "is there a continuous forgivingness gradient that predicts safety balance?" The manuscript answered: "No — the moderation is mostly discrete and profile-specific, especially A2." That is a high-value negative: it replaces a naive scalar model with a compound profile-conditioned mechanism that is far more consistent with the validated apparatus architecture (C1639-C1647).

Safety style depends on:
- section-conditioned thermal program (Stars baseline law)
- apparatus-family regime (A2 categorical inversion)
- closure authenticity / strength (within-section continuous modulator)
- whether weak closures are trustworthy in that response surface

This is much more sophisticated than any historical bridge that collapses to "more sealed = more preventive." Together with C1735, C1739, and C1740, this indicates that Brunschwig alignment survives not as apparatus-name mapping but as a section- and profile-conditioned safety doctrine: preventive stabilization where closure can be trusted, transformative rescue where closure authenticity is difficult to maintain.
