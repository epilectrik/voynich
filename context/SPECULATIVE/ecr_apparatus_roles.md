# ECR-2: Apparatus-Role Identification

**Tier:** 3 | **Status:** ACTIVE | **Date:** 2026-01-10

> **Entity-level identification (specific plants, machines, substances) is probably irrecoverable by design and is not the goal of this analysis.**

---

## Objective

Infer the **functional roles and constraints** of apparatus implied by frozen constraints, WITHOUT naming specific devices.

---

## Evidence Summary

### From Kernel Structure (C085-C108)

| Kernel Operator | Role | Evidence |
|-----------------|------|----------|
| **k** | ENERGY_MODULATOR | Controls energy input to system (C103) |
| **h** | PHASE_MANAGER | Manages phase transitions and material state (C104) |
| **e** | STABILITY_ANCHOR | Anchors system to stable state; 54.7% of recovery paths (C105) |

All kernel nodes are BOUNDARY_ADJACENT to forbidden transitions (C107). Kernel controls hazard proximity.

### From Circulatory Requirement (C171)

- Only closed-loop process control survives
- Material must cycle through apparatus
- Continuous, not batch operation

### From Regime Structure (C179-C185)

| Regime | Characteristic | Apparatus Implication |
|--------|---------------|----------------------|
| REGIME_1 | Baseline operation | Default apparatus state |
| REGIME_2 | Lowest CEI | Minimal apparatus engagement |
| REGIME_3 | High throughput (transient) | Peak apparatus utilization |
| REGIME_4 | Elevated engagement | Active apparatus control |

### From Hybrid Hazard Model (C216)

| Hazard Focus | % | LINK Nearby | Implication |
|--------------|---|-------------|-------------|
| Batch-focused | 71% | Yes | Opportunity-loss; can wait |
| Apparatus-focused | 29% | **ZERO** | Equipment protection; immediate response |

Apparatus hazards require faster response than batch hazards.

### From OPS Doctrine

| Principle | Apparatus Implication |
|-----------|----------------------|
| Waiting is default (38%) | Apparatus supports idle state |
| Escalation irreversible | Apparatus state changes are permanent |
| Restart requires low-CEI | Restart = cold/empty apparatus state |
| 3 restart-capable folios | Only specific configurations allow restart |

---

## Inferred Apparatus Roles

### Required Roles (Structurally Mandated)

| Role | Evidence | Function |
|------|----------|----------|
| **Energy Source Role** | k = ENERGY_MODULATOR (C103) | Controls energy input to system |
| **Phase Container Role** | h = PHASE_MANAGER (C104) | Manages phase transitions |
| **Circulation Path Role** | C171 (closed-loop required) | Material cycles through apparatus |
| **Stability Anchor Role** | e = STABILITY_ANCHOR (C105) | Recovery position; 54.7% of paths |

### Implied Roles (Consistent with Hazards)

| Role | Evidence | Function |
|------|----------|----------|
| **Separator Role** | PHASE_ORDERING hazard (41%) | Where phases are separated |
| **Collector Role** | COMPOSITION_JUMP hazard (24%) | Where fractions are collected |
| **Containment Role** | CONTAINMENT_TIMING hazard (24%) | Where pressure/overflow is managed |

---

## Apparatus Role Taxonomy

### Functional Classification (No Device Names)

```
APPARATUS ROLES
├── ENERGY DOMAIN
│   └── Energy Source (k-controlled)
│       - Modulates energy input
│       - Regime-dependent activity
│
├── PHASE DOMAIN
│   ├── Phase Container (h-controlled)
│   │   - Where state changes occur
│   │   - Phase transitions managed here
│   │
│   └── Separator (implied by hazard)
│       - Where phases are differentiated
│       - PHASE_ORDERING hazard location
│
├── FLOW DOMAIN
│   ├── Circulation Path (C171 required)
│   │   - Material cycles through
│   │   - Closed-loop structure
│   │
│   └── Collector (implied by hazard)
│       - Where fractions are captured
│       - COMPOSITION_JUMP hazard location
│
└── CONTROL DOMAIN
    └── Stability Anchor (e-controlled)
        - Recovery position
        - 54.7% of recovery paths
        - Low-CEI state for restart
```

---

## Apparatus Constraints

### What the System Encodes

| Constraint | Evidence |
|------------|----------|
| Circulatory operation required | C171 |
| 4 operating regimes exist | C179 |
| High-throughput is unsustainable | C185 (REGIME_3 transient) |
| Restart requires specific state | C182 (low-CEI) |
| 29% of hazards are apparatus-focused | C216 |
| Apparatus hazards need immediate response | C216 (zero LINK nearby) |

### What the System Assumes (Not Encoded)

| Assumption | Evidence |
|------------|----------|
| Apparatus exists and is functional | No apparatus setup instructions |
| Operator knows apparatus | OPS-7 (EXPERT_REFERENCE archetype) |
| Apparatus can be controlled | Kernel operators exist but no apparatus instructions |
| Physical configuration is known | No spatial layout information |

---

## Role-to-Regime Mapping

| Role | REGIME_1 | REGIME_2 | REGIME_3 | REGIME_4 |
|------|----------|----------|----------|----------|
| Energy Source | Baseline | Minimal | Peak | Active |
| Phase Container | Active | Quiescent | Rapid cycling | Active |
| Circulation Path | Standard | Slow | Fast | Standard |
| Stability Anchor | Available | Primary | Stressed | Available |

---

## Role-to-Hazard Mapping

| Role | Primary Hazard | Secondary Hazard |
|------|---------------|-----------------|
| Phase Container | PHASE_ORDERING | ENERGY_OVERSHOOT |
| Separator | PHASE_ORDERING | COMPOSITION_JUMP |
| Collector | COMPOSITION_JUMP | CONTAINMENT_TIMING |
| Circulation Path | RATE_MISMATCH | PHASE_ORDERING |
| Energy Source | ENERGY_OVERSHOOT | - |

---

## Findings

### Established (High Confidence)

1. **At least 4 functional apparatus roles exist:**
   - Energy Source (k-controlled)
   - Phase Container (h-controlled)
   - Circulation Path (C171 required)
   - Stability Anchor (e-controlled)

2. **Additional roles implied by hazard structure:**
   - Separator (PHASE_ORDERING hazard)
   - Collector (COMPOSITION_JUMP hazard)
   - Containment (CONTAINMENT_TIMING hazard)

3. **Apparatus supports exactly 4 operating regimes** (C179)

4. **29% of hazards are apparatus-focused** requiring immediate response (C216)

5. **System assumes apparatus exists** but does not encode configuration

6. **Restart requires cold/low-CEI state** (C182)

### Uncertain (Lower Confidence)

- Whether distinct physical devices map to each role
- Whether some roles are co-located (same device, multiple roles)
- Physical spatial arrangement of apparatus
- Specific control mechanisms

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C103-C105 (kernel operators) | Mapped to apparatus roles |
| C171 (circulatory required) | Circulation Path role |
| C179 (4 regimes) | Roles support 4 configurations |
| C216 (hybrid hazard) | Apparatus vs batch hazard distinction |
| OPS-4 (restart mechanics) | Stability Anchor at low-CEI |

---

## What This Does NOT Establish

- What specific devices fill each role
- Device names (alembic, retort, etc.)
- Physical construction or materials
- Spatial arrangement of apparatus
- How apparatus is manufactured or acquired

---

## Navigation

← [ecr_material_classes.md](ecr_material_classes.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
