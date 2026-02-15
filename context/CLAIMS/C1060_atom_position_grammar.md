# C1060: Compound Atom Position Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_DEEP_STRUCTURE (Phase 379)
**Extends:** C521 (kernel ordering: e→h blocked), C522 (kernel composition), C935 (compound specification)
**Relates to:** C766 (UN compound rate 81.1%), C767 (compound bimodality)

---

## Statement

Atoms within compound MIDDLEs have **non-random positional preferences** (V=0.333, chi²=201.1, p=3.8e-14). 5 of 37 testable atoms show significant individual bias after Bonferroni correction (p < 0.00135).

Strong INITIAL-preferring atoms:

| Atom | N | INIT | MED | FIN | Mean position | Kernel |
|------|---|------|-----|-----|---------------|--------|
| opch | 15 | 14 | 1 | 0 | 0.010 | h |
| eol | 14 | 12 | 1 | 1 | 0.060 | e |
| op | 24 | 20 | 2 | 2 | 0.075 | - |

Strong FINAL-preferring atoms:

| Atom | N | INIT | MED | FIN | Mean position | Kernel |
|------|---|------|-----|-----|---------------|--------|
| ai | 51 | 7 | 15 | 29 | 0.526 | - |
| kc | 14 | 0 | 2 | 12 | 0.599 | k |
| ed | 42 | 13 | 9 | 20 | 0.448 | e |
| eod | 26 | 3 | 6 | 17 | 0.417 | e |

Kernel prediction (extending C521): k-containing atoms tend toward earlier positions (mean=0.292) than e-containing atoms (mean=0.332). Mann-Whitney p=0.054 — marginally significant, directionally consistent with C521's one-way valve (k→e favored, e→h blocked).

---

## Interpretation

C521 established kernel ordering within single MIDDLEs: e→h is blocked (0.00 ratio), k/h→e is favored (4.32x/7.00x). This constraint extends that principle to compound MIDDLEs: atoms that contain k-operators tend to appear earlier in the compound structure, while e-containing atoms tend to appear later.

The strongest positional signal is not kernel-driven but structural: `opch` (14/15 INITIAL), `eol` (12/14 INITIAL), and `op` (20/24 INITIAL) are almost exclusively found at compound beginnings. These are "gateway atoms" — structural entry points for compounds. Conversely, `ai` (29/51 FINAL) and `kc` (12/14 FINAL) are "terminal atoms" that close compounds.

The atom `kc` is notable: despite containing k (which should predict early position per C521), it is overwhelmingly FINAL (12/14). This is the k-operator in its terminal/boundary role, not its initiating role — consistent with k's dual function as both energy-application and program-closure operator.

---

## Method

- 449 compound MIDDLEs from Currier B inventory (MiddleAnalyzer)
- Normalized position: character offset of atom's first character / compound MIDDLE length → [0,1]
- Categorical classification: INITIAL (starts at index 0), MEDIAL (neither), FINAL (ends at last char)
- Overall: chi² on 37-atom × 3-position contingency table, Cramér's V
- Per-atom: chi-square goodness-of-fit against uniform distribution, Bonferroni correction (0.05/37)
- Kernel prediction: atoms pooled by k-containing vs e-containing, Mann-Whitney on mean normalized positions

**Script:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py`
**Results:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t3_atom_position_grammar.json`
