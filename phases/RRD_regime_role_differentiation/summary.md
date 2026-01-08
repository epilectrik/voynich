# Phase RRD: Regime-Role Differentiation

## Core Question

> **Do aggressive and conservative programs use different role/family mixtures, or is intensity purely parametric?**

## Motivation

Prior phases established that 83 Currier B folios form distinct intensity regimes (AGGRESSIVE, MODERATE, CONSERVATIVE) based on control signatures (link_density, hazard_density, kernel_contact_ratio). The question is whether these regimes represent:
- Different operational MODES (categorical) with distinct instruction mixes, OR
- Same instruction mix applied at different INTENSITIES (parametric)

If regimes are categorical, this supports the theory that different "families" of programs serve different purposes.

## Results

### Classification

Folios classified into 3 intensity groups using median splits on link_density, hazard_density, and kernel_contact_ratio:

| Intensity | Folios | Criteria |
|-----------|--------|----------|
| AGGRESSIVE | 40 | Low LINK, high hazard, high kernel |
| CONSERVATIVE | 40 | High LINK, low hazard, low kernel |
| MODERATE | 3 | Mixed signals |

### Role Composition by Intensity

| Role | Conservative | Moderate | Aggressive | p-value |
|------|-------------|----------|------------|---------|
| ENERGY_OPERATOR | 31.0% | 27.0% | 41.4% | 0.012* |
| CORE_CONTROL | 19.7% | 13.8% | 24.3% | 0.033* |
| HIGH_IMPACT | 14.9% | 21.6% | 7.5% | 0.0004*** |
| FREQUENT_OPERATOR | 15.3% | 15.8% | 10.0% | 0.059 |
| FLOW_OPERATOR | 10.2% | 13.5% | 8.2% | 0.15 |
| AUXILIARY | 9.0% | 8.2% | 8.5% | 0.99 |

### Key Findings

**Verdict: CATEGORICAL (not parametric)**

1. **AGGRESSIVE programs are kernel-heavy:**
   - 1.34x more ENERGY_OPERATOR (p=0.012)
   - 1.24x more CORE_CONTROL (p=0.033)
   - Strategy: Rapid small adjustments without waiting

2. **CONSERVATIVE programs are HIGH_IMPACT heavy:**
   - 2.0x more HIGH_IMPACT (p=0.0004)
   - Strategy: Bigger, less frequent moves with more waiting

3. **AUXILIARY is INVARIANT (p=0.99):**
   - Infrastructure tokens remain constant
   - Grammar skeleton is fixed
   - Only intervention strategy varies

### Correlation with Continuous Metrics

| Role | link_density | hazard_density | kernel_ratio |
|------|--------------|----------------|--------------|
| ENERGY_OPERATOR | -0.291* | +0.422* | +0.291* |
| HIGH_IMPACT | +0.378* | -0.333* | -0.378* |
| CORE_CONTROL | -0.184 | -0.054 | +0.184 |
| AUXILIARY | +0.025 | -0.012 | -0.025 |

Pattern confirms: HIGH_IMPACT tokens used when environment is SAFE (high LINK, low hazard), not when hazardous.

## Interpretation

This is a **sophisticated dual control strategy**:

| Context | Strategy | Tokens |
|---------|----------|--------|
| Time-constrained (aggressive) | Rapid small adjustments | ENERGY_OPERATOR, CORE_CONTROL |
| Time-available (conservative) | Big moves + settle | HIGH_IMPACT + LINK |

HIGH_IMPACT is not about when hazards are present, but about what happens AFTER you use them. Conservative programs have time to let the system respond to big interventions.

## Also Tested: Cross-System Coordination

### Question: Do B programs cluster by A-section reference?

Hypothesis: Different B program families might correspond to different physical processes (pelican alembic, plant management, etc.) drawing from different A sections.

### Result: NO CLUSTERING

All 82 B folios have uniform A-section reference mix:
- H-fraction: 0.348-0.458 (tight range)
- P-fraction: 0.287-0.385
- T-fraction: 0.169-0.365

No bimodality in A-section profiles. B programs are **universal** - they don't specialize by material category.

### Conclusion

Differentiation is by **intensity** (how hard you push), not by **material** (what you're processing). All B programs use the same A-section vocabulary mix; they differ only in operational aggressiveness.

## Constraints Added

**Constraint 394**: INTENSITY-ROLE DIFFERENTIATION: Aggressive programs use 1.34x more ENERGY_OPERATOR (41.4% vs 31.0%, p=0.012) and 1.24x more CORE_CONTROL (24.3% vs 19.7%, p=0.033); conservative programs use 2.0x more HIGH_IMPACT (14.9% vs 7.5%, p=0.0004); role composition varies systematically by operational intensity (RRD, Tier 2)

**Constraint 395**: DUAL CONTROL STRATEGY: Aggressive = rapid small adjustments (kernel-heavy, less waiting); Conservative = bigger moves with more waiting (HIGH_IMPACT heavy, more LINK); confirms intensity regimes are categorical operational modes, not just parametric variation (RRD, Tier 2)

**Constraint 396**: AUXILIARY INVARIANCE: AUXILIARY role is invariant across intensity regimes (8.5-9.0%, p=0.99); infrastructure tokens remain constant while intervention tokens vary; grammar skeleton is fixed, intervention strategy is variable (RRD, Tier 2)

## Theory Update

**User's theory "5 families = 5 different processes" is NOT SUPPORTED by A-section correlation.**

What IS supported:
- Regimes are categorical operational modes (not parametric)
- Each mode has distinct instruction mix
- But all modes use same universal vocabulary/material base
- Differentiation is in HOW you operate, not WHAT you process

## Files

- `archive/scripts/regime_role_differentiation.py` - Role composition analysis
- `archive/scripts/cross_system_coordination.py` - A-section reference analysis

## Status

**CLOSED** - 3 constraints established (394-396)

Intensity regimes are CATEGORICAL operational modes with distinct instruction mixes. B programs are UNIVERSAL (not material-specific).
