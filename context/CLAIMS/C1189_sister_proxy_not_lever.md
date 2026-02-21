# C1189: Sister Choice Is a Proxy for Opener-Routing Features, Not an Independent Lever

**Tier:** 2 | **Scope:** B, sister pairs, boundary architecture, synthesis | **Phase:** 421 (SISTER_ENTRY_DIVERGENCE_EXTENSION)

## Statement

Sister-pair composition (ch/sh) at line openers is correlated with entry divergence (C1186) but this correlation is entirely mediated by the opener-routing features established in C1163-C1165. When opener role entropy, prefix entropy, initial-specialist fraction, and AXM return rate are included as regressors, sister adds zero independent predictive power (ΔLOO-R² = -0.020). The overall verdict is **SISTER_ENTRY_LEVER_ABSENT**.

This closes the "below role identity" entry control investigation initiated by C1162. Sister was the strongest remaining candidate for a missing entry lever, and its failure to extend the model confirms that the existing boundary architecture (C1168) has captured the available deterministic structure in entry divergence.

## Design

Pre-registered minimal model comparison (expert-designed):
- **Target:** jsd_entry (per-folio entry divergence, 6-state JSD, Phase 415 definition)
- **Baseline B3:** section + regime dummies + role_entropy + prefix_entropy_opener + init_spec_frac + axm_return_rate + hazard_density + bridge_pc1 + prefix_entropy
- **Extension S:** B3 + opener_ch_frac
- **Threshold:** ΔLOO-R² ≥ 0.02 (pre-registered)
- **CV scheme:** LOFO with nested preprocessing (standardize per fold)
- **Result:** ΔLOO-R² = -0.020, coefficient sign wrong, all sections absent

## Implications

1. **C1169's ~27% AXM residual is genuine:** The largest remaining candidate lever (sister) failed to reduce it. The residual is likely irreducible design freedom (C980, C1035).

2. **C1186 reframed:** Sister-boundary coupling is an EMERGENT correlation — opener prefix distributions that favor ch also tend to produce higher role entropy and initial-specialist fractions, which in turn drive entry divergence. Sister is downstream, not causal.

3. **Boundary architecture is structurally complete:** The entry-side model (C1163-C1165) and exit-side model (C1166-C1167), combined in C1168, represent the full deterministic structure available in boundary divergence. Further predictor search is at diminishing returns.

## Source

`phases/SISTER_ENTRY_DIVERGENCE_EXTENSION/results/sister_entry_divergence_extension.json`
