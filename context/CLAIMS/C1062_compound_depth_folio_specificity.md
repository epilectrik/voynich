# C1062: Compound Depth Predicts Folio Specificity

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_DEEP_STRUCTURE (Phase 379)
**Extends:** C769 (folio-specificity of compound types), C766 (UN=81.1% compound), C767 (compound bimodality)
**Relates to:** C768 (FL=0% compound, FQ=46.7%), C935 (compound specification)

---

## Statement

Compound depth (number of maximal atoms) **negatively correlates** with folio spread: deeper compounds appear in fewer folios (Spearman rho=-0.270, p=5.3e-23, n=1293 MIDDLE types).

Depth distribution:

| Depth | MIDDLE types | Mean folio count |
|-------|-------------|-----------------|
| 0 (atomic) | 319 | 10.5 |
| 1 (simple) | 525 | 2.5 |
| 2 | 363 | 3.9 |
| 3 | 76 | 1.2 |
| 4 | 8 | 1.0 |
| 5 | 2 | 1.0 |

Maximum compound depth = 5. Depth 3+ MIDDLEs are almost exclusively folio-unique (mean 1.0-1.2 folios).

Classified vs UN depth:

| Group | Mean depth | Median | MW p |
|-------|-----------|--------|------|
| Classified (86 types) | 0.52 | 0.0 | — |
| UN (1207 types) | 1.22 | 1.0 | **5.5e-13** |

UN MIDDLEs are significantly deeper than classified MIDDLEs, extending C766 (UN=81.1% compound) with a depth dimension.

Within-role depth does **not** vary significantly (Kruskal-Wallis H=0.4, p=0.50). Depth is a **between-role** property (classified vs UN), not a **within-role** property.

---

## Interpretation

Compound depth functions as a **specialization gradient**: deeper compounds encode more specific (folio-local) operations. Atomic MIDDLEs (depth 0) are the universal vocabulary, appearing across ~10.5 folios on average. Each additional layer of composition narrows the scope.

The depth ceiling of 5 suggests a physical or combinatorial limit on MIDDLE composition. The rapid drop-off (76 at depth 3, 8 at depth 4, 2 at depth 5) indicates exponential decay rather than a hard cutoff.

The classified/UN depth gap (0.52 vs 1.22, p=5.5e-13) explains why UN tokens dominate compounds (C766): the 49-class system captures the atomic vocabulary but not the compositional vocabulary. UN MIDDLEs are not noise — they are precisely the specialized, folio-specific compounds that extend the core grammar.

The absence of within-role depth variation (p=0.50) means that once a MIDDLE is classified into a role, its depth is not further informative about its sub-role function. Depth distinguishes classified from UN, not EN from AX or FQ.

---

## Method

- 1,293 MIDDLE types from Currier B inventory (MiddleAnalyzer)
- Depth: count of maximal atoms (0 for atomic, 1+ for compound)
- Folio count: number of distinct folios in which MIDDLE type appears
- Primary: Spearman correlation (depth vs folio_count)
- Classified vs UN: Mann-Whitney U test on depth distributions
- Within-role: Kruskal-Wallis test across roles with compound MIDDLEs (AX, EN, FQ, CC)

**Script:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py`
**Results:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t5_compound_depth_role.json`
