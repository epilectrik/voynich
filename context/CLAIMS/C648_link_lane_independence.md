# C648: LINK-Lane Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

LINK rate is lane-independent: QO 15.4% vs CHSH 14.7% (chi2=0.44, p=0.506, V=0.0095). Excluding AX_FINAL: 11.0% vs 11.1%. The two-lane architecture does not modulate monitoring behavior.

## Evidence

- 5,542 EN tokens with nearest-AX pairing across 2,420 B lines
- Overall chi2=0.44, p=0.506, Cramer's V=0.0095 (negligible)
- By AX sub-position: INIT (23.6% vs 23.9%, NS), MED (3.9% vs 3.5%, NS), FINAL (43.3% vs 36.1%, p=0.052 marginal)
- AX_FINAL marginal signal fully explained by C617 (LINK concentrates at AX_FINAL 35.3%) and C599 (AX_FINAL avoids QO 0.59x)
- Excluding AX_FINAL: QO 11.0% vs CHSH 11.1% -- identical to third decimal

## Interpretation

LINK monitoring operates at a level above lane identity. The observation/intervention boundary (C366) is lane-agnostic: both energy-application (QO) and stabilization (CHSH) contexts receive equal monitoring.

## Cross-References

- C365: LINK spatially uniform across B
- C366/C190: LINK as observation/intervention boundary
- C609: LINK density 13.2% across all roles
- C617: AX-LINK subgroup asymmetry (AX_FINAL concentrates LINK)
- C599: AX scaffolding routing (AX_FINAL avoids QO)

## Provenance

LANE_FUNCTIONAL_PROFILING, Script 1 (lane_monitoring_correlates.py), Test 1
