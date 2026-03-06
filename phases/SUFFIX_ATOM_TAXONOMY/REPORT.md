# Phase 540: Suffix Atom Taxonomy

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1510-C1515 (6 new)
**Script:** `phases/SUFFIX_ATOM_TAXONOMY/scripts/suffix_atom_taxonomy.py`
**Results:** `phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json`

---

## Motivation

Phase 539 (Bridge Atom Stability) completed the cross-system MIDDLE atom characterization. The suffix layer -- the second compositional domain in the TOKEN = [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX] decomposition -- had been characterized at the string level (C1408-C1410) but never decomposed at atom resolution. C1408 established that suffix uses 16 atoms (reduced from MIDDLE's 18, missing k,t,p,f,c) with HEAD->TERM structure. C1409 showed atoms carry different information in suffix vs MIDDLE position (JSD 0.004-0.560). C1410 showed suffix modes are atom-level category partitions.

Phase 540 completes the suffix atom taxonomy with 12 analyses at full category-level resolution, extending the prior string-level findings to quantified atom profiles.

---

## Method

12 analyses (T1-T12) using CategoryClassifier (8 operational categories) and morphological decomposition:

| Test | Topic | Method |
|------|-------|--------|
| T1 | Population census | Count suffixed tokens, unique suffixes, atom-length distribution |
| T2 | Atom inventory comparison | Compare suffix vs MIDDLE atom sets, identify missing atoms |
| T3 | First-atom category profile | Cramer's V(suffix first-atom x category) |
| T4 | Last-atom positional profile | R2(suffix last-atom -> line position), final enrichment |
| T5 | HEAD+TERM decomposition test | Compare category V and positional R2 for first/last atoms |
| T6 | Suffix x MIDDLE HEAD interaction | V(MIDDLE HEAD x suffix first-atom) |
| T7 | Suffix x MIDDLE TERMINAL interaction | V(MIDDLE TERMINAL x suffix first-atom), opacity rates |
| T8 | Mode A vs B category anatomy | 8-category profiles for each suffix mode |
| T9 | Missing atom functional class | Classify missing atoms by MIDDLE slot role |
| T10 | Cross-system comparison | Compare A and B suffix atom inventories |
| T11 | Behavioral divergence MIDDLE vs suffix | Per-atom category JSD across positions |
| T12 | Suffix atom pairwise distances | JSD distance matrix within suffix |

---

## Key Findings

### T1: Population Census
- 11,151 suffixed tokens (48.3%), 11,945 bare tokens (51.7%)
- 35 unique suffix strings
- Top 3: -edy (1,972), -dy (1,000), -aiin (949)
- Atom-length distribution: 1-atom 1,636 (14.7%), 2-atom 5,764 (51.7%), 3-atom 3,751 (33.6%)

### T2: Atom Inventory
- 13 single-char atoms in suffix: {a, d, e, g, h, i, l, m, n, o, r, s, y}
- 5 atoms missing from suffix: {c, f, k, p, t}
- 3 doubled atoms: ee, ii, oo (extensible atoms only)
- All 5 missing atoms have 0 TERMINAL occurrences in MIDDLE -- they never close MIDDLEs either

### T3: First-Atom Category Profile (C1510)
- V(suffix first-atom x category) = 0.277
- This is 53% of MIDDLE HEAD selectivity (V=0.520)
- Top first-atoms: a (36.1%), e (26.7%), d (10.5%), h (9.0%), o (7.9%), ee (6.3%)
- a-first: THERMAL-dominant (41.8%), FLOW secondary (28.3%)
- e-first: THERMAL-dominant (60.5%), FLOW secondary (10.9%)
- h-first: OPERATION-dominant (23.8%), MONITORING secondary (17.4%)

### T4: Last-Atom Positional Profile (C1510)
- R2(suffix last-atom -> position) = 0.059
- This is 1.68x MIDDLE TERM positional signal (R2=0.035)
- Only 5 terminal atoms: y (53.5%), n (19.5%), r (13.1%), l (10.8%), m (3.1%)
- m-terminal: mean position 0.924, line-final enrichment 7.89x
- n, r: interior-biased (mean ~0.476-0.478)
- l: slightly late (mean 0.499)

### T5: Decomposition Verdict
- **PARALLEL_DECOMPOSITION** confirmed
- First-atom = category selector (V=0.277, attenuated from MIDDLE HEAD)
- Last-atom = positional scope marker (R2=0.059, amplified from MIDDLE TERM)
- Suffix is a NARROWER compositional domain with shifted emphasis toward positional scope

### T6: MIDDLE HEAD -> Suffix Content (C1512)
- V(MIDDLE HEAD x suffix first-atom) = 0.305
- k-HEAD routes to a-first (1,109) and e-first (921) -- THERMAL operation outcomes
- e-HEAD routes to a-first (735) and e-first (705) -- balanced stability outcomes
- Headless MIDDLEs route to a-first (799) and e-first (428)

### T7: MIDDLE TERMINAL -> Suffix Content (C1512)
- V(MIDDLE TERMINAL x suffix first-atom) = 0.513
- TERMINAL is 1.68x stronger than HEAD for suffix content prediction
- h-terminal: 98.7% suffix rate, e-first dominant (59.4%)
- y-terminal: 1.6% suffix rate (near-opaque)
- n-terminal: 0.8% suffix rate (near-opaque)
- r-terminal: 19.5%, a-first dominant (72.8%)
- l-terminal: 16.8%, o-first dominant (36.9%)

### T8: Mode A vs B Category Anatomy (C1515)
- Mode A (N=5,676): THERMAL 42.9%, OPERATION 14.8%, MARKING 10.9%, FLOW 10.7%
- Mode B (N=5,454): THERMAL 35.8%, FLOW 22.7%, MARKING 13.2%, STAGING 11.4%
- Mode A enriched: MONITORING 5.08x, CONTAINMENT 2.93x, OPERATION 2.95x, THERMAL 1.20x
- Mode B enriched: FLOW 2.13x, STAGING 2.15x, TRANSITION 2.17x
- Positional: Mode A is medial (mean 0.491), Mode B is boundary-biased (mean 0.514)

### T9: Missing Atom Functional Classes (C1511)
- k, t = ACTION HEADs (primary domain selectors in MIDDLE)
- p, f, c = EXECUTIVE MODIFIERs (parameter modifiers in MIDDLE)
- All 5 also have 0 TERMINAL occurrences in MIDDLE
- Suffix is SYSTEMATICALLY action-free and executive-free

### T10: Cross-System Comparison (C1514)
- A suffix atoms: 13 = B suffix atoms: 13 (identical inventory)
- 0 system-exclusive atoms
- JSD(A, B) = 0.050
- B-enriched: e (0.41x A/B ratio), i (0.35x), d (0.50x) -- execution atoms
- A-enriched: o (3.31x), h (1.71x), l (1.67x), s (2.01x) -- arrangement/state atoms

### T11: Behavioral Divergence (C1513)
- ALL 12 shared atoms divergent MIDDLE vs suffix position
- Mean JSD = 0.526
- Most stable: e (JSD=0.202, THERMAL-dominant in both)
- Most divergent: n (JSD=1.000, TRANSITION in MIDDLE vs FLOW in suffix)
- Key inversions: y (TRANSITION in MIDDLE, THERMAL in suffix), r (FLOW in MIDDLE, STAGING in suffix)

### T12: Suffix Atom Pairwise Distances
- Mean pairwise JSD = 0.108
- Closest: ii-l (0.005), a-n (0.005), l-n (0.006)
- Most distant: ee-h (0.416), h-i (0.361), h-s (0.342)
- h is maximally distant from all other suffix atoms -- unique MONITORING/OPERATION niche

---

## Constraints Produced

| ID | Claim | Tier | Key Evidence |
|----|-------|------|-------------|
| C1510 | Suffix parallel HEAD+TERM decomposition | 2 | First-atom V=0.277 (53% HEAD), last-atom R2=0.059 (1.68x TERM) |
| C1511 | Suffix excludes ACTION HEAD and EXECUTIVE MOD atoms | 2 | Missing {k,t}=ACTION HEADs + {p,f,c}=EXEC MODs; suffix action-free |
| C1512 | MIDDLE terminal dominates suffix content (V=0.513) | 2 | TERM V=0.513 vs HEAD V=0.305 (1.68x); h-term 98.7% suffix, e-first 59.4% |
| C1513 | Suffix atoms universally divergent from MIDDLE atoms | 2 | 12/12 divergent, mean JSD=0.526; e most stable (0.202), n most divergent (1.000) |
| C1514 | Cross-system suffix atom identity (A=B=13, JSD=0.050) | 2 | Identical inventories; B enriches d/e/i (execution), A enriches o/h/l/s (arrangement) |
| C1515 | Suffix mode category anatomy with positional asymmetry | 2 | Mode A: THERMAL/MONITORING/OPERATION/CONTAINMENT, medial; Mode B: FLOW/STAGING/TRANSITION, boundary |

---

## Relationship to Prior Work

### Confirmed/Extended
- **C1408** (suffix HEAD->TERM structure): Confirmed with quantified attenuation/amplification ratios
- **C1409** (suffix atom divergence JSD 0.004-0.560): Extended to full 8-category profiles, ALL 12 atoms divergent (mean 0.526)
- **C1410** (suffix modes are atom-level category partitions): Extended to 8-category resolution with positional asymmetry
- **C1440-C1445** (terminal opacity): h-terminal 98.7% suffix rate, y-terminal 1.6%, n-terminal 0.8% -- fully confirmed
- **C1499** (shared substrate): Extended to suffix layer -- identical atom inventories across A and B (JSD=0.050)
- **C1507** (A arrangement emphasis): A suffix also enriched in o (3.31x) -- arrangement emphasis spans MIDDLE and suffix

### Connected
- **C1393-C1394** (HEAD+MOD*+TERM grammar): Same grammar in suffix layer, attenuated HEAD, amplified TERM
- **C1475-C1479** (HEAD domain differentiation): k/t exclusion from suffix = action domains excluded
- **C1389-C1392** (c/p/f modifier roles): Executive modifier exclusion from suffix = parameterization excluded
- **C1412** (MIDDLE terminal dominates suffix): Confirmed at atom level (V=0.513 vs 0.305)
- **C1413** (PREFIX-SUFFIX MIDDLE-mediated): Specifically through TERMINAL atom, not HEAD

---

## Verdict

The suffix is a PARALLEL compositional domain -- same shared alphabet, same HEAD+TERM structure, but with compressed inventory (13 vs 18 atoms), shifted emphasis (category selection attenuated, positional scope amplified), and categorically different atom semantics (mean JSD=0.526 vs MIDDLE). The suffix is systematically action-free and executive-free: it encodes outcomes, conditions, and positional scope but never the operational actions or executive parameters themselves. Cross-system identity is perfect (A=B=13 atoms, JSD=0.050), extending the manuscript-wide shared substrate to the suffix layer.
