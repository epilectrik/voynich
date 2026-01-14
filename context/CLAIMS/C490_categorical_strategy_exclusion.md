# C490: Categorical Strategy Exclusion

**Tier:** 2
**Scope:** B
**Status:** CLOSED
**Source:** STRUCTURAL_TOPOLOGY_TESTS

---

## Statement

Some Currier B programs impose *categorical strategy exclusion*: for at least 20.5% of folios, no grammar-compatible realization of the AGGRESSIVE strategy exists. Strategy admissibility is not continuous or preference-based but may be structurally forbidden.

---

## Evidence

### Archetype-Strategy Compatibility Matrix

| Archetype | Count | AGGRESSIVE Compatibility |
|-----------|-------|--------------------------|
| AGGRESSIVE_INTERVENTION | 6 | 0.67 |
| MIXED | 50 | 0.36 |
| ENERGY_INTENSIVE | 10 | 0.63 |
| CONSERVATIVE_WAITING | **17** | **0.000** |

### Statistical Verification

- **17/83 folios (20.5%)** have exactly zero AGGRESSIVE compatibility
- Chi-square for archetype × AGGRESSIVE viability: p < 0.0001
- Perfect separation: 0 overlap between forbidden and permitted groups

### Defining Threshold

Programs with `link_density > 0.404` categorically exclude AGGRESSIVE strategy.

---

## Structural Interpretation

This constraint establishes that strategy admissibility is a **legality property**, not a **preference gradient**:

- Some strategies are grammatically impossible, not just inadvisable
- The prohibition is categorical (0.000), not asymptotic
- The boundary is defined by grammar features (link_density threshold)

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C458 | Strengthens: design clamp includes strategy exclusion |
| C488 | Sharpens: correlation becomes prohibition at boundary |
| C485 | Aligns: grammar minimality includes forbidden configurations |

---

## Historical Parallel

Matches Brunschwig's "4th degree fire" - explicitly FORBIDDEN, not merely inadvisable. Medieval distillation sources distinguished between degrees of appropriateness and categorical prohibition.

---

## Epistemic Note

This constraint is expressed entirely in grammar space (strategy compatibility scores derived from instruction patterns). No semantic content is implied.
