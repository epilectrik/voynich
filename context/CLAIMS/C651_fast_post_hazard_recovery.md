# C651: Fast Uniform Post-Hazard QO Recovery

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Post-hazard QO recovery is fast and uniform: first EN is 75.2% CHSH (exact C645 replication); subsequent QO return requires median 1.0 CHSH tokens (45.1% immediate, 40.4% after one). No section (p=0.42), REGIME (p=0.18), or hazard class (p=0.12) variation. Recovery timing is unconditionally stable.

## Evidence

- 504 hazard events with subsequent EN tokens in same line
- First EN after hazard: QO 24.8%, CHSH 75.2% (binomial p < 1e-6 vs base 44.7%)
- Exactly replicates C645 (75.2% CHSH post-hazard dominance)
- CHSH-before-QO distribution (277 uncensored sequences):
  - 0 CHSH: 125 (45.1%) -- immediate QO return
  - 1 CHSH: 112 (40.4%)
  - 2 CHSH: 23 (8.3%)
  - 3 CHSH: 14 (5.1%)
  - 4 CHSH: 3 (1.1%)
  - Mean: 0.77, Median: 1.0
- 227 censored sequences (no QO found before line end)
- By section: Kruskal-Wallis H=3.87, p=0.42 (NS)
- By REGIME: Kruskal-Wallis H=4.90, p=0.18 (NS)
- By hazard class (7 vs 30): Mann-Whitney U=8353, p=0.12 (NS)

## Interpretation

After a hazard intervention, the system returns to energy-application mode (QO) within 0-1 stabilization tokens (CHSH). This is unconditionally fast: neither section content, execution stage, nor hazard type affects recovery speed. Consistent with C636 (recovery is unconditionally free) and C601 (hazard sub-group concentration). The tight distribution suggests recovery is a fixed-length grammatical operation, not a variable process.

## Cross-References

- C645: CHSH post-hazard dominance (75.2%) -- independently replicated
- C601: Hazard sub-group concentration (QO never participates, EN_CHSH absorbs 58%)
- C636: Recovery pathway is unconditionally free
- C643: Lane hysteresis oscillation

## Provenance

LANE_FUNCTIONAL_PROFILING, Script 2 (lane_oscillation_dynamics.py), Test 5
