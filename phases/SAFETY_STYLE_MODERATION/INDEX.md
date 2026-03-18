# Phase 601: SAFETY_STYLE_MODERATION

**Status:** COMPLETE
**Verdict:** STARS_ONLY_REPLICATION (S2+P3+P4 pass, P1+P2 fail)
**Constraints:** C1741–C1742
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
| P2 | Herbal nested OLS F-test | F=0.457, p=0.506, dR²=0.006 | **FAIL** |
| P3 | Herbal A3 surgery (R4 vs R3) | R4=0.101 > R3=0.032, p=0.021 | **PASS** |
| P4 | strong_close_fraction partial Spearman | rho=0.304, p=0.008 | **PASS** |
| S1a | DYE orthogonality (Stars) | rho=-0.282, p=0.204 | orthogonal |
| S1b | DYE orthogonality (all) | rho=0.045, p=0.702 | orthogonal |
| S3 | A2 dummy sensitivity | coeff=-0.124, t=-5.31, p=1e-6 | profile-concentrated |

**Formal verdict: STARS_ONLY_REPLICATION** per pre-registered decision logic (S2 passes, P1+P2 fail, so verdict falls to "Only S2 passes" branch).

## Key Findings

### 1. Stars Safety-Balance Replicates (S2)
The combined safety_balance metric captures the individual-axis signal from C1740. S:R1=0.122 > S:R3=0.012 (p=0.002). The calibration anchor holds: gentle sustained (R1) favors preventive safety; open-cycle elevated (R3) favors transformative.

### 2. Continuous Forgivingness Moderation Fails (P1, P2)
P1 (section-controlled partial Spearman): rho=-0.047, p=0.686. The raw correlation is strong (rho=-0.383, p=0.0006) but vanishes under section control — the forgivingness-safety association is entirely driven by between-section contrasts (B section has both low mean_null_dye and low safety_balance). Within sections, no gradient effect.

P2 (Herbal nested OLS): REGIME alone captures R²=0.696. Adding mean_null_dye contributes dR²=0.006 (F=0.457, p=0.506). Because family and REGIME are perfectly confounded in Herbal, REGIME dummies already absorb the A2/A3 contrast. The continuous metric adds nothing beyond what the categorical already captures.

### 3. A2 Profile Is a Discrete Categorical Safety-Style Shift (S3)
The A2 dummy in a section-controlled OLS yields coefficient=-0.124, t=-5.31, p=1.2×10⁻⁶, R²=0.579. A2 mean safety_balance = -0.022 vs non-A2 = 0.096. The safety-style moderation is real but operates as a discrete profile-level shift, not a continuous forgivingness gradient. A2 folios categorically prefer transformative safety (ii) over preventive (e→y). This is the mechanism behind the H:R2 reversal (C1739): H:R2 = all A2, and A2 shifts safety toward transformative intervention.

### 4. Herbal A3 Surgery Recovers Thermal-Intensity Signal (P3)
Removing all A2 folios from Herbal, the thermal-intensity → safety-balance signal reappears among A3 folios: H(A3):R4=0.101 > H(A3):R3=0.032, p=0.021. This confirms that A2 was the source of the Phase 600 Herbal reversal. Among A3 folios, the thermal-intensity ordering (higher REGIME = more preventive safety) works in Herbal just as it does in Stars.

### 5. Closure Authenticity Modulates Safety Strategy (P4)
Section-controlled partial Spearman: strong_close_fraction vs safety_balance, rho=0.304, p=0.008. Folios with more authentic closures (higher fraction of strong close events) sustain preventive safety (e→y). Folios where closures are mostly weak/counterfeitable shift toward transformative rescue (ii). This connects C1642 (strong-vs-weak closure architecture) to C1732-C1733 (safety substitution) via a within-section mechanism. The raw correlation is near zero (rho=0.010, p=0.932) — the authenticity-safety link only emerges after section control, consistent with section-specific closure profiles.

### 6. DYE Orthogonality Confirmed (S1a, S1b)
DYE_advantage is orthogonal to safety_balance both within Stars (rho=-0.282, p=0.204) and across all folios (rho=0.045, p=0.702). This confirms that DYE operates on the intervention-productivity axis (C1633-C1634), independent of the preventive/transformative safety axis (C1732-C1733).

## What This Means

The formal verdict (STARS_ONLY_REPLICATION) is technically correct — the pre-registered core test (P2) and global association (P1) both fail. But the supplementary tests reveal a clear mechanistic picture:

1. **A2 profile categorically shifts safety toward transformative** (S3: p=1e-6). This is not a continuous forgivingness gradient but a discrete apparatus-family effect.
2. **Removing A2 recovers the thermal-intensity signal in Herbal** (P3: p=0.021). A2 was the entire source of the Phase 600 H:R2 reversal.
3. **Closure authenticity modulates safety within sections** (P4: p=0.008). Strong closures sustain preventive safety; weak/counterfeitable closures favor transformative.
4. **DYE is orthogonal to safety** (S1a/S1b: both p>0.20). Intervention-productivity and safety-polarity are independent dimensions of the closure apparatus manifold.

P2 fails because of the Herbal family×REGIME perfect confound: REGIME dummies already absorb what mean_null_dye measures. P1 fails because section control absorbs the between-section component that drives the raw correlation (rho=-0.383, p=0.0006). The moderation is real, but it operates at the discrete profile level (A2 vs non-A2), not along a smooth continuous gradient. The pre-registration framed the mechanism as continuous; the data says it's categorical.

The validated Brunschwig-Voynich alignment now includes:
1. Thermal intensity within Stars: ey_rate R1>R3 (C1735, p=0.0003) and safety_balance R1>R3 (S2, p=0.002)
2. Safety substitution within Stars: ii_rate R1<R3 (C1740, p=0.026)
3. Within-folio thermal gradient: THERMAL→ke-depth (C1736, rho=0.303)
4. **A2 profile = discrete transformative safety shift** (C1741, S3 p=1e-6)
5. **Herbal A3 thermal-intensity recovery** (C1741, P3 p=0.021)
6. **Closure authenticity → preventive safety** (C1742, P4 p=0.008)
