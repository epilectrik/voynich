### C1070 — Atom Ordering Grammar Independent of Kernel Directional Bias

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (compound MIDDLE construction grammar)
- **Phase:** MULTI_LAYER_COMPATIBILITY_ARCHITECTURE (2026-02-15)

**Finding:** Of C1065's 21 asymmetric atom pairs (>80% directional dominance), only 2 involve cross-kernel-class ordering (e-type before k-type). Both MISMATCH C521's prediction that e→k should be suppressed (0.27x within-token ratio). 18/21 pairs involve same-class ordering (k→k, e→e) where C521 makes no prediction.

**Interpretation:** The compound atom ordering grammar (C1065, V=0.376) does NOT inherit C521's character-level directional asymmetry. At the compound level, e-type atoms CAN precede k-type atoms (eol→olk, eo→ke), even though C521 suppresses e→k within individual characters. This confirms C1066's construction-execution independence at a finer grain: construction grammar operates at the compound level with its own rules, not reducible to kernel physics.

**Extends:** C1065 (atom bigram grammar V=0.376), C1066 (construction-execution independence rho=-0.004), C521 (kernel directional asymmetry)

**Quantitative:**
- Kernel-involved cross-class pairs: 2/21
- C521 matches: 0/2
- Match rate: 0.0%
- Binomial p: 1.0 (no C521 signal)
- Same-class pairs (no C521 prediction): 18/21
