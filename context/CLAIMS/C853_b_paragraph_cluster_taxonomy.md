# C853: B Paragraph Cluster Taxonomy

**Tier:** 2
**Scope:** Currier-B
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

B paragraphs cluster into 5 natural types. Single-line paragraphs (9%) show no header effect. Long EN-dominated paragraphs (10%) represent major instruction blocks. Standard paragraphs (81%) show moderate EN and positive header delta.

## Evidence

K-means clustering with k=5, silhouette=0.237:

| Cluster | n | % | Lines | HT Delta | EN Rate | Interpretation |
|---------|---|---|-------|----------|---------|----------------|
| 0 | 51 | 9% | 1.16 | -0.033 | 0.0% | Single-line, no header |
| 1 | 185 | 32% | 3.26 | 0.128 | 34.9% | Short, moderate EN |
| 2 | 60 | 10% | **12.38** | **0.206** | **51.1%** | Long, EN-dominated |
| 3 | 205 | 35% | 3.82 | 0.162 | 40.8% | Medium, strong header |
| 4 | 84 | 14% | 4.37 | 0.131 | 45.6% | Medium, EN-rich |

## Interpretation

**Three functional paragraph types:**

1. **Single-line (9%)**: Minimal paragraphs, no header effect - possibly labels or markers
2. **Long EN-dominated (10%)**: 12+ lines, 51% EN, high header effect - major instruction blocks
3. **Standard (81%)**: 3-4 lines, moderate EN, positive header delta - typical operational units

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C840 | EXTENDS - Paragraph types explain HT variance |
| C850 | PARALLEL - Both systems have 5 natural clusters |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/11_paragraph_clustering.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/cluster_analysis.json`

## Status

CONFIRMED
