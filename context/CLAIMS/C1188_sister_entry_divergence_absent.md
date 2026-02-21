# C1188: Sister Choice Does Not Independently Predict Entry Divergence

**Tier:** 2 | **Scope:** B, sister pairs, boundary architecture | **Phase:** 421 (SISTER_ENTRY_DIVERGENCE_EXTENSION)

## Statement

opener_ch_frac (ch/(ch+sh) among line-initial tokens) does not independently predict per-folio entry divergence (jsd_entry) beyond the existing boundary architecture (C1163-C1165). Pre-registered minimal model comparison: ΔLOO-R²(S vs B3) = -0.020 (below 0.02 threshold; actually hurts prediction). Coefficient sign is NEGATIVE (opposite pre-registered expectation of positive). Effect absent in all sections and in AXM mediation.

## Evidence

Pre-registered 5-test battery (n=65 folios):

**T1 Model Cascade (full-sample OLS):**
- B0 (section+regime): R²=0.630
- B1 (+opener routing): R²=0.666
- B2 (+axm_return_rate): R²=0.725 (F=11.24, p=0.0015 — biggest gain)
- B3 (+hazard/bridge/pfx_ent): R²=0.739
- **S (+opener_ch_frac): R²=0.739** (dR²=0.0006, F=0.12, p=0.73)

**T2 Nested LOFO (per-fold standardization):**
- B3: LOO-R²=0.425
- S: LOO-R²=0.406
- **ΔLOO = -0.020** (adding sister HURTS cross-validation)

**T3 Within-section LOFO:** All sections negative (B: -0.40, H: -0.59, S: -0.24)

**T4 Coefficient analysis:**
- beta(opener_ch_frac) = -0.003 (negative, wrong sign)
- Unstable under ablation (flips sign when prefix_entropy_opener dropped)
- Collinearity R²=0.415 (moderate, not driving the null)

**T5 AXM mediation:** ΔLOO = -0.014, F=0.32, p=0.57 (absorbed)

## Interpretation

C1186's correlation (entry JSD partial rho=0.312) is REAL but fully mediated by opener-routing features (C1164: role_entropy, prefix_entropy_opener, init_spec_frac) and AXM return rate (C1163). Sister choice tracks these features but carries no independent information about entry divergence.

## Relation to Other Constraints

- **Refines C1186:** The correlation is proxy, not causal
- **Confirms C1163-C1165:** The existing entry-side battery is sufficient
- **Confirms C1169:** The ~27% AXM residual is not reducible by sister metrics
- **Extends C1187:** Sister is a boundary control knob but operates THROUGH opener-routing features, not independently of them

## Source

`phases/SISTER_ENTRY_DIVERGENCE_EXTENSION/results/sister_entry_divergence_extension.json`
