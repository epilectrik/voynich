# C1210: MIDDLE Slot Syntax -- Forbidden Combinations and Strong Affinities

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MIDDLE_SLOT_INTERACTION (Phase 429)
**Extends:** C1209 (MIDDLE positional grammar), C1065 (atom bigram ordering grammar)
**Relates to:** C1207 (atom correlation clusters), C1190 (additive behavioral composition)

---

## Statement

The INITIAL and TERMINAL positional slots within MIDDLEs are NOT independent. Chi2=27,465 (df=342), Cramer's V=0.307, MI=1.071 bits across 16,153 multi-character MIDDLEs. The interaction persists at all MIDDLE lengths: V=0.428 (len 2), V=0.371 (len 3), V=0.285 (len 4+). This is not an adjacency effect from C1065 -- at length 4+, INITIAL and TERMINAL atoms are separated by 2+ medial atoms yet interaction remains strong.

### Forbidden INITIAL-TERMINAL Combinations

Near-categorical exclusions where observed count is 0 or 1 despite high expected counts:

| INITIAL | TERMINAL | Observed | Expected | Ratio |
|---------|----------|----------|----------|-------|
| a | y | 1 | 796 | 0.00x |
| e | n | 1 | 813 | 0.00x |
| i | y | 1 | 243 | 0.00x |
| i | e | 0 | 53 | 0.00x |
| k | n | 0 | 135 | 0.00x |
| c | n | 0 | 81 | 0.00x |
| c | l | 0 | 65 | 0.00x |
| d | n | 0 | 107 | 0.00x |
| t | n | 0 | 46 | 0.00x |
| p | n | 0 | 21 | 0.00x |
| q | n | 0 | 14 | 0.00x |

The pattern: **n-terminal is forbidden with every INITIAL atom except a and i.** Only the iteration-axis atoms (C1207: {a,i,n,r}) can produce n-completion. Similarly, a-initial never produces y-terminal -- the iteration axis and closure axis (C1207: {d,y}) are mutually exclusive in the same MIDDLE.

### Strong Affinities

| INITIAL | TERMINAL | Observed | Expected | Ratio | C1207 Cluster |
|---------|----------|----------|----------|-------|---------------|
| k | e | 464 | 58 | 7.94x | Energy -> Stability |
| p | h | 87 | 12 | 7.24x | Structural -> Monitoring |
| i | n | 825 | 122 | 6.78x | Iteration axis |
| c | t | 96 | 15 | 6.58x | Monitoring -> FREE |
| c | k | 200 | 34 | 5.81x | Monitoring -> Energy |
| c | h | 233 | 47 | 4.98x | Monitoring axis |
| a | m | 174 | 40 | 4.38x | Iteration -> Terminal |
| a | n | 1272 | 399 | 3.18x | Iteration axis |
| d | y | 677 | 213 | 3.18x | Closure axis |

Affinities align precisely with C1207 correlation clusters: iteration atoms pair with iteration atoms, closure with closure, monitoring with monitoring. The slot syntax enforces cluster-internal pairing.

### FREE Atoms (k, t) When Initial

k-initial strongly selects e-terminal (45.6%), consistent with energy→stability response. t-initial is more distributed (29.3% e, 22.3% h, 13.9% o, 13.3% d), suggesting k and t have different operational profiles despite both being position-free.

---

## Compatibility with C1190

C1190 established additive behavioral composition: given atoms A and B, the compound AB has behavioral profile A + B. This constraint shows that which atoms A and B appear together is non-random. Both are true simultaneously -- the behavioral output is additive, but the selection of which atoms co-occur has syntax. Analogy: amino acids fold additively, but which amino acids appear adjacent in a protein sequence is highly non-random.

---

## Method

- 16,153 multi-character Currier B MIDDLEs, stratified by length (2, 3, 4+)
- Contingency tables: INITIAL x TERMINAL character
- Chi-squared independence test, Cramer's V, mutual information
- Enrichment ratios (observed/expected) with minimum expected count >= 5

**Script:** `phases/MIDDLE_SLOT_INTERACTION/scripts/slot_interaction_test.py` (T1, T4)
**Results:** `phases/MIDDLE_SLOT_INTERACTION/results/slot_interaction_results.json`
