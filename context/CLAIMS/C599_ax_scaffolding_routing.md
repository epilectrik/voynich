# C599: AX Scaffolding Routing

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> AX sub-positions route to different operational sub-groups (chi2=48.3, p=3.9e-4). AX_FINAL avoids EN_QO (0.59x) and preferentially feeds FQ_CONN (1.31x). AX_MED shows slight QO preference (1.10x) and avoids FQ_CONN (0.81x). AX is not a neutral positional frame — sub-position predicts which operational sub-group follows.

---

## Evidence

**Test:** `phases/SUB_ROLE_INTERACTION/scripts/sub_role_conditioning.py`

### AX -> First Operational Token

| AX Sub-Group | EN_QO | EN_CHSH | FQ_CONN | FQ_PAIR | FL_HAZ | n |
|-------------|-------|---------|---------|---------|--------|---|
| AX_INIT | 0.96x | 1.05x | 1.23x | 0.84x | 0.96x | 955 |
| AX_MED | 1.10x | 0.96x | 0.81x | 1.11x | 0.96x | 1660 |
| AX_FINAL | **0.59x** | 1.09x | **1.31x** | 0.93x | 1.29x | 326 |

### AX Routing Independence

Chi-squared: 48.27, df=20, p=3.90e-4. Significant — AX sub-groups route differently.

### REGIME Independence of AX->FQ

AX->FQ routing is REGIME-independent (homogeneity chi2=16.7, p=0.86). The AX_INIT->FQ_CONN preference (1.57x in direct adjacency, 1.23x to first operational) holds regardless of thermal/flow context. This is structural routing, not REGIME-modulated.

---

## Interpretation

AX scaffolding is a **routing mechanism**, not a uniform frame:
- AX_FINAL closes the scaffold and feeds into the connector/boundary sub-groups (FQ_CONN, FL_HAZ) while avoiding QO — suggesting AX_FINAL prepares for a structural reset
- AX_MED, the neutral scaffold body, shows weak QO preference — consistent with QO's medial, content-carrying function
- AX_INIT, the opener, shows slight FQ_CONN preference — consistent with connector's role in initiating sequences

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C563 | Extended - AX positional stratification now shown to have routing consequences |
| C565 | Refined - AX scaffold function is not passive but routing-specific |
| C593 | Connected - FQ CONNECTOR receives preferentially from AX_INIT/FINAL |
| C598 | Instantiated - AX->EN and AX->FQ are both Bonferroni-significant |

---

## Provenance

- **Phase:** SUB_ROLE_INTERACTION
- **Date:** 2026-01-26
- **Script:** sub_role_conditioning.py

---

## Navigation

<- [C598_cross_boundary_subgroup_structure.md](C598_cross_boundary_subgroup_structure.md) | [INDEX.md](INDEX.md) ->
