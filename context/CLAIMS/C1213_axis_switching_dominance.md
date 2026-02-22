# C1213: Axis-Switching Dominance Between Tokens

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** CROSS_TOKEN_CHAINING (Phase 430)
**Relates to:** C1207 (atom correlation clusters), C1212 (cross-token sequential chaining), C1208 (atom carryover classification)

---

## Statement

Between consecutive tokens, programs switch C1207 axes 84.8% of the time. Same-axis continuation occurs at 15.2%, only 1.15x the expected rate of 13.2% under independence. Currier B programs are multi-axis instruction sequences that alternate between operational channels rather than executing long same-axis runs.

### Axis Transition Rates

| Metric | Value |
|--------|-------|
| Same-axis rate | 15.2% |
| Expected same-axis | 13.2% |
| Enrichment | 1.15x |
| Switch rate | 84.8% |

### Largest Same-Axis Flows

| Transition | Count | Notes |
|------------|-------|-------|
| ITERATION->ITERATION | 1,113 | Largest same-axis block |
| STABILITY->STABILITY | 320 | Second largest |
| CLOSURE->CLOSURE | 315 | |
| ENERGY->ENERGY | 160 | |
| STRUCTURAL->STRUCTURAL | 110 | |
| MONITORING->MONITORING | 59 | |

### Largest Cross-Axis Flows

| Transition | Count | Notes |
|------------|-------|-------|
| CLOSURE->STABILITY | 1,770 | Dominant cross-axis flow |
| ITERATION->STABILITY | 1,184 | Second largest |
| CLOSURE->ITERATION | 951 | |
| ENERGY->STABILITY | 886 | |

STABILITY is the dominant target from all axes, consistent with its role as the convergence attractor (C1207 cluster: {e,t,s}).

---

## Interpretation

The near-chance same-axis rate (1.15x) means programs do not execute extended runs of same-axis instructions. Instead, they interleave across axes: an iteration instruction, then a stability instruction, then a closure instruction, etc. This is consistent with a control system that must attend to multiple operational dimensions within each line (control block).

The exception is ITERATION->ITERATION at 1,113 tokens (33.2% of post-iteration tokens stay iteration), which is elevated relative to other same-axis pairs. This aligns with C1208's finding that iteration-axis atoms {a,i,n,r} have mixed carryover (a,r positive; i,n negative).

---

## Method

- Each atom mapped to its C1207 axis (ITERATION, ENERGY, CLOSURE, MONITORING, STRUCTURAL, STABILITY, FREE_T, OTHER)
- TERMINAL atom of token N classified by axis, INITIAL atom of token N+1 classified by axis
- Same-axis = both atoms on same C1207 axis
- Expected same-axis = sum of squared axis marginal proportions
- 13,737 consecutive within-line token pairs

**Script:** `phases/CROSS_TOKEN_CHAINING/scripts/chaining_test.py` (T3)
**Results:** `phases/CROSS_TOKEN_CHAINING/results/chaining_results.json`
