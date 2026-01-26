# C600: CC Trigger Sub-Group Selectivity

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> CC sub-groups trigger completely different EN families (chi2=129.2, p=9.6e-21). CC_DAIIN (daiin) and CC_OL (ol) both strongly avoid EN_QO (0.18x) and trigger EN_CHSH (1.60-1.74x). CC_OL_D (ol-derived, Class 17) reverses this pattern: triggers EN_QO at 1.39x and suppresses EN_CHSH at 0.77x. CC is not a uniform trigger — morphological origin predicts which EN family is activated.

---

## Evidence

**Test:** `phases/SUB_ROLE_INTERACTION/scripts/sub_role_conditioning.py`

### CC -> Operational Sub-Group Distributions

| CC Sub-Group | EN_QO | EN_CHSH | FQ_CONN | FQ_PAIR | n |
|-------------|-------|---------|---------|---------|---|
| CC_DAIIN | **0.18x** | **1.60x** | 0.63x | 1.06x | 179 |
| CC_OL | **0.18x** | **1.74x** | **1.58x** | 0.60x | 201 |
| CC_OL_D | **1.39x** | 0.77x | 0.41x | 1.25x | 137 |

### Independence Test

Chi-squared: 129.23, df=14, p=9.64e-21. Highly significant — CC sub-groups have completely different follower profiles.

### REGIME Stability

The CC->EN routing pattern is stable across all 4 REGIMEs:
- CC_OL_D->EN_QO enrichment: REGIME_1=2.83x, REGIME_2=2.89x, REGIME_3=3.19x, REGIME_4=2.22x
- CC_DAIIN->EN_QO depletion: REGIME_1=0.13x, REGIME_2=0.43x, REGIME_3=0.00x, REGIME_4=0.62x

### CC_OL Additional Pattern

CC_OL (ol) also triggers FQ_CONN at 1.58x and avoids FQ_PAIR at 0.60x. This means ol routes to both CHSH and the FQ connector, while avoiding the QO family and the FQ prefixed pair.

---

## Interpretation

CORE_CONTROL sub-groups are **differentiated triggers**:
- **daiin/ol** (Classes 10, 11): activate the ch/sh ENERGY pathway and avoid qo entirely
- **ol-derived** (Class 17, C560): activates the qo ENERGY pathway

This means the "canonical opener" daiin (C557) doesn't trigger ENERGY generically — it specifically triggers the CHSH branch. The qo branch is triggered by a different mechanism (ol-derived compounds). This may reflect that ch/sh and qo prefixes encode different processing types, with CC sub-groups acting as selectors.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C557 | Refined - daiin is not a generic ENERGY trigger but a CHSH-specific trigger |
| C560 | Extended - Class 17 ol-derived operators trigger QO specifically |
| C590 | Connected - CC positional dichotomy now extends to trigger selectivity |
| C576 | Extended - EN QO/CHSH bifurcation has upstream CC selectors |
| C598 | Instantiated - CC->EN is the strongest cross-role pair (chi2=104) |

---

## Provenance

- **Phase:** SUB_ROLE_INTERACTION
- **Date:** 2026-01-26
- **Script:** sub_role_conditioning.py

---

## Navigation

<- [C599_ax_scaffolding_routing.md](C599_ax_scaffolding_routing.md) | [INDEX.md](INDEX.md) ->
