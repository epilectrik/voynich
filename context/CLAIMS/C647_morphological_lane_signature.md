# C647: Morphological Lane Signature

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> QO EN tokens contain k (ENERGY_MODULATOR) in their MIDDLEs at 70.7%; CHSH EN tokens contain e (STABILITY_ANCHOR) in their MIDDLEs at 68.7% (chi2 = 2689.7, p < 0.0001, Cramer's V = 0.654). This massive discrimination is a MIDDLE-level morphological signature, not a positional or contextual effect. The two lanes are built from different kernel-character vocabularies.

---

## Evidence

**Test:** `phases/LANE_CHANGE_HOLD_ANALYSIS/scripts/change_hold_validation.py` Section 2, Test B

### Kernel Character Content in EN Token MIDDLEs

| Character | QO (n=3192) | CHSH (n=3948) |
|-----------|-------------|---------------|
| k (ENERGY_MODULATOR) | 2,257 (70.7%) | 524 (13.3%) |
| h (PHASE_MANAGER) | 235 (7.4%) | 48 (1.2%) |
| e (STABILITY_ANCHOR) | 516 (16.2%) | 2,711 (68.7%) |

Chi-squared = 2689.7, p < 0.0001, Cramer's V = 0.654.

### Contrast: CC Token Proximity (No Discrimination)

Nearest CC (CORE_CONTROL) token to each EN token shows NO lane discrimination:

| Kernel | QO | CHSH |
|--------|-----|------|
| k | 56.5% | 56.1% |
| h | 43.5% | 43.9% |
| e | 0.0% | 0.0% |

Chi2 = 0.023, p = 0.879. No e-kernel CC tokens exist in the data.

The lane discrimination is INTERNAL to the EN token vocabulary (MIDDLE content), not about proximity to external kernel-bearing tokens.

---

## Interpretation

The two lanes are morphologically distinct at the MIDDLE level:
- QO = k-rich vocabulary (energy modulation characters)
- CHSH = e-rich vocabulary (stability anchor characters)

Per C522 (construction-execution independence, r = -0.21), MIDDLE character content reflects construction-layer vocabulary assignment, not execution-layer behavior. The lanes inherit their kernel-character composition from their PP MIDDLE ancestry (C646 shows QO-enriched PP MIDDLEs are k/t-based; CHSH-enriched are o-based).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C521 | Context: kernel one-way valve (e->h blocked, h->e elevated) |
| C522 | Critical: construction-execution independence means MIDDLE content != execution behavior |
| C576 | Extended: vocabulary bifurcation now has specific kernel-character basis |
| C646 | Upstream: PP-lane discrimination in A shows same k/t vs o pattern |
| C601 | Related: QO's k-rich vocabulary with zero hazard = controlled energy application |

---

## Provenance

- **Phase:** LANE_CHANGE_HOLD_ANALYSIS
- **Date:** 2026-01-26
- **Script:** change_hold_validation.py (Section 2)

---

## Navigation

<- [C646_pp_lane_middle_discrimination.md](C646_pp_lane_middle_discrimination.md) | [INDEX.md](INDEX.md) ->
