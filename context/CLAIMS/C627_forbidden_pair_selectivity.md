# C627: Forbidden Pair Selectivity

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** HAZARD_CIRCUIT_TOKEN_RESOLUTION

## Statement

Within hazard class-pairs, forbidden tokens are **not** frequency-biased (mean normalized rank 0.562, expected 0.500). Reciprocal asymmetry is strong: 8/17 forbidden A->B pairs have allowed B->A (0 have both forbidden). Circuit direction is the primary discriminant, explaining **9/12 classifiable pairs (75%)**: 6 reverse-flow prohibitions + 2 EN_CHSH internal + 1 FL_HAZ internal. Two FORWARD-specific and 1 CROSS_GROUP pair remain unexplained by direction alone. The hazard system is a **directional, token-specific lookup table** -- not frequency-dependent, not morphologically predictable, but partially circuit-structured.

## Evidence

### Frequency Analysis

| Class | Members | Forbidden Ranks | Pattern |
|-------|---------|-----------------|---------|
| 7 (FL_HAZ) | 2 | 1, 2 | All forbidden (saturated) |
| 8 (EN_CHSH) | 3 | 1, 2, 3 | All forbidden (saturated) |
| 9 (FQ_CONN) | 3 | 1, 2, 3 | All forbidden (saturated) |
| 23 (FQ_CLOSER) | 7 | 1, 5, 6 | Mixed |
| 30 (FL_HAZ) | 5 | 2 | Single |
| 31 (EN_CHSH) | 12 | 1, 2 | Top 2 only |

Mean normalized rank: 0.562 (0=highest, 1=lowest). Expected if random: 0.500.
Classes 7, 8, 9 are fully saturated (all members forbidden) -- no frequency discrimination possible. Class 23 shows no frequency pattern (ranks 1, 5, 6 of 7).

### Reciprocal Pair Analysis

| Status | Count |
|--------|-------|
| Both directions forbidden | 0 |
| A->B forbidden, B->A allowed | 8 |
| A->B forbidden, B->A unobserved | 9 |

For the 4 REVERSE forbidden pairs with observed reciprocals, the forward direction (B->A) is always allowed (counts 1-5). This confirms directional asymmetry: the circuit blocks specific directions, not specific token pairings.

### Predictive Summary

| Explanation Category | Count | % |
|---------------------|-------|---|
| REVERSE_CIRCUIT | 6 | 35.3% |
| UNCLASSIFIED_TOKEN | 5 | 29.4% |
| EN_CHSH_INTERNAL | 2 | 11.8% |
| FORWARD_SPECIFIC | 2 | 11.8% |
| FL_HAZ_INTERNAL | 1 | 5.9% |
| CROSS_GROUP | 1 | 5.9% |

Among 12 classifiable pairs: 9 explained by circuit topology (75%), 3 unexplained (25%).

### Unexplained Pairs

| Pair | Direction | Explanation Needed |
|------|-----------|-------------------|
| dy -> chey | FORWARD (FQ_CLOSER -> EN_CHSH) | Forward-circuit, not reverse |
| l -> chol | FORWARD (FQ_CLOSER -> EN_CHSH) | Forward-circuit, not reverse |
| dy -> aiin | CROSS_GROUP (FQ_CLOSER -> FQ_CONN) | Inter-FQ transition |

All three unexplained pairs involve FQ_CLOSER source tokens (dy, l). FQ_CLOSER is a boundary specialist (C597) that sits outside the main FL->FQ_CONN->EN circuit. These may represent boundary-specific prohibitions rather than circuit-direction prohibitions.

## Interpretation

The hazard system is a hybrid mechanism: primarily circuit-directional (75% explained by topology), with a secondary boundary-specific component involving FQ_CLOSER tokens. It is not frequency-driven (no systematic bias), not morphologically predictable (C623), and not lane-dependent (C626). The zero reciprocal-forbidden rate (0/17 pairs forbidden in both directions) is the strongest single piece of evidence for directional structure.

## Extends

- **C624**: Resolves the within-pair discrimination question -- forbidden tokens are specific but not frequency-biased
- **C625**: Combined with direction analysis to produce the 75% classification rate

## Related

C109, C541, C597, C622, C623, C624, C625, C626
