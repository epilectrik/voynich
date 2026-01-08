# C109: 5 Hazard Failure Classes

**Tier:** 0 | **Status:** FROZEN | **Phase:** Phase 18

---

## Claim

The 17 forbidden transitions cluster into exactly 5 failure classes, representing distinct categories of operational hazard.

## The 5 Classes

| Class | Count | % | Description |
|-------|-------|---|-------------|
| PHASE_ORDERING | 7 | 41% | Material in wrong phase/location |
| COMPOSITION_JUMP | 4 | 24% | Impure fractions passing |
| CONTAINMENT_TIMING | 4 | 24% | Overflow/pressure events* |
| RATE_MISMATCH | 1 | 6% | Flow balance destroyed |
| ENERGY_OVERSHOOT | 1 | 6% | Thermal damage/scorching |

*Note: CONTAINMENT_TIMING has 0 corpus impact (theoretical-only per SEL-D)

## Evidence

- 17 forbidden transitions identified in grammar
- Cluster analysis reveals 5 natural groupings
- All 5 classes map to real physical failure modes
- 65% asymmetric (SEL-D revision)
- 59% distant from kernel (SEL-D revision)

## Hybrid Hazard Model (EXT-ECO-02)

| Type | % | Characteristic |
|------|---|----------------|
| Batch-focused | 71% | Opportunity-loss (mistimed action) |
| Apparatus-focused | 29% | Equipment protection |

Apparatus hazards have ZERO LINK nearby (faster response needed).

## Related Constraints

- C110 - PHASE_ORDERING dominant (41%)
- C111 - 65% asymmetric
- C112 - 59% distant from kernel
- C216 - Hybrid hazard model

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
