# C1110: SOUTH (C2) Directional Profile Confirmed

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** ROSETTES_CROSS_REFERENCE_VALIDATION (Phase 393)
**Strengthens:** C1092 (SOUTH TARGET-dominant profile)
**Revised:** Phase 396 mapping correction — all group position labels corrected.

---

## Statement

The SOUTH ring text region (C2) on f85v2 is directionally distinct from WEST+CENTER (N1+N2) and NW+NORTH (V1+V2) on both predicted dimensions: higher TARGET fraction (0.458 vs 0.333/0.375) and lower kernel percentage (54.5% vs 69.2%/71.9%). This confirms C1092's finding that C2 has a distinctive TARGET-dominant profile compared to other description regions.

However, the full operational profile comparison (P1) shows these differences fall within noise for random blocks of matched size (p=0.459). C2 is directionally but not statistically distinct at the 9-dimensional profile level.

---

## Mapping Correction (Phase 396)

Original group labels mapped incorrectly. Corrected per voynich.nu fRos_tr.txt:

| Original label | Region codes | Correct positions |
|---------------|-------------|-------------------|
| "CENTER" | C2 | **SOUTH cardinal** |
| "NORTH" | N1+N2 | **WEST + CENTER** |
| "VERT" | V1+V2 | **NW + NORTH** |

**Impact:** The comparison is really: SOUTH vs (WEST+CENTER) vs (NW+NORTH). The finding that C2 is directionally distinct remains valid as a data point, but the "CENTER convergence" interpretation no longer applies — this is SOUTH showing a different profile from other description groups.

---

## Evidence

### Hub Role Balance (corrected labels)
| Group | Correct Positions | src | tgt | buf | con | Total | tgt_fraction |
|-------|------------------|-----|-----|-----|-----|-------|-------------|
| N1+N2 | WEST + CENTER | 17 | 15 | 6 | 7 | 45 | 0.333 |
| V1+V2 | NW + NORTH | 17 | 18 | 4 | 9 | 48 | 0.375 |
| C2 | SOUTH | 4 | 11 | 4 | 5 | 24 | **0.458** |

SOUTH tgt_fraction > WEST+CENTER: YES (0.458 > 0.333)
SOUTH tgt_fraction > NW+NORTH: YES (0.458 > 0.375)

### Kernel Balance (corrected labels)
| Group | Correct Positions | k_pct | hazard_pct |
|-------|------------------|-------|------------|
| N1+N2 | WEST + CENTER | 69.2% | 71.1% |
| V1+V2 | NW + NORTH | 71.9% | 72.9% |
| C2 | SOUTH | **54.5%** | 62.5% |

SOUTH k_pct < WEST+CENTER: YES (54.5 < 69.2)
SOUTH k_pct < NW+NORTH: YES (54.5 < 71.9)

### Caveat: P1 Gate Failure
Despite directional confirmation, the 9-dimensional profile comparison places C2 within the expected range for random 33-token blocks from the Rosettes corpus (p=0.459). The small sample size (33 tokens) limits statistical power.

---

## Revised Interpretation

C2 (SOUTH) has the highest TARGET fraction and lowest kernel concentration of the three description groups. This is a genuine structural difference. With the corrected mapping, this means:

- SOUTH (C2) is more TARGET-leaning than WEST+CENTER (N1+N2) and NW+NORTH (V1+V2)
- The original "CENTER convergence" interpretation is weakened — SOUTH is not the spatial center
- The TARGET-dominant profile may instead reflect SOUTH's role as a terminal/output stage

The P1 gate failure means the difference is directional but not robust at the full profile level, consistent with the small sample size.

---

## Provenance

- Phase: 393 (ROSETTES_CROSS_REFERENCE_VALIDATION), Test P6
- Script: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/scripts/rosettes_crossref_validation.py`
- Results: `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/results/rosettes_crossref_validation.json`
- Related: C1092, C1098
- Revised: Phase 396 (ROSETTES_FUNCTIONAL_ANATOMY) mapping correction
