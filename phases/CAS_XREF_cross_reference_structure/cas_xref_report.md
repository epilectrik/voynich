# CAS-XREF: Cross-Reference Structure Analysis

## Phase Code
`CAS-XREF` (Currier A Schema - Cross Reference)

## Research Question
How do Currier A (catalog) and Currier B (procedures) structurally relate?

---

## Results Summary

| Hypothesis | Result | Tier |
|------------|--------|------|
| H1: Balanced tokens = cross-references | NO SIGNAL | - |
| H2: CT-in-B = material references | NO SIGNAL | - |
| H3: A-vocabulary patterns in B | NO SIGNAL | - |
| **H4: Section mapping** | **STRONG SIGNAL** | **Tier 2 STRUCTURAL** |

---

## H1: Balanced Tokens as Cross-Reference Points

**Test:** Do the 161 balanced tokens (0.5x-2.0x A/B ratio) appear in predictable positions suggesting indexing function?

**Result: NO SIGNAL**

- Balanced tokens appear 92.6% line-middle in both A and B
- Line-initial enrichment: 0.76x in A, 1.20x in B (no significant pattern)
- Chi-square p-values significant but in wrong direction (depleted, not enriched)

**Conclusion:** Balanced tokens are NOT positional markers. Their balance reflects frequency equilibrium, not cross-reference function.

---

## H2: CT-in-B as Material References

**Test:** Are CT tokens (A-enriched) clustered at specific positions when they appear in B?

**Result: NO SIGNAL**

- CT occurrences in B: 214 (across 48 folios)
- Mean relative position: 0.522 (exactly mid-line)
- Distribution: uniform across line positions

**Preceding tokens:** No clear pattern (chedy, aiin, qoteedy, dain most common)
**Following tokens:** No clear pattern (otedy, oteol, chey most common)

**Conclusion:** CT tokens in B are integrated into grammar, not marked as references.

---

## H3: A-Enriched Vocabulary Patterns in B

**Test:** Do A-enriched tokens (>2x in A) show consistent positional patterns in B?

**Result: NO SIGNAL**

- A-enriched tokens: 236 (appearing 2,318 times in B)
- Mean position: 0.499 (exactly mid-line)
- Line-initial enrichment: 1.13x (not significant)

**Prefix distribution in B:**
- ch: 914 (most common)
- other: 788
- sh: 169
- ok: 134
- qo: 129
- ct: 116

**Conclusion:** A-enriched vocabulary integrates into B grammar without positional marking.

---

## H4: A-Section to B-Folio Mapping

**Test:** Do B folios cluster by which A-section vocabulary they contain?

**Result: STRONG SIGNAL (Tier 2)**

### A Section Vocabulary Sizes
| Section | Unique Tokens | Exclusive Tokens |
|---------|---------------|------------------|
| H | 3,543 | 2,789 |
| P | 1,802 | 1,144 |
| T | 754 | 375 |

### B Folio Classification by Dominant A-Section
| Dominant Section | B Folios | Percentage |
|------------------|----------|------------|
| **H** | 76 | 91.6% |
| **P** | 7 | 8.4% |
| **T** | 0 | 0% |

**Statistical Test:**
- Chi-square: χ² = 127.54
- p-value: < 0.0001
- Uniformity null hypothesis: REJECTED

### Top H-Dominant B Folios
| Folio | H-exclusive tokens | Total A-vocab | H% |
|-------|-------------------|---------------|-----|
| f113r | 56 | 88 | 63.6% |
| f104v | 47 | 74 | 63.5% |
| f113v | 45 | 70 | 64.3% |
| f115r | 44 | 66 | 66.7% |
| f106v | 44 | 67 | 65.7% |

### P-Dominant B Folios (rare)
| Folio | P-exclusive tokens | Total A-vocab | P% |
|-------|-------------------|---------------|-----|
| f31v | 13 | 27 | 48.1% |
| f31r | 11 | 17 | 64.7% |
| f83v | 10 | 22 | 45.5% |

---

## Interpretation

### Tier 2 STRUCTURAL (What We Measured)

1. **Section H vocabulary dominates B procedures**
   - 76 of 83 B folios (91.6%) use predominantly H-section vocabulary
   - This is a structural fact about vocabulary distribution

2. **Section P vocabulary is rare in B**
   - Only 7 B folios (8.4%) use predominantly P-section vocabulary

3. **Section T vocabulary is absent from B**
   - Zero B folios show T-section vocabulary dominance

4. **Cross-Reference Mechanism**
   - The link between A and B is NOT explicit positional markers
   - Instead, it's VOCABULARY OVERLAP: B procedures use A-catalog vocabulary
   - The vocabulary itself IS the reference

### Tier 3-4 SPECULATIVE (What This Might Mean)

The following interpretations are NON-BINDING and DISCARDABLE:

- H might catalog materials that require procedural processing
- P might catalog materials used differently (additives? reagents? different workflows?)
- T might catalog materials not requiring B-type procedures (reference? standards?)

**These semantic labels are speculative.** The structural finding is only that H/P/T have non-uniform B-procedure coverage.

### Distribution Model (STRUCTURAL)

```
Currier A (Catalog)           Currier B (Procedures)
─────────────────────         ──────────────────────
Section H: 3,543 tokens  ───► 76 folios (91.6%) use H vocabulary
Section P: 1,802 tokens  ───► 7 folios (8.4%) use P vocabulary
Section T: 754 tokens    ───► 0 folios (0%) use T vocabulary
```

---

## New Constraint

**Constraint 299:** Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); distribution non-uniform (chi² = 127.54, p < 0.0001). A sections have NON-UNIFORM mapping to B procedure applicability. (CAS-XREF)

---

## Files

- Analysis script: `archive/scripts/cas_xref_analysis.py`
- Results JSON: `phases/CAS_XREF_cross_reference_structure/cas_xref_results.json`
- This report: `phases/CAS_XREF_cross_reference_structure/cas_xref_report.md`

---

*CAS-XREF COMPLETE. 1 new constraint validated.*
