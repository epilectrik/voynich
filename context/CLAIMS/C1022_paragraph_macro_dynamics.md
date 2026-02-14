# C1022: Paragraph Macro-Dynamics — 6-State Automaton Does Not Differentiate Paragraph Structure

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** PARAGRAPH_MACRO_DYNAMICS (Phase 345)
**Extends:** C1010 (6-state partition scope), C1016 (folio-level decomposition)
**Relates to:** C840-C869 (paragraph structure), C863 (ordinal EN gradient), C932-C935 (spec→exec gradient), C1015 (transition matrix)

---

## Statement

The 6-state macro-automaton (C1010) does not differentiate paragraph-level structure. Paragraph dynamics operate WITHIN the AXM macro-state, not across macro-states. Six pre-registered tests produced 1/6 PASS, establishing that paragraph is below the macro-automaton's resolution. Key findings:

**A. Header lines are scaffold-enriched, not boundary-marked.** Header lines (line 1 of each paragraph) show elevated AXM (+2.8pp) and depleted FQ (-2.9pp) relative to body lines (chi2=16.04, p=0.007). The prediction of CC or AXm enrichment fails — headers are MORE scaffold-heavy, not control-change markers.

**B. Specification-execution gradient is sub-threshold at macro-state level.** Execution zones show +1.4pp AXM over specification zones (chi2=11.81, p=0.037), but this falls below the 3pp effect-size threshold. The spec→exec gradient (C932) operates within AXM's 32-class internal diversity, not between macro-states.

**C. Gallows tokens are AXM/AXm scaffold.** Gallows-initial paragraph openers map 87.7% AXM and 12.3% AXm — zero CC, zero FQ, zero FL. Non-gallows openers are far more diverse (52.4% AXM, 32.2% FQ, 4.9% FL_HAZ). Gallows are structural scaffold markers, not execution boundaries.

**D. qo/chsh gradient is entirely within AXM.** Both qo-prefixed (99.0% AXM) and ch/sh-prefixed (98.3% AXM) tokens map almost exclusively to AXM. The qo→ch/sh ordinal gradient (C863) is a WITHIN-class phenomenon invisible to the 6-state partition.

**E. Late paragraphs converge to AXM dominance (sole PASS).** Macro-state entropy decreases with paragraph ordinal (rho=-0.215, p=0.007). Late paragraphs (ordinal 5+) have lower entropy (1.258) than early paragraphs (ordinal 1-2, entropy 1.409). This is consistent with stabilization/convergence but reflects AXM concentration, not state-switching.

**F. AXM self-transition trend is directionally correct but underpowered.** Spearman correlation of AXM self-transition with ordinal is rho=0.207, p=0.011 (significant), but the binary early/late split fails (Mann-Whitney p=0.12, n=10 late paragraphs).

---

## Evidence

### T1: Header vs Body (FAIL — informative)

| Zone | AXM | AXm | FQ | CC | FL_HAZ | FL_SAFE | N |
|------|-----|-----|----|----|--------|---------|---|
| Header | 0.705 | 0.045 | 0.151 | 0.035 | 0.058 | 0.005 | 925 |
| Body | 0.677 | 0.029 | 0.180 | 0.046 | 0.059 | 0.008 | 15,031 |

Chi-squared: 16.04, p=0.007. Headers are AXM-enriched (+2.8pp), FQ-depleted (-2.9pp).

### T2: Specification vs Execution (FAIL — sub-threshold)

| Zone | AXM | FQ | N |
|------|-----|----|---|
| Spec | 0.668 | 0.187 | 5,747 |
| Exec | 0.683 | 0.176 | 9,200 |

Chi-squared: 11.81, p=0.037. Direction correct but delta (+1.4pp AXM) below 3pp threshold.

### T3: AXM Self-Transition by Ordinal (FAIL — directional, underpowered)

- Early (ord 1-2): mean 0.661, n=112
- Late (ord 5+): mean 0.724, n=10
- Spearman: rho=0.207, p=0.011 (significant)
- Mann-Whitney: U=393.5, p=0.121 (not significant)

### T4: Gallows-Initial CC (FAIL — informative)

| Type | AXM | AXm | FQ | CC | FL_HAZ | N |
|------|-----|-----|----|----|--------|---|
| Gallows | 0.877 | 0.123 | 0.000 | 0.000 | 0.000 | 65 |
| Non-gallows | 0.524 | 0.084 | 0.322 | 0.021 | 0.049 | 143 |

Gallows tokens are pure AXM/AXm scaffold. CC rate = 0.0%.

### T5: Entropy by Ordinal (PASS)

- Spearman: rho=-0.215, p=0.007
- Early: 1.409 (n=114), Late: 1.258 (n=12)
- Late paragraphs are more macro-state-concentrated.

### T6: qo/chsh ↔ Macro-State (FAIL — informative)

| PREFIX | AXM | AXm | FQ | CC | FL_HAZ | FL_SAFE | N |
|--------|-----|-----|----|----|--------|---------|---|
| qo | 0.990 | 0.010 | 0.000 | 0.000 | 0.000 | 0.000 | 3,206 |
| ch/sh | 0.983 | 0.017 | 0.000 | 0.000 | 0.000 | 0.000 | 4,105 |

Both are >98% AXM. The C863 gradient is entirely within-AXM.

---

## Interpretation

This is a clean negative result that establishes a **resolution boundary** for the 6-state macro-automaton. The macro-automaton differentiates:
- Line-level structure (C556, C813)
- Folio-level programs (C1016, 6 archetypes)
- Cross-folio dynamics (C1015 transition matrix)

But it does NOT differentiate:
- Paragraph header vs body
- Specification vs execution zones
- qo/chsh prefix gradient
- Gallows vs non-gallows boundaries

The reason is structural: AXM contains 32 of 49 classes (65.3%), creating a resolution floor. Paragraph-level variation occurs within AXM's 32-class internal diversity — the spec→exec gradient, the qo/chsh ordinal shift, and the gallows boundary function all operate below the 6-state partition.

This is consistent with the macro-automaton being a deliberately coarse compression (8.17x, C1010) that sacrifices within-AXM resolution for topological clarity. The paragraph level is where the sacrificed resolution would have been informative.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | Header CC or AXm elevated ≥3pp | AXm +1.6pp, CC -1.2pp (AXM +2.8pp dominant) | FAIL |
| P2 | Exec AXM > Spec AXM ≥3pp | +1.4pp, p=0.037 (sub-threshold) | FAIL |
| P3 | Late paragraphs higher AXM self-transition | Spearman rho=0.207, p=0.011; binary p=0.121 | FAIL |
| P4 | Gallows first tokens CC-enriched (OR>1.5) | CC rate = 0.0%, gallows are 100% AXM/AXm | FAIL |
| P5 | Late paragraphs lower entropy (\|rho\|>0.15) | rho=-0.215, p=0.007 | PASS |
| P6 | qo elevated FL, ch/sh elevated AXM | Both >98% AXM, zero FL | FAIL |

1/6 PASS → PARAGRAPH_MACRO_DYNAMICS_NEGATIVE

---

## Method

- 16,054 Currier B classified tokens across 208 paragraphs (82 folios)
- Token→class mapping from `class_token_map.json`; class→macro-state from C1010 partition
- Paragraph boundaries from `par_initial` transcript field
- Zone assignment: HEADER (line 1), SPECIFICATION (pos < 0.4), EXECUTION (pos ≥ 0.4), per C932
- Statistical tests: chi-squared for distributions, Mann-Whitney for group comparison, Spearman for ordinal correlation, Fisher exact for 2×2 tables

**Script:** `phases/PARAGRAPH_MACRO_DYNAMICS/scripts/paragraph_macro_dynamics.py`
**Results:** `phases/PARAGRAPH_MACRO_DYNAMICS/results/paragraph_macro_dynamics.json`

---

## Verdict

**PARAGRAPH_MACRO_DYNAMICS_NEGATIVE**: The 6-state macro-automaton does not resolve paragraph-level structure. Paragraph dynamics are a within-AXM phenomenon operating below the macro-state partition's resolution floor. The macro-automaton is a line/folio-level description, not a paragraph-level one.
