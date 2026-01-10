# Second-Wave Record Geometry Analysis - Currier A

**Date:** 2026-01-09
**Status:** COMPLETE
**Constraint outcome:** NONE (descriptive findings only)

---

## Executive Summary

This analysis examined record-internal usage geometry in Currier A using DA-segmented blocks. All findings describe **usage patterns**, not grammar rules. No constraints proposed.

**Mode:** BLOCK_SEGMENTED (DA masked as BOUNDARY)

---

## Dataset

| Metric | Value |
|--------|-------|
| Total entries | 1,829 |
| Multi-block entries | 780 (42.6%) |
| Total tokens analyzed | 33,595 |

---

## Analysis 1: Block-Index × Component Distribution

### Entropy by Block Position

| Block Index | Token Count | Prefix Entropy | Suffix Entropy | Middle Entropy | Unique Middles |
|-------------|-------------|----------------|----------------|----------------|----------------|
| FIRST | 3,874 | 2.596 | 3.279 | 6.198 | 305 |
| MIDDLE | 9,376 | 2.585 | 3.328 | 6.392 | 467 |
| LAST | 3,156 | 2.699 | 3.431 | 6.419 | 301 |
| ONLY | 17,189 | 2.563 | 3.390 | 6.763 | 697 |

### Interpretation

- **MIDDLE entropy increases toward later blocks**: FIRST (6.198) → MIDDLE (6.392) → LAST (6.419)
- **ONLY blocks have highest MIDDLE entropy** (6.763) - single-block entries use most diverse vocabulary
- **Prefix entropy relatively stable** across positions (2.56-2.70)

**Pattern:** Soft vocabulary diversification gradient. NOT a constraint (no prohibition, no necessity).

### Prefix Distribution by Block Index

| Prefix | FIRST | MIDDLE | LAST | ONLY |
|--------|-------|--------|------|------|
| ch | 25.5% | 26.6% | 25.1% | 27.4% |
| sh | 10.7% | 9.7% | 8.9% | 9.9% |
| qo | 12.0% | 11.3% | 11.3% | 9.1% |
| ct | 3.5% | 5.0% | 5.1% | 4.3% |

**Observations:**
- qo slightly enriched in FIRST blocks (12.0% vs 9.1% in ONLY)
- ct slightly depleted in FIRST blocks (3.5% vs 5.1% in LAST)
- ch stable across all positions

These are **mild tendencies** consistent with earlier C250.a findings.

---

## Analysis 2: Position-in-Block Effects

### Token Distribution by Position

| Position | Tokens |
|----------|--------|
| INITIAL | 4,007 |
| INTERNAL | 24,941 |
| FINAL | 4,007 |
| ONLY | 640 |

### Prefix Enrichment vs Shuffled Baseline

| Prefix | INITIAL | INTERNAL | FINAL | Baseline |
|--------|---------|----------|-------|----------|
| ch | 20.2% ▼ | 27.7% | 27.5% | 26.7% |
| sh | 8.7% | 10.7% | 6.7% ▼ | 9.9% |
| qo | 12.8% ▲ | 10.1% | 8.8% | 10.3% |

**Key findings:**
- ch is DEPLETED at block-initial position (20.2% vs 27.7% internal)
- qo is ENRICHED at block-initial position (12.8% vs 10.3% baseline)
- sh is DEPLETED at block-final position (6.7% vs 9.9% baseline)

**Interpretation:** Modest positional tendencies. The effect sizes (2-7%) are statistically real but do NOT constitute illegality. Tokens with any prefix can appear at any position.

### Suffix Enrichment by Position

| Position | Top 5 Suffixes |
|----------|---------------|
| INITIAL | -or (18.6%), -ol (18.4%), -ey (10.8%), -y (10.7%), -aiin (8.7%) |
| INTERNAL | -ol (19.7%), -y (14.7%), -or (14.3%), -ey (12.9%), -aiin (7.7%) |
| FINAL | -ol (22.9%), -y (16.7%), -ey (11.2%), -or (8.5%), -dy (8.0%) |

**Observations:**
- -or enriched at INITIAL (18.6% vs 8.5% at FINAL)
- -ol enriched at FINAL (22.9% vs 18.4% at INITIAL)
- -y enriched at FINAL (16.7% vs 10.7% at INITIAL)

These are **soft usage preferences**, not structural rules.

---

## Analysis 3: Block-to-Block Similarity by Coordinate

### Jaccard Similarity (sampled)

| Comparison | Middle-Jaccard | Full-Jaccard | N |
|------------|----------------|--------------|---|
| FIRST ↔ FIRST | 0.053 | 0.009 | 780 |
| LAST ↔ LAST | 0.026 | 0.007 | 780 |
| FIRST ↔ LAST | 0.028 | 0.005 | cross |

### Interpretation

- **Very low similarity** across all comparisons (< 0.06)
- **No strong coordinate-based vocabulary clustering**
- FIRST blocks are slightly more similar to other FIRST blocks (0.053) than LAST blocks are to other LAST blocks (0.026)

**Conclusion:** Block content is NOT determined by block position. Each block draws from the full vocabulary. Domain continuity is absent at this level.

---

## Analysis 4: Rare-Item Structural Placement

### Definition
- **RARE MIDDLEs:** lowest-frequency decile (104 items, freq ≤ 1)

### Rare MIDDLE Rate by Position

| Position | Rare | Total | Rate |
|----------|------|-------|------|
| FIRST | 5 | 1,629 | 0.31% |
| MIDDLE | 26 | 3,966 | 0.66% |
| LAST | 8 | 1,380 | 0.58% |
| ONLY | 65 | 7,342 | 0.89% |

### Rare MIDDLE Rate by Entry Type

| Entry Type | Rare | Total | Rate |
|------------|------|-------|------|
| Single-block | 65 | 7,342 | 0.89% |
| Multi-block | 39 | 6,975 | 0.56% |
| Low articulation (0-1 DA) | 68 | 7,676 | 0.89% |
| High articulation (2+ DA) | 36 | 6,641 | 0.54% |

### Interpretation

- **Rare items cluster in simpler entries** (single-block, low articulation)
- **Rare items avoid FIRST blocks** (0.31%) - canonical positions use common vocabulary
- **ONLY blocks have highest rare rate** (0.89%)

**Pattern:** Simple entries tolerate outliers; complex entries use core vocabulary. This is a **usage regularity**, not a constraint (rare items can appear anywhere).

---

## Analysis 5: Complexity Gradient Inside Records

### Metrics by Block Index (multi-block entries only)

| Block | Mean Tokens | Median | Prefix Div | Suffix Div | Middle Div | N |
|-------|-------------|--------|------------|------------|------------|---|
| FIRST | 5.0 | 4.0 | 2.27 | 1.96 | 1.82 | 780 |
| MIDDLE | 4.6 | 4.0 | 2.22 | 2.00 | 1.81 | 2,038 |
| LAST | 4.0 | 3.0 | 1.94 | 1.71 | 1.60 | 780 |

### Interpretation

- **FRONT-HEAVY confirmed (MODEST):** FIRST blocks average 5.0 tokens, LAST blocks average 4.0
- **Ratio = 1.25** (not meeting 1.5x threshold for "strong")
- **Diversity also decreases:** FIRST blocks have higher prefix/suffix diversity

**Conclusion:** Front-heavy is a **tendency**, confirmed at modest level. Not a rule (no illegality for balanced or back-heavy entries).

---

## Summary of Findings

| Analysis | Finding | Status |
|----------|---------|--------|
| 1. Block-Index × Components | MIDDLE entropy increases toward later blocks | Descriptive |
| 2. Position-in-Block | ch depleted INITIAL, qo enriched INITIAL | Descriptive |
| 3. Block Similarity | No coordinate-based vocabulary clustering | Null |
| 4. Rare-Item Placement | Rare items cluster in simple entries | Descriptive |
| 5. Complexity Gradient | FRONT-HEAVY (modest, ratio 1.25) | Confirms C250.a |

---

## Constraint Status

**NO NEW CONSTRAINTS.** All findings describe **usage patterns within a flexible structure**.

| Finding | Why Not a Constraint |
|---------|---------------------|
| MIDDLE entropy gradient | No prohibition on high/low entropy blocks |
| Positional prefix tendencies | All prefixes appear at all positions |
| Rare-item clustering | Rare items CAN appear anywhere |
| Front-heavy | Back-heavy entries exist; no illegality |

---

## Integration with Existing Constraints

| Constraint | Status |
|------------|--------|
| C250 (64.1% repetition) | UNCHANGED |
| C250.a (block-aligned repetition) | CONFIRMED by similarity patterns |
| C422 (DA articulation) | LEVERAGED as block boundary |
| C234 (POSITION_FREE) | CONFIRMED - no positional illegality found |

---

## Files Created

| File | Purpose |
|------|---------|
| `record_geometry_analysis.py` | Second-wave analysis script |
| `RECORD_GEOMETRY_SYNTHESIS.md` | This synthesis document |

---

## Conclusion

Record geometry in Currier A exhibits coherent but flexible patterns:

1. **Blocks are structurally interchangeable** - no position-specific vocabulary
2. **Entropy increases toward entry periphery** - FIRST blocks more canonical
3. **Front-heavy is a tendency, not a rule** - confirmed at modest level
4. **Rare items tolerated in simple contexts** - complex entries use core vocabulary

> Record structure behaves coherently but flexibly, consistent with a human-designed, non-semantic registry.

**CONSTRAINT COUNT UNCHANGED: 423**
