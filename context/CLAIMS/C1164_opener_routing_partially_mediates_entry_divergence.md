# C1164: Opener Routing Partially Mediates Entry Divergence

**Tier:** 2
**Scope:** B, line, opener, entry divergence, AXM residual
**Phase:** ENTRY_RESET_MECHANISM (Phase 415)
**Depends on:** C1158, C1163, C1035

## Statement

Opener properties (role entropy, initial-specialist PREFIX fraction, AXM return rate) partially mediate the C1158 entry divergence effect: coefficient shrinkage=0.406 (entry_div beta drops from -0.0548 to -0.0325 when controlling for opener features). Entry divergence retains independent signal (partial rho=-0.293, p=0.013 controlling for all opener features + C1035 baseline). Opener features alone add more variance than entry divergence alone (dR²=0.159 vs 0.068 on C1035 baseline, F=13.01, p<0.000002, LOO=0.656). Combined model R²=0.815, LOO=0.669.

## Evidence

| Model | R² | LOO | dR² vs baseline |
|-------|-----|-----|-----------------|
| C1035 baseline (n=65) | 0.634 | 0.511 | — |
| + entry_div only | 0.703 | 0.543 | 0.068 |
| + opener features only | 0.793 | 0.656 | 0.159 |
| + entry_div + opener | 0.815 | 0.669 | 0.180 |

**Coefficient shrinkage:** 0.406 (partial mediation range 0.20-0.50)

**Partial rho (entry_div vs AXM | opener + baseline):** -0.293, p=0.013 (survives)

## Structural Implication

Entry divergence (C1158) is not reducible to opener identity — it captures transition dynamics at position 0→1 that go beyond what the opener's role, PREFIX, or average routing pattern can explain. However, ~40% of entry divergence's predictive power overlaps with opener routing. The two predictors are partially redundant: opener features tell you WHAT the opener does on average; entry divergence tells you HOW DIFFERENT that is from the interior. Both carry non-overlapping information about the folio's procedural complexity.
