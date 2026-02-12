# C1009: AXM Exit Hazard-Target Compositional Curvature

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> AXM runs exhibit compositional curvature toward the hazard-boundary region in the final tokens before exit. HAZARD_TARGET MIDDLE density increases from ~10% at t-3 to ~16% at the exit token (rho=-0.055, p=0.0001). This is a compositional effect, not a spectral-geometric one: radial depth in the MIDDLE compatibility space shows no significant gradient toward exit (rho=-0.023, p=0.098). Exit boundaries are enriched in HAZARD_TARGET sub-role relative to mid-run positions (chi2=13.89, p=0.003).

---

## Evidence

**Script:** `phases/AXM_GATEKEEPER_INVESTIGATION/scripts/gatekeeper_analysis.py`

### Position-from-End Profiles (T8)

AXM runs of length >= 4 (n=1,016):

| Position | Depth Mean | HazTar % | Gatekeeper % | n |
|----------|-----------|----------|--------------|---|
| t-0 (exit) | 2.066 | 15.6% | 8.7% | 1,016 |
| t-1 | 2.012 | 11.8% | 2.8% | 1,016 |
| t-2 | 2.062 | 11.3% | 2.9% | 1,016 |
| t-3 | 2.025 | 9.6% | 2.1% | 1,016 |
| t-4 | 2.030 | 10.1% | 2.4% | 614 |
| t-5 | 2.030 | 10.7% | 2.5% | 354 |

### Statistical Tests

| Test | Statistic | p-value | Interpretation |
|------|-----------|---------|---------------|
| Spearman: position vs depth | rho=-0.023 | 0.098 | No depth gradient |
| Spearman: position vs hazard-target | rho=-0.055 | 0.0001 | Hazard-target INCREASES toward exit |
| Mann-Whitney: exit depth vs interior depth | U=1,068,118 | 0.007 | Borderline, no practical difference (2.066 vs 2.027) |
| Chi2: exit vs mid-run sub-role composition | chi2=13.89 | 0.003 | Different sub-role distribution at exit |

### Sub-Role Composition (T6)

| Sub-Role | Exit Boundary | Mid-Run | Direction |
|----------|--------------|---------|-----------|
| HAZARD_SOURCE | 25.9% | 28.5% | lower at exit |
| HAZARD_TARGET | 22.7% | 17.5% | HIGHER at exit |
| SAFETY_BUFFER | 32.4% | 34.7% | lower at exit |
| PURE_CONNECTOR | 18.9% | 19.2% | neutral |

HAZARD_TARGET is the only sub-role with substantial enrichment at exit boundaries.

---

## Interpretation

1. **Compositional curvature, not spectral.** The approach to AXM exit is marked by accumulating hazard-monitoring vocabulary (HAZARD_TARGET MIDDLEs), not by drifting toward a geometric boundary in the MIDDLE compatibility space. The mechanism is lexical-compositional.

2. **Connects gatekeeper to hazard architecture.** C1000 established that HUB_UNIVERSAL MIDDLEs decompose into 4 sub-roles. C1009 shows that the exit-boundary specialization specifically selects for HAZARD_TARGET tokens — linking the gating mechanism to the hazard monitoring subsystem.

3. **Gatekeeper probability spike.** The gatekeeper class fraction rises from ~2% at t-3 to 8.7% at t-0, concentrated at the final token. This is consistent with a single-token switching mechanism rather than a gradual approach.

4. **Radial depth is uninformative.** The spectral embedding geometry (C982, C991) does not predict exit behavior within AXM. The relevant structure is compositional (which sub-role appears) not geometric (where in the compatibility space).

5. **REGIME does NOT modulate curvature slope (T11).** Per-REGIME hazard-target buildup slopes show no systematic relationship with REGIME intensity (Spearman rho=+0.800, p=0.200, n=4). The curvature mechanism is REGIME-invariant in shape, consistent with a structural property rather than a contextual one. This does NOT contradict C979 (REGIME modulates weights) — REGIME modulates gatekeeper class identity (T5) but not the hazard-target accumulation rate.

6. **No micro-exit schema (T10).** The sub-role at t-1 before gatekeeper exit is indistinguishable from pre-non-gatekeeper (chi2=0.40, p=0.94). Exit bigram entropy matches baseline. There is no constrained 2-3 step motif preceding exit — the gatekeeper mechanism is a single-token boundary phenomenon.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C982 | Context: discrimination space dimensionality (spectral embedding used for depth) |
| C991 | Context: radial depth as energy predictor (NOT predictive within AXM) |
| C1000 | Connected: HUB sub-role decomposition (HAZARD_TARGET enrichment at exit) |
| C1007 | Parent: gatekeeper subset discovery |
| C979 | Tested: REGIME modulates weights but NOT curvature slope (T11) |
| C1008 | Companion: directional gating mechanism |

---

## Provenance

- **Phase:** AXM_GATEKEEPER_INVESTIGATION
- **Date:** 2026-02-12
- **Script:** gatekeeper_analysis.py (T6, T8, T10, T11)
- **Results:** `phases/AXM_GATEKEEPER_INVESTIGATION/results/gatekeeper_analysis.json`

---

## Navigation

<- [C1008_axm_directional_gating.md](C1008_axm_directional_gating.md) | [INDEX.md](INDEX.md) ->
