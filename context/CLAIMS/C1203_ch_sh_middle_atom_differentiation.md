# C1203: ch/sh MIDDLE Atom-Level Differentiation

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ENERGY_MODE_TRANSITION (Phase 426, exploratory extension)
**Extends:** C929 (ch/sh sensory modality), C911 (prefix-middle compatibility), C649 (EN-exclusive lane partition)

---

## Statement

Within the shared e-family MIDDLE pool, ch and sh prefixes select MIDDLEs with systematically different atom compositions. ch-prefixed MIDDLEs have higher k-atom fraction (7.1% vs 5.9%) and strongly prefer e-free MIDDLEs (dy 3.1x ch-biased, d 2.8x, k 3.1x). sh-prefixed MIDDLEs are more e-enriched (35.1% vs 30.2% e-atom fraction). Both prefixes share the same core vocabulary (top MIDDLEs: edy, ey, e, eey), but frequency distributions within that vocabulary diverge along the k/e axis.

| Measure | ch-prefix | sh-prefix |
|---------|-----------|-----------|
| Total tokens | 4,014 | 2,474 |
| Distinct MIDDLEs | 328 | 220 |
| Shared MIDDLEs | 116 | 116 |
| k-atom fraction | 7.1% | 5.9% |
| e-atom fraction | 30.2% | 35.1% |
| h-atom fraction | 2.8% | 1.8% |

### ch-biased MIDDLEs (ratio > 2x expected)

| MIDDLE | ch count | sh count | Ratio vs baseline | Atoms |
|--------|----------|----------|-------------------|-------|
| dy | 206 | 66 | 3.1x | e-free, k-free |
| k | 71 | 23 | 3.1x | pure k |
| d | 113 | 41 | 2.8x | e-free, k-free |
| ck | 123 | 54 | 2.3x | contains k |

---

## Interpretation

The differentiation is consistent with C929's functional model: ch (active testing) preferentially pairs with k-containing and e-free operations, while sh (passive monitoring) skews toward e-enriched operations. This may reflect that active testing operates on heating/energy-input processes while passive monitoring tracks cooling/stability processes. However, the effect is modest (+4.9pp e-atom difference) and may be a downstream consequence of the lane partition (C649) and operational context differences (C929) rather than an independent mechanism.

---

## Method

- 23,096 Currier B tokens, filtered to ch-prefix (4,014) and sh-prefix (2,474)
- Prefix detected via morphological extraction (prefix or prefix2 field)
- Atom composition computed per-character across all MIDDLEs under each prefix
- Bias ratios computed against the overall ch:sh token ratio (1.62:1)

**Script:** `phases/ENERGY_MODE_TRANSITION/scripts/ch_sh_middle_exploration.py`
