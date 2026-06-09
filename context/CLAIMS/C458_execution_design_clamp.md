# C458: Execution Design Clamp vs Recovery Freedom

**Tier:** 2 | **Status:** CLOSED | **Scope:** Currier B

> **DEMOTED 2->3 (SELF_CITATION_HEAD_TO_HEAD P4b, 2026-06-08) -- FREQUENCY SHADOW (C475 class).**
> The headline clamp/free CV asymmetry does not survive frequency matching: raw density-CV gap
> 0.720 collapses to a corrected gap of 0.089 when each token set is compared against random
> sets matched on its own per-type corpus frequencies (hazard set at the 82nd percentile of its
> frequency-matched null; recovery at the 36th -- NEITHER anomalous). "Hazard clamped / recovery
> free" = "common words are folio-uniform, rare words are folio-variable" (Zipf). Compounding:
> the clamped dimensions were densities/ratios while the free dimensions were raw counts.
> The REGIME-separation findings below are untested by this audit and stand. Audit:
> `phases/SELF_CITATION_HEAD_TO_HEAD/scripts/p0_preflight_audits.py`.

---

## Statement

In Currier B programs, hazard exposure, kernel contact, and intervention diversity exhibit **extremely low variance** across folios (CV = 0.04-0.11), while recovery operations and near-miss handling exhibit **high variance** (CV = 0.72-0.82).

This indicates deliberate **clamping of risky interaction surfaces** alongside **freedom in recovery architecture**.

---

## Evidence

### Variance Analysis (Coefficient of Variation)

| Dimension | CV | Category |
|-----------|-----|----------|
| intervention_diversity | 0.040 | CLAMPED |
| kernel_contact_ratio | 0.112 | CLAMPED |
| hazard_density | 0.114 | CLAMPED |
| mean_cycle_length | 0.152 | CLAMPED |
| link_density | 0.181 | MODERATE |
| recovery_ops_count | 0.819 | FREE |
| near_miss_count | 0.722 | FREE |

### Regime Separation

All key metrics show highly significant regime differences (p < 0.0001) with large effect sizes:

| Metric | H-statistic | eta-squared |
|--------|-------------|-------------|
| link_density | 61.5 | 0.741 |
| hazard_density | 58.3 | 0.700 |
| CEI_total | 54.0 | 0.646 |
| qo_density | 37.7 | 0.440 |

Regimes partition the design space **cleanly**, not as overlapping fuzz.

---

## C458.a: Hazard/LINK Mutual Exclusion Surface

Hazard density and LINK density are near-perfectly anticorrelated:

| Metric | Value |
|--------|-------|
| Spearman r | -0.945 |
| p-value | < 0.0001 |
| Empty cells | 15/25 (60%) |

**Interpretation:** There is a forbidden region of design space where high hazard and high monitoring cannot coexist. This is an observed design boundary, not yet fully explained.

**Note:** Revisit after D2 (AZC) and D3 (HT) to check for cross-system parallels.

---

## What This Constraint Claims

1. B programs are **not uniformly flexible** - some dimensions are free, others are clamped
2. The designer **deliberately constrains hazard exposure** while allowing **freedom in recovery**
3. Regimes represent **distinct design configurations**, not random variation
4. High hazard + high LINK is a **forbidden combination**

---

## What This Constraint Does NOT Claim

- WHY the boundary exists (apparatus physics, safety margin, etc.)
- Whether this pattern appears in other systems (A, AZC, HT)
- The functional meaning of "clamped" vs "free" dimensions

---

## Architectural Interpretation

The asymmetry suggests a design philosophy:

> "Constrain the dangerous interactions tightly. Let recovery operations vary freely."

This is consistent with a risk-managed system where:
- Core hazard exposure is non-negotiable
- Recovery flexibility is adaptive/contextual

---

## Phase Documentation

Research conducted: 2026-01-10 (D1 - B Design Space Cartography)

Scripts:
- `phases/exploration/b_design_space_cartography.py`

Results:
- `results/b_design_space_cartography.json`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
