# C1349: Dark Pipeline Preserves Category Structure Across Systems

**Tier:** 2
**Scope:** cross-system
**Phase:** A_B_CATEGORY_FLOW (471)

## Constraint

The dark pipeline (300 MIDDLEs, identification channel) preserves category structure almost perfectly between A and B (JSD=0.009, rho=0.976, p=0.005). MARKING dominates both sides (A: 40.0%, B: 33.1%), followed by THERMAL (A: 19.2%, B: 24.0%). Dark categories are section-modulated in B (chi2=184, V=0.166, perm p=0.001) but show no correlation with bridge (grammar) categories at the section level (overall rho=0.19, p=0.57). The bridge and dark pipelines carry independent category information.

## Evidence

From a_b_category_flow.py test T4 (292 dark MIDDLEs with category assignments):

**Dark pipeline category profiles:**

| Category | A dark | B dark |
|----------|--------|--------|
| MARKING | **40.0%** | **33.1%** |
| THERMAL | 19.2% | 24.0% |
| FLOW | 17.4% | 15.5% |
| OPERATION | 13.0% | 11.0% |
| STAGING | 6.2% | 9.2% |
| MONITORING | 2.2% | 4.0% |
| TRANSITION | 1.5% | 1.2% |
| CONTAINMENT | 0.5% | 1.9% |

| Metric | Value |
|--------|-------|
| JSD(A_dark, B_dark) | 0.009 |
| Spearman rho | **0.976** |
| Spearman p | **0.005** |

**B-section dark category modulation:**

| Metric | Value |
|--------|-------|
| Section chi-squared | 183.6 |
| Cramer's V | 0.166 |
| Permutation p | 0.001 |

**Bridge-dark independence (per B section):**

| B section | rho(bridge, dark) | p |
|-----------|-------------------|---|
| B | 0.19 | 0.57 |
| C | 0.02 | 0.95 |
| H | 0.22 | 0.51 |
| S | 0.48 | 0.18 |
| T | 0.02 | 0.95 |
| Overall | 0.19 | 0.57 |

## Interpretation

The dark pipeline behaves fundamentally differently from the bridge. Where the bridge shows active reshaping by B (C1347: 4 categories shift >1.5x), the dark pipeline shows near-perfect preservation (rho=0.976). This is consistent with C1272: dark MIDDLEs are NOT category-sorted by AZC, so they carry A's raw category imprint into B unchanged.

The MARKING dominance (40% in A, 33% in B) confirms dark MIDDLEs primarily carry identification/annotation content rather than operational grammar. The bridge-dark independence (rho=0.19) at category level extends C1146 (r=-0.865 negative correlation at token level): the two pipelines operate as orthogonal channels, each carrying different types of information.

The dual-channel architecture is now quantified: bridge carries grammar (B reshapes for execution), dark carries identification (B preserves for reference). They are categorically independent within each B section.

## Provenance

- a_b_category_flow.json: test T4
- Extends: C1272 (dark pipeline NOT category-sorted — explains preservation: no AZC filtering means raw A structure passes through)
- Extends: C1146 (bridge-dark negative correlation — now shown to extend to category-level independence)
- Extends: C1148 (dark pipeline section concentration — consistent with section-modulated chi2)
- Extends: C918 (A parameterizes B — dark pipeline is the identification channel of parameterization)

## Status

CONFIRMED — dark pipeline preserves category structure (rho=0.976, JSD=0.009) while bridge reshapes it (C1347). Bridge and dark carry independent category information (rho=0.19).
