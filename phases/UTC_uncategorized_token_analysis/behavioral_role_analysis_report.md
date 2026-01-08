# Behavioral Role Analysis of Uncategorized Tokens

**Phase:** UTC (Uncategorized Token Characterization)
**Status:** MODEL DIAGNOSTIC (not grammar expansion)
**Date:** 2026-01-04

---

## Executive Summary

This analysis tests what behavioral role the ~40,000 uncategorized token occurrences (33.4% of corpus) play in the frozen system. Five mutually exclusive hypotheses were tested against observable structure.

### Primary Findings

| Hypothesis | Verdict | Key Evidence |
|------------|---------|--------------|
| H1: Boundary Conditions | **MODERATE** | 2.16x line-initial concentration |
| H2: Sensory Checkpoints | NULL | 0.87x hazard proximity (avoidance) |
| H3: Quantitative Markers | NULL | 1.23x repetition (not significant) |
| H4: Navigation Scaffolding | **MODERATE** | 18.5x role co-occurrence skew |
| H5: Scribal Variants | WEAK | 9.1% vocabulary overlap (extreme drift) |

### Critical Discovery

**Uncategorized vocabulary is almost entirely LOCAL (section/quire-specific).**

Only 9.1% of uncategorized token types appear in both the first and last thirds of the manuscript. This is not a uniform "missing vocabulary" - these are spatially-bound phenomena.

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total token occurrences | 121,531 |
| Categorized (Phase 20A) | 80,891 (66.6%) |
| Uncategorized | 40,640 (33.4%) |
| Categorized types | 479 |
| Uncategorized types | ~11,000+ |
| Hazard-involved tokens | 23 |

---

## Analysis 1: Positional Distribution (H1)

**Question:** Do uncategorized tokens cluster at folio starts, after LINK runs, or near high-constraint transitions?

### Results

| Position Metric | Categorized | Uncategorized | Ratio |
|-----------------|-------------|---------------|-------|
| Mean folio position | 0.506 | 0.486 | 0.96x |
| Folio start (first 10%) | 8.70% | 12.83% | **1.48x** |
| Folio end (last 10%) | 10.00% | 9.68% | 0.97x |
| Line-initial position | 10.14% | 21.89% | **2.16x** |

### Interpretation

Uncategorized tokens are:
- **Strongly enriched at line beginnings** (2.16x)
- **Moderately enriched at folio starts** (1.48x)
- **Not enriched at folio ends**

This is consistent with **boundary/header markers** - tokens that initiate lines or sections rather than carry operational content.

### H1 Verdict: MODERATE SUPPORT

Evidence FOR: Higher start concentration, strong line-initial enrichment
Evidence AGAINST: None significant
Falsification: Would be falsified by uniform positional distribution

---

## Analysis 2: Constraint Neighborhood (H2)

**Question:** Do uncategorized tokens cluster near hazard zones as sensory checkpoints?

### Results

| Metric | Categorized | Uncategorized | Ratio |
|--------|-------------|---------------|-------|
| Near hazard token (within 3) | 60.6% | 52.9% | **0.87x** |
| At forbidden seam | 93 (100%) | 0 (0%) | 0.00x |

### Interpretation

Uncategorized tokens:
- **Avoid hazard-involved tokens** (0.87x proximity)
- **Never appear at forbidden transition seams** (0/93)

This is the OPPOSITE of the sensory checkpoint hypothesis. If uncategorized tokens marked critical judgment points, they would cluster NEAR hazards, not away from them.

### H2 Verdict: NULL (Falsified)

Evidence FOR: None
Evidence AGAINST: Actively avoid hazard zones, zero presence at forbidden seams
Falsification: This hypothesis is effectively falsified

---

## Analysis 3: Repetition Patterns (H3)

**Question:** Do uncategorized tokens behave like counters, tallies, or quantitative markers?

### Results

| Metric | Categorized | Uncategorized | Ratio |
|--------|-------------|---------------|-------|
| Immediate repetition | 1.78% | 2.18% | 1.23x |
| Runs (3+ consecutive) | 269 | 377 | 1.40x |
| Max run length | 6 | 8 | 1.33x |
| Local repetition (within 10) | 63.72% | 52.60% | **0.83x** |

### Interpretation

Uncategorized tokens:
- Show **slightly higher immediate repetition** but not statistically distinct
- Form **more runs** but of similar length
- Have **lower local repetition** (less likely to recur in window)

The last finding is critical: if these were counters/tallies, they should repeat MORE locally, not less. The pattern suggests these are **rare/specialized markers**, not numeric quantities.

### H3 Verdict: NULL (No Support)

Evidence FOR: None significant
Evidence AGAINST: Lower local repetition, no distinctive tally behavior
Falsification: This hypothesis lacks support

---

## Analysis 4: Co-Occurrence with Instruction Roles (H4)

**Question:** Do uncategorized tokens preferentially appear near certain instruction classes?

### Results

| Role | Co-occurrence | Percentage |
|------|---------------|------------|
| ENERGY_OPERATOR | 39,567 | **40.4%** |
| AUXILIARY | 26,854 | **27.4%** |
| FREQUENT_OPERATOR | 15,452 | 15.8% |
| FLOW_OPERATOR | 8,350 | 8.5% |
| CORE_CONTROL | 5,667 | 5.8% |
| HIGH_IMPACT | 2,144 | **2.2%** |

**Max/Min ratio: 18.5x**

### Interpretation

Uncategorized tokens:
- **Strongly cluster near ENERGY_OPERATOR and AUXILIARY** (67.8% combined)
- **Strongly avoid HIGH_IMPACT** (only 2.2%)

This is exactly the pattern expected for **contextual/organizational markers**. High-impact operations are rare and critical - they don't need additional scaffolding. Energy and auxiliary operations are frequent - they benefit from organizational context.

### H4 Verdict: MODERATE SUPPORT

Evidence FOR: Massive role skew (18.5x), rational avoidance of critical operations
Evidence AGAINST: None
Falsification: Would be falsified by uniform role distribution

---

## Analysis 5: Temporal Stratification (H5)

**Question:** Does uncategorized vocabulary drift through the manuscript (scribal variants)?

### Temporal Rate

| Period | Uncategorized Rate |
|--------|-------------------|
| First third | 35.0% |
| Middle third | 35.6% |
| Last third | 31.7% |

**Trend: -3.3 percentage points (stable)**

### Vocabulary Overlap

| Metric | Value |
|--------|-------|
| First third unique types | 2,505 |
| Last third unique types | 6,750 |
| Shared types | 770 |
| **Overlap rate** | **9.1%** |

### Section Variation

| Section | Uncategorized Rate | Token Count |
|---------|-------------------|-------------|
| A (Astronomy?) | 54.8% | 1,514 |
| B (Biological?) | 21.8% | 6,101 |
| Z (Zodiac?) | 52.8% | 1,631 |
| S (Stars?) | 34.0% | 10,333 |

### Hand Variation

| Hand | Uncategorized Rate |
|------|-------------------|
| Hand 2 | **24.8%** (lowest) |
| Hand 4 | **45.3%** (highest) |

### Interpretation

**The 9.1% vocabulary overlap is the most striking finding.**

This means:
- Uncategorized tokens are **almost entirely section-specific**
- They are **not** a uniform missing vocabulary
- They are **local phenomena** tied to specific manuscript regions

The rate stability (35.0% -> 31.7%) combined with vocabulary drift suggests:
- **The scribal practice remained consistent** (stable rate)
- **But the specific tokens varied** by section/hand/quire

### H5 Verdict: WEAK (Partial Support)

Evidence FOR: Extreme vocabulary drift (9.1% overlap)
Evidence AGAINST: Stable temporal rate
Falsification: Partial - scribal RATE is stable, but vocabulary is local

---

## Synthesis: What Are Uncategorized Tokens?

### They Are

1. **Boundary/Position Markers** (H1 supported)
   - Line-initial enrichment: 2.16x
   - Folio-start enrichment: 1.48x
   - Function: Initiate lines/sections

2. **Section-Specific Scaffolding** (H4, H5 supported)
   - Only 9.1% vocabulary overlap across manuscript
   - Cluster near routine operations, avoid critical ones
   - Function: Local organizational context

3. **Human-Track (Non-Executable)** (all tests consistent)
   - Never appear at forbidden seams
   - Avoid hazard zones
   - Don't affect constraint topology

### They Are NOT

1. **Sensory Checkpoints** (H2 falsified)
   - Avoid hazard zones, never at forbidden seams

2. **Quantitative Markers** (H3 null)
   - No tally/counter behavior

3. **Uniform Missing Vocabulary**
   - 9.1% overlap proves locality

---

## Constraint for Interpretive Model

If uncategorized tokens:
- Do not alter execution flow (not at forbidden seams)
- Do not cluster at judgment points (avoid hazards)
- Appear at structural boundaries (line-initial, folio-start)
- Show extreme locality (9.1% overlap)

Then they must be treated as **HUMAN-TRACK INSTRUMENTATION**, not system logic.

**They encode WHERE the operator is in the manuscript, not WHAT the operator does.**

---

## Recommendation for Next Phase

### DO NOT

- Assign classes to uncategorized tokens
- Merge them into the grammar
- Treat them as semantic content

### DO

- Test if they correlate with physical page layout
- Test if they mark quire/gathering boundaries
- Test if they encode line numbers or visual references

### Key Question

> Are uncategorized tokens a COORDINATE SYSTEM for manuscript navigation?

The line-initial enrichment (2.16x) and section-specificity (9.1% overlap) strongly suggest a human-facing indexing system layered over the operational grammar.

---

## Files Generated

- `uncategorized_token_analysis.py` - Main analysis script
- `behavioral_role_analysis_report.md` - This report

---

*Phase UTC complete. Model diagnostic only - grammar remains frozen.*
