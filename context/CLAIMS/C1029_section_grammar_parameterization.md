# C1029: Section-Parameterized Grammar Weights

**Tier:** 2 | **Scope:** B | **Phase:** SECTION_GRAMMAR_VARIATION

## Statement

The 49-class grammar topology is shared across manuscript sections (zero section-only transitions observed; all section transitions are proper subsets of the global matrix), but transition weights are section-modulated at the same scale as REGIME variation (mean pairwise JSD: section 0.3245 vs REGIME 0.3195, ratio 1.016x). 42.6% of classes (20/47 tested) show statistically significant section-dependent transitions (chi-squared, p<0.05). This extends C979 (REGIME modulates weights not topology) to the section dimension: the universal grammar (C124) has universal topology but is parameterized by both REGIME and section independently.

## Evidence

### Pairwise JSD Between Sections

| Pair | JSD |
|------|-----|
| BIO vs COSMO | 0.378 |
| BIO vs HERBAL | 0.307 |
| BIO vs STARS_RECIPE | 0.238 |
| COSMO vs HERBAL | 0.399 |
| COSMO vs STARS_RECIPE | 0.352 |
| HERBAL vs STARS_RECIPE | 0.273 |
| **Mean** | **0.325** |

### Pairwise JSD Between REGIMEs (comparison)

| Pair | JSD |
|------|-----|
| R1 vs R2 | 0.329 |
| R1 vs R3 | 0.216 |
| R1 vs R4 | 0.323 |
| R2 vs R3 | 0.339 |
| R2 vs R4 | 0.390 |
| R3 vs R4 | 0.320 |
| **Mean** | **0.320** |

### Topology Invariance

| Section | Non-zero Transitions | Section-Only | Global Coverage |
|---------|---------------------|-------------|-----------------|
| BIO | 1053 | 0 | 61.0% |
| HERBAL | 893 | 0 | 51.7% |
| COSMO | 557 | 0 | 32.3% |
| STARS_RECIPE | 1369 | 0 | 79.3% |
| **GLOBAL** | **1726** | — | 100% |

Coverage varies by sample size (994–7027 tokens per section) but no section introduces transitions absent from the global matrix. Topology is shared.

### Section-Specific Properties

| Section | Self-Loop Rate | Spectral Gap | Tokens |
|---------|---------------|-------------|--------|
| BIO | 0.063 | 0.840 | 5324 |
| COSMO | 0.055 | 0.708 | 994 |
| HERBAL | 0.043 | 0.849 | 2305 |
| STARS_RECIPE | 0.066 | 0.828 | 7027 |
| GLOBAL | 0.061 | 0.812 | 16054 |

### Role Self-Loop Ordering by Section

The role self-loop ordering is section-dependent, not universal:

| Section | FQ | EN | FL | Ordering |
|---------|-----|-----|-----|----------|
| BIO | 0.069 | **0.085** | 0.030 | EN > FQ > FL |
| HERBAL | **0.086** | 0.041 | 0.021 | FQ > EN > FL |
| COSMO | **0.124** | 0.024 | 0.044 | FQ > FL > EN |
| STARS_RECIPE | **0.109** | 0.069 | 0.074 | FQ > FL > EN |

BIO's EN dominance is consistent with C552 (thermal-intensive, +EN enriched).

## Provenance

C124, C552, C553, C979

**Script:** `phases/SECTION_GRAMMAR_VARIATION/scripts/section_grammar_variation.py`
**Results:** `phases/SECTION_GRAMMAR_VARIATION/results/section_grammar_variation.json`
