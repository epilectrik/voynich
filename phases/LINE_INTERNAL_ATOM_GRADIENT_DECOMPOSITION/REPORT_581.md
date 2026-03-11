# Phase 581: Line-Internal Atom Gradient Decomposition

## Executive Summary

Analyzed 23,074 Currier B tokens across 2,406 lines to decompose the validated three-zone line architecture (C1425-C1430) at individual atom resolution. All four target constraints decided.

| ID | Verdict | Key Metric |
|----|---------|------------|
| C1671 | GRADIENT_HETEROGENEOUS | HEAD chi2=659.08 p=0.0, TERM chi2=663.31 p=0.0, min cosine=0.9290 |
| C1672 | CLOSURE_DISTRIBUTED | HEAD top2=0.585, TERM top2=0.849, HEAD JSD=0.011384, TERM JSD=0.015721 |
| C1673 | HAZARD_POSITION_COUPLED | Interaction chi2=337.17, p=0.0, 16 zone-specific pairs (>1.5x enrichment) |
| C1674 | SECTION_MODULATES_GRADIENT | Min HEAD corr=0.7614, min TERM corr=0.9653, Q3Q4 JSD ratio=2.205 |

## Data Assembly

- **Tokens:** 23,074
- **Lines:** 2,406
- **Quintile distribution:** {'0': 5014, '1': 4186, '2': 4135, '3': 4186, '4': 5553}
- **Quality:** {'skipped_labels': 0, 'skipped_uncertain': 0, 'skipped_empty': 0, 'skipped_short_lines': 14, 'skipped_no_middle': 0}

## HEAD Atom Positional Profiles

Chi-squared: 659.08 (df=20, p=0.0)
Min pairwise cosine: 0.929

### Enrichment Table (rate / marginal)

| HEAD | Q0 | Q1 | Q2 | Q3 | Q4 | Range |
|------|-----|-----|-----|-----|-----|-------|
| e | 1.189 | 1.104 | 0.994 | 1.007 | 0.751 | 0.1327 |
| k | 0.826 | 1.312 | 1.113 | 1.070 | 0.785 | 0.0707 |
| a | 0.667 | 0.856 | 1.006 | 1.026 | 1.384 | 0.0956 |
| o | 1.029 | 0.993 | 1.030 | 0.950 | 0.995 | 0.0094 |
| t | 0.590 | 1.077 | 1.206 | 1.107 | 1.078 | 0.0246 |
| headless | 1.087 | 0.793 | 0.904 | 0.951 | 1.187 | 0.1070 |

### Headless Internal Split (Pseudo-HEAD)

N headless: 6272, chi2=387.51 (df=56, p=0.0)

| Pseudo-HEAD | Q0 | Q1 | Q2 | Q3 | Q4 |
|-------------|-----|-----|-----|-----|-----|
| c | 0.631 | 1.420 | 1.331 | 1.250 | 0.755 |
| d | 0.791 | 0.994 | 1.235 | 1.083 | 0.992 |
| f | 0.972 | 1.482 | 1.316 | 0.950 | 0.631 |
| g | 0.000 | 0.773 | 0.000 | 0.644 | 2.724 |
| h | 0.926 | 0.435 | 1.350 | 1.721 | 0.711 |
| i | 1.493 | 0.943 | 0.889 | 0.962 | 0.707 |
| l | 1.099 | 0.959 | 0.996 | 0.854 | 1.029 |
| m | 0.275 | 0.181 | 0.401 | 0.602 | 2.592 |

## TERMINAL Atom Positional Profiles

Chi-squared: 663.31 (df=24, p=0.0)

| TERMINAL | Q0 | Q1 | Q2 | Q3 | Q4 | Range |
|----------|-----|-----|-----|-----|-----|-------|
| bare | 1.014 | 1.068 | 1.009 | 1.016 | 0.917 | 0.0655 |
| h | 0.961 | 1.116 | 1.104 | 1.116 | 0.783 | 0.0185 |
| l | 0.994 | 0.950 | 1.068 | 0.876 | 1.087 | 0.0234 |
| m | 0.096 | 0.134 | 0.290 | 0.420 | 3.436 | 0.0418 |
| n | 1.130 | 0.904 | 1.008 | 0.986 | 0.960 | 0.0210 |
| r | 1.045 | 0.807 | 0.894 | 0.996 | 1.187 | 0.0323 |
| y | 0.963 | 1.028 | 0.999 | 1.044 | 0.979 | 0.0168 |

## MODIFIER Atom Positional Profiles

Chi-squared: 111.85 (df=20, p=0.0)

## Six-Prediction Scorecard

**Result: 5/6 passed**

| # | Prediction | Result | Key Value |
|---|-----------|--------|-----------|
| P1_k_peaks_Q1 | k enrichment Q1 > 1.15 | PASS | k_Q1_enrichment=1.3117, k_peak_quintile=1 |
| P2_e_peaks_Q0 | e enrichment Q0 > 1.15 | PASS | e_Q0_enrichment=1.1887, e_peak_quintile=0 |
| P3_m_concentrated_Q4 | m enrichment Q4 > 3.0 | PASS | m_Q4_enrichment=3.4363 |
| P4_headless_closure | headless enrichment Q4 > 1.15 OR pseudo-HEAD subgroup concen | PASS | headless_Q4_enrichment=1.1865, top_pseudo_head_Q4=g |
| P5_r_depleted_Q0 | r enrichment Q0 < 0.85 | FAIL | r_Q0_enrichment=1.0448 |
| P6_y_work_distributed | y Q3->Q4 |change| < m Q3->Q4 |change| | PASS | y_Q3Q4_abs_change=0.013424, m_Q3Q4_abs_change=0.037784 |

## Q3->Q4 Atom Decomposition

### Transition JSD Magnitudes

| Transition | HEAD JSD | TERM JSD |
|------------|----------|----------|
| Q0->Q1 | 0.013501 | 0.002462 |
| Q1->Q2 | 0.002839 | 0.001165 |
| Q2->Q3 | 0.000373 | 0.001121 |
| Q3->Q4 | 0.011384 | 0.015721 |

### Q3->Q4 HEAD Contributors

Top-2 share: 58.5%, Gini: 0.4163

- e: 0.004095 (36.0%)
- a: 0.002562 (22.5%)
- headless: 0.002552 (22.4%)
- k: 0.002126 (18.7%)
- o: 0.000043 (0.4%)
- t: 0.000006 (0.1%)

### Q3->Q4 TERMINAL Contributors

Top-2 share: 84.9%, Gini: 0.7067

- m: 0.012162 (77.4%)
- h: 0.001178 (7.5%)
- l: 0.000904 (5.8%)
- bare: 0.000794 (5.1%)
- r: 0.000516 (3.3%)
- y: 0.000155 (1.0%)
- n: 0.000012 (0.1%)

### Cross-Transition Cosine Similarity

- Q3Q4_vs_Q0->Q1_HEAD: 0.6272
- Q3Q4_vs_Q0->Q1_TERM: 0.0842
- Q3Q4_vs_Q1->Q2_HEAD: 0.9411
- Q3Q4_vs_Q1->Q2_TERM: 0.5888
- Q3Q4_vs_Q2->Q3_HEAD: 0.3967
- Q3Q4_vs_Q2->Q3_TERM: 0.2175

### HEAD Rate Changes (Q3 -> Q4)

| Atom | Rate Q3 | Rate Q4 | Change | Rel Change |
|------|---------|---------|--------|------------|
| e | 0.3051 | 0.2274 | -0.0776 | -0.25 |
| headless | 0.2585 | 0.3225 | +0.0640 | +0.25 |
| a | 0.1369 | 0.1846 | +0.0477 | +0.35 |
| k | 0.1436 | 0.1053 | -0.0382 | -0.27 |
| o | 0.1118 | 0.1171 | +0.0053 | +0.05 |
| t | 0.0442 | 0.0430 | -0.0012 | -0.03 |

### TERMINAL Rate Changes (Q3 -> Q4)

| Atom | Rate Q3 | Rate Q4 | Change | Rel Change |
|------|---------|---------|--------|------------|
| bare | 0.4427 | 0.3996 | -0.0431 | -0.10 |
| m | 0.0053 | 0.0430 | +0.0378 | +7.19 |
| l | 0.0975 | 0.1208 | +0.0234 | +0.24 |
| h | 0.0621 | 0.0436 | -0.0185 | -0.30 |
| r | 0.0846 | 0.1008 | +0.0163 | +0.19 |
| y | 0.2162 | 0.2028 | -0.0134 | -0.06 |
| n | 0.0917 | 0.0893 | -0.0024 | -0.03 |

## Hazard x Atom x Position Interaction

Interaction chi-squared: 337.17 (df=6, p=0.0)
Zone-specific pairs (enrichment > 1.5x): 16

| Hazard | HEAD | Zone | Enrichment | N |
|--------|------|------|------------|---|
| HIGH | a | SPEC | 2.816x | 390 |
| HIGH | a | WORK | 4.000x | 1382 |
| HIGH | a | CLOSURE | 4.648x | 713 |
| HIGH | o | SPEC | 3.183x | 389 |
| HIGH | o | WORK | 2.762x | 842 |
| HIGH | o | CLOSURE | 2.859x | 387 |
| IMMUNE | k | SPEC | 6.155x | 556 |
| IMMUNE | k | WORK | 8.681x | 1956 |
| IMMUNE | k | CLOSURE | 5.848x | 585 |
| LOW | t | WORK | 2.472x | 564 |

### Thermal Cluster: k vs t vs e Work-Zone Deployment

Interpretation: **K_LED**

| HEAD | N | Mean Pos | SPEC | WORK | CLOSURE |
|------|---|----------|------|------|---------|
| k | 3097 | 0.4835 | 0.179 | 0.632 | 0.189 |
| t | 921 | 0.5455 | 0.128 | 0.612 | 0.260 |
| e | 6992 | 0.4509 | 0.258 | 0.561 | 0.181 |

### ZERO-Frame Position Profiles

| Frame | N | Mean Pos | SPEC Fraction |
|-------|---|----------|---------------|
| e->l | 355 | 0.3683 | 0.363 |
| e->y | 3472 | 0.4627 | 0.236 |
| i->n | 825 | 0.3992 | 0.364 |

## Section-Conditioned Atom Gradients

Qualifying sections (>= 500 tokens): ['S', 'H', 'T', 'B', 'C']

| Section | N | HEAD corr | TERM corr | Q3Q4 HEAD JSD | m surge |
|---------|---|-----------|-----------|---------------|---------|
| B | 6845 | 0.9384 | 0.9694 | 0.010994 | +0.0140 |
| C | 1479 | 0.7614 | 0.9653 | 0.024247 | +0.0541 |
| H | 3426 | 0.9051 | 0.9859 | 0.023452 | +0.0591 |
| S | 10664 | 0.9549 | 0.9931 | 0.013466 | +0.0443 |
| T | 660 | 0.8938 | 0.9785 | 0.012116 | +0.0426 |

Q3Q4 JSD ratio (max/min): 2.205

## Carryover Class Cross-Reference

Top-3 position-sensitive HEADs: {'headless': 'N/A', 'e': 'NEG', 'a': 'POS'}
Top-3 position-sensitive TERMs: {'bare': 'NEU', 'm': 'POS', 'r': 'POS'}
Dominant carryover class: **POS** (50%)

## Constraints

### C1671: GRADIENT_HETEROGENEOUS

**Rationale:** HEAD chi2=659.08 p=0.0, TERM chi2=663.31 p=0.0, min cosine=0.9290

### C1672: CLOSURE_DISTRIBUTED

**Rationale:** HEAD top2=0.585, TERM top2=0.849, HEAD JSD=0.011384, TERM JSD=0.015721

### C1673: HAZARD_POSITION_COUPLED

**Rationale:** Interaction chi2=337.17, p=0.0, 16 zone-specific pairs (>1.5x enrichment)

### C1674: SECTION_MODULATES_GRADIENT

**Rationale:** Min HEAD corr=0.7614, min TERM corr=0.9653, Q3Q4 JSD ratio=2.205
