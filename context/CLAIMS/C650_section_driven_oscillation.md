# C650: Section-Driven EN Oscillation Rate

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

EN QO/CHSH oscillation rate is section-driven, not REGIME-driven. Section partial eta2=0.174 (p=0.024) after controlling REGIME; REGIME partial eta2=0.158 (p=0.069 NS) after controlling section. BIO has highest oscillation (0.593); HERBAL lowest (0.457).

## Evidence

- 66 folios with >= 5 EN-EN pairs and known REGIME
- Kruskal-Wallis by REGIME: H=10.44, p=0.015 (significant alone)
- Kruskal-Wallis by section: H=10.50, p=0.033 (significant alone)
- Two-way permutation test (10,000 shuffles):
  - Section partial eta2=0.174, perm p=0.024 (SIGNIFICANT after controlling REGIME)
  - REGIME partial eta2=0.158, perm p=0.069 (NS after controlling section)
- By section: BIO=0.593, T=0.582, S=0.530, C=0.512, HERBAL=0.457
- REGIME_4 has lowest mean (0.457), but this is confounded with HERBAL section

## Interpretation

Oscillation rate reflects material type (what is being processed), not execution stage (how far along the program is). BIO content requires faster lane switching; herbal processing allows sustained same-lane operation. The REGIME effect is mediated through section assignment.

## Cross-References

- C643: Lane hysteresis oscillation (0.563 overall, BIO=0.606, HERBAL_B=0.427) -- C650 identifies section as driver
- C577: Interleaving is content-driven, not positional
- C551: ENERGY/FLOW anticorrelation across sections
- C552-C555: Section specialist profiles

## Provenance

LANE_FUNCTIONAL_PROFILING, Script 2 (lane_oscillation_dynamics.py), Test 4
