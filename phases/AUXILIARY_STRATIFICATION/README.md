# AUXILIARY_STRATIFICATION Phase

## Purpose

Investigate the internal structure of the AUXILIARY role (20 classes, 28.4% of Currier B) to determine whether it contains meaningful sub-structure beyond "heterogeneous residual" (Q6 from CLASS_SEMANTIC_VALIDATION).

## Status: CLOSED

Phase complete. 4 constraints documented (C563-C566). AUXILIARY is a positionally stratified execution scaffold with three sub-roles (INIT/MED/FINAL), not a heterogeneous residual.

## Research Questions

| Question | Status | Finding | Constraint |
|----------|--------|---------|------------|
| Q1: AX census reconciliation | **DOCUMENTED** | 20 classes, 4559 tokens (28.4%), 19 taxonomy discrepancies | C563 |
| Q2: AX distributional profiles | **DOCUMENTED** | Tripartite positional split (INIT/MED/FINAL) | C563 |
| Q3: AX natural clustering | Resolved | Weak clusters (sil=0.232), positional gradient > clusters | - |
| Q4: AX sub-group characterization | **DOCUMENTED** | Frame openers / scaffold / frame closers | C563, C565 |
| Q5: AX transition grammar | **DOCUMENTED** | Flat transitions (1.09x), 71.8% INIT-before-FINAL | C565 |
| Q6: UN token audit | **DOCUMENTED** | 7042 tokens = hapax/single-folio, not a role | C566 |

## Key Finding: Positional Scaffold

AUXILIARY is not "heterogeneous residual." It is a **positionally stratified execution scaffold**:

| Sub-Group | Classes | Tokens | Position | Function |
|-----------|---------|--------|----------|----------|
| AX_INIT | 4, 5, 6, 24, 26 | 1195 (26.2%) | Initial (0.419) | Frame openers |
| AX_MED | 1, 2, 3, 14, 16, 18, 27, 28, 29 | 2763 (60.6%) | Medial (0.514) | Scaffold |
| AX_FINAL | 15, 19, 20, 21, 22, 25 | 601 (13.2%) | Final (0.660) | Frame closers |

Statistical validation: Kruskal-Wallis H=213.9, p=3.6e-47. Cohen's d=0.69 (INIT vs FINAL).

## Documented Findings

### C563: AX Internal Positional Stratification (Tier 2)
- 20 AX classes split into INIT (5), MED (9), FINAL (6) sub-groups
- Kruskal-Wallis H=213.9, p=3.6e-47
- 71.8% INIT-before-FINAL directional ordering in lines

### C564: AX Morphological-Positional Correspondence (Tier 2)
- AX_INIT: articulator rate 17.5%, diverse prefixes
- AX_MED: ok/ot prefix 88.8%, low articulator (6.4%)
- AX_FINAL: prefix-light (60.9%), zero articulators

### C565: AX Execution Scaffold Function (Tier 2)
- AX mirrors named role positions but provides STRUCTURAL framing
- 0% hazard involvement across all sub-groups
- Flat transitions (1.09x self-chaining vs EN 2.38x)
- AX_FINAL enriched in REGIME_1 (39.4%) and BIO (40.9%)

### C566: UN Token Resolution (Tier 2)
- 7042 tokens (30.5%) not in class_token_map
- 74.1% hapax, 74.8% single-folio
- Morphologically normal (same prefix/suffix patterns)
- NOT a separate role -- insufficient data for cosurvival test

## Resolved Questions

### Q3: AX Natural Clustering
- Hierarchical clustering gives weak silhouette (0.232 at k=2)
- Best split isolates FINAL group [15, 21, 22, 25] from rest
- Positional gradient is more meaningful than distributional clusters
- AX is a GRADIENT, not a set of discrete clusters

## Census: Role Map Reconciliation

19 discrepancies found between ICC/CSV/BCSC taxonomies:
- CSV ROLE_MAP had only 17 explicit class mappings (of 49)
- 12 ENERGY classes defaulted to AX in CSV scripts
- Classes 13/14 and 20/21 had conflicting FQ vs AX assignments
- Class 17: CC per C560, AX per BCSC range (C560 is authoritative)

Definitive AX classes (20): 1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29

## Scripts

| Script | Status | Output |
|--------|--------|--------|
| ax_census_reconciliation.py | **C563** | ax_census.json |
| ax_feature_matrix.py | **C563** | ax_features.json |
| ax_clustering_test.py | Complete | ax_clustering.json |
| ax_subgroup_characterization.py | **C563, C565** | ax_subgroups.json |
| ax_transition_analysis.py | **C565** | ax_transitions.json |
| un_token_audit.py | **C566** | un_audit.json |
