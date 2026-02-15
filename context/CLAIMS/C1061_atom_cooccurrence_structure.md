# C1061: Atom Co-occurrence Structure in Compounds

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_DEEP_STRUCTURE (Phase 379)
**Extends:** C475 (MIDDLE incompatibility, 95.7%), C1053 (compound atom body prediction)
**Relates to:** C521 (kernel ordering), C1060 (atom position grammar)

---

## Statement

Atom pairs within compound MIDDLEs show **structured co-occurrence** (chi²=1830, p=3.6e-7). 10 enriched pairs (z > 3.0), 0 depleted pairs (z < -3.0).

Top enriched atom pairs:

| Atom 1 | Atom 2 | Observed | Expected | z |
|--------|--------|----------|----------|---|
| eeo | eod | 10 | 1.3 | +7.51 |
| al | lk | 12 | 2.4 | +6.10 |
| al | lo | 12 | 3.3 | +4.74 |
| ech | ke | 6 | 1.1 | +4.74 |
| lch | ol | 7 | 1.6 | +4.36 |
| ee | et | 6 | 1.3 | +4.06 |
| ai | ka | 12 | 4.1 | +3.91 |
| eok | ke | 6 | 1.5 | +3.74 |
| ot | te | 5 | 1.2 | +3.46 |
| al | lch | 9 | 3.1 | +3.33 |

C475 compliance: **100%** (512/512 known within-compound atom pairs are C475-compatible). However, the random baseline is also 100% (780/780), so enrichment = 1.0x. C475 incompatibility operates at the **token level**, not the **atom-within-compound level**.

---

## Interpretation

The enriched pairs reveal two composition principles:

1. **Overlap-driven pairing:** Many enriched pairs share characters (al+lk, al+lo, lch+ol, eeo+eod). These atoms frequently co-occur because they are adjacent segments of the same compound MIDDLE string, not because of semantic compatibility.

2. **Kernel coherence:** Several enriched pairs share kernel content (ech+ke both contain k and e; eok+ke share ke; ee+et share e-kernel). This suggests compounds preferentially combine atoms from compatible kernel families.

The absence of depleted pairs (0 found) is notable: compounds avoid unfavorable atom combinations not by explicit exclusion but by simply not constructing those compounds. The construction grammar is generative (enrichment) rather than restrictive (depletion).

C475's 100% compliance at the atom level (matching the random baseline) clarifies the scope of MIDDLE incompatibility: C475 applies to **token-level** forbidden transitions, not to **within-compound** atomic composition. Compounds are assembled from atoms that are individually compatible with everything, because if they weren't, they wouldn't be core MIDDLEs in the first place.

---

## Method

- 449 compound MIDDLEs with 2+ maximal atoms
- 56 unique atoms across all compounds
- Co-occurrence matrix: count of compounds containing both atom A and atom B
- Expected: P(A) × P(B) × N_compounds (independence model)
- Standardized residuals z = (observed - expected) / sqrt(expected)
- C475 compliance: check each within-compound atom pair against connected components from `middle_incompatibility.json`

**Script:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py`
**Results:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t4_atom_cooccurrence_rules.json`
