# C1007: AXM Exit-Boundary Gatekeeper Subset

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The 32-class AXM macro-state contains a gatekeeper subset: instruction classes {15, 20, 21, 22, 25} are significantly enriched at run exit boundaries relative to mid-run positions (chi2=178.21, p<0.0001). All 5 are AUXILIARY (AX role). Classes 22, 21, and 15 show 3-10x enrichment. AXM exits primarily to FQ (57.1%) and enters from FQ (55.1%), establishing FQ as the principal interchange state.

---

## Evidence

**Discovery:** `phases/REGIME_DWELL_ARCHITECTURE/scripts/dwell_architecture.py` (T8)
**Full investigation:** `phases/AXM_GATEKEEPER_INVESTIGATION/scripts/gatekeeper_analysis.py` (T1-T9)

### Exit Skyline

AXM exits to (n=2,847 observed exits):

| Target State | Count | Fraction |
|-------------|-------|----------|
| FQ | 1,627 | 57.1% |
| FL_HAZ | 488 | 17.1% |
| CC | 393 | 13.8% |
| AXm | 268 | 9.4% |
| FL_SAFE | 71 | 2.5% |

### Entry Skyline

AXM enters from (n=2,579 observed entries):

| Source State | Count | Fraction |
|-------------|-------|----------|
| FQ | 1,420 | 55.1% |
| FL_HAZ | 431 | 16.7% |
| CC | 424 | 16.4% |
| AXm | 274 | 10.6% |
| FL_SAFE | 30 | 1.2% |

### Boundary Class Enrichment

Classes at AXM run exit boundaries vs mid-run positions (runs length >= 3):

| Class | Boundary Fraction | Mid-Run Fraction | Enrichment |
|-------|------------------|------------------|------------|
| 22 | 0.012 | 0.001 | 9.58x |
| 21 | 0.024 | 0.006 | 4.25x |
| 15 | 0.011 | 0.004 | 3.08x |
| 20 | 0.029 | 0.011 | 2.68x |
| 25 | 0.015 | 0.007 | 2.30x |

Chi2 test (exit-boundary vs mid-run distribution): chi2=178.21, p<0.0001.

### Phase 327 Characterization (9 tests)

| Test | Result | p-value |
|------|--------|---------|
| T1: Entry/exit asymmetry | DETECTED (directional) | <0.0001 |
| T2: Exit routing specificity | NOT DETECTED | 0.286 |
| T3: Mid-line positional control | GENUINE (survives control) | 0.002 |
| T4: Duration prediction | NO | 0.128 |
| T5: REGIME invariance | Variable (2/4 significant) | mixed |
| T6: HUB sub-role enrichment | YES (HAZARD_TARGET at exit) | 0.003 |
| T7: Transition entropy | LOWER (routing switches) | 0.016 |
| T8: Radial depth gradient | NO depth curvature | 0.098 |
| T9: Betweenness centrality | NOT higher | 0.514 |

---

## Interpretation

1. **Directional gating.** Entry and exit boundaries have different class composition (chi2=152.60). Gatekeepers are exit-specific, not symmetric boundary markers.

2. **Genuine structural effect.** Gatekeeper enrichment survives mid-line positional control (T3) — not a line-boundary artifact.

3. **Exit choke points, not routing switches.** Gatekeepers do not preferentially route to specific target states (T2) but do have lower transition entropy (T7) — they constrain which classes can appear at the exit while being agnostic about destination.

4. **HAZARD_TARGET enrichment.** Exit boundaries are enriched in the HAZARD_TARGET sub-role (C1000), linking the gatekeeper mechanism to hazard architecture. See C1009.

5. **FQ as principal interchange.** AXM-FQ channel is dominant circulation pathway (57.1% exits, 55.1% entries).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C976 | Context: 6-state topology (AXM = 32-class hub) |
| C977 | Context: S3/S4 internal structure (24.4x directional asymmetry) |
| C1000 | Connected: HUB sub-role decomposition (HAZARD_TARGET at exit) |
| C1006 | Context: non-geometric dwell is topology artifact, but internal structure is real |
| C1008 | Extension: directional gating mechanism |
| C1009 | Extension: compositional curvature toward hazard boundary |

---

## Provenance

- **Phase:** REGIME_DWELL_ARCHITECTURE (discovery), AXM_GATEKEEPER_INVESTIGATION (full characterization)
- **Date:** 2026-02-12
- **Scripts:** dwell_architecture.py (T8), gatekeeper_analysis.py (T1-T9)
- **Results:** `phases/AXM_GATEKEEPER_INVESTIGATION/results/gatekeeper_analysis.json`

---

## Navigation

<- [C1006_dwell_topology_artifact.md](C1006_dwell_topology_artifact.md) | [C1008_axm_directional_gating.md](C1008_axm_directional_gating.md) ->
