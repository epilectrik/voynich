# C1181: Sister Choice Is Dynamically Consequential (AXM and Hazard)

**Tier:** 2
**Scope:** B, sister pairs, dynamics
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C1035, C1169

## Statement

Sister preference (ch/(ch+sh)) correlates with dynamical properties after controlling for section. ch-heavy folios have lower AXM self-transition rates (partial rho=-0.250, p=0.032) and higher hazard density (partial rho=0.255, p=0.028). The C1017 residual correlation is suggestive but not significant (partial rho=-0.191, p=0.106). Sister choice is a within-class control knob that modulates program dynamics, consistent with C506.b (intra-class behavioral heterogeneity) and C1026 (token identity is partial).

## Evidence

| Metric | Partial rho | p-value |
|--------|------------|---------|
| AXM self-transition | -0.250 | 0.032 |
| Hazard density | +0.255 | 0.028 |
| QO fraction | -0.097 | 0.418 |
| C1017 residual | -0.191 | 0.106 |
| Bridge PC1 | -0.193 | 0.102 |

All correlations control for section via partial Spearman.

## Interpretation

ch-heavy programs operate in a higher-hazard, lower-stability regime. This is consistent with C929's characterization: ch = active testing (more interventionist, more disruption risk), sh = passive monitoring (more stable). The effect is modest but genuine, and it establishes that sister choice is NOT free variation — it co-varies with the dynamical operating point of the program.

Note: This does NOT extend C1169's dual-boundary model (the C1017 residual correlation is below significance). Sister choice is a parallel axis of design freedom, not an extension of the AXM residual.

## Provenance

- Phase 420 Test 2: DYNAMICAL_CONSEQUENCE
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test2_dynamical_consequence
