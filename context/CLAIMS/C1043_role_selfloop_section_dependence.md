# C1043: Role Self-Loop Section Dependence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_PARAMETERIZED_LINE_GRAMMAR (Phase 365)
**Extends:** C1029 (section-parameterized grammar weights)
**Relates to:** C552 (section-specific role profiles), C821 (REGIME-invariant line syntax), C964 (self-loop rates)

---

## Statement

Within-line self-loop rates (consecutive tokens of same instruction class) in the WORK zone are section-dependent (chi2=268.73, p<0.0001). Maximum enrichment ratios across sections:

| Role | Max/Min Ratio |
|------|--------------|
| FLOW_OPERATOR | 5.17x |
| ENERGY_OPERATOR | 3.57x |
| CORE_CONTROL | 3.15x |

Sections modulate role persistence within lines while preserving the universal grammar (C124). This is consistent with C552's section-specific role profiles but quantifies the specific mechanism: sections control how often roles repeat consecutively, not just which roles appear.

---

## Evidence

- WORK zone: positions 2 to N-2, lines with 5+ tokens
- 4 sections: B (BIO), C (COSMO), H (HERBAL), S (STARS_RECIPE)
- Chi-squared on section x role self-loop contingency table: 268.73, p<0.0001
- 3/5 roles show >= 1.5x enrichment ratio across sections

---

## Relationship to C821

C821 established that line syntax is REGIME-invariant (eta-squared=0.13%). H2 shows that sections DO modulate role behavior, while REGIMEs don't. This is consistent: C1029 already noted section effects are comparable to REGIME effects at the aggregate level (JSD 0.325 vs 0.320), but self-loop rates reveal a mechanism where section effects are much larger than REGIME effects.

---

## Method

- Per-section, per-role self-loop counts in WORK zone
- Chi-squared contingency test on stacked self/non-self table
- Enrichment ratio: max(section_rate) / min(section_rate) per role
- Threshold: p < 0.01 AND >= 2 roles with ratio >= 1.5

**Script:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/scripts/section_line_grammar.py`
**Results:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json`
