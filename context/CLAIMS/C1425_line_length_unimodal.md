# C1425: Line Length Unimodal Distribution

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, length, distribution
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C958 (opener determines line length), C677 (line complexity trajectory)
**Relates to:** C357 (lines 3.3x more regular than random), C680 (positional feature prediction)

---

## Statement

Currier B lines have a unimodal length distribution: mean=9.54 tokens, median=10, CV=0.340, mode=10 (19.9% of lines). 94.7% of lines fall within 3-13 tokens. Header lines (paragraph-initial) average 10.25 tokens vs body 9.34 (ratio 1.097x). Section variation: BIO shortest (8.97), COSMO longest (11.65, inflated by outlier long lines up to 54 tokens). Excluding COSMO, max=16 and CV drops to ~0.27.

### Distribution Shape

| Length | % of Lines |
|--------|-----------|
| 1-4 | 4.8% |
| 5-7 | 16.0% |
| 8-10 | 42.5% |
| 11-13 | 34.1% |
| 14-16 | 2.3% |
| 17+ | 0.5% |

### Section Variation

| Section | Mean | Median | Std | Max |
|---------|------|--------|-----|-----|
| BIO | 8.97 | 9 | 2.33 | 16 |
| HERBAL | 9.11 | 10 | 2.65 | 14 |
| ZODIAC | 9.59 | 10 | 2.61 | 14 |
| STARS_RECIPE | 9.85 | 10 | 2.48 | 16 |
| COSMO | 11.65 | 10 | 9.14 | 54 |

### Implication

Line length is continuous and unimodal, not discrete. The modal line of 10 tokens is universal across sections. No discrete line-type classes based on length.

---

## Falsification Criteria

1. If a bimodal or multimodal length distribution is found in any section (excluding COSMO outliers)
2. If header-body length ratio exceeds 1.3x (would indicate structurally distinct header format)

---

## Method

- 23,096 tokens across 2,420 lines in 83 B folios (H-track, labels excluded)
- Length = token count per line
- Header = paragraph-initial lines (535), body = all others (1,885)

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T1)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`
