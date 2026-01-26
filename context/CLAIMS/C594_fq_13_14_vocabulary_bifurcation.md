# C594: FQ 13-14 Complete Vocabulary Bifurcation

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FQ Classes 13 and 14 share **zero MIDDLEs** (Jaccard = 0.000): Class 13 uses {aiin, ain, e, edy, eey, eol} (6 MIDDLEs, 18.2% suffixed), Class 14 uses {al, am, ar, ey, ol, or, y} (7 MIDDLEs, 0% suffixed). Both use ok/ot prefixes (13: 55% ok, 14: 57% ot). Positionally separated (mean 0.530 vs 0.615, p=1.6e-10). Regime/section near-identical (JS=0.0018/0.0051). This is a complete lexical partition — sharper than EN's QO/CHSH bifurcation (Jaccard=0.133, C576).

---

## Evidence

**Test:** `phases/FQ_ANATOMY/scripts/fq_structural_anatomy.py`

### MIDDLE Vocabulary

| Class | MIDDLEs | Count | Suffixed |
|-------|---------|-------|----------|
| 13 | aiin, ain, e, edy, eey, eol | 6 | 18.2% |
| 14 | al, am, ar, ey, ol, or, y | 7 | 0.0% |
| **Shared** | **none** | **0** | — |

- Jaccard similarity: **0.000** (complete non-overlap)
- Suffix complement: Fisher's exact p = 4.0e-48

### Prefix Distribution

| Class | ok | ot |
|-------|----|----|
| 13 | 657 (55%) | 534 (45%) |
| 14 | 302 (43%) | 405 (57%) |

Both classes gate through the same PREFIX system but select entirely disjoint MIDDLE sets.

### Positional Separation

| Measure | Class 13 | Class 14 | p-value |
|---------|----------|----------|---------|
| Mean position | 0.530 | 0.615 | 1.6e-10 |

Class 14 is significantly more final-biased.

### Distributional Similarity

| Measure | Value | Interpretation |
|---------|-------|----------------|
| Context JS | 0.008 | Near-identical context |
| Regime JS | 0.0018 | Near-identical REGIME usage |
| Section JS | 0.0051 | Near-identical section usage |

### Comparison with EN Bifurcation (C576)

| Property | FQ 13/14 | EN QO/CHSH |
|----------|----------|------------|
| MIDDLE Jaccard | **0.000** | 0.133 |
| Shared MIDDLEs | 0 | 8 |
| Suffix complement | 18.2% vs 0% | ~61% vs ~61% |
| Positional separation | p=1.6e-10 | p=0.104 (NS) |
| Context divergence | JS=0.008 | JS=0.0024 |

FQ's bifurcation is **more extreme** than EN's: complete non-overlap (vs 87% non-overlap), plus positional separation (vs positional equivalence).

---

## Interpretation

Classes 13 and 14 represent the same PREFIX gate applied to **completely disjoint MIDDLE subvocabularies**. This parallels EN's QO/CHSH bifurcation (C576) but is even sharper:
- EN: same prefix family → different MIDDLEs (87% non-overlap), same positions
- FQ: same prefix system → different MIDDLEs (100% non-overlap), different positions

The suffix complement (13 uses suffixes, 14 never does) plus positional separation suggests these are functionally distinct operators that happen to share a morphological gating mechanism.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C576 | Parallels - EN MIDDLE bifurcation by prefix (weaker: Jaccard=0.133) |
| C593 | Contextualized - 13/14 form the PREFIXED_PAIR sub-group |
| C267 | Instantiated - compositional morphology creates vocabulary partitions |
| C587 | Extended - 13/14 differentiation now fully characterized |

---

## Provenance

- **Phase:** FQ_ANATOMY
- **Date:** 2026-01-26
- **Script:** fq_structural_anatomy.py

---

## Navigation

<- [C593_fq_3group_structure.md](C593_fq_3group_structure.md) | [INDEX.md](INDEX.md) ->
