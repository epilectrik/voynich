# C1207: Atom Correlation Clusters -- 5-6 Independent Axes

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ATOM_BEHAVIORAL_CENSUS (Phase 428)
**Extends:** C1190 (behavioral atomicity), C1205 (i/k/e orthogonality)
**Relates to:** C1197 (atom extensibility partition), C1154 (program-specific variation)

---

## Statement

The ~20 MIDDLE atoms organize into 5-6 correlated clusters at the folio level, reducing the effective dimensionality of the MIDDLE system from 20 independent characters to approximately 6 independent axes. 64 of 153 pairwise correlations are FDR-significant (alpha=0.05) across 82 Currier B folios.

### Cluster 1: Iteration Axis {a, i, n, r}

The strongest cluster. All four atoms strongly co-vary across folios:

| Pair | r | Description |
|------|---|-------------|
| a-i | +0.826 | Strongest non-trivial pair |
| i-n | +0.832 | i and n nearly interchangeable at folio level |
| a-n | +0.811 | a tracks n as strongly as i does |
| a-r | +0.572 | r joins the iteration cluster |
| i-r | +0.435 | Weaker but significant |
| n-r | +0.470 | Consistent membership |

This cluster anti-correlates with {e} (a-e=-0.574, i-e=-0.513, n-e=-0.522), {y} (i-y=-0.599, a-y=-0.498), {d} (d-n=-0.487, d-i=-0.408), and {t} (i-t=-0.422, a-t=-0.401). Folios that are iteration-heavy are energy-light.

### Cluster 2: Monitoring Axis {c, h}

r(c,h) = +0.746. Both associate with PREFIX monitoring characters (ch, sh from C929). Also correlates with {t} (h-t=+0.371, c-t=+0.370) and {p} (h-p=+0.405).

### Cluster 3: Energy-Execution {k, l}

r(k,l) = +0.542. k is the energy kernel atom; l's association suggests structural co-deployment. k also anti-correlates with o (-0.585) and p (-0.392).

### Cluster 4: Closure {d, y}

r(d,y) = +0.479. d = "seal/checkpoint" (C1195), y = "end" (C1195). Their co-variation is consistent with both serving closure/completion functions.

### Cluster 5: Structural {o, p}

r(o,p) = +0.410. Both associate with structural positions (op = gateway compound, C1060). Also h-o=+0.346, o correlates with the monitoring cluster.

### Other Notable Correlations

- e-r = -0.675 (strongest anti-correlation): e and r compete for folio space
- k-e = +0.079 (near-zero): confirms C1205 independence of k and e
- f-s = +0.352: rare characters that co-vary (both PREFIX-associated)
- m isolated: correlates weakly with {a,i,n,r} cluster (a-m=+0.359) but no strong cluster membership

### daiin-Controlled Replication (T1b)

All major clusters survive aiin exclusion. The {a,i,n,r} cluster weakens slightly (a-i drops from +0.826 to +0.628, i-n from +0.832 to +0.551) but remains the dominant cluster. This is expected since aiin contains a, i, and n, so removing it reduces their mechanical co-occurrence. The residual correlations confirm genuine folio-level co-variation beyond daiin.

---

## Method

- 23,096 Currier B tokens, 82 folios with 20+ MIDDLE characters
- Character-fraction per folio for each of 18 atoms (g, x excluded: <50 occurrences)
- Pairwise Pearson correlations: 153 pairs
- Benjamini-Hochberg FDR correction at alpha=0.05

**Script:** `phases/ATOM_BEHAVIORAL_CENSUS/scripts/atom_census_test.py` (T1, T1b)
**Results:** `phases/ATOM_BEHAVIORAL_CENSUS/results/atom_census_results.json`
