# C1051: Section-Conditioned Class Convergence Asymmetry

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** A<>B
**Phase:** A_B_SECTION_CORRESPONDENCE (Phase 367)
**Extends:** C708 (funnel topology: MIDDLE Jaccard=0.274 → class Jaccard=0.830)
**Relates to:** C1048 (BIO dynamical coherence), C909 (96% MIDDLEs section-specific)

---

## Statement

The funnel topology (C708) is NOT section-uniform. Per-section class Jaccard across A folio pairs:

| Section | Mean Class Jaccard | Mean Enabled Classes | Diff from Global |
|---------|-------------------|---------------------|-----------------|
| B (BIO) | **0.794** | 37.3 / 49 | **-0.054** |
| H (HERBAL) | **0.813** | 38.1 / 49 | -0.034 |
| S (RECIPE) | **0.824** | 39.3 / 49 | -0.023 |
| Global | **0.847** | 41.2 / 49 | — |

Kruskal-Wallis H=469.3, p=1.2×10^-102. All sections show LOWER class Jaccard than global, but BIO is most divergent. BIO enables the fewest classes (37.3/49) and shows the most inter-A-folio variation in class repertoire (Jaccard=0.794).

---

## Evidence

- 111 A folios × 3 sections × 6105 pairwise comparisons per section
- Class assignment via token_to_class mapping (480 B tokens → 49 classes)
- Per-section class sets = classes instantiable by legal B tokens within that section
- C708 reference: global class Jaccard = 0.830 (our replication: 0.847)

---

## Interpretation

C708 established that diverse PP inputs (Jaccard 0.274) converge to similar B class repertoires (Jaccard 0.830) through C502.a filtering — the funnel topology. This constraint shows the funnel is section-dependent. BIO's narrower MIDDLE vocabulary (396 MIDDLEs vs 851 for RECIPE) means A folio PP composition has more leverage on which classes are enabled. Different A folios enable more different class sets in BIO than in RECIPE.

This is structurally consistent with C1048 (BIO dynamical coherence): BIO's tight operational clustering means the specific class repertoire matters more — fewer MIDDLEs, fewer classes, but higher dynamical predictability. RECIPE's broader vocabulary (851 MIDDLEs) absorbs PP variation more easily, producing more uniform class repertoires regardless of which A folio provides the PP pool.

The funnel has section-dependent aperture: narrow in BIO (more A-folio-sensitive), wide in RECIPE (more A-folio-agnostic).

---

## Method

- For each A folio × section: enabled class set = {token_to_class[w] for w in legal ∩ section_vocab}
- Pairwise Jaccard across all 111 A folio pairs within each section
- Kruskal-Wallis across 3 sections, with C708 global as reference

**Script:** `phases/A_B_SECTION_CORRESPONDENCE/scripts/ab_section_correspondence.py`
**Results:** `phases/A_B_SECTION_CORRESPONDENCE/results/ab_section_correspondence.json`
