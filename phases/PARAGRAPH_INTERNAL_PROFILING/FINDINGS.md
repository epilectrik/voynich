# PARAGRAPH_INTERNAL_PROFILING: Findings

**Phase Status:** COMPLETE
**Date:** 2026-01-29

## Summary

Currier A and B paragraphs show parallel structural patterns: both have **header-enriched line 1** with distinct marker vocabulary (A: RI concentration 3.84x; B: HT delta +0.134), followed by operational body zones. Clustering reveals 5 natural paragraph types in each system, with size being the primary discriminant.

## Key Findings

### 1. A Paragraph Profiles

| Metric | Value |
|--------|-------|
| Paragraphs | 342 |
| Mean lines | 4.8 |
| Mean tokens | 32.7 |
| Mean RI rate | 11.8% |
| RI line-1 concentration | **3.84x** (expected 1.85x) |
| Linker rate | 8.8% (30 paragraphs) |

**By folio position:**

| Position | n | Lines | Tokens | RI Rate |
|----------|---|-------|--------|---------|
| first | 86 | 5.35 | 39.0 | 9.3% |
| middle | 142 | 2.75 | 18.7 | **14.3%** |
| last | 86 | 5.36 | 36.2 | 11.8% |
| only | 28 | **11.79** | 73.4 | 7.1% |

**Key observation:** "Middle" paragraphs are short (2.75 lines) but have highest RI rate (14.3%). "Only" paragraphs (single-paragraph folios) are much larger (11.79 lines).

**By section:**

| Section | n | RI Rate | PP Rate | Compound Rate |
|---------|---|---------|---------|---------------|
| H | 197 | 8.4% | 42.0% | 27.7% |
| P | 130 | **17.2%** | **67.5%** | 32.0% |
| T | 15 | 9.8% | 53.3% | 29.9% |

**Key observation:** Section P (pharmaceutical) has significantly higher RI and PP rates than H (herbal).

### 2. B Paragraph Profiles

| Metric | Value |
|--------|-------|
| Paragraphs | 585 |
| Mean lines | 4.37 |
| Mean tokens | 39.5 |
| Mean HT rate | 36.4% |
| HT delta (line 1 - body) | **+0.134** (expected +0.158) |
| Positive delta rate | **76.8%** (expected 76%) |
| First token is HT | 75.6% |

**Gallows-initial pattern:**

| Gallows | Count | % of Gallows |
|---------|-------|--------------|
| p | 219 | 63.8% |
| t | 89 | 25.9% |
| k | 26 | 7.6% |
| f | 9 | 2.6% |

Overall gallows-initial rate: 58.6% (lower than expected 71.5% - see interpretation below).

**By B section:**

| Section | n | HT Delta | EN Rate | FL Rate | FQ Rate |
|---------|---|----------|---------|---------|---------|
| BIO | 149 | 0.093 | 30.6% | 2.9% | 16.7% |
| HERBAL_B | 54 | **0.209** | 33.8% | 9.5% | 20.9% |
| PHARMA | 42 | 0.046 | 18.4% | 2.9% | **43.2%** |
| RECIPE_B | 289 | 0.144 | **44.5%** | 6.8% | 19.1% |

**Key observations:**
- HERBAL_B has highest HT delta (0.209)
- PHARMA has highest FQ rate (43.2%) - frequency/repetition dominated
- RECIPE_B has highest EN rate (44.5%) - energy/thermal dominated
- Section differences are highly significant (Kruskal-Wallis p < 0.0001)

### 3. Cross-System Comparison

| Dimension | A | B |
|-----------|---|---|
| Paragraphs | 342 | 585 |
| Mean lines | 4.8 | 4.37 |
| Mean tokens | 32.7 | 39.5 |
| Tokens/line | 5.81 | 8.04 |
| Header enrichment | RI 3.84x | HT +0.134 delta |

**Mann-Whitney line count:** U=107,164, p=0.067 (not significant)

**Structural parallel confirmed:**
- Both systems show clear header (line 1) enrichment
- A: RI concentration 3.84x higher in line 1 than body
- B: HT rate 46.5% in line 1 vs 23.7% in body
- Line counts are statistically indistinguishable

### 4. Clustering Analysis

**A paragraphs (k=5, silhouette=0.337):**

| Cluster | n | Lines | RI Rate | Linker Rate | Interpretation |
|---------|---|-------|---------|-------------|----------------|
| 0 | 80 | 5.44 | 8.6% | 7.5% | Standard paragraphs |
| 1 | 117 | 2.01 | **20.1%** | 3.4% | Short, RI-heavy (middle position) |
| 2 | 15 | 7.20 | 9.8% | 0.0% | Long, no linkers (T section) |
| 3 | 28 | **11.79** | 7.1% | **32.1%** | Very long, linker-rich (only position) |
| 4 | 102 | 5.23 | 6.4% | 10.8% | Standard with moderate linkers |

**B paragraphs (k=5, silhouette=0.237):**

| Cluster | n | Lines | HT Delta | EN Rate | Interpretation |
|---------|---|-------|----------|---------|----------------|
| 0 | 51 | 1.16 | -0.033 | 0.0% | Single-line, no header effect |
| 1 | 185 | 3.26 | 0.128 | 34.9% | Short, moderate EN |
| 2 | 60 | **12.38** | **0.206** | **51.1%** | Long, high header effect, EN-dominated |
| 3 | 205 | 3.82 | 0.162 | 40.8% | Medium, strong header |
| 4 | 84 | 4.37 | 0.131 | 45.6% | Medium, EN-rich |

## Interpretation

### Parallel Header-Body Architecture

Both A and B paragraphs exhibit the same structural pattern:
1. **Header zone** (line 1): Enriched with marking vocabulary
   - A: RI tokens concentrated 3.84x higher than body
   - B: HT tokens elevated by +13.4pp over body
2. **Body zone** (lines 2+): Operational vocabulary
   - A: PP tokens (67.5% in section P)
   - B: Classified 49-class tokens

This validates C827 (paragraphs as operational units) and extends to both systems.

### Discrepancy Notes

**Gallows-initial rate (B):** Found 58.6% vs expected 71.5% from C841. The difference may be due to:
- Different paragraph boundary detection method
- C841 measured first token of paragraph vs first character

**C552 section validation:** At paragraph level, section-role relationships differ from folio-level expectations:
- BIO vs HERBAL: HERBAL has higher EN (opposite of C552)
- PHARMA vs HERBAL: PHARMA has *lower* FL (opposite of C552)

This suggests section effects are stronger at folio level than paragraph level.

### Clustering Insights

**A paragraph types:**
1. **Short RI-heavy** (34%, cluster 1): 2 lines, 20% RI - likely metadata-dense records
2. **Long linker-rich** (8%, cluster 3): 12 lines, 32% linkers - structural anchor paragraphs
3. **Standard** (62%, clusters 0,2,4): 5-7 lines, moderate RI

**B paragraph types:**
1. **Single-line** (9%, cluster 0): No header effect - minimal paragraphs
2. **Long EN-dominated** (10%, cluster 2): 12 lines, 51% EN, high header effect - major instruction blocks
3. **Standard** (81%, clusters 1,3,4): 3-4 lines, moderate EN

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C847 | A Paragraph Size Distribution | Mean 4.8 lines, "only" position = 11.8 lines; Cohen's d = 0.110 vs B |
| C848 | A Paragraph RI Position Variance | Middle position = 14.3% RI vs first 9.3%; Kruskal-Wallis p=0.001 |
| C849 | A Paragraph Section Profile | P section: 17.2% RI, 67.5% PP vs H: 8.4% RI, 42% PP |
| C850 | A Paragraph Cluster Taxonomy | 5 clusters: short-RI (34%), long-linker (8%), standard (58%) |
| C851 | B Paragraph HT Variance Validation | Delta mean +0.134; 76.8% positive delta; line 1 = 46.5% HT |
| C852 | B Paragraph Section-Role Interaction | RECIPE: 44.5% EN; PHARMA: 43.2% FQ; differences p<0.0001 |
| C853 | B Paragraph Cluster Taxonomy | 5 clusters: single-line (9%), long-EN (10%), standard (81%) |
| C854 | A-B Paragraph Structural Parallel | Both show line-1 enrichment; line counts indistinguishable p=0.067 |

## Source Files

- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/00_build_paragraph_inventory.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/01_a_size_density_profile.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/02_a_ri_profile.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/03_a_pp_composition.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/04_a_position_section_effects.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/05_b_size_density_profile.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/06_b_ht_variance.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/07_b_gallows_markers.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/08_b_role_composition.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/09_b_section_effects.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/10_cross_system_summary.py`
- `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/11_paragraph_clustering.py`

## Results Files

- `a_paragraph_inventory.json`, `b_paragraph_inventory.json` - Raw inventories
- `a_paragraph_profiles.json`, `b_paragraph_profiles.json` - Merged profiles
- `a_size_density.json`, `b_size_density.json` - Size metrics
- `a_ri_profile.json` - RI composition
- `a_pp_composition.json` - PP composition
- `b_ht_variance.json` - HT variance
- `b_gallows_markers.json` - Gallows/markers
- `b_role_composition.json` - Role composition
- `a_position_section_effects.json`, `b_section_effects.json` - Position/section effects
- `cross_system_summary.json` - A-B comparison
- `cluster_analysis.json` - Clustering results
