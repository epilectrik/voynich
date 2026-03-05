# C1408: Suffix Has HEAD→TERM Compositional Structure

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, atom, compositional, structure
**Phase:** SUFFIX_ATOM_DECOMPOSITION (Phase 515)
**Extends:** C1394 (instruction encoding architecture), C906 (vowel primitive suffix saturation), C1002 (suffix positional/sequential grammar)
**Relates to:** C1393 (MIDDLE compound composition grammar), C1209 (MIDDLE slot syntax)

---

## Statement

Suffix decomposes into atoms from a 16-atom subset of the MIDDLE inventory (missing k, t, p, f, c) with **strong HEAD→TERM ordering** parallel to MIDDLE's slot syntax. 76.6% of multi-atom suffixes have a HEAD-class atom (a, e, o) in initial position; 100% have a TERM-class atom (y, l, r, n, m) in terminal position; zero ordering violations observed. The first atom (HEAD) predicts operational category (V=0.277), while the last atom (TERM) predicts line position (R²=0.059), exactly paralleling MIDDLE's HEAD→MOD→TERM architecture at a reduced scale.

### Suffix Atom Inventory (16 atoms)

| Class | Atoms | Role in suffix |
|-------|-------|---------------|
| HEAD | a, e, o | Domain selection (initial position, V=0.277 for category) |
| MOD | d, s, i, ii | Modification (medial position) |
| TERM | y, l, r, n, m, h | Exit/scope (terminal position, R²=0.059 for line position) |
| Absent | k, t, p, f, c | Never appear in suffix (these are MIDDLE-only HEAD/MOD atoms) |

### Compositional Structure Evidence (T7)

| Measure | First atom | Last atom | Whole suffix |
|---------|-----------|-----------|-------------|
| Category V | **0.277** | 0.163 | 0.291 |
| Position R² | 0.022 | **0.059** | 0.077 |

First atom dominates category prediction; last atom dominates position prediction. This is the HEAD→TERM pattern.

### Suffix Length Distribution (T1)

| Length | Count | % |
|--------|-------|---|
| 1 atom | 1,608 (y, r, s, l, m, n, g) | 14.4% |
| 2 atoms | 5,424 (dy, hy, ey, al, ar, or, ol, am, om, ly, ry, in, an, er, el, en) | 48.7% |
| 3 atoms | 3,932 (edy, eey, ain, iin, aiin, eol, oin, eeol, oiin, eiin) | 35.3% |
| 4 atoms | 187 (aiin counted as 3: a+ii+n) | 1.7% |

### Ordering Constraints (T2)

- HEAD atoms (a, e, o): 76.6% initial, near-zero terminal
- TERM atoms (y, l, r, n, m): near-zero initial, high terminal
- MOD atoms (d, s, i): strictly medial in multi-atom suffixes
- **Zero violations** of HEAD→MOD→TERM ordering observed

---

## Falsification Criteria

1. If a suffix type with HEAD in non-initial position is discovered at significant frequency, the ordering constraint fails
2. If the first-atom category V drops below last-atom V with better category data, the HEAD interpretation weakens
3. If more than 2 of the 5 "absent" atoms (k, t, p, f, c) appear in suffix at non-negligible frequency, the reduced inventory claim fails

---

## Method

- 11,151 suffixed tokens from 23,096 Currier B tokens (48.3% suffixed)
- 35 distinct suffix types decomposed into atoms using C1393 slot grammar
- Positional analysis: atom position within multi-atom suffixes
- Category assignment via PREFIX proxy (C1297/C1305): qo→THERMAL, ch/sh→MONITORING, ok/ot→OPERATION, d→CONTAINMENT, s→STAGING
- Cramér's V for atom × category; R² for atom × line position
- Nested comparison: first-atom vs last-atom vs whole-suffix predictive power

**Script:** `phases/SUFFIX_ATOM_DECOMPOSITION/scripts/suffix_atom_decomposition.py`
**Results:** `phases/SUFFIX_ATOM_DECOMPOSITION/results/suffix_atom_decomposition.json` (T1, T2, T7)
