# C942: Context-Dependent MIDDLE Successor Profiles

**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** MATERIAL_LOCUS_SEARCH

## Statement

The same MIDDLE shows different successor distributions in different sections. For 24 common MIDDLEs (200+ successor pairs), 45.8% show statistically significant section-dependent successor profiles (Bonferroni-corrected alpha=0.00208). Section-stratified KL divergence is 2.0x greater than paragraph-position-stratified KL divergence, and 100% of MIDDLEs show section KL > position KL. MIDDLE behavior is shaped more by section identity than by operational phase within a paragraph.

## Evidence

### Section Stratification

| Metric | Value |
|--------|-------|
| Significant after Bonferroni | 11/24 (45.8%) |
| Mean pairwise symmetric KL | 9.42 |
| Median pairwise symmetric KL | 9.73 |

### Paragraph Position Stratification (EARLY/MID/LATE)

| Metric | Value |
|--------|-------|
| Significant after Bonferroni | 0/24 (0.0%) |
| Mean pairwise symmetric KL | 4.69 |
| Median pairwise symmetric KL | 4.54 |

### KL Comparison

- MIDDLEs with section KL > position KL: 24/24 (100%)
- Mean ratio: 2.01x
- Zero MIDDLEs show position-dependent successors after correction

### Top Section-Sensitive MIDDLEs

`eol` (KL=12.85), `ke` (12.05), `eo` (11.86), `o` (11.73), `in` (11.38)

### Method

23,096 Currier B tokens, 20,542 successor pairs (same-line, valid MIDDLEs), chi-square with Bonferroni correction, symmetric KL divergence with epsilon smoothing.

## Implication

Section identity modulates how operational MIDDLEs connect to each other. This is consistent with sections being operational configurations (material domains) that shape the combinatorial grammar — the information is distributed across transition patterns, not concentrated in any single token.

## Caveat: Role Composition Confound

The section-dependent KL divergence may be partially explained by section-level role composition differences (C551: ENERGY/FLOW anticorrelation r=-0.89; C552: section-specific role profiles Chi2=565.8). If sections have different role balances, the same MIDDLE appearing in different sections will have different successor pools available. The test did not control for role composition. The 2.0x KL ratio over position may reflect downstream consequences of C551/C552 rather than an independent material signal.

## Related

C909, C619, C941, C943
