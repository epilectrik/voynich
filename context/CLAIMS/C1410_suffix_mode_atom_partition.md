# C1410: Suffix Modes are Atom-Level Category Partitions

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, atom, mode, paragraph, cycling
**Phase:** SUFFIX_ATOM_DECOMPOSITION (Phase 515)
**Extends:** C1229 (alternating suffix modes), C1382 (k/a atom suffix mode polarization)
**Relates to:** C1398 (paragraph operational gradient), C1230 (mode MIDDLE differentiation)

---

## Statement

The two alternating suffix modes identified in C1229 decompose cleanly at atom level into operationally distinct partitions:

- **Mode A (specification)**: Enriched in {d, e, ee, h, y} — THERMAL/MONITORING atoms (1.68-2.38x enrichment)
- **Mode B (continuation)**: Enriched in {a, i, ii, l, m, n, o, r, s} — STAGING/TRANSITION/FLOW atoms

The modes are not arbitrary line clusters — they reflect alternation between two operational vocabularies at the atom level.

### Mode Enrichment Table (T8)

| Atom | Mode A frac | Mode B frac | Ratio | Direction |
|------|-----------|-----------|-------|-----------|
| e | 0.129 | 0.054 | 2.38 | MODE_A |
| d | 0.152 | 0.069 | 2.22 | MODE_A |
| ee | 0.031 | 0.017 | 1.84 | MODE_A |
| h | 0.049 | 0.029 | 1.69 | MODE_A |
| y | 0.310 | 0.196 | 1.58 | MODE_A |
| a | 0.097 | 0.200 | 0.49 | MODE_B |
| ii | 0.034 | 0.077 | 0.44 | MODE_B |
| n | 0.058 | 0.133 | 0.44 | MODE_B |
| i | 0.030 | 0.068 | 0.44 | MODE_B |
| r | 0.047 | 0.086 | 0.55 | MODE_B |
| l | 0.043 | 0.066 | 0.65 | MODE_B |
| o | 0.016 | 0.023 | 0.70 | MODE_B |
| s | 0.017 | 0.022 | 0.77 | MODE_B |
| m | 0.009 | 0.018 | 0.50 | MODE_B |

### Operational Interpretation

Mode A lines use suffix atoms from the THERMAL/MONITORING domain — specifying what's being measured or controlled. Mode B lines use atoms from the STAGING/FLOW/TRANSITION domain — continuing the process, routing, or sequencing.

This maps onto the "specification vs continuation" interpretation from C1229: specification lines (Mode A) parametrize the current thermal/monitoring operation; continuation lines (Mode B) handle staging, material flow, and transitions to the next operation.

### Mode Balance

- Mode A: 1,241 lines (51.8%)
- Mode B: 1,153 lines (48.2%)
- Near-equal balance, consistent with C1229's 80% interleaved pattern

---

## Falsification Criteria

1. If a third mode emerges with distinct atom profile at silhouette > 0.3, the binary partition is insufficient
2. If mode assignment is driven by a single atom (e.g., removing 'd' collapses the partition), the atom-level interpretation is fragile
3. If the operational interpretation (thermal vs flow) doesn't replicate with direct category data (not PREFIX proxy), the category mapping may be an artifact

---

## Method

- Suffix-bearing lines (2,394) clustered into k=2 using suffix atom frequency vectors
- Enrichment ratio: atom fraction in Mode A / atom fraction in Mode B
- Direction assigned at ratio > 1.5 (MODE_A) or < 0.67 (MODE_B)
- Connected to C1229's alternating mode finding

**Script:** `phases/SUFFIX_ATOM_DECOMPOSITION/scripts/suffix_atom_decomposition.py`
**Results:** `phases/SUFFIX_ATOM_DECOMPOSITION/results/suffix_atom_decomposition.json` (T8)
