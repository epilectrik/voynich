# C1204: i-Extension Inverted Gradient

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** I_ATOM_CHARACTERIZATION (Phase 427)
**Extends:** C1197 (atom extensibility partition), C901 (e stability gradient)
**Relates to:** C1195 (i = cycle/iterate, LOCKED), C777 (i/ii FL INITIAL markers)

---

## Statement

The i-extension gradient is structurally inverted relative to e. For e, single-e dominates (81.1%) with monotonic decline to ee (18.1%), eee (0.8%). For i, double-i (53.7%) is MORE common than single-i (45.9%), with iii at 0.3%. Despite near-identical total extension counts (C1197: 1555 e vs 1554 i), their gradient shapes are opposite.

| Run length | i-count | i-% | e-count | e-% |
|------------|---------|-----|---------|-----|
| 1 | 1,321 | 45.9% | 6,678 | 81.1% |
| 2 | 1,544 | 53.7% | 1,490 | 18.1% |
| 3 | 10 | 0.3% | 64 | 0.8% |
| 4 | 0 | 0.0% | 1 | 0.0% |

The inversion is driven by the aIn family (ain/aiin = 420/834, ii-form 2x more common) and In family (in/iin = 264/560, ii-form 2.1x more common). By section: HERBAL has highest ii+ rate (67.6%), BIO lowest (46.7%).

---

## Interpretation

e-extension encodes depth/stability gradients (C901: e->ee->eee = increasing stability depth). The inverted i-gradient suggests i-extension encodes something structurally different. Given i = "cycle/iterate" (C1195), the doubled form (ii) being dominant is consistent with iteration being the default mode -- procedures typically repeat rather than execute once.

---

## Method

- 23,096 Currier B tokens, morphologically decomposed
- Counted maximum consecutive i/e runs per MIDDLE
- Mapped ratio families by non-i skeleton
- Stratified by section

**Script:** `phases/I_ATOM_CHARACTERIZATION/scripts/i_atom_test.py` (T1)
**Results:** `phases/I_ATOM_CHARACTERIZATION/results/i_atom_results.json`
