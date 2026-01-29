# C620: Folio Vocabulary Network

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** UNIQUE_VOCABULARY_ROLE

## Statement

B folios cluster by vocabulary into 2 groups (silhouette=0.055) that align strongly with section (ARI=0.497) but not REGIME (ARI=0.022). Cluster 1 = section H (31 folios); Cluster 2 = sections B/C/S/T (51 folios). C533's adjacency effect (1.30x class overlap ratio) reduces to 1.057x after section control — section is the primary vocabulary organizer, with only marginal residual adjacency. Mean pairwise folio Jaccard is 0.288. Unique vocabulary count correlates with manuscript position (rho=+0.600***) but unique density does not (rho=-0.047, p=0.676) — later folios are simply larger.

## Evidence

### Section-Controlled Adjacency

| Pair Type | Mean Jaccard | n |
|-----------|-------------|---|
| Adjacent same-section | 0.3285 | 74 |
| Adjacent diff-section | 0.2758 | 7 |
| Same-section non-adjacent | 0.3107 | 876 |
| Diff-section non-adjacent | 0.2614 | 2,364 |

Section-controlled adjacency ratio: 1.057x (0.3285 / 0.3107).
Raw adjacency ratio: 1.179x.
C533 reported 1.30x for ICC class overlap (different metric).

Section explains ~80% of the adjacency effect. The residual 5.7% is real but marginal.

### Clustering

| k | Silhouette |
|---|-----------|
| 2 | 0.0545 |
| 3 | 0.0443 |
| 4 | 0.0423 |
| 5-10 | 0.025-0.029 |

Silhouette is uniformly low across all k. There is no strong discrete structure — vocabulary similarity is a continuous gradient dominated by section membership.

### Cluster Composition (k=2)

| Cluster | Folios | Sections | REGIME distribution |
|---------|--------|----------|-------------------|
| 1 | 31 | H=31 | R1=4, R2=10, R3=4, R4=13 |
| 2 | 51 | B=20, C=5, S=23, T=2, H=1 | R1=19, R2=14, R3=4, R4=14 |

The vocabulary divide is section H vs everything else — herbal folios have distinct MIDDLE vocabularies.

### Extremes

| Folio | Mean Jaccard | Section | REGIME | Unique MIDDLEs |
|-------|-------------|---------|--------|---------------|
| f114r (most isolated) | 0.2199 | S | REGIME_3 | 34 |
| f78v (most central) | 0.3378 | B | REGIME_3 | 2 |

### Vocabulary Gradient

| Metric | rho | p |
|--------|-----|---|
| Unique count vs manuscript position | +0.600 | <0.001 *** |
| Unique density vs manuscript position | -0.047 | 0.676 n.s. |

Raw unique count increases with position because later sections (S) have larger folios. Density is uniform — unique vocabulary is proportionally constant across the manuscript.

## Refines

- **C533**: Adjacent folio class overlap (1.30x) is primarily section-driven. Section-controlled MIDDLE Jaccard ratio is only 1.057x.
- **C535**: Vocabulary minimality (81/82 folios needed) reflects hapax distribution, not functional folio design.

## Related

C531, C533, C534, C535, C618, C619
