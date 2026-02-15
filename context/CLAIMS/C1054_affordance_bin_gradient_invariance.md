# C1054: Affordance Bin Composition is Paragraph-Gradient Invariant

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** AFFORDANCE_BIN_PARAGRAPH_DYNAMICS (Phase 369)
**Relates to:** C932 (body vocabulary gradient), C995-C1000 (affordance bins), C1052 (B cluster selectivity)

---

## Statement

The 9-bin affordance architecture (C995-C1000) is **invariant** across the B paragraph specification→execution gradient (C932). HUB_UNIVERSAL fraction remains ~64% at every quintile position; no bin shows systematic gradient dependence.

| Quintile | HUB Fraction | Non-HUB Fraction |
|----------|-------------|-----------------|
| Q0 (spec) | 0.649 | 0.351 |
| Q1 | 0.616 | 0.384 |
| Q2 | 0.674 | 0.327 |
| Q3 | 0.628 | 0.372 |
| Q4 (exec) | 0.649 | 0.351 |
| Spearman rho | -0.10 | +0.10 |
| p-value | 0.873 | 0.873 |

No individual non-HUB bin shows Bonferroni-significant decline from Q0→Q4 (0/8 bins). HUB sub-roles (HAZARD_SOURCE, HAZARD_TARGET, SAFETY_BUFFER, PURE_CONNECTOR) are also quintile-independent (0/4 significant at Bonferroni threshold). Bin-to-bin transition grammar barely differs between specification and execution zones (mean row-wise JSD = 0.066). Section does not parameterize gradient slope (KW p = 0.688).

---

## Interpretation

The paragraph gradient (C932) does NOT operate by recomposing the affordance bin mixture. The functional scaffold — the proportion of HUB, STABILITY_CRITICAL, FLOW_TERMINAL, etc. — is maintained uniformly from the first body line to the last. The gradient selects WHICH MIDDLEs from within each bin, not which bins. Affordance bins define a static functional architecture that the gradient preserves while varying MIDDLE identity within it.

This complements C1052 (cluster selectivity) and C1053 (compound mediation): the gradient's variation operates at the level of C475 compatibility neighborhoods and specific MIDDLE selection, not at the level of functional role composition.

---

## Method

- 73 B paragraphs with 8+ lines (sections B=39, H=17, S=17)
- 972 MIDDLEs mapped to 9 affordance bins via `data/middle_affordance_table.json`
- Bin 4 (BULK_OPERATIONAL, 566 hapax MIDDLEs) excluded (near-zero paragraph occurrence)
- 23 HUB MIDDLEs decomposed into 4 sub-roles via `t1_hub_sub_role_partition.json`
- Token coverage: 96.0% (6881/7166)
- 5 hypotheses tested: HUB dominance gradient, non-HUB specification, sub-role gradients, transition grammar, section parameterization
- All 5 FAIL — verdict: NO_GRADIENT_BIN_INTERACTION

**Script:** `phases/AFFORDANCE_BIN_PARAGRAPH_DYNAMICS/scripts/affordance_bin_paragraph_dynamics.py`
**Results:** `phases/AFFORDANCE_BIN_PARAGRAPH_DYNAMICS/results/affordance_bin_paragraph_dynamics.json`
