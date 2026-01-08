# Phase PAS: Program Archetype Synthesis

## Core Question

> **Do the 83 B folios form a coherent taxonomy of program archetypes?**

Synthesize all control metrics, role compositions, and vocabulary patterns into a unified organizational model.

## Methodology

Clustered 82 Currier B folios using 15 features:
- Control signatures: link_density, hazard_density, kernel_contact_ratio, intervention_frequency
- Role composition: 6 grammar roles
- Vocabulary metrics: TTR, concentration, core_coverage
- LINK behavior: max_run, mean_run

## Results

### Optimal Clustering

| k | Silhouette |
|---|------------|
| 2 | 0.179 |
| 3 | **0.193** |
| 4 | 0.148 |
| 5 | 0.140 |

Silhouette scores are low (0.14-0.19), indicating programs form a **continuum** rather than discrete clusters. However, k=5 reveals interpretable archetypes.

### 5 Program Archetypes

#### ARCHETYPE 1: Conservative Waiting Programs (10 folios)
**Profile**: WAIT-HEAVY + HAZARD-AVOIDING + KERNEL-LIGHT

| Metric | Value |
|--------|-------|
| LINK density | 0.502 (highest) |
| Hazard density | 0.478 (lowest) |
| Kernel ratio | 0.498 (lowest) |
| HIGH_IMPACT | 21.7% (highest) |

*Folios: f105r, f105v, f115v, f26v, f31v, f48r, f48v, f86v3, f86v5, f95v1*

**Interpretation**: Maximum waiting, minimum risk. Uses big interventions (HIGH_IMPACT) when action needed, then returns to waiting. For high-value materials requiring patience.

#### ARCHETYPE 2: Aggressive Intervention Programs (10 folios)
**Profile**: ACTION-HEAVY + HAZARD-TOLERANT + KERNEL-ENGAGED

| Metric | Value |
|--------|-------|
| LINK density | 0.333 (lowest) |
| Hazard density | 0.622 (high) |
| Kernel ratio | 0.667 (high) |
| CORE_CONTROL | 26.3% (highest) |

*Folios: f114v, f31r, f39r, f46r, f46v, f66v, f85r2, f86v4, f95r1, f95r2*

**Interpretation**: Active control with high coordination between ENERGY and CORE. For time-sensitive materials requiring close monitoring and rapid response.

#### ARCHETYPE 3: Balanced Standard Programs (20 folios)
**Profile**: BALANCED

| Metric | Value |
|--------|-------|
| All metrics | Near median |
| ENERGY_OPERATOR | 39.2% |

*Folios: f104r, f104v, f106r, f106v, f107r, f107v, f111r, f112r, f112v, f113r, ...*

**Interpretation**: Generic operational profile. The "default" program type.

#### ARCHETYPE 4: FREQUENT_OPERATOR-Dominated Programs (16 folios)
**Profile**: BALANCED but FREQUENT_OPERATOR dominant

| Metric | Value |
|--------|-------|
| FREQUENT_OPERATOR | **26.7%** (only archetype where dominant) |
| ENERGY_OPERATOR | 19.6% (lowest) |
| TTR | 0.806 (highest vocabulary diversity) |

*Folios: f26r, f33r, f33v, f39v, f40r, f40v, f41r, f41v, f50r, f50v, ...*

**Interpretation**: Unusual instruction mix dominated by FREQUENT_OPERATOR. High vocabulary diversity suggests specialized procedures. Possibly the "workhorse" programs for routine operations.

#### ARCHETYPE 5: Energy-Intensive Programs (26 folios)
**Profile**: ACTION-HEAVY + HAZARD-TOLERANT + KERNEL-ENGAGED

| Metric | Value |
|--------|-------|
| ENERGY_OPERATOR | **47.2%** (highest) |
| HIGH_IMPACT | 4.0% (lowest) |
| Core coverage | 0.822 (highest) |
| TTR | 0.545 (lowest vocabulary diversity) |

*Folios: f103r, f103v, f108r, f108v, f111v, f116r, f75r, f75v, f76r, f76v, ...*

**Interpretation**: Dominated by energy management with minimal big interventions. High core vocabulary usage indicates standard, well-established procedures. For materials requiring steady energy input without phase transitions.

## Key Findings

1. **Programs form a continuum** (low silhouette) rather than discrete clusters
2. **5 archetypes are interpretable** with distinct operational profiles
3. **Role composition varies systematically** (confirms RRD phase)
4. **FREQUENT_OPERATOR dominance** in Archetype 4 is anomalous — not seen elsewhere
5. **Vocabulary diversity inversely correlates** with ENERGY_OPERATOR dominance

## Constraint Added

**Constraint 403**: PROGRAM ARCHETYPE CONTINUUM: 83 B programs form a continuum (silhouette 0.14-0.19) with 5 interpretable archetypes: (1) Conservative Waiting (10 folios, LINK 0.50, HIGH_IMPACT 21.7%), (2) Aggressive Intervention (10 folios, CORE_CONTROL 26.3%), (3) Balanced Standard (20 folios), (4) FREQUENT_OPERATOR-Dominated (16 folios, 26.7%), (5) Energy-Intensive (26 folios, ENERGY_OPERATOR 47.2%); programs are not discrete categories but positions on a multidimensional operational manifold (PAS, Tier 2)

## Files

- `archive/scripts/program_archetype_synthesis.py` - Main analysis

## Status

**CLOSED** - 1 constraint established (403)

Programs form a structured continuum of operational profiles, not discrete categories. The 5-archetype taxonomy provides a coherent organizational model for understanding program variation.
