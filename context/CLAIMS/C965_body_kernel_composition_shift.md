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

This is NOT a diversity collapse: the number of distinct kernels per line is flat, and kernel entropy is flat. The system does not lose options; it changes which kernel it favors.

**Risk profile migration (RISK_PROFILE_MIGRATION phase):** The kernel composition shift operates exclusively in non-hazard tokens (safe pool: h_fraction partial rho = +0.090, p=0.002; hazard pool: rho = +0.048, p=0.23). Hazard sub-group mix is completely flat through body lines (T02, T03, T05 all FAIL). The controller does not reduce what it can do — it changes what kinds of mistakes are still possible. Late body lines shift toward monitoring vocabulary (h-kernel, ch/sh prefix) within the safe operational space, while the hazard management strategy remains invariant. AX scaffold tokens increase proportionally in late lines not because extra scaffolding is added, but because fewer active interventions remain — the scaffold fraction rises as the intervention fraction falls (C568: AX is structurally obligatory, not optional).

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
- `phases/RISK_PROFILE_MIGRATION/scripts/04_kernel_mediation_hazard_vs_safe.py` (safe-only localization)
- `phases/RISK_PROFILE_MIGRATION/results/07_integrated_verdict.json` (phase verdict: WEAK)
- Related: C677, C842, C932, C963, C458, C568

## Status

CONFIRMED — h_fraction and e_fraction both survive Bonferroni correction and line-length control.
