# C1148: Dark Pipeline Frequency Profiles Are Hyper-Modulated Across Sections

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / section differentiation
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

Dark-pipeline MIDDLEs show **3.9x greater** inter-section frequency divergence than the PP baseline (C1134), making the dark pipeline the primary vehicle for section-level vocabulary modulation.

### Jensen-Shannon Divergence (Pairwise)

| Section Pair | JS Divergence |
|-------------|---------------|
| B vs C | 0.619 |
| B vs T | 0.619 |
| C vs T | 0.555 |
| S vs T | 0.510 |
| C vs S | 0.475 |
| C vs H | 0.462 |
| H vs T | 0.457 |
| B vs H | 0.431 |
| B vs S | 0.385 |
| H vs S | 0.319 |
| **Mean** | **0.483** |

### Comparison to C1134 Baseline

| Metric | Dark Pipeline | PP Baseline (C1134) | Ratio |
|--------|--------------|--------------------| ------|
| Mean JS | 0.483 | 0.124 | **3.90x** |

### Section-Level Dark Pipeline Statistics

| Section | MIDDLEs Used | Tokens | Herfindahl |
|---------|-------------|--------|------------|
| S | 237 | 860 | 0.015 |
| B | 110 | 386 | 0.035 |
| H | 129 | 256 | 0.013 |
| C | 71 | 120 | 0.021 |
| T | 49 | 74 | 0.030 |

Section S uses the most diverse dark-pipeline vocabulary (237 MIDDLEs) while section T uses the fewest (49). The within-section Herfindahl values are uniformly low (0.013-0.035), indicating no single MIDDLE dominates within any section.

## Evidence

- Phase 409, Test 6: Pairwise JS divergence on dark-pipeline MIDDLE frequency profiles across 5 sections
- 300 dark-pipeline MIDDLEs, 1,696 tokens total
- C1134 baseline: mean JS = 0.124 across all PP MIDDLEs

## Implication

The dark pipeline operates as a **hyper-modulated frequency channel**. While the grammar channel (bridge MIDDLEs) achieves section differentiation through moderate frequency shifts (JS=0.124, C1134), the dark pipeline achieves nearly 4x greater differentiation. Each section draws on a largely distinct subset of the 300 dark-pipeline MIDDLEs, with minimal cross-section overlap. This is consistent with the dark pipeline's role as identification vocabulary: section identity is encoded primarily through WHICH dark-pipeline MIDDLEs appear, while grammar structure uses the same bridge MIDDLEs modulated at lower intensity.

Combined with C1146 (bridge anti-correlation), this reveals a dual-channel architecture: bridge MIDDLEs provide stable grammar infrastructure with moderate modulation, while dark-pipeline MIDDLEs provide section-specific identification with extreme modulation.

## Provenance

- Source: Phase 409, Test 6
- Related: C1134 (PP frequency modulation, JS=0.124), C1135 (dark pipeline section concentration, Herf=0.716), C1137 (dark pipeline HT substrate), C1146 (bridge anti-correlation)
