# C626: Lane-Hazard MIDDLE Discrimination

**Tier:** 2 | **Status:** CLOSED (NULL) | **Scope:** CURRIER_B | **Source:** HAZARD_CIRCUIT_TOKEN_RESOLUTION

## Statement

The two-lane architecture (C600, C606-C608) does **NOT** predict hazard participation at the token or MIDDLE level. Forbidden-exclusive MIDDLEs are in neither CHSH-lane nor QO-lane vocabulary (4/5 = NEITHER). CC trigger context shows no difference between forbidden and non-forbidden source tokens (Fisher p=0.866). Lane activation context shows no direction-dependent concentration. QO-lane hazard immunity (C601) is not explained by lane context -- hazard-class bigrams occur in QO context (167 total) even more than CHSH context (108 total).

## Evidence

### Forbidden-Exclusive MIDDLE Lane Membership

| MIDDLE | Lane Status |
|--------|-------------|
| aiin | NEITHER |
| al | NEITHER |
| edy | NEITHER |
| ey | NEITHER |
| l | BOTH (chsh + qo) |

4/5 forbidden-exclusive MIDDLEs are not found in any lane-specific vocabulary. The two-lane model's MIDDLE sets do not contain the hazard-discriminating vocabulary.

### CC Trigger Context

| Metric | Before Forbidden | Before Non-Forbidden |
|--------|-----------------|---------------------|
| CC_OL_D (QO trigger) | 96 | 87 |
| CC_DAIIN + CC_OL | 316 | 298 |
| Total with CC | 412 | 385 |

Fisher's exact test (CC_OL_D proportion x forbidden status): odds ratio 0.961, p=0.866. No difference.

### Lane Activation by Direction

| Direction | CHSH Rate | QO Rate | UNCLEAR Rate |
|-----------|-----------|---------|-------------|
| FORWARD | 12.9% | 21.2% | 53.1% |
| REVERSE | 17.9% | 27.6% | 37.9% |
| SELF_LOOP | 16.4% | 29.7% | 43.8% |
| CROSS_GROUP | 34.1% | 25.0% | 27.3% |

No direction category shows CHSH-lane over-representation consistent with a lane-specific hazard mechanism.

### QO Lane Hazard Context Volume

| Lane Context | Hazard Bigrams |
|-------------|---------------|
| QO context | 167 |
| CHSH context | 108 |
| MIXED | 83 |
| UNCLEAR | 291 |

QO contexts contain 55% more hazard-class bigrams than CHSH contexts, directly contradicting the hypothesis that QO immunity arises from lane-level hazard avoidance.

## Interpretation

The two-lane architecture operates at the token-routing level (C606, C608) but does not extend to hazard discrimination. Lane vocabulary, CC trigger context, and lane activation all fail to distinguish forbidden from non-forbidden transitions. The QO lane's hazard immunity (C601: QO never participates in forbidden transitions) is a property of EN_QO's class membership, not of the lane-activation context surrounding hazard transitions. Hazard is determined by circuit topology (C625), not by lane context.

## Extends

- **C600**: CC trigger selectivity does not extend to hazard prediction
- **C608**: Lane model is local routing, confirmed here as not reaching hazard level

## Related

C598, C600, C601, C606, C607, C608, C625
