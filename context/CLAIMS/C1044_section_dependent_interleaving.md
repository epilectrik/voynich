# C1044: Section-Dependent Phase Interleaving Rate

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_PARAMETERIZED_LINE_GRAMMAR (Phase 365)
**Extends:** C962 (phase interleaving, corpus-level alternation rate 0.566)
**Relates to:** C1029 (section-parameterized grammar), C552 (section-specific role profiles)

---

## Statement

KERNEL/LINK/FL phase alternation rate varies by section (Kruskal-Wallis=55.68, p<0.0001):

| Section | Mean Alternation Rate |
|---------|----------------------|
| B (BIO) | 0.796 |
| C (COSMO) | 0.808 |
| H (HERBAL) | 0.742 |
| S (STARS_RECIPE) | 0.770 |

Interleaving is a section-parameterized quantity, not a fixed grammar property. Sequential compliance (KERNEL-before-LINK ordering) is NOT section-dependent (chi2=3.60, p=0.308) — only the rate of phase switching varies.

---

## Evidence

- Phase assignment: KERNEL = {AUXILIARY, ENERGY_OPERATOR}, LINK = {CORE_CONTROL, FREQUENT_OPERATOR}, FL = {FLOW_OPERATOR}
- Lines with 4+ tokens, 3+ phase assignments
- Alternation rate = fraction of consecutive phase pairs that differ
- Kruskal-Wallis across 4 sections: 55.68, p<0.0001
- Sequential compliance chi-squared: 3.60, p=0.308 (not significant)

---

## Interpretation

HERBAL has the lowest alternation rate (0.742), meaning longer sustained phase runs. BIO and COSMO have the highest (0.796, 0.808), meaning faster phase cycling. This is consistent with C552: BIO's energy-intensive processing requires faster phase cycling, while HERBAL's flow-dominated processing allows longer sustained phases. The ordering constraint (sequential compliance) is universal — only the rate parameter is section-tuned.

---

## Method

- Per-line phase sequence from role-to-phase mapping
- Alternation rate: count(consecutive_differences) / (n_phases - 1)
- Sequential compliance: fraction of half-lines where first KERNEL precedes first LINK
- Kruskal-Wallis + chi-squared tests, threshold p < 0.01

**Script:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/scripts/section_line_grammar.py`
**Results:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json`
