# C1153: Generative Design Freedom Is ~40%, Consistent with C1035

**Tier:** 2
**Scope:** B, generative model, dynamics
**Phase:** SECTION_CONDITIONED_GENERATIVE_FIDELITY (Phase 411)
**Depends on:** C1016, C1035, C1055

## Statement

At the generative level, ~40% of folio-level variation is program-specific (not section-captured). This decomposes as: 32.4% uncaptured class distribution variance, 43.2% uncaptured AXM spread, 44.0% uncaptured kernel profile variance. The AXM component (43.2%) is consistent with C1035's 57% irreducible residual. The aggregate is lower than C1016's 66.3% because class distribution (the largest component by weight) is substantially section-captured.

## Evidence

| Component | Uncaptured fraction | Reference constraint |
|-----------|-------------------|---------------------|
| Class distribution (T1) | 32.4% | — |
| AXM spread (T2) | 43.2% | C1035 (57%) |
| Kernel profile (T3) | 44.0% | C1150 |
| **Aggregate** | **39.9%** | C1016 (66.3%) |

**C1035 consistency:** T2 uncaptured (43.2%) is within tolerance of C1035's 57% (different metric: SD ratio vs variance decomposition). Both confirm AXM dynamics are substantially program-specific. PASS.

**C1016 consistency:** Aggregate (39.9%) is lower than C1016's 66.3%. This is NOT a contradiction — C1016 measured macro-state transition variance (a dynamics measure, corresponding to T2/T3), while the aggregate mixes in T1 (class distribution, which IS section-captured). The metrics measure different layers.

## Interpretation

The ~40% figure is the generative lower bound on design freedom. It means: if you know what section a folio belongs to and use the section's M2 transition matrix, you still cannot predict ~40% of the folio's structural characteristics. This 40% is the "program-specific" signature — the part that makes each folio a unique operational procedure rather than a generic section representative.
