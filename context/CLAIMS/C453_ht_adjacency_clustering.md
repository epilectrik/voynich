# C453: HT Adjacency Clustering

**Tier:** 2 | **Status:** CLOSED | **Scope:** HT / GLOBAL | **Parallels:** C424

---

## Statement

HT vocabulary exhibits significant **adjacency clustering** (1.69x enrichment, p<0.0001), **STRONGER than Currier A adjacency** (1.31x per C424). Adjacent folios share more HT types than non-adjacent folios.

**Interpretation:** HT was produced in continuous sessions, with scribes maintaining vocabulary continuity across adjacent folios. This stronger-than-operational adjacency effect suggests HT was applied with even more session coherence than the underlying text.

---

## Evidence

### Adjacent vs Non-Adjacent Similarity

| Measure | Adjacent Folios | Non-Adjacent Folios |
|---------|-----------------|---------------------|
| Mean Jaccard similarity | 0.0611 | 0.0361 |
| Std | 0.0511 | 0.0344 |
| N pairs | 225 | 492 |

### Enrichment Test

| Statistic | Value |
|-----------|-------|
| Enrichment ratio | **1.69x** |
| Observed difference | 0.025 |
| Permutation test p-value | **< 0.0001** |
| Verdict | SIGNIFICANT ADJACENCY CLUSTERING |

Adjacent folios share **69% more HT types** than non-adjacent folios.

### Comparison to C424 (Currier A Adjacency)

| Analysis | Enrichment | P-value | Scope |
|----------|------------|---------|-------|
| C424 (Currier A vocabulary) | 1.31x | < 0.000001 | A only |
| C453 (HT vocabulary) | **1.69x** | < 0.0001 | GLOBAL |

**HT shows STRONGER adjacency clustering than Currier A vocabulary.**

This is a notable finding: the non-operational HT layer exhibits stronger production-session coherence than the operational registry layer.

---

## What This Constraint Claims

- Adjacent folios share significantly more HT vocabulary
- Enrichment ratio is 1.69x (p < 0.0001)
- HT adjacency exceeds Currier A adjacency (1.69x vs 1.31x)
- HT was applied in continuous production sessions

---

## What This Constraint Does NOT Claim

- HT was applied "after" operational text
- Adjacency = same scribe (possible but not proven)
- Session boundaries can be identified
- Causal mechanism for adjacency coherence

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C424** | C453 parallels: both show adjacency clustering, HT stronger |
| **C450** | C453 is additive: quire clustering + adjacency clustering |
| **C452** | C453 extends: same vocabulary used, but locally clustered |

---

## Methodological Note

The analysis used Jaccard similarity of complete HT type sets (not just prefixes) between folio pairs:

1. For each adjacent folio pair (in manuscript order): compute Jaccard(HT_types_i, HT_types_j)
2. For sampled non-adjacent pairs (gap >= 2): compute same metric
3. Permutation test: shuffle adjacency labels 1000 times, compute null distribution

This mirrors the methodology of C424 for direct comparison.

---

## Implication for 4-Layer Model

The finding that HT has stronger adjacency than Currier A supports the interpretation that:

1. Currier A is a **registry** (entries need not be adjacent)
2. Currier B is **execution** (folio-local, moderate adjacency)
3. AZC is **context** (discrete scaffolds, rigid)
4. HT is **orientation** (session-continuous, high adjacency)

HT's strong adjacency is consistent with it being applied as a continuous overlay or margin notation during production sessions.

---

## Phase Documentation

Research conducted: 2026-01-10 (HT-THREAD analysis)

Scripts:
- `phases/exploration/ht_adjacency_analysis.py` - Adjacency pattern analysis

Results:
- `results/ht_adjacency_analysis.json`
- `results/ht_threading_synthesis.md`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
