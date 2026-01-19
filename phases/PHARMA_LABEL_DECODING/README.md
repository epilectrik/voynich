# PHARMA_LABEL_DECODING

**Phase ID:** PHARMA-LABEL-DECODING
**Status:** COMPLETE
**Started:** 2026-01-16
**Completed:** 2026-01-17

---

## Purpose

Map the hierarchical structure of pharmaceutical labels in Section P folios and analyze morphological differences between label categories.

---

## Key Findings

### 1. Two-Level Naming System

Pharma folios use a **Jar -> Content** labeling hierarchy:
- **Jar labels** (first token in group) = container/category identifier
- **Content labels** (following tokens) = root/leaf specimen identifiers

### 2. Complete Vocabulary Separation

| Comparison | Jaccard Similarity | Interpretation |
|------------|-------------------|----------------|
| **Jar vs Content** | 0.000 (ZERO overlap) | Completely disjoint naming systems |
| **Root vs Leaf** | 0.013 (2 shared tokens) | Almost entirely distinct vocabularies |

The 18 jar labels share **no tokens** with the 191 content labels. This confirms jars and contents are named by fundamentally different schemes.

### 3. PREFIX Clustering by Plant Part

10 of 13 multi-occurrence prefixes cluster by plant part:

| Lean | Prefixes |
|------|----------|
| ROOT-leaning | ot-, op-, da-, ch-, sh-, ar- |
| LEAF-leaning | so-, or-, ol-, sa- |
| MIXED | ok-, do-, yk- |

### 4. No Brunschwig Processing Signature

Tested whether root labels (aggressive extraction) show different morphology from leaf labels (gentler processing). **No significant alignment detected** - both plant parts have similar intense/gentle prefix ratios.

---

## Folios Mapped (13 total)

### Root Folios (8 folios, 152 labels)

| Folio | Jars | Roots | Structure |
|-------|------|-------|-----------|
| f88v | 4 | 27 | 3 rows, t/m/b placement |
| f89r1 | 5 | 28 | 3 rows, t/m/b placement |
| f89r2 | 4 | 21 | 3 rows, t/m/b placement |
| f89v2 | - | 17 | 3 rows (standalone labels) |
| f99r | 4 | 30 | Original mapping, detailed |
| f99v | 4 | 21 | 4 rows with jars |
| f102r1 | 4 | 23 | 4 rows, jar->root hierarchy |
| f102r2 | - | 14 | Continuation of f102r1 |
| f102v1 | 2 | 10 | 2 rows with jars |

### Leaf Folios (4 folios, 71 labels)

| Folio | Jars | Leaves | Structure |
|-------|------|--------|-----------|
| f100r | - | 15 | Flat structure (no jars) |
| f100v | - | 12 | Mixed leaves/roots, first flowers (unlabeled) |
| f101v2 | - | 18 | 2 rows, R1/R2 placement |
| f102v2 | 2 | 26 | 2 rows with jars |

### Excluded

| Folio | Classification | Reason |
|-------|----------------|--------|
| f49v | Reference page | Numbers 1-5 + single characters, not plant labels |

---

## Transcription Placement Variability

Labels are encoded differently across folios in the transcription:

| Code | Meaning | Folios |
|------|---------|--------|
| L1/L2/L3/L4 | Standard label position | f99r, f99v |
| t/m/b | Top/middle/bottom | f88v, f89r1, f89r2, f100v |
| R1/R2 | Row markers | f101v2 |
| X | Special placement | Various |

---

## Statistics Summary

From `label_category_results.json`:

```
Total labels analyzed: 222
  - Jar labels: 18 unique types
  - Content labels: 204 (191 unique types)
    - Root labels: 92 (88 unique types)
    - Leaf labels: 71 (69 unique types)

Jar vs Content overlap: 0 tokens (Jaccard = 0.000)
Root vs Leaf overlap: 2 tokens (Jaccard = 0.013)
  - Shared: okol, otory
```

---

## Files

| File | Description |
|------|-------------|
| `*_mapping.md` | Human-readable folio mappings (13 files) |
| `*_mapping.json` | Programmatic folio data (13 files) |
| `label_category_analysis.py` | Main analysis script |
| `label_category_results.json` | Full statistical results |

---

## Observations

1. **Jars are containers, not plants** - Jar labels name vessels/categories, not specimens
2. **Vocabulary isolation** - Each naming level (jar/content) and plant part (root/leaf) has distinct vocabulary
3. **PREFIX encodes plant part** - Weak but detectable clustering of prefixes by root vs leaf
4. **Flowers unlabeled** - First appearance of flowers (f100v) has no labels on flower specimens
5. **Reference page exists** - f49v is an index/reference page, not plant labels

---

## Implications

The complete separation of jar vocabulary from content vocabulary (Jaccard = 0.000) suggests:

1. **Jar labels are not plant names** - They identify containers or processing categories
2. **Content labels are specimen identifiers** - They name individual roots/leaves within a category
3. **Two-level organization** - The pharma section organizes by category (jar) then by specimen (content)

This aligns with a recipe/formulary interpretation where jars represent ingredient types and content labels identify specific variants or sources.
