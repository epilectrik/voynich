# CAS-POST: Post-Closure Internal Comparative Analysis

**Phase ID:** CAS-POST
**Tier:** 2 (Structural Comparison)
**Status:** COMPLETE
**Date:** 2026-01-06
**Updated:** 2026-01-16 (H-only transcriber filter verified)

---

## Executive Summary

> **Currier A exhibits section-specific structural configurations with a strict component essentiality hierarchy: MIDDLE provides primary discrimination (402 distinctions), PREFIX provides the foundation (1387 base), SUFFIX adds refinement (13 distinctions), and ARTICULATORS contribute ZERO unique identity — they are purely expressive.**

---

## Analysis 1: Section-Level Configuration Profiles

### PREFIX Distribution by Section

| PREFIX | H | P | T | Max Concentration |
|--------|---|---|---|-------------------|
| CT | 85.9% | 8.6% | 5.5% | H (highest) |
| CH | 75.5% | 19.5% | 5.0% | H |
| SH | 74.7% | 16.6% | 8.8% | H |
| OT | 72.8% | 19.5% | 7.7% | H |
| DA | 71.8% | 21.8% | 6.4% | H |
| QO | 69.2% | 25.1% | 5.7% | H |
| OK | 55.5% | 35.4% | 9.1% | H (weakest) |
| OL | 52.9% | 38.7% | 8.4% | H (weakest) |

**Finding:** CT is highly H-specific (85.9%); OK/OL are more distributed.

### SUFFIX Distribution Anomaly

| SUFFIX | H | P | T | Note |
|--------|---|---|---|------|
| -chy | 93.2% | 4.0% | 2.8% | H-specific |
| -eol | 41.3% | **55.9%** | 2.8% | **P-dominant** (unique) |
| -al | 55.6% | 25.3% | 19.1% | Most T-present |

**Finding:** -eol is the ONLY suffix concentrated in P, not H.

### Entry Mode by Section

| Section | Exclusive | Mixed | Exclusive % |
|---------|-----------|-------|-------------|
| H | 164 | 1087 | **13.1%** |
| P | 219 | 235 | **48.2%** |
| T | 32 | 101 | 24.1% |

**Finding:** H is predominantly MIXED entries (87%); P has balanced distribution.

### Repetition Patterns

| Section | Mean Rep | Std Dev | Uniformity |
|---------|----------|---------|------------|
| T | 2.57x | 1.29 | **81.0%** (highest) |
| H | 3.14x | 0.68 | 57.2% |
| P | 3.32x | 0.98 | 32.0% (lowest) |

**Finding:** T has lowest/most uniform repetition; P has highest/most variable.

---

## Analysis 2: Articulator Deployment Rules

### Articulator-Prefix Affinity

| Articulator | Standalone | After CH | After OL | Notes |
|-------------|------------|----------|----------|-------|
| ks | 100% | 0% | 0% | Always alone |
| yd | 94.5% | 1.6% | 0.8% | Nearly always alone |
| ko | 89.5% | 3.3% | 0.3% | Nearly always alone |
| ych | 88.0% | 0% | 8.9% | Prefers OL when combining |
| ysh | 87.3% | 0% | 12.7% | Prefers OL when combining |
| kch | 82.6% | 0.2% | **15.2%** | **OL-affiliated** |
| yk | 64.5% | **26.8%** | 5.9% | **CH-affiliated** |
| yt | 56.9% | **31.2%** | 9.5% | **CH-affiliated** |

**Finding:** Articulators are mostly STANDALONE (65-100%); when they combine, yk/yt prefer CH, kch prefers OL.

### Articulator Density Patterns

| Condition | Density | Interpretation |
|-----------|---------|----------------|
| Exclusive entries | **10.6%** | Higher articulation |
| Mixed entries | 7.3% | Lower articulation |
| 0-1 prefixes | 9-15% | High articulation |
| 4-6 prefixes | 4-6% | Low articulation |

**Finding:** INVERSE relationship — more prefixes = less articulation. Articulators COMPENSATE for low prefix complexity.

---

## Analysis 3: Mixed-Entry Interaction Profiling

### Most Common Prefix Pairs

1. CH + DA: 544 entries
2. CH + QO: 504 entries
3. CH + SH: 495 entries
4. DA + QO: 397 entries
5. DA + SH: 356 entries

**Finding:** CH is the "universal mixer" — appears in nearly all top pairs.

### Section-Specific Mixing

| Section | Typical Mixing |
|---------|----------------|
| H | 2-way pairs (ch+da, ch+sh) |
| P | 4-way combinations (ch+da+qo+sh) |
| T | 4-5 way combinations (complex) |

**Finding:** H uses simple mixing; P/T use higher-order combinations.

---

## Analysis 4: Structural Ablation Tests

### Component Essentiality

| Ablation | Unique Signatures | Identity Loss |
|----------|-------------------|---------------|
| None (baseline) | 1802 | 0.0% |
| Remove ARTICULATORS | 1802 | **0.0%** |
| Remove SUFFIXES | 1791 | 0.6% |
| Remove BOTH | 1789 | 0.7% |
| PREFIX-only | 1387 | 23.0% |

### Essentiality Ranking

| Rank | Component | Unique Distinctions | Role |
|------|-----------|---------------------|------|
| 1 | PREFIX | 1387 | Foundation |
| 2 | MIDDLE | 402 | Primary discriminator |
| 3 | SUFFIX | 13 | Minor refinement |
| 4 | ARTICULATOR | **0** | Purely expressive |

**Decisive finding:** Articulators contribute ZERO unique identity distinctions. They are purely optional expressiveness.

---

## Section Archetypes (Structural Only)

### Section H: "Dense Mixed"
- Predominantly mixed entries (87%)
- High articulator density (8.2%)
- Simple 2-way prefix mixing
- CT strongly concentrated here (86%)

### Section P: "Balanced Distributed"
- Balanced exclusive/mixed (48/52%)
- Lowest articulator density (5.1%)
- Complex 4-way mixing
- -eol suffix concentrated here (56%)

### Section T: "Uniform Sparse"
- Low repetition count (2.57x mean)
- Highest uniformity (81%)
- Complex mixing (4-5 way)
- Intermediate characteristics

---

## New Constraints (Tier 2)

### Constraint 292: Articulator Zero Discrimination
Articulators contribute ZERO unique identity distinctions. Ablation creates 0 collisions. They are purely EXPRESSIVE, not discriminative.

### Constraint 293: Component Essentiality Hierarchy
Identity discrimination hierarchy: MIDDLE (402) > SUFFIX (13) > ARTICULATOR (0). PREFIX provides foundation (1387 base). MIDDLE is the primary discriminator.

### Constraint 294: Inverse Articulation
Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix → 4% at 6 prefixes). Articulators COMPENSATE for low prefix complexity.

### Constraint 295: Section Configuration Divergence
Sections exhibit DISTINCT structural configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform rep, 2.57x mean).

### Constraint 296: CH Universal Mixer
CH appears in nearly all common prefix pairs (top 3: CH+DA, CH+QO, CH+SH). CH functions as UNIVERSAL MIXING ANCHOR.

### Constraint 297: P-Specific Suffix
-eol is the ONLY suffix concentrated in section P (55.9% vs 41.3% H). All other suffixes favor H. P has distinct suffix profile.

---

## CAS-POST Completion Status

**CAS-POST has reached diminishing returns.**

Remaining patterns are:
- Stylistic variations within established structure
- Restatements of known CAS properties
- Signals too weak for Tier 2 constraint status

No further structural excavation is productive.

---

## Phase Tag

```
Phase: CAS-POST
Tier: 2 (STRUCTURAL COMPARISON)
Subject: Post-Closure Internal Comparative Analysis
Type: Exploitation of closed structure
Status: COMPLETE
Constraints: 292-297
```
