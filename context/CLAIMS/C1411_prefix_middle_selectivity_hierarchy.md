# C1411: PREFIX->MIDDLE Selectivity Hierarchy with Sister Pair Atom Identity

**Tier:** 2 (ESTABLISHED)
**Scope:** B, PREFIX, MIDDLE, atom, sister pair, selectivity
**Phase:** CROSS_SLOT_INTERACTION (Phase 516)
**Extends:** C911 (PREFIX-MIDDLE compatibility), C1305 (MIDDLE determines category), C1219 (base determines MIDDLE content)
**Relates to:** C1003 (pairwise compositionality), C1218 (PREFIX internal grammar)

---

## Statement

PREFIX strongly selects MIDDLE HEAD atom (V=0.414, MI=1.089 bits, N=16,537) and moderately selects MIDDLE TERM atom (V=0.314, MI=0.384 bits, N=7,428). Sister pairs (ch/sh, ok/ot) select **nearly identical** MIDDLE atom distributions (JSD=0.010-0.012 for both HEAD and TERM), quantifying C1305 at atom resolution: sisters differ in manner/mode, not in which operational atoms they access.

### PREFIX -> MIDDLE HEAD Selectivity

| PREFIX | Dominant HEAD atoms | Domain |
|--------|-------------------|--------|
| qo | k (53.1%), t (18.1%), e (2.1%) | THERMAL/ENERGY |
| ch | e (70.6%), o (15.2%), a (4.1%) | STABILITY |
| sh | e (78.5%), o (12.1%), a (2.9%) | STABILITY |
| ok | e (46.4%), a (43.5%) | ITERATION/STABILITY |
| ot | e (46.1%), a (39.6%), o (7.8%) | ITERATION/STABILITY |
| da | i (45.9%), r (18.2%), d (10.5%) | INFRASTRUCTURE |

### Sister Pair Identity

| Comparison | HEAD JSD | TERM JSD | Interpretation |
|------------|----------|----------|----------------|
| ch vs sh | 0.010 | 0.010 | Near-identical atom selection |
| ok vs ot | 0.010 | 0.012 | Near-identical atom selection |

### PREFIX Base vs Modifier

PREFIX base (last character) predicts MIDDLE HEAD at V=0.494, vs modifier V=0.295. Base is 1.67x more informative than modifier for MIDDLE content selection, confirming C1219 at the cross-slot atom level.

---

## Falsification Criteria

1. If a sister pair shows JSD > 0.10 for HEAD or TERM atom distributions, the atom-identity claim fails
2. If the PREFIX -> MIDDLE HEAD V drops below 0.20 with better morphological parsing, the selectivity is weaker than claimed
3. If modifier alone predicts MIDDLE HEAD better than base (V_modifier > V_base), C1219 is overturned

---

## Method

- 23,096 Currier B tokens decomposed into PREFIX, MIDDLE HEAD, MIDDLE TERM using C1393 atom roles
- Chi-squared tests, Cramer's V, mutual information for PREFIX -> HEAD and PREFIX -> TERM
- Jensen-Shannon divergence between sister pair HEAD/TERM distributions
- Separate base/modifier analysis using C1218 PREFIX decomposition

**Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
**Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` (T1, T7)
