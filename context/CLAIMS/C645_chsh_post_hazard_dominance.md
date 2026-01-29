# C645: CHSH Post-Hazard Dominance

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> CHSH tokens dominate post-hazard positions: 75.2% of EN tokens immediately following hazard-class tokens are CHSH, vs 44.7% base CHSH rate. QO is depleted after hazards (enrichment = 0.55x, binomial p = 1.0 for QO > base). CHSH is also marginally closer to hazard tokens within lines (mean distance 3.81 vs QO 3.82, p = 0.002, r = 0.072).

---

## Evidence

**Test:** `phases/LANE_CHANGE_HOLD_ANALYSIS/scripts/change_hold_validation.py` Sections 4 & 5

### Post-Hazard EN Distribution

| Lane | Post-Hazard Count | Post-Hazard Rate | Base Rate |
|------|-------------------|-----------------|-----------|
| QO | 125 | 24.8% | 44.7% |
| CHSH | 379 | 75.2% | 55.3% |

QO enrichment after hazard = 0.55x (depleted). CHSH enrichment = 1.36x.

### Hazard Proximity

| Lane | Mean Distance | Median | N |
|------|---------------|--------|---|
| QO | 3.82 | 3.0 | 855 |
| CHSH | 3.81 | 3.0 | 1,229 |

Mann-Whitney p = 0.002, rank-biserial r = 0.072. Within 2 tokens of hazard: QO = 37.1%, CHSH = 42.2%.

### Convergence Association

QO rate in convergent (STATE-C) lines = 46.1% vs non-convergent = 44.1% (Fisher p = 0.129, not significant).

---

## Interpretation

CHSH tokens are preferentially deployed near and after hazard-class tokens. Combined with C601 (QO = 0/19 hazard participation), this establishes a clear functional division: CHSH operates in and recovers from hazard-adjacent contexts; QO operates in hazard-distant contexts. This extends C601 from a binary participation fact to a continuous proximity gradient.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C601 | Extended: QO's zero hazard participation now shown as depletion gradient |
| C105 | Related: e-kernel (STABILITY_ANCHOR) dominates recovery; CHSH MIDDLEs are 68.7% e-content |
| C643 | Context: rapid QO-CHSH alternation places CHSH near hazard through oscillation |
| C395 | Supports: dual control strategy deploys different resources near vs away from hazard |

---

## Provenance

- **Phase:** LANE_CHANGE_HOLD_ANALYSIS
- **Date:** 2026-01-26
- **Script:** change_hold_validation.py (Sections 4, 5)

---

## Navigation

<- [C644_qo_transition_stability.md](C644_qo_transition_stability.md) | [INDEX.md](INDEX.md) ->
