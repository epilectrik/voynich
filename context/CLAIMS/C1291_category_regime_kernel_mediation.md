# C1291: Category-REGIME Association is Kernel-Mediated

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_REGIME_INTEGRATION (Phase 456)
**Date:** 2026-02-24

## Statement

Folio-level category composition strongly associates with REGIME assignment (chi2=526, V=0.106, p=5.5e-98), but this association is largely mediated by kernel atoms (k, h, e). After residualizing category fractions on kernel composition, the REGIME association drops to non-significant (Fisher combined KW p=0.061). Kernel R2 per category: THERMAL=0.779, TRANSITION=0.546, FLOW=0.409, CONTAINMENT=0.201. N=72 valid folios.

## Architecture

- **Kernel atoms are the common channel.** REGIMEs are defined from 15 folio features including k_ratio, h_ratio, e_ratio. Categories are defined from atoms including k ('heat'->THERMAL), h ('watch'->MONITORING), e ('cool'->THERMAL). The strong T1 association (V=0.106) runs primarily through this shared substrate.
- **REGIME_1 = THERMAL-dominant (29.7%)** because REGIME_1 folios have high k_ratio. REGIME_4 = OPERATION/TRANSITION-dominant because those categories don't depend on kernel atoms. The REGIME-category mapping is a consequence of kernel chemistry, not an independent organizational axis.
- **Not fully circular.** OPERATION (kernel R2=0.100) and MARKING (R2=0.105) have low kernel dependence but also show weak REGIME discrimination. The kernel pathway dominates but doesn't explain everything.

## Provenance

- Combines T1 (chi2=526, PASS) with T3 (circularity decomposition, FAIL)
- Connects C179/C494 (4 REGIMEs) with C1250 (8 categories)
- Explains why categories and REGIMEs appear related without being independently designed
