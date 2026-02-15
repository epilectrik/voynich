# C1065: Atom Bigram Ordering Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE (Phase 380)
**Extends:** C1060 (atom position grammar V=0.333), C521 (kernel ordering)
**Relates to:** C517 (superstring compression), C873 (kernel positional ordering), C1061 (atom co-occurrence)

---

## Statement

Atom ordering within compound MIDDLEs follows a **strong directed grammar** (chi²=1898.8, p=1.8e-73, V=0.376). 21 atom pairs show > 80% directional dominance (n >= 5), with 15 pairs at 100% dominance.

| Measure | Value |
|---------|-------|
| Compounds analyzed | 449 |
| Total ordered atom pairs | 659 |
| Unique atoms | 56 |
| Chi² | 1898.8 (p = 1.8e-73) |
| Cramér's V | 0.376 |
| Asymmetric pairs (> 80%) | **21** |
| 100% dominant pairs | 15 |
| Permutation null p | 0.0000 (observed chi² >> null mean 1481.1) |

Selected 100%-dominant ordering rules:

| Before | After | n |
|--------|-------|---|
| al | lo | 12 |
| ka | ai | 12 |
| eeo | eod | 10 |
| al | lch | 9 |
| ke | eo | 8 |
| ek | ke | 7 |

Kernel asymmetry (extending C521):

| Direction | Count | Rate | p |
|-----------|-------|------|---|
| k-before-e | 91/155 | 58.7% | 0.036 |
| e-before-h | 43/100 | 43.0% | 0.193 |

k-before-e is significant (p=0.036) but at 58.7%, weaker than C521's within-token ratio (4.32x). e-before-h is NOT significant — C521's e→h block (0.00 ratio) does not propagate to compound atom ordering.

---

## Interpretation

Compound MIDDLEs are assembled by a directed construction grammar. The 21 asymmetric pairs with > 80% dominance establish that atom ordering is highly constrained — not random concatenation. The permutation null (p=0.0000) confirms this is genuine grammar beyond what marginal atom frequencies predict.

The grammar exhibits "gateway-terminal chains": op→al→lo/lch, eeo→eod, ka→ai, te→ed/eeo. These chains show that compound construction follows specific assembly paths, not arbitrary composition.

C521's kernel ordering partially propagates: k-atoms tend to precede e-atoms (58.7%, p=0.036), but the effect is weaker than within single MIDDLEs (where e→h is completely blocked). This suggests compound construction operates at a higher structural level where kernel constraints apply directionally but not absolutely. The e-before-h non-result (43%, NS) shows that the one-way valve becomes permeable at the compound level.

---

## Method

- 449 compound MIDDLEs with 2+ maximal atoms
- For each compound, extract all ordered atom pairs by string position (middle.find())
- Type-level analysis: each unique compound MIDDLE counts once
- Transition matrix: 56 atoms, filtered to rows/columns with >= 5 bigrams
- Asymmetry: for each unordered pair {A,B}, rate = count(A-before-B) / total
- Permutation null: 1000 random shuffles of atom order within each compound (preserving composition)
- Kernel test: classify atoms by k/e/h content, count directional pairs

**Script:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py`
**Results:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t3_atom_bigram_grammar.json`
