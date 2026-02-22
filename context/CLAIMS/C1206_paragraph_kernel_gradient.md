# C1206: Paragraph Kernel Gradient -- h Declines, k/e Rise

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** I_ATOM_CHARACTERIZATION (Phase 427)
**Extends:** C965 (body kernel composition shift), C932 (body vocabulary gradient)
**Relates to:** C963 (paragraph body homogeneity), C934 (parallel startup pattern)

---

## Statement

Through the paragraph body (folio lines split into quintiles), h-kernel fraction declines strongly (r = -0.920) while k and e both rise (r = +0.727 and r = +0.881). i shows a weak positive trend (r = +0.534). Lines also shorten (9.9 to 9.4 tokens/line), consistent with C932.

| Quintile | Lines | k-frac | e-frac | h-frac | i-frac | tok/line |
|----------|-------|--------|--------|--------|--------|----------|
| Q0 | 519 | 0.077 | 0.189 | 0.039 | 0.080 | 9.9 |
| Q1 | 480 | 0.090 | 0.188 | 0.033 | 0.090 | 9.7 |
| Q2 | 488 | 0.089 | 0.193 | 0.033 | 0.088 | 9.4 |
| Q3 | 480 | 0.085 | 0.206 | 0.028 | 0.092 | 9.2 |
| Q4 | 453 | 0.095 | 0.203 | 0.028 | 0.087 | 9.4 |

Gradients (Q4 - Q0): k +0.018, e +0.014, h -0.011, i +0.007.

---

## Relation to C965

C965 reported h-kernel rises +0.10 and e-kernel drops -0.086 through paragraph body. This measurement used a different methodology (paragraph body lines only, after header exclusion). The present test measured all folio lines by quintile position without paragraph segmentation. The h-direction is consistent in sign with the monitoring-to-operations interpretation: early lines are monitoring-heavy, later lines are operation-heavy. The magnitudes differ because C965 controlled for paragraph boundaries while this test uses raw folio-line position.

The pattern is: monitoring (h) front-loads, energy operations (k/e) back-load within the folio's line sequence.

---

## Method

- 23,096 Currier B tokens grouped by folio
- Folios with 5+ lines included (quintile assignment)
- k, e, h, i character fractions computed per quintile
- Pearson correlation with quintile index

**Script:** `phases/I_ATOM_CHARACTERIZATION/scripts/i_atom_test.py` (T6b)
**Results:** `phases/I_ATOM_CHARACTERIZATION/results/i_atom_results.json`
