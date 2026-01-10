# HT-THREAD: Global Human Track Threading Analysis

**Status:** COMPLETE | **Constraints Identified:** 4 potential

---

## Executive Summary

The Human Track (HT) threads through the manuscript as a **single unified notation layer** that:
1. Uses the **same prefix vocabulary** across all systems (Jaccard >= 0.947)
2. Varies in **density by system** (A > AZC > B)
3. Shows **quire-level clustering** (not uniform distribution)
4. Exhibits **strong adjacency effects** (1.69x enrichment, stronger than Currier A)

---

## Key Findings

### Phase 1: Per-Folio Features
- 227 folios analyzed
- System distribution: A=114, B=83, AZC=30 folios
- **HT density by system:** A (0.170) > AZC (0.162) > B (0.149)

### Phase 2: Distribution Analysis
| Test | Result | Significance |
|------|--------|--------------|
| Runs test | **CLUSTERED** | p < 0.0001 |
| Quire effect | **SIGNIFICANT** | H=47.20, p=0.000063, eta-squared=0.150 |
| System differences | **SIGNIFICANT** | H=7.79, p=0.020 |
| Position gradient | None | r=-0.150 |

**High HT quires:** G (0.193), B (0.189), I (0.186)
**Low HT quires:** M (0.111), K (0.126), T (0.138)

### Phase 4: Cross-System Threading
| Test | Result |
|------|--------|
| Boundary discontinuity | **DISCONTINUOUS** (p=0.049) |
| Prefix overlap A-B | **1.000** (complete) |
| Prefix overlap A-AZC | **0.947** |
| Prefix overlap B-AZC | **0.947** |

**Key insight:** HT uses the SAME prefix vocabulary across all systems but varies in DENSITY at system boundaries.

### Phase 5: Adjacency Patterns
| Measure | HT | Currier A (C424) |
|---------|-----|------------------|
| Adjacency enrichment | **1.69x** | 1.31x |
| P-value | **<0.0001** | <0.000001 |

**Key insight:** HT vocabulary clusters MORE strongly in adjacent folios than Currier A vocabulary.

---

## Potential Constraints

### C450 - HT Quire Clustering
**Tier:** 2 | **Status:** PROPOSED

HT density exhibits significant quire-level clustering (Kruskal-Wallis H=47.20, p<0.0001, eta-squared=0.150). HT is not uniformly distributed across the manuscript but organized at codicological boundaries.

**Evidence:**
- Runs test: 84 runs observed vs 114.5 expected (p<0.0001)
- Quire variance: eta-squared = 0.150 (moderate effect)
- High quires: G (0.193), B (0.189); Low quires: M (0.111), K (0.126)

### C451 - HT System Stratification
**Tier:** 2 | **Status:** PROPOSED | **Extends:** C341

HT density is system-conditioned: Currier A (0.170) > AZC (0.162) > Currier B (0.149), with A vs B significantly different (Mann-Whitney p=0.0043 after Bonferroni correction).

**Evidence:**
- Kruskal-Wallis H=7.79, p=0.020
- A vs B: p=0.0043 (Bonferroni-corrected threshold: 0.0167)
- Consistent with HT as "waiting notation" - A has more waiting-heavy registry operations

### C452 - HT Unified Prefix Vocabulary
**Tier:** 2 | **Status:** PROPOSED | **Refines:** C347

HT prefix vocabulary is unified across all three systems (A, B, AZC) with near-complete overlap (Jaccard >= 0.947). However, HT density is discontinuous at system boundaries (p=0.049). HT is a SINGLE notation layer that varies in DENSITY, not VOCABULARY, across systems.

**Evidence:**
- A-B prefix overlap: Jaccard = 1.000 (complete)
- A-AZC prefix overlap: Jaccard = 0.947
- B-AZC prefix overlap: Jaccard = 0.947
- Boundary discontinuity: p=0.049

### C453 - HT Adjacency Clustering
**Tier:** 2 | **Status:** PROPOSED | **Parallels:** C424

HT vocabulary exhibits significant adjacency clustering (1.69x enrichment, p<0.0001), STRONGER than Currier A adjacency (1.31x per C424). Adjacent folios share more HT types than non-adjacent folios.

**Evidence:**
- Mean adjacent similarity: 0.0611
- Mean non-adjacent similarity: 0.0361
- Enrichment ratio: 1.69x
- Permutation test: p<0.0001

**Interpretation:** HT was produced in continuous sessions, with scribes maintaining vocabulary continuity across adjacent folios.

---

## Threading Model

```
MANUSCRIPT STRUCTURE
====================
       |<-------- Quire A -------->|<-------- Quire B -------->|
       +----+----+----+----+----+----+----+----+----+----+----+
       | A  | A  | B  | B  | B  | A  | A  | B  | B  | B  | AZC|
       +----+----+----+----+----+----+----+----+----+----+----+
HT     |####|####|##  |##  |##  |####|####|##  |##  |##  |### |
DENSITY|HIGH|HIGH|MED |MED |MED |HIGH|HIGH|MED |MED |MED |MED |
       +----+----+----+----+----+----+----+----+----+----+----+
                  ^                        ^
                  |                        |
              System boundary         System boundary
              (density shift)         (density shift)

LEGEND:
  ####  = High HT density (Currier A)
  ##    = Medium HT density (Currier B)
  ###   = Variable HT density (AZC)
```

**Threading behavior:**
1. HT density clusters at quire level (codicological unit)
2. HT density shifts at system boundaries (A/B/AZC transitions)
3. HT vocabulary is continuous (same prefixes everywhere)
4. HT vocabulary clusters in adjacent folios (production sessions)

---

## Architectural Integration

The 4-layer model remains valid, with HT now better characterized:

| Layer | System | Organization | This Analysis |
|-------|--------|--------------|---------------|
| Execution | Currier B | Adaptive per-folio | (confirmed) |
| Distinction | Currier A | Registry chains | (confirmed) |
| Context | AZC | Discrete scaffolds | (confirmed) |
| **Orientation** | **HT** | **Quire-clustered, system-conditioned** | **NEW** |

**Key refinement:** HT is not just "system-conditioned" (C341) but shows:
- Quire-level clustering (codicological organization)
- Unified vocabulary (single notation system)
- Strong adjacency effects (production continuity)

---

## Files Generated

- `results/ht_folio_features.json` - Per-folio HT features
- `results/ht_distribution_analysis.json` - Distribution tests
- `results/ht_cross_system_analysis.json` - Cross-system threading
- `results/ht_adjacency_analysis.json` - Adjacency patterns
- `phases/exploration/ht_folio_features.py` - Phase 1 script
- `phases/exploration/ht_distribution_analysis.py` - Phase 2 script
- `phases/exploration/ht_cross_system_analysis.py` - Phase 4 script
- `phases/exploration/ht_adjacency_analysis.py` - Phase 5 script

---

## Stop Condition

Structure has been largely exhausted. Further investigation would require:
- Individual HT type tracking (beyond prefix level)
- Grapheme-level analysis (rare form engagement)
- Cross-session identification (if multiple scribes)

These are Tier 3+ questions that exceed current scope.

---

*Generated: 2026-01-10 | HT-THREAD Analysis | Tier 2 Exploratory*
