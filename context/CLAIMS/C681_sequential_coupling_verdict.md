# C681: Sequential Coupling Verdict

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

**24 of 27 line features** show significant lag-1 prediction beyond position. Knowing the previous line's feature value improves prediction of the next line's value, even after accounting for positional trends. Verdict: **SEQUENTIALLY_COUPLED** — but the coupling is **folio-mediated** (shared context), not **line-to-line state propagation** (sequential memory).

## Method

For each feature: regression models comparing position-only (feature_N+1 ~ norm_pos_N+1) vs combined (feature_N+1 ~ feature_N + norm_pos_N+1). Delta-R2 with F-test for the lag-1 addition. Applied to 2,322 strictly consecutive line pairs. Verdict thresholds: >=10 features = SEQUENTIALLY_COUPLED; <=2 = INDEPENDENT; 3-9 = PARTIAL.

## Top Lag-1 Contributors

| Feature | R2 position | R2 combined | Delta-R2 | F | p |
|---------|-------------|-------------|----------|---|---|
| line_length_z | 0.040 | 0.137 | +0.098 | 262.6 | <1e-16 |
| EN | 0.006 | 0.097 | +0.091 | 234.2 | <1e-16 |
| link_density | 0.002 | 0.065 | +0.063 | 157.1 | <1e-16 |
| pfx_qo | 0.012 | 0.054 | +0.042 | 103.3 | <1e-16 |
| pfx_ot | 0.000 | 0.038 | +0.038 | 91.2 | <1e-16 |
| sfx_e_family | 0.006 | 0.044 | +0.037 | 90.3 | <1e-16 |
| pfx_sh | 0.000 | 0.029 | +0.029 | 69.3 | <1e-16 |
| FQ | 0.000 | 0.029 | +0.029 | 68.6 | <1e-16 |

## Non-Significant Features (3/27)

AX (p=0.060), sfx_ol (p=0.261), sfx_y (p=0.227).

## Key Numbers

| Metric | Value |
|--------|-------|
| Consecutive pairs | 2,322 |
| Features with significant lag-1 | 24/27 (88.9%) |
| Mean Delta-R2 (significant) | 0.024 |
| Max Delta-R2 | 0.098 (line_length_z) |
| Verdict | SEQUENTIALLY_COUPLED |

## Reconciliation

This SEQUENTIALLY_COUPLED verdict must be reconciled with:
- C670: No adjacent vocabulary coupling (Jaccard ns)
- C673: No CC trigger memory
- C674: QO autocorrelation is entirely folio-driven

The resolution: **lag-1 captures folio-level configuration, not line-to-line state transfer.** When feature_N predicts feature_N+1, it's primarily because both lines share the same folio's specific parameter settings (REGIME, section, folio-specific conditions), which vary beyond what a single REGIME label captures. Evidence: C674 showed that within-folio permutation eliminates autocorrelation — the coupling is folio-mediated.

## Structural Summary

Lines within a Currier B folio operate as **contextually-coupled, individually-independent assessments:**

1. The folio configures a parameter context (REGIME, section, folio-specific conditions)
2. Each line independently samples from that context
3. Adjacent lines are more similar than random (C679: +3.1%) because they share context
4. But lines do NOT propagate state: no vocabulary memory (C670), no trigger memory (C673), no lane memory beyond folio identity (C674)
5. The controller is stateless per-line but stateful per-folio

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_profile_classification.py` (Test 15)
- Extends: C670-C674 (independence tests), C664-C669 (class stationarity), C679 (adjacent coupling)
