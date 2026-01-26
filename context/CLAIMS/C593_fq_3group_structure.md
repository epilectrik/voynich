# C593: FQ 3-Group Structure

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The 4 FQ classes {9, 13, 14, 23} split into three behaviorally distinct sub-groups: CONNECTOR {9}, PREFIXED_PAIR {13, 14}, and CLOSER {23}. k=3 Ward clustering recovers this partition exactly (silhouette 0.68). PC1 (64.2%) separates by position, PC2 (28.2%) by morphology. Morphology and hazard show perfect overlap: BARE={9,23}=HAZARDOUS, PREFIXED={13,14}=SAFE.

---

## Evidence

**Test:** `phases/FQ_ANATOMY/scripts/fq_structural_anatomy.py`

### Sub-Group Summary

| Sub-Group | Classes | Tokens | Character |
|-----------|---------|--------|-----------|
| CONNECTOR | {9} | 630 | Bare, medial, hazardous, or→aiin bigram |
| PREFIXED_PAIR | {13, 14} | 1,898 | ok/ot-prefixed, medial-to-final, non-hazardous |
| CLOSER | {23} | 362 | Bare, final-biased, hazardous, minimal tokens |

### Partition Comparison

Three candidate partitions were tested:

| Candidate | Groups | Sum |r| | Cluster-Aligned | Silhouette |
|-----------|--------|--------|-----------------|------------|
| 2G_MORPHOLOGICAL | {9,23} vs {13,14} | 0.951 | No | 0.507 (k=2) |
| 2G_POSITIONAL | {9,13} vs {14,23} | 0.999 | No | 0.507 (k=2) |
| **3G_TRIO** | **{9} vs {13,14} vs {23}** | **N/A** | **Yes** | **0.681 (k=3)** |

### PCA

- PC1 (64.2%): final_rate, section_RECIPE_B, self_chain_rate (position-related)
- PC2 (28.2%): prefix_rate, suffix_rate, mean_token_length (morphology-related)
- Positional separation (4.94) > morphological separation (2.36)

### Morphology × Hazard Overlap

| Property | Classes | Overlap |
|----------|---------|---------|
| BARE | {9, 23} | = HAZARDOUS |
| PREFIXED | {13, 14} | = SAFE |

Perfect correspondence: every bare FQ class is hazardous, every prefixed FQ class is safe.

---

## Interpretation

The 3-group structure reflects FQ's operational grammar:
- **CONNECTOR** (Class 9): Bare medial operator, primarily or→aiin bigram (C561), bridges other FQ tokens
- **PREFIXED_PAIR** (Classes 13, 14): The bulk of FQ (65.7%), ok/ot-prefixed, medial-to-final workhorse operators
- **CLOSER** (Class 23): Bare final-biased operator, closes FQ sequences

Position is the primary organizing dimension, but the 3-group partition captures both positional and morphological variation better than either 2-group partition alone.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C583 | Extended - census now has internal structure |
| C587 | Extended - 4-way differentiation organized into 3 groups |
| C561 | Contextualized - Class 9 or→aiin bigram is CONNECTOR behavior |
| C594 | Refined - PREFIXED_PAIR further splits by vocabulary |
| C595 | Extended - 3 groups have structured internal transitions |

---

## Provenance

- **Phase:** FQ_ANATOMY
- **Date:** 2026-01-26
- **Script:** fq_structural_anatomy.py

---

## Navigation

<- [C592_c559_membership_correction.md](C592_c559_membership_correction.md) | [INDEX.md](INDEX.md) ->
