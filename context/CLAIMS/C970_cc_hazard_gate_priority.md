# C970: CC-Hazard Gate Priority

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> When both CC routing and hazard gating are active for the same EN token position, the hazard gate takes stochastic priority. In 22 co-occurrence cases, the lane distribution matches hazard-only profile (P(QO|both)=0.23) rather than CC-only profile. Fisher exact test p=0.36 comparing CC-only vs both-present. CC routing effect is real but subordinate to hazard intervention. BIC model selection confirms: hazard gate justifies its parameters, CC gate does not (BIC markov_haz=9166.3 < full=9198.5).

---

## Evidence

**Test:** `phases/LANE_OSCILLATION_CONTROL_LAW/scripts/t3_cc_routing_gate_estimation.py`

### CC-Hazard Interaction

| Condition | N | P(QO) | P(CHSH) |
|-----------|---|-------|---------|
| Hazard only | 345 | 24.8% | 75.2% |
| CC only | 482 | 21.4% | 78.6% |
| Both present | 22 | 22.7% | 77.3% |

Fisher exact (CC-only vs both): p=0.36. No significant difference when hazard is added.

### CC Routing Confirmation (directional, subordinate)

| CC Type | Offset +1 CHSH% | N | C817 Target | Status |
|---------|-----------------|---|-------------|--------|
| DAIIN | 78.6% | 262 | 90.8% | Directional match |
| OL | 79.6% | 108 | 93.2% | Directional match |
| OL_DERIVED | 54.3% QO | 47 | 57.4% QO | Directional match |

Lower magnitudes vs C817 due to offset definition difference (EN-count vs absolute token).

### Model Selection (T6)

CC gate adds 6 parameters (3 CC types x 2 lane probs) to markov_haz. BIC penalizes: markov_haz (9166.3) vs full (9198.5). Delta BIC = -32.2 favors simpler model. CC gate improves raw LL (0.6734 -> 0.6719 per token) but not enough to justify complexity.

---

## Interpretation

The hazard gate is the dominant contextual modifier of lane selection. CC routing operates within the residual probability space after hazard gating. This hierarchy is consistent with the system's architecture: hazard management is primary (C601, C645, C651), CC routing is a secondary nuance for initialization (C817: "CC sets initial lane, not persistent lane"). The BIC result confirms this is not just a power issue — the CC gate genuinely does not add enough predictive value beyond what the Markov + hazard model already captures.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C817 | Refined: CC routing confirmed directionally but shown subordinate to hazard |
| C645 | Related: hazard gate takes priority in combined contexts |
| C606 | Related: CC-EN routing is local mechanism |
| C966 | Context: CC gate excluded from optimal BIC model |

---

## Provenance

- **Phase:** LANE_OSCILLATION_CONTROL_LAW
- **Date:** 2026-02-10
- **Script:** t3_cc_routing_gate_estimation.py, t6_model_assembly_validation.py
- **Results:** `phases/LANE_OSCILLATION_CONTROL_LAW/results/t3_cc_routing_gate.json`, `t6_model_validation.json`

---

## Navigation

<- [C969_second_order_non_load_bearing.md](C969_second_order_non_load_bearing.md) | [INDEX.md](INDEX.md) ->
