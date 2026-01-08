# Phase OPS-4: Decision Model Summary

**Date:** 2026-01-04

---

## 1. Executive Summary

This document describes a **non-semantic operator decision model** derived from operational
pressures (OPS-1 through OPS-3). The model explains regime transitions as responses to
accumulated pressure gradients, NOT as deliberate choices or goal-directed behavior.

**Key findings:**
- 9 pressure-induced transition pathways identified
- 3 prohibited/unsupported transitions
- REGIME_3 (dominated) serves as transient throughput state
- Conservative stabilization paths always available

---

## 2. Pressure Signal Definitions

### 2.1 Time Pressure

Derived from:
- High `loops_until_state_c` (slow convergence)
- Low `convergence_speed_index` (inefficient progression)
- Short `mean_link_run_length` (insufficient waiting)

**Interpretation:** Accumulated time pressure creates gradient toward faster regimes.

### 2.2 Risk Pressure

Derived from:
- High `hazard_density` (proximity to forbidden transitions)
- High `aggressiveness_score` (operating near boundaries)
- High `kernel_contact_ratio` (frequent boundary contact)
- High `near_miss_count` (accumulated close calls)

**Interpretation:** Accumulated risk pressure creates gradient toward safer regimes.

### 2.3 Stability Pressure

Derived from:
- Low `control_margin_index` (narrow operating margin)
- Low `conservatism_score` (aggressive posture)
- Non-restart-capable status (no recovery option)
- Low `recovery_ops_count` (limited recovery capacity)

**Interpretation:** Accumulated stability pressure creates gradient toward resilient regimes.

---

## 3. Regime Pressure Profiles (Summary)

| Regime | Time | Risk | Stability | N |
|--------|------|------|-----------|---|
| REGIME_1 | 0.678 | 0.608 | 0.601 | 31 |
| REGIME_2 | 0.433 | 0.189 | 0.345 | 11 |
| REGIME_3 | 0.278 | 0.692 | 0.736 | 16 |
| REGIME_4 | 0.140 | 0.409 | 0.483 | 25 |

*Higher values indicate more pressure (unfavorable condition).*

---

## 4. Regime Switching Pressure Map

### 4.1 Favorable Transitions (Net Pressure Relief)

| From | To | Weight | Primary Driver |
|------|-----|--------|----------------|
| REGIME_1 | REGIME_2 | 0.919 | time pressure relief (gradient=0.245) |
| REGIME_3 | REGIME_2 | 0.895 | risk pressure relief (gradient=0.503) |
| REGIME_1 | REGIME_4 | 0.855 | time pressure relief (gradient=0.537) |
| REGIME_3 | REGIME_4 | 0.675 | time pressure relief (gradient=0.137) |
| REGIME_4 | REGIME_2 | 0.357 | risk pressure relief (gradient=0.219) |
| REGIME_3 | REGIME_1 | 0.220 | risk pressure relief (gradient=0.084) |

### 4.2 Transition Type Distribution

- **enter_dominated_transient**: 2 transitions
- **exit_dominated**: 3 transitions
- **pareto_tradeoff**: 4 transitions

---

## 5. Dominated Regime Justification (REGIME_3)

**Pareto Status:** DOMINATED
**N Folios:** 16

### 5.1 Why REGIME_3 Exists

REGIME_3 is **Pareto-dominated** (inferior on all tradeoff axes to at least one other regime),
yet it contains 16 folios. This apparent paradox is explained by **local pressure conditions**:

- extreme time pressure conditions favor REGIME_3 (fastest execution)

### 5.2 Entry Conditions

Pressure conditions that induce transition **into** REGIME_3:

- acute time pressure spike (convergence urgency)
- time-critical phase requiring rapid throughput
- transient passage during regime shifting

### 5.3 Exit Conditions

Pressure conditions that induce transition **out of** REGIME_3:

- accumulated risk pressure creates gradient toward REGIME_2 or REGIME_4
- stability pressure builds without compensating advantage
- no sustainable equilibrium in high-risk, low-stability region

### 5.4 Transient Role

REGIME_3 serves as a transient state: entered when time pressure is acute, but pressure accumulation forces exit toward more sustainable regimes. It is a throughput-maximizing passage, not a dwelling state.

---

## 6. Prohibited/Unsupported Transitions

| From | To | Reason | Δ Time | Δ Risk | Δ Stability |
|------|-----|--------|--------|--------|-------------|
| REGIME_2 | REGIME_1 | worsens all three pressure axes | +0.245 | +0.419 | +0.256 |
| REGIME_4 | REGIME_1 | worsens all three pressure axes | +0.537 | +0.200 | +0.118 |
| REGIME_4 | REGIME_3 | worsens all three pressure axes | +0.137 | +0.284 | +0.254 |

---

## 7. Cross-Check Results

| Check | Description | Status |
|-------|-------------|--------|
| regime_3_transient | REGIME_3 appears only as transient sink or bridge | **PASS** |
| conservative_path_exists | At least one conservative stabilization path always exists | **PASS** |
| restart_regime_4_alignment | Restart pressure routes align with REGIME_4 bias | **PASS** |
| no_pressure_free_cycles | Switching graph has no pressure-free cycles | **PASS** |

**Overall Status:** ALL PASS

---

## 8. Switching Graph Visualization (ASCII)

```
                    ┌───────────┐
                    │  REGIME_1 │ ◀─── high stability
                    │ (stable)  │
                    └─────┬─────┘
                          │
           time pressure  │  risk pressure
                 ▼        │        ▼
         ┌───────────┐    │    ┌───────────┐
         │  REGIME_2 │◀───┼───▶│  REGIME_4 │
         │ (low risk)│    │    │  (fast)   │
         └─────┬─────┘    │    └─────┬─────┘
               │          │          │
               │    ┌─────┴─────┐    │
               └───▶│  REGIME_3 │◀───┘
                    │(transient)│
                    │ dominated │
                    └───────────┘
                          │
                    exit pressure
                          ▼
```

**Legend:**
- Arrows indicate pressure gradient direction
- REGIME_3 is entered under acute time pressure, exited under accumulated risk/stability pressure

---

> **"OPS-4 is complete. A non-semantic operator decision and regime-switching model has been
> derived using purely operational pressures. No historical, craft, or product interpretation
> has been introduced."**

*Generated: 2026-01-04T21:49:49.099149*