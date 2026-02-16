### C1075 — Compatibility Asymmetry Is Frequency-Dominated

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (MIDDLE pairwise compatibility x morphological features)
- **Phase:** TERMINAL_COMPATIBILITY_GEOGRAPHY (2026-02-15)

**Finding:** Logistic regression on 271,245 MIDDLE pairs (after excluding both-singleton pairs per C513) identifies token frequency as the dominant predictor of C475 compatibility (freq_sum standardized coefficient +1.654, CI [1.626, 1.684]). INITIAL character match shows a genuine but sub-threshold signal (+0.089, CI [0.051, 0.125]), while FINAL character match is non-significant (+0.026, CI [-0.011, 0.064]). The INITIAL x FINAL interaction term is near zero (+0.016, CI [-0.023, 0.047]), consistent with C1003 (pairwise compositionality, no synergy). Shared C517 hinge letter (+0.096) and same affordance bin (+0.078) are significant secondary features. Length sum is negatively associated (-0.133).

**Interpretation:** The 3.2x INITIAL > FINAL compatibility asymmetry from C1072 is real but frequency-dominated. After controlling for frequency, length, affordance bin, prefix, and C517 hinge letters, INITIAL character matching contributes only +0.089 standardized units — below the pre-registered 0.10 threshold for claiming character identity drives the effect. The asymmetry appears to be a consequence of frequency neighborhoods rather than morphological character identity per se. Sensitivity analysis with singletons included shows INITIAL_match rises to +0.114, suggesting the threshold miss is marginal. The C1003 interaction confirmation (no synergy between INITIAL and FINAL match) validates the pairwise compositionality model.

**Extends:** C1072 (INITIAL > FINAL 3.2x asymmetry), C986 (frequency dominance), C985 (character-level limits)
**Confirms:** C1003 (pairwise compositionality — INITIAL x FINAL interaction ~0)
**Consistent with:** C517 (superstring hinge), C513 (singleton dominance)

**Quantitative:**
- Total pairs: 471,906; after singleton exclusion: 271,245 (57.5% coverage)
- Positive rate (compatible): 3.71%
- Standardized coefficients (95% CI, 100 bootstrap):
  - freq_sum: +1.654 [1.626, 1.684] (dominant)
  - length_sum: -0.133 [-0.173, -0.094]
  - shared_hinge: +0.096 [0.053, 0.128]
  - INITIAL_match: +0.089 [0.051, 0.125] (below 0.10 threshold)
  - same_bin: +0.078 [0.032, 0.123]
  - FINAL_match: +0.026 [-0.011, 0.064] NS
  - INITIAL_x_FINAL: +0.016 [-0.023, 0.047] NS (C1003 consistent)
  - same_prefix: +0.001 [-0.031, 0.026] NS
- Sensitivity (with singletons): INITIAL_match rises to +0.114
