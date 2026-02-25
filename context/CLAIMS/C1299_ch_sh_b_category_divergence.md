# C1299: ch-sh B-Specific Category Divergence

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

Sister PREFIXes ch and sh diverge in 8-category operational profiles in Currier B (chi2 = 85.7, dof = 7, p = 9.4e-16, Cramer's V = 0.121, JSD = 0.011), despite being category-identical in Currier A (C1268, V = 0.021, p = 0.48). This divergence survives section control (combined within-section chi2 = 113.3, Fisher p = 3.4e-10) and position control (present in both halves of lines).

## Category Profiles

| Category | ch | sh | Difference |
|----------|----|----|------------|
| OPERATION | 25.9% | 30.8% | sh +4.9pp |
| THERMAL | 20.9% | 24.0% | sh +3.1pp |
| FLOW | 11.8% | 8.5% | ch +3.3pp |
| CONTAINMENT | 9.6% | 6.7% | ch +2.8pp |
| TRANSITION | 13.8% | 17.3% | sh +3.5pp |
| MARKING | 9.1% | 5.7% | ch +3.4pp |
| STAGING | 6.0% | 4.7% | ch +1.3pp |
| MONITORING | 3.0% | 2.2% | ch +0.8pp |

## Mechanism

ch selects a broader MIDDLE vocabulary including minority categories (FLOW, CONTAINMENT, MARKING). sh concentrates on high-frequency MIDDLEs in OPERATION and THERMAL. The divergence is MIDDLE-level: ch-specific MIDDLEs include ot (91.9% ch among h-base), l (88.2%), ckh (76.4%), cth (76.3%). sh concentrates on edy (OPERATION) at 21.2%.

## Scope Distinction

C1268 remains valid: ch/sh are category-identical **in Currier A** (V = 0.021). B's richer vocabulary reveals PREFIX-MIDDLE selectivity differences that A's smaller, more uniform vocabulary cannot expose. This is a system-dependent effect, not a contradiction.

## Method

- N = 5,821 tokens (ch = 3,492; sh = 2,329)
- 2 x 8 contingency table, chi-squared test
- Section control: separate chi-squared per section, Fisher-combined
- Position control: split lines at midpoint, test each half
- Mechanism: per-MIDDLE ch/(ch+sh) fraction analysis

## Extends

- C1268 (ch/sh orthogonal in A, V = 0.021) -- B reveals divergence absent in A
- C408 (sister pairs) -- ch/sh sisterhood is system-dependent
- C911 (ch/sh select e-family MIDDLEs) -- B adds category-level differentiation within shared MIDDLE families

## Falsifiability

Would be falsified if the divergence were driven by a single section or a single outlier MIDDLE.

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T3_ch_sh_control)
- `_tmp_chsh_divergence.py` (mechanism decomposition, scratch)
