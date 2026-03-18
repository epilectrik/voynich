# C1735: 1512 Thermal Intensity Alignment

**Tier:** 2
**Phase:** BRUNSCHWIG_1512_BLIND_PREDICTION (Phase 598)
**Scope:** B, Brunschwig, REGIME, safety, e->y, ke-depth

## Finding

The held-out 1512 Brunschwig *de compositis* (431 recipes, never used in any prior fit) predicts that the Voynich grammar's process-intensity axis modulates safety infrastructure. Specifically:

1. **e->y safe pathway rate discriminates REGIMEs within Stars section** (p=0.0007): R1 folios (gentle) show higher e->y rates (mean 0.182) than R3+R4 folios (intense, mean 0.106). This survives section stratification — the effect holds within Stars where both groups are represented (n=10 R1, n=13 R3+R4).

2. **Complexity correlates with ke-depth after size control**: Folio-level instruction class entropy correlates with mean ke-depth (partial Spearman rho=0.248, p=0.024) after controlling for log(token count). Attenuated from raw rho=0.377 but survives.

## What This Is

The 1512 book's gentle/elevated fire degree distinction predicts paragraph-level safety and kernel-depth modulation in the Voynich grammar. Gentle processes (balneum mariae, degree 1) map to higher safety provisioning. Elevated processes (degree 2-3, fire-based) map to deeper kernel engagement with less preventive safety.

## What This Is NOT

This is NOT an apparatus alignment finding. The 1512's fire degree distinction does not predict:
- REGIME population distribution (P1 FAIL: 47.8% R1 vs predicted >60%)
- k/(k+ke) ratio within sections (P2 FAIL stratified: p=0.058)
- r->a routing (P4 FAIL: p=0.315, consistent with C1724)
- MIDDLE-based apparatus profile scores within sections (598d Block 1 FAIL)

The alignment is about thermal intensity, not apparatus identity.

## Pre-Registration

Predictions locked with SHA-256 hash `ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d` before any test execution (commit 542e150).

## Key Metrics

- P3 within Stars: Mann-Whitney U=120.0, p=0.000725, n=10+13
- P5 size-controlled: partial Spearman rho=0.248, p=0.024, n=82
- Bonferroni-adjusted P3: p=0.0035 (across 5 tests), still significant

## Provenance

- Source: `phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/blind_prediction_results.json`
- Depends on: C1457 (e->y safety), C1225 (ke-depth parametricity), C1404 (section-REGIME)
- Expert-reviewed: Post-hoc corrections for REGIME grouping, section stratification, size control
