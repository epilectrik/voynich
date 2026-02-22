# C1208: Atom Carryover Classification -- Three Behavioral Classes

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ATOM_BEHAVIORAL_CENSUS (Phase 428)
**Extends:** C1200 (k/e state carryover z=+7.90), C1205 (i anti-clustering z=-6.14)
**Relates to:** C1190 (behavioral atomicity), C1207 (atom correlation clusters)

---

## Statement

All 18 testable atoms classify into three carryover classes based on within-line state persistence (1000-iteration shuffle permutation test):

### POSITIVE Carryover (state persists token-to-token): 9 atoms

| Atom | z-score | P(B\|A) | P(B\|~A) | Delta |
|------|---------|---------|----------|-------|
| m | +9.58 | 0.077 | 0.014 | +0.063 |
| a | +7.97 | 0.255 | 0.146 | +0.109 |
| p | +4.27 | 0.164 | 0.026 | +0.138 |
| t | +4.13 | 0.132 | 0.064 | +0.068 |
| h | +4.12 | 0.128 | 0.066 | +0.062 |
| k | +3.55 | 0.247 | 0.185 | +0.062 |
| c | +3.23 | 0.139 | 0.089 | +0.050 |
| r | +2.59 | 0.124 | 0.089 | +0.036 |
| s | +2.47 | 0.056 | 0.021 | +0.035 |

### NEGATIVE Carryover (anti-clustering): 4 atoms

| Atom | z-score | P(B\|A) | P(B\|~A) | Delta |
|------|---------|---------|----------|-------|
| i | -6.14 | 0.112 | 0.120 | -0.008 |
| y | -5.96 | 0.210 | 0.220 | -0.010 |
| e | -4.31 | 0.365 | 0.347 | +0.019 |
| n | -3.91 | 0.090 | 0.089 | +0.001 |

### NEUTRAL (no significant carryover): 5 atoms

| Atom | z-score | P(B\|A) | P(B\|~A) | Delta |
|------|---------|---------|----------|-------|
| f | +1.30 | 0.071 | 0.009 | +0.062 |
| o | +0.75 | 0.225 | 0.174 | +0.051 |
| d | -0.71 | 0.224 | 0.180 | +0.044 |
| l | -0.42 | 0.147 | 0.136 | +0.011 |
| q | +0.08 | 0.017 | 0.006 | +0.011 |

---

## Key Finding: e Anti-Clusters

e shows NEGATIVE carryover (z=-4.31), meaning e-presence in token A makes e LESS likely in token B than random. This does not contradict C1200, which measured directional terminal-to-initial transitions (k→e and e→k alternation patterns). The distinction:

- **C1200 (directional):** k-terminal tokens predict e-initial successors (transition carryover)
- **C1208 (presence):** e-containing tokens predict FEWER e-containing successors (identity anti-clustering)

Both are true simultaneously: the system alternates energy states (C1200) while avoiding consecutive tokens with the same atom (C1208). This is consistent with e encoding a "stability/cooling" state that resolves rather than persists.

---

## Cross-Line Reset

Carryover is predominantly within-line. For POSITIVE atoms, the within/cross-line ratio ranges from 1.6x (k) to 21x (a) and infinity (p, s show negative cross-line). For NEGATIVE atoms, the anti-clustering reverses or vanishes across line boundaries. This confirms C1200's line-boundary reset finding extends to all atoms.

---

## daiin-Controlled Replication (T2b)

All classifications survive aiin exclusion. The four NEGATIVE atoms remain NEGATIVE (i z=-3.97, y z=-6.20, e z=-4.88, n z=-2.66). One NEUTRAL atom (o) shifts to marginally POSITIVE (z=+2.01). All other POSITIVE atoms remain POSITIVE.

---

## Method

- 23,096 Currier B tokens across 2,420 lines
- For each atom X: P(X in B | X in A) vs P(X in B | no X in A) for consecutive within-line pairs
- 1000 shuffle permutations per test (MIDDLEs shuffled within lines)
- z-score computed from permutation distribution
- Classification: z > 2 POSITIVE, z < -2 NEGATIVE, else NEUTRAL
- Min 30 atom occurrences to include

**Script:** `phases/ATOM_BEHAVIORAL_CENSUS/scripts/atom_census_test.py` (T2, T2b)
**Results:** `phases/ATOM_BEHAVIORAL_CENSUS/results/atom_census_results.json`
