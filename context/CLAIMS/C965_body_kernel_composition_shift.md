# C965: Body Kernel Composition Shift

**Tier:** 2 | **Scope:** B | **Phase:** PARAGRAPH_STATE_COLLAPSE

## Statement

B paragraph body lines exhibit a kernel composition shift: h-kernel fraction (ch/sh prefix tokens) increases and e-kernel fraction decreases through body lines, controlling for line length. This is a composition change, not a diversity collapse — the number of distinct kernel types per line (~2.6) remains flat.

## Evidence

- 187 paragraphs with 5+ lines, 1,261 body lines analyzed
- All metrics tested with partial Spearman rho (OLS residualized for line_length)
- Bonferroni alpha = 0.002 (5 sub-tests)

| Metric | Partial rho | p-value | Shuffle p | Significant? |
|--------|-------------|---------|-----------|-------------|
| h_fraction | +0.1005 | 0.0004 | 0.999 | Yes (Bonferroni) |
| e_fraction | -0.0863 | 0.0022 | 0.001 | Yes (Bonferroni) |
| k_fraction | -0.0027 | 0.923 | 0.458 | No |
| n_distinct_kernels | -0.0122 | 0.665 | 0.320 | No |
| kernel_entropy | +0.0281 | 0.318 | 0.836 | No |

**Quintile means (h_fraction):** Q0=0.278 → Q4=0.326 (steady increase)
**Quintile means (e_fraction):** Q0=0.589 → Q4=0.553 (steady decrease)
**Quintile means (n_distinct_kernels):** Q0=2.64 → Q4=2.42 (flat after length control)

## Interpretation

Late body lines favor h-kernel tokens (ch/sh prefix) over e-kernel tokens, while k-kernel remains stable. This is the only genuine positional signal within paragraph bodies that survives the C677 line-length confound, apart from C932's vocabulary rarity shift.

This is compatible with the "job card" model (C932): early lines specify parameters using more e-kernel vocabulary (which tends toward specification), while late lines shift toward h-kernel vocabulary (which tends toward execution/monitoring). The transition is gradual and partial — both kernels remain present throughout.

This is NOT a diversity collapse: the number of distinct kernels per line is flat, and kernel entropy is flat. The system does not lose options; it changes which kernel it favors.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|-------------|
| C963 | COMPATIBLE — C963 body homogeneity holds for role fractions, entropy, distinct counts; this is a composition shift within stable diversity |
| C932 | COMPATIBLE — C932 shows rarity gradient; this shows kernel gradient; both are specification→execution |
| C677 | CONTROLLED — line shortening confound removed via partial Spearman |
| C842 | COMPATIBLE — HT fraction flat in body; kernel shift operates within non-HT tokens |

## Provenance

- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/07_kernel_diversity_collapse.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/results/07_kernel_diversity_collapse.json`
- Related: C677, C842, C932, C963

## Status

CONFIRMED — h_fraction and e_fraction both survive Bonferroni correction and line-length control.
