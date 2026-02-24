# C1255: Category-Section Universal Vocabulary

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** CATEGORY_SECTION_VOCABULARY (Phase 449)
**Extends:** C1134 (section specificity frequency-modulated), C1148 (dark pipeline hyper-modulated), C1176 (atom-selection-dominated)
**Relates to:** C1250 (8 gloss categories), C1254 (dark pipeline generalization)

---

## Statement

Operational gloss categories are **section-universal in vocabulary but section-parameterized in frequency**. A 5-test battery produces 2/5 WEAK_SIGNAL, with the pass/fail pattern cleanly separating vocabulary overlap (shared) from frequency differentiation (section-specific):

| Test | Null Model | Statistic | Result | Key Value |
|------|-----------|-----------|--------|-----------|
| T1: Within-category Jaccard | Permuted folio-section | Mean Jaccard distance | FAIL | J=0.676 vs null 0.669, p=0.334 |
| T2: Section-enriched MIDDLEs | Permuted token-section | Enrichment rate >2x | **PASS** | 34.3% vs null 13.4%, p=0.001 |
| T3: Section classification | Shuffled folio-section | LOO accuracy | **PASS** | 76.8% vs baseline 39.0%, p=0.001 |
| T4: Conditioned vs raw JS | Permuted MIDDLE-category | JS ratio | FAIL | 1.13x, p=0.603 |
| T5: Confidence stratification | Descriptive | Jaccard comparison | FAIL (reversed) | WEAK J=0.894, LS J=0.343 |

### Key Findings

1. **Vocabulary is shared across sections** (T1 null): Sections use the same MIDDLEs within each category. Jaccard distance (0.676) is indistinguishable from the folio-permuted null (0.669).

2. **Frequencies are section-specific** (T2/T3 pass): 34.3% of MIDDLEs with ≥5 tokens are >2x enriched in at least one section (null: 13.4%). Within-category MIDDLE frequency profiles predict section at 76.8% accuracy (+37.8pp over majority baseline).

3. **Category conditioning adds nothing to section divergence** (T4 null): Partitioning MIDDLEs into 8 categories does not increase section JS divergence (1.13x, below shuffled null). Section identity is orthogonal to operational categories.

4. **Dark compounds are the section-specific layer** (T5 reversed): WEAK-confidence auto-assigned MIDDLEs (dark pipeline compounds) have Jaccard 0.894 (nearly disjoint across sections). LOCKED/SOLID MIDDLEs (core grammar) have Jaccard 0.343 (substantial overlap). The grammar/dark boundary is also the universal/specific boundary.

### Per-Category Section Specificity

| Category | Jaccard | Enriched Rate | Conditioned JS |
|----------|---------|--------------|----------------|
| CONTAINMENT | 0.294 | 3/9 (33%) | 0.065 |
| FLOW | 0.505 | 3/16 (19%) | 0.048 |
| MARKING | 0.816 | 16/33 (48%) | 0.247 |
| MONITORING | 0.791 | 11/20 (55%) | 0.313 |
| OPERATION | 0.632 | 4/10 (40%) | 0.080 |
| STAGING | 0.795 | 7/20 (35%) | 0.089 |
| THERMAL | 0.842 | 15/64 (23%) | 0.151 |
| TRANSITION | 0.734 | 11/32 (34%) | 0.116 |

MONITORING and MARKING have the highest section specificity — consistent with their role in identifying process-specific states.

---

## Interpretation

Operational categories describe *what the system does* (heat, cool, transfer, mark). Sections describe *what apparatus it does it to*. The core operational grammar is equipment-independent (shared MIDDLEs across all sections). Section identity is encoded in two ways:
1. **Frequency modulation** of shared grammar MIDDLEs (C1134, confirmed here)
2. **Section-specific dark compounds** (C1148, confirmed by T5 reversal)

This unifies C1134, C1148, and C1176 into a single mechanistic picture: the grammar is universal, the dark compounds provide section identity, and frequency modulation bridges the two.

---

## Method

- 22,969 classified B tokens (human + dark auto-assigned per C1254) across 5 sections (S, B, H, C, T; min 500 tokens)
- T1: Mean pairwise Jaccard distance within categories; null permutes folio→section
- T2: Count MIDDLEs >2x enriched in any section (min 5 tokens, min 3 in section); null permutes token sections
- T3: Leave-one-folio-out nearest-centroid classification from per-category MIDDLE frequency vectors
- T4: Mean within-category section JS vs raw section JS; null permutes MIDDLE→category
- T5: Jaccard comparison between LOCKED/SOLID (human + high-confidence) and WEAK (dark pipeline) tiers
- 1000 permutations, p < 0.01 threshold

**Script:** `phases/CATEGORY_SECTION_VOCABULARY/scripts/category_section_vocabulary.py`
**Results:** `phases/CATEGORY_SECTION_VOCABULARY/results/category_section_vocabulary.json`
