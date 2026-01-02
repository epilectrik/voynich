# Process Outcome Patterns
> **SCOPE**: State-change level descriptions only. No substances, products, or stopping conditions.

## Outcome Pattern Inventory

### INCREASED_HOMOGENEITY
**Mechanism**: Repeated circulation through controlled path reduces spatial variation

**Evidence**:
- STRUCTURALLY SUPPORTED: 100% convergence to STATE-C
- STRUCTURALLY SUPPORTED: Cycle regularity decreases variance
- SPECULATIVE BUT CONSISTENT: Circulation averaging perturbations

**Metric Support**:
- convergence_rate: 100% across all compatible geometries
- state_c_time: >99.8% in G4/G5 geometries

---

### INCREASED_MOBILITY
**Mechanism**: Circulation increases effective diffusion paths

**Evidence**:
- SPECULATIVE BUT CONSISTENT: CLASS_D (rapid diffusion) most compatible
- SPECULATIVE BUT CONSISTENT: LINK effectiveness higher in closed loops
- WEAK: Extended programs might allow greater mobility change

**Metric Support**:
- class_d_convergence: 100%
- link_effectiveness_g5: 1.35 (highest)

---

### PROGRESSIVE_CONCENTRATION
**Mechanism**: Selective retention/release at circulation boundaries

**Evidence**:
- SPECULATIVE BUT CONSISTENT: Hazard boundaries = concentration limits
- SPECULATIVE BUT CONSISTENT: Near-miss counts = operating near limits
- WEAK: No direct evidence of concentration endpoint

**Metric Support**:
- mean_near_miss: ~15 per program
- hazard_density_range: 0.40-0.67

---

### GRADUAL_STABILIZATION
**Mechanism**: Repeated damped cycles reduce excursions from target

**Evidence**:
- STRUCTURALLY SUPPORTED: LINK-heavy programs = safer (d=1.60)
- STRUCTURALLY SUPPORTED: Slower reconvergence with high LINK
- STRUCTURALLY SUPPORTED: All programs reach STATE-C eventually

**Metric Support**:
- link_stability_advantage: p<0.0001, d=1.60
- convergence: 100%

---

### MAINTENANCE_OF_TARGET_STATE
**Mechanism**: Continuous feedback maintains operating point

**Evidence**:
- STRUCTURALLY SUPPORTED: STATE-C is universal endpoint
- STRUCTURALLY SUPPORTED: Kernel contact ratio ~60% (sustained control)
- STRUCTURALLY SUPPORTED: No drift detected in extended programs

**Metric Support**:
- kernel_contact_mean: 62%
- state_c_fraction: 100% convergence

---

## Evidence Classification
| Pattern | STRUCTURAL | SPECULATIVE | WEAK |
|---------|------------|-------------|------|
| INCREASED_HOMOGENEITY | 2 | 1 | 0 |
| INCREASED_MOBILITY | 0 | 2 | 1 |
| PROGRESSIVE_CONCENTRATION | 0 | 2 | 1 |
| GRADUAL_STABILIZATION | 3 | 0 | 0 |
| MAINTENANCE_OF_TARGET_STATE | 3 | 0 | 0 |

## Outcome Patterns by Program Role
How do program roles correlate with expected outcomes?

| Program Role | Primary Outcome | Secondary Outcome |
|--------------|-----------------|-------------------|
| ULTRA_CONSERVATIVE | MAINTENANCE_OF_TARGET_STATE | GRADUAL_STABILIZATION |
| CONSERVATIVE | GRADUAL_STABILIZATION | INCREASED_HOMOGENEITY |
| MODERATE | INCREASED_HOMOGENEITY | PROGRESSIVE_CONCENTRATION |
| AGGRESSIVE | PROGRESSIVE_CONCENTRATION | INCREASED_MOBILITY |
| LINK_HEAVY | GRADUAL_STABILIZATION | MAINTENANCE_OF_TARGET_STATE |
| LINK_SPARSE | INCREASED_MOBILITY | PROGRESSIVE_CONCENTRATION |
| EXTENDED | All patterns with greater magnitude | - |

## What These Patterns Do NOT Imply
- NO specific substances or feedstocks
- NO product identities
- NO stopping conditions (outcomes are ongoing, not completed)
- NO yield or production rates
- NO quality metrics beyond stability
