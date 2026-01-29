# C646: PP-Lane MIDDLE Discrimination

**Tier:** 2 | **Status:** CLOSED | **Scope:** A/B

---

## Statement

> 20 of 99 testable PP MIDDLEs significantly predict QO vs CHSH lane preference at FDR < 0.05 (permutation z = 24.26, p < 0.0001). 15 are QO-enriched, 5 are CHSH-enriched. QO-enriched MIDDLEs are k/t-based ENERGY_OPERATOR role (11/15); CHSH-enriched MIDDLEs are o-based AUXILIARY role (3/5). No obligatory lane-exclusive slots exist.

---

## Evidence

**Test:** `phases/LANE_CHANGE_HOLD_ANALYSIS/scripts/lane_pp_discrimination.py`

### Test Parameters

- 404 PP MIDDLEs from A_INTERNAL_STRATIFICATION
- 99 tested (>= 10 records containing MIDDLE); 305 skipped
- Point-biserial correlation of MIDDLE presence with continuous qo_prefix_frac
- Benjamini-Hochberg FDR correction
- 10,000 permutation null: mean 0.64 significant (std 0.80, max 6)
- Observed: 20 significant. z = 24.26.

### Top Discriminators

**QO-enriched (positive r):**

| MIDDLE | r | FDR | Material | EN Subfamily | B Role |
|--------|---|-----|----------|-------------|--------|
| k | 0.346 | <0.001 | MIXED | MIXED_EN | ENERGY_OPERATOR |
| tc | 0.224 | <0.001 | HERB | QO | ENERGY_OPERATOR |
| kc | 0.203 | <0.001 | HERB | QO | ENERGY_OPERATOR |
| t | 0.199 | <0.001 | MIXED | QO | ENERGY_OPERATOR |
| kch | 0.153 | <0.001 | ANIMAL | QO | ENERGY_OPERATOR |

**CHSH-enriched (negative r):**

| MIDDLE | r | FDR | Material | EN Subfamily | B Role |
|--------|---|-----|----------|-------------|--------|
| o | -0.140 | <0.001 | HERB | CHSH | AUXILIARY |
| ol | -0.130 | <0.001 | MIXED | CHSH | AUXILIARY |
| or | -0.105 | <0.001 | MIXED | CHSH | AUXILIARY |
| e | -0.087 | 0.007 | MIXED | CHSH | ENERGY_OPERATOR |
| ot | -0.077 | 0.020 | HERB | CHSH | ENERGY_OPERATOR |

### EN Association Caveat

17 of 20 discriminators have EN subfamily associations. Since EN subfamilies are DEFINED by QO/CHSH prefix (C570-C571), EN-associated MIDDLEs discriminating by lane is partially tautological. The 3 non-EN discriminators (g, kcho, ko — all QO-enriched) represent the genuinely novel finding: lane discrimination leaks beyond EN into other roles.

### Obligatory Slot Analysis

No MIDDLE achieves > 80% presence in one extreme quartile and < 20% in the other. One strong differential: k (Q1=4.4%, Q4=39.1%). Lane discrimination is probabilistic, not categorical.

### Role and Material Patterns

- QO-enriched: 11/15 ENERGY_OPERATOR, 12/15 AZC-Mediated
- CHSH-enriched: 3/5 AUXILIARY, 5/5 AZC-Mediated
- QO-enriched: k/t-based character pattern (energy modulation)
- CHSH-enriched: o-based character pattern (auxiliary/stabilization)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C576 | Extended: vocabulary bifurcation has systematic character pattern (k/t vs o) |
| C575 | Context: EN 100% pipeline-derived, so PP discrimination IS the pipeline |
| C642 | Related: A-record architecture predicts B behavior |
| C647 | Related: morphological lane signature at B-side confirms A-side pattern |

---

## Provenance

- **Phase:** LANE_CHANGE_HOLD_ANALYSIS
- **Date:** 2026-01-26
- **Script:** lane_pp_discrimination.py

---

## Navigation

<- [C645_chsh_post_hazard_dominance.md](C645_chsh_post_hazard_dominance.md) | [INDEX.md](INDEX.md) ->
