# AZC_TRAJECTORY_SHAPE Phase

**Status:** PRE-REGISTERED
**Date:** 2026-01-19
**Hypotheses:** 9 (LOCKED)

---

## Goal

Comprehensive investigation of AZC family differentiation combining:
1. **Vector 1: Trajectory Shape** (external expert) - judgment withdrawal patterns
2. **Vector 2: Apparatus Mapping** (expert-advisor) - pelican alembic structural correspondence

---

## Expert Hypotheses

### External Expert: Trajectory Shape

| Family | Pattern | Characteristics |
|--------|---------|-----------------|
| **Zodiac** | Wide-then-collapse | Sustained coarse monitoring, high entropy early, monotonic decline, sharp terminal compression |
| **A/C** | Narrow-then-spike | Punctuated fine discrimination, low entropy with sharp checkpoints, non-monotonic |

### Expert-Advisor: Apparatus Mapping

| AZC Zone | Escape Rate | Pelican State (Predicted) |
|----------|-------------|---------------------------|
| C | 1.4% | Charging/loading - errors fixable |
| P | 11.6% | Active reflux - intervention permitted |
| R1->R3 | 2%->0% | Concentration - progressively committed |
| S | 0-3.8% | Collection - irreversible |

---

## PRE-REGISTERED HYPOTHESES (LOCKED)

### VECTOR 1: Trajectory Shape

#### H1: Entropy Trajectory Slope Differs
- **Prediction:** Zodiac has more negative slope (widening->narrowing) than A/C
- **Test:** Linear regression of entropy vs zone position per folio
- **Threshold:** Cohen's d >= 0.5, p < 0.05

#### H2: Monotonicity Differs
- **Prediction:** Zodiac shows steady decline (rho < -0.7), A/C shows oscillation (|rho| < 0.5)
- **Test:** Spearman correlation of entropy with zone order
- **Threshold:** Mann-Whitney p < 0.05

#### H3: Terminal Compression Ratio Differs
- **Prediction:** Zodiac has sharper collapse (lower final/peak ratio) than A/C
- **Test:** Ratio of final zone entropy to peak entropy
- **Threshold:** Difference >= 0.2, p < 0.05

#### H4: Peak Count Differs
- **Prediction:** A/C has more entropy peaks (>= 1.5) than Zodiac (< 1.0)
- **Test:** Count local maxima in entropy trajectory
- **Threshold:** Poisson rate ratio >= 2.0

#### H5: Judgment Elimination Order Differs
- **Prediction:** Families eliminate judgment types in different orders
- **Test:** Kendall's tau on elimination sequences
- **Threshold:** tau < 0.6, p < 0.05

### VECTOR 2: Apparatus Mapping

#### H6: R-Series MIDDLE Restriction Gradient
- **Prediction:** R1->R2->R3 shows monotonically decreasing legal MIDDLEs
- **Test:** Count unique MIDDLEs permitted at each R-position
- **Threshold:** Monotonic decrease with Spearman rho < -0.8, p < 0.05

#### H7: S-Zone to B-Terminal Vocabulary Overlap
- **Prediction:** S-zone MIDDLEs preferentially appear in STATE-C terminal B programs
- **Test:** Enrichment analysis - S-zone vocabulary vs B termination vocabulary
- **Threshold:** Odds ratio >= 2.0, Fisher's exact p < 0.05

#### H8: Zone-Apparatus Phase Alignment
- **Prediction:** Escape gradient matches pelican operational reversibility
- **Test:** Correlation of escape rate with procedural reversibility from Brunschwig
- **Threshold:** Spearman rho > 0.7, p < 0.05

#### H9: Family-Conditioned Escape Asymmetry
- **Prediction:** Zodiac has steeper escape collapse than A/C (uniform scaffold = stricter)
- **Test:** Compare escape rate variance across zones by family
- **Threshold:** Levene's test p < 0.05, Zodiac variance < A/C variance

---

## Tier Assessment Criteria

| Vector 1 | Vector 2 | Combined | Verdict |
|----------|----------|----------|---------|
| 4-5/5 | 3-4/4 | 7-9/9 | **Tier 2** - Strong structural evidence |
| 3-4/5 | 2-3/4 | 5-6/9 | **Tier 3** - Partial evidence, enrichment |
| 2/5 | 1-2/4 | 3-4/9 | **Tier 4** - Suggestive but insufficient |
| 0-1/5 | 0-1/4 | 0-2/9 | **FALSIFIED** |

---

## Constraint Compliance

| Constraint | How Respected |
|------------|---------------|
| C384 | Aggregate placement distributions only, no token-to-referent mapping |
| C430 | Explicit Zodiac/A/C family separation |
| C434 | Uses R-series forward ordering as structural input |
| C435 | Respects S/R positional division |

---

## Data Sources

| File | Contents |
|------|----------|
| `results/azc_folio_features.json` | Per-folio placement vectors |
| `results/azc_escape_by_position.json` | Escape rates by zone and family |
| `results/azc_internal_oscillation.json` | Per-folio HT densities |
| `data/voynichese_analysis.db` | MIDDLE extraction |
| `data/brunschwig_materials_master.json` | Procedural reversibility |

---

*Pre-registration locked: 2026-01-19*
*Builds on: TRAJECTORY_SEMANTICS, AZC constraint hunting*
