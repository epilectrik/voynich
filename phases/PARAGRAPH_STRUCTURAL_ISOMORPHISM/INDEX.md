# Phase 624: Paragraph Structural Isomorphism

**Status:** COMPLETE
**Verdict:** CONTINUOUS_MANIFOLD
**Constraints:** C1840-C1847
**Date:** 2026-03-25

---

## Question

Do B paragraphs collapse to a small number of structural arc templates -- defined by how compositional features evolve across body positions -- despite near-zero vocabulary overlap? Do sections differ in template diversity?

## Background

C855/C862 established that paragraphs are PARALLEL_PROGRAMS with near-zero vocabulary overlap (Jaccard=0.061). C853 identified a 5-cluster taxonomy (silhouette=0.237) based on static features. C1790 confirmed zero duplicate paragraphs at token level. But these characterizations are all static: they describe what paragraphs *contain*, not how their content *evolves* from opening to close.

Phase 623 revealed that paragraphs have genuine internal structure: backward TE dominance (C1832), a narrowing-but-diversifying complexity gradient (C1836), anti-parallel boundaries (C1837, cosine=-0.989), and section-stratified grammar temperature (C1838). C1729 established that boundary content concentrates at Q0/Q4 with indistinct interiors.

The question is whether these dynamic trajectories -- the *arc* from opening through interior to close -- cluster into a small set of reusable templates, or whether each paragraph traces a unique path. If templates exist, they would represent the operational *programs* that the grammar instantiates, distinct from the static size/entropy clusters of C853.

## Design

### Arc Signature Extraction (9 features x 3 boundary-aware bins = 27-dim)

Each paragraph's body is partitioned into three bins following C1729's boundary enrichment finding:

**Boundary-aware bins:**
- **OPEN:** First body line only (Q0 specification signal)
- **INTERIOR:** All middle body lines (operational content)
- **CLOSE:** Last body line only (Q4 closure signal)

**Minimum 6 body lines** for reliable interior bin estimates.

**9 features per bin:**

| # | Feature | Computation | Rationale |
|---|---------|-------------|-----------|
| 1 | log_ke_ratio | log((k+0.5)/(e+0.5)) | Kernel energy polarity (C1206) |
| 2 | h_rate | h/total_tokens | Monitoring intensity (C965) |
| 3 | headless_rate | headless fraction | Infrastructure (C1574) |
| 4 | mode_a_frac | Mode A suffix fraction | Specification (C1229) |
| 5 | mean_opacity | terminal opacity mean | Closure gradient (C1440) |
| 6 | cat_entropy | 8-category Shannon entropy | Operational diversity (C1250) |
| 7 | mean_line_length | tokens per line | Sequential channel (C1728) |
| 8 | m_terminal_rate | m-TERM fraction | Closure signature (C1434) |
| 9 | dark_frac | dark pipeline fraction | Pipeline axis (C1146) |

### Clustering Pipeline

**Pass A (diagnostic):** Ward clustering on raw z-normalized PCA-reduced signatures. Expected to find section as primary axis. This pass calibrates the section effect before removing it.

**Pass B (primary):** Ward clustering on section-residualized PCA-reduced signatures. The real test: does within-section template structure exist beyond section identity?

### Five Null Models (200 replicates each)

| Null | Construction | Tests |
|------|-------------|-------|
| N0: Bin permutation | Permute 3 bins within each paragraph | Trajectory shape specificity |
| N1: Pool shuffle | Pool body lines within section, redistribute | Paragraph-specific vs aggregate |
| N2: Folio mediation | Chi-squared of template x folio vs shuffled folio labels | Folio-level template structure |
| N3: Length-matched | Shuffle arc vectors between length-matched paragraphs | Length artifact |
| N4: Within-folio shuffle | Shuffle body lines across paragraphs within folio | Paragraph vs folio ecology |

### Verdict Logic

- **DISCRETE_TEMPLATES:** silhouette > 0.25, gap significant, N0 kills, REGIME ARI < 0.40
- **WEAK_TEMPLATES:** silhouette 0.15-0.25
- **CONTINUOUS_MANIFOLD:** no k gives silhouette > 0.15
- **SECTION_ONLY:** Raw finds structure, residualized does not
- **REGIME_ALIAS:** Residualized finds structure but REGIME ARI > 0.40
- **LINE_POSITIONAL_ONLY:** N1 pool shuffle preserves >80%

### Section Analysis

- Per-section independent clustering (minimum 30 eligible) with bootstrap stability
- Cross-section template portability (train on largest section, project others)
- Anti-parallel boundary universality per template
- Header atom validation (nearest-centroid, LOO)
- Short paragraph phase matching (4-5 body lines mapped to nearest template)
- Template ordering null (C1399 consistency)

---

## Scripts

| # | Script | Purpose | Runtime |
|---|--------|---------|---------|
| 1 | `extract_arc_signatures.py` | Arc signature extraction, z-normalization, section residualization, PCA | ~10s |
| 2 | `cluster_templates.py` | Two-pass clustering, 5 null models, REGIME test, verdict | ~4min |
| 3 | `section_analysis.py` | Section analysis, validation, header prediction, ordering null | ~30s |

Shared module: `shared_624.py`

---

## Script Details

### Script 1: extract_arc_signatures.py

**Purpose:** Extract 27-dimensional arc signatures (9 features x 3 boundary-aware bins) for all eligible B paragraphs, then z-normalize, section-residualize, and PCA-reduce.

**Pipeline:**
1. Identify eligible paragraphs: B-track, H-only, minimum 6 body lines (labels excluded)
2. For each eligible paragraph, partition body lines into OPEN/INTERIOR/CLOSE bins
3. Compute 9 features per bin, yielding a 27-dimensional raw arc vector
4. Z-normalize across all paragraphs (per feature dimension)
5. Section-residualize: subtract per-section mean from each dimension
6. PCA on both raw-normalized and section-residualized matrices
7. Output: JSON with raw vectors, residualized vectors, PCA projections, paragraph metadata

**Morphological requirements:**
- Kernel classification (k/h/e) via RecordAnalyzer or equivalent
- Terminal opacity via suffix classification (C1440-C1445 opacity mapping)
- 8-category classification for Shannon entropy (C1250)
- Mode A suffix detection (C1229)
- Dark pipeline membership (C1146)
- m-terminal detection (C1434)
- Headless token identification (C1574)

**Output:** `results/arc_signatures.json`

**Constraint candidates:**
- Arc dimensionality and variance structure

---

### Script 2: cluster_templates.py

**Purpose:** Two-pass Ward clustering with gap statistic, five null models, and REGIME alias test. Produces the primary verdict.

**Pass A (diagnostic):**
1. Ward clustering on raw z-normalized PCA-reduced data (retain PCs explaining 90% variance)
2. Sweep k=2..12, compute silhouette, Calinski-Harabasz, Davies-Bouldin
3. Gap statistic with 200 uniform reference replicates
4. Compute ARI between best-k clusters and section labels
5. Expected: ARI with section > 0.40 (section dominates raw structure)

**Pass B (primary):**
1. Ward clustering on section-residualized PCA-reduced data
2. Same k-sweep and metrics
3. Gap statistic with 200 reference replicates
4. Compute ARI between best-k clusters and:
   - Section labels (should be low post-residualization)
   - C853 static clusters (should be low if arcs differ from statics)
   - REGIME labels (must be < 0.40 to avoid REGIME_ALIAS verdict)

**Five null models (200 replicates each):**
- N0: Bin permutation -- permute the 3 bins within each paragraph, re-cluster, report silhouette distribution
- N1: Pool shuffle -- pool body lines within section, redistribute into paragraph-sized blocks, re-extract arcs, re-cluster
- N2: Folio mediation -- chi-squared of template x folio contingency vs 200 shuffled-folio-label baselines
- N3: Length-matched -- shuffle arc vectors between paragraphs with the same body-line count (within +/-1), re-cluster
- N4: Within-folio shuffle -- shuffle body lines across paragraphs within the same folio, re-extract, re-cluster

**Verdict assignment:** Apply verdict logic tree (see Design section above).

**Output:** `results/cluster_results.json`

**Constraint candidates:**
- Template count and silhouette
- Null model results
- REGIME independence

---

### Script 3: section_analysis.py

**Purpose:** Section-level template analysis, cross-section portability, boundary universality, header prediction, short-paragraph matching, and template ordering null.

**Analyses:**

1. **Per-section clustering:** For sections with 30+ eligible paragraphs, independent Ward clustering with bootstrap stability (100 resamples, ARI distribution)

2. **Cross-section portability:** Train k-means on largest section's arc vectors, project other sections' paragraphs to nearest centroid. Report assignment entropy and silhouette on projected data

3. **Anti-parallel boundary universality:** For each template from Pass B, compute cosine between OPEN divergence vector and CLOSE divergence vector (per C1837). Report fraction of templates with cosine < -0.30

4. **Header atom validation:** LOO nearest-centroid classification using header atom composition to predict template membership. Compare accuracy to (a) chance baseline and (b) gallows-only baseline. If headers predict template above both baselines, specification-level reality confirmed

5. **Short paragraph phase matching:** Paragraphs with 4-5 body lines (excluded from main clustering). Map to nearest template centroid. Report assignment confidence (distance to nearest vs second-nearest) and whether assignments are section-biased

6. **Template ordering null (C1399 consistency):** Within each folio, compute transition matrix of template-to-template sequences. Chi-squared test vs uniform. If p > 0.05, templates have no preferred ordering (consistent with C1399)

**Depends on:** Scripts 1 and 2 JSON outputs.

**Output:** `results/section_analysis.json`

**Constraint candidates:**
- Section template diversity
- Cross-section portability
- Anti-parallel boundary universality
- Header prediction accuracy
- Template ordering null

---

## Pre-Registered Predictions

| # | Prediction | Basis | Pass Criterion | Result |
|---|-----------|-------|----------------|--------|
| P1 | Optimal k is 3-8 on section-residualized data | C853 found 5; arcs should refine | 3 <= k <= 8 with gap p < 0.05 | **FAIL** k=2, sil=0.075 |
| P2 | Template centroids span 3+ PCs | Templates differ in multiple dimensions | Top 3 PCs explain >80% centroid variance | **FAIL** 1 PC at 80% |
| P3 | N0 (bin permutation) destroys structure | Trajectory shape matters | null_sil/real_sil < 0.50 | **FAIL** ratio=3.49 (inverted) |
| P4 | N1 (pool shuffle) reduces structure | Arc shape is paragraph-specific | null_sil/real_sil < 0.80 | **FAIL** ratio=1.79 (inverted) |
| P5 | Higher grammar temp -> more diverse arcs within section | Temperature = operational freedom | Positive Spearman rho in largest section | **PASS** rho=0.191 (weak) |
| P6 | Templates cross-cut C853 static clusters | Arc dynamics != static size/EN | ARI(new, C853) < 0.30 | **PASS** ARI=0.035 (trivial) |
| P7 | Anti-parallel boundaries in majority of templates | Boundary divergence = grammar property | >60% templates cosine < -0.30 | **FAIL** 0% anti-parallel |
| P8 | Headers predict template above chance AND above gallows-only | Specification-level reality | Both comparisons significant | **FAIL** p=0.30, gallows>full |
| P9 | Template sequence within folios is null | C1399: no paragraph ordering | Transition chi-squared p > 0.05 | **PASS** p=0.146 |

---

## Dependency Graph

```
Independent (run in parallel):
  Script 1 (arc signature extraction)

Depends on Script 1:
  Script 2 (clustering + null models + verdict)

Depends on Scripts 1 and 2:
  Script 3 (section analysis + validation)
```

---

## Methodological Standards

### Arc Signature Construction
- 9 features x 3 bins = 27 dimensions per paragraph
- OPEN = first body line, CLOSE = last body line, INTERIOR = all middle lines averaged
- Minimum 6 body lines per paragraph (ensures 4+ interior lines)
- Labels excluded from body line count
- H-track only, Currier B only

### Z-Normalization and Section Residualization
- Z-normalize: per-dimension (mean=0, std=1) across all eligible paragraphs
- Section-residualize: subtract per-section centroid from each paragraph's vector
- PCA retains components explaining 90% cumulative variance

### Clustering
- Ward linkage (minimizes within-cluster variance)
- K-sweep: k=2..12
- Gap statistic: 200 uniform reference replicates, 1-SE rule for optimal k
- Silhouette, Calinski-Harabasz, Davies-Bouldin reported for all k

### Null Models
- 200 replicates per null model
- Report: mean null silhouette, 95th percentile, p-value (fraction of nulls >= observed)
- N0 and N1 are the critical nulls; N2-N4 provide supplementary diagnostics

### Significance
- Gap statistic: 1-SE rule (standard)
- Null model p-values: one-sided (fraction of null >= observed)
- ARI thresholds: > 0.40 = substantial overlap, < 0.30 = independent
- Bootstrap stability: ARI > 0.60 across 80% of resamples = stable
- Header prediction: permutation test (1000 shuffles) for both chance and gallows-only comparisons

### Sample Requirements
- Minimum 6 body lines per paragraph for main analysis
- Minimum 4-5 body lines for short-paragraph phase matching
- Minimum 30 eligible paragraphs per section for independent section clustering
- Report effective N after all filtering

### Confounds
- Section: removed via residualization in Pass B; Pass A calibrates effect
- Paragraph length: N3 length-matched null tests for length artifact
- Folio ecology: N4 within-folio shuffle tests for folio-level effects
- REGIME: ARI test prevents REGIME alias

---

## Expected Verdict

**DISCRETE_TEMPLATES** -- If section-residualized clustering yields silhouette > 0.25 with 3-8 templates, N0 kills, and REGIME ARI < 0.40. Paragraphs instantiate a small template library.

**WEAK_TEMPLATES** -- If silhouette is 0.15-0.25. Structure exists but templates overlap substantially.

**CONTINUOUS_MANIFOLD** -- If no k yields silhouette > 0.15. Paragraphs vary continuously; no discrete program types.

**SECTION_ONLY** -- If Pass A finds structure but Pass B does not. All apparent template structure is section membership in disguise.

**REGIME_ALIAS** -- If Pass B finds structure but REGIME ARI > 0.40. Templates are really REGIME labels.

---

## Results

### Verdict: CONTINUOUS_MANIFOLD

**Predictions: 3 PASS / 6 FAIL** (passes are trivial or weak)

B paragraphs do NOT collapse into discrete structural arc templates. The 27-dimensional arc signature space (9 features x 3 boundary-aware bins) forms a continuous cloud with no separable cluster structure after section residualization.

### Key Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Eligible paragraphs | 75 / 528 (14.2%) | High exclusion (85.8%) at min 6 body lines |
| Pass A best silhouette | 0.076 (k=7) | No structure even with section included |
| Pass A section Cramer's V | 0.154 | Section barely affects raw clustering |
| Pass B silhouette (k=2) | 0.075 | Far below 0.15 WEAK threshold |
| Pass B R-squared | 0.063 | Templates explain 6% of variance |
| Pass B Ward-KMeans ARI | 0.002 | No robust cluster structure |
| C853 ARI | 0.035 | Orthogonal to static taxonomy |
| REGIME ARI | 0.004 | Not a regime artifact |
| N0 bin permutation ratio | 3.49 | **Inverted**: permutation improves clustering |
| N1 pool shuffle ratio | 1.79 | Also inverted |
| N2 folio mediation p | 0.000 | Folio mediates (but base structure absent) |
| N3 length-matched ratio | 1.11 | Length not a confound |
| N4 within-folio ratio | 1.77 | Inverted |
| Section B bootstrap ARI | 0.40 | Unstable (below 0.50 threshold) |
| Header LOO accuracy | 0.56 (p=0.30) | Not significant (chance=0.50) |
| Gallows-only accuracy | 0.63 | Better than full header |
| Anti-parallel fraction | 0.00 | No template shows anti-parallel boundaries |
| Template ordering p | 0.146 | Null (consistent with C1399) |
| Grammar temp rho | 0.191 | Positive direction (weak, low power) |
| PCA components at 90% | 18 / 27 | Data is diffuse |
| OPEN-CLOSE cosine | 0.967 | Positive (not anti-parallel in these features) |

### Interpretation

The inverted N0 result (ratio=3.49) is the most informative finding. Bin permutation — destroying the OPEN/INTERIOR/CLOSE trajectory while preserving per-paragraph feature budgets — produces HIGHER silhouette than real data. This means the universal positional gradient (all paragraphs follow approximately the same arc from opening through closure) actively SPREADS paragraphs across feature space. The arc is a shared property of the grammar, not a differentiator between paragraph types.

The positive OPEN-CLOSE cosine (0.967) shows that these 9 compositional features yield SIMILAR profiles at paragraph boundaries, unlike C1837's anti-parallel finding (cosine=-0.989) which was measured with enrichment profiles at the atom level. The anti-parallel signature operates at a finer grain than the arc features capture.

The high exclusion rate (85.8%) means this finding applies specifically to the long-paragraph population (≥6 body lines). Short paragraphs (4-5 lines, N=94) all mapped to a single template centroid, consistent with the absence of template diversity.

---

## Constraints

| Constraint | Claim | Tier | Scope |
|-----------|-------|------|-------|
| C1840 | B paragraph arc signatures form a CONTINUOUS_MANIFOLD: section-residualized silhouette peaks at 0.075 (k=2), far below 0.15 threshold. No discrete template types exist in the 27-dim arc feature space. | 2 | B, paragraph, clustering |
| C1841 | Bin permutation IMPROVES clustering (null/real ratio=3.49): the universal OPEN→INTERIOR→CLOSE gradient spreads paragraphs across feature space rather than concentrating them into types. Trajectory shape is shared, not discriminative. | 2 | B, paragraph, positional |
| C1842 | OPEN and CLOSE bins show positive cosine similarity (0.967) across 9 compositional features, unlike C1837's anti-parallel finding (cosine=-0.989) at atom enrichment level. The anti-parallel boundary operates below the arc feature grain. | 2 | B, paragraph, boundary |
| C1843 | REGIME does not mediate paragraph arc shape: REGIME-template ARI=0.004. Despite REGIME driving PREFIX (C1404), this does not produce arc template types. | 2 | B, paragraph, REGIME |
| C1844 | Arc templates are orthogonal to C853's static taxonomy: ARI(arc, C853)=0.035. Dynamic positional features add no clustering value beyond static features. | 2 | B, paragraph, clustering |
| C1845 | Section weakly affects raw arc clustering (Cramer's V=0.154, chi2 p=0.54). Unlike most structural features, arc shape is minimally section-determined. | 2 | B, paragraph, section |
| C1846 | Within Herbal (N=47), bootstrap stability ARI=0.40 (below 0.50 threshold). Even the largest section produces no robust within-section template structure. | 2 | B, H-section, paragraph |
| C1847 | Header features do not predict arc template above chance (LOO accuracy=0.56, p=0.30). Gallows type alone (0.63) outperforms full header features. Templates lack specification-level reality. | 2 | B, paragraph, header |
