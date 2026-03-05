# C1415: 83 Forbidden PREFIX x MIDDLE HEAD Combinations at Atom Level

**Tier:** 2 (ESTABLISHED)
**Scope:** B, PREFIX, MIDDLE, atom, forbidden, combinations
**Phase:** CROSS_SLOT_INTERACTION (Phase 516)
**Extends:** C911 (102 PREFIX-MIDDLE forbidden combinations), C1393 (HEAD+MOD+TERM grammar)
**Relates to:** C1411 (PREFIX->MIDDLE selectivity), C1219 (base determines MIDDLE content)

---

## Statement

83 PREFIX x MIDDLE HEAD atom pairs are strongly depleted (observed/expected < 0.10, chi2 p < 0.001) from 16,537 prefixed tokens across 15 major PREFIXes. These represent atom-level selectivity constraints that extend C911's 102 whole-MIDDLE forbidden combinations to the sub-MIDDLE level. Key patterns: qo categorically avoids e/a/o/y-initial MIDDLEs (ratio 0.037-0.070); ok/ot categorically forbid k/t-initial MIDDLEs (0 observed); da categorically forbids e-initial MIDDLEs (0 observed, 214 expected); ch/sh forbid i/m/h-initial MIDDLEs.

### Major Forbidden Channels

**qo (THERMAL channel):**
- qo x e HEAD: obs=97, exp=1585, ratio=0.061
- qo x a HEAD: obs=31, exp=444, ratio=0.070
- qo x o HEAD: obs=11, exp=298, ratio=0.037
- qo x y HEAD: obs=5, exp=98, ratio=0.051
- qo x m HEAD: 0 observed (exp=16)
- qo x h HEAD: 0 observed (exp=11)

**ok/ot (CONTAINMENT channel):**
- ok x k HEAD: 0 observed (exp=269)
- ok x t HEAD: 0 observed (exp=79)
- ot x k HEAD: 1 observed (exp=263), ratio=0.004
- ot x t HEAD: 0 observed (exp=77)

**da (INFRASTRUCTURE):**
- da x e HEAD: 0 observed (exp=214)
- da x k HEAD: 1 observed (exp=95), ratio=0.011
- da x o HEAD: 0 observed (exp=40)
- da x t HEAD: 0 observed (exp=28)

**ch/sh (MONITORING channel):**
- ch x i HEAD: 0 observed (exp=28)
- ch x m HEAD: 0 observed (exp=13)
- ch x h HEAD: 0 observed (exp=9)
- sh x i HEAD: 0 observed (exp=20)
- sh x m HEAD: 0 observed (exp=9)
- sh x h HEAD: 0 observed (exp=6)

### Channel Exclusion Pattern

| PREFIX | Forbidden HEAD atoms | Permitted HEAD atoms |
|--------|---------------------|---------------------|
| qo | e, a, o, y, m, h | k, t, d, s |
| ok/ot | k, t, r, i, m | e, a, o, y, d |
| da | e, k, o, t, a | i, r, d, l, s |
| ch/sh | i, m, h, r, (k for sh) | e, o, a, d, y, s |

Each PREFIX defines a narrow atom window. Combined with C1411, this shows the token construction grammar is strongly channeled: PREFIX selects both which MIDDLE atoms are legal AND which operational domain those atoms come from.

---

## Falsification Criteria

1. If more than 10% of the 83 forbidden pairs achieve O/E > 0.20 with refined morphological parsing, the selectivity is weaker
2. If the absolute zeros (ok x k, da x e, etc.) are found at non-negligible rates in a different transcript reading, the categoricality fails
3. If section-conditioning eliminates > 50% of the forbidden pairs, the effect is section-mediated not intrinsic

---

## Method

- 16,537 prefixed Currier B tokens with MIDDLE HEAD atom identified per C1393
- For each PREFIX x HEAD atom pair: observed count, expected count (under independence), ratio
- Depleted threshold: O/E < 0.10 AND chi2 test p < 0.001
- 15 PREFIXes with N >= 50 tested: qo, ch, sh, ok, ot, da, ol, lk, sa, lch, yk, te, ke, pch, ka
- Additional minor PREFIXes (or, al, tch, ar, ta, so) included where expected > 5

**Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
**Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` (T9)
