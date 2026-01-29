# C850: A Paragraph Cluster Taxonomy

**Tier:** 2
**Scope:** Currier-A
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

A paragraphs cluster into 5 natural types based on size, RI rate, and linker presence. The primary axis of variation is size, with secondary variation in RI concentration.

## Evidence

K-means clustering with k=5, silhouette=0.337:

| Cluster | n | % | Lines | RI Rate | Linker Rate | Interpretation |
|---------|---|---|-------|---------|-------------|----------------|
| 0 | 80 | 23% | 5.44 | 8.6% | 7.5% | Standard |
| 1 | 117 | 34% | 2.01 | **20.1%** | 3.4% | Short, RI-heavy |
| 2 | 15 | 4% | 7.20 | 9.8% | 0.0% | Long, no linkers |
| 3 | 28 | 8% | **11.79** | 7.1% | **32.1%** | Very long, linker-rich |
| 4 | 102 | 30% | 5.23 | 6.4% | 10.8% | Standard with linkers |

## Interpretation

**Three functional paragraph types:**

1. **Short RI-heavy (34%)**: 2 lines, 20% RI - metadata records, likely "middle" position paragraphs
2. **Long linker-rich (8%)**: 12 lines, 32% linkers - structural anchors, maps to "only" position
3. **Standard (58%)**: 5-7 lines, moderate RI - typical operational paragraphs

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C847 | CONFIRMS - Size variation by position |
| C835 | ALIGNS - Linkers in specific paragraph types |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/11_paragraph_clustering.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/cluster_analysis.json`

## Status

CONFIRMED
