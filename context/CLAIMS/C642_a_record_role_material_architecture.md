# C642: A Record Role & Material Architecture

**Tier:** 2 | **Status:** CLOSED | **Scope:** CROSS_SYSTEM | **Source:** A_TO_B_ROLE_PROJECTION

## Statement

The PP-PP co-occurrence lattice from A records is **sparse** (8.0% density, 6488/81406 possible pairs observed) with 92.0% of PP MIDDLE pairs never co-occurring. Role heterogeneity within legal pairs is **at chance** (55.2% observed vs 55.9% expected, permutation p=0.55), but **record-level role coverage is below expected** (1.91 distinct roles per record vs 2.13 expected, p=0.022). Material class consistency is **significantly below chance** (0.6% observed vs 4.1% expected, permutation p=0.0006) — A records **actively mix material classes** rather than maintaining per-record consistency. Material class shows no association with B-side role (Cramer's V=0.122, chi2 p=0.874).

## Evidence

### PP-PP Co-occurrence Lattice

| Metric | Value |
|--------|-------|
| Active PP MIDDLEs | 404 |
| Records with 2+ PP | 1536 |
| Total possible pairs | 81,406 |
| Legal (observed) pairs | 6,488 (8.0%) |
| Incompatibility rate | 92.0% |
| Mean pair recurrence | 4.07 |
| Max pair recurrence | 218 |
| Single-occurrence pairs | 3,965 (61.1%) |

The lattice is very sparse: each PP MIDDLE co-occurs with only ~8% of other PP MIDDLEs. 61.1% of observed pairs appear in only one record, suggesting most co-occurrences are rare combinations. The max recurrence of 218 indicates a few PP pairs are highly systematic.

### Role Heterogeneity (Permutation Test, n=10,000)

| Metric | Value |
|--------|-------|
| Pairs with both roles assigned | 2,284 |
| Observed heterogeneity | 55.2% (1261 different) |
| Permutation mean | 55.9% |
| Permutation std | 1.02% |
| p-value (two-tailed) | 0.55 |
| Verdict | AS_EXPECTED |

Legal pairs do not preferentially combine same or different B roles — the observed heterogeneity rate matches random expectation.

**Pathway stratification:**

| Stratum | Pairs | Heterogeneity |
|---------|-------|---------------|
| AZC_Med x AZC_Med | 2,069 | 54.0% |
| B-Native x B-Native | 2 | 0.0% |
| Cross-pathway | 213 | 67.6% |

Cross-pathway pairs show higher heterogeneity (67.6%), but the strata are confounded by B-Native's tiny matched population.

### Record-Level Role Coverage (Permutation Test, n=10,000)

| Metric | Value |
|--------|-------|
| Mean distinct roles per record | 1.91 |
| Permutation mean | 2.13 |
| p-value | 0.022 * |

Records contain fewer distinct B roles than expected. This is consistent with A records grouping PP MIDDLEs that serve **similar B execution functions**, even though the pairwise heterogeneity test is null — the effect operates at the record level, not the pair level.

### Material Class Consistency (Permutation Test, n=10,000)

| Metric | Value |
|--------|-------|
| Records with 2+ non-neutral PP | 1,531 |
| ALL_HERB | 9 (0.6%) |
| ALL_ANIMAL | 0 (0.0%) |
| ALL_MIXED | 171 (11.2%) |
| HETEROGENEOUS | 1,351 (88.2%) |
| Observed consistency | 0.6% |
| Permutation mean | 4.1% |
| p (one-tailed, >= observed) | 0.9999 |
| p (two-tailed) | 0.0006 * |
| Direction | LESS_CONSISTENT |

A records are **significantly LESS materially consistent** than chance: 0.6% of records have all-ANIMAL or all-HERB PP MIDDLEs, compared to 4.1% expected by random assignment. Records actively combine PP MIDDLEs from different material classes. No ALL_ANIMAL records exist at all.

### Material x Role Cross-Tabulation

| Material | AX | EN | FL | FQ |
|----------|----|----|----|----|
| ANIMAL | 8 | 9 | 0 | 0 |
| HERB | 11 | 13 | 2 | 0 |
| MIXED | 24 | 14 | 1 | 1 |

Chi2=2.45, df=6, p=0.874, Cramer's V=0.122. No significant association between material class and B-side role. (Warning: some expected counts < 5.)

## Interpretation

The A record co-occurrence lattice reveals two key architectural principles:

1. **Role clustering at record level, not pair level.** Pairwise role mixing is at chance, but records contain fewer distinct roles than expected. This suggests A records are weakly role-coherent: they tend to group MIDDLEs serving similar B functions, but do not enforce strict same-role pairing.

2. **Active material mixing.** Records deliberately combine PP MIDDLEs from different material classes. This contradicts a simple "material-specific record" model and instead suggests A records encode **multi-material specifications** — each record references components from multiple material domains.

The lattice sparsity (92% incompatibility) confirms that A's 404 PP vocabulary is heavily constrained in what combinations are legal. Most PP MIDDLEs are highly selective about their co-occurrence partners. This selectivity operates largely independent of B-role identity and material class — other mechanisms (possibly positional, morphological, or section-specific) govern PP combinatorics.

## Extends

- **C484**: A records are 2+ token entries — now shown to have sparse PP co-occurrence
- **C506**: PP composition doesn't affect class survival — extends to record-level role composition
- **C640**: PP role projection used as foundation for heterogeneity test

## Related

C484, C498, C506, C640, C641

## Provenance

- **Phase:** A_TO_B_ROLE_PROJECTION
- **Date:** 2026-01-26
- **Script:** lattice_material_test.py
