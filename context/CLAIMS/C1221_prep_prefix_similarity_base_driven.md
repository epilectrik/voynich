# C1221: Prep PREFIX Similarity is Base-Driven

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PREFIX_ATOM_ROLES (Phase 434)
**Extends:** C933 (prep verb early concentration), C1219 (base determines MIDDLE content)
**Relates to:** C931 (PREFIX positional phase mapping), F-BRU-012 (Brunschwig prep verb assignments)

---

## Statement

Prep PREFIXes (pch, tch, dch, te, lch) carry highly similar MIDDLE content (mean pairwise cosine = 0.963), but this similarity is NOT special to prep verbs. A within-folio shuffle test (1000 iterations) shows that random groups of 5 PREFIXes achieve equal or greater similarity 99.8% of the time (p=0.998). The prep group's uniformity is fully explained by their shared base characters (4 of 5 are h-based, where within-base cosine = 0.950).

### Prep PREFIX MIDDLE Profiles

| PREFIX | N | ITER | ENRG | STAB | MON | CLOS | STRC | FREE |
|--------|---|------|------|------|-----|------|------|------|
| pch | 245 | 7% | 6% | 28% | 3% | 41% | 13% | 1% |
| tch | 172 | 6% | 5% | 25% | 1% | 48% | 13% | 0% |
| dch | 104 | 2% | 7% | 36% | 2% | 39% | 12% | 1% |
| lch | 315 | 3% | 4% | 35% | 2% | 49% | 5% | 0% |
| te | 289 | 3% | 4% | 24% | 1% | 56% | 11% | 1% |

### Shuffle Test

- Observed prep mean cosine: 0.963
- Exceeded in 998/1000 shuffles (p=0.998)
- Conclusion: prep group similarity is not distinctive

### Implication for Brunschwig Glosses

F-BRU-012 assigned distinct operations to prep PREFIXes based on Brunschwig frequency correlation:
- pch = CHOP (prep), tch = POUND (prep), lch = STRIP (completion), te = GATHER (prep)

The identical MIDDLE content challenges these as genuinely different operations. If pch=CHOP and tch=POUND specified different physical actions, they should parameterize differently (carry different MIDDLE atoms). Instead, all prep PREFIXes specify the same STABILITY+CLOSURE domain, suggesting they are **variants of a single preparatory mode** differentiated only by their modifier character and line position, not by MIDDLE content.

---

## Interpretation

The Brunschwig-derived gloss distinctions (CHOP vs POUND vs STRIP vs GATHER) may reflect:
1. Position-based phase differences (pch is paragraph-initial, lch is line-final per C931) rather than operation-type differences
2. Modifier-specific adjustments within a shared preparatory/completion domain
3. Brunschwig's terminology mapping to an operational sequence rather than independent operations

The prep PREFIXes are better understood as: **h-base mode** (STABILITY+CLOSURE domain) + **modifier variant** (p, t, d, l selecting phase/timing), not as independent action verbs.

---

## Method

- 23,096 Currier B tokens with non-empty MIDDLEs
- Computed MIDDLE axis profiles for 5 prep PREFIXes
- Mean pairwise cosine similarity within prep group
- Shuffle test: 1000 iterations, sampled random groups of 5 PREFIXes from the full PREFIX set, computed mean pairwise cosine, compared to observed prep cosine
- Random seed 42

**Script:** `phases/PREFIX_ATOM_ROLES/scripts/prefix_atom_test.py` (T4)
**Results:** `phases/PREFIX_ATOM_ROLES/results/prefix_atom_results.json`
