# Phase 514: SECTION AND PARAGRAPH AXM DRIVERS

**Date:** 2026-03-05
**Follows:** Phase 513 (STATE_C_CONVERGENCE_REVISIT)
**Constraints produced:** C1404-C1407
**Script:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py`
**Results:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json`

---

## Background

Phase 513 established that AXM dominance is a thematic property (C1403), not sequential convergence. It showed section drives AXM rate, and folio ICC = 0.286 leaves 71% of paragraph-level AXM variance unexplained by folio membership. Phase 514 asks the two follow-up questions:

1. **What structurally differentiates the Currier B sections?** (Beyond AXM rate)
2. **What drives paragraph-level AXM variance?** (The 71% not explained by folio)

---

## Part A: Section Structural Characterization (Tests A1-A6)

### A1: Macro-State Profiles (chi2=384.8, V=0.077)

Sections differ significantly in their 6-state macro-automaton distributions:

| Section | AXM | FQ | CC | FL_HAZ | AXm | FL_SAFE | n |
|---------|-----|-----|-----|--------|-----|---------|---|
| B | 0.744 | 0.131 | 0.059 | 0.044 | 0.016 | 0.005 | 5324 |
| S | 0.670 | 0.193 | 0.033 | 0.063 | 0.035 | 0.007 | 7027 |
| C | 0.604 | 0.213 | 0.048 | 0.082 | 0.043 | 0.009 | 994 |
| H | 0.589 | 0.240 | 0.049 | 0.072 | 0.039 | 0.011 | 2305 |
| T | 0.582 | 0.183 | 0.064 | 0.082 | 0.067 | 0.022 | 404 |

Section B is the most AXM-dominant (74.4%) and least FQ-heavy (13.1%). Section H has the highest FQ rate (24.0%), and T has the most transitional states (AXm=6.7%, FL_SAFE=2.2%).

The largest standardized residual is B/FQ = -8.38 (Section B depleted in escape operations).

### A2: Morphological Signatures (mean PREFIX JSD = 0.033)

Sections differ in PREFIX usage:
- **B**: qo-dominated (23.7% vs 17.1% corpus-wide), depleted in ok/ot
- **H**: ch-dominant (17.0%), balanced ok (8.4%), high yk (3.3%)
- **S**: Balanced ch/qo/BARE (each ~17%), highest lk (3.4%)
- **C**: BARE-dominant (22.3%), high ot (8.6%)
- **T**: sh-dominant (14.2% vs ch 13.4%), unusual sh>ch inversion

Suffix rates: S highest (50.9%), B lowest (46.3%). Mean token length: S longest (5.33), H shortest (4.92).

### A3: Kernel Profiles (chi2=142.8, V=0.071)

| Section | k-frac | h-frac | e-frac |
|---------|--------|--------|--------|
| B | 0.242 | 0.062 | 0.364 |
| S | 0.177 | 0.073 | 0.390 |
| H | 0.170 | 0.074 | 0.290 |
| C | 0.132 | 0.071 | 0.246 |
| T | 0.148 | 0.097 | 0.334 |

Section B is k-enriched (24.2%, highest), T is h-enriched (9.7%, highest), S is e-enriched (39.0%, highest).

### A4: Hazard Profiles

| Section | FL_HAZ rate | FL_SAFE rate | Forbidden violations | Eligible | Violation rate |
|---------|-------------|-------------|---------------------|----------|---------------|
| B | 0.044 | 0.005 | 0 | 727 | 0.000 |
| S | 0.063 | 0.007 | 5 | 831 | 0.006 |
| H | 0.072 | 0.011 | 5 | 503 | 0.010 |
| C | 0.082 | 0.009 | 1 | 196 | 0.005 |
| T | 0.082 | 0.022 | 0 | 71 | 0.000 |

Section B has the lowest hazard rate (4.4%) and zero forbidden violations. Sections C and T have the highest FL_HAZ rates (8.2%).

### A5: REGIME Distribution (V=0.573)

This is the strongest section differentiator by far:

| Section | R1 | R2 | R3 | R4 |
|---------|-----|-----|-----|-----|
| B | 100% | 0% | 0% | 0% |
| S | 43% | 0% | 52% | 4% |
| H | 6% | 41% | 16% | 38% |
| C | 0% | 40% | 40% | 20% |
| T | 0% | 0% | 50% | 50% |

V=0.573 -- far larger than any other effect. Section B is pure REGIME_1. This is the dominant structural distinction between sections.

### A6: Transition Entropy

| Section | H(class_t | class_{t-1}) | n transitions |
|---------|---------------------------|---------------|
| T | 3.094 bits | 336 |
| C | 3.813 bits | 870 |
| B | 4.221 bits | 4561 |
| H | 4.252 bits | 1930 |
| S | 4.470 bits | 5948 |

Section T has the tightest grammar (3.09 bits), S the loosest (4.47 bits). Overall: 4.63 bits.

---

## Part B: Paragraph-Level AXM Drivers (Tests B1-B6)

### B1: Morphological Predictors (CV R2 = 0.747)

Using all 21 morphological features (PREFIX fractions, kernel fractions, suffix rate, mode fraction, mean token length, 8 operational categories), a linear regression achieves 5-fold CV R2 = 0.747.

Top 5 univariate correlates with paragraph AXM rate (n=283):

| Feature | Spearman rho | p-value |
|---------|-------------|---------|
| qo_frac | +0.576 | 1.9e-26 |
| staging_frac | -0.525 | 1.9e-21 |
| bare_frac | -0.515 | 1.5e-20 |
| chsh_frac | +0.508 | 5.7e-20 |
| operation_frac | -0.469 | 7.0e-17 |

### B2: Paragraph Length

Length is a weak predictor: rho(body_lines, AXM) = +0.139, p=0.019. Longer paragraphs have slightly higher AXM rates.

### B3: PREFIX Channel

All three major PREFIX channels predict AXM:
- qo: rho = +0.576 (p < 1e-25) -- more heat = more AXM
- ch/sh: rho = +0.508 (p < 1e-19) -- more monitoring = more AXM
- BARE: rho = -0.515 (p < 1e-20) -- more bare = less AXM

### B4: Kernel Balance

All three kernel atoms predict AXM:
- k: rho = +0.432 (p < 1e-13) -- more energy = more AXM
- e: rho = +0.273 (p < 1e-5) -- more stability = more AXM
- h: rho = +0.173 (p = 0.004) -- more monitoring = more AXM

k-fraction is the strongest kernel predictor, consistent with C1384.

### B5: Hazard Density

FL_HAZ rate predicts AXM (rho = -0.440) and this survives length control (partial rho = -0.455). FQ rate is the strongest single predictor: rho = -0.803 (partly tautological since FQ is a non-AXM macro-state).

### B6: Variance Decomposition (CRITICAL)

| Model | CV R2 |
|-------|-------|
| Section only | **-0.027** |
| REGIME only | -0.092 |
| Section + REGIME | -0.077 |
| Morphology only | -0.095 |
| PREFIX only | **0.736** |
| Kernel only | 0.096 |
| Category only | 0.271 |
| Length only | -0.167 |
| Section + PREFIX | 0.736 |
| Section + kernel | 0.244 |
| Section + category | 0.315 |
| **Full model** | **0.760** |
| Full minus section | 0.743 |
| **Section marginal** | **+0.017** |

**Key findings:**

1. **Section alone has NEGATIVE CV R2 (-0.027).** At the paragraph level, knowing the section tells you essentially nothing about that paragraph's AXM rate that isn't better captured by its PREFIX composition.

2. **PREFIX alone explains 73.6%.** This is the dominant predictor set. Adding section to PREFIX provides zero gain (0.736 vs 0.736).

3. **The full model explains 76.0%.** The remaining 24% is genuine paragraph-level design freedom.

4. **Section's marginal contribution is +1.7%.** Section adds almost nothing beyond what PREFIX, kernel, and category already capture.

5. **REGIME alone also has negative CV R2 (-0.092).** The high folio-level section-REGIME correlation (V=0.573) does not translate to paragraph-level predictive power because within each section/REGIME, paragraph PREFIX profiles vary freely.

---

## Part C: Synthesis

### C1: What ARE sections?

Sections are primarily distinguished by:
1. **REGIME composition** (V=0.573) -- the dominant differentiator
2. **Transition entropy** (3.09-4.47 bits range)
3. **Macro-state profiles** (V=0.077) -- modest
4. **Kernel balance** (V=0.071) -- modest

### C2: What drives paragraph AXM?

The paragraph's **own PREFIX composition** is the answer. Section, REGIME, morphology, and length are all either redundant with PREFIX or uninformative at paragraph granularity. PREFIX profile alone achieves 73.6% CV R2; adding everything else gains only 2.4%.

### C3: Interaction Test

Correlation signs are consistent across sections for 6/7 tested features. Only `transition_frac` shows sign inconsistency (positive in B/C, near-zero in H/S). The PREFIX-to-AXM relationship is **universal across sections**.

---

## Constraints Produced

- **C1404**: Section structural differentiation
- **C1405**: Paragraph AXM driven by PREFIX not section
- **C1406**: Section is REGIME composition at paragraph level
- **C1407**: PREFIX-AXM relationship universal across sections

---

## Relationship to Prior Work

- **Extends C1403** (MONOSTATE is thematic dominance): Section determines the folio-level theme, but within that theme, paragraphs vary freely via PREFIX composition.
- **Extends C1169** (27% AXM residual): The 24% paragraph-level residual (from this phase) is consistent with C1169's folio-level finding. PREFIX captures most of the signal at both levels.
- **Confirms C1023** (PREFIX routing is sole load-bearing macro component): PREFIX dominates paragraph AXM prediction just as it dominates folio-level macro-state routing.
- **Extends C1029** (section-parameterized grammar weights): Section modulates grammar weights but this operates through REGIME/PREFIX composition, not independently.
