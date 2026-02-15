# C1046: Mandatory Bigram Section Modulation

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_PARAMETERIZED_LINE_GRAMMAR (Phase 365)
**Extends:** C957 (26 mandatory bigrams), C1029 (section-parameterized grammar weights)
**Relates to:** C552 (section-specific role profiles)

---

## Statement

5/10 tested mandatory bigrams (C957) show significant section-dependent rates (Bonferroni alpha=0.005). Mandatory bigrams are universal (present in all sections) but their frequency is section-parameterized. This extends C1029's section-parameterized grammar weights to the specific bigram level.

---

## Evidence

- 10 mandatory bigrams tested (those with >= 5 global occurrences from C957's 26)
- Per-section bigram rates compared via chi-squared per bigram
- Bonferroni correction: alpha = 0.05/10 = 0.005
- 5/10 significant — half of mandatory pair bonds are section-sensitive

---

## Interpretation

The mandatory bigrams represent strong sequential dependencies (5x or more above independence). That half of them show section-dependent rates means that even the strongest pairwise bonds in the grammar are modulated by section context. The bigrams remain mandatory (they occur in all sections) but at different rates. This is the token-level manifestation of C1029's class-level section parameterization.

---

## Method

- Top 10 mandatory bigrams by global count (>= 5 occurrences)
- Per-section: count bigram occurrences / total bigrams
- Chi-squared per bigram across 4 sections (present/absent table)
- Bonferroni correction at alpha=0.005
- Threshold: >= 3/10 significant

**Script:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/scripts/section_line_grammar.py`
**Results:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json`
