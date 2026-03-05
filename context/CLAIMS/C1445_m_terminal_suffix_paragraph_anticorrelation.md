# C1445: m-Terminal and Suffix Anticorrelation at Paragraph Level

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, suffix, paragraph, anticorrelation, section, C1439, C1440, C1441
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

Across 486 paragraphs with 3+ tokens, m-terminal fraction and suffix fraction anticorrelate (Spearman rho=-0.199, p=0.00001). Paragraphs that use more m-terminal closure use less suffix attachment. Bio section uses least m-terminal (0.57%), Stars/Recipe uses highest suffix (52.0%). The two closure layers are partial substitutes at paragraph scale, extending the token-level orthogonality (C1439) to paragraph-level budget allocation.

## Evidence

### Paragraph-level statistics

| Metric | Mean across 486 paragraphs |
|--------|---------------------------|
| m-terminal fraction | 1.27% |
| Suffix fraction | 49.7% |
| Both (m-term AND suffixed) | 0.06% |
| Neither (bare, non-m-term) | 39.7% |

### Correlation

Spearman rho = -0.199, p = 0.00001. Weak but highly significant anticorrelation. Paragraphs trade off between m-terminal closure and suffix attachment.

### Section variation

| Section | N paras | m-term mean | Suffix mean |
|---------|---------|-------------|-------------|
| B (Bio) | 90 | 0.57% | 46.8% |
| H (Herbal) | 69 | 1.97% | 45.0% |
| C (Cosmo) | 26 | 2.46% | 46.7% |
| T (Zodiac) | 15 | 1.56% | 51.4% |
| S (Stars/Recipe) | 286 | 1.19% | 52.0% |

Bio has the lowest m-terminal usage, consistent with m's anti-THERMAL profile (C1435, C1436). Stars/Recipe has the highest suffix rate. Section modulates both layers but the anticorrelation is present within sections as well as across them.

### Co-occurrence rarity

Mean both fraction = 0.06%. Tokens that have BOTH m-terminal MIDDLE AND a suffix are extremely rare across all paragraphs, consistent with C1439's 1-token overlap and C1441's active exclusion.

## Interpretation

The paragraph distributes its closure work between two layers: MIDDLE terminals (primarily m for body-line closure) and suffixes (for parametric specification). When one layer is used more heavily, the other is used less. This is a design-level budget allocation, not a statistical artifact, because the same character `m` operating at two grammar levels (MIDDLE terminal vs suffix component) is actively excluded by the grammar (C1441).

## Falsification Criteria

1. If paragraph-level m/suffix correlation changes sign (positive) under section control
2. If the "both" fraction exceeds 2%

## Method

- 486 paragraphs with 3+ tokens extracted from Currier B
- Per-paragraph: fraction of tokens with m-terminal, fraction with any suffix, fraction with both, fraction with neither
- Spearman correlation between m-terminal fraction and suffix fraction
- Section-stratified means

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` (T9)

## Dependencies

- C1439 (m-terminal and -am suffix orthogonal)
- C1440 (three-tier terminal opacity gradient)
- C1441 (active terminal-suffix exclusion)
- C1435 (m-terminal body-line exclusivity)
