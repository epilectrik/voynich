# C1205: i-Atom Orthogonal to k/e Energy System

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** I_ATOM_CHARACTERIZATION (Phase 427)
**Extends:** C1197 (atom extensibility partition), C1200 (k/e state carryover)
**Relates to:** C1195 (i = cycle/iterate), C777 (i/ii FL INITIAL), C1003 (pairwise compositionality)

---

## Statement

The i-atom operates on a structurally independent axis from the k/e energy state system. Evidence from five independent tests:

### 1. No carryover (anti-clustering)
i shows NO within-line state carryover. P(i in B | i in A) = 0.112 vs P(i in B | no i in A) = 0.120, delta = -0.008. Shuffle z-score = -6.14 (significantly BELOW random -- i actively anti-clusters). This is the structural opposite of k/e carryover (C1200: z = +7.90).

### 2. Atom-level disjunction
i-containing MIDDLEs have near-zero k (0.009 vs 0.104) and near-zero e (0.005 vs 0.236). Chi-squared = 2,272.4 (df=2). i occupies its own atom space, nearly disjoint from k/e.

### 3. Folio-level anti-correlation
r(i-fraction, k-fraction) = -0.437, r(i-fraction, e-fraction) = -0.412 across 82 folios. Folios with more i have less of BOTH k and e. For reference, r(k, e) = +0.079 (near-zero).

### 4. Program-specific distribution
i-fraction varies by program: within-section/between-section variance ratio = 1.83 (PROGRAM_SPECIFIC). BIO depleted (0.083), COSMO/STARS_RECIPE enriched (0.161/0.148). HERBAL has highest within-section CV (0.42).

### 5. Partial carryover interruption
When an i-token mediates between k-terminal and next token, k/e carryover is dampened: deviation from baseline halved (0.017 vs 0.030). i partially resets the energy state chain but does not fully break it.

### 6. daiin-controlled replication
All signals survive removal of aiin-containing tokens (T5: carryover z = -3.97, chi2 = 1,566.3). Findings are not daiin artifacts.

---

## Energy Profile by i-Count

Lines with higher i-count have lower energy content:

| Category | Lines | k-frac | e-frac | h-frac | tok/line |
|----------|-------|--------|--------|--------|----------|
| no_i | 825 | 0.115 | 0.231 | 0.039 | 8.8 |
| single_i | 514 | 0.092 | 0.197 | 0.037 | 9.7 |
| double_i | 1,067 | 0.069 | 0.174 | 0.027 | 10.2 |

Both k and e drop equally with increasing i-count. i displaces energy content rather than modulating the k/e ratio.

---

## Method

- 23,096 Currier B tokens across 2,420 lines
- T2: Within-line and cross-line conditional probabilities with 1,000 shuffle permutations
- T3: Token-level atom fractions, line-level median split, folio-level Pearson correlations, chi-squared independence test
- T5: All tests replicated excluding aiin-containing MIDDLEs
- T6a: 3-token window carryover interruption test
- T6c: Line classification by max i-run

**Script:** `phases/I_ATOM_CHARACTERIZATION/scripts/i_atom_test.py` (T2, T3, T5, T6a, T6c)
**Results:** `phases/I_ATOM_CHARACTERIZATION/results/i_atom_results.json`
