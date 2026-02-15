# C1053: Compound Atom Prediction is C475-Mediated

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** PARAGRAPH_GRADIENT_COMBINATORICS (Phase 368)
**Extends:** C935 (compound specification dual purpose, 71.6% hit rate)
**Relates to:** C475 (MIDDLE incompatibility), C932 (body vocabulary gradient)

---

## Statement

C935's finding that line-1 compound MIDDLE atoms predict body simple MIDDLEs (71.6% hit rate) is mediated by the C475 compatibility graph. Compound atoms that are mutually C475-compatible predict body MIDDLEs at **12x the rate** of atoms that are mutually incompatible.

| Atom Type | Body Hit Rate | n |
|-----------|--------------|---|
| C475-compatible atoms | **46.2%** | 13 compounds |
| C475-incompatible atoms | **3.9%** | 13 compounds |
| Wilcoxon p | **0.002** | |

Among 180 total compound evaluations, overall atom hit rate was 60.8% (consistent with C935's 71.6% on a slightly different sample).

---

## Interpretation

The specification mechanism (C935) does not simply predict body vocabulary by frequency or co-occurrence — it operates THROUGH the compatibility graph. When a compound MIDDLE's atoms are mutually compatible (i.e., they could legally co-occur per C475), those atoms are strongly predictive of body content. When atoms are incompatible, they almost never appear in the body (3.9%).

This means the compound MIDDLE on line 1 is not just a compressed hint about body vocabulary — it is a compatibility-encoded specification. The atoms that define the compound's structural neighborhood in C475 space are the ones that materialize as body content.

---

## Method

- 73 B paragraphs with 8+ lines
- MiddleAnalyzer identifies compound MIDDLEs and extracts atoms
- For each compound, atoms classified as C475-compatible (compatible with at least one other atom) or incompatible
- Hit rate = fraction of atoms appearing as simple MIDDLEs in paragraph body
- Only compounds with both compatible and incompatible atoms included (n=13)
- Wilcoxon signed-rank test on paired differences

**Script:** `phases/PARAGRAPH_GRADIENT_COMBINATORICS/scripts/paragraph_gradient_combinatorics.py`
**Results:** `phases/PARAGRAPH_GRADIENT_COMBINATORICS/results/paragraph_gradient_combinatorics.json`
