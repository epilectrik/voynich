# C1212: Cross-Token Sequential Chaining

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** CROSS_TOKEN_CHAINING (Phase 430)
**Relates to:** C1207 (atom correlation clusters), C1208 (atom carryover classification), C1209 (MIDDLE positional grammar), C1210 (MIDDLE slot syntax), C1001 (cross-token MI through PREFIX)

---

## Statement

The TERMINAL atom of token N predicts the INITIAL atom of token N+1 with genuine sequential structure (chi2=1242.9, V=0.0709, MI=0.0637 bits, shuffle z=19.74), but this cross-token signal is much weaker than within-MIDDLE slot syntax (V ratio=0.231, MI ratio=0.059). Cross-line transitions are NOT weaker than within-line transitions (cross-line MI=0.0804, ratio=1.262).

### Full 3x3 Slot Matrix

All 9 cross-token slot pairings were tested (T5). TERMINAL->INITIAL has the highest genuine sequential signal despite not having the highest raw MI.

| Rank by z | Cell | MI (obs) | MI (shuf) | z-score |
|-----------|------|----------|-----------|---------|
| 1 | TERMINAL->INITIAL | 0.0637 | 0.0270 | 20.3 |
| 2 | INITIAL->INITIAL | 0.0521 | 0.0283 | 13.5 |
| 3 | TERMINAL->TERMINAL | 0.0566 | 0.0336 | 11.6 |
| 4 | MEDIAL->INITIAL | 0.0703 | 0.0389 | 10.4 |
| 5 | MEDIAL->TERMINAL | 0.0638 | 0.0424 | 6.8 |
| 6 | INITIAL->TERMINAL | 0.0385 | 0.0272 | 6.3 |
| 7 | TERMINAL->MEDIAL | 0.0596 | 0.0422 | 5.8 |
| 8 | MEDIAL->MEDIAL | 0.0924 | 0.0739 | 3.4 |
| 9 | INITIAL->MEDIAL | 0.0462 | 0.0387 | 2.6 |

MEDIAL->MEDIAL has the highest raw MI (0.0924) but the lowest z-score among significant cells (3.4). 80% of its MI is within-line co-occurrence, not sequential structure. The token boundary (TERMINAL->INITIAL) is where genuine sequential order resides.

### PREFIX Lane Stratification

Within-lane consecutive pairs (both tokens share the same PREFIX lane) show that MEDIAL->MEDIAL persists within lanes but is driven by within-line homogeneity, not sequence:

| Lane | MEDIAL x MEDIAL MI | n |
|------|-------------------|---|
| BARE | 0.725 | 124 |
| qo | 0.550 | 81 |
| ch | 0.513 | 141 |
| OTHER | 0.488 | 116 |
| sh | 0.413 | 85 |
| ol | 0.282 | 197 |

The signal does not collapse under lane stratification (not purely a PREFIX confound per C911/C1001), but combined with the shuffle z=3.4, it reflects within-line compositional homogeneity rather than genuine sequential chaining.

### Cross-Token Contingency

| Metric | Value |
|--------|-------|
| N pairs | 13,737 |
| chi2 | 1,242.9 |
| Cramer's V | 0.0709 |
| Mutual information | 0.0637 bits |
| Shuffle mean MI | 0.0272 |
| Shuffle z-score | 19.74 |

### Enriched Transitions (obs/exp > 1.5x)

| Pair | Obs | Exp | Ratio |
|------|-----|-----|-------|
| h->p | 29 | 11.1 | 2.61x |
| r->a | 417 | 209.6 | 1.99x |
| y->q | 45 | 23.6 | 1.91x |
| i->o | 96 | 55.5 | 1.73x |
| h->t | 40 | 25.3 | 1.58x |
| e->k | 81 | 53.8 | 1.51x |

### Depleted Transitions (obs/exp < 0.5x)

| Pair | Obs | Exp | Ratio |
|------|-----|-----|-------|
| r->t | 6 | 24.2 | 0.25x |
| r->l | 7 | 23.4 | 0.30x |
| i->d | 7 | 20.1 | 0.35x |
| n->t | 16 | 43.1 | 0.37x |
| r->k | 25 | 67.7 | 0.37x |
| r->i | 18 | 47.9 | 0.38x |
| n->l | 18 | 41.6 | 0.43x |
| n->k | 60 | 120.5 | 0.50x |

### Cross vs Within Comparison

| Metric | Within-MIDDLE | Cross-Token | Ratio |
|--------|---------------|-------------|-------|
| Cramer's V | 0.3073 | 0.0709 | 0.231 |
| MI (bits) | 1.0714 | 0.0637 | 0.059 |

### Cross-Line Boundary

| Metric | Within-line | Cross-line |
|--------|-------------|------------|
| N pairs | 13,737 | 2,334 |
| Cramer's V | 0.0709 | 0.0868 |
| MI (bits) | 0.0637 | 0.0804 |
| MI ratio | -- | 1.262 |

Cross-line transitions are slightly STRONGER than within-line, contradicting an assumption that line boundaries reset sequential state. This is consistent with C1200's finding that carryover resets at boundaries for k/e state specifically, but cross-token atom chaining operates at a different level.

### daiin-Excluded Control (T1b)

Results survive singleton exclusion: N=12,418, V=0.0722, z=16.13. Same enriched/depleted pattern. The chaining signal is not driven by high-frequency formulaic tokens.

---

## Interpretation

Cross-token chaining exists but is a WEAK constraint relative to within-MIDDLE syntax. Each token is primarily a self-contained instruction (C1210, C1211), with modest sequential dependencies between tokens. The enriched pairs follow C1207 axis boundaries (r->a both iteration, e->k energy cycle) but also cross axes (h->p monitoring->structural, i->o iteration->structural).

The depleted pairs show that iteration-TERMINAL atoms (r, n) strongly avoid starting energy-axis tokens (k, l, t), suggesting that iteration instructions are followed by non-energy instructions.

The 3x3 slot matrix with shuffle controls establishes that genuine sequential structure resides at the token boundary (TERMINAL->INITIAL, z=20.3), not in operational core repetition (MEDIAL->MEDIAL, z=3.4). The MEDIAL row's high raw MI reflects within-line compositional homogeneity -- tokens on the same line tend to share MEDIAL atoms -- but this is co-occurrence, not sequence-dependent.

---

## Method

- 13,737 consecutive within-line token pairs from Currier B
- TERMINAL = last character of token N's MIDDLE, INITIAL = first character of token N+1's MIDDLE
- MEDIAL = second character of MIDDLE (requires len >= 3)
- Multi-character MIDDLEs only (len >= 2)
- 1000-iteration shuffle control (T1): permute token order within lines
- 500-iteration shuffle control (T5b): all 9 slot-pair cells
- Cross-line: 2,334 pairs spanning line boundaries within same folio
- PREFIX lane stratification (T5c): qo, ch, sh, da, ol, BARE, OTHER

**Script:** `phases/CROSS_TOKEN_CHAINING/scripts/chaining_test.py` (T1, T1b, T2, T4, T5, T5b, T5c)
**Results:** `phases/CROSS_TOKEN_CHAINING/results/chaining_results.json`
