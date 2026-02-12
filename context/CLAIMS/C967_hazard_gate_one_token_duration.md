# C967: Hazard Gate Duration Is Exactly One Token

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Post-hazard CHSH dominance (75.2%, C645) decays to baseline within exactly 1 EN token. KL divergence drops from 0.098 at offset +1 to 0.0005 at offset +2. Chi-squared significance: offset +1 p<1e-21, offset +2 p=0.58 (not significant). No class 7 vs class 30 differentiation (pooled Fisher p=0.728). The hazard gate is a fixed 1-step deterministic function, not a decaying influence.

---

## Evidence

**Test:** `phases/LANE_OSCILLATION_CONTROL_LAW/scripts/t2_hazard_gate_estimation.py`

### Gate Profile (offset from hazard token, EN-count)

| Offset | N | CHSH% | KL vs baseline | Cramer's V | Chi2 p |
|--------|---|-------|----------------|------------|--------|
| +1 | 504 | 75.2% | 0.098 | 0.43 | <1e-21 |
| +2 | 431 | 53.9% | 0.0005 | 0.002 | 0.58 |
| +3 | 360 | 54.2% | 0.0008 | 0.004 | 0.46 |
| +4 | 290 | 55.2% | 0.003 | 0.009 | 0.29 |
| +5 | 233 | 53.2% | 0.0002 | 0.002 | 0.74 |

Baseline CHSH rate: 53.7%.

### Class Invariance

| Hazard Class | Offset +1 CHSH% | N |
|-------------|-----------------|---|
| Class 7 | 75.8% | 330 |
| Class 30 | 73.6% | 174 |
| Fisher p | 0.728 | |

Pooled offsets 1-3: p=0.41. No differentiation at any offset.

---

## Interpretation

The hazard gate operates as a single-step override: one EN token after a hazard-class token, P(CHSH) jumps to 75.2%, then immediately returns to base Markov. This is not gradual dampening or exponential decay. It is a discrete, 1-token pulse. The class invariance confirms that all hazard tokens trigger identical recovery dynamics regardless of hazard sub-type. Combined with C651 (median 1.0 CHSH before QO return), this establishes recovery as a fixed-length grammatical operation.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C645 | Independently replicated: 75.2% CHSH post-hazard |
| C651 | Confirmed: median 1.0 CHSH tokens before QO return |
| C601 | Extended: QO zero hazard participation now characterized as gate mechanism |
| C966 | Context: hazard gate is one of two components in optimal model |

---

## Provenance

- **Phase:** LANE_OSCILLATION_CONTROL_LAW
- **Date:** 2026-02-10
- **Script:** t2_hazard_gate_estimation.py
- **Results:** `phases/LANE_OSCILLATION_CONTROL_LAW/results/t2_hazard_gate.json`

---

## Navigation

<- [C966_lane_oscillation_first_order_sufficiency.md](C966_lane_oscillation_first_order_sufficiency.md) | [INDEX.md](INDEX.md) ->
