# C1412: MIDDLE Dominates Suffix Determination via Terminal Atom

**Tier:** 2 (ESTABLISHED)
**Scope:** B, MIDDLE, suffix, atom, selectivity, terminal
**Phase:** CROSS_SLOT_INTERACTION (Phase 516)
**Extends:** C1338 (MIDDLE suffix selectivity), C1408 (suffix compositional structure), C1393 (MIDDLE HEAD+MOD+TERM)
**Relates to:** C1003 (pairwise compositionality), C1229 (alternating suffix modes)

---

## Statement

MIDDLE is the dominant suffix determinant at every level: full MIDDLE -> suffix mode V=0.678 (MI=0.422 bits), MIDDLE TERM -> suffix mode V=0.503 (MI=0.187 bits), MIDDLE HEAD -> suffix mode V=0.323 (MI=0.091 bits). MIDDLE HEAD also strongly predicts suffix PRESENCE (V=0.568). MIDDLE TERM alone outpredicts PREFIX (V=0.503 vs 0.169) for suffix mode selection. The terminal atom of the MIDDLE is the primary cross-slot junction for suffix determination.

### Selectivity Hierarchy

| Predictor | Suffix mode V | Suffix mode MI | N |
|-----------|--------------|----------------|---|
| Full MIDDLE | 0.678 | 0.422 bits | 10,940 |
| MIDDLE TERM only | 0.503 | 0.187 bits | 1,755 |
| MIDDLE HEAD only | 0.323 | 0.091 bits | 9,425 |
| PREFIX | 0.169 | 0.021 bits | 9,246 |

### MIDDLE HEAD -> Suffix Mode Polarization

| HEAD atom | Mode A fraction | Interpretation |
|-----------|----------------|----------------|
| d | 0.031 | Near-pure Mode B (STAGING/FLOW) |
| r | 0.008 | Near-pure Mode B |
| i | 0.032 | Near-pure Mode B |
| h | 0.681 | Strong Mode A (THERMAL/MONITORING) |
| e | 0.562 | Moderate Mode A |
| k | 0.549 | Moderate Mode A |
| a | 0.227 | Mode B leaning |

### Conditional Entropy Evidence

MIDDLE reduces suffix entropy by 1.767 bits (45.1% of H(suffix)=3.915); PREFIX reduces by only 0.283 bits (7.2%). MIDDLE TERM reduces suffix by 0.910 bits vs HEAD's 0.366 bits. The exit atom of the MIDDLE carries 2.5x more suffix information than the entry atom.

---

## Falsification Criteria

1. If PREFIX V for suffix mode exceeds 0.50 with expanded PREFIX inventory, MIDDLE dominance weakens
2. If MIDDLE HEAD outpredicts MIDDLE TERM for suffix mode (reversing the 0.323 vs 0.503 relationship), the terminal-atom gatekeeper model fails
3. If three-way synergy > 0.20 bits, pairwise dominance of MIDDLE->SUFFIX is insufficient

---

## Method

- 23,096 Currier B tokens with suffix/MIDDLE decomposition per C1393, C1408
- Cramer's V and MI for each predictor -> suffix mode (A vs B per C1229)
- Conditional entropy H(SUFFIX | MIDDLE), H(SUFFIX | PREFIX), H(SUFFIX | BOTH)
- Separate analysis for MIDDLE HEAD, MIDDLE TERM, and full MIDDLE

**Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
**Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` (T3, T4, T8)
