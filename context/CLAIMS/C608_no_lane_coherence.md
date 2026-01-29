# C608: No Lane Coherence / Local Routing Mechanism

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase LINE_LEVEL_LANE_VALIDATION
**Scope:** B_INTERNAL | EN | CC

## Statement

Lines do NOT specialize toward one EN subfamily. Observed dominant proportion (0.662) is below the null expectation (0.672), p=0.963. No directional asymmetry exists: first-half CC does not predict second-half EN more than the reverse (difference=-0.008, 95% CI [-0.151, 0.141]). The two-lane model operates via local token-level routing (CC->next EN), not through line-level lane identity.

## Evidence

### Lane Coherence Test
- 462 lines with >=5 EN (QO/CHSH) tokens
- Global CHSH base rate: 0.531
- Observed mean dominant proportion: 0.662
- Permutation null (10,000 shuffles): mean=0.672, std=0.006
- p=0.963 (one-sided), Cohen's d=-1.754
- **Lines mix freely — no specialization**

### Directionality Test
- Forward (first-half CC -> second-half EN): rho=0.027, p=0.603, n=372
- Reverse (second-half CC -> first-half EN): rho=0.035, p=0.503, n=363
- Difference: -0.008, Bootstrap 95% CI: [-0.151, 0.141]
- **No directional asymmetry — shared line context, not left-to-right causation**

## Mechanism Implication

The two-lane model is NOT:
- Line-level specialization (lines don't prefer one lane)
- Left-to-right causal routing (no directional asymmetry)

The two-lane model IS:
- Local token-level routing (C606: CC predicts next EN, distance 1.8 tokens)
- Aggregate outcome of many local routing events within a folio (C603, C605)

This constrains interpretation: lanes are a grammar mechanism (CC triggers specific EN subfamilies), not an organizational principle (lines don't "choose" a lane).

## Related

- C606 (CC->EN line-level routing - the local mechanism)
- C607 (line-level escape prediction - confirmed at line level)
- C577 (EN interleaving content-driven)
- C605 (two-lane folio-level validation)
