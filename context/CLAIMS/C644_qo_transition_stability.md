# C644: QO Transition Stability Advantage

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> QO tokens appear in more stable grammatical contexts than CHSH tokens. QO mean context stability = 0.318 vs CHSH = 0.278 (Mann-Whitney p = 0.0006, r = -0.039). QO transition entropy = 4.08 vs CHSH = 4.51.

---

## Evidence

**Test:** `phases/LANE_CHANGE_HOLD_ANALYSIS/scripts/change_hold_validation.py` Section 3

### Context Stability Score

For each EN token at position i in a line, stability = 1 if the instruction class at i-1 equals the class at i+1, else 0. Higher values = more predictable surrounding context.

| Lane | Mean Stability | N |
|------|---------------|---|
| QO | 0.318 | 2,797 |
| CHSH | 0.278 | 3,649 |

Mann-Whitney U: p = 0.0006, rank-biserial r = -0.039

### Transition Entropy

Shannon entropy of the (prev_role -> next_role) distribution for tokens of each lane.

| Lane | Entropy (bits) |
|------|---------------|
| QO | 4.08 |
| CHSH | 4.51 |

QO operates in lower-entropy (more predictable) grammatical neighborhoods.

### Effect Size

The effect size is small (r = 0.039) but statistically significant. This is a distributional tendency, not a categorical difference.

---

## Interpretation

QO tokens occupy more predictable grammatical positions. This is consistent with QO serving a routine/regular function (controlled energy application) while CHSH responds to variable conditions (stabilization/correction after disturbance).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C574 | Refines: successor distributions near-identical (JS=0.0024), but self-transition stability differs |
| C601 | Consistent: QO avoids hazards -> more stable contexts |
| C643 | Related: QO exits faster (60%), implying briefer presence in any context |

---

## Provenance

- **Phase:** LANE_CHANGE_HOLD_ANALYSIS
- **Date:** 2026-01-26
- **Script:** change_hold_validation.py (Section 3)

---

## Navigation

<- [C643_lane_hysteresis_oscillation.md](C643_lane_hysteresis_oscillation.md) | [INDEX.md](INDEX.md) ->
