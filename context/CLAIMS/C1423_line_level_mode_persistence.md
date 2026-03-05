# C1423: Line-Level Mode Persistence With Weak Inertia

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, mode, line, sequential, persistence
**Phase:** SUFFIX_MODE_CYCLING_MECHANISM (Phase 518)
**Extends:** C1229 (alternating suffix modes), C1422 (MIDDLE-determined without sequential dependency)
**Relates to:** C1424 (TERMINAL-independent mode switching), C1412 (MIDDLE dominates suffix determination), C1233 (cross-line independence)

---

## Statement

Consecutive lines within paragraphs show 60.6% same-mode rate (vs 50% random expectation), indicating mild mode PERSISTENCE rather than mode interleaving. Line-level sequential dependency is weak but genuine: CMI(prev_line_mode; curr_line_mode | dominant_TERMINAL) = 0.0289 bits (2.89% of H(mode)). 4/8 TERMINAL strata show significant persistence after controlling for dominant TERMINAL: y (p<0.001, n=868), l (p=0.0003, n=291), n (p=0.0012, n=207), h (p=0.025, n=71).

### Line-Level Mode Statistics

| Metric | Value |
|--------|-------|
| Total line pairs | 1,766 |
| Same-mode rate | 0.6065 |
| Switch rate | 0.3935 |
| Random expectation | 0.499 |
| Permutation mean switch | 0.417 |
| Permutation p-value | 0.999 (not more interleaved than random) |

### C1229 Reconciliation

C1229's "80% interleaved" refers to the fraction of paragraphs (with 8+ body lines) that CONTAIN both Mode A and Mode B lines in non-trivial mixture (k-means paragraph classification). It does NOT mean 80% of consecutive line pairs switch modes. The actual consecutive-line switch rate is 39.4%, which is 10.5 pp BELOW random -- lines mildly persist in mode, not alternate.

### Implication

The appearance of "cycling" in C1229 arises because paragraphs contain a mixture of Mode A and Mode B MIDDLEs, producing both mode types within any sufficiently long paragraph. But consecutive lines tend to PERSIST in the same mode (60.6% same-mode), driven by MIDDLE vocabulary continuity (C670, C675) and mild operational state inertia (2.89% sequential signal). There is no independent paragraph-level oscillation mechanism.

---

## Falsification Criteria

1. If a paragraph-level rhythm variable is found that predicts line mode beyond TERMINAL and previous mode, the "no oscillation" verdict weakens
2. If same-mode rate drops below 52% in a controlled replication, the persistence finding is not robust

---

## Method

- 1,766 consecutive line pairs within paragraphs (paragraphs with 2+ mode-assigned lines)
- Line mode assigned by aggregating suffix atoms across all tokens in the line (Mode A: {d, e, ee, h, y}; Mode B: {a, i, ii, l, m, n, o, r, s}; MIXED excluded)
- Dominant TERMINAL per line = most frequent TERMINAL atom (base char)
- CMI computed via MI(prev_mode, curr_mode) - MI(dom_term, curr_mode) subtraction and verified by stratified chi-squared tests
- Permutation test: 1000 shuffles of line modes within paragraphs

**Script:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/scripts/suffix_mode_mechanism.py` (T7, T9, T10)
**Results:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json`
