# C1008: AXM Directional Gating Mechanism

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> AXM runs exhibit directional gating: entry and exit boundaries have statistically different class compositions (chi2=152.60, p<0.0001). Five AUXILIARY classes {15, 20, 21, 22, 25} are 2-10x enriched at exit boundaries but NOT at entry boundaries. Gatekeepers have lower transition entropy than non-gatekeeper AXM classes (4.123 vs 4.555 bits, p=0.016), making them constrained exit points. This is a genuine structural effect that survives mid-line positional control (chi2=58.42, p=0.002) and is not a line-boundary artifact.

---

## Evidence

**Script:** `phases/AXM_GATEKEEPER_INVESTIGATION/scripts/gatekeeper_analysis.py`

### Entry vs Exit Asymmetry (T1)

Enrichment ratios for gatekeeper classes at entry vs exit boundaries (runs >= 3, n=1,633):

| Class | Entry Enrichment | Exit Enrichment | Role |
|-------|-----------------|-----------------|------|
| 15 | 0.51x | 3.08x | AX_INIT |
| 20 | 1.60x | 2.68x | AX_FINAL |
| 21 | 0.44x | 4.25x | AX_FINAL |
| 22 | 0.96x | 9.58x | AX_FINAL |
| 25 | 0.18x | 2.30x | AX_FINAL |

Chi2 (entry vs exit class distribution): 152.60, p<0.0001, dof=31.

### Positional Control (T3)

Mid-line exits (n=961) retain gatekeeper enrichment (chi2=58.42, p=0.002). Line-end exits show higher enrichment but mid-line exits are independently significant.

Mean normalized line position: gatekeeper=0.668, non-gatekeeper=0.471 (p<0.0001). Gatekeepers occur later in lines, consistent with exit function.

### Transition Entropy (T7)

| Metric | Gatekeeper Classes | Non-Gatekeeper AXM |
|--------|-------------------|-------------------|
| Mean entropy | 4.123 bits | 4.555 bits |
| Mann-Whitney p | 0.016 | - |

Lower entropy = more constrained successor distribution = routing switches with fewer exit paths.

### Negative Results (Architectural Constraints)

| Test | Finding | p-value |
|------|---------|---------|
| T2: Exit routing | No target-state specificity | 0.286 |
| T4: Duration prediction | Gatekeeper identity does not predict run length | 0.128 |
| T5: REGIME invariance | Pattern varies by REGIME (2/4 significant) | mixed |
| T9: Betweenness centrality | Gatekeepers are NOT structural bridges | 0.514 |

Gatekeepers are peripheral exit-specialists, not central routing hubs.

---

## Interpretation

1. **Exit-specific mechanism.** Entry and exit use different class subsets. The grammar has an asymmetric boundary structure within AXM.

2. **Constrained exit, unconstrained routing.** Gatekeepers constrain WHICH classes can appear at the boundary but are agnostic about WHERE the exit goes (T2 null). The gating is about leaving AXM, not about choosing a destination.

3. **Not structural bridges.** Low betweenness centrality (T9) confirms gatekeepers occupy the periphery of the AXM internal transition graph — they are endpoints, not connectors.

4. **REGIME-contextual.** The specific gatekeeper class identity shifts across REGIMEs (mean cross-rho = -0.245), suggesting the grammar adapts which classes serve as exits depending on operational context. The mechanism exists in all REGIMEs but uses different participants.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C976 | Context: 6-state topology defines AXM |
| C977 | Context: S3/S4 internal asymmetry within AXM |
| C979 | Connected: REGIME modulates weights (gatekeeper identity is REGIME-contextual) |
| C1000 | Connected: gatekeeper classes are AUXILIARY, mapped to HUB sub-roles |
| C1006 | Context: topology artifact (dwell), but internal structure is real |
| C1007 | Parent: gatekeeper subset discovery |
| C1009 | Companion: compositional curvature toward hazard boundary at exit |

---

## Provenance

- **Phase:** AXM_GATEKEEPER_INVESTIGATION
- **Date:** 2026-02-12
- **Script:** gatekeeper_analysis.py (T1, T3, T7, T2, T4, T5, T9)
- **Results:** `phases/AXM_GATEKEEPER_INVESTIGATION/results/gatekeeper_analysis.json`

---

## Navigation

<- [C1007_axm_gatekeeper_subset.md](C1007_axm_gatekeeper_subset.md) | [C1009_axm_exit_hazard_curvature.md](C1009_axm_exit_hazard_curvature.md) ->
