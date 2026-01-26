# REGIME_SEMANTIC_INTERPRETATION Results

**Phase:** REGIME_SEMANTIC_INTERPRETATION
**Date:** 2026-01-25
**Status:** CLOSED
**Predecessor:** LINE_BOUNDARY_OPERATORS

---

## Goal

Determine what REGIME classifications encode - why are some folios control-intensive (REGIME_1/3) and others output-intensive (REGIME_2/4)?

---

## Primary Finding: REGIME = Grammar Infrastructure Allocation

REGIME classifications reflect **grammar infrastructure allocation**, not execution intensity.

| REGIME | L-compound | LATE | Kernel | Interpretation |
|--------|------------|------|--------|----------------|
| REGIME_1 | 2.35% | 1.37% | 16.8% | Control-infrastructure-heavy |
| REGIME_2 | 0.32% | 3.14% | 10.2% | Output-intensive |
| REGIME_3 | 1.60% | 1.05% | 12.8% | Control without output |
| REGIME_4 | 0.87% | 1.98% | 14.0% | Balanced |

---

## Key Correlation: Section B Concentration

**70% of Section B (balneological) folios are REGIME_1.**

| Section | REGIME_1 | REGIME_2 | REGIME_3 | REGIME_4 | Total |
|---------|----------|----------|----------|----------|-------|
| B (balneological) | 14 (70%) | 1 (5%) | 3 (15%) | 2 (10%) | 20 |
| H (herbal) | 4 (13%) | 10 (31%) | 4 (13%) | 14 (44%) | 32 |
| S (stellar) | 4 (17%) | 8 (35%) | 1 (4%) | 10 (43%) | 23 |
| C (cosmological) | 0 | 4 (80%) | 0 | 1 (20%) | 5 |

**Conclusion:** Section B procedures require heavy control infrastructure (kernel, L-compound, energy prefixes).

---

## Orthogonal to C494 Precision Axis

This classification is **orthogonal** to C494's execution intensity axis:

| Axis | Measures | Source |
|------|----------|--------|
| C494 | Execution intensity/precision | BRUNSCHWIG_TEMPLATE_FIT |
| This phase | Grammar infrastructure type | LINE_BOUNDARY_OPERATORS |

A folio can be both high-precision (C494) AND control-infrastructure-heavy (this phase).

---

## REGIME_1 Characteristics (Control-Infrastructure-Heavy)

| Property | Value | Comparison |
|----------|-------|------------|
| L-compound | 2.31% | 5.1x REGIME_2 |
| Kernel usage | 16.8% | 1.6x REGIME_2 |
| MIDDLE repetition | 31.0% | 1.2x REGIME_2 |
| Bare energy prefix | 23.21% | 1.4x REGIME_2 |
| Section B concentration | 70% | vs 5% for REGIME_2 |

**Enriched MIDDLEs in REGIME_1:**
- lsh: 7.51x
- lch: 4.38x
- lk: 2.61x
- ect: 4.66x
- ct: 2.31x

---

## Fire-Degree by Section (NOT a REGIME differentiator)

| Section | High Fire | Low Fire | Ratio |
|---------|-----------|----------|-------|
| B | 7.5% | 19.4% | 0.39 |
| H | 3.9% | 17.8% | **0.22** (lowest) |
| S | 7.1% | 15.2% | 0.47 |
| C | 6.1% | 12.9% | **0.48** (highest) |

Fire-degree distributes by **section**, not by REGIME.

---

## Semantic Interpretation

### Section B (Balneological) = Complex Thermal Processing

Section B folios with "bathing figures" show:
- Highest control infrastructure (REGIME_1 dominant)
- Highest kernel intervention rates
- Highest L-compound (modified energy operators)

This suggests the "bathing" imagery depicts **thermal processing** requiring:
- Active temperature control (kernel = intervention)
- Modified energy operations (L-compound = shifted timing)
- Heavy monitoring (MIDDLE repetition)

### Section H/S = Simpler or Output-Focused Procedures

Sections H and S distribute across REGIMEs, with more REGIME_2/4:
- Lower control infrastructure needs
- More output marking (LATE prefix)
- Less intervention required

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C494 | Orthogonal - C494 measures execution precision, this measures grammar allocation |
| C536 | Compatible - material class routes independently of grammar infrastructure |
| C298.a | Extended - L-compound = l + energy operator pattern |
| C539 | Compatible - LATE marks output-intensive procedures |

---

## New Understanding: Two-Axis REGIME Model

```
         CONTROL INFRASTRUCTURE (This Phase)
              High                 Low
         +----------+----------+
   High  | REGIME_1 | REGIME_2 |  LATE PREFIX
         | (Sec B)  | (Sec C)  |  (Output)
OUTPUT   +----------+----------+
         | REGIME_3 | REGIME_4 |
   Low   |          | (Sec H)  |
         +----------+----------+
```

---

## Scripts

- `create_regime_mapping.py` - Classify folios into REGIMEs
- `regime_correlation_analysis.py` - Suffix, kernel, diversity analysis
- `regime_section_deep_dive.py` - Section correlation analysis
- `regime_c494_reconciliation.py` - Reconcile with C494 precision axis

---

## Tier 3 Characterization

**Grammar-Based REGIME Classification:**
- REGIME_1: Control-infrastructure-heavy (70% Section B)
- REGIME_2: Output-intensive (distributed H/S/C)
- REGIME_4: Balanced (44% Section H)

**Section B Interpretation:**
- Balneological imagery depicts thermal processing requiring active control
- Control infrastructure (L-compound, kernel) maps to intervention requirements
- "Bathing" = thermal bath processing, not literal bathing

---

---

## Secondary Finding: Section H = Gentle Precision (C494.a)

Section H provides empirical confirmation of C494's "gentle but precise" case.

| Section | REGIME_4 | ch/sh | High-fire | Profile |
|---------|----------|-------|-----------|---------|
| H | **43.8%** | **1.86** | **3.9%** | Gentle + Precise |
| S | 43.0% | 2.00 | 7.1% | Aggressive + Precise |
| B | 10.0% | 0.96 | 7.5% | Balanced |

**Key insight:** Precision and intensity are orthogonal.

Section H uses precision mode (ch dominates) but stays at low fire-degree. Even within ch-tokens, Section H shows lowest high/low ratio (0.20 vs 0.43 for S).

**Interpretation:** Section H documents "volatile aromatic distillation" - procedures requiring gentle heat but exact temperature control. This confirms C494's claim with empirical section-level data.

**Constraint extended:** C494.a added to document empirical evidence.

---

## Navigation

<- [LINE_BOUNDARY_OPERATORS](../LINE_BOUNDARY_OPERATORS/RESULTS.md) | [../README.md](../README.md) ->
