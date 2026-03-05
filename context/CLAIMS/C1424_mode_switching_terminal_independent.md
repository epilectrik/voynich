# C1424: Mode Switching Is TERMINAL-Independent at Line Level

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, mode, line, TERMINAL, independence
**Phase:** SUFFIX_MODE_CYCLING_MECHANISM (Phase 518)
**Extends:** C1423 (line-level mode persistence), C1412 (MIDDLE dominates suffix determination)
**Relates to:** C1422 (MIDDLE-determined without sequential dependency), C1229 (alternating suffix modes)

---

## Statement

Whether the dominant TERMINAL atom changes between consecutive lines has NO effect on whether the suffix mode changes. Mode switch rate is 39.1% when consecutive lines share the same dominant TERMINAL vs 39.4% when they have different dominant TERMINALs (delta = 0.3 pp, not significant). TERMINAL vocabulary determines each line's mode independently; the line-to-line cycling pattern is not driven by TERMINAL alternation.

### Decomposition Evidence

| Condition | N pairs | Mode switch rate |
|-----------|---------|-----------------|
| Same dominant TERMINAL | 644 | 0.3913 |
| Different dominant TERMINAL | 1,051 | 0.3939 |
| All pairs | 1,766 | 0.3935 |

### TERMINAL Contribution to Mode Pattern

The below-random interleaving (switch rate 0.3935 vs random 0.499) is fully captured by TERMINAL vocabulary effects:

| Metric | Value |
|--------|-------|
| Observed interleave rate | 0.3935 |
| Random expectation | 0.499 |
| Excess over random | -0.1054 |
| Predicted from TERMINAL alone | 0.3929 |
| TERMINAL % of excess | 100.6% |
| Residual % | -0.6% |

### Implication

TERMINAL atoms gate each line's mode independently (C1412, C1422). The below-random mode switching between lines arises because consecutive lines tend to use similar MIDDLE vocabularies (C670), not because TERMINALs actively alternate or persist. The mode persistence in C1423 is a consequence of vocabulary continuity, with only 2.89% genuine sequential signal beyond this.

---

## Falsification Criteria

1. If a controlled experiment shows TERMINAL switching rate significantly predicts mode switching rate (after controlling for TERMINAL identity), the independence claim fails
2. If mode switch rate differs by >5 pp between same-TERMINAL and different-TERMINAL pairs in a larger sample, the finding is not robust

---

## Method

- 1,766 consecutive line pairs within paragraphs
- Dominant TERMINAL per line = most frequent TERMINAL atom (base char) among suffixed tokens
- 644 same-TERMINAL pairs vs 1,051 different-TERMINAL pairs
- Mode switch rates compared between conditions
- TERMINAL contribution computed as: predicted_switch = P(mode_switch | same_term) * P(same_term) + P(mode_switch | diff_term) * P(diff_term)

**Script:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/scripts/suffix_mode_mechanism.py` (T10)
**Results:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json`
