# C1007: AXM Exit-Boundary Gatekeeper Subset

**Tier:** 2 | **Status:** OPEN (motivates further investigation) | **Scope:** B

---

## Statement

> The 32-class AXM macro-state contains a gatekeeper subset: specific instruction classes are significantly enriched at run exit boundaries relative to mid-run positions (chi2=178.21, p<0.0001). Classes 22, 21, and 15 show 3-10x enrichment at exit boundaries. AXM exits primarily to FQ (57.1%) and enters primarily from FQ (55.1%), establishing FQ as the principal interchange state.

---

## Evidence

**Test:** `phases/REGIME_DWELL_ARCHITECTURE/scripts/dwell_architecture.py` (T8)

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

Chi2 test (exit-boundary vs mid-run distribution): chi2=178.21, p<0.0001. The exit-boundary class distribution is strongly different from mid-run.

---

## Interpretation

1. **AXM is not internally homogeneous.** The 32 classes are not interchangeable — specific classes preferentially occupy run boundaries, suggesting internal functional differentiation.

2. **Connects to C1000.** The HUB_ROLE_DECOMPOSITION (C1000) classified HUB_UNIVERSAL MIDDLEs into 4 sub-roles: HAZARD_SOURCE, HAZARD_TARGET, SAFETY_BUFFER, PURE_CONNECTOR. If the gatekeeper classes correspond to specific sub-roles, AXM has internal zoning.

3. **FQ as principal interchange.** AXM exits to FQ 57.1% of the time and enters from FQ 55.1%. The AXM-FQ channel is the dominant circulation pathway in the 6-state automaton.

4. **Motivates dedicated investigation.** Which instruction classes are gatekeepers? Do they correspond to known sub-roles (C1000)? Is there a systematic entry/exit asymmetry? Does the gatekeeper identity vary by REGIME?

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C976 | Context: 6-state topology (AXM = 32-class hub) |
| C977 | Context: S3/S4 internal structure (24.4x directional asymmetry) |
| C1000 | Potentially related: HUB sub-role decomposition |
| C1006 | Context: non-geometric dwell is topology artifact, but internal structure is real |

---

## Provenance

- **Phase:** REGIME_DWELL_ARCHITECTURE
- **Date:** 2026-02-12
- **Script:** dwell_architecture.py (T8)
- **Results:** `phases/REGIME_DWELL_ARCHITECTURE/results/dwell_architecture.json`

---

## Navigation

<- [C1006_dwell_topology_artifact.md](C1006_dwell_topology_artifact.md) | [INDEX.md](INDEX.md) ->
