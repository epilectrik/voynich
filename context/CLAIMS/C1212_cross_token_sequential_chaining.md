# C1212: Cross-Token Sequential Chaining

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** CROSS_TOKEN_CHAINING (Phase 430)
**Relates to:** C1207 (atom correlation clusters), C1208 (atom carryover classification), C1209 (MIDDLE positional grammar), C1210 (MIDDLE slot syntax), C1001 (cross-token MI through PREFIX)

---

## Statement

The TERMINAL atom of token N predicts the INITIAL atom of token N+1 with genuine sequential structure (chi2=1242.9, V=0.0709, MI=0.0637 bits, shuffle z=19.74), but this cross-token signal is much weaker than within-MIDDLE slot syntax (V ratio=0.231, MI ratio=0.059). Cross-line transitions are NOT weaker than within-line transitions (cross-line MI=0.0804, ratio=1.262).

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

---

## Method

- 13,737 consecutive within-line token pairs from Currier B
- TERMINAL = last character of token N's MIDDLE, INITIAL = first character of token N+1's MIDDLE
- Multi-character MIDDLEs only (len >= 2)
- 1000-iteration shuffle control: permute MIDDLEs within lines to break sequential order
- Cross-line: 2,334 pairs spanning line boundaries within same folio

**Script:** `phases/CROSS_TOKEN_CHAINING/scripts/chaining_test.py` (T1, T1b, T2, T4)
**Results:** `phases/CROSS_TOKEN_CHAINING/results/chaining_results.json`
