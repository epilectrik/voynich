# C1413: PREFIX-SUFFIX Coupling Is MIDDLE-Mediated

**Tier:** 2 (ESTABLISHED)
**Scope:** B, PREFIX, MIDDLE, suffix, independence, mediation
**Phase:** CROSS_SLOT_INTERACTION (Phase 516)
**Extends:** C1003 (pairwise compositionality, no three-way synergy), C1346 (contextual modulation decomposition)
**Relates to:** C1411 (PREFIX->MIDDLE selectivity), C1412 (MIDDLE->SUFFIX selectivity)

---

## Statement

PREFIX and SUFFIX are the most independent morphological slot pair (NMI=0.090, MI=0.283 bits, z=79.1). Their coupling is almost entirely mediated through MIDDLE: PREFIX-MIDDLE NMI=0.481, MIDDLE-SUFFIX NMI=0.451, but PREFIX-SUFFIX NMI=0.090. Three-way synergy for suffix mode is +0.047 bits (mild) and for suffix identity +0.009 bits (negligible). The instruction encoding chain is PREFIX -> MIDDLE -> SUFFIX, not a three-way interaction.

### Slot Independence Hierarchy

| Pair | MI (bits) | NMI | z-score | Interpretation |
|------|-----------|-----|---------|----------------|
| MIDDLE <-> SUFFIX | 1.767 | 0.451 | 239.1 | Strongest coupling |
| PREFIX <-> MIDDLE | 1.514 | 0.481 | 148.5 | Strong coupling |
| PREFIX <-> SUFFIX | 0.283 | 0.090 | 79.1 | Weak (mediated) |

### Three-Way Synergy Test

| Target | I(PREFIX) | I(MIDDLE) | I(joint) | Synergy | Verdict |
|--------|-----------|-----------|----------|---------|---------|
| Suffix mode | 0.021 | 0.384 | 0.452 | +0.047 | Mild positive |
| Suffix identity | 0.269 | 1.704 | 1.982 | +0.009 | Negligible |

### Conditional Entropy Chain

| Conditioning | H(SUFFIX) remaining | % of total |
|-------------|--------------------|----|
| Nothing | 3.915 bits | 100% |
| PREFIX only | 3.632 bits | 92.8% |
| MIDDLE only | 2.148 bits | 54.9% |
| PREFIX + MIDDLE | 1.853 bits | 47.3% |

PREFIX provides only +5.5pp additional suffix reduction beyond MIDDLE alone (from 54.9% to 47.3%). Most of PREFIX's apparent suffix information is redundant with what MIDDLE already carries.

### Information Chain Architecture

```
PREFIX --[1.514 bits]--> MIDDLE --[1.767 bits]--> SUFFIX
  |                                                  ^
  +----------[0.283 bits, mostly mediated]-----------+
```

---

## Falsification Criteria

1. If PREFIX-SUFFIX NMI exceeds 0.30 without MIDDLE conditioning, direct coupling exists
2. If three-way synergy > 0.20 bits for suffix identity, the pairwise mediation model is insufficient
3. If conditioning on MIDDLE reduces PREFIX-SUFFIX MI by less than 50%, MIDDLE mediation is partial

---

## Method

- 9,422 tokens with all three slots (PREFIX + MIDDLE + SUFFIX) present
- Mutual information and normalized MI for all three slot pairs
- Three-way synergy: I(PREFIX+MIDDLE; SUFFIX) - I(PREFIX; SUFFIX) - I(MIDDLE; SUFFIX)
- Conditional entropy chain: H(SUFFIX), H(SUFFIX|PREFIX), H(SUFFIX|MIDDLE), H(SUFFIX|PREFIX,MIDDLE)

**Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
**Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` (T4, T5, T8)
