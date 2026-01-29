# C606: CC->EN Line-Level Routing

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase LINE_LEVEL_LANE_VALIDATION
**Scope:** B_INTERNAL | EN | CC

## Statement

CC trigger type predicts the immediately following EN subfamily within the same line. CC_OL_D routes to QO at 1.67x enrichment; CC_DAIIN and CC_OL route to CHSH at 0.78-0.74x QO depletion. Same-lane CC->EN pairs sit physically closer (1.81-1.83 tokens) than cross-lane pairs (2.48-2.78 tokens).

## Evidence

Contingency table (665 CC->next-EN pairs):

| CC type | QO | CHSH | QO% | obs/exp QO |
|---------|-----|------|-----|------------|
| CC_DAIIN | 46 | 169 | 21.4% | 0.78 |
| CC_OL | 56 | 219 | 20.4% | 0.74 |
| CC_OL_D | 80 | 95 | 45.7% | 1.67 |

Chi-squared: chi2=40.28, df=2, p<10^-6
Cramer's V: 0.246

Mean token distance (CC to first EN):
- Same-lane: CC_DAIIN->CHSH=1.83, CC_OL_D->QO=1.81
- Cross-lane: CC_DAIIN->QO=2.78, CC_OL->QO=2.77, CC_OL_D->CHSH=2.48

## Relationship to C603

C603 established folio-level prediction (rho=0.345-0.355). C606 demonstrates the mechanism operates at the token level: CC type determines the next EN, with same-lane pairs physically adjacent.

## Related

- C600 (CC trigger sub-group selectivity - token-level)
- C603 (CC folio-level subfamily prediction)
- C608 (no lane coherence - mechanism is local, not line-wide)
